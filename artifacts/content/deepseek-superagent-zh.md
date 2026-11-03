---
title: "DeepSeek Super-agent 设计探索：迈向更自主的 Agent 系统"
author: "DeepSeek Harness 团队"
date: "2026-10-31"
source: "https://github.com/deepseek-ai/dsh-superagent-prototype"
official_chinese: true
copyright: "DeepSeek"
language: "zh"
---

# DeepSeek Super-agent 设计探索

*来源：DeepSeek Harness 团队公开设计文档 + dsh-superagent-prototype（MIT）*

一个人通常只能同时跟进 3–5 个活跃会话。模型能力已不再是瓶颈，**人类注意力**成为下一阶段的约束。

Super-agent 的四个特征：

- **连续**：跨 IM、GitHub 等渠道，感觉始终是同一个 Agent。
- **高效**：可并行处理多个复杂任务。
- **主动**：持续观察环境事件，值得处理时主动推进。
- **持久**：始终在线，异常可恢复。

## 两层架构

- **Router 层**（常驻）：处理所有人类交互、全局协调、跨任务记忆与分派。
- **Worker 层**（隔离）：每个任务独立会话与目录，并行执行，上下文不污染。

后续消息通过**订阅直通**直接送达对应 Worker，不再全部经过 Router。

## 其他关键设计

- 事件驱动（Trigger → Thread → Ticket）
- 工单（Ticket）作为工作与授权的基本单位
- 外部 Watchdog 监控活性与进度
- 存算分离，支持恢复

开源原型：https://github.com/deepseek-ai/dsh-superagent-prototype  
（研究原型，非正式产品）

初步实验：Super-agent p50 完成时间约 12.4 分钟，p95 约 15.7 分钟；单会话 + Subagent 基线 p95 达 29.5 分钟。

*原文有中文版本。本站收录要点，完整内容请参考官方公开文档与仓库。*
