# 0003 /body 上的主站外壳和主站服务端接口路径

- 状态：已采纳（产品负责人 2026-11-09 确认；(c) 分流按关口三 b 冷审 P1-5 补；研究卡随外壳包发、(c) 补 Veli 的静态资源和切换票，按关口三 b 第二轮冷审 P1-2、P1-3 改；代理目标、Veli 生产分支、`/manual`、`/v2` 按第三轮冷审 P1-C、P2-2、P2-5 补）
- 关联：ADR-0001（同域名、按路径分流）、Veli 仓库 ADR-0032（路由表）、主站 PRD v1.2（冷审第二轮 P1-2、P1-4，第三轮 P1-1、P1-2、P2-4、P2-6）、`quality-terms` U10

## 背景

站稳一站的页面 /body 由 Veli 仓库实现（产品负责人 11-09 决定）。这带来两个问题：

1. **接口路径撞车。** 按 ADR-0032，`/api/*` 归 Veli。主站也有服务端接口：订阅提交、一键退订、Resend 回调、健康检查。没有自己的前缀，就会落到 Veli 那边。
2. **外壳走样。** 用户在主站和 /body 之间来回走，导航、书脊、订阅条、页脚必须是同一个组件（U10）。两个仓库各写一份，迟早不一样。

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

**(b) /body 的外壳由主站打包给 Veli。**

- 主站把导航、页脚、书脊、页底订阅条做成独立组件，只依赖设计 token（`vc-` 前缀），不依赖主站的路由、数据和登录。
- 这些组件打包成主站仓库里的一个小包（`packages/site-shell`），Veli 用 git 依赖固定到一个版本引入。升级时 Veli 改版本号，走它自己的评审。
- 外壳包按里程碑分批：第一个版本（M1）只含导航和页脚；书脊随 M2（F08）、页底订阅条随 M3（F07）进后续版本。
- 外壳包发布前，/body 先用 Veli 自己的导航，站标链回 `/`。外壳包的导航可以先不带 ⌘K：搜索按钮链到 `/?q=<词>`，打开主站首页并展开搜索浮层（PRD F26），不新增 `/search` 路径。
- 两边共用同一个源（同一个域名），外观和语言的选择存在 localStorage 的 `vc-theme`、`vc-lang` 两个键里，主站和 /body 读写同一份；外壳包导出这两个键名常量，Veli 不自己写字符串。
- 订阅条在 /body 上也提交到 `/api/site/subscribe`，同一个域名，不跨域。
- **研究卡数据跟外壳包一起发。** 主站构建研究卡源数据时，把同一份 JSON（带 `schemaVersion`，不含审核记录）写进外壳包（`packages/site-shell/data/research.json`），随外壳包的版本发；Veli 从固定版本的 git 依赖读它，不在构建时请求网络地址。这样主站上线前 /body 就有研究卡数据，而且和外壳走同一条升级路径。主站自己的 `/data/research.json` 是同一份文件的公开副本，Veli 不读它。研究卡改了，主站发一个外壳包的补丁版本，Veli 升版本号。

**(c) 分流：主站的 Vercel 项目接管根域名，用 rewrites 把 Veli 的路径反向代理到 Veli 的生产部署。**

- `velicoach.com` 挂在主站的 Vercel 项目上。分流规则写在主站仓库的 Vercel 配置里（rewrites），不用 microfrontends：一个项目、一份规则、一个仓库里能评审和测试。
- 归 Veli 的路径（`docs/architecture/overview.md` 路由表 Veli 两行，含 `/en/body`、`/en/legal/*`、`/en/data-usage`、`/auth/*`、`/api/*`（`/api/site/*` 除外））rewrite 到 Veli 项目的生产域名（项目自带的 `*.vercel.app` 域名，跟着 Veli 的生产分支走）；不用某一次部署的生成地址：生成地址在 Vercel 的标准部署保护后面，生产域名不在。其余由主站处理。具体的前缀先写。
- **Veli 的生产分支是 `main`**：B1 期间 Veli 的票只合并进 `feature/b1`，由 thin-muscle-coach#72 一次合并进 `main`。/body、法务页、外壳（#185、#101）要等 #72 才在 Veli 生产上，所以**主站上线不早于 Veli B1 上线（#72）**，除非产品负责人另行同意把 #185、#101 的改动当紧急修复单独进 Veli `main`。Veli 的切换 PR（#213）以 `main` 为 base，由产品负责人合并。
- **Veli 的静态资源也要转给 Veli**：Veli 是 Next.js，没有设 `assetPrefix`，页面的脚本、样式、字体和图片都从同一个域名的 `/_next/*`（含 `/_next/static/*`、`/_next/image`）取。Veli 根目录的静态文件逐个列出：`/manual` 和 `/manual/*`（Veli `public/` 现在唯一的目录；`/manual` 由 Veli 跳到 `/manual/index.html`），新应用壳的临时路由 `/v2`（Veli 改名后删掉这一行），以及 Veli F106（主屏幕 Web App，Serwist）要加的 `/sw.js`、`/manifest.webmanifest`、`/favicon.ico`、`/icons/*`。主站的资源在 `/assets/*` 和自己的 `/favicon.svg`，和这些不重名。Veli 新加根目录文件前先改两边的路由表（thin-muscle-coach#213）。
- 同一个域名，Cookie 和登录状态照旧共享（ADR-0001）。Veli 项目不再直接挂 `velicoach.com`，它的生产地址只给主站的 rewrites 用。
- 先在主站的预览域名上配好、逐条验证（每个 Veli 路径都能从主站预览打开），再切根域名：切换是上线时的最后一步。两步各一张票（`docs/delivery/gate-3b-split.md`）。
- Veli 仓库要配合的事分两张票：切换前要做完的（/body、法务页、研究卡从外壳包读、接入外壳包）在 thin-muscle-coach#185；只能在切换那一刻做的（去掉 Veli 自己 `/` 的临时跳转、不再出 robots.txt、ADR-0032 的路由表改成「由主站代理」、Service Worker 作用范围限定在 `/app`）在 thin-muscle-coach#213。切换的顺序、谁做和回退见 `docs/delivery/launch-runbook.md`。

## 考虑过的其他做法

| 做法 | 为什么不选 |
|---|---|
| 两边各自复制一份外壳 | 复制以后各改各的，会走样，违反 U10（导航、页脚、书脊每页都是同一个组件） |
| 用 Vercel microfrontends 分流 | 规则和两个项目的关系分在 Vercel 的团队配置里，评审和测试都不在仓库里；v1 只有两个应用，rewrites 够用 |
| 规则放在 Veli 仓库 | 主站的上线要改另一个仓库，上线票的 PR 落在哪个仓库说不清；主站拥有根路径和大部分路径，规则跟着主站走 |
| /body 不带主站外壳 | 站稳一站看起来像另一个网站；用户从首页点进站稳，导航、页脚全变，不知道自己还在不在 Velicoach |

## 后果

- 主站多维护一个包，改外壳要发版本；Veli 的外壳最多落后一个版本。
- 外壳组件不能读登录状态（主站 v1 不读，ADR-0001 修订）；v2 加账号菜单时，再定由谁提供会话。
- 新增主站接口一律放在 `/api/site/` 下；新增顶层路径前照旧查 `docs/architecture/overview.md` 的路由表。
- Veli 侧要做的事记在 thin-muscle-coach#185（切换前）和 #213（切换时）。
- 研究卡改了要发外壳包的补丁版本，Veli 升版本号才看得到；外壳包的落后版本检查同样管住它。
