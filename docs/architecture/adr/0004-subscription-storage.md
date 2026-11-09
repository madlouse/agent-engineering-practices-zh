# 0004 订阅的存储、发信、退订令牌和频率限制

- 状态：已采纳（待事后确认，2026-11-09，关口三 b 拆票时写）
- 关联：主站 PRD v1.2 F07 和「订阅的细则」第 2–15 条（第 8 条要求在关口三 b 写 ADR 定表结构和同步方式，第 9 条要求定令牌怎么签、多久失效）；ADR-0003（`/api/site/*`）；PRD 第 3 节路由表 `/unsubscribe`；第三轮冷审 P2-4

## 背景

订阅只收邮箱，提交即订阅（细则第 1 条）。要存的有两类：名单（谁在订阅、什么语言、什么状态）和同意证据（每次提交五项）。退订要能一步生效，邮件安全扫描预取链接又不能误退。频率限制要挡住滥用，IP 不能落库（细则第 6 条）。这些都涉及邮箱，按 PRD 第 8 节「安全」打 `risk:high`。

## 决定

**(a) 存储：主站自己的 Supabase 项目，两张表，开行级安全，不用 service_role。**

- 主站单独一个 Supabase 项目（免费额度），不放进 Veli 的项目：Veli 的项目里有健康数据，主站拿不到它的任何密钥。
- 连接沿用仓库已有的数据库层：构建时 `npm run db:migrate` 用 `DATABASE_URL` 跑迁移；运行时接口用另一个连接串 `SITE_DB_URL`，登录角色 `site_api`，只有这两张表的读、写、删权限。两个连接串只放在 Vercel 的生产环境变量里。
- 预览部署不配这两个变量，数据库层自动用内存里的 PGLite（`src/lib/db.ts` 已有），迁移在启动时执行；预览上的订阅不写真实名单。
- 两张表都开行级安全，不给 `anon`、`authenticated` 任何策略和授权：Supabase 的公开接口读写都被拒，只有服务端的 `site_api` 能读写。

| 表 | 字段 |
|---|---|
| `subscribers` | `id`（uuid）、`email`（小写后唯一）、`lang`（zh / en）、`status`（active / unsubscribed / stopped_hard_bounce / stopped_complaint / stopped_soft_bounce）、`soft_bounce_streak`、`created_at`、`updated_at`、`unsubscribed_at`、`stopped_at` |
| `consent_records` | `id`、`subscriber_id`（删订阅者时级联删除）、`email`、`submitted_at`（UTC）、`lang`、`path`（不带查询参数）、`utm_source`、`form_copy_version` |

状态怎么变只写在细则第 4、7、15 条，代码按那里实现，这里不重写。

**(b) 发信：从数据表直接发，不在 Resend 里存第二份名单。**

- 发送前从 `subscribers` 读状态为 active 的地址，按订阅语言用 Resend 的批量发送接口发；这就是细则第 8 条的「发送前同步名单」。Resend 里不建受众（Audience），删除时少一处要删。
- 每封邮件带自己的退订令牌，放进 `List-Unsubscribe`、`List-Unsubscribe-Post` 两个邮件头和正文底部的退订链接。
- Resend 的打开追踪和点击追踪关闭。发信域名 news.velicoach.com（PRD 第 10 节）。
- 回调 `POST /api/site/resend` 先校验 Resend 的签名（Svix），再按事件编号去重，写回状态。
- 定时：Vercel Cron 触发发送；英文版按 America/New_York 的 08:00 换算，夏令时由处理函数判断。Hobby 套餐的定时任务精度是一小时内，周日 08:00 准点要 Pro（PRD 第 8 节「成本」，产品负责人待确认）。
- 预览部署不配 `RESEND_API_KEY`，发信只记一行日志（不带邮箱），不真发。

**(c) 退订令牌：HMAC 签名，365 天失效，密钥可轮换。**

- 令牌 = 密钥编号、订阅者 `id`、签发日期，加上用 `SUBSCRIBE_TOKEN_SECRET_<编号>` 算的 HMAC-SHA256，base64url 编码。令牌里没有邮箱。
- 签发 365 天后失效（自定：美国 CAN-SPAM 要求退订链接至少 30 天内可用；邮件会被翻出来再看，所以取一年）。
- 换密钥时加一个新编号，旧编号继续验证 365 天后删掉。
- 篡改、过期、密钥编号已删、订阅者已删除：`/unsubscribe` 页显示「这个退订链接已失效」，给联系邮箱；不透露这个地址在不在名单里。
- `GET /unsubscribe?token=…` 只显示页面，不改数据；「确认退订」按钮和邮件头的一键退订都走 `POST /api/site/unsubscribe`。

**(d) 频率限制：IP 只在内存里，邮箱按数据表算。**

- 同一 IP 每小时 5 次：在接口进程的内存里计数，1 小时过期，不落库，不写日志。多个实例各算各的，实际放行的次数可能多于 5 次（自定，接受这个误差）；Vercel 套餐确认以后，可以在防火墙加同样的规则作为第二道。
- 同一邮箱每小时 3 次：每次提交都存一条同意证据（细则第 2 条），所以数 `consent_records` 里这个邮箱最近 1 小时的条数；被限流挡掉的提交不存。
- 超过任一限制返回 429。不用验证码（`quality-terms` X5）。

**(e) 删除：一条命令，30 天内做完。**

按邮箱删 `subscribers`（级联删同意证据），再调用 Resend 的接口删能删的；Resend 发送日志的保留期写进隐私评审清单。运行手册随删除那张票写进 `docs/`。

## 考虑过的其他做法

| 做法 | 为什么不选 |
|---|---|
| 放进 Veli 的 Supabase 项目 | 主站要拿那个项目的连接串，健康数据和订阅名单在同一个权限边界里 |
| 用 Resend 的受众和广播管理退订 | 退订在 Resend 那边，`/unsubscribe` 页和同意证据要两边对账；Resend 里多一份名单，删除要删两处 |
| 用 Redis 之类的外部存储做 IP 限流 | 多一家服务商，隐私评审的第三方清单多一行；v1 先用内存计数加邮箱限流和一键退订，上线两周后按数据复核 |
| 令牌不失效 | 泄露的旧链接永远可用；失效以后还有联系邮箱这条路 |

## 后果

- 新增环境变量：`DATABASE_URL`、`SITE_DB_URL`、`RESEND_API_KEY`、`RESEND_WEBHOOK_SECRET`、`SUBSCRIBE_TOKEN_SECRET_<编号>`，只在 Vercel 生产环境；值不进代码、文档和提交信息。
- 第三方仍是 PRD 列的那几家（Vercel、Supabase、Resend、Cloudflare），隐私政策不用多写一家。
- IP 限流是每个实例各算，挡不住分布很广的滥用；靠一键退订、退信停发兜底。观察者上线两周后按 Resend 的退信和投诉数复核。
- 实现落在关口三 b 拆出的订阅票里（见 `docs/delivery/gate-3b-split.md`），每张都打 `risk:high`，过安全评审。
