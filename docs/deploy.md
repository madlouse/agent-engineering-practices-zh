# 部署到 velicoach.com

本仓库是 velicoach.com 主站。velicoach.com 按路径分给两个 Vercel 项目：主站（本仓库）和 Veli（`madlouse/thin-muscle-coach`）。路由表见 [architecture/overview.md](architecture/overview.md)，出处是 Veli 仓库的 ADR-0032。

## 主站上线前

- `velicoach.com/` 临时 307 跳到 Veli 的 `/body`（Veli 仓库已经配置）。
- 本仓库可以先部署到 Vercel 的预览地址，用来验收页面。

## 主站上线时

1. 本项目的 Vercel 配置用 rewrites 把归 Veli 的路径（路由表 Veli 两行，含 `/_next/*` 和 Veli 根目录的静态文件）反向代理到 Veli 项目的生产域名（`*.vercel.app`），其余由本项目处理；先在本项目的预览域名上逐条验证（#62），再把 `velicoach.com` 挂到本项目上（ADR-0003 (c)）。
2. 把 `/` 从临时跳转改成主站首页（Veli 侧在 thin-muscle-coach#213 去掉它的临时跳转）。
3. 看清的文章地址是 `velicoach.com/mind/<slug>`。

上线的顺序、谁做、切换后的核对和回退：[delivery/launch-runbook.md](delivery/launch-runbook.md)。

## 数据库迁移

订阅库的迁移不在构建里跑。迁移文件在 `migrations/site/`，只由 GitHub Actions 工作流 `site-db-migrate` 用 `SITE_DB_MIGRATE_URL` 执行（ADR-0004 (a)）：上线前手动触发、分支选 `feature/v1`；上线后改了 `migrations/site/**` 的提交进 `site` 时自动执行。自动执行和 Vercel 的生产构建同时开始，新代码可能比迁移先上线，所以迁移必须向后兼容（先加后删，ADR-0004「迁移约定」）；做不到兼容的，先单独合并只含迁移的 PR。工作流文件只由主会话维护。Vercel 项目的构建命令是 `tsc --noEmit && eslint . && vite build`。

## 代码里已经准备的

`vercel.json` 指定了安装命令和 `ignoreCommand`。站点没有写死主机名。

**只改文档的提交不出预览部署**（2026-11-13 主频道定：免费额度一天 100 次，连着挡了 #137、#140、#145 的预览）。`ignoreCommand` 跑 `scripts/preview-skip.mjs`：从这个分支上次部署的提交（`VERCEL_GIT_PREVIOUS_SHA`）到当前提交，改到的文件都是文档，就跳过构建；有一个不是就照常构建。文档指 `docs/`、`.grok/skills/`、`.grok/references/`、`.claude/skills/`、`.claude/agents/`、`attachments/`、`screenshots/` 下的文件和根目录的 `.md`，但不含 eslint 会查的脚本（`.js`、`.mjs`、`.ts` 这类；`docs/uiue/prototypes/` 下的 eslint 不查，算文档）。`.grok/app-env.json` 不算文档：`with-app-env.mjs` 把它并进构建环境。比较时关掉改名检测、按原始字节读路径，把代码挪进文档目录或中文文件名都不会判错。三种情况总是构建：`site` 和 `feature/v1` 两个分支（集成分支变绿要最新提交的预览 READY，生产要每次部署）；分支还没有成功的部署；克隆里找不到上次部署的那个提交。`scripts/preview-skip.mjs` 和 `vercel.json` 是门槛文件（`merge-gates.mjs` 的 `GATE_FILES`），票改不了。合并脚本怎么对待没有预览的提交，见 `docs/standards/pipeline.md` §5.1。
