---
title: "Claude Code 团队如何做 Code Review"
author: "Addy Osmani, Morgan Westlee Lunt, Qing Wang"
date: "2026-10-15"
source: "https://claude.dev/blog/solving-code-review-at-anthropic/"
official_chinese: false
copyright: "Anthropic / Claude"
language: "zh"
---

# Claude Code 团队如何做 Code Review

*来源：https://claude.dev/blog/solving-code-review-at-anthropic/（信达雅中文整理）*

Claude 已撰写 Claude Code 约 90% 的代码。从 6 月到 9 月，合并的 PR 数量翻倍以上，而需要回滚的比例下降超过 40%。

团队没有取消审查，而是把大部分阅读工作交给机器，优化人类时间和注意力，并大力投资于快速、容易撤销错误的能力。

## 核心转变

- 审查从“终点门”变成“持续过程”，更像写代码时的拼写检查。
- 大多数变更在人类查看前，已被 Claude 至少审查并修复过一次。
- 目标：大多数 PR 最多只需要一个人类在环（可以是作者本人），同时不增加回滚或事故率。

## 多层审查体系

1. **PR 前验证**：Agent 运行测试、构建、截图对比；子 agent 用新鲜上下文审查 diff。使用 `CLAUDE.md` 和 `REVIEW.md`。
2. **每个 PR 的 AI Review**：Claude 对照整个仓库和 PR 意图审查。多 agent 并行找问题，再投票验证，只发布实质性发现（Important / Nit / Pre-existing）。
3. **安全审查**：可阻断合并。发现未解决则不能合并。
4. **自动化检查**：lint、类型检查、跨平台测试、构建。
5. **风险分层的人类审批**：
   - Low：文档、文案、flag 后的加法变更 → 自动化通过后无需人类审批。
   - Medium：普通产品变更 → 1 人。
   - High：敏感代码 → 2 人。
6. **合并队列 + 渐进发布**：主分支重新运行检查；新功能先对内部用户开放。
7. **快速检测与回滚**：flag 可瞬间关闭；on-call + 仪表盘。

## 关键实践

- 发现必须被回应：修复或带理由关闭线程。
- 将事故转化为每日评估集，持续改进审查器。
- 过滤风格/诊断类噪音，聚焦真实 bug。
- “你落地它，你就拥有它”：作者对后续问题负责。

*完整原文请访问官方链接。本整理仅供学习分享，版权归 Anthropic 所有。*
