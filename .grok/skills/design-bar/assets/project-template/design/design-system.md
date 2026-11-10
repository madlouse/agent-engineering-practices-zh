# 设计系统

状态：未建立

本项目的设计语言以 Claude Design 的设计系统为唯一来源。建立后在这里填写：

| 项目 | 内容 |
|---|---|
| 设计系统 | （链接） |
| 代码里的 token | （tokens.css 的路径，由 `sync_tokens.py` 生成，不手改） |
| 最近一次同步 | （日期） |
| 关键界面画布 | （Design 画布链接，可以有多个） |

## 怎么用

1. 先读设计系统的 README，再读代码里的 tokens.css。
2. 需要新 token 或改规则：先改设计系统，再运行 `sync_tokens.py` 同步到代码。
3. 交付前运行 `check_page.py` 和 `lint_tokens.py`，报告放进 `reviews/`。
