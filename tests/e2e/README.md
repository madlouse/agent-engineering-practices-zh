# 端到端测试（主站）

用真实浏览器像用户一样操作主站，证明它照 PRD 工作。规范在生态手册 `velicoach-mono/verify/`（唯一来源）；这里是主站的第一版：只做 Web，不登录（v1 主站不读登录状态）。

| 目录和文件 | 管什么 |
|---|---|
| `docs/prd/e2e-scenarios.md` | 场景表：从主站 PRD 提炼的用户场景 S01–S20，每行写明出自 PRD 哪一节、触发、期望、边界、验收标准 |
| `env.ts`、`core/target.ts`、`core/doctor.ts` | 环境：被测站点、证据目录、跑前体检；缺什么就跳过并说明原因 |
| `core/web.ts`、`core/scenario.ts` | Web 驱动：`open`、`tap`、`sees`、`notSees`、`path`、`navLinks`、`isDark` 等用户语言的操作；`tap`、`canTap` 可以限定在导航或正文里点，`onFirstScreen` 判断不滚动就看得到点得到；失败自动截图；第三方请求一律拦掉，案例只验主站自己的行为 |
| `core/coverage.ts`、`core/report.ts` | 运行时覆盖率：浏览器里主站自己构建出的脚本（`/assets/*.js`）被走到的比例，V8 覆盖率按字节算 |
| `cases/*.test.ts` | 案例：一个场景一个文件，标题以场景编号开头，比如 `scenario("S08 切换语言：…")` |

能力模块（`core/`、`env.ts`）管怎么跑，案例（`cases/`）管验什么。改案例、改能力模块、改源码分开提 PR（`scripts/check-role-paths.mjs`）；跑 E2E 的人只报问题，不改这三类文件。案例里不写选择器和固定等待，按可访问的名称、文字和路由找元素；找不到元素说明产品的可访问性有问题，不在驱动里绕。

## 怎么跑

被测站点是任何一个能打开的主站地址：本地构建产物的预览、集成环境（`feature/v1` 的预览部署）或线上。不需要任何密钥。

```bash
npm install
npx playwright install chromium
node scripts/with-app-env.mjs vite build
node scripts/with-app-env.mjs vite preview &
export E2E_BASE_URL=http://127.0.0.1:8081
npm run e2e:doctor
npm run test:e2e
npm run e2e:coverage
node scripts/check-e2e-trace.mjs
```

| 命令 | 作用 |
|---|---|
| `npm run e2e:doctor` | 只读体检：浏览器、站点、首页是网页；不过就是环境问题，不算案例失败 |
| `npm run test:e2e` | 跑全部案例；截图和覆盖率写到 `E2E_ARTIFACTS`（默认系统临时目录 `velicoach-e2e/<运行编号>`） |
| `npm run e2e:coverage` | 汇总最近一次运行的覆盖率 |
| `node scripts/check-e2e-trace.mjs` | PRD 场景有几条有案例、还缺哪几条 |

| 变量 | 作用 |
|---|---|
| `E2E_BASE_URL` | 被测站点；没设置时所有案例跳过并写明原因 |
| `E2E_BYPASS` | 预览部署开了登录保护时的自动化绕过密钥；只放环境变量或 `.env.e2e`（不提交） |
| `E2E_ARTIFACTS`、`E2E_RUN_ID` | 证据和覆盖率放哪、这次运行叫什么；不设时同一次 `npm run test:e2e` 的所有案例共用一个运行目录 |

没有安装 Chromium 时案例同样跳过，并写明「没有安装 Playwright 的 Chromium」，不算通过。

## 覆盖率

现在按字节算浏览器端第一方脚本，先报数、不设门槛（`minCoverage` 是 0）。要换算到源码文件，集成环境的构建得带浏览器 source map；服务端另开 `NODE_V8_COVERAGE`，两项都还没做。有了第一份基线以后，把门槛写进 `.velicoach-checks.json`，只升不降。

## 案例先于实现

主站的页面还在按里程碑实现（`docs/delivery/roadmap.md`）。案例对着 PRD 写，实现还没到的页面，案例会失败：失败说明产品还没做到 PRD，不是案例错了。跑 E2E 的人把失败写成报告交给写代码的 Agent，不改案例去迁就现状；认为案例和 PRD 对不上，先对照 PRD 单独提一个只改案例的 PR。

## 还没做

- 登录相关的场景：v1 没有登录入口，v2 补。
- App 验收：主站没有原生 App；PWA 的安装、离线、推送案例以后加。
- 订阅（S15、S16）、RSS 与给智能体读的版本（S19）、搜索引擎与站点地图（S20）等场景，案例待补，见 `node scripts/check-e2e-trace.mjs` 列出的编号。
