# 文档地图

先读 [GLOSSARY.md](GLOSSARY.md)（术语），再按任务进入下面的模块。同一件事只在一个地方写，其他地方链接过去。

## 在线文档（唯一来源）

主站的需求和设计语言在 Claude 的在线文档里编辑；仓库里放的是快照，供 agent 离线读取。改的时候先改在线文档，再更新快照。

| 文档 | 在线地址 | 仓库快照 |
|---|---|---|
| Velicoach 主站 PRD v1.0 | https://claude.ai/artifact/DCjVTmTknxzkLpjHgrho8R | [prd/velicoach.md](prd/velicoach.md) |
| Velicoach 总体方案（金字塔梳理） | https://claude.ai/artifact/R5P7pEGDRaoym7mEBtLMu4 | [prd/velicoach-strategy.md](prd/velicoach-strategy.md) |
| Velicoach 设计系统 | https://claude.ai/artifact/6JqC3pUJ5GjDvXD2sEMZ5w | [uiue/system/](uiue/system/) |
| 动效原型（A / B / C 三个方向，选定 C） | https://claude.ai/artifact/PGihowSLLCHsh3xDx14Dtd | [uiue/prototypes/velicoach-motion.html](uiue/prototypes/velicoach-motion.html) |
| 早期探索画布 v0.3（只作参考，「01 站稳」画板有原地展开的示范） | https://claude.ai/artifact/8Nx35n8NXRebQn4aapiW9L | — |

## 仓库里的文档

| 目录 | 放什么 | 什么时候读 |
|---|---|---|
| [requirements/](requirements/) | 用户原句（`timeline.md`，按时间，一字不改）、需求追踪（`trace.md`，第 28 条起）、原同席博客部分的主题汇总（`summary.md`）、截图 | 拿不准用户本意时；改需求、改设计前 |
| [prd/](prd/) | 主站 PRD 和总体方案的快照；看清的文章部分还没做完的范围（`remaining.md`） | 做任何功能前 |
| [uiue/](uiue/) | 设计系统的链接与副本、设计决定、动效原型；看清一站的定位，以及原同席博客留下和改掉的约定（`identity.md`） | 改界面前；做了新的体验决定后 |
| [architecture/](architecture/) | 技术方案、路由表、ADR | 写代码前；技术选型或结构变化前 |
| [issues/](issues/) | 原同席博客开过的打磨项和状态 | 接着打磨文章部分时 |
| [deploy.md](deploy.md) | 上线到 velicoach.com 的分流，`with.velicoach.com` 的跳转 | 部署时 |

## 相关仓库

| 仓库 | 关系 | 先读 |
|---|---|---|
| `madlouse/thin-muscle-coach` | Veli：站稳一站的产品，管 `/body`、`/app` 等路径；账号服务也在那里 | `AGENTS.md`、`docs/product/PRD.md`、`docs/architecture/adr/0032-velicoach-path-routing.md` |
