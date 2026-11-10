# Velicoach

本文件是这个仓库的项目说明。沙箱契约以 `AGENTS.md` 为准：预览、端口、认证和数据库不要在这里改。

本仓库是 velicoach.com 主站：「AGI 路上的陪练」，先站稳，再看清，然后动手。首页、三站（站稳、看清、动手）的页面，以及看清一站的文章（原来的同席博客）都在这里。Veli（站稳一站的产品）在 `madlouse/thin-muscle-coach`；以后的新产品各开仓库，从动手一站链接过去。

## 先读什么

| 你要做的事 | 先读 |
|---|---|
| 任何任务 | [docs/README.md](docs/README.md)（文档地图）、[docs/GLOSSARY.md](docs/GLOSSARY.md)（术语，一个词一个意思） |
| 弄清用户到底要什么 | [docs/requirements/timeline.md](docs/requirements/timeline.md)（用户原句，按时间）→ [docs/requirements/trace.md](docs/requirements/trace.md)（第 28 条起每条怎么理解、落在哪）→ [docs/requirements/summary.md](docs/requirements/summary.md)（原同席博客部分按主题汇总）。汇总和原句冲突时，以原句为准；原句按语义和整体目标理解，语音转写错误不照字面；第 1 条只有残段，不要补写 |
| 改主站需求或产品规则 | [docs/prd/velicoach.md](docs/prd/velicoach.md)（主站 PRD 快照，在线文档是唯一来源）、[docs/prd/velicoach-strategy.md](docs/prd/velicoach-strategy.md) |
| 改看清的文章部分的范围 | [docs/prd/remaining.md](docs/prd/remaining.md)、[docs/uiue/identity.md](docs/uiue/identity.md)、[docs/issues/README.md](docs/issues/README.md) |
| 写、改、审内容 | 技能 `velicoach-content`；收录一篇文章另见下面「收录一篇时」 |
| 改界面、版式、交互、动效 | 技能 `velicoach-layout`、[docs/uiue/design-system.md](docs/uiue/design-system.md)、[docs/uiue/decisions.md](docs/uiue/decisions.md)；界面实现另开已有的 `design-ui` |
| 技术选型、部署、结构变化 | [docs/architecture/overview.md](docs/architecture/overview.md)、[docs/architecture/adr/](docs/architecture/adr/)、[docs/deploy.md](docs/deploy.md)；先写 ADR 再动手 |

## 技能

技能都在 `.grok/skills/`。`.claude/skills/` 里放了指向主站相关技能的链接，Claude Code 能自动发现；新加的技能要在那里也加一个链接。做对应的事情时先加载技能，再动手：

| 技能 | 什么时候用 |
|---|---|
| `velicoach-content` | 写、改写、校对、审阅或校准任何对外内容：研究卡片、里程碑、学习路径步骤、文章、3 分钟视频脚本、开发日志、订阅邮件、页面文案、社交帖子 |
| `velicoach-layout` | 设计或实现主站的页面、组件、画板：骨架、三种版式、阅读排版、导航与语言切换、两步原则、原地展开、玻璃、「叶与网」动效、交付检查 |
| `article-pipeline` | 收录一篇文章：顺序、该停的地方、每一步叫哪一份技能都写在那里 |
| `design-ui` | 界面实现和打磨 |
| `threejs` | 首页「叶与网」动效的实现 |

## 不能越过的线

1. **对外只放正式版**：页面和发布稿里没有占位符、过程说明、口头禅和语音转写错误；过程思考写进 `docs/`。
2. **两步原则**：核心场景两步内完成，不常用的不超过三步（主站 PRD 第 4 节「步数预算」）；按钮直达结果，一个入口有几个去处时原地展开。
3. **中英双语**：所有对外文字都有两版；英文按英语读者重写。
4. **设计系统是唯一来源**：主站样式只引用 token，不写死颜色、字号、间距、圆角和时长。浅色、深色两套主题都要支持，默认跟随系统。
5. **主站不读健康数据**：只用账号里的名字和邮箱；训练内容只在 Veli 里读。
6. **事实有出处**：数字、研究、引用都写明出处；官方中文原样保留，学习分享，不替代原文。
7. **一条意见代表一类问题**：改完所有同类位置，把原则写回技能、设计系统或术语表，在 `docs/requirements/trace.md` 记一笔。
8. 密钥只放在服务端环境变量，不写进代码、文档和提交信息。

## 收录一篇时

只打开 `article-pipeline`。顺序、该停的地方、以及每一步叫哪一份 skill，都写在那里。

本站四份叶子是 `article-fidelity`、`article-zh-style`、`article-feynman`、`article-visual`。
Poteto 的叶子装在同一处 `.grok/skills/`：`principle-sequence-verifiable-units`、`technical-writing`、`unslop`、`principle-experience-first`、`principle-minimize-reader-load`、`principle-prove-it-works`、`deslop`、`no-comments`、`how`、`principle-subtract-before-you-add`、`principle-encode-lessons-in-structure`、`pstack-harness`。

用户只点了其中一件事时，只做那一件。不要在这里再写一遍步骤。`article-zh-style` 和 `velicoach-content` 冲突时，以 `velicoach-content` 为准。

## 内容约定

- 文章在 `src/content/`。块类型见 `src/content/types.ts`。
- 原图、原视频的说明不翻译。文件在 `public/originals/`，或使用官方可外链的地址。
- 讲解文案在 `src/content/explainers.ts`。中文旁白在 `public/explainers/{slug}.zh.mp3`，英文旁白在 `{slug}.en.mp3`。
- 文末 `note` 写明是全文、整理，还是仍有缺口。

## 冲突时以谁为准

用户最新确认的意见（`trace.md`）> 主站 PRD > 设计系统 > 技能 > 代码。发现冲突时改低的一方，并在 `docs/requirements/trace.md` 或 `docs/uiue/decisions.md` 记一笔。
