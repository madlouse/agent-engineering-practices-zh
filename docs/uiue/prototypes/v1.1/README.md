# 画板源：Velicoach 主站 · UI v1.1

在线画布「Velicoach 主站 · UI v1.1」（地址见 `docs/README.md`）的 18 块画板，和生成它们的脚本、源片段。2026-11-12 第三轮小修以后的版本，和在线画布一致。

设计语言的唯一来源仍是在线设计系统，仓库副本在 `docs/uiue/system/`；这里放的是画板。每条设计决定的理由在 `docs/uiue/decisions.md`「2026-11-12 · 设计 v1.1」，画了什么在 `docs/uiue/coverage.md`。

## 目录

| 位置 | 是什么 | 源还是产物 |
|---|---|---|
| `boards/*.dc.html` | 18 块画板：页面画板 10 块（Main、Mind、Learn、Article、Build、Project、About、States、Body、Controls），设备画板 8 块（Tablet、Mobile、Fold、MindMobile、LearnMobile、ArticleMobile、AboutMobile、BuildMobile） | 产物，不直接改。例外：`Main.dc.html` 是手写的，本身就是源 |
| `boards/canvas.json` | 画布的布局：每块画板的位置、宽高、标题，和画布上的便签 | 源（手改）。画板变长或变短以后改这里的 `h` |
| `canvas.js` | 画板共用的脚本（液态玻璃） | 源 |
| `shell.md` | 外壳的标准片段：骨架、`SHELL` 和 `shellVals()`、导航、订阅条、页底订阅、页脚。各页面的生成脚本从它里面取片段 | 产物，由 `src/shell/test/ShellTest.dc.html` 生成 |
| `../../system/canvas.css` | 画板共用的样式表（设计系统副本的一部分，只有这一份） | 产物，由 `src/shell/tools/canvas.head.css`、`canvas.glass.css` 和 `../../system/tokens.json` 生成 |
| `src/shell/tools/` | 样式表的手写部分（`canvas.head.css`、`canvas.glass.css`）；`build_css.py`、`gen_canvas_vars.py`（组装样式表、由 token 生成变量）；`gen_shell_md.py`；`gen_controls.py` 和它读的 `controls_samples.json`（控件样张的标记，由 `extract_samples.py` 从页面画板取）；`contrast.py`（算对比度） | 源 |
| `src/shell/test/ShellTest.dc.html` | 外壳的验证页，`shell.md` 的来源 | 源 |
| `src/mind/` | 看清首页、学习路径：`Mind`、`Learn` 的 `.body.html`、`.ms.html`、`.js` 和 `build.py` | 源 |
| `src/pages/` | 文章页、页面状态、关于：`parts/` 和 `build.py`（States 里列表页的状态直接用 `src/mind/` 的标记） | 源 |
| `src/build/` | 动手、项目页、站稳：`parts.py`、`build.py`、`project.py`、`body.py`、`body_copy.json` | 源 |
| `gen_device_boards.py` | 由页面画板生成设备画板：同一份标记，只改标题和预览尺寸。高度写在脚本的表里，和 `canvas.json` 一致 | 源 |
| `tools/` | `sync_shell.py`（首页的外壳和 `shell.md` 对齐）、`audit_classes.py`（类名审计）、`verify_all.sh`（验证）、`shots.sh`、`motion_frames.sh`、`compare_shots.py`（截图和比较） | 工具 |
| `rebuild.sh` | 从源重新生成样式表、`shell.md` 和全部画板，再做类名审计 | 入口 |

留作记录、平时不跑的两个一次性脚本：`src/shell/tools/update_tokens.py`（把 v1.0 的 `tokens.json` 改成 v1.1；v1.0 的 `spine-width` 是它删的）、`tools/rename_classes.py`（合并样式时的类名改名表）。

没有放进来的：截图、验证器的输出目录、各轮的备份和制作方的报告草稿。

## 改画板

1. 改源，不改 `boards/` 里的产物（`Main.dc.html` 除外）。样式只改 `src/shell/tools/canvas.head.css`；token 先改在线设计系统，再覆盖 `docs/uiue/system/tokens.json`。
2. 重新生成（从仓库根目录跑；从别的目录跑也可以，路径都相对脚本自己算）：

   ```
   export PYTHONDONTWRITEBYTECODE=1
   bash docs/uiue/prototypes/v1.1/rebuild.sh
   ```

   五步：共享样式表 → `shell.md` 和首页的外壳 → 页面画板 → 设备画板 → 类名审计（重复定义、没用到、没定义，有一项就退出码 1）。只要 Python 3，不用装依赖。
3. 验证（要 Playwright 和它的 Chromium；输出目录必填，放在仓库外面，截图不进仓库）：

   ```
   bash docs/uiue/prototypes/v1.1/rebuild.sh --verify <输出目录>
   ```

   它在上面五步之后跑两遍 `.grok/skills/design-bar/scripts/verify_canvas.py`：页面画板 10 块（浅色、深色、伪语言，另加 390×844、320×568、820×1180，首页再加四种尺寸）和设备画板 8 块，都带本站的色面门槛 `--face-contrast 1.8`（`docs/standards/pipeline.md` §7「画板」）。报告在 `<输出目录>/pages/verify-canvas.md` 和 `<输出目录>/devices/verify-canvas.md`，换进 `docs/uiue/reviews/<日期>/`。只跑其中一遍：`bash docs/uiue/prototypes/v1.1/tools/verify_all.sh <输出目录>`，设备画板加 `--devices`。
4. 页面画板里组件的内容或结构改了，控件样张要重新取一次：`python3 docs/uiue/prototypes/v1.1/src/shell/tools/extract_samples.py`（要起浏览器，`rebuild.sh` 不跑这一步），再跑 `rebuild.sh`。
5. 画板变长或变短：改 `gen_device_boards.py` 表里的高度和 `boards/canvas.json` 里那块画板的 `h`，两处一致。

2026-11-12 搬进仓库以后实际跑过一次：`rebuild.sh` 重新生成的 18 块画板、`shell.md` 和 `canvas.css` 与搬进来的逐字节相同；`rebuild.sh --verify` 跑通，用时约 7 分钟，结论是页面画板 2 条、设备画板 2 条，都是文章页加载态的骨架被判成首屏空白带（已知误报，`docs/delivery/roadmap.md` §6）。`extract_samples.py`、`shots.sh`、`motion_frames.sh` 只改了路径，搬进来以后没有跑过。

## 画板怎么引用样式表和脚本

画板的 `<head>` 里是两行在线画布上的地址，源里固定写这两个编号：

- 样式表：`/_blob/2d0ccacf7377c5a050e285f270f25ffd`
- 脚本：`/_blob/26c007f478ecf5fa646eda60cbc23992`

本地读不到这两个地址，所以验证和截图时用 `--blob <编号>=<本地文件>` 把它们指到 `docs/uiue/system/canvas.css` 和这里的 `canvas.js`（`tools/verify_all.sh` 已经带上）。

## 发布到在线画布

1. 把 `docs/uiue/system/canvas.css` 作为资产上传到在线画布，得到一个新的地址（每次上传编号都会变）。
2. 复制一份 `boards/` 到仓库外面的临时目录，把 18 块画板里样式表的那一行换成上一步返回的地址。脚本没有改就不用重新上传，引用不动。仓库里的画板不改，仍然写上面两个固定编号。
3. 把 `docs/uiue/system/tokens.json` 放到那份副本的 `ds/velicoach/tokens.json`（画布挂的设计系统副本）。
4. 发布这份副本：18 块 `.dc.html` 和 `canvas.json`。
5. 设计系统有改动时，在线设计系统另外发布一次（README 和 `tokens.json`），再覆盖 `docs/uiue/system/`。

地址和编号以外，这里不写任何密钥。
