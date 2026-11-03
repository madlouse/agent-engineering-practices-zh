# with.velicoach.com

站点代码可以放到 Vercel，也可以放到 Cloudflare。域名记录要等 `velicoach.com` 的持有人自己改。这个仓库改不了 DNS。

## 要改的记录

在 `velicoach.com` 的 DNS 里加一条：

| 主机 | 类型 | 值 |
| --- | --- | --- |
| `with` | CNAME | 部署平台给这个项目的主机名 |

用 Vercel 时，值通常是 `cname.vercel-dns.com`。用 Cloudflare 时，值是那个项目的 `*.pages.dev` 主机名。以平台当时显示的为准，不要猜。

加好之后，在平台里把 `with.velicoach.com` 填成这个项目的域名，并等证书签发。

## 代码里已经准备的

`vercel.json` 只指定了安装命令。站点没有写死主机名，所以同一个构建可以用在 `with.velicoach.com`。
