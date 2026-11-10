# 技术方案

本仓库是 velicoach.com 主站：首页、三站页面和 看清的文章都在这里。文章部分已经有代码（TanStack Start + Vite + React，见 `src/`）；首页和三站页面还没写。这里记已经定下的技术决定和它们的出处；选型变化先写 ADR。

## 域名与路由

velicoach.com 按路径分给两个 Vercel 项目（Veli 仓库 ADR-0032）：

| 路径 | 归谁 |
|---|---|
| `/`、`/mind`（看清，文章在 `/mind/<slug>`）、`/build`、`/about`、`/en/*`，以及其余路径 | 主站（本仓库） |
| `/body` | Veli：对外落地页，同时是主站的站稳一站 |
| `/app`、`/pricing`、`/legal/*`、`/data-usage`、`/auth/*`、`/api/*`、`/manual/*` | Veli |

- 主站上线前，`/` 临时 307 跳到 `/body`。主站上线时在 Vercel 上按路径分流（microfrontends 或 rewrites，实现时选定），并把 `/` 改为主站首页。
- 新增顶层路径前先查这张表，两个仓库一起改。

## 账号

- 两站共用一个账号（Supabase Auth，项目在 Veli 仓库）；同一个域名，登录状态天然共享。
- 主站只读名字和邮箱，不读健康数据；「进入今天的训练」只是入口，训练内容在 Veli 里读。
- 登录方式和 Veli 一致：Google、Apple，邮箱验证码备用；登录在当前页面原地弹出（两步原则）。
- 页面先按未登录渲染（静态、可缓存），客户端读到登录状态后原地换成「继续」类入口，位置预先留好，不影响 CLS。

## 页面与内容

- 中文在根路径，英文在 `/en/` 下，一一对应，互相声明 `hreflang`。
- 内容按 PRD 第 5 节的字段存成结构化数据，新增一篇文章不改代码。
- 性能门槛：手机 75 分位 LCP ≤ 2.5 秒、INP ≤ 200 毫秒、CLS ≤ 0.1。

## 动效

- three.js r180 的 `WebGPURenderer` 加 TSL 节点材质：同一份着色器在 WebGPU 和 WebGL2 上都能跑，两者都不可用时显示静态画面。参考实现见 `docs/uiue/prototypes/velicoach-motion.html`。
- 首屏文字绘制完再加载 three.js（约 260 KB gzip），不拖慢 LCP；滚出视口或切走标签页时暂停；帧率持续低于 40 时降到 1 倍像素密度；减弱动态效果时只画一帧。
- 原型里踩过的坑：共享 `uniform()` 节点的材质不能单独销毁（切换场景时缓存，不 dispose）；WebGPU 读回像素时每行补齐到 256 字节。

## 部署与服务

框架沿用本仓库已有的 TanStack Start（Vite、React），不换。原来计划的 `with.velicoach.com` 改为永久跳转到 `velicoach.com/mind`（PRD 决定记录）。本仓库 `AGENTS.md` 是 Grok 构建沙箱的契约，它的 `auth`、`neon` 技能只用于沙箱预览；正式站的账号用 Veli 的 Supabase Auth（ADR-0001）。

其余沿用 Veli 的选择：Vercel 跑应用，Cloudflare 管域名和 DNS，Supabase 管数据和登录，Resend 发订阅邮件（与 Veli 同一个发信域名）。

## ADR

| 编号 | 决定 |
|---|---|
| [0001](adr/0001-shared-domain-and-account.md) | 与 Veli 共用域名和账号，按路径分流 |
| [0002](adr/0002-webgpu-motion.md) | 首页动效用 three.js WebGPURenderer + TSL，自动回退 WebGL2 |
