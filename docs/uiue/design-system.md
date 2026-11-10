# 设计系统

**唯一来源**：Claude Design 里的 Velicoach 设计系统 https://claude.ai/artifact/6JqC3pUJ5GjDvXD2sEMZ5w 。仓库里的 `system/README.md` 和 `system/tokens.json` 是它的副本，供 agent 离线读取；改设计语言先改在线的设计系统，再覆盖这两个文件。

## 它管什么

- velicoach.com 主站和三站的颜色、字体、间距、圆角、阴影、玻璃、断点、动效时长与缓动。
- 品牌语气、版式（三种版式、导航与语言切换、两步原则）、动效、标识、无障碍。

Veli App 和 Veli 网页版（`/body`、`/app`）以 Veli 设计系统为准。两套系统共用叶子标识、纸色、苔绿、主按钮和同一套玻璃参数；本系统的颜色 token 都以 `vc-` 开头，避免重名。

## 进代码

做主站页面时，把 `tokens.json` 生成为一份 CSS 变量文件（例如 `src/tokens.css`，做法沿用 Veli 仓库 design-bar 技能的 `sync_tokens.py`），在 `src/styles.css` 里引入，样式只引用 CSS 变量。原同席博客的文章页先保持原样，接入主站时再换成这套 token。媒体查询里不能用变量，断点写死同值并注释来自哪个 token（`breakpoint-tablet` 744px、`breakpoint-desktop` 1180px）。

## 相关文件

- [system/README.md](system/README.md)：品牌手册
- [system/tokens.json](system/tokens.json)：token
- [prototypes/velicoach-motion.html](prototypes/velicoach-motion.html)：动效原型（three.js r180 WebGPURenderer + TSL），首页「叶与网」的参考实现
- [decisions.md](decisions.md)：设计决定
