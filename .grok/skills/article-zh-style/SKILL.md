---
name: article-zh-style
description: >
  Write or revise Chinese for 同席 (Velicoach Mind) in the Fenng technical-doc style.
  Triggers on "翻译", "信达雅", "中文技术文档", "Fenng", "体例", "排版".
metadata:
  short-description: "中文体例：信达雅，官方中文不改口"
user-invocable: false
---

# 中文体例

参照 [Fenng/Tech-Doc-Style-Chinese](https://github.com/Fenng/Tech-Doc-Style-Chinese)。
不要使用 kai 排版 skill。

## 先分流

- 来源有官方中文：整段搬入，不润色，不替换用词。原文写了「闭环」就留「闭环」。
- 没有官方中文：翻译。标准是信、达、雅。准确，顺，克制。不添原文本没有的判断。

## 句子

- 中文引号用「」。书名、篇名需要时用《》。
- 中文与英文、数字之间留一个空格。盘古之白。
- 术语全文一致。第一次出现可以带原文专名，之后不来回换译名。
- 不用赋能、抓手、闭环、打通，除非这四个字写在官方原文里。
- 代码、URL、命令、文件名、标识符用等宽语义，原样，不翻译。
- 一步只写一个动作。步骤用有序列表，并列用无序列表。
- 不发明数字、日期、百分比、能力。不确定就写「原文未给出」，不要补一个看起来合理的数。

## 块

只使用 `Block` 已有类型：`p` `h2` `h3` `ul` `ol` `q` `code` `note` `video` `figure`。
`h2` / `h3` 的 `id` 在该文内唯一。引文用 `q`，不把引文揉进段落。
原视频、原图的 `caption` 不翻译，见 `article-fidelity`。

## 英文对照

只有用户要求双语时才写 `blocksEn`。英文对照是结构化对照，不假装逐句还原，
除非来源本身就是英文全文并且本页决定整篇搬入。`titleEn` 与 `dekEn` 成对出现。

## 写完

本站新写的句子，Call the Skill tool with `technical-writing`，再 Call the Skill tool with `unslop`。
官方中文整段不送去这两份 skill。原图注、原视频说明也不送。
