---
name: article-pipeline
description: >
  Compose one article from poteto leaf skills plus the site leaves.
  Use when the user asks to add, translate, expand, refresh, or check a post.
  Triggers on "收录", "放进博客", "处理原文", "文章流水线", "制作流水线",
  "article pipeline", "加一篇", "poteto", "pstack".
metadata:
  short-description: "一篇文章的制作顺序：poteto 叶子 skill 与本站四份 skill"
user-invocable: false
---

# 文章制作流水线

一篇来源走完下面的顺序。每一步只打开点名的 skill，按它的正文做，不把别的 skill 的规则抄进这一步。

用户只点了其中一件事时，只做那一件，并从那一件的 skill 进入。不要为了「完整」重跑已经核对过的正文。

沙箱契约在 `AGENTS.md`。预览、端口、认证、数据库以它为准。这里不跑 poteto-mode 的提交和开 PR 循环。那份 skill 没有装进本项目。

Poteto 叶子来自 [mdsmithaustin/pstack](https://github.com/mdsmithaustin/pstack)（MIT）。装在 `.grok/skills/`，与本站 skill 并列。不改它们的正文。要改的是本文件的顺序。

## 顺序

1. Call the Skill tool with `principle-sequence-verifiable-units`. 一篇来源是一个单元。这一篇的检查过了，再开始下一篇。
2. Call the Skill tool with `article-fidelity`. 没有稳定文件地址的图，停在这一步，不另画。
3. 来源不是官方中文时，Call the Skill tool with `article-zh-style`. 官方中文整段原样留下，不送去改写。
4. 本站新写的中文和英文（整理、注记、旁白、屏幕短句）写完后，Call the Skill tool with `technical-writing`. 然后 Call the Skill tool with `unslop`. 官方中文和原图注不送去这两份。
5. 正文稳定之后，Call the Skill tool with `article-feynman`. 改播放器之前，Call the Skill tool with `principle-experience-first`，再打开 `design-ui`。
6. Call the Skill tool with `principle-minimize-reader-load`. 讲解不另起一套导航，不把旁白整段贴上屏幕。
7. Call the Skill tool with `article-visual`. 然后 Call the Skill tool with `principle-prove-it-works`. 证据是渲染出来的页面，不是类型检查通过。
8. 这一轮改了代码时，Call the Skill tool with `deslop`. 它点名的 `no-comments` 也要打开。它指向的 poteto-mode playbook 不在本项目里。那一步停下来，写出缺的文件，不要现场补一份 playbook。
9. 想加块类型、第二套播放器或另一份说明之前，Call the Skill tool with `principle-subtract-before-you-add`.

怀疑现有代码怎么接到页面上，先 Call the Skill tool with `how`，再改。

同一条纠正写到第二遍时，Call the Skill tool with `principle-encode-lessons-in-structure`. 写进对应 skill 的一步，不在本文件再抄一遍。

## 落点

- 文章在 `src/content/`。块类型只使用 `src/content/types.ts` 里已有的 `Block`。
- 原图、原视频能外链官方地址就外链。地址不稳就放 `public/originals/`。
- 讲解旁白在 `public/explainers/{slug}.zh.mp3` 与 `{slug}.en.mp3`，文案在 `src/content/explainers.ts`。
- 播放器是 `src/components/feynman-film.tsx`，挂在标题和元信息之后、正文之前。
- 文末 `note` 写明是全文、整理，还是仍有缺口。

## Grok Build 里怎么打开

本环境没有名为 Skill 的工具。`Call the Skill tool with` 一个名字，就是读 `.grok/skills/<name>/SKILL.md` 全文，再按它的步骤去读它点名的文件。名字对不上目录，就停下并写出缺的路径。
