# 上线步骤：feature/v1 → site → velicoach.com

> 关口三 b 第二轮冷审 P1-3。上线票是 #66（`ready-for-human`，主会话 + 产品负责人）。关口四的检查清单在 `docs/standards/pipeline.md` §2.3，分「合并前」「切换后」两段；本页写顺序和谁做。

**主站上线不早于 Veli B1 上线（thin-muscle-coach#72）。** Veli 的生产分支是 `main`，B1 的票（含 thin-muscle-coach#185、thin-muscle-coach#101）只合并进 `feature/b1`，thin-muscle-coach#72 合并后才到 Veli 生产；主站的 rewrites 代理的是 Veli 生产。产品负责人 2026-11-09 定：主站和 Veli B1 一起上线，不把 thin-muscle-coach#185、thin-muscle-coach#101 单独紧急发布。
> 回退的做法也在本页；`docs/deploy.md` 只放部署的说明和指向这里的链接。

## 谁做什么

| 角色 | 做的事 |
|---|---|
| 产品负责人 | 关口四「合并前」的确认；把 `feature/v1` 合并进 `site`（`site` 上线前只接受这一次合并，`pipeline.md` §5.1）；真机、RSS 阅读器、告警邮件这几项人工核对；订阅的上线开关打开那天合并打开的 PR、核对真实邮件 |
| 主会话 | 手动触发两个工作流；跑核对脚本；用 Vercel 的接口挪域名、改监控目标；贴结果；判断要不要回退 |
| Veli 的主会话 | 按 thin-muscle-coach#213 准备切换 PR（base 是 Veli 的 `main`），由产品负责人在「切换」一步合并 |

## 开始之前（一次性）

0. **工作流已就位**：主会话的 `chore/` PR 已把 `site-db-migrate`、`site-monitor`、`site-audit` 三个工作流文件放进默认分支 `feature/v1`（手动触发执行的是所选分支上的文件）。工作流文件只由主会话改。

## 合并前（在 `feature/v1` 的预览上）

1. **首次生产迁移**：先核对 Environment `site-db` 的部署分支只允许 `site`、`feature/v1`，密钥 `SITE_DB_MIGRATE_URL` 已配（#40）；核对前不触发。然后主会话手动触发 `site-db-migrate`（`ref=feature/v1`），再做 #67 的核对。不过就停在这里修。
2. **监控演练**：主会话手动触发 `site-monitor`（`ref=feature/v1`），`target` 填允许清单内、必定失败的地址 `https://velicoach-drill-404.vercel.app`（先请求一次确认返回 404；允许清单外的地址脚本直接拒绝，演练不了告警，ADR-0005 (a)），连跑两次，开出一个标题以「主站告警：」开头的 issue；产品负责人回复收到告警邮件；关掉这个 issue。
3. **关口四「合并前」清单**全部通过（`pipeline.md` §2.3）。
4. **Veli 侧就绪**：thin-muscle-coach#72 已合并，Veli 生产上 `/body`、`/en/body`、法务页返回 200（直接请求 Veli 项目的生产域名）；thin-muscle-coach#185、thin-muscle-coach#101 已关；thin-muscle-coach#213 的切换 PR 已开、以 Veli 的 `main` 为 base、评审通过、还没合并。
4a. **导航约定检查**（ADR-0003 (b)，PRD F09）：主站不打包导航和页脚给 Veli，/body 的导航由 Veli 自己做。主会话用 Playwright 从主站预览打开 `/body` 和 `/en/body`，逐条检查三件事，结果贴 #66：
   - 站标回首页：左上角站标的链接是 `/`（英文页是 `/en/`）；
   - 三站的链接：导航里有站稳、看清、动手三个链接，地址是 `/body`、`/mind`、`/build`（英文加 `/en`），站稳高亮；
   - 语言和外观的记忆共用：在主站把语言切到英文、外观切到深色，本机的 `vc-lang` 是 `en`、`vc-theme` 是 `dark`，再打开 /body 是英文、深色；在 /body 切回去，回到主站也跟着变。取值只有 `zh` / `en` 和 `auto` / `light` / `dark`。
   有一条不过就不切换域名：在 thin-muscle-coach#185 写明哪一条，等 Veli 改完重查。
4b. **订阅的上线开关默认关**：核对生产配置里开关的值是关；`SITE_DB_URL`、`RESEND_API_KEY`、`RESEND_WEBHOOK_SECRET`、`MAIL_TICKET_READ_TOKEN` 里已经配了的，范围都只有 Production（只看变量名和范围，不打印值）；律师对「授权与确认」表和法务页的书面意见已经回来、没有未处理的项，#98 已关闭（产品负责人 2026-11-11 定：拿到意见再上线，需求第 91 条）；四项条件（见下面「订阅的上线开关」）到齐以前不打开。开关关着不挡上线。预览上开关恒为开，订阅的全流程在预览上照常验（`subscribe` 事件也在预览上触发，PRD F29）。
5. 产品负责人在 #66 回复「确认上线」。

## 合并

6. 产品负责人在 GitHub 上把 `feature/v1` 合并进 `site`（合并脚本只合并进集成分支，不做这一步，`pipeline.md` §5.1）。
7. 主站生产部署 READY；`site-db-migrate` 用 `ref=site` 再跑一次（没有新迁移时什么也不改），#67 的查询再跑一次。
8. `/api/site/health` 返回 200。订阅的上线开关关着时它只查数据库，不查 `RESEND_API_KEY`（ADR-0005 (c)）。返回 503 时先看 Supabase 项目是不是被暂停了（免费项目闲置会暂停）：暂停了就在 Supabase 后台恢复，等项目起来再请求一次。
9. 主会话用 #62 的核对脚本对**主站项目的生产域名**（`*.vercel.app`，不是某一次部署的生成地址）跑一遍：路由表每一行、`/api/site/health`。全过以后，主会话把仓库变量 `MONITOR_TARGET` 设成这个生产域名，再进下一步。在这之前不设：上线合并前生产部署没有 `/api/site/health`，提前设会误报并开告警 issue。

## 切换

10. 主会话用 Vercel 的接口把 `velicoach.com` 从 Veli 项目移除、挂到主站项目；同时产品负责人把 thin-muscle-coach#213 的切换 PR 合并进 Veli 的 `main`，Veli 生产部署 READY。
11. 主会话把仓库变量 `MONITOR_TARGET` 从主站项目的生产域名（第 9 步设的）改成 `https://velicoach.com`。

## 切换后（60 分钟内做完）

12. 主会话用核对脚本对 `velicoach.com` 跑一遍路由表每一行；迁入的 5 篇文章 `/mind/<slug>` 和它们的中英旁白都返回 200（#32 的清单）。
13. Playwright 经 `velicoach.com` 打开 `/`、`/body`、`/en/body`、`/app`：页面发出的请求里 4xx、5xx 为 0；首页「为什么是肌肉」的研究卡锚点在（研究卡只在首页，/body 不放）；第 4a 步的导航约定三件事在 `velicoach.com` 上再查一遍。
13a. 订阅的上线开关关着时：首页和各页没有订阅条和页底订阅，首屏底部是 RSS 链接；`POST https://velicoach.com/api/site/subscribe` 返回 404，订阅库里没有新增的行。开关已经打开的，改做下面「订阅的上线开关」第 4 步的验证。
14. `pipeline.md` §2.3「切换后」清单逐项做完，结果贴 #66。
15. 任何一项不过：按下面的回退步骤恢复，在 #66 写明哪一项、原因、下一次上线前要改什么。

## 回退（5 分钟内）

1. Vercel：把 `velicoach.com` 从主站项目移除、挂回 Veli 项目。
2. Veli：产品负责人在 Veli 的 `main` 上 revert thin-muscle-coach#213 的切换 PR（恢复 `/` 到 `/body` 的临时跳转和 Veli 自己的 robots.txt），Veli 生产部署 READY。
3. `MONITOR_TARGET` 改回主站项目的生产域名。
4. `site` 上的主站代码不用回退：没有域名指向它，访客看不到。订阅库里已经写进的订阅照常保留。

## 订阅的上线开关

站点配置的一项，默认关（PRD「订阅的细则」第 16 条；`pipeline.md` §5.1）。它不挡上线：上线那天条件没齐，就关着上线，订阅后开。打开这件事是 #89。

**最早在域名切换完成以后打开**（上面第 10–14 步做完）。合并（第 6 步）到切换（第 10 步）之间 `velicoach.com` 还指向 Veli：这时有人订阅，欢迎邮件里的退订链接、邮件头的一键退订和 Resend 的回调都落到 Veli，退订不生效。所以条件再齐，也等切换后的清单全过再开。

**关着时**：不渲染订阅条和页底订阅；首屏底部原来放订阅的位置换成 RSS 链接（页脚的 RSS 照常）；生产的订阅接口返回 404，不写库。预览恒为开。

**四项条件，齐了才打开**，证据贴在打开开关的 PR 里（#89）：

| 条件 | 证据 |
|---|---|
| 律师意见 | 「订阅的细则」第 14 条三件事的书面意见，没有未处理的项 |
| 发信域名和 DNS | news.velicoach.com 的 SPF、DKIM、DMARC 记录在 Resend 后台都是已验证 |
| 通讯地址 | 发件人的实际通讯地址已定，写进邮件模板的页脚 |
| Veli 隐私政策写明订阅 | Veli 生产上的隐私政策（中英两版）写了订阅收什么、存在哪、交给哪些服务商、怎么退订和删除 |

**打开的步骤**

1. 主会话提一个 `chore/` PR，只把配置里的开关改成开；PR 说明里逐项贴上表的证据，打 `owner:merge`，附决策简报（涉及法律责任，`pipeline.md` §5.1）。
2. 产品负责人合并；生产部署 READY。
3. 核对生产环境变量 `RESEND_API_KEY`、`RESEND_WEBHOOK_SECRET`、`SUBSCRIBE_TOKEN_SECRET_<编号>`、`CRON_SECRET`、`MAIL_TICKET_READ_TOKEN`（发送任务读邮件票用的只读 GitHub 令牌，只有读 issue 的权限）都已配，范围都只有 Production；`SUBSCRIBE_FORCE_OFF` 没有设；单独的 GitHub Environment `site-mail-log` 里有 `SITE_DB_MAIL_LOG_URL`（#96），`site-db` 里没有它；工作流 `site-mail-log` 已在默认分支上，放入连接串之前它的文件过了一次独立的安全评审（ADR-0004 (b)，#89）。
4. 验证：各页出现订阅条和页底订阅，首屏底部是订阅入口；用真实邮箱订阅一次，原位显示「已订阅，每周日见」，收到欢迎邮件；在 Gmail「显示原始邮件」里 SPF、DKIM、DMARC 三项都是 PASS，页脚有通讯地址，邮件头有 `List-Unsubscribe` 和 `List-Unsubscribe-Post`；点一键退订生效；订阅库里有这一条同意证据；`/api/site/health` 返回 200，正文里有发信配置一项（开关开着以后它照查）。结果贴在 PR 上。
5. 订阅数从这一天算起（PRD 第 1 节）。

**再关上**。先看邮件是不是已经在发，再选办法：

| 情况 | 第一步 |
|---|---|
| 一期邮件已经在发（周日 08:00 以后、还没发完），要立刻停 | 两件事一起做。一，直接在 Resend 后台删掉发信的 API key（下面第 3 条），不必先试别的：环境变量要重新部署才生效，管不到已经在跑的发送。二，同时给当期邮件票打 `agent:hold`（第 2 条）：另一种语言是相隔十几小时的另一次发送（中文按北京时间周日 08:00，英文按美国东部时间周日 08:00），不打的话 key 一恢复它就照原样发出。key 等确认邮件文件没问题以后再恢复 |
| 一期邮件已经在发，不必一秒都不等 | 给当期邮件票打 `agent:hold` 或关掉它（第 2 条）：发送任务每批发出前重读邮件票，在批与批之间停下 |
| 还没开始发，要马上停收新订阅、之后也不发 | 紧急关 `SUBSCRIBE_FORCE_OFF`（第 1 条） |
| 只想让还没开始的这一期不发 | 给当期邮件票打 `agent:hold` 或关掉它（第 2 条） |
| 不急：验证不过，或律师、退信数据要求停收 | 主会话提 PR 把开关改回关（类别和谁合并按 `pipeline.md` §5.1），在 #13 告知产品负责人 |

1. **紧急关**（ADR-0004「后果」）：产品负责人在 Vercel 后台给主站项目的 Production 加环境变量 `SUBSCRIBE_FORCE_OFF`，值填 1，点重新部署。任何非空且不是 `0` 的值都算关，填错了也是关。部署 READY 以后不管配置是什么，订阅都算关，一个开关管两件事：订阅表单不显示、`POST /api/site/subscribe` 返回 404；之后开跑的发送任务也不发。退订和 Resend 回调照常可用。它只能关、不能开，而且**要重新部署才生效，管不到已经在跑的那一次发送**。事后主会话补一个把配置改回关的 PR，合并后再把这个变量删掉。
2. **当期邮件票打 `agent:hold`，或关掉它**：还没开始的一期不发；已经在发的一期，发送任务每批发出前重读邮件票，会在下一批之前停下，已发的封数记进发送记录。这一期不补发。
3. **删掉 Resend 的 API key**：在 Resend 后台删掉发信的 API key，发送马上停。Resend 没有「停用」，删了撤不回。恢复之前先确认：邮件文件没问题，或当期邮件票已经打了 `agent:hold`（不然还没开跑的另一种语言会照原样发出）。恢复要三步：在 Resend 新建一个只能用 news.velicoach.com 发信的 key，更新 Vercel Production 的 `RESEND_API_KEY`，重新部署。删 key 时正在发的那一期按已发算、失败数照实记，这一期不补发；欢迎邮件在恢复以前也发不出去。

关上以后，已有的订阅和同意证据保留；开关关着时发送任务不发任何邮件（#49），也不排邮件、不开邮件票（`pipeline.md` §5.1「每周内容」第 3 条）。

**一期出了错要重来怎么办**（例如被拦停、出错停下，或占位行是别人伪造的）：发送记录表只追加，谁都不删行，包括表所有者。重来一律用新的期号、新的邮件票、新的邮件文件，排到下一个周日，照每周的流程走一遍（`docs/delivery/loops/content-runner.md` 周五）；旧的一期不复活。期号只是个递增的整数（1 到 9999），跳号没有影响。在 #13 记一笔：哪一期作废、为什么、新的一期是第几期。

## 密钥泄露了怎么办

发现或怀疑某个密钥泄露（进了日志、票、提交，或被别人看到）时，按下表换掉。换之前不用先确认有没有被用过。值不贴在票、评论和聊天里；做完在 #13 记一句换了哪一个、什么时候。

| 密钥 | 泄露了能做什么 | 在哪换 | 换完要做什么 |
|---|---|---|---|
| `CRON_SECRET` | 它是发送接口唯一的身份认证：拿到它就能触发定时发送，但只在发送窗口内有效：窗口外带着它也不发、不写占位行；窗口内只能发排定在当天的那一期，只发一次的占位行仍然拦着重发 | 主会话用 Vercel 的环境变量接口生成新值，Production、Preview 各一个 | 重新部署；Vercel 的定时任务用新值；核对带旧值的请求返回 401 |
| `SITE_DB_URL`（`site_api` 的连接串） | 读写订阅名单、读和新增同意证据（删不掉单条同意证据）；往发送记录表里插行：给还没发的期号预先插占位行，那一期就永远发不出去；伪造结果行，让邮件票里的记录变假。`site_api` 对发送记录表没有 delete；伪造的行不清（见上面「一期出了错要重来怎么办」），被占的期号作废 | 产品负责人在 Supabase 的 SQL 编辑器里 `alter role site_api password …`，再更新 Vercel Production 的 `SITE_DB_URL` | 重新部署；`/api/site/health` 返回 200；按 #67 的查询核对一遍；用表所有者的身份（Supabase 的 SQL 编辑器）查发送记录表：清点发送记录表时不信行自己的字段（期号、时间、封数都能伪造）：泄露可能发生以来的每一期每种语言，拿 Resend 的发送日志和 `subscribers` 里 `last_issue_sent` 等于这一期的人数对账，对不上的行列出来，不删，在 #13 记一笔；被占的期号作废，之后的期号跳过它们。伪造的 `complete` 会让邮件票里出现假的「发完」记录，由产品负责人在那张票里补一条说明（他的账号在锁定、已关的票上也能评论）；名单可能被读过，按隐私政策和律师的意见判断要不要通知 |
| `SITE_DB_MIGRATE_URL`（表所有者的连接串） | 改表结构、读写全部数据 | 产品负责人在 Supabase 后台重置数据库密码，更新 Environment `site-db` 的密钥 | 手动触发一次 `site-db-migrate` 确认还能跑；#67 的查询全部重跑；同上判断要不要通知 |
| `SITE_DB_MAIL_LOG_URL`（`site_mail_log` 的连接串） | 只能读发送记录表的七列（期号、语言、`kind`、`outcome`、时间、封数、失败数），没有邮箱 | 产品负责人 `alter role site_mail_log password …`，更新 Environment `site-mail-log` 的密钥 | 手动触发一次 `site-mail-log` 确认还能跑 |
| `MAIL_TICKET_READ_TOKEN` | 只读本仓库的 issue（仓库是公开的，读到的都是公开内容） | 产品负责人在 GitHub 上撤销这个令牌，新建一个同样权限的，更新 Vercel Production | 重新部署；按 #96 的核对再做一遍（读返回 200、写返回 403） |
| `RESEND_API_KEY` | 用 news.velicoach.com 发信 | 产品负责人在 Resend 后台删掉旧的，新建一个只能用这个域名发信的，更新 Vercel Production | 重新部署；发一封测试的欢迎邮件；看 Resend 的发送日志里有没有不是我们发的 |
| `RESEND_WEBHOOK_SECRET` | 伪造退信、投诉回调，让地址被停发 | 产品负责人在 Resend 后台重新生成回调的签名密钥，更新 Vercel Production | 重新部署；带旧签名的回调返回 401；核对最近的停发记录 |
| `SUBSCRIBE_TOKEN_SECRET_<编号>` | 伪造退订令牌，替别人退订 | 主会话加一个新编号的密钥，把泄露的那个编号删掉（ADR-0004 (c)） | 重新部署；用旧编号签的退订链接会显示「这个退订链接已失效」，这是预期的；下一期邮件用新编号签 |

## 上线后（当天）

16. 切换后的清单全过以后，主会话把 GitHub 默认分支改回 `site`，删掉 `feature/v1`，同时把 `feature/v1` 从各个 Environment（`site-db`，以及已经建了的 `site-mail-log`）的允许分支里去掉，只留 `site`：不然这个分支名以后被重新建起来，又能读到里面的密钥。核对：`gh api repos/madlouse/velicoach/environments/<名字>/deployment-branch-policies --jq '.branch_policies[].name'` 只有 `site`。合并脚本读到 `feature/v1` 404 就只合并进 `site`（`pipeline.md` §5）。开着的 PR 把 base 改成 `site`。工作流文件已随上线合并进了 `site`，确认定时运行改在 `site` 上触发。
