# 0004 订阅的存储、发信、退订令牌和频率限制

- 状态：已采纳（产品负责人 2026-11-09 确认；按关口三 b 冷审 P0-1、P1-1 修订；迁移工作流、公开仓库的限制按第二轮冷审 P1-1、P2-6–P2-9、P2-15 补；工作流由主会话维护、迁移约定按第三轮冷审 P1-A、P2-8 补）
- 关联：主站 PRD v2.0 F07 和「订阅的细则」第 1–17 条（第 8 条要求写 ADR 定表结构和同步方式，第 9 条要求定令牌怎么签、多久失效；第 12 条每期的排定和取消、第 17 条邮件内容见 (b)；第 16 条订阅的上线开关见「后果」）；ADR-0003（`/api/site/*`）；PRD 第 3 节路由表 `/unsubscribe`；第三轮冷审 P2-4；关口三 b 冷审 `docs/delivery/reviews/2026-11-09-gate-3b.md` P0-1、P1-2、P1-3、P2-5、P2-9

## 背景

订阅只收邮箱，提交即订阅（细则第 1 条）。要存的有两类：名单（谁在订阅、什么语言、什么状态）和同意证据（每次提交五项）。退订要能一步生效，邮件安全扫描预取链接又不能误退。频率限制要挡住滥用，IP 不能落库（细则第 6 条）。这些都涉及邮箱，按 PRD 第 8 节「安全」打 `risk:high`。

## 决定

**(a) 存储：主站自己的 Supabase 项目，表放在不对外暴露的 schema `site`，只给 `site_api` 角色写策略，不用 service_role。**

- 主站单独一个 Supabase 项目（免费额度），不放进 Veli 的项目：Veli 的项目里有健康数据，主站拿不到它的任何密钥。
- **表放在 schema `site`**，不加进 Supabase Data API 暴露的 schema 列表，公开接口（PostgREST）根本看不到它。
- **迁移里显式收回权限**：`revoke all` 收回 `anon`、`authenticated`、`public` 对 schema `site` 和其中每张表、序列的权限，不靠 Supabase 的默认授权。
- **运行时角色 `site_api`**：能登录，不是表的所有者，不带 `BYPASSRLS`；只授予 `usage on schema site` 和每张表需要的操作。
- **`site` 里的每张表都开行级安全，按表写策略，只给 `site_api` 它需要的操作**：`subscribers` 给 select、insert、update、delete；`consent_records` 给 select、insert、delete（同意证据只增不改）。策略写成 `to site_api`；发送记录表另给只读角色 `site_mail_log` 一条 select 策略（见 (b)）。除这两个角色外没有别的策略，一行也读不到。
- **三个连接串，分开用**（第三个 `SITE_DB_MAIL_LOG_URL` 只读发送记录表，见 (b)，订阅打开前才配）：
  - `SITE_DB_URL`：`site_api` 经 Supabase 连接池（事务模式，用户名是 `site_api.<项目编号>`）的连接串，只放在 Vercel 的生产环境变量里，运行时只读它。
  - `SITE_DB_MIGRATE_URL`：表所有者的连接串，只放在 GitHub 的 Environment `site-db` 里（部署分支只允许 `site`、`feature/v1`，其他分支上的工作流读不到），只由站点迁移脚本在 CI 里读；不进 Vercel，运行时拿不到。
- **迁移只走工作流 `site-db-migrate`**（`.github/workflows/site-db-migrate.yml`），构建命令里不跑迁移。触发只有两种：手动（`workflow_dispatch`）和 `push: site`（只看 `migrations/site/**`），不用 `pull_request`、`pull_request_target`。GitHub 只允许手动触发默认分支上已有的工作流，手动触发时执行的是所选分支上的那份文件。上线前默认分支是 `feature/v1`（`docs/standards/pipeline.md` §5），所以主会话的 `chore/` PR 把文件一次写全放进 `feature/v1`，上线前用 `ref=feature/v1` 手动触发，把迁移跑进生产库；上线合并把文件带进 `site`，上线后默认分支改回 `site`。上线前 `site` 上没有 `migrations/site/`，`push` 不会触发。Environment `site-db` 的部署分支限制配好并核对之前，不手动触发这个工作流（#40）。首次生产迁移后的权限核对是一张单独的票（#67）。迁移日志是公开的：`site:migrate` 不打印连接串或它的片段，驱动错误只输出类别和迁移文件名；迁移只依赖 `pg`，工作流的安装改成 `npm ci --omit=dev --ignore-scripts`（主会话改，#70 安全评审）。
- **工作流文件只由主会话维护**：`.github/workflows/` 是门槛文件，合并脚本拦住改它的票 PR，Agent 会话也没有推送工作流的权限。票只写工作流调用的脚本（`site:migrate`、`scripts/monitor/run.mjs`、`scripts/audit/run.mjs`），并用 `node --test` 断言工作流的配置。
- **迁移约定：向后兼容，先加后删。** `push: site` 触发的迁移和 Vercel 的生产构建同时开始，新代码可能比迁移先上线，旧代码也可能在迁移后还跑一会儿。所以每个迁移都要让新旧两版代码都能跑：加列、加表、加策略可以直接合；删列、改名、改类型、收紧约束拆成两次：先合并兼容的迁移和不再依赖旧结构的代码，等迁移成功、生产部署 READY，再合并删除旧结构的迁移。做不到兼容的改动，先单独合并只含迁移的 PR，等这次运行成功再合并读写新结构的代码。
- **仓库是公开的**：工作流的输入、日志和运行记录谁都看得到。所以删除订阅者、导出同意证据这类要输入邮箱的命令不做成工作流，只在产品负责人本机用 `SITE_DB_URL` 那组 `site_api` 的连接串跑（(e)）。这串连接串只存在 Vercel 的生产环境变量 `SITE_DB_URL` 里，不另存；要用时产品负责人用 `vercel env pull` 取到本机的临时文件，跑完删掉。
- **不碰沙箱契约**：运行时用一个新的服务端模块连 `SITE_DB_URL`，不读预置的 `DATABASE_URL`，不改 `src/lib/db.ts` 和 `src/lib/auth/*`（本仓库 `AGENTS.md`）。加一个检查脚本：`src/` 里读 `SITE_DB_MIGRATE_URL` 的地方为 0；读 `DATABASE_URL` 的地方除沙箱预置的 `src/lib/db.ts`、`src/lib/auth/*` 以外为 0；新模块不引用 `src/lib/db.ts`。
- **连接池的事务模式**不支持命名的预编译语句：驱动关掉它（例如 postgres.js 的 `prepare: false`），否则生产上第一次请求就报错，PGLite 上测不出来。
- **缺连接串时不假装成功**：`VERCEL_ENV=production` 而 `SITE_DB_URL` 缺失或连不上时，订阅接口返回 503，不落到内存库。只有在非生产环境（预览、本地、测试），新模块才用它自己的内存 PGLite，并在启动时执行 `migrations/site/`；PGLite 里没有 `anon`、`authenticated`、`site_api` 时先建同名的不能登录的角色，否则迁移里的 `revoke`、`grant` 会报错；预览上的订阅不写真实名单。
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
- Resend 的打开追踪和点击追踪关闭。发信域名 news.velicoach.com（`docs/prd/decisions.md`）。
- 回调 `POST /api/site/resend` 先校验 Resend 的签名（Svix），再按事件编号去重，写回状态。
- 定时：Vercel Cron 触发发送；英文版按 America/New_York 的 08:00 换算，夏令时由处理函数判断。定时接口只接受带 `Authorization: Bearer $CRON_SECRET` 的请求，其余返回 401。Hobby 套餐的定时任务精度是一小时内，周日 08:00 准点要 Pro（PRD 第 8 节「成本」，升级票见 `docs/delivery/gate-3b-split.md` §5）。
- 预览部署不配 `RESEND_API_KEY`，发信只记一行日志（不带邮箱），不真发。
- **每期一份邮件文件**（2026-11-11 补，PRD 细则第 12、17 条）：一期邮件的内容是仓库里的一份文件，由内容车道在周五合并（只用已发布的内容按固定模板拼成）；发送任务只发已经合并的那一份，不在发送时现拼正文。
- **发送前查当期的票**：周五内容车道另开一张票「订阅邮件第 N 期」。发送任务开跑前查这张票：带 `agent:hold` 或已经关闭，这一期不发，也不补发；查不到这张票或查询失败同样不发（宁可少发一期）。发送任务自己不写 GitHub；发完在票里记录并关票由一个单独的工作流做（见下面「发完由工作流在邮件票里记录」）。
- **每期每种语言只发一次**：发送任务发信前先在订阅库里按（期号，语言）写一条唯一的发送记录占位（(a) 的 schema `site` 里加一张发送记录表，期号加语言唯一，随发信的票建迁移），写不进去（已经有了）就不发；「已发」以这条记录为准，不以邮件票的状态为准。票被重开、任务被重复触发、内容推进器停摆时都不会重发。
- **按票号读票，不按标题搜**：当期邮件文件里写死邮件票的编号。发送任务按编号读票，并核对：是 issue 不是 PR、作者是仓库所有者、状态开着、没有 `agent:hold`；有一项不符就不发。另核对票标题里的期号和邮件文件的期号一致（写死的票号只能证明「这是仓库所有者开的一张 issue」）。读票用一个只读的 GitHub 令牌（进密钥清单），发送任务不写 GitHub。
- **发完由工作流在邮件票里记录**（2026-11-11 定，关口三 b 冷审 P1-10 的做法 (b)）：一个 GitHub Actions 工作流 `site-mail-log`（主会话维护，跑在 Environment `site-db` 里）用只读角色 `site_mail_log` 的连接串 `SITE_DB_MAIL_LOG_URL` 读发送记录表，只取期号、语言、发出时间、封数、失败数五项，用工作流自带的 `GITHUB_TOKEN`（`issues: write`）按邮件文件里的票号在邮件票里写一条评论（首行 `<!-- vc-bot role=邮件记录 -->`）并关票；这一期没发就只写没发的原因。**写票之前的核对**：邮件文件里的票号是内容车道能改的数据，工作流又拿着能写票的令牌，所以写评论、关票之前用和发送任务同一套核对：是 issue 不是 PR、作者是仓库所有者、标题是「订阅邮件第 N 期」、标题里的期号和邮件文件的期号一致；有一项不符就不写不关，只在工作流日志里报错。工作流照迁移工作流的加固写法（#73）：action 固定到完整的提交 SHA、checkout 不留凭据、安装不跑安装脚本；它调用的 `scripts/mail-log/` 进合并脚本的高风险文件清单，改它的 PR 都要安全评审（#91）。`site_mail_log` 不带 `BYPASSRLS`，只有发送记录表的 select 授权和策略，读不到 `subscribers` 和 `consent_records`。角色由迁移建成不能登录的（`nologin`），授权和策略也写在迁移里，这样上线前的首次生产迁移不依赖任何人工步骤；订阅打开前，产品负责人只做一件事：把它改成能登录、设密码，把连接串放进 `site-db` 环境（#96）。不为这件事加公开接口，内容推进器不读发送记录、也拿不到任何数据库连接串。没有选的两种做法：`/api/site/` 下加只读接口（多一个公开接口和一个密钥）；发送任务把这五项写进运行时日志由推进器读（依赖日志保留期）。
- **发送时再核对一遍条目**：邮件里链到的内容已撤下，去掉那一条；去掉以后没有条目，这一期不发。

**(c) 退订令牌：HMAC 签名，365 天失效，密钥可轮换。**

- 令牌 = 密钥编号、订阅者 `id`、签发日期，加上用 `SUBSCRIBE_TOKEN_SECRET_<编号>` 算的 HMAC-SHA256，base64url 编码。令牌里没有邮箱。
- 签发 365 天后失效（自定：美国 CAN-SPAM 要求退订链接至少 30 天内可用；邮件会被翻出来再看，所以取一年）。
- 换密钥时加一个新编号，旧编号继续验证 365 天后删掉。
- 篡改、过期、密钥编号已删、订阅者已删除：`/unsubscribe` 页显示「这个退订链接已失效」，给联系邮箱；不透露这个地址在不在名单里。
- `GET /unsubscribe?token=…` 只显示页面，不改数据；「确认退订」按钮和邮件头的一键退订都走 `POST /api/site/unsubscribe`。

**(d) 频率限制：IP 只在内存里，邮箱按数据表算。**

- 同一 IP 每小时 5 次：在接口进程的内存里计数，1 小时过期，不落库，不写日志。多个实例各算各的，实际放行的次数可能多于 5 次。产品负责人 2026-11-09 同意按实例计数，PRD 细则第 6 条已写明；Vercel 套餐确认以后，可以在防火墙加同样的规则作为第二道。
- 同一邮箱每小时 3 次：每次提交都存一条同意证据（细则第 2 条），所以数 `consent_records` 里这个邮箱最近 1 小时的条数；被限流挡掉的提交不存。
- 超过任一限制返回 429。不用验证码（`quality-terms` X5）。

**(e) 删除：一条命令，30 天内做完。**

按邮箱删 `site.subscribers`（级联删同意证据），再调用 Resend 的接口删能删的。命令在产品负责人本机用 `site_api` 的连接串跑（`site_api` 有两张表的 delete 授权和策略），不用所有者连接串，也不做成 GitHub Actions 的工作流：仓库是公开的，运行的输入和日志会泄露邮箱。Resend 不存名单（(b)），留下的只有发送日志：删除那张票查明所用 Resend 套餐的日志保留期并写进运行手册和隐私评审清单；保留期超过 30 天，就和 PRD 第 8 节「隐私」「删除订阅记录后 Resend 里查不到这个邮箱」不一致，算需求偏差，交产品负责人和律师。运行手册另写一条查询命令：按邮箱拿出这个订阅者全部的同意证据。

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

- 新增密钥：Vercel 生产环境里的 `SITE_DB_URL`、`RESEND_API_KEY`、`RESEND_WEBHOOK_SECRET`、`SUBSCRIBE_TOKEN_SECRET_<编号>`、`CRON_SECRET`、读邮件票用的只读 GitHub 令牌 `MAIL_TICKET_READ_TOKEN`（只给读 issue 的权限）；GitHub Actions（Environment `site-db`）里的 `SITE_DB_MIGRATE_URL` 和只读角色 `site_mail_log` 的连接串 `SITE_DB_MAIL_LOG_URL`。预览环境的 `SUBSCRIBE_TOKEN_SECRET_1`、`CRON_SECRET` 用另一组值。值不进代码、文档和提交信息；谁配见 `docs/delivery/gate-3b-split.md` §5。
- 订阅的上线开关（PRD 细则第 16 条）：站点配置的一项，默认关。关着时生产的订阅接口返回 404、不写库，页面不渲染订阅条和页底订阅；预览恒为开。打开的条件和步骤见 `docs/delivery/launch-runbook.md`「订阅的上线开关」；最早在域名切换完成以后打开。
- 紧急关（2026-11-11 补，PR #84 安全评审的建议）：读开关的函数另读环境变量 `SUBSCRIBE_FORCE_OFF`，值是 `1` 时不管站点配置是什么都算关，只能关、不能开。产品负责人在 Vercel 后台设上并点重新部署就生效，不用等 PR、评审和合并。一个开关管两件事，因为接口、页面和发送任务调的是同一个函数：订阅表单不显示、订阅接口返回 404，发送任务也不发；退订和 Resend 回调照常可用。只想让某一期不发，给当期邮件票打 `agent:hold`（发送任务只在开跑前查一次，拦得住还没开始的一期）。最后的办法是在 Resend 后台删掉 API key：Resend 没有「停用」，删了撤不回，恢复要新建一个 key、更新 Vercel 的 `RESEND_API_KEY` 并重新部署；发送任务是先写占位再发，删 key 以后正在发的这一期会记成已发、失败数照实记，这一期不补发。
- Supabase 免费项目闲置会被暂停：上线后每 10 分钟的健康检查（ADR-0005）会访问数据库；上线前生产库没有访问，开工前按 Supabase 当前的规则核实，上线步骤里核对项目没有被暂停（`docs/delivery/launch-runbook.md`）。
- 第三方仍是 PRD 列的那几家（Vercel、Supabase、Resend、Cloudflare），隐私政策不用多写一家。
- IP 限流是每个实例各算，挡不住分布很广的滥用；靠一键退订、退信停发兜底。观察者上线两周后按 Resend 的退信和投诉数复核。
- 实现落在关口三 b 拆出的订阅票里（见 `docs/delivery/gate-3b-split.md`），每张都打 `risk:high`，过安全评审。
