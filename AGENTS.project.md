# 落地实践

本文件是这个博客的项目说明。沙箱契约以 `AGENTS.md` 为准：预览、端口、认证和数据库不要在这里改。

## 这篇站点在做什么

收录公开的 Agent 工程实践，以及一篇双语的 Agent 与生活。官方中文原样保留。没有官方中文时，按信达雅翻译。学习分享，不替代原文。

## 收录一篇时

只打开 `article-pipeline`。顺序、该停的地方、以及每一步叫哪一份 skill，都写在那里。

本站四份叶子是 `article-fidelity`、`article-zh-style`、`article-feynman`、`article-visual`。
Poteto 的叶子装在同一处 `.grok/skills/`：`principle-sequence-verifiable-units`、`technical-writing`、`unslop`、`principle-experience-first`、`principle-minimize-reader-load`、`principle-prove-it-works`、`deslop`、`no-comments`、`how`、`principle-subtract-before-you-add`、`principle-encode-lessons-in-structure`、`pstack-harness`。
界面改动另开已有的 `design-ui`。

用户只点了其中一件事时，只做那一件。不要在这里再写一遍步骤。

## 内容约定

- 文章在 `src/content/`。块类型见 `src/content/types.ts`。
- 原图、原视频的说明不翻译。文件在 `public/originals/`，或使用官方可外链的地址。
- 讲解文案在 `src/content/explainers.ts`。中文旁白在 `public/explainers/{slug}.zh.mp3`，英文旁白在 `{slug}.en.mp3`。
- 文末 `note` 写明是全文、整理，还是仍有缺口。
