# 文档地图

先读 [GLOSSARY.md](GLOSSARY.md)（术语），再按任务进入下面的模块。同一件事只在一个地方写，其他地方链接过去。

## 在线文档（唯一来源）

主站的需求和设计语言在 Claude 的在线文档里编辑；仓库里放的是快照，供 agent 离线读取。改的时候先改在线文档，再更新快照。

| 文档 | 在线地址 | 仓库快照 |
|---|---|---|
| Velicoach 主站 PRD v2.0 | https://claude.ai/artifact/DCjVTmTknxzkLpjHgrho8R | [prd/velicoach.md](prd/velicoach.md) |
| Velicoach 总体方案（金字塔梳理） | https://claude.ai/artifact/R5P7pEGDRaoym7mEBtLMu4 | [prd/velicoach-strategy.md](prd/velicoach-strategy.md) |
| Velicoach 设计系统 v1.1 | https://claude.ai/artifact/6JqC3pUJ5GjDvXD2sEMZ5w | [uiue/system/](uiue/system/) |
| 动效原型（A / B / C 三个方向，选定 C） | https://claude.ai/artifact/PGihowSLLCHsh3xDx14Dtd | [uiue/prototypes/velicoach-motion.html](uiue/prototypes/velicoach-motion.html) |
| 主站画板 UI v1.1（18 块：首页四种设备、看清、学习路径、文章页、动手、项目页、关于、页面状态、控件样张，和站稳的参考页） | https://claude.ai/artifact/8Nx35n8NXRebQn4aapiW9L | 画板文件、生成脚本和源在 [uiue/prototypes/v1.1/](uiue/prototypes/v1.1/)（怎么重建、验证、发布见那里的 README）；画了什么见 [uiue/coverage.md](uiue/coverage.md) |

## 仓库里的文档

| 目录 | 放什么 | 什么时候读 |
|---|---|---|
| [requirements/](requirements/) | 用户原句（`timeline.md`，按时间，一字不改）、需求追踪（`trace.md`，第 28 条起）、原来博客部分的要求按主题汇总（`summary.md`）、截图 | 拿不准用户本意时；改需求、改设计前 |
| [prd/](prd/) | 主站 PRD 和总体方案的快照；看清的文章部分还没做完的范围（`remaining.md`）；E2E 场景表（`e2e-scenarios.md`，从 PRD 提炼的用户场景，案例按编号对应） | 做任何功能前；写、跑 E2E 案例前 |
| [prd/decisions.md](prd/decisions.md) | 主站 PRD 的决定记录：每次决定的内容、理由、取代了哪条旧决定，最新的在最上面；PRD 只写「现在是什么」 | 想知道一条需求为什么这样定、能不能改时 |
| [prd/changelog.md](prd/changelog.md) | 主站 PRD 的修订记录，和 v1.0 定稿时的对抗评审记录 | 写规格和票、要注明依据哪一版时 |
| [uiue/](uiue/) | 设计系统的链接与副本、设计简报（`brief.md`）、需求到画板的覆盖表（`coverage.md`）、设计决定、评审报告（`reviews/`）、动效原型和画板源（`prototypes/`）；看清一站的定位，以及原来的博客留下和改掉的约定（`identity.md`） | 改界面前；做了新的体验决定后 |
| [architecture/](architecture/) | 技术方案、路由表、ADR | 写代码前；技术选型或结构变化前 |
| [issues/](issues/) | 原来的博客开过的打磨项和状态 | 接着打磨文章部分时 |
| [standards/](standards/) | 流水线：从需求到上线的关口、多 Agent 的角色和循环、两条车道、观察者；复用 Veli 的机制 | 做票、拆票、改协作机制前 |
| [delivery/](delivery/) | 开发团队和开发路线：团队怎么搭（`team-setup.md`）、开发路线（`roadmap.md`）、定时任务的提示词（`loops/`）、上线步骤（`launch-runbook.md`）、经验库（`lessons.md`） | 想知道现在走到哪、下一步做什么；建或改定时任务时；子 Agent 开工前读经验库 |
| [deploy.md](deploy.md) | 上线到 velicoach.com 的分流、订阅库的迁移 | 部署时 |
| [handoff/](handoff/) | 交接文档：一个阶段收尾时的现状、关口进度、遗留问题、等产品负责人决定的事、接手指南；最新一份见 [handoff/README.md](handoff/README.md) | 接手编排的会话开工前；想知道现在卡在哪、等谁时 |

## 相关仓库

| 仓库 | 关系 | 先读 |
|---|---|---|
| `madlouse/thin-muscle-coach` | Veli：站稳一站的产品，管 `/body`、`/app` 等路径；账号服务也在那里 | `AGENTS.md`、`docs/product/PRD.md`、`docs/architecture/adr/0032-velicoach-path-routing.md` |
