---
name: article-visual
description: >
  Visually check 同席 (Velicoach Mind) pages, figures, videos, and code blocks before
  calling an article done. Triggers on "视觉", "代码块", "图注", "目录",
  "检查页面", "visual QA".
metadata:
  short-description: "视觉检查：正文、原图、代码、窄屏、讲解"
user-invocable: false
---

# 视觉检查

在保真、中文、讲解都落地之后做。不在这一步改文章事实。

## 先看结构

- 页眉、阅读进度、目录、语言切换沿用现有组件。不新加一套导航。
- 讲解在正文之前，宽度与正文同为 `max-w-2xl`。五镜在窄屏不横溢。
- 原视频有原生控件，图注以「原文视频，不译。」起头。
- 原图在纸色边框里，图注以「原图，不译。」起头。图内文字保持原文件，不重绘。
- 带箭头的流程用纸面步骤，不放进深色圆角终端。真正的代码用 `.code-scroll`。
- 英文模式走 `[data-lang="en"]` 的衬线与无衬线，不另加字体。

## 窄屏

约 390 像素宽时：没有横向溢出；按钮和目录摘要可点区域不小于 44 像素；
长图可以横向看全，页面本身不跟着横溢。目录在大屏是侧栏，小屏是 `details`。

## 对照

桌面和手机各看：首页、刚改的文章顶部（讲解）、原图或原视频所在的位置、文末来源。
控制台没有未捕获错误。原图裂开、视频只有空框、讲解压住标题，都算没过。

## 不要做

- 不要为了对比度把 `--color-faint` 改到和 `--color-muted` 分不开。层级是故意的。
- 不要把原图的配色收成站点五色。原图保持原样，站点界面才守五色。
- 不要在 JSX 里写新的十六进制色或无尺度的间距。进度条的动态宽度除外。

看完页面后，Call the Skill tool with `principle-prove-it-works`。真页面是证据。类型检查通过不算看过。
这一步不改文章事实。想加一块新界面之前，Call the Skill tool with `principle-subtract-before-you-add`。
