# 交付流水线：主站的多 Agent 协作

> 建立：2026-11-04 · 产品负责人：「参考另一个项目（Veli）定义的几个 Agent loop，定义出这个项目不同 Agent 之间的协作；PRD 到 UI/UE 做完对抗评审后，开始拆这些 loop，看实现路径需要多少个 Agent 协作；同样要有负责观察的 Agent。能复用的就复用。」
> 复用自：Veli 仓库 `madlouse/thin-muscle-coach` 的 `docs/standards/pipeline.md`、`observer.md`、`agent-gitflow.md`、`quality-gates.md`、`spec-quality.md` 和 `.claude/agents/`（`feature/b1` 提交 `19170d2`，2026-11-04）；设计评审的做法复用 `design-bar` 技能第 5 步（独立评审）和 `references/craft.md` §6（只读验证者）。
> 本页管「主站的流水线怎么转」。和 Veli 相同的机制写一句话、引用 Veli 的固定版本（§9），只把主站不同的地方写全。冲突时以 `AGENTS.project.md`「不能越过的线」为准。

## 1. 一句话

**两条车道（站点、内容）各由一个定时任务推进，每张票由新的子 Agent 做、由另一个新的子 Agent 冷评审；关口没过不进下一阶段；GitHub 上的票、PR 和集成分支是唯一的状态；观察者从外面看整条流水线，人只看日报、关口和定稿。**

## 2. 从需求到上线：五个阶段，四个关口

PRD 第 9 节定了顺序：PRD → 设计语言 → UI/UE → 代码 → 上线，阶段之间是四个关口。每个关口有负责的 Agent 组合和能检查的出口。

| 关口 | 从哪到哪 | 出口 | 谁做、谁查 | 状态 |
|---|---|---|---|---|
| 一 | PRD → 设计语言 | PRD 对抗评审（PRD 附录） | 主会话写；独立评审 | 已过（PRD v1.0） |
| 二 | 设计语言 → UI/UE | 设计系统确认、动效选定 C | 主会话；产品负责人 | 已过 |
| 三 | UI/UE → 代码 | **3a UI/UE 对抗评审**（§2.1）；**3b 拆成就绪的规格和票**（§2.2），也就是把循环拆出来 | 3a：`design-reviewer` + `design-reviewer-b` 独立评审，`verify_canvas.py` 只读验证；3b：主会话 `to-spec`、`to-tickets`，`spec-reviewer` 冷审；主会话判定通过，拆分里涉及需求取舍的地方向产品负责人说清 | **下一步：3a（#14）** |
| 四 | 代码 → 上线 | 上线检查（§2.3） | 两条车道的循环（§4）；`design-reviewer` 两份走查；产品负责人确认上线 | 关口三之后 |

### 2.1 关口三 a：UI/UE 对抗评审

复用 `design-bar` 第 5 步和 Veli 的两人走查（不同模型、互相看不到）。

0. **标杆卡**：`docs/uiue/bar-sheet.md`（2026-11-04 已写），标杆原则 P1–P5 由 `docs/standards/quality-terms.md` 的规则判定。它是体验类决定，由主会话定、记进 `docs/uiue/decisions.md`，产品负责人有意见再改。没有它，评审打不了分，停止条件也判不了。
1. **只读验证**：`verify_canvas.py <画板目录> --out docs/uiue/reviews/<日期>-ui-v1 --themes light,dark,pseudo`，结论只有 `done` 或 `needs_work`，修到 `done`。画板引用的共享样式表在 `/_blob/` 上，加 `--blob <id>=<本地文件>` 指过去（`design-bar` 2026-11-04 加的参数）。
2. **两份独立评审**：`design-reviewer`（Opus）和 `design-reviewer-b`（Sonnet）各派一个新的，互相看不到。只给它们：三种版式 × 两种主题的截图、PRD（功能表 F01–F25、步数预算、页面状态，当作 brief）、标杆卡 `docs/uiue/bar-sheet.md` 和规则原文 `docs/standards/quality-terms.md`、设计系统 README、`velicoach-layout` 技能、`design-bar` 的 `references/rubric.md` 和 `anti-patterns.md`，以及上一轮的问题清单。不给制作过程。规则里写明由内容评审查的（C1、C2、C6、T1、T6、T7 等），同时派一个 `content-reviewer` 审画板上的文字，结论并进同一份清单。
3. **合并与修**：主会话把两份清单去重，按「影响 × 修复成本」排序，每轮修前 3 项，再派新的评审核对。停止条件见 `bar-sheet.md` §7：P1–P5 都 ≥ 4 分且底线全过才算通过；一轮没有提升或已经 3 轮还没通过，就在 #13 上报，不算通过。
4. **需求覆盖**：PRD 每个 v1 功能都在画板上有状态，或在覆盖表里写明为什么没有界面。
5. **出口**：报告放 `docs/uiue/reviews/<日期>-ui-v1/`。P1–P5 都 ≥ 4 分、底线全过、P0 和 P1 为 0 时，主会话判定 3a 通过，在 #13 写明结论和理由（体验类决定，产品负责人有意见再改；涉及需求的改动另外说清）；没到这条线就按 `bar-sheet.md` §7 上报，不算通过。被接受的修改写回设计系统和 `docs/uiue/decisions.md`。

### 2.2 关口三 b：拆成规格和票

- 站点车道：按 v1 范围拆里程碑和票，竖切（数据 → 页面 → 测试），一次会话做得完。规格和票的出口标准照 Veli 的 `spec-quality.md` §2–§3，主站不同的两处：没有数据库和健康数据的条目不适用；每张界面票必须写明对应的画板和状态。
- 内容车道：已有总票 #3 和九个模块票 #4–#12。每张票先补齐验收，标 `ready-for-agent`。
- 验收里的质量词和虚词按 `AGENTS.project.md` 第 10 条。
- `spec-reviewer` 冷审一批票，结论「就绪：是 / 否」。两轮不过交产品负责人。冷审通过后主会话判定关口三通过，在 #13 写明拆分和理由，循环开始跑（§8）；拆分里涉及需求取舍的地方（砍范围、改优先级）先向产品负责人说清。

### 2.3 关口四：上线

在集成分支的预览部署上，下面全部通过，产品负责人确认后，集成分支一次合并进 `site` 并上线：

- PRD 第 6 节「上线前检查」六项：三种版式、两套主题、减弱动态效果、键盘操作；
- PRD「关键路径与页面状态」的六条路径各有一条端到端测试，跑过且没有未说明的跳过；
- Lighthouse（性能预算作为上线关口，PRD 第 8 节）；axe 严重和较严重的问题为 0；
- 真机各走一遍：iOS 和 iPadOS 的 Safari、Android 的 Chrome（产品负责人在场，同 Veli 的多端通道 B）；
- 折叠屏：U13、A8 按 `quality-terms.md` 的「怎么查」做；
- 两份独立走查（`design-reviewer` 两份）P0、P1 为 0；`quality-terms.md` 里适用的规则全部通过（含只能在实现上查的 U8 速度、U9 响应时间）；
- 五秒测试：5 个没看过的人看首页和三站首屏 5 秒，至少 4 人说得出「给谁的、能做什么、点哪里」（U2，产品负责人找人）；
- `npm run check:terms`、`npm run check:vague` 通过；中英两版齐全；
- 带 `risk:high` 的 PR 都有安全评审的通过记录。

## 3. 角色：谁做、谁查、交接物

复用 Veli `observer.md` §2 的角色表。每一段都要有人负责、有交接物、有人检查。

| 角色 | 定义 | 模型 · 强度 | 负责 | 交接物 | 谁来查 |
|---|---|---|---|---|---|
| 产品负责人 | — | — | 产品意图和需求类的改动、关口四（上线）的确认、内容的周一选题和周五定稿、`owner:merge` 的合并；安排持证教练审核训练指导类内容，把审核记录贴在内容票上 | 状态 issue 里的回复 | — |
| 主会话 | 和产品负责人对话的会话 | Opus · high | 关口三 a 的合并与修改、规格和拆票、落实产品负责人的决定；把内容票提出的写回（PRD、技能、术语表、画板、`trace.md`）落到对应位置；写合并脚本 | 规格、票、`chore/` 分支的 PR | `spec-reviewer`；观察者 |
| 站点票推进器 | 定时任务 ① | Sonnet · medium | 选票、派活、合并、交接 | 运行锁、领票评论、交接评论 | 观察者 |
| 内容推进器 | 定时任务 ② | Sonnet · medium | 同上，只管内容车道 | 同上 | 观察者 |
| `implementer` | 复用 | Sonnet · medium | 实现一张站点票 + 证据 | PR 和证据表 | `reviewer` |
| `reviewer` | 复用，加主站检查 | Opus · medium | 冷评审一个站点 PR | 一条结论评论 + 标签 | 观察者抽查复审 |
| `content-writer` | 新增 | Sonnet · medium | 起草一张内容票：选材、成稿、中英两版 | PR 和出处表 | `content-reviewer` |
| `content-reviewer` | 新增 | Opus · medium | 冷审一个内容 PR：事实、出处、授权、术语、双语 | 一条结论评论 + 标签 | 观察者抽查 |
| `design-reviewer` / `design-reviewer-b` | 新增，复用 Veli 两人走查和 `design-bar` 独立评审 | Opus · medium / Sonnet · medium | 关口三 a、里程碑关口和关口四的独立评审 | 各自一份问题清单 | 主会话合并；观察者 |
| `security-reviewer` | 复用 | Sonnet · high | 带 `risk:high` 的 PR 的独立安全评审：订阅和发信、表单、数据库和行级安全、密钥（PRD 第 8 节「安全」） | 一条 `kind=security` 结论评论 + `security:*` 标签 | 观察者全查 |
| `spec-reviewer` | 复用 | Opus · high | 冷审规格和一批票 | 一条「就绪：是 / 否」评论 | 观察者看下游返工 |
| `digest-writer` | 复用 | Haiku · low | 日报正文 | 状态 issue 正文 | 观察者核对和真实状态一致 |
| `observer` | 复用 | Opus · high | 整条流水线和机制本身（`observer.md`） | 观察报告、`docs/quality/` | 产品负责人每周看一次 |
| 合并脚本、检查脚本 | 复用后改写 | — | 确定性的门 | 退出码 | 观察者看有没有被绕过 |

**一共 10 份子 Agent 定义、4 个定时任务**（§4）。平时同一时刻 6 个 Agent 在跑：两条车道各一个主会话 + 一个做事的 + 一个评审的。最多约 11 个：站点车道一次能跑 6 小时，会和观察者（主会话 + `observer` + 它派的 `reviewer`）、日报（主会话 + `digest-writer`）重叠；`risk:high` 的 PR 同时派两个评审。返工第 2 轮的 `implementer` 和 `content-writer` 改用 Opus · medium（同 Veli）。

## 4. 循环（定时任务）

| # | 循环 | 触发 | 做什么 | 刹车 | 交还给人 |
|---|---|---|---|---|---|
| ① | **站点票推进器** | 心跳每 2 小时，拉起后连续推进 | 照 Veli `pipeline.md` §7 的 11 步：开工检查和运行锁 → 接棒 → 选票 → 领票 → `implementer` → 证据 → 预览 READY 后派 `reviewer` → 返工 → 合并脚本 → 交接 → 下一张；里程碑开着的票为 0 时做里程碑关口（`design-reviewer` 两份独立评审 + `check_page.py` 六项） | 一次最多 8 张或 6 小时；开着的 agent PR ≥ 3 不领新票；评审最多 3 次，第 3 次不过废弃重来并复盘 | 意图不清、要账号：标 `ready-for-human` + 两行决策简报 |
| ② | **内容推进器** | 心跳每天一次；运营期按 PRD 第 6 节的每周节奏 | 阶段一（定框架）：按 #3 的顺序做模块票，`content-writer` 起草选材标准、模板和样稿，`content-reviewer` 冷审，PR 打 `owner:merge` 等产品负责人确认样稿。阶段二（运营）：周一推荐 5 篇候选和 3 个训练主题，周二到周四生产，周五列疑点交定稿，周六排期，周日起草订阅邮件 | 同 ①；健康内容另要持证教练的审核记录 | 周一选题、周五定稿、周日发信由人做 |
| ③ | **日报** | 每天早上 | 覆盖更新状态 issue 正文（§6） | 只读 | 产品负责人每天看 2–5 分钟 |
| ④ | **观察者** | 每天日报之前；周日加深度 | `docs/standards/observer.md` | 不写票里的代码、不合并票的 PR；可以打 `agent:stop` | 每周机制评审 |

评审清扫和清理与经验两个循环先不开，按 §8 的条件再开（定义照 Veli 的 `review-sweeper.md`、`janitor.md`）。

每个循环的提示词在 `docs/delivery/loops/`，改提示词先改那里，再同步到定时任务。

### 4.1 两条车道怎么不打架：按文件分

| 位置 | 站点车道 | 内容车道 |
|---|---|---|
| 页面、组件、路由、样式、token、脚本、配置、`src/content/types.ts`（块类型） | 改 | 不改 |
| 一篇文章的文件 `src/content/<slug>.ts`、`public/originals/`、`public/explainers/`、`docs/content/` | 不改 | 改 |
| `src/content/index.ts`（文章注册表） | 改结构 | 只加或删一行注册 |
| `src/content/explainers.ts`、界面文案的翻译文件 | 加新的键和字段（带初稿） | 只改已有条目的文字 |
| PRD、技能、术语表、设计系统、画板、`docs/requirements/` | 不改，在 PR 说明里列出要写回什么 | 同左 |

PRD、技能、术语表、设计系统、画板和需求追踪由主会话改（§3）：两条车道的 PR 说明里列出「要写回的」，主会话合并后落实。内容要新的块类型或字段：在内容票里写清楚，另开一张站点票，站点票合并以后内容票才往下做（用 GitHub 原生的「被谁卡住」连起来）。

## 5. 分支、标签、锁

- **分支**：生产分支 `site`（默认分支）。命名照 Veli `agent-gitflow.md` §3.1：`feat/<票号>-<短名>`、`fix/…`、`content/<票号>-<短名>`（内容车道，和 `feat/` 一样算票的分支）、`obs/<日期>-<短名>`（观察者）、`chore/<短名>`（主会话）。
  - **上线前**：集成分支 `feature/v1` 从 `site` 开，两条车道的 PR 都合并回 `feature/v1`；关口四通过后，产品负责人确认一次合并进 `site`。
  - **上线后**：`feature/v1` 删掉，两条车道的 PR 直接以 `site` 为 base，门不变（冷评审通过、预览 READY、合并脚本）。内容的周六上线就是把定稿的 PR 合并进 `site`。
- **标签**：issue 用 `ready-for-agent`、`ready-for-human`、`spec`、`gate`，车道用 `lane:site`、`lane:content`；PR 用 `agent:pass`、`agent:rework`、`agent:hold`、`owner:merge`、`risk:high`、`security:pass`、`security:rework`，含义照 Veli `pipeline.md` §3，只有 `owner:merge` 在主站多一种用法：**等产品负责人本人合并**的 PR，除了删掉或放宽要求的机制改动，还有要人定稿的内容（模块样稿、每周的文章）。产品负责人合并就是定稿。
- **机器人标记**：Agent 在 GitHub 上写的**每一条**评论，首行都是 `<!-- vc-bot role=<角色> -->`（运行锁、领票、交接、评审、观察报告都一样）。不带这个标记的评论才算产品负责人的回复；漏了标记，Agent 的话会被当成指令执行。
- **总开关和运行锁**：在状态 issue #13「主站工厂状态」上。它带 `agent:stop` 时，任何运行开工就结束。运行锁照 Veli `pipeline.md` §7 第 1 步：评论「运行开始 / 运行结束 / 运行跳过」，评论开头写 `<!-- vc-bot role=<循环名> -->`；90 分钟没有动静算断掉。两条车道各用自己的锁（评论里写 `lane=site` 或 `lane=content`），互不阻塞。
- **领票**：指派给自己 + 一条领票评论（分支名、接棒结果、就绪结论）。
- **交接评论**：格式照 Veli `pipeline.md` §8，标记改为 `<!-- vc-handoff -->`。

## 6. 人的注意力

状态 issue「主站工厂状态」的正文每天覆盖更新，格式照 Veli `pipeline.md` §6：今天（合并、在评审、卡住、集成分支的状态）、等你合并、等你决定（最多 3 条，每条两行 + 推荐答案）、里程碑进度。

**集成分支的状态只有绿和红，只在这里定义**：绿 = §7 的检查全过，且最新提交的预览部署 READY；红 = 检查不过，或预览部署不是 READY（排队或构建中先等，超过 30 分钟算红）。主站没有健康检查接口，所以没有 Veli 的「黄」。红了先修，不领新票。

主站多两段：

```
## 内容这周
- 周一选题：候选 5 篇 / 3 个训练主题，等你选（回复编号）
- 周五定稿：#… 列了 x 个疑点
## 关口
- 关口三 a / 三 b / 四：进行中 / 等你确认 / 已过
```

只有不带 `<!-- vc-bot` 标记的评论算产品负责人的回复。一句「全部按推荐」可以批量回复。

## 7. 主站的检查（实际跑过才算）

| 检查 | 命令 | 谁跑 |
|---|---|---|
| 术语 | `npm run check:terms` | 两条车道的评审 |
| 质量词 | `npm run check:vague`；票和规格的正文先存成临时文件再跑 `node scripts/check-vague.mjs <文件>` | 两条车道的评审；`spec-reviewer` |
| 脚本单元测试 | `npm test`（含 `node --test 'scripts/**/*.test.mjs'`；2026-11-04 有 8 个失败，见 §8 第 0 阶段） | `reviewer` |
| 类型检查、lint、构建 | 分支的 Vercel 预览部署，构建命令是 `tsc --noEmit && eslint . && vite build`、安装带开发依赖 | `reviewer` 用 Vercel 连接器看构建日志 |
| 页面 | `python .grok/skills/design-bar/scripts/check_page.py <预览地址> --out <目录> --dark --widths 320,375,744,1180 --targets-up-to 1180`：三种版式和 320px、浅色深色的截图，溢出、小字、对比度、所有宽度的可点区域、焦点、控制台报错，并查样式里有没有 `prefers-reduced-motion`。减弱动态效果和键盘操作它不走，界面票的验收里写明怎么手工验证。预览部署有访问保护，用 #15 里配的绕过头访问 | `reviewer`（界面票）；里程碑关口 |
| token | `python .grok/skills/design-bar/scripts/lint_tokens.py src --tokens <token 文件>` | `reviewer`（界面票） |
| 画板 | `python .grok/skills/design-bar/scripts/verify_canvas.py <画板目录> --out <目录> --themes light,dark,pseudo`（`--out` 必填） | 关口三 a；改了画板的票 |
| 内容 | 出处逐条打开核对；授权状态；`velicoach-content` 的审核清单；中英两版都在 | `content-reviewer` |

## 8. 先慢后快

复用 Veli `pipeline.md` §4 的四个阶段，进入条件按主站调整。

| 阶段 | 开哪些 | 进入条件 |
|---|---|---|
| 0 准备 | 都不开 | 前置票 #15 全部做完：Vercel 项目和预览绕过头、`feature/v1`、基线变绿（`npm test` 现在 8 个失败）、合并脚本（主会话从 Veli 复用改写，`chore/` 分支，冷评审后 `owner:merge`，不能由票自己写：票的 PR 不能改门槛文件）、云端会话放行合并脚本 |
| 试跑 | 手动跑一次 ①，做第一张票 | 关口三已过；走完整条链路，交接评论格式对 |
| 1 | ① ② ③ ④ | 前 5 个合并的 PR 产品负责人抽查，没有要退回的 |
| 2 | 加评审清扫、清理与经验 | 连续一周没有「集成分支红超过 4 小时」 |

## 9. 复用的方式：引用 Veli 的固定版本

**共用机制的版本：Veli `feature/b1` 提交 `19170d2`。** 本页写「照 Veli 某某」的地方，Agent 读那个版本的原文：

```
git clone --filter=blob:none https://github.com/madlouse/thin-muscle-coach /tmp/veli
git -C /tmp/veli checkout 19170d2
```

读的时候按下表换成主站的说法。表里没有的 Veli 专用内容（训练、健康数据、Supabase、iOS），主站不适用。

| Veli | 主站 |
|---|---|
| 集成分支 `feature/b1`，生产 `main`，#72 一次合并 | `feature/v1`，生产 `site`，关口四一次合并 |
| 总纲 #7 的 `agent:stop`；#85「B1 工厂状态」 | #13「主站工厂状态」（总开关、运行锁、日报都在它上面） |
| `<!-- veli-bot` / `veli-handoff` / `veli-review` | `<!-- vc-bot` / `vc-handoff` / `vc-review` |
| `npm run verify`、`tmc-dev-setup` §5 | 本页 §7 的检查 |
| `tmc-ux-walkthrough`、`ux-walker` 两人走查 | `design-reviewer` + `design-reviewer-b`，加 `check_page.py` 六项 |
| `docs/delivery/milestones/M<n>.json` | 里程碑总票里写的退出条件 |
| `risk:high`、`security-reviewer` | 照用：订阅要收邮箱（PRD F07），订阅和发信、表单、数据库和行级安全、密钥的 PR 都打 `risk:high` |
| 数据库迁移（Supabase、集成库） | 主站用自己的数据库和 `npm run db:migrate`；改表的票写明迁移，在预览环境执行 |
| 集成分支「黄」、`/api/health` | 不适用，状态只有绿和红（§6） |
| `scripts/merge-ticket-pr.sh`、`merge-gates.mjs` | 主站的同名脚本（§8 第 0 阶段，主会话写）：认 `kind=general` 和 `kind=content` 两种结论；`content/` 和 `feat/`、`fix/` 一样算票的分支，同样不能改门槛文件、按关掉没合并的 PR 数尝试次数 |

## 10. 和 Veli 一起改机制

两个仓库的流水线是同一套机制。Veli 那边改了规则（`docs/standards/` 或 `.claude/agents/`），主站的观察者每周日对比一次：适用于主站的，开一个 `obs/` PR 把 §9 的版本号换成新提交（必要时补对照表）；不适用的在观察报告里写一句理由。换版本号算改流程，打 `owner:merge` 等产品负责人合并。主站发现的机制问题，也写进观察报告，由产品负责人决定要不要改到 Veli。经验库各自维护，观察者读对方的 `docs/delivery/lessons.md`。

## 11. 总开关和回退

- 暂停：状态 issue 打 `agent:stop`，或在定时任务里关掉。
- 回退一个合并：`git revert -m 1 <合并提交>`，走一个修复 PR，不改历史。
- 流水线自己出错：写进日报，交给产品负责人决定；Agent 不自动修流水线本身。
