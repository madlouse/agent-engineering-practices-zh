---
name: article-fidelity
description: >
  Keep 100% of source media and untranslatable wording when adding a post to
  同席 (the Velicoach Mind station). Triggers on "原文", "100%", "视频", "图", "不译", "版权",
  "fidelity", "漏了", "图标".
metadata:
  short-description: "原文保真：全文、原视频、原图，不能译的不译"
user-invocable: false
---

# 原文保真

先决定这篇是不是官方全文。写进该文最后一条 `note`，用下面三种句子之一，不要混用：

- 官方中文全文：`以上为官方中文全文。` 再点名嵌入了哪些原视频、原图，并写明画面和图注不另译。
- 结构化整理：`本稿是结构化中文整理，不是逐句全文。` 再点名哪些原件已按文件嵌入。
- 缺口：`某图没有稳定的官方文件地址，本页不另画替代图。` 禁止用重绘、截图转绘或第三方示意图冒充原文。

## 收录原件

1. 打开来源，列出正文中的每一张图、每一段视频、每一个无法翻译的标识。站点页眉、页脚、下载按钮、相关文章卡片不算正文。
2. 视频用 `{ t: "video", src, caption }`。`src` 用原文件地址。`caption` 用原文图注，不翻译。
3. 图用 `{ t: "figure", src, caption, alt? }`。`caption` 保留原文图注或图内标题。`alt` 只有在原文提供了更长的说明时才填，而且用原文。
4. 图里的英文、路径、命令、阶段名、专名留在图里。正文需要提到时，照写，不另造中文替代词冒充原文。
5. 官方地址会失效或依赖页面 CSS 时，把文件存进 `public/originals/`。SVG 若使用原站变量，把算好的色值写进该 SVG 自己的 `<style>`，不要改图内文字。
6. 代码、URL、命令、标识符原样保留。不发明数字、日期、能力。

## 和翻译的边界

保真先于文笔。官方中文里出现的词，即使 `article-zh-style` 平时避开，也保留。
没有官方中文时，把全文交给 `article-zh-style`，但原件块已经插在对应段落后，翻译不得把它们删掉或改写成「见图」。

怀疑这些块现在怎么接到页面上，先 Call the Skill tool with `how`。调查完再改代码，调查本身不改正文。

## 做完自查

- 来源里的每张正文图、每段正文视频，都能在 `blocks` 里找到 `src`。
- 每个 `figure` / `video` 的说明能在来源里对上，而不是事后概括。
- `note` 写明了是全文、整理，还是仍有缺口。
