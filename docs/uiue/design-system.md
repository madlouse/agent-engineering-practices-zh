# 设计系统

**唯一来源**：Claude Design 里的 Velicoach 设计系统 https://claude.ai/artifact/6JqC3pUJ5GjDvXD2sEMZ5w 。仓库里的 `system/README.md`、`system/tokens.json` 和 `system/canvas.css` 是它的副本，供 agent 离线读取；改设计语言先改在线的设计系统，再覆盖这三个文件，旧版本不留。

**现在的版本：v1.1，2026-11-12 同步（第三轮小修以后的版本，和在线的一致）。** 画板是在线画布「Velicoach 主站 · UI v1.1」（https://claude.ai/artifact/8Nx35n8NXRebQn4aapiW9L ），18 块；画板文件、生成脚本和源在 [prototypes/v1.1/](prototypes/v1.1/)，在线画布由它发布。v1.1 相对 v1.0 改了什么、每条的理由和放弃的方案，见 [decisions.md](decisions.md)「2026-11-12 · 设计 v1.1」；裁决的依据是 [brief.md](brief.md)（设计简报）和 [reviews/2026-11-12-audit/](reviews/2026-11-12-audit/)（两轮独立评审和汇总）。

## 它管什么

- velicoach.com 主站和三站的颜色、字体、间距、圆角、阴影、玻璃、断点、动效时长与缓动。
- 品牌语气、版式（三种版式、导航与语言切换、两步原则）、动效、标识、无障碍。

Veli App 和 Veli 网页版（`/body`、`/app`）以 Veli 设计系统为准。两套系统共用叶子标识、纸色、苔绿、主按钮和同一套玻璃参数；本系统的颜色 token 都以 `vc-` 开头，避免重名。

## 进代码

做主站页面时，把 `tokens.json` 生成为一份 CSS 变量文件（例如 `src/tokens.css`，做法沿用 Veli 仓库 design-bar 技能的 `sync_tokens.py`），在 `src/styles.css` 里引入，样式只引用 CSS 变量。原来博客的文章页先保持原样，接入主站时再换成这套 token。媒体查询里不能用变量，断点写死同值并注释来自哪个 token（`breakpoint-tablet` 744px、`breakpoint-desktop` 1180px）。

## 相关文件

- [system/README.md](system/README.md)：品牌手册
- [system/tokens.json](system/tokens.json)：token
- [system/canvas.css](system/canvas.css)：画板共用的样式表（token 变量、外壳和组件的类）。它是生成的：手写的类在 `prototypes/v1.1/src/shell/tools/canvas.head.css`，变量部分由 `tokens.json` 生成，改了源以后跑 `prototypes/v1.1/rebuild.sh`，不直接改这个文件
- [prototypes/v1.1/](prototypes/v1.1/)：UI v1.1 的 18 块画板、生成脚本和源，README 写了怎么重建、验证和发布到在线画布
- [brief.md](brief.md)：v1.1 的设计简报（两份诊断上的裁决，和复评后的第二轮裁决）
- [coverage.md](coverage.md)：需求 → 画板覆盖表
- [prototypes/velicoach-motion.html](prototypes/velicoach-motion.html)：动效原型（three.js r180 WebGPURenderer + TSL），首页「叶与网」的参考实现
- [shell.json](shell.json)：主站外壳约定（`vc-theme` 取 `auto`、`light`、`dark`，`vc-lang` 取 `zh`、`en`，站标回 `/`，导航 `/body`、`/mind`、`/build`；依据 ADR-0003 (b)、PRD F05、F06、F09、F24），`check_shell.py` 按它查源码
- [design-bar.json](design-bar.json)：本站的检查阈值（相邻色面 ≥ 1.8:1），`verify_canvas.py` 不带参数也读
- [decisions.md](decisions.md)：设计决定
