# 交付：开发团队和开发路线

主站怎么从需求做到上线、由哪些 Agent 来做。规则在 `docs/standards/`，这里放怎么搭、怎么走、怎么跑。

| 文件 | 回答什么 |
|---|---|
| [../standards/pipeline.md](../standards/pipeline.md) | 机制：四个关口、角色和交接物、四个循环、两条车道、分支和标签、复用 Veli 的方式（唯一来源） |
| [../standards/observer.md](../standards/observer.md) | 观察者：从外面看整条流水线，怎么判断机制要收紧还是简化 |
| [team-setup.md](team-setup.md) | 开发团队怎么搭起来：准备、建定时任务、试跑、先慢后快、日常怎么用 |
| [roadmap.md](roadmap.md) | 开发路线：现在在哪个关口，站点车道的里程碑，内容车道的阶段，两条车道在哪里交汇 |
| [polish-status-2026-11-13.md](polish-status-2026-11-13.md) | PRD 和 UI/UX 打磨到 2026-11-13 的现状：每块已定什么、缺什么、哪些在打转、哪些该停；收敛路线图的依据，记录当时的情况，不随进度改 |
| [launch-runbook.md](launch-runbook.md) | 上线那一天：合并 `feature/v1` → `site`、切换 `velicoach.com` 的顺序、谁做、切换后的核对和回退 |
| [loops/](loops/) | 四个定时任务的提示词和配置 |
| [lessons.md](lessons.md) | 经验库：踩过的坑、落成了什么检查 |
| [gate-3b-split.md](gate-3b-split.md) | 关口三 b：PRD 拆成了哪些规格和票、为什么这样拆 |

子 Agent 的定义在仓库根目录的 `.claude/agents/`；技能在 `.grok/skills/`（`.claude/skills/` 里是指向它们的链接）。
