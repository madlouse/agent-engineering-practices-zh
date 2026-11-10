# 上线步骤：feature/v1 → site → velicoach.com

> 关口三 b 第二轮冷审 P1-3。上线票是 #66（`ready-for-human`，主会话 + 产品负责人）。关口四的检查清单在 `docs/standards/pipeline.md` §2.3，分「合并前」「切换后」两段；本页写顺序和谁做。

**主站上线不早于 Veli B1 上线（thin-muscle-coach#72）。** Veli 的生产分支是 `main`，B1 的票（含 #185、#101）只合并进 `feature/b1`，#72 合并后才到 Veli 生产；主站的 rewrites 代理的是 Veli 生产。产品负责人 2026-11-09 定：主站和 Veli B1 一起上线，不把 #185、#101 单独紧急发布。
> 回退的做法也在本页；`docs/deploy.md` 只放部署的说明和指向这里的链接。

## 谁做什么

| 角色 | 做的事 |
|---|---|
| 产品负责人 | 关口四「合并前」的确认；把 `feature/v1` 合并进 `site`（`site` 上线前只接受这一次合并，`pipeline.md` §5.1）；真机、真实邮件、RSS 阅读器、告警邮件这几项人工核对 |
| 主会话 | 手动触发两个工作流；跑核对脚本；用 Vercel 的接口挪域名、改监控目标；贴结果；判断要不要回退 |
| Veli 的主会话 | 按 thin-muscle-coach#213 准备切换 PR（base 是 Veli 的 `main`），由产品负责人在「切换」一步合并 |

## 开始之前（一次性）

0. **工作流已就位**：主会话的 `chore/` PR 已把 `site-db-migrate`、`site-monitor`、`site-audit` 三个工作流文件放进默认分支 `feature/v1`（手动触发执行的是所选分支上的文件）。工作流文件只由主会话改。

## 合并前（在 `feature/v1` 的预览上）

1. **首次生产迁移**：先核对 Environment `site-db` 的部署分支只允许 `site`、`feature/v1`，密钥 `SITE_DB_MIGRATE_URL` 已配（#40）；核对前不触发。然后主会话手动触发 `site-db-migrate`（`ref=feature/v1`），再做 #67 的核对。不过就停在这里修。
2. **监控演练**：主会话手动触发 `site-monitor`（`ref=feature/v1`），`target` 填一个必定失败的地址，连跑两次，开出一个告警 issue；产品负责人回复收到告警邮件；关掉这个 issue。
3. **关口四「合并前」清单**全部通过（`pipeline.md` §2.3）。
4. **Veli 侧就绪**：thin-muscle-coach#72 已合并，Veli 生产上 `/body`、`/en/body`、法务页返回 200（直接请求 Veli 项目的生产域名）；#185、#101 已关；#213 的切换 PR 已开、以 Veli 的 `main` 为 base、评审通过、还没合并。
5. 产品负责人在 #66 回复「确认上线」。

## 合并

6. 产品负责人在 GitHub 上把 `feature/v1` 合并进 `site`（合并脚本只合并进集成分支，不做这一步，`pipeline.md` §5.1）。
7. 主站生产部署 READY；`site-db-migrate` 用 `ref=site` 再跑一次（没有新迁移时什么也不改），#67 的查询再跑一次。
8. Supabase 项目没有处于暂停状态（`/api/site/health` 返回 200）。
9. 主会话用 #62 的核对脚本对**主站项目的生产域名**（`*.vercel.app`，不是某一次部署的生成地址）跑一遍：路由表每一行、`/api/site/health`。全过以后，主会话把仓库变量 `MONITOR_TARGET` 设成这个生产域名，再进下一步。在这之前不设：上线合并前生产部署没有 `/api/site/health`，提前设会误报并开告警 issue。

## 切换

10. 主会话用 Vercel 的接口把 `velicoach.com` 从 Veli 项目移除、挂到主站项目；同时产品负责人把 #213 的切换 PR 合并进 Veli 的 `main`，Veli 生产部署 READY。
11. 主会话把仓库变量 `MONITOR_TARGET` 从主站项目的生产域名（第 9 步设的）改成 `https://velicoach.com`。

## 切换后（60 分钟内做完）

12. 主会话用核对脚本对 `velicoach.com` 跑一遍路由表每一行；迁入的 5 篇文章 `/mind/<slug>` 和它们的中英旁白都返回 200（#32 的清单）。
13. Playwright 经 `velicoach.com` 打开 `/`、`/body`、`/en/body`、`/app`：页面发出的请求里 4xx、5xx 为 0；首页「为什么是肌肉」和 /body 的研究卡锚点都在（#54 的生产核对）。
14. `pipeline.md` §2.3「切换后」清单逐项做完，结果贴 #66。
15. 任何一项不过：按下面的回退步骤恢复，在 #66 写明哪一项、原因、下一次上线前要改什么。

## 回退（5 分钟内）

1. Vercel：把 `velicoach.com` 从主站项目移除、挂回 Veli 项目。
2. Veli：产品负责人在 Veli 的 `main` 上 revert #213 的切换 PR（恢复 `/` 到 `/body` 的临时跳转和 Veli 自己的 robots.txt），Veli 生产部署 READY。
3. `MONITOR_TARGET` 改回主站项目的生产域名。
4. `site` 上的主站代码不用回退：没有域名指向它，访客看不到。订阅库里已经写进的订阅照常保留。

## 上线后（当天）

16. 切换后的清单全过以后，主会话把 GitHub 默认分支改回 `site`，删掉 `feature/v1`；合并脚本读到 `feature/v1` 404 就只合并进 `site`（`pipeline.md` §5）。开着的 PR 把 base 改成 `site`。工作流文件已随上线合并进了 `site`，确认定时运行改在 `site` 上触发。
