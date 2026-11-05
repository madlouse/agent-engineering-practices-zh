# 收尾确认：G1、G2、G3、#2、N1

> 2026-11-05。只核对这 5 条，没开新题；只读，没改画板和样式。画板 v38、`vc.css`、`liquid-glass.js` 是主会话交来的那一份（`scratchpad/canvas2/`）。
> 截图都在 `scratchpad/close-Qk7/`。用 `capture_motion.py` 截（执行画板挂载代码，透镜挂上，`lenses` 字段 ≥ 1，除非另写）。G2 需要按键聚焦，我把脚本复制成 `close-Qk7/cm.py`，只加了「Tab 聚焦」和「量溢出」，原脚本没动。

| 编号 | 结论 |
|---|---|
| G1 | 修好 |
| G2 | 修好 |
| G3 | 修好（只在 Chromium 无头里验证，Safari、Firefox 留给关口四） |
| #2 | 修好 |
| N1 | 修好 |

## G1 动手页导航：修好
- 首屏：`g1-top.png`、`g1-top-dark.png`。导航胶囊是 `nav-moss` 实色（苔绿叠 8% 白 + 内边光 + 影子），不再有玻璃的灰边和渐变，浅色字，和首屏分得开。
- 正文压在导航下：`g1-behind.png`、`g1-behind-dark.png`。换成纸色玻璃（`lg`），不再是发灰的绿；背后的标题被糊成一团，字读得清。`--probe '.gnav'`：`spatial_range 0.838`，判定「背后会变」。
- 代码：`Build.dc.html:288` 首屏 `nav-moss on-dark`，压住正文时 `lg`；`lg-moss` 已删除。

## G2 「动手」圆焦点：修好
- 做法：首页（`Main.dc.html`，1440×900）用键盘 Tab 聚焦 `.orb`，确认 `:focus-visible` 为真，截图 `g2-focus.png`、`g2-focus-dark.png`；沿过圆心的水平线取像素，按 WCAG 相对亮度算对比度。
- 圆骑在接缝上，两侧都有 ≥ 3:1 的圈：

| 主题 | 一侧 | 圈 | 对比度 |
|---|---|---|---|
| 浅色 | 纸色（244,242,236） | 外圈焦点蓝（47,95,179） | 5.50:1 |
| 浅色 | 墨色（23,21,15） | 贴圆的白圈（216,209,196） | 12.03:1 |
| 浅色 | 圆本身（38,59,46） | 白圈 | 7.92–8.61:1 |
| 深色 | 纸侧（39,37,33） | 外圈蓝（134,169,242） | 6.53:1 |
| 深色 | 墨侧（22,20,15） | 白圈（209,205,198） | 11.62:1 |

- 墨色一侧外圈蓝对墨只有 2.96:1，但那一侧还有贴着圆的白圈，所以那一侧的圈是白圈，满足 A1。上一轮的 2.09:1 不再出现。

## G3 文章页吸顶导航：修好
- 怎么截的：`capture_motion.py Article.dc.html … --size WxH --scroll Y`，透镜**开着**（`lenses: 2`）；`--wait 3000`（默认）和 `--wait 0`（滚完立刻截）各一张；浅色、深色各一张。尺寸 1440×900 和 1280×720。
- 上一轮用的 `--scroll 2000` 这一段，文章正好滚到一段稀疏处，导航下面几乎没有字（`g3-1440x900-wait3s-crop.png`、`g3-1280x720-wait3s-crop.png`）。所以我又换了正文最密的位置扫一遍：1440×900 滚 1100、1150、1200、1250、1300、1350、1450、1500（`g3c-all.png`），1280×720 滚 1250，等待 0 毫秒，浅色深色（`g3d-all.png`）。
- 结果：压在胶囊里面的字都是糊成一团的灰块，读不出字形。只有胶囊最外面一圈圆角的边缘透镜折射区里，能认出半个字（比如「保住」的「住」），那是透镜的折射，不是模糊没起作用。胶囊外面的字是清楚的，应当如此。上一轮在 `art-scroll-2000.png` 看到的「下半截清楚透出」没有复现。
- 局限：这里是 Chromium 无头（SwiftShader）。透镜的 `backdrop-filter: url()` 在 Safari 上不画，模糊部分在 Safari、Firefox 上没验证，关口四真机再看（主会话 `decisions.md` 也这么写了）。

## #2 研究卡：修好
- 截图 `n2-cards.png`（Body.dc.html，1440 宽，中英各一行）。
- 阅读顺序：含数字的结论（数字等宽加粗，和正文同号，没有放大）→ 出处 → 研究类型、样本量、可信度。和 `quality-terms.md` T8 新写法一致：「数字开头的结论 → 出处 → 研究类型、样本量、可信度」，「不放大」那一条也一致（`.metric` 只设了字体、粗细、等宽数字，没设字号）。
- BMJ 卡：`g = −0.49 力量训练对抑郁有中等大小的效果：效应量 g 为负表示症状减轻，越负改善越大。`；英文 `g = −0.49 Strength training had a moderate effect on depression: a negative effect size g means fewer symptoms, and the more negative, the bigger the improvement.` 数值和读法都在了。
- `coverage.py --data research.json --skip-fields id,topic`：`metric` 现在列为 `Body.dc.html、Main.dc.html`，没有漏画的字段。
- 另一个小地方（不算问题）：其他三张卡的数字和结论里的数字重复（「−23% … 少了 23%」），读起来有点啰嗦，但这是 T8 允许的写法（先数字后句子）。

## N1 平板 744、折叠屏 884，英文：修好
- 做法：`Tablet.dc.html` 744×1133 和 820×1180、`Fold.dc.html` 884×1104 和 984×1092，中英文、浅色深色各跑一遍，量所有元素有没有越出视口（`overflow` 输出），再看截图。
- 结果：16 个组合都是 0 个元素越界、`scrollWidth` 等于视口宽。`n1-t744-English-浅色.png`：「Read this week's article」「History of AI」「Human–AI collaboration」「Subscribe」都完整在画面里。`n1-f884-English-浅色.png`：语言收成「中 / EN」一个按钮，主操作、订阅条都在。
- 观察（P3，不进本次判定）：折叠屏 884、984 宽下「然后动手」圆放在铰链右边的墨色一侧，没有骑在接缝上，和手机、平板、桌面不一样；画板里 `left: calc(50% + 24px)` 是写死的，看起来是为了躲开铰链线。焦点圈的两色设计在这个位置也成立，但如果想要「圆都骑在接缝上」，这里要么写进决定里说明，要么调回去。
- 提醒：`verify_canvas.py` 我自己跑时，没标尺寸的默认视口（390）会对平板和折叠屏报一串「内容超出画板」，那是 390 宽跑的，不是 744、884；主会话的 `r14-all` 里这两块都是「通过」。别把默认视口的结果当成平板的结果。

## 截图和文件（`/tmp/claude-0/-home-claude/b9e68665-1a1a-5bba-80a0-e8161ba32ea6/scratchpad/close-Qk7/`）
- G1：`g1-top.png`、`g1-behind.png`、`g1-top-dark.png`、`g1-behind-dark.png`、`g1-behind-probe.png`
- G2：`g2-focus.png`、`g2-focus-dark.png`
- G3：`g3-1440x900-wait3s-crop.png`、`g3-1440x900-wait0-crop.png`、`g3-1280x720-wait3s-crop.png`、`g3-1280x720-wait0-crop.png`、`g3-1280x720-dark-crop.png`、`g3b-all.png`、`g3c-all.png`、`g3d-all.png`
- #2：`n2-cards.png`、`n2-zh.png`、`n2-en.png`
- N1：`n1-t744-*.png`、`n1-t820-*.png`、`n1-f884-*.png`、`n1-f984-*.png`

通过
