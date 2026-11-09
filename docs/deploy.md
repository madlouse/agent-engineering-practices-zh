# 部署到 velicoach.com

本仓库是 velicoach.com 主站。velicoach.com 按路径分给两个 Vercel 项目：主站（本仓库）和 Veli（`madlouse/thin-muscle-coach`）。路由表见 [architecture/overview.md](architecture/overview.md)，出处是 Veli 仓库的 ADR-0032。

## 主站上线前

- `velicoach.com/` 临时 307 跳到 Veli 的 `/body`（Veli 仓库已经配置）。
- 本仓库可以先部署到 Vercel 的预览地址，用来验收页面。

## 主站上线时

1. 本项目的 Vercel 配置用 rewrites 把归 Veli 的路径（路由表 Veli 两行，含 `/_next/*` 和 Veli 根目录的静态文件）反向代理到 Veli 的生产部署，其余由本项目处理；先在本项目的预览域名上逐条验证（#62），再把 `velicoach.com` 挂到本项目上（ADR-0003 (c)）。
2. 把 `/` 从临时跳转改成主站首页（Veli 侧在 thin-muscle-coach#213 去掉它的临时跳转）。
3. 看清的文章地址是 `velicoach.com/mind/<slug>`。

上线的顺序、谁做、切换后的核对和回退：[delivery/launch-runbook.md](delivery/launch-runbook.md)。

## 数据库迁移

订阅库的迁移不在构建里跑。迁移文件在 `migrations/site/`，只由 GitHub Actions 工作流 `site-db-migrate` 用 `SITE_DB_MIGRATE_URL` 执行（ADR-0004 (a)）：上线前手动触发、分支选 `feature/v1`；上线后合并进 `site` 时自动执行。Vercel 项目的构建命令是 `tsc --noEmit && eslint . && vite build`。

## 原来的 with.velicoach.com

不再作为站点地址。如果这个子域名已经有人用过，在 Cloudflare 的 DNS 和 Vercel 上把它设成永久跳转（301，PRD F27）到 `velicoach.com/mind`，文章路径一一对应。DNS 要由域名持有人改，这个仓库改不了。

## 代码里已经准备的

`vercel.json` 只指定了安装命令。站点没有写死主机名。
