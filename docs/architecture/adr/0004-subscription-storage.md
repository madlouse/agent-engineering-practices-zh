# 0004 订阅的存储、发信、退订令牌和频率限制

- 状态：待产品负责人确认（2026-11-09，关口三 b 拆票时写；按关口三 b 冷审 P0-1、P1-1 修订。属于安全和数据类决定，确认后才开工，见 #40）
- 关联：主站 PRD v1.2 F07 和「订阅的细则」第 2–15 条（第 8 条要求在关口三 b 写 ADR 定表结构和同步方式，第 9 条要求定令牌怎么签、多久失效）；ADR-0003（`/api/site/*`）；PRD 第 3 节路由表 `/unsubscribe`；第三轮冷审 P2-4；关口三 b 冷审 `docs/delivery/reviews/2026-11-09-gate-3b.md` P0-1、P1-2、P1-3、P2-5、P2-9

## 背景

订阅只收邮箱，提交即订阅（细则第 1 条）。要存的有两类：名单（谁在订阅、什么语言、什么状态）和同意证据（每次提交五项）。退订要能一步生效，邮件安全扫描预取链接又不能误退。频率限制要挡住滥用，IP 不能落库（细则第 6 条）。这些都涉及邮箱，按 PRD 第 8 节「安全」打 `risk:high`。

## 决定

**(a) 存储：主站自己的 Supabase 项目，表放在不对外暴露的 schema `site`，只给 `site_api` 角色写策略，不用 service_role。**

- 主站单独一个 Supabase 项目（免费额度），不放进 Veli 的项目：Veli 的项目里有健康数据，主站拿不到它的任何密钥。
- **表放在 schema `site`**，不加进 Supabase Data API 暴露的 schema 列表，公开接口（PostgREST）根本看不到它。
- **迁移里显式收回权限**：`revoke all` 收回 `anon`、`authenticated`、`public` 对 schema `site` 和其中每张表、序列的权限，不靠 Supabase 的默认授权。
- **运行时角色 `site_api`**：能登录，不是表的所有者，不带 `BYPASSRLS`；只授予 `usage on schema site` 和每张表需要的操作。
- **两张表都开行级安全，按表写策略，只给 `site_api` 它需要的操作**：`subscribers` 给 select、insert、update、delete；`consent_records` 给 select、insert、delete（同意证据只增不改）。策略写成 `to site_api`，其他角色没有策略，一行也读不到。
- **两个连接串，分开用**：
  - `SITE_DB_URL`：`site_api` 经 Supabase 连接池（事务模式，用户名是 `site_api.<项目编号>`）的连接串，只放在 Vercel 的生产环境变量里，运行时只读它。
  - `SITE_DB_MIGRATE_URL`：表所有者的连接串，只放在 GitHub Actions 的仓库密钥里，只由站点迁移脚本在 CI 里读；不进 Vercel，运行时拿不到。迁移文件放在 `migrations/site/`，由 GitHub Actions 在生产分支合并后（或手动触发）执行。
- **不碰沙箱契约**：运行时用一个新的服务端模块连 `SITE_DB_URL`，不读预置的 `DATABASE_URL`，不改 `src/lib/db.ts` 和 `src/lib/auth/*`（本仓库 `AGENTS.md`）。加一个检查脚本：运行时代码里读 `SITE_DB_MIGRATE_URL` 或 `DATABASE_URL` 的地方为 0。
- **缺连接串时不假装成功**：`VERCEL_ENV=production` 而 `SITE_DB_URL` 缺失或连不上时，订阅接口返回 503，不落到内存库。只有在非生产环境（预览、本地、测试），新模块才用它自己的内存 PGLite，并在启动时执行 `migrations/site/`；预览上的订阅不写真实名单。
- **预览的多实例**：内存 PGLite 每个函数实例各一份，跨请求的状态（先订阅再退订、重复提交）在 `node --test` 加 PGLite 里测；预览部署上只测界面和单个请求。

| 表 | 字段 |
|---|---|
| `site.subscribers` | `id`（uuid）、`email`（小写后唯一）、`lang`（zh / en）、`status`（active / unsubscribed / stopped_hard_bounce / stopped_complaint / stopped_soft_bounce）、`soft_bounce_streak`、`last_issue_sent`（最近发到第几期，没有发过为空）、`created_at`、`updated_at`、`unsubscribed_at`、`stopped_at` |
| `site.consent_records` | `id`、`subscriber_id`（删订阅者时级联删除）、`email`、`submitted_at`（UTC）、`lang`、`path`（不带查询参数）、`utm_source`、`form_copy_version` |

`last_issue_sent` 给两件事用：每周发送时跳过这一期已经发过的地址（重跑不重复发）；退信回调判断「连续 3 期」软退信时，按期号算。

状态怎么变只写在细则第 4、7、15 条，代码按那里实现，这里不重写。

**(b) 发信：从数据表直接发，不在 Resend 里存第二份名单。**

- 发送前从 `subscribers` 读状态为 active 的地址，按订阅语言用 Resend 的批量发送接口发；这就是细则第 8 条的「发送前同步名单」。Resend 里不建受众（Audience），删除时少一处要删。
- 每封邮件带自己的退订令牌，放进 `List-Unsubscribe`、`List-Unsubscribe-Post` 两个邮件头和正文底部的退订链接。
- Resend 的打开追踪和点击追踪关闭。发信域名 news.velicoach.com（PRD 第 10 节）。
- 回调 `POST /api/site/resend` 先校验 Resend 的签名（Svix），再按事件编号去重，写回状态。
- 定时：Vercel Cron 触发发送；英文版按 America/New_York 的 08:00 换算，夏令时由处理函数判断。定时接口只接受带 `Authorization: Bearer $CRON_SECRET` 的请求，其余返回 401。Hobby 套餐的定时任务精度是一小时内，周日 08:00 准点要 Pro（PRD 第 8 节「成本」，升级票见 `docs/delivery/gate-3b-split.md` §5）。
- 预览部署不配 `RESEND_API_KEY`，发信只记一行日志（不带邮箱），不真发。

**(c) 退订令牌：HMAC 签名，365 天失效，密钥可轮换。**

- 令牌 = 密钥编号、订阅者 `id`、签发日期，加上用 `SUBSCRIBE_TOKEN_SECRET_<编号>` 算的 HMAC-SHA256，base64url 编码。令牌里没有邮箱。
- 签发 365 天后失效（自定：美国 CAN-SPAM 要求退订链接至少 30 天内可用；邮件会被翻出来再看，所以取一年）。
- 换密钥时加一个新编号，旧编号继续验证 365 天后删掉。
- 篡改、过期、密钥编号已删、订阅者已删除：`/unsubscribe` 页显示「这个退订链接已失效」，给联系邮箱；不透露这个地址在不在名单里。
- `GET /unsubscribe?token=…` 只显示页面，不改数据；「确认退订」按钮和邮件头的一键退订都走 `POST /api/site/unsubscribe`。

**(d) 频率限制：IP 只在内存里，邮箱按数据表算。**

- 同一 IP 每小时 5 次：在接口进程的内存里计数，1 小时过期，不落库，不写日志。多个实例各算各的，实际放行的次数可能多于 5 次。**这改了细则第 6 条的验收，待产品负责人决定**（选项见 `docs/delivery/gate-3b-split.md` §6）；Vercel 套餐确认以后，可以在防火墙加同样的规则作为第二道。
- 同一邮箱每小时 3 次：每次提交都存一条同意证据（细则第 2 条），所以数 `consent_records` 里这个邮箱最近 1 小时的条数；被限流挡掉的提交不存。
- 超过任一限制返回 429。不用验证码（`quality-terms` X5）。

**(e) 删除：一条命令，30 天内做完。**

按邮箱删 `site.subscribers`（级联删同意证据），再调用 Resend 的接口删能删的。Resend 不存名单（(b)），留下的只有发送日志：删除那张票查明所用 Resend 套餐的日志保留期并写进运行手册和隐私评审清单；保留期超过 30 天，就和 PRD 第 8 节「隐私」「删除订阅记录后 Resend 里查不到这个邮箱」不一致，算需求偏差，交产品负责人和律师。运行手册另写一条查询命令：按邮箱拿出这个订阅者全部的同意证据。

## 考虑过的其他做法

| 做法 | 为什么不选 |
|---|---|
| 放进 Veli 的 Supabase 项目 | 主站要拿那个项目的连接串，健康数据和订阅名单在同一个权限边界里 |
| 用 Resend 的受众和广播管理退订 | 退订在 Resend 那边，`/unsubscribe` 页和同意证据要两边对账；Resend 里多一份名单，删除要删两处 |
| 用 Redis 之类的外部存储做 IP 限流 | 多一家服务商，隐私评审的第三方清单多一行；v1 先用内存计数加邮箱限流和一键退订，上线两周后按数据复核 |
| 表放在 `public`，靠 `revoke` 加策略挡公开接口 | 少一道：只要有人改了 Supabase 的默认授权或加错一条策略，公开接口就能读到邮箱；单独的 schema 不暴露，公开接口从根上看不到 |
| 运行时沿用 `src/lib/db.ts` 和 `DATABASE_URL` | 那是沙箱预置的模块，登录模块也读 `DATABASE_URL`；所有者连接串进了运行时，行级安全形同虚设；缺变量时静默落到内存库，订阅会丢 |
| 令牌不失效 | 泄露的旧链接永远可用；失效以后还有联系邮箱这条路 |

## 后果

- 新增密钥：Vercel 生产环境里的 `SITE_DB_URL`、`RESEND_API_KEY`、`RESEND_WEBHOOK_SECRET`、`SUBSCRIBE_TOKEN_SECRET_<编号>`、`CRON_SECRET`、首页本周文章的部署钩子地址；GitHub Actions 里的 `SITE_DB_MIGRATE_URL`。预览环境的 `SUBSCRIBE_TOKEN_SECRET_1`、`CRON_SECRET` 用另一组值。值不进代码、文档和提交信息；谁配见 `docs/delivery/gate-3b-split.md` §5。
- Supabase 免费项目闲置会被暂停：上线后每 10 分钟的健康检查（ADR-0005）会访问数据库；上线前生产库没有访问，开工前按 Supabase 当前的规则核实。
- 第三方仍是 PRD 列的那几家（Vercel、Supabase、Resend、Cloudflare），隐私政策不用多写一家。
- IP 限流是每个实例各算，挡不住分布很广的滥用；靠一键退订、退信停发兜底。观察者上线两周后按 Resend 的退信和投诉数复核。
- 实现落在关口三 b 拆出的订阅票里（见 `docs/delivery/gate-3b-split.md`），每张都打 `risk:high`，过安全评审。
