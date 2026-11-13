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

`vercel.json` 只指定了安装命令。站点没有写死主机名。

## 服务邮箱

velicoach.com 的服务邮箱用 Cloudflare 邮件路由（Email Routing），三个地址都转到产品负责人已验证的同一个收件地址，以后由 Agent 维护（需求第 105 条）。全收规则（catch-all）关闭，发到其他地址的邮件不收。

| 地址 | 用途 |
|---|---|
| hello@velicoach.com | 联系邮箱：关于页 `#contact`、页脚「联系」、文章页的纠错入口（F16）、退订链接失效时的出路、订阅者要求删除数据、权利人通知（#21） |
| privacy@velicoach.com | 隐私和法务页里的联系地址 |
| billing@velicoach.com | 订阅收费的联系地址 |

转发目标和规则只在 Cloudflare 控制台改，目标地址不写进仓库。只能收信，不能用这些地址发信；订阅邮件的发信域名另配（#41）。

