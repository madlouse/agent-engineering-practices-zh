# 0003 /body 的导航约定和主站服务端接口路径

- 状态：已采纳；**(b) 于 2026-11-13 再修订：第 3 条约定加偏好 cookie**；**(b) 于 2026-11-11 修订：撤掉外壳包，改成导航约定**（产品负责人确认，`docs/requirements/timeline.md` 第 89 条；依据 `docs/prd/reviews/2026-11-10-vision-review.md` 10.2 A）（原记录：产品负责人 2026-11-09 确认；(c) 分流按关口三 b 冷审 P1-5 补；研究卡随外壳包发、(c) 补 Veli 的静态资源和切换票，按关口三 b 第二轮冷审 P1-2、P1-3 改；代理目标、Veli 生产分支、`/manual`、`/v2` 按第三轮冷审 P1-C、P2-2、P2-5 补）
- 关联：ADR-0001（同域名、按路径分流）、Veli 仓库 ADR-0032（路由表）、主站 PRD v2.0 F09（修订前依据 PRD v1.2：冷审第二轮 P1-2、P1-4，第三轮 P1-1、P1-2、P2-4、P2-6）、`quality-terms` U10

## 背景

站稳一站的页面 /body 由 Veli 仓库实现（产品负责人 11-09 决定）。这带来两个问题：

1. **接口路径撞车。** 按 ADR-0032，`/api/*` 归 Veli。主站也有服务端接口：订阅提交、一键退订、Resend 回调、健康检查。没有自己的前缀，就会落到 Veli 那边。
2. **导航走样。** 用户在主站和 /body 之间来回走，要认得出还在 Velicoach、知道怎么回去。两个仓库各写一份导航，没有约定迟早不一样。（修订前这一条要求导航、书脊、订阅条、页脚是同一个组件；2026-11-11 起 U10 在 /body 上按 (b) 的三条约定判，书脊在 v1 不做，订阅条只在主站。）

## 决定

**(a) 主站接口统一放在 `/api/site/*`。**

| 接口 | 路径 |
|---|---|
| 订阅提交 | `POST /api/site/subscribe` |
| 一键退订（RFC 8058 邮件头；退订页 `/unsubscribe` 的「确认退订」按钮也提交到这里） | `POST /api/site/unsubscribe` |
| Resend 回调 | `POST /api/site/resend` |
| 健康检查 | `GET /api/site/health` |

Veli 的 `/api/*` 规则排除这个前缀。Vercel rewrites 按顺序匹配，具体的前缀先写：`/api/site/*` 写在 `/api/*` 前面；`/en/body`、`/en/legal/*`、`/en/data-usage` 归 Veli，写在主站的 `/en/*` 前面。Veli ADR-0032 的路由表同步改。

邮件正文里的「退订」链接不直接调接口：它落到主站页面 `/unsubscribe?token=…`，页面上一个「确认退订」按钮提交 `POST /api/site/unsubscribe`，邮件安全扫描预取链接时不会误退；退订后原位显示结果和「重新订阅」。

**(b) /body 的导航按约定各自实现，不共用代码包。**（2026-11-11 修订）

/body 是 Veli 的落地页，由 Veli 仓库实现。主站不再把导航、页脚打成包给 Veli。两边的导航各自按同一套设计 token 做，只约定三件事：

1. **站标回首页**：/body 导航左上角的站标链到 `/`（英文页链到 `/en/`）。
2. **三站的链接**：导航里有站稳、看清、动手三个链接，地址是 `/body`、`/mind`、`/build`（英文加 `/en`），当前所在的站高亮。
3. **语言和外观的记忆共用**：两边在同一个域名下，语言和外观的选择读写同一组 localStorage 键 `vc-lang`、`vc-theme`，取值和主站一致（`zh` / `en`；`auto` / `light` / `dark`）。（2026-11-13 修订，需求第 103 条）同时写 `.velicoach.com` 的 cookie，让子域名上的家族产品（WordS）读得到：属性 `Domain=.velicoach.com; Path=/; SameSite=Lax; Max-Age=31536000`，不加 `Secure`，和共享约定一致（条文在 `design-bar` 的 `references/family.md`，2026-11-13 已同步，#141）；读的顺序是 cookie、本机存储、系统偏好。依据 `docs/uiue/decisions.md`「2026-11-13 · M1 规格的决定」的偏好 cookie 一条。

主站的上线测试（关口四）打开 /body 和 /en/body，逐条检查这三件事（第 3 条的 cookie 在真实域名上查，见 `launch-runbook.md` 切换后第 13 步）；不通过不切换域名。

「为什么是肌肉」的研究卡只放在主站首页，/body 不放，研究卡数据不跨仓库共用，主站也不再出 `/data/research.json`。订阅条只在主站的页面上。搜索在 v1 不做，`/?q=` 的约定随之取消。

修订前的做法（主站把导航、页脚、书脊、订阅条打成 `packages/site-shell`，Veli 用固定版本的 git 依赖引入，研究卡数据跟着包发）不再采用：它要发版本、两边同步，Veli 的外壳最多落后一个版本；而用户在两边之间只需要认得出「还在 Velicoach」和「怎么回去」，三条约定加一次上线检查就够。

**(c) 分流：主站的 Vercel 项目接管根域名，用 rewrites 把 Veli 的路径反向代理到 Veli 的生产部署。**

- `velicoach.com` 挂在主站的 Vercel 项目上。分流规则写在主站仓库的 Vercel 配置里（rewrites），不用 microfrontends：一个项目、一份规则、一个仓库里能评审和测试。
- 归 Veli 的路径（`docs/architecture/overview.md` 路由表 Veli 两行，含 `/en/body`、`/en/legal/*`、`/en/data-usage`、`/auth/*`、`/api/*`（`/api/site/*` 除外））rewrite 到 Veli 项目的生产域名（项目自带的 `*.vercel.app` 域名，跟着 Veli 的生产分支走）；不用某一次部署的生成地址：生成地址在 Vercel 的标准部署保护后面，生产域名不在。其余由主站处理。具体的前缀先写。
- **Veli 的生产分支是 `main`**：B1 期间 Veli 的票只合并进 `feature/b1`，由 thin-muscle-coach#72 一次合并进 `main`。/body、法务页、外壳（thin-muscle-coach#185、thin-muscle-coach#101）要等 thin-muscle-coach#72 才在 Veli 生产上，所以**主站上线不早于 Veli B1 上线（thin-muscle-coach#72）**，除非产品负责人另行同意把 thin-muscle-coach#185、thin-muscle-coach#101 的改动当紧急修复单独进 Veli `main`。Veli 的切换 PR（thin-muscle-coach#213）以 `main` 为 base，由产品负责人合并。
- **Veli 的静态资源也要转给 Veli**：Veli 是 Next.js，没有设 `assetPrefix`，页面的脚本、样式、字体和图片都从同一个域名的 `/_next/*`（含 `/_next/static/*`、`/_next/image`）取。Veli 根目录的静态文件逐个列出：`/manual` 和 `/manual/*`（Veli `public/` 现在唯一的目录；`/manual` 由 Veli 跳到 `/manual/index.html`），新应用壳的临时路由 `/v2`（Veli 改名后删掉这一行），以及 Veli F106（主屏幕 Web App，Serwist）要加的 `/sw.js`、`/manifest.webmanifest`、`/favicon.ico`、`/icons/*`。主站的资源在 `/assets/*` 和自己的 `/favicon.svg`，和这些不重名。Veli 新加根目录文件前先改两边的路由表（thin-muscle-coach#213）。
- 同一个域名，Cookie 和登录状态照旧共享（ADR-0001）。Veli 项目不再直接挂 `velicoach.com`，它的生产地址只给主站的 rewrites 用。
- 先在主站的预览域名上配好、逐条验证（每个 Veli 路径都能从主站预览打开），再切根域名：切换是上线时的最后一步。两步各一张票（`docs/delivery/gate-3b-split.md`）。
- Veli 仓库要配合的事分两张票：切换前要做完的（/body、法务页、按 (b) 的三条约定做导航）在 thin-muscle-coach#185；只能在切换那一刻做的（去掉 Veli 自己 `/` 的临时跳转、不再出 robots.txt、ADR-0032 的路由表改成「由主站代理」、Service Worker 作用范围限定在 `/app`）在 thin-muscle-coach#213。切换的顺序、谁做和回退见 `docs/delivery/launch-runbook.md`。

## 考虑过的其他做法

| 做法 | 为什么不选 |
|---|---|
| 主站把外壳打成包给 Veli（修订前的 (b)） | 要发版本、两边同步，Veli 的外壳最多落后一个版本；v1 用不到同一份代码，三条约定加上线检查就够（2026-11-11） |
| 用 Vercel microfrontends 分流 | 规则和两个项目的关系分在 Vercel 的团队配置里，评审和测试都不在仓库里；v1 只有两个应用，rewrites 够用 |
| 规则放在 Veli 仓库 | 主站的上线要改另一个仓库，上线票的 PR 落在哪个仓库说不清；主站拥有根路径和大部分路径，规则跟着主站走 |
| Veli 自己做导航，不守任何约定 | 站稳一站看起来像另一个网站：用户从首页点进站稳，站标不回首页、找不到另外两站、语言和外观要重新选，不知道自己还在不在 Velicoach。所以 (b) 不共用代码，但约定三件事并在上线时检查 |

## 后果

- 两边的导航是两份代码，靠 (b) 的三条约定和上线测试保持一致；`quality-terms` U10「同一个组件」在 /body 上按这三条约定判（规范已改，2026-11-11）。
- v2 加账号菜单时，再定导航怎么读会话、要不要回到共用代码。
- 新增主站接口一律放在 `/api/site/` 下；新增顶层路径前照旧查 `docs/architecture/overview.md` 的路由表。
- Veli 侧要做的事记在 thin-muscle-coach#185（切换前）和 thin-muscle-coach#213（切换时）。
