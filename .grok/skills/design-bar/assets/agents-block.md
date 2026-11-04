<!-- design-bar:start -->
## 设计工作（design-bar）

设计语言以 Claude Design 的设计系统为唯一来源，链接见 `{{DESIGN_DIR}}/design-system.md`。凡是涉及界面、样式、交互、动效或文案语气的改动：

1. 先读设计系统的 README，再读 `{{TOKENS_PATH}}`。设计系统还没建立时，先用 design-bar 技能（`{{SKILL_PATH}}/SKILL.md`）建立，再做页面。
2. 新功能或打磨旧功能：先在 `{{DESIGN_DIR}}/features/` 下按 `_template.md` 写一份功能简报。产品意图（受众、核心任务、气质）和难以撤回的大改先向用户确认，不要用默认值猜；体验和交互细节以专业判断直接决定，写进 `{{DESIGN_DIR}}/decisions.md` 并在交付时说明理由。
3. 样式只引用 token，不写死颜色、字号、间距、圆角和动效时长。`{{TOKENS_PATH}}` 由设计系统生成，不手改：需要新 token 时先改设计系统，再运行 `python {{SKILL_PATH}}/scripts/sync_tokens.py <tokens.json> --out {{TOKENS_PATH}}`。
4. 交付前运行检查，报告放进 `{{DESIGN_DIR}}/reviews/<日期-主题>/`：
   - `python {{SKILL_PATH}}/scripts/check_page.py <页面路径或 URL> --out {{DESIGN_DIR}}/reviews/<日期-主题>`
   - `python {{SKILL_PATH}}/scripts/lint_tokens.py <源码目录> --tokens {{TOKENS_PATH}}`
   - 改了画板：`python {{SKILL_PATH}}/scripts/verify_canvas.py <画板目录> --out {{DESIGN_DIR}}/reviews/<日期-主题> --themes light,dark,pseudo`，修到结论为 done
   - 项目里有 unslop 技能时，按它的信号清单（`references/signs.md`）过一遍，结果写进同一份报告；和设计系统冲突时以设计系统为准
   - 改了需求或说法：`coverage.py`（还没画的功能，覆盖表 `{{DESIGN_DIR}}/coverage.md`）和 `stale_terms.py`（旧说法，词汇表 `{{DESIGN_DIR}}/glossary.md`）
5. 一条修改意见代表一类问题：找出背后的原则，改完所有同类位置，写回设计系统（规则或 token）或检查阈值，并在 `{{DESIGN_DIR}}/decisions.md` 记一笔。
6. 产品决定影响界面时，同一轮改完设计系统、画板和需求文档的验收，旧说法记进词汇表。
7. 不留下探索用的临时代码、未使用的样式和组件变体。
<!-- 这一块由 design-bar 的 init_project.py 维护，重新运行会覆盖；项目自己的补充写在块外。 -->
<!-- design-bar:end -->
