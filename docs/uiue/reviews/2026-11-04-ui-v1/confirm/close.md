# 关口三 a（#14）确认轮（满 3 轮之后）· 独立评审

> 2026-11-05。只核对 `final.md` §7 的 F1–F6，加 §2–§6 里不过或回归的条目，加这次改动带出的回归。不做全量评审。没看制作过程。
> 材料：`shots-r6/`（179 张）、`shots-r6/motion/` 四帧、`canvas2/project/*.dc.html`、`canvas2/vc.css`、设计系统 README、`verify-canvas-final.md`（0 个问题）。
> 自己补的（只读，临时副本在 scratchpad 的 `cx/`，没动仓库）：用 `render_dc.py` 渲染 Main 1440×790、Mobile 390×664 / 320×568（中英）；给「动手」圆加 `is-hover`、`is-press` 类，取圆内、文字框外 4px 的最亮像素算对比度；用 Chromium 模拟「降低透明度」读计算样式；逐字取行框扫 Body、Mind、Build、Article、Main 在 1440、820、320 下的孤字、孤词、行首标点（中英）。

## 0. 结论

**不通过。** P0 = 0，P1 = 0（A1 已修），但 F5（V9 孤字孤词）没修干净：中文、英文各还有一处。其余五条（F1、F2、F3、F4、F6）都已修。最小改法见 §3，两处各一行 CSS。

另有一处这次改动带出的新问题（英文手机 320×568 的圆压住「See clearly」），记 P2，进实现票，不影响结论。

## 1. 逐条核对

| 条目 | 结论 | 证据 |
|---|---|---|
| F1 A1 液态玻璃按下的对比度 | **已修** | 实测（浅色，最亮背景算）。首页圆标题 26px：默认 6.91 / 悬停 7.69 / 按下 8.64；副标题 14px：7.35 / 8.08 / 9.09（上一轮按下 4.13）。手机圆标题 16px 粗体：5.30 / 5.70 / 6.30（上一轮默认 4.51、按下 3.73）；副标题 12px：8.10 / 8.98 / 9.97。原因：`vc.css` 第 279–280 行给 `glass-moss` 的悬停、按下改成叠黑（8%、16%），不再叠白，越按越暗。深色主题同一规则，只会更高 |
| F2 U2 手机矮屏受众词 | **已修** | `Mobile-390-light.png`：「先站稳」下有「给上班族的力量训练」，「再看清」下有「写给想跟上 AI 的人」。英文 320×568 `Mobile-lang-English-320-light.png`：「Strength training for busy workers」「For anyone keeping up with AI」。`Mobile.dc.html` 第 35 行 `.m-aud{display:none}` 已挪到第 36 行媒体查询前面 |
| F3 V3 看清导语字数 | **已修** | 标题加导语：中文「看清」加「写给想跟上 AI 的人：AI 是怎么一步步走到今天的，人和智能体又该怎么一起工作。」共 33 个汉字加两个「AI」；英文 25 词（上限 50 字 / 35 词）。`Mind-light.png`、`Mind-lang-English-light.png` 首屏两行导语 |
| F4 V5 暂停按钮的玻璃底色 | **已修（换了做法）** | 暂停按钮不再是玻璃：首页 `icon-btn surface-ink`，手机 `icon-btn surface-solid`，计算后底色 `rgb(29,27,21)`、`rgb(255,253,248)`，没有模糊，降低透明度也不会变。`vc.css` 第 203 行 `.icon-btn:not([class*="glass"])…` 的选择器也改了。「动手」圆降低透明度时背景从 `rgba(38,59,46,0.84)` 变成 `rgb(38,59,46)` 实色。设计系统 README 第 98 行已只把圆、播放条、滚动时的导航列为液态玻璃，和实现一致 |
| F5 V9 孤字、孤词、行首标点、标签断词 | **部分修，没修干净** | 见 §2 |
| F6「动手」圆的写法 | **已修** | `vc.css` 第 232–234 行 `.orb` 只剩两条状态色，没有 `scale`；`Controls.dc.html` 第 22 行 `.orb` 只过渡 `box-shadow`。首页和清单是同一种写法，按下变暗、不缩放 |

## 2. F5 细项

已修：
- 英文孤词：「Finish and grow a leaf」（Body 1440、820）现在是「Finish and / grow a leaf」；「about 90 h」「about 40 h」「about 15 h」在 Mind 1440、320 不再单独成行。
- 中文行首标点：Build 320 产品列表「，公开分享。」不在行首（`vc.css` 第 285 行 `a` 里的说明 `word-break:normal`）。
- 中文标签断词「队 / 列」「步 / 速」「试 / 验」：Main 1440、Body 320 的研究卡里都不再断。
- 扫描没有发现行首标点（中英 1440、820、320）。

**没修干净：**

1. **中文 Body 320，研究卡元信息「这篇综述的摘要没有给出证据可信度分 / 级」**（`o-Body.png`）：「分级」拆开，「级」单字成行。元素 `.meta-part`，计算样式 `word-break:keep-all; overflow-wrap:anywhere; text-wrap:pretty`。违反 V9「避免孤字成行」和「标签不把一个词拆到两行」。
2. **英文 Article 320，元信息「Applies to: harness engineering, any / model」**（`o-Arti.png`）：「model」单词成行。上一轮 F5 列过「any / model」，没动。违反 V9「避免孤字成行」。

## 3. 最小改法

| 差的 | 改法 |
|---|---|
| 中文 `.meta-part` 孤字 | `vc.css` 第 287 行 `.meta-part{…text-wrap:pretty}` 改成 `text-wrap:balance`（两行均分，「级」不会单独落下） |
| 英文文章元信息孤词 | `Article.dc.html` 里放「Applies to / Checked / Published」的那一行（类 `mono`）加 `text-wrap:balance`，或者「any model」之间用不换行空格 |

改完在 Body 320 中文、Article 320 英文各看一眼即可。

## 4. 其余上一轮条目

| 条目 | 状态 |
|---|---|
| V10、C4、X1 | 保持已修（`Article-lang-English-light.png` 播放条各标签一行；`f-Mind-320-en` 分段按钮；p2 三种结局并列） |
| A2–A8、U6–U12 | `verify-canvas-final.md` 浅、深、伪语言 0 个问题；降低透明度、减弱动态效果见 §1 F4 和 `motion/3-reduced-motion-still.png` |
| S2 手机两处登录按钮外观不同 | 没动（P3，进实现票） |
| S3 站稳「开始训练」卡片的 Esc 挂在 `#start-options` 上 | 没动（P3，进实现票） |
| S4 手机上视频出错的说明被 `.vf-body{display:none}` 藏掉 | 没动（P3，进实现票） |
| S6 看清英文 320 分段控件第二项被裁成「Human–AI collabora」 | 没动（P3，进实现票） |
| S7 文字没跟上 | 没动：`Controls.dc.html` 第 32 行还写「按下叠 vc-state-press 并缩到 0.98」，`vc.css` 第 211 行注释同，第 232 行注释写「放大缩小」（P3，进实现票） |
| S8 看清、状态页的导航不吸顶却用玻璃（`position:absolute`） | 没动（P3，进实现票） |
| S9 手机英文 320×568 暂停按钮压登录按钮、订阅条超出视口 | **已修**：暂停按钮 y 76–120，登录按钮 y 122 起，没有重叠；订阅条 y 512–564，在 568 以内。`.m-hero` 总高 580，比视口高 12px，是动效层多出的空白，不影响操作 |

## 5. 新发现（不影响结论，进实现票）

- **N1（P2）英文手机 320×568，圆压住「See clearly」**：圆 x 112–208、y 272–368，标题 y 352–383，英文「See clearly」比中文「再看清」宽，「ly」被圆盖住（`Mobile-lang-English-320-light.png`）。违反 V1/V2（内容不被遮挡，H1）。390×664 圆 y 318–414、标题 y 426 起，不重叠。建议矮屏（`max-height:600px`）下圆再缩小或上移 20px，或标题字号缩一档。
- **N2（P3）`.m-hero` 在 320×568 总高 580，页面多出 12px 可滚动**：不影响操作，实现时让两半高度按视口算。
- 无新增规则缺口。

## 6. 数字

| | 最终确认 | 本轮 |
|---|---|---|
| 不过的规则 | 4（U2、V3、V5、V9） | **1（V9）** |
| 底线 | A1 不过 | 全过（U13 留到关口四） |
| P0 / P1 | 0 / 1 | **0 / 0** |
| F1–F6 | — | 5 条已修，1 条（F5）部分修 |
