# 技术方案

本仓库是 velicoach.com 主站：首页、三站页面和 看清的文章都在这里。文章部分已经有代码（TanStack Start + Vite + React，见 `src/`）；首页和三站页面还没写。这里记已经定下的技术决定和它们的出处；选型变化先写 ADR。

## 域名与路由

velicoach.com 按路径分给两个 Vercel 项目（Veli 仓库 ADR-0032）：

| 路径 | 归谁 |
|---|---|
| `/`、`/mind`（看清，文章在 `/mind/<slug>`）、`/build`、`/about`、`/unsubscribe`、`/api/site/*`、`/explainers/*`、`/originals/*`、`/sitemap.xml`、`/robots.txt`（整个域名只有这一份，也覆盖 Veli 的路径）、`/en/*`（下面归 Veli 的英文路径除外），以及其余路径 | 主站（本仓库） |
| `/body`、`/en/body` | Veli：对外落地页，同时是主站的站稳一站 |
| `/app`、`/pricing`、`/legal/*`、`/en/legal/*`、`/data-usage`、`/en/data-usage`、`/auth/*`、`/admin/*`、`/plan-only`、`/api/*`（`/api/site/*` 除外）、`/v2`（Veli 新应用壳的临时路由，改名后删掉） | Veli |
| Veli 的静态资源：`/_next/*`（脚本、样式、字体、`/_next/image`）；Veli 根目录的静态文件 `/manual`、`/manual/*`、`/sw.js`、`/manifest.webmanifest`、`/favicon.ico`、`/icons/*` | Veli（ADR-0003 (c)；主站的资源在 `/assets/*`、`/favicon.svg`，不重名） |

- 主站上线前，`/` 临时 307 跳到 `/body`。主站上线时 `velicoach.com` 挂到主站的 Vercel 项目，主站用 rewrites 把归 Veli 的路径反向代理到 Veli 项目的生产域名（`*.vercel.app`，ADR-0003 (c)），并把 `/` 改为主站首页。
- 分流规则按「具体的前缀先匹配」排：`/api/site/*` 写在 `/api/*` 前面，`/en/body`、`/en/legal/*`、`/en/data-usage` 写在 `/en/*` 前面。
- 新增顶层路径或根目录的静态文件前先查这张表，两个仓库一起改（Veli 侧见 thin-muscle-coach#213）。
- 切换根域名的顺序、谁做和回退见 `docs/delivery/launch-runbook.md`。
- 主站的服务端接口都在 `/api/site/*`，`/body` 的导航由 Veli 按三条约定自己做，主站不打包导航和页脚给 Veli，上线时检查（ADR-0003 (b)）。

## 账号

- 两站共用一个账号（Supabase Auth，项目在 Veli 仓库）；同一个域名，登录状态天然共享。
- **主站 v1 不读会话**（需求第 80 条，ADR-0001 修订）：页面全部按未登录渲染（静态、可缓存）；登录在 Veli 里完成，「开始训练」直接去 Veli，已登录的人由 Veli 带到今天的安排。
- 主站不读健康数据；「进入今天的训练」只是入口，训练内容在 Veli 里读。
- v2 再读会话：只读名字和邮箱；登录在当前页面原地弹出，读到登录状态后原地换成「继续」类入口，位置预先留好，不影响 CLS。

## 页面与内容

- 中文在根路径，英文在 `/en/` 下，一一对应，互相声明 `hreflang`。
- 内容按 PRD 第 5 节的字段存成结构化数据，新增一篇文章不改代码。
- 性能门槛：手机 75 分位 LCP ≤ 2.5 秒、INP ≤ 200 毫秒、CLS ≤ 0.1。

## 动效

- three.js r180 的 `WebGPURenderer` 加 TSL 节点材质：同一份着色器在 WebGPU 和 WebGL2 上都能跑，两者都不可用时显示静态画面。签名的现行实现以 Main 画板为准（`docs/uiue/prototypes/v1.1/boards/Main.dc.html`）；`docs/uiue/prototypes/velicoach-motion.html` 是选方向时的历史原型。
- 首屏文字绘制完再加载 three.js（约 260 KB gzip），不拖慢 LCP；滚出视口或切走标签页时暂停；帧率持续低于 40 时降到 1 倍像素密度；减弱动态效果时只画一帧。
- 原型里踩过的坑：共享 `uniform()` 节点的材质不能单独销毁（切换场景时缓存，不 dispose）；WebGPU 读回像素时每行补齐到 256 字节。

## 部署与服务

框架沿用本仓库已有的 TanStack Start（Vite、React），不换。看清用主站的二级目录 `velicoach.com/mind`，不另用子域名（PRD 决定记录）。本仓库 `AGENTS.md` 是 Grok 构建沙箱的契约，它的 `auth`、`neon` 技能只用于沙箱预览；正式站的账号用 Veli 的 Supabase Auth（ADR-0001）。

其余沿用 Veli 的选择：Vercel 跑应用，Cloudflare 管域名和 DNS，Supabase 管数据和登录，Resend 发订阅邮件（订阅用子域名 news.velicoach.com，Veli 的登录验证码继续用主域名）。

## ADR

| 编号 | 决定 |
|---|---|
| [0001](adr/0001-shared-domain-and-account.md) | 与 Veli 共用域名和账号，按路径分流 |
| [0002](adr/0002-webgpu-motion.md) | 首页动效用 three.js WebGPURenderer + TSL，自动回退 WebGL2 |
| [0003](adr/0003-body-shell-and-site-api.md) | /body 的导航约定、主站服务端接口路径、按路径分流的方式（已采纳，2026-11-09；(b) 于 2026-11-11 修订成导航约定） |
| [0004](adr/0004-subscription-storage.md) | 订阅的存储（主站自己的 Supabase 项目）、发信、退订令牌和频率限制（已采纳，2026-11-09） |
| [0005](adr/0005-monitoring-and-alerts.md) | 外部监控用 GitHub Actions 定时探测，线上错误进每日日报，不开 Vercel 的告警（已采纳，2026-11-09；第二、三轮冷审修订） |
