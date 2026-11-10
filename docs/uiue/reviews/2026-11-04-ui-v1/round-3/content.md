# 关口三 a 第 3 轮 · 内容评审（画板文字，中英两版）

评审人：content-reviewer（冷评审，没看过制作过程）· 2026-11-04
材料：`canvas2/project/*.dc.html`（标签文字，以及 `renderVals`、`copy()`、`CHROME`、`PAGE`、`CONTENT`、`MILESTONES`、`LEVELS`、`POSTS` 里会渲染到页面上的中英文字）；研究卡数据 `canvas2/data/research.json`；截图 `shots-r3/`（看了 Mind 人机协作、Article 暂无英文版）。
规则：quality-terms C1–C9、T1–T10（T8 按本轮改过的版本）；`docs/GLOSSARY.md`；PRD 快照第 4、5、6 节；`velicoach-content`。
上一轮：`../round-2/content.md`。

## 结论：要改

阻塞 11 条（R1–R11），建议 6 条（S1–S6）。可信度低于 80 的发现没有列出。Controls 是控件状态板，只查了错字，没有发现问题。

上一轮的 23 条：已修 15 条，部分修 5 条，没修 3 条。Shopify 原文这一轮打开了，大部分数字对得上，但有三处和原文不符（R1–R3）。另外两处最重要：步速研究卡把效应大小填进了「证据可信度」一栏，站稳页却说每条都写了证据可信度（R4）；学习路径推荐的 nanoGPT，作者已在 README 里写明过时、请改用 nanochat（R10）。

## 〇、检查命令

在当前工作区（不是 git 仓库，没有另做检出）上运行：

```
> check:terms
> node scripts/check-terms.mjs

docs/uiue/reviews/2026-11-04-ui-v1/round-2/content.md:98: （英文口号第二句）
docs/uiue/reviews/2026-11-04-ui-v1/round-2/reviewer-a.md:114: （同上）
docs/uiue/reviews/2026-11-04-ui-v1/round-2/reviewer-b.md:96: （同上）
docs/uiue/reviews/2026-11-04-ui-v1/round-2/reviewer-b.md:144: （同上）
docs/uiue/system/tokens.json:383: （「里程碑」的旧说法，在 usage 说明里）

5 处用了不再用的说法，改法见 docs/GLOSSARY.md「不再用的说法」。

> check:vague
> node scripts/check-vague.mjs

质量词检查通过：51 个文件，42 个质量词，18 个虚词，50 条规则。
```

`check:terms` 没通过，但 5 处都不在画板里：4 处在第 2 轮的评审报告里（引用了口号原文），1 处在 `tokens.json` 的说明文字里。画板不在这个脚本的扫描范围内，所以我另外用术语表的清单逐个搜了画板，结果见 R7、R8。本报告不写这些词，以免再触发检查。

## 一、上一轮问题的处理情况

| # | 上一轮的问题 | 这一轮 | 说明 |
|---|---|---|---|
| B1 | 文章页数字无法核对、页脚缺作者、引语 | **部分修** | 原文这一轮能打开（见第二节）。引语的 `blockquote` 已去掉，转载与引用说明已补（T5）。作者仍写团队名，原文署名是 Zack Deveau（R1）；另有两处和原文不符（R2、R3） |
| B2 | Body BJSM 10–17% | 已修 | 全站都用 research.json 的一份：−15%，7 项研究、263,058 人，证据可信度很低 |
| B3 | 未上架的 App 下载入口 | 已修 | 二维码和说明都改成「打开 Veli 网页版」，画板里没有商店按钮和「下载」 |
| B4 | 预告睡眠和饮食 | 已修 | 画板里搜不到 |
| B5 | States 英文叫法 | 已修 | 和 Mind 一致：History of AI、Human–AI collaboration、Content lines、Milestones that changed the road |
| B6 | 达特茅斯 1956 | 已修 | States 和 Mind 都是「1955 · McCarthy 等：达特茅斯人工智能提案」 |
| B7 | 暂无英文版的文案和做法 | 已修 | 截图里说明下面直接是中文正文，文案「Our Chinese write-up is below.」和画面一致 |
| B8 | Code Review 归到 Loop 工程 | 已修 | Mind 列表和 Article「接着读」都是 Harness 工程 |
| B9 | 长句、「分区」 | 已修 | 拆成短句；「分区」删掉了。原文确实有 partitions（把仓库切成文件子集），删掉不影响要点 |
| B10 | 列表用原文日期 | **部分修** | Harness 一篇改成 10-31；Dan Koe 一篇仍是原文日期（R11） |
| B11 | 英文标题不一 | 已修 | 两篇文章的英文标题全站一致。但 2025 里程碑的标题在 Main 和 Mind 不一样（R9，同一类问题） |
| B12 | 威利第一次出现没有说明 | **部分修** | Main、States 写了「AI 力量训练教练」「AI 教练」，Body、Build 的说法不同，Body 中文看不出是 AI（R5） |
| B13 | 学习路径缺「为什么学」、前置 | 已修 | 每步有「为什么学」；导语写明「后一级默认你学完了前一级」 |
| N1 | 「四项研究」 | 已修 | 「一份指南、三项综述」 |
| N2 | 「大就是不一样」 | 已修 | 首页最新三篇已不含这条；Mind 写「按可预测的规律变好」 |
| N3 | Codex 无出处、句长 | 已修 | 删了 Codex，拆成两句 |
| N4 | 里程碑缺作者 | **部分修** | 1986、2012、2017、2020 补了作者；2025 仍没有作者（R9） |
| N5 | builder、「带去动手」、Critical | 已修 | builder 进了术语表，Build 第一次出现时有说明；按钮「去动手一站」；「严重」（Critical） |
| N6 | 同一事物多种叫法 | **部分修** | 页脚、aria、阅读时长已统一（中文 12 分钟、英文 9 min，各语言内一致）。「每封信」「letter」和英文免责的三种写法还在（S2、S3） |
| N7 | BJSM 16 和 7 | 已修 | 标签改成「队列研究的系统综述」 |
| N8 | 第一练动作不一、「各三组」、教练审核 | **没修** | 见 S1 |
| N9 | 「AI 走得越快，越要先站稳」 | **没修** | 见 S4 |
| N10 | 学习路径四级和 PRD 不一致 | 已修 | 和 PRD 第 5 节一样：基础、智能体、模型、前沿 |

## 二、事实和出处核对（T1）

查询日期都是 2026-11-04。WebFetch 返回的是工具摘录的原句，下面引号里的英文是它给出的原文句子；两次独立抓取的结果一致。

| 位置 | 画板上的说法 | 核对结果 |
|---|---|---|
| 首页、站稳研究卡 vs research.json | 5 张卡的来源、数字、结论、研究类型、样本量、可信度、链接 | **一字不差**。Main、Tablet、Fold、Mobile 内嵌的 `research()` 与 json 的 `use.Main` 四张逐字段比对相同；Body 的 `studies` 与 `use.Body` 四张相同（`meta` 是 类型 · 样本 · 可信度 三段拼接）。Body 不显示大数字，数字在结论句里 |
| 研究卡 · Cochrane 2009 步速 | 「步速：24 项试验、1,179 人」「+0.08 米/秒」「力量提高幅度大，步速提高幅度小」 | 数字一致。PubMed 19588334：「a modest improvement in gait speed (24 trials, 1179 participants, MD 0.08 m/s…)」「PRT had a large positive effect on muscle strength (73 trials, 3059 participants, SMD 0.84…)」。摘要**没有**证据可信度分级。问题见 R4 |
| 研究卡 · WHO、BJSM、Cochrane 2019、BMJ 2024 | 同上一轮 | 数字与上一轮核对过的原句一致，本轮未改。who.int 和 doi.org/10.1136/bmj-2023-075847 两个链接本轮请求被拒，没打开 |
| Article · Shopify 原文 | 署名、日期、约五个月、30 多个候选、六周、80 多个应用、数千次、300 多个发现、2 个 Critical、超过 40 万美元、Dispatch | 打开了 shopify.engineering/building-an-agentic-harness-that-outlasts-the-model。**一致**：「Published on Jul 29, 2026」；「Over the past five months, we've been evaluating new security-tuned frontier models inside that harness」；「better than our baseline frontier models at discovering findings」「more potential issues that needed to be confirmed」；30 多个候选「every one was downgraded to low or medium, found to be a false positive, or reclassified as defense in depth」；「Dispatch is a thin Ruby client」「runs each scan as an ordered set of stages」；「Over roughly six weeks, we've run thousands of scans, produced over 300 findings」；「two findings would have been rated as Critical according to our severity calculator」；「We conservatively value these findings at over $400,000 in equivalent bug bounty payouts」。**不一致**：署名（R1）、证明不了的发现怎么处理（R2）、80 多个应用的时间范围（R3）。原文没有转载或授权声明，本页按「学习整理，不是译文」处理，符合 PRD 第 6 节来源规则 |
| Mind · 学习路径新步骤 Anthropic Academy | anthropic.skilljar.com；「Claude Code、MCP、Agent Skills 课程」 | **真实**。目录页有「Claude Code 101」「Claude Code in Action」「Introduction to Model Context Protocol」「Model Context Protocol: Advanced Topics」「Introduction to agent skills」 |
| Mind · Karpathy autoresearch | github.com/karpathy/autoresearch；「在一张 GPU 上跑通一晚的实验」 | **真实**。2026 年 3 月 7 日开源，作者 Andrej Karpathy；智能体改训练代码、跑固定 5 分钟的训练、按验证指标保留或丢弃；单张 GPU，一晚约 100 次实验（NYU Shanghai RITS 报道）。仓库页没有直接打开 |
| Mind · nanoGPT | github.com/karpathy/nanoGPT；「用最少的代码走完一次真正的训练」 | 链接真实，但 README：「nanoGPT (this repo) is now very old and deprecated but I will leave it up for posterity.」「It is very likely you meant to use/find nanochat instead.」见 R10 |
| Mind · 其余学习路径链接 | CS50x、ML Specialization、Building effective agents、Agentic AI（已改成 alpha 地址）、Zero to Hero、CS25 | 地址是作者的官方地址；本轮没有逐个打开 |
| Mind · 里程碑作者和年份 | 1950 图灵；1955 McCarthy 等；1986 Rumelhart、Hinton、Williams；2012 Krizhevsky、Sutskever、Hinton；2017 Vaswani 等；2019 萨顿；2020 Kaplan 等；2022、2024 OpenAI；2025 无作者 | 作者和年份都对（与上一轮核对的出处一致；「七十年」对应 Sutton 原文「70 years of AI research」）。2025 条链接的是 Anthropic 的 Claude 3.7 Sonnet 公告（Claude Code 在其中首次发布），标题里没有作者（R9） |
| Mind · Dan Koe | 「如何在一天内彻底改变你的人生」· 2026-01-12 | 标题与原文一致。日期是原文在 X 上的发布日期（仓库 `src/content/dankoe.ts` 的 `date` 与原帖 status id 换算出的时间都是 2026-01-12），见 R11 |

## 三、阻塞项

| # | 画板 · 位置（原文摘录） | 规则 | 为什么 | 改法 | 可信度 |
|---|---|---|---|---|---|
| R1 | Article 元信息「Shopify 应用安全团队」；页脚「原文：《…》，Shopify 应用安全团队，Shopify Engineering，2026 年 7 月 29 日，英文。」；英文「by Shopify Application Security」 | T1「写明作者」、T5；PRD 第 5 节文章必填「作者」 | 原文署名是 Zack Deveau。团队名不是作者 | 元信息「Zack Deveau · Shopify 应用安全团队」；页脚「原文：《Building an agentic harness that outlasts the model》，Zack Deveau，Shopify Engineering，2026 年 7 月 29 日，英文。」英文「by Zack Deveau, Shopify Engineering, July 29, 2026.」正文里「Shopify 应用安全团队」作为主语可以保留（原文用的是「we」） | 92 |
| R2 | Article p4「写扫描的人只需要写一个智能体，专门搜寻某一类缺陷。……不能用真实集成测试证明可被利用的发现，一律不接受。」（英文同） | T1；技能 §5 讲解「忠实原文」 | 原文：证明不了的发现「are either rejected or downgraded to a "Low" or "Medium" rating」，不是一律不接受。原文还写了同时用「generalist」和专门的智能体，「只需要写一个」说过了头 | 「写扫描的人可以很快写出专找某一类缺陷的智能体。……在这些限制下证明不了的发现，要么不接受，要么降成『低』或『中』。」英文「Scan authors can quickly build agents that hunt one category of bug. … Findings that can’t be proven within these limits are rejected or downgraded to Low or Medium.」 | 88 |
| R3 | Article p5「约六周内，扫描覆盖了 80 多个应用，执行了数千次，产出 300 多个发现。」（英文同） | T1 | 原文的六周只对应数千次扫描和 300 多个发现；80 多个应用是另一句「complete scans of over 80 unique applications so far」，是到目前为止的累计数，没有说是六周内 | 「约六周内，扫描执行了数千次，产出 300 多个发现。到目前为止，团队已经完整扫描了 80 多个应用。」英文同改 | 85 |
| R4 | research.json `cochrane-2009-gait`：`certainty`「力量提高幅度大，步速提高幅度小」；Body 导语「下面四条来自系统综述，每条写了研究类型、样本量和证据可信度。」；卡片结论「……力量也明显提高」，样本只写步速的 24 项、1,179 人 | T8（研究类型、样本量、证据可信度；样本量对应卡片上那个结论）；技能「数字能在原文里找到」 | ① 这一栏写的是效应大小，不是证据可信度；这篇 2009 年的摘要没有可信度分级。Body 导语说四条都写了可信度，对这一条不成立。② 结论里「力量也明显提高」对应的是 73 项试验、3,059 人，卡片上没有 | 在 research.json 改一次（全站跟着变）：`certainty`「这篇综述没有给证据可信度分级」/「The review does not grade certainty of evidence」；效应大小并进结论：「步速平均每秒快 0.08 米（幅度小）；力量提高幅度大」；`sample`「步速：24 项试验、1,179 人；力量：73 项试验、3,059 人」。Body 导语改成「每条写了研究类型、样本量，以及原文给出的证据可信度」 | 85 |
| R5 | 威利第一次出现：Main「AI 力量训练教练威利」；States「AI 教练威利」；Body「威利是 Veli 里的力量训练教练」，英文「Veli is a strength coach in an app」；Build「Veli 威利 · 力量训练的教练兼管家」 | 术语表「威利：AI 力量训练教练」、「例外」第一次出现带一句说明；C3 | 四块画板四种说法。Body 是站稳的落地页，中文没写「AI」，读者仍看不出威利是人还是 AI；英文「in an app」也和「上架前只推网页版」对不上 | 统一照术语表：Body「威利是 Veli 的 AI 力量训练教练。它提前排好……」，英文「Veli is an AI strength coach. It plans…」；Build「AI 力量训练教练，也替你打理训练的安排。……」 | 82 |
| R6 | Build 页脚：只有链接和外观、语言，没有免责一行（其余 8 块对外画板都有「威利不是医生」） | PRD 第 6 节质量标准第 2 条「每页写明『威利不是医生』」；C3 | 同一套页脚，只有动手页少了这一行；Build 的项目卡也介绍了威利 | 照其他页加上 `disclaimer`：「威利不是医生。有伤病或疼痛，先停下来，问医生。」英文按 S3 统一后的写法 | 82 |
| R7 | Build「builder 的一周」实例和开发日志：「画板里的『叶与网』为什么没了」「合并前，冷评审抓出 11 处问题」（英文「leaf-and-net animation」「cold review」） | 术语表：叶与网是「设计和工程内部用语（不出现在界面上）」；冷评审是「协作用语（只在文档和票里用）」；C3 | 对外页面用了内部用语，读者看不懂，也没有解释 | 「首页的动画为什么在设计稿里消失了」「合并前，一位没参与制作的评审抓出 11 处问题」；英文「Why the home page animation vanished from the design file」「Before merging, a reviewer who hadn’t seen the work caught 11 problems」。开发日志正文里的「画板」同样改成「设计稿」 | 85 |
| R8 | Mind 人机协作列表的 meta：「原文英文 · 文章 · 3 分钟讲解」，英文「3-min explainer」 | 术语表「3 分钟视频 / 3-minute video」；C3 | Main（「附 3 分钟视频」）和 Article（「播放 3 分钟视频」）用的是术语表的说法，Mind 用了第三种 | 「· 3 分钟视频」「· 3-minute video」 | 85 |
| R9 | 2025 里程碑：Main 最新三篇「智能体走进日常工作」/「Agents join everyday work」；Mind「编程智能体走进日常工作」/「Coding agents join everyday work」；两处都没有作者 | C3（一个东西一个叫法，同 B11）；T1「写明作者」（同 N4） | 同一个里程碑在两块画板上标题不同；其他里程碑都写了作者或机构，这一条没有 | 两处统一成「Anthropic：Claude Code 与编程智能体」/「Anthropic, Claude Code and coding agents」，Main 的列表照抄 Mind | 82 |
| R10 | Mind 学习路径第 3 级「nanoGPT · Andrej Karpathy · 代码 · 用最少的代码走完一次真正的训练。」 | 技能「学习路径步骤」、「知道多少说多少」；PRD 第 5 节第 3 级「nanoGPT、nanochat」 | 作者在 README 里写明 nanoGPT「very old and deprecated」，并说读者要找的很可能是 nanochat。照现在的写法，读者会去学一个作者自己不再推荐的仓库 | 换成 nanochat（github.com/karpathy/nanochat）：「用一套完整但精简的代码，从训练到对话走一遍。」检验：「在自己的数据上跑通一次训练，讲清每一步在做什么。」时间重新估计；如果要保留 nanoGPT，写明「作者已不再维护，作为读代码的入门」 | 82 |
| R11 | Mind 人机协作列表《如何在一天内彻底改变你的人生》「2026-01-12」 | T3；C3（B10 同一类问题） | 列表其余文章用的是我们的发布日期，这一条是原文在 X 上的发布日期，排序会错 | 改成我们发布这篇的日期；原文日期只放在文章页元信息里。顺手核对 Manus、Super-agent、Code Review 三篇的列表日期是不是我们的发布日期（仓库 `src/content` 里 `date` 字段对 Shopify 存的是原文日期，含义不统一） | 80 |

## 四、建议项

| # | 画板 · 位置（原文摘录） | 规则 | 为什么 | 改法 | 可信度 |
|---|---|---|---|---|---|
| S1 | Main 本周一练「深蹲、俯卧撑、臀桥，各三组。」；Body「练什么：先练三个动作」是深蹲、俯卧撑、划船 | T8；技能 §6 数字 | 两页都讲第一次练什么，动作不一样；「各三组」和别处「3 组 × 10 次」写法不一。训练指导的持证教练审核记录，#14 的评论里搜「教练」「coach」没有找到 | 两页用同一组动作；「各 3 组」；上线前把教练审核记录贴到票上（T8） | 82 |
| S2 | Body、Build 订阅说明「每封信底部都能一键退订」，英文「every letter has a one-click unsubscribe link」 | 术语表「订阅：每周日一封邮件」；C3 | 标题写「邮件」，说明写「信」 | 「每封邮件底部都能一键退订。」「every email has a one-click unsubscribe link.」 | 85 |
| S3 | 英文免责三种：Main「Veli is not a doctor. … stop and see a doctor.」；Body「Veli isn’t a doctor. … stop and see one.」；Mind、Article、States「Veli isn’t a doctor. … stop and see a doctor.」 | C3 | 同一句话三种写法 | 全站「Veli isn’t a doctor. If you’re injured or in pain, stop and see a doctor.」 | 85 |
| S4 | Main「为什么是现在 · AI 走得越快，越要先站稳」 | T1；T9 | 上一轮 N9 没改。下面是四条健康证据，没有一条支持「AI 越快越要练」，口号放在证据上方，像是研究得出的结论 | 标题「先站稳：力量训练的四条证据」，口号留在首屏 | 80 |
| S5 | Article 视频条英文「Captions · Transcript」，中文「字幕 · 文字稿 · 旁白用合成音色『晓晓』」 | C7；术语表「3 分钟视频：英文旁白 Andrew」 | 英文页没写旁白，中英两版信息不对等 | 「Captions · Transcript · Narrated by Andrew, a synthetic voice」 | 80 |
| S6 | `check:terms` 不通过（见第〇节） | `AGENTS.project.md` 第 10 条、完成的定义 | 不在画板里，但让仓库检查一直是红的，后面真问题会被淹没 | 评审报告里引用旧说法时改写成描述（例如「英文口号第二句」）；`tokens.json` 的 usage 说明改成「里程碑」。或者让脚本跳过 `docs/uiue/reviews/`，但要先在 `quality-terms.md` 写明为什么 | 85 |

## 五、查过、没有问题的地方

- **全站一致**：两篇文章的中英标题、发布日期（10-31）、阅读时长（中文 12 分钟，英文 9 min）在 Main、Mind、Article 之间一致；订阅标题全站「每周日一封邮件」/「One email every Sunday」（只剩 S2 一处）；登录方式在 Main、Body、Tablet、Fold、Mobile 都是先 Google 后 Apple，第一次登录的说明都是「先确认年龄和数据怎么用，一屏完成」；Tablet、Fold、Mobile 的文案和 Main 逐键比对相同。
- **研究卡**：除 R4 以外，研究类型、样本量、证据可信度齐全，样本量对应结论；BJSM 写明「关联，不是因果」；有「这些是人群研究的平均结果」的说明；没有讲身材的说法。
- **英文体例**：美式拼写；标题 sentence case；列表 serial comma；按英语读者重写（例如「Only the turns: how people worked before, and why they switched after.」）；英文页上没有中文界面文字，「暂无英文版」状态下的中文正文是 PRD 规定的做法。
- **只放正式版**：没有占位符、「示例」「待定」「即将上线」、TODO；还没上线的 App 和睡眠、饮食都不在页面上；States 的「画板说明」在页面框外。人机协作里还没有文章的范式（提示词、上下文、Loop 工程）只显示标题和它解决的问题，没有预告文字。
- **页面状态**：订阅四态、离线、页面不存在、内容加载失败、加载中、文章加载失败（给重试和原文）、视频无法播放（给文字稿）、暂无英文版，都说清发生了什么、接下来能做什么，没有错误码。
- **文章页**：有「我们的判断」（值得读、适合谁、代价）、适用于、最后核对日期、更新记录、纠错入口、练习、转载与引用说明（T3–T7）。

## 六、核对不了的地方（不是发现，上线前补）

- who.int 的 WHO 指南页、doi.org/10.1136/bmj-2023-075847：本轮请求没有获批，没打开；数字以上一轮用同一研究的其他官方页面核对的结果为准。
- autoresearch 仓库页没有直接打开，用报道核对；CS50x、ML Specialization、Building effective agents、Agentic AI、Zero to Hero、CS25 的链接本轮没有逐个打开。
- Shopify 原文是用 WebFetch 抓取的摘录核对的，不是全文逐段对照；p1b、p4 的「真实的集成测试」，原文开头写的是「real tests」，正文另有「Tests must exercise as much of the public stack as possible」，用「集成测试」是否贴切，定稿前由能读全文的人确认。
- 训练指导（Body 的动作、组数和第一练）的持证教练审核记录（S1）。
