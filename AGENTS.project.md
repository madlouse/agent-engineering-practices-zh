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
| 做票、拆票、跑流水线、改协作机制 | [docs/delivery/README.md](docs/delivery/README.md)（开发团队和开发路线的入口：`team-setup.md`、`roadmap.md`）、[docs/standards/pipeline.md](docs/standards/pipeline.md)（关口、角色、循环、车道、复用 Veli 的方式）、[docs/standards/observer.md](docs/standards/observer.md)、[docs/delivery/loops/](docs/delivery/loops/)（定时任务的提示词）、[docs/delivery/lessons.md](docs/delivery/lessons.md)；子 Agent 定义在 `.claude/agents/` |
| 技术选型、部署、结构变化 | [docs/architecture/overview.md](docs/architecture/overview.md)、[docs/architecture/adr/](docs/architecture/adr/)、[docs/deploy.md](docs/deploy.md)；先写 ADR 再动手 |

## 技能

技能都在 `.grok/skills/`。`.claude/skills/` 里放了指向主站相关技能的链接，Claude Code 能自动发现；新加的技能要在那里也加一个链接。做对应的事情时先加载技能，再动手。

**技能在这里迭代，这里是唯一来源。** 打磨中改进的技能（包括从 Veli 复用来的）都改在 `.grok/skills/<名字>/` 并随 PR 提交；账号里的同名技能是副本，仓库里改完再同步过去。观察者每周对比一次，发现副本落后就在观察报告里写明。

| 技能 | 什么时候用 |
|---|---|
| `velicoach-content` | 写、改写、校对、审阅或校准任何对外内容：研究卡片、里程碑、学习路径步骤、文章、3 分钟视频脚本、开发日志、订阅邮件、页面文案、社交帖子 |
| `velicoach-layout` | 设计或实现主站的页面、组件、画板：骨架、三种版式、阅读排版、导航与语言切换、一站一键一秒、原地展开、玻璃、「叶与网」动效、交付检查 |
| `article-pipeline` | 收录一篇文章：顺序、该停的地方、每一步叫哪一份技能都写在那里 |
| `design-ui` | 界面实现和打磨 |
| `threejs` | 首页「叶与网」动效的实现 |
| `design-bar` | 画板和页面的只读验证（`verify_canvas.py`、`check_page.py`、`lint_tokens.py`）、独立设计评审、需求覆盖；关口三 a 和界面票都用。从 Veli 复用 |
| `grill-with-docs`、`to-spec`、`to-tickets` | 新需求开工前逐题追问；把定下来的需求写成规格、拆成带依赖的票（关口三 b）。Matt Pocock 的技能，MIT，从 Veli 复用 |
| `implement`、`implement-spec`、`tdd`、`code-review` | 按票实现、测试先行、代码评审（站点车道）。同上 |
| `domain-modeling`、`grilling` | 改术语表、写 ADR；追问一个方案。同上 |
| `agent-team-setup` | 给一个产品仓库搭多 Agent 开发团队：关口、角色、车道、循环、观察者，复用已经在跑的流水线。主站是第一次做成的例子 |

### 给 Matt Pocock 技能的约定

- **Issue tracker**：本仓库的 GitHub Issues；云端会话只能用 REST（`gh api`）。
- **Triage labels**：issue 用 `ready-for-agent`、`ready-for-human`、`spec`、`gate`，车道用 `lane:site`、`lane:content`；PR 上另有 `agent:pass`、`agent:rework`、`agent:hold`、`owner:merge`、`risk:high`、`security:pass`、`security:rework`；状态 issue #13 上的 `agent:stop` 是总开关（`docs/standards/pipeline.md` §5）。
- **评论**：Agent 写的每一条评论首行都是 `<!-- vc-bot role=<角色> -->`；不带它的评论才算产品负责人的回复。
- **Domain docs**：单一上下文，术语表 `docs/GLOSSARY.md`，ADR 在 `docs/architecture/adr/`。

## 不能越过的线

1. **对外只放正式版**：页面和发布稿里没有占位符、过程说明、口头禅和语音转写错误；过程思考写进 `docs/`。
2. **一站、一键、一秒**：不让用户离开、不再登录；核心场景两步内完成，不常用的不超过三步；操作 P95 ≤ 1 秒；看图标和位置就会用，少放要读的字（主站 PRD 第 4 节；`quality-terms.md` U1、U7、U8、C10）。
3. **中英双语**：所有对外文字都有两版；英文按英语读者重写。
4. **设计系统是唯一来源**：主站样式只引用 token，不写死颜色、字号、间距、圆角和时长。浅色、深色两套主题都要支持，默认跟随系统。
5. **主站不读健康数据**：只用账号里的名字和邮箱；训练内容只在 Veli 里读。
6. **事实有出处**：数字、研究、引用都写明出处；官方中文原样保留，学习分享，不替代原文。
7. **一条意见代表一类问题**：改完所有同类位置，把原则写回技能、设计系统或术语表，在 `docs/requirements/trace.md` 记一笔。
8. 密钥只放在服务端环境变量，不写进代码、文档和提交信息。
9. **合并只走合并脚本**：上线前所有票的 PR 合并进集成分支 `feature/v1`，关口四通过后由产品负责人确认一次合并进 `site`；上线后 PR 直接进 `site`，门不变（`docs/standards/pipeline.md` §5）。
10. **形容词和动词都要能判对错**：「体验友好」「高级感」「打磨」「优化」这类词，意思以 [docs/standards/quality-terms.md](docs/standards/quality-terms.md) 为准：每个词有对标产品、可观察的特征和可检查的规则。验收里用到它们必须链到定义，或者直接写成那里的规则；「适当」「尽量」这类判不了对错的虚词不能出现在验收里（`npm run check:vague`）。新的质量词先进那份文档，再用。

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
