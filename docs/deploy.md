# 部署到 velicoach.com

本仓库是 velicoach.com 主站。velicoach.com 按路径分给两个 Vercel 项目：主站（本仓库）和 Veli（`madlouse/thin-muscle-coach`）。路由表见 [architecture/overview.md](architecture/overview.md)，出处是 Veli 仓库的 ADR-0032。

## 主站上线前

- `velicoach.com/` 临时 307 跳到 Veli 的 `/body`（Veli 仓库已经配置）。
- 本仓库可以先部署到 Vercel 的预览地址，用来验收页面。

## 主站上线时

1. 在 Vercel 上把本项目接到 `velicoach.com`，按路径分流：`/body`、`/app`、`/pricing`、`/legal/*`、`/data-usage`、`/auth/*`、`/api/*`、`/manual/*` 交给 Veli，其余交给本项目。用 Vercel 的 microfrontends 还是 rewrites，实现时选定，写进 ADR。
2. 把 `/` 从临时跳转改成主站首页。
3. 看清的文章地址是 `velicoach.com/mind/<slug>`。

## 原来的 with.velicoach.com

不再作为站点地址。如果这个子域名已经有人用过，在 Cloudflare 的 DNS 和 Vercel 上把它设成永久跳转（308）到 `velicoach.com/mind`，文章路径一一对应。DNS 要由域名持有人改，这个仓库改不了。

## 代码里已经准备的

`vercel.json` 只指定了安装命令。站点没有写死主机名。
