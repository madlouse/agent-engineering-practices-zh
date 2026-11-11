# 上线步骤：feature/v1 → site → velicoach.com

> 关口三 b 第二轮冷审 P1-3。上线票是 #66（`ready-for-human`，主会话 + 产品负责人）。关口四的检查清单在 `docs/standards/pipeline.md` §2.3，分「合并前」「切换后」两段；本页写顺序和谁做。

**主站上线不早于 Veli B1 上线（thin-muscle-coach#72）。** Veli 的生产分支是 `main`，B1 的票（含 #185、#101）只合并进 `feature/b1`，#72 合并后才到 Veli 生产；主站的 rewrites 代理的是 Veli 生产。产品负责人 2026-11-09 定：主站和 Veli B1 一起上线，不把 #185、#101 单独紧急发布。
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
4. **Veli 侧就绪**：thin-muscle-coach#72 已合并，Veli 生产上 `/body`、`/en/body`、法务页返回 200（直接请求 Veli 项目的生产域名）；#185、#101 已关；#213 的切换 PR 已开、以 Veli 的 `main` 为 base、评审通过、还没合并。
4a. **导航约定检查**（ADR-0003 (b)，PRD F09）：主站不打包导航和页脚给 Veli，/body 的导航由 Veli 自己做。主会话用 Playwright 从主站预览打开 `/body` 和 `/en/body`，逐条检查三件事，结果贴 #66：
   - 站标回首页：左上角站标的链接是 `/`（英文页是 `/en/`）；
   - 三站的链接：导航里有站稳、看清、动手三个链接，地址是 `/body`、`/mind`、`/build`（英文加 `/en`），站稳高亮；
   - 语言和外观的记忆共用：在主站把语言切到英文、外观切到深色，本机的 `vc-lang` 是 `en`、`vc-theme` 是 `dark`，再打开 /body 是英文、深色；在 /body 切回去，回到主站也跟着变。取值只有 `zh` / `en` 和 `auto` / `light` / `dark`。
   有一条不过就不切换域名：在 thin-muscle-coach#185 写明哪一条，等 Veli 改完重查。
4b. **订阅的上线开关默认关**：核对生产配置里开关的值是关；四项条件（见下面「订阅的上线开关」）到齐以前不打开。开关关着不挡上线。预览上开关恒为开，订阅的全流程在预览上照常验（`subscribe` 事件也在预览上触发，PRD F29）。
5. 产品负责人在 #66 回复「确认上线」。

## 合并

6. 产品负责人在 GitHub 上把 `feature/v1` 合并进 `site`（合并脚本只合并进集成分支，不做这一步，`pipeline.md` §5.1）。
7. 主站生产部署 READY；`site-db-migrate` 用 `ref=site` 再跑一次（没有新迁移时什么也不改），#67 的查询再跑一次。
8. Supabase 项目没有处于暂停状态（`/api/site/health` 返回 200）。
9. 主会话用 #62 的核对脚本对**主站项目的生产域名**（`*.vercel.app`，不是某一次部署的生成地址）跑一遍：路由表每一行、`/api/site/health`。全过以后，主会话把仓库变量 `MONITOR_TARGET` 设成这个生产域名，再进下一步。在这之前不设：上线合并前生产部署没有 `/api/site/health`，提前设会误报并开告警 issue。

## 切换

10. 主会话用 Vercel 的接口把 `velicoach.com` 从 Veli 项目移除、挂到主站项目；同时产品负责人把 #213 的切换 PR 合并进 Veli 的 `main`，Veli 生产部署 READY。
11. 主会话把仓库变量 `MONITOR_TARGET` 从主站项目的生产域名（第 9 步设的）改成 `https://velicoach.com`。

## 切换后（60 分钟内做完）

12. 主会话用核对脚本对 `velicoach.com` 跑一遍路由表每一行；迁入的 5 篇文章 `/mind/<slug>` 和它们的中英旁白都返回 200（#32 的清单）。
13. Playwright 经 `velicoach.com` 打开 `/`、`/body`、`/en/body`、`/app`：页面发出的请求里 4xx、5xx 为 0；首页「为什么是肌肉」的研究卡锚点在（研究卡只在首页，/body 不放）；第 4a 步的导航约定三件事在 `velicoach.com` 上再查一遍。
13a. 订阅的上线开关关着时：首页和各页没有订阅条和页底订阅，首屏底部是 RSS 链接；`POST https://velicoach.com/api/site/subscribe` 返回 404，订阅库里没有新增的行。开关已经打开的，改做下面「订阅的上线开关」第 4 步的验证。
14. `pipeline.md` §2.3「切换后」清单逐项做完，结果贴 #66。
15. 任何一项不过：按下面的回退步骤恢复，在 #66 写明哪一项、原因、下一次上线前要改什么。

## 回退（5 分钟内）

1. Vercel：把 `velicoach.com` 从主站项目移除、挂回 Veli 项目。
2. Veli：产品负责人在 Veli 的 `main` 上 revert #213 的切换 PR（恢复 `/` 到 `/body` 的临时跳转和 Veli 自己的 robots.txt），Veli 生产部署 READY。
3. `MONITOR_TARGET` 改回主站项目的生产域名。
4. `site` 上的主站代码不用回退：没有域名指向它，访客看不到。订阅库里已经写进的订阅照常保留。

## 订阅的上线开关

站点配置的一项，默认关（PRD「订阅的细则」第 16 条；`pipeline.md` §5.1）。它不挡上线：上线那天条件没齐，就关着上线，订阅后开。

**关着时**：不渲染订阅条和页底订阅；首屏底部原来放订阅的位置换成 RSS 链接（页脚的 RSS 照常）；生产的订阅接口返回 404，不写库。预览恒为开。

**四项条件，齐了才打开**，证据贴在 #66（上线后贴在打开开关的 PR 里）：

| 条件 | 证据 |
|---|---|
| 律师意见 | 「订阅的细则」第 14 条三件事的书面意见，没有未处理的项 |
| 发信域名和 DNS | news.velicoach.com 的 SPF、DKIM、DMARC 记录在 Resend 后台都是已验证 |
| 通讯地址 | 发件人的实际通讯地址已定，写进邮件模板的页脚 |
| Veli 隐私政策写明订阅 | Veli 生产上的隐私政策（中英两版）写了订阅收什么、存在哪、交给哪些服务商、怎么退订和删除 |

**打开的步骤**

1. 主会话提一个 `chore/` PR，只把配置里的开关改成开；PR 说明里逐项贴上表的证据，打 `owner:merge`，附决策简报（涉及法律责任，`pipeline.md` §5.1）。
2. 产品负责人合并；生产部署 READY。
3. 核对生产环境变量 `RESEND_API_KEY`、`RESEND_WEBHOOK_SECRET`、`SUBSCRIBE_TOKEN_SECRET_<编号>`、`CRON_SECRET` 都已配（ADR-0004）。
4. 验证：各页出现订阅条和页底订阅，首屏底部是订阅入口；用真实邮箱订阅一次，原位显示「已订阅，每周日见」，收到欢迎邮件；在 Gmail「显示原始邮件」里 SPF、DKIM、DMARC 三项都是 PASS，页脚有通讯地址，邮件头有 `List-Unsubscribe` 和 `List-Unsubscribe-Post`；点一键退订生效；订阅库里有这一条同意证据。结果贴在 PR 上。
5. 订阅数从这一天算起（PRD 第 1 节）。

**再关上**：验证不过，或律师、退信数据要求停收时，主会话提 PR 把开关改回关（类别和谁合并按 `pipeline.md` §5.1），在 #13 告知产品负责人；已有的订阅和同意证据保留，每周的发送按当期邮件票的状态决定（`pipeline.md` §5.1「每周内容」第 3 条）。

## 上线后（当天）

16. 切换后的清单全过以后，主会话把 GitHub 默认分支改回 `site`，删掉 `feature/v1`；合并脚本读到 `feature/v1` 404 就只合并进 `site`（`pipeline.md` §5）。开着的 PR 把 base 改成 `site`。工作流文件已随上线合并进了 `site`，确认定时运行改在 `site` 上触发。
