---
title: "构建比模型更持久的 Agentic Harness"
author: "Shopify Application Security 团队"
date: "2026-07-29"
source: "https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model"
official_chinese: false
copyright: "Shopify"
language: "zh"
---

# 构建比模型更持久的 Agentic Harness

*来源：https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model（中文整理）*

Shopify 应用安全团队构建了 agentic 代码审查与测试预言（test oracle）harness，用于发现漏洞、用真实集成测试证明可利用性，并提供 Shopify 调优的修复建议。

## 核心观点

模型会不断变强，但 **harness 才是持久资产**。

在一次审计中，模型提出 30+ 个候选漏洞，经过验证后全部被降级、判定为误报或重新分类为纵深防御。

## 编排流程（Dispatch）

内部 harness 编排器 Dispatch（轻量 Ruby 客户端）将扫描抽象为有序阶段：

- Test bootstrap
- Architecture documentation
- File cataloging
- Partitioning
- Hunting
- Verification（对抗性检查）
- Post-processing
- Reporting
- Remediation

关键：只有能用真实集成测试证明可利用性的发现才被接受。

## 成果

约 6 周内，对 80+ 应用（包括 Shopify Core 单体）进行数千次扫描，产出 300+ 发现，保守估值超过 40 万美元等值赏金。

## 相关实践

- **River**：Slack 原生 Agent，约 1/8 的合并 PR 由其共同撰写。
- **Roast**：开源工作流框架，确定性步骤与 AI 步骤交错，支持会话重放。
- **Remote Dev**：远程 Mac 机群，让 Agent 可并行构建与测试移动端。

*完整原文请访问 Shopify Engineering 博客。本整理仅供学习分享。*
