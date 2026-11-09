# 人与 Agent 友好的设计：AUI 与 AX

调研日期 2026-11-05。分两半：AUI 讲人怎么用 Agent 做事；AX 讲 Agent 怎么用我们的网站和产品。每节先写结论。引用原文不超过 15 个字，其余是转述。

## 0. 结论

1. **人和 Agent 读的是同一份结构。** 浏览器 Agent 先读无障碍树，看不清再截图（Claude 浏览器工具文档、web.dev、Google 搜索的 AI 指南）。所以对 Agent 友好，八成工作就是把无障碍、语义 HTML、稳定版面和稳定地址做对。这些我们的 PRD 大多已经要求，按人的标准做到，Agent 也就能用。
2. **确认要按后果分级，不能每步都确认。** Anthropic 的实测数据建议不要强制逐步批准，重点是人随时看得见、插得进手。苹果、OpenAI、Anthropic 的浏览器 Agent 只在不可逆或有外部后果的动作前确认。这和我们「能撤回的用撤销，不弹确定吗」是同一条规则，也和 Veli 的 A/S/B/C/D 自主等级一致。
3. **给机器的新文件和新协议大多还在提案阶段。** llms.txt 是提案，Google 搜索不读它；WebMCP 是社区组草案，只在 Chrome 149 的源试用里有，API 名字也改过一次；IETF 的 Agent 签名还是草案。这些便宜的可以顺手做，但不能把它们当成增长手段，也不该为它们改架构。
4. **我们最该补的一件事：主要状态写进地址。** 先修语言：现在的代码用 React 状态切语言，不改地址，`<html lang>` 也写死成 `zh-CN`。这条对人（分享、收藏、搜索的语言版本）和 Agent（直达、复现）都有用，PRD 已经要求 `/en/`，所以不需要新的产品决定。

来源分级：一手 = 标准文本、官方文档、论文、作者本人的原文。没读到原文、只用了二手报道的，在表里标「二手」。读取失败的：OpenAI 帮助中心的 ChatGPT agent 页面（请求失败，改用 OpenAI 发布原文）；PAIR Guidebook 的模式页靠脚本渲染，抓不到全文（改用 Google 官方 codelab 和 PAIR 团队的博客）。

---

## 第一部分 AUI：人怎么用 Agent 做事

### 1.1 结论

AUI 的老规矩（2019 年微软 18 条、Google PAIR）放在今天仍然成立，变的是重心：从「这个 AI 功能准不准」，转到「我交出去的这件事，我看得见、拦得住、撤得回吗」。可以检查的规则集中在四处：**AI 内容有标识、动作按后果分级确认、长任务的进度写在外部、生成的界面只用受信组件拼。** 「AI 是第三种交互范式」是 Nielsen 2023 年的观点文章，方向对，但不是实证研究。他自己的结论也是意图输入和图形控件要混用，不能只剩一个对话框。

### 1.2 来源要点

| 来源 | 讲了什么（转述） | 链接 |
|---|---|---|
| Amershi 等，CHI 2019，微软 | 18 条分四个时段：开始时（说清能做什么、多常出错）；交互中（时机、相关上下文、社会规范、减少偏见）；出错时（容易调用、容易忽略、容易纠正、拿不准时缩小范围、能解释）；长期（记得近期交互、从行为中学、谨慎更新、细粒度反馈、说清后果、全局控制、通知变化） | [Microsoft Research 博客](https://www.microsoft.com/research/blog/guidelines-for-human-ai-interaction-design/) · [项目页](https://www.microsoft.com/research/project/guidelines-for-human-ai-interaction/) |
| Google PAIR People + AI Guidebook | 六章：用户需求与成功定义、心智模型、可解释与信任、数据收集与评估、反馈与控制、出错与优雅失败。模式按 8 个问题分组，其中「怎么帮用户建立并校准信任」最多（7 个）。2023-11 起按生成式 AI 修订：幻觉、何时重写或核对生成文本 | [Guidebook](https://pair.withgoogle.com/guidebook-v2/) · [生成式 AI 修订说明](https://medium.com/people-ai-research/updating-the-people-ai-guidebook-in-the-age-of-generative-ai-cace6c846db4) · [官方 codelab](https://codelabs.developers.google.com/codelabs/pair-guidebook) |
| Apple HIG「Generative AI」（2025-06 新页，2026-06-08 更新） | 让人掌控：能忽略、撤回、重试；标明哪里用了 AI；先说清能做什么、做不到什么，开放输入给示例；降低幻觉；不可逆或有问题的动作先征得同意，不要自动执行删除、代买；生成结果旁放编辑、撤销、重试、调整；等待时说清正在做什么，不写「处理中」；可以给几个不同版本；反馈自愿、不打断；没有 AI 也要有好体验 | [HIG Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai.md) |
| NN/g，Nielsen，2023-06-18 | 第三种范式「intent-based outcome specification」：用户说要什么结果，不说怎么做，控制权反转；写提示词有「表达门槛」；未来是意图、命令、图形三者混合 | [AI: First New UI Paradigm in 60 Years](https://nngroup.com/articles/ai-paradigm) |
| NN/g，Moran 与 Neusesser，2025-04-25 | 提示词建议分三类：用例建议（新手、空状态）、自动补全（输入中）、追问建议（回答后，目前最有用）；要和上下文相关，否则被忽略 | [Prompt Suggestions](https://www.nngroup.com/articles/prompt-suggestions/) |
| NN/g，Feifei Liu，2024-08-02 | 输入框周围的控件解决可发现性、示范、限定范围、追问；图标要标准并带文字，功能名要说清楚 | [Prompt Controls](https://www.nngroup.com/articles/prompt-controls-genai/) |
| NN/g，Samsonov，2025-05-16 | 聊天界面让人不去核对：核对成本高、排版精致显得权威、「可能出错」的提示太小；建议在原处给可点出处、让人选中一段追问、显示推理和把握 | [AI Chatbots Discourage Error Checking](https://www.nngroup.com/articles/ai-chatbots-discourage-error-checking/) |
| NN/g，Moran 与 Gibbons，2024-03-22 | 生成式界面（genUI）和「面向结果的设计」：设计师定目标和约束（必须显示、应该显示、绝不显示）；风险是一致性、可学性、可预测性下降 | [Generative UI and Outcome-Oriented Design](https://www.nngroup.com/articles/generative-ui/) |
| Feng、McDonald、Zhang，arXiv 2506.12469，2025 | 五级自主按用户角色分：操作者、协作者、顾问、批准者、观察者；自主是设计选择，和能力分开 | [Levels of Autonomy for AI Agents](https://arxiv.org/abs/2506.12469) |
| Anthropic，2026-02-18 | Claude Code 实测：新用户约 20% 会话全自动批准，750 个会话后超过 40%；老用户打断反而更多（约 9% 的轮次），是在主动监督；复杂任务上 Claude 主动停下来问的次数是人打断次数的两倍多；建议投入「看得见」和「插得进」，不要强制逐步批准 | [Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy) |
| Anthropic 工程博客，2025-11-26 | 长任务跨会话：初始化时写进度文件、功能清单（JSON，只许改通过状态）、git 提交；每个新会话先读日志和进度、跑一遍端到端，再接着做 | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) |
| OpenAI，2025-07-17 | ChatGPT agent：有现实后果的动作先问许可；发邮件这类关键任务要人盯着（Watch Mode）；登录时人接管浏览器；可以打断、暂停、要进度摘要、停止并拿到部分结果；拒绝银行转账这类高风险任务 | [Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/) |
| Anthropic，Claude for Chrome（2025-08，后续更新） | 发布、购买、分享个人数据前确认；按网站授权、随时撤回；屏蔽金融等高风险类别；提示注入攻击成功率加防护后从 23.6% 降到 11.2% | [Claude for Chrome](https://claude.com/resources/articles/claude-for-chrome) |
| Google Research，2025-11-18 | 生成式界面：评分者更喜欢专家设计的网站，生成界面紧随其后，明显好于纯文本；但生成有时要一分钟以上，偶有错误 | [Generative UI](https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/) |
| Google A2UI（2025-12） | Agent 输出声明式 JSON，客户端只从自己的受信组件目录里渲染，不收可执行代码（二手：SD Times；原文见 Google 开发者博客、[github.com/google/A2UI](https://github.com/google/A2UI/)） | [SD Times 报道](https://sdtimes.com/ai/google-launches-a2ui-project-to-enable-agents-to-build-contextually-relevant-uis/) |
| MCP Apps（2026-01-26，MCP 第一个官方扩展） | 工具可以返回交互界面，在沙箱 iframe 里渲染；宿主可审查模板、记录消息、界面发起的工具调用要用户批准 | [MCP Apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) |

### 1.3 核心原则（8 条）

| # | 一句话 | 要解决的问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| A1 | **先说清能做什么、多常出错** | 用户心智模型不准：要么不敢用，要么过度信任 | 入口旁一句能力说明；空状态给 2–4 个能直接点的用例；已知局限写在前面 | 微软 G1、G2；HIG Transparency；PAIR「心智模型」；NN/g 提示词建议 |
| A2 | **人说结果，系统给可编辑的计划** | 只有对话框时，人要会写才会用（表达门槛）；控制权交出去后看不到怎么做 | 先给计划或预览（今天的安排、要改的文件、要发的内容），人可以改其中一项再执行；常用约束做成控件，不靠打字 | NN/g 第三范式、Prompt Controls；HIG「多个版本」 |
| A3 | **按后果分级确认，不逐步确认** | 每步都问会让人疲劳、乱点同意；一步不问又会闯祸 | 每个动作有自主等级；只有不可逆或对外有后果的动作（付款、删除、对外发送、分享个人数据）停下来确认；其余直接做，给撤销 | Feng 等五级；Anthropic 自主度实测；HIG「不可逆动作先征得同意」；OpenAI、Claude for Chrome 的确认规则 |
| A4 | **随时看得见、插得进、撤得回** | Agent 在后台做事，人不知道它做到哪一步，出错时停不下来 | 有活动记录（做了什么、为什么）；任何时刻都能暂停、改方向、接管；生成结果旁有编辑、撤销、重试 | 微软 G8、G9、G11；HIG Outputs；OpenAI 打断与接管；Anthropic「看得见、插得进」 |
| A5 | **等待说清正在做什么；长任务的进度写在外面** | 长时间没反馈，人以为卡死；会话断了、换设备了，进度就丢了 | 进度文字是具体动作（「在挑今天的动作」），不是「处理中」；跨会话的任务有持久化的步骤清单、当前步、下一步；中断后从断点接着做，拿得到已完成的部分 | HIG「具体、让人安心的反馈」；Anthropic 长任务 harness；OpenAI「停止并拿到部分结果」；MCP tasks 扩展（轮询） |
| A6 | **让核对比相信更省力** | 生成内容看起来权威，人不核对；核对一整篇的成本太高 | 事实旁有可点出处，链到原文段落；数字和安全相关的判断来自代码，不来自模型；可以选中一句追问 | NN/g「聊天界面让人不核对」；HIG「降低幻觉」；PAIR「校准信任」；微软 G11 |
| A7 | **生成界面只用受信组件拼，保持一致** | 每次都不一样的界面难学、难预测；模型生成任意代码有安全风险 | 模型输出结构化描述，客户端用自己的组件渲染；组件有目录和 schema；导航、主操作的位置不随生成变化 | A2UI；MCP Apps 沙箱；NN/g genUI 的一致性风险 |
| A8 | **记住什么、学到什么，让人看得见、改得了** | 个性化悄悄发生，人不知道为什么结果变了 | 能看到「威利记住了什么」并删除；行为更新前通知；反馈一步完成、自愿 | 微软 G12–G18；HIG Continuous improvement |

### 1.4 能判对错的规则

「脚本」一列标 ✓ 的可以写成自动检查。

| 规则 | 怎么查 | 脚本 |
|---|---|---|
| AUI-1 每块 AI 生成的内容都有可见标识（图标加文字，或一行说明），DOM 上带 `data-origin="ai"` | 组件测试：所有 `data-origin="ai"` 的节点内或相邻处有可见标识文字 | ✓ |
| AUI-2 每个主动动作在配置里声明自主等级和是否可逆；`reversible: false` 或有外部后果（付款、删除、对外发送、分享个人数据）的动作必须是「先确认」等级 | 对动作配置做 lint：不可逆且不需要确认的条目数 = 0 | ✓ |
| AUI-3 可逆的动作不弹「确定吗」，做完给「撤销」，撤销至少保留到下一次操作或 10 秒（10 秒是自定） | 端到端：执行后能撤销，撤销后状态与执行前一致 | ✓ |
| AUI-4 每个生成结果旁至少有编辑、撤销、重试中的两项 | 组件测试 | ✓ |
| AUI-5 等待超过 1 秒时显示具体在做什么；界面文案里不出现「处理中」「加载中…」「Processing…」这类笼统词（骨架屏除外）；超过 10 秒的允许离开，后台继续，完成后通知 | 文案 lint 禁用词表；端到端量时间 | ✓（禁用词）|
| AUI-6 跨会话的任务把步骤、当前步、下一步存在服务端；关掉页面再打开，从断点继续，已完成的部分仍可见 | 端到端：任务进行中关闭上下文、重开，比较步骤状态 | ✓ |
| AUI-7 Agent 正在执行时，暂停或停止按钮一直可见，按下后 1 秒内生效，并保留已完成的结果 | 端到端 | ✓ |
| AUI-8 模型输出里的数字和安全判断，必须等于代码或数据库给的值；做不到就不显示数字 | 单元测试：对比模型输出里的数字和工具返回值（Veli 已有这条线：「数字和安全只由代码决定」） | ✓ |
| AUI-9 事实性陈述附可点出处，链到原文的具体位置（锚点或段落） | 内容评审抽查；出处链接 200 可以脚本查 | 部分 ✓ |
| AUI-10 生成式界面只渲染组件目录里的类型，props 过 schema 校验；不渲染模型给的任意 HTML 或脚本 | 单元测试：目录外的类型被拒绝 | ✓ |
| AUI-11 开放输入（搜索、对威利说话）的空状态有 2–4 个能直接点的用例，点了直接执行，不只是填进输入框 | 设计评审 | |
| AUI-12 有一页「威利记住了什么」：列出记忆，每条可以删除，删除后下一次行为不再用它 | 端到端 | ✓ |
| AUI-13 主动提醒经过打扰预算和统一改期，不在用户正在做的事中途打断 | 规则引擎单元测试（Veli 已有） | ✓ |
| AUI-14 对每条生成结果的反馈一步完成（赞或踩），不弹层、不打断 | 设计评审 | |

### 1.5 批判

**还是提案、没有落地的**
- 自主等级五级（Feng 等）是框架论文，没有用户实验验证；它的「自主证书」只是设想。我们拿它当词表用，不当标准用。
- A2UI 0.x 和 MCP Apps 都还在快速变化。MCP Apps 是正式扩展，但宿主各自实现。生成式界面在我们的两个产品里都没有现成场景，不要为它搭基础设施。

**炒作的**
- 「界面会消失，以后一切都是对话」：Nielsen 本人的结论就是混合界面。NN/g 测过，用户常常不知道该问什么，所以才需要提示词建议和控件。
- 「每个界面都按人实时生成」：Google 自己的实现要一分钟以上，评分者仍然更喜欢专家设计的页面。对内容站来说，不划算。
- 「人在回路就是每步都批准」：Anthropic 的数据说，老用户全自动批准得更多，打断也更多。监督靠看得见和插得进，不靠逐步批准。

**旧指南的局限**
- 微软 18 条成文于大模型之前，针对的是推荐、补全这类功能，没讲 Agent 替人执行动作；18 条也没分轻重。PAIR 大部分章节针对传统机器学习，生成式的修订只列了问题，没给新模式。
- HIG 的用词是「consider」「generally」，判不了对错，要按我们的 `quality-terms.md` 改写成规则才能验收。

**和面向人的体验冲突的地方，以及怎么取舍**

| 冲突 | 取舍 |
|---|---|
| 确认多一步，和「核心场景两步内」冲突 | 只给不可逆和对外有后果的动作加确认；其余用撤销。确认属于安全确认，不计入步数预算（PRD 已把删除账号的「输入删除」算作安全确认） |
| 能力说明、用例建议要字，和 C10「首屏要读的字不超过 80 字」冲突 | 用例建议做成按钮，算控件，不算要读的说明；能力说明一句话 |
| 标识 AI 内容会显得啰嗦 | 标识放在区块级（一次），不逐句标 |
| 活动记录、记忆页增加界面 | 放在二级入口，主屏只放「威利替你做了什么」的一行摘要 |

---

## 第二部分 AX：Agent 怎么用我们的网站

### 2.1 结论

Agent 有三种读网页的方式：读无障碍树、读正文、看截图。Claude 浏览器工具的文档建议先读无障碍树，因为它更省、给出可以直接操作的引用，也不怕版面移动。Google 搜索的 AI 指南也说浏览器 Agent 读截图、DOM 和无障碍树，所以语义 HTML 有用。结论是：**AX 的主体是早就该做的无障碍和网页基本功，新东西只是一层薄薄的补充。**新东西里，只有「认签名而不是上验证码」和「站点一侧对有后果的动作要求人确认」值得现在就定成规则；llms.txt 便宜，可以顺手做；WebMCP 等标准定了再说。

### 2.2 来源要点

| 来源 | 讲了什么（转述） | 链接 |
|---|---|---|
| Netlify，Biilmann | AX 是 Agent 作为产品用户的整体体验：拿到访问权要简单、接口描述清楚、给机器读的文档、把 Agent 当一类用户、对外部 Agent 开放、缩短从输入到结果的路。Netlify 另出了 AXIS 评分框架，用真实 Agent 跑真实场景 | [Introducing AX](https://hn.jakechampion.name/reader/https://biilmann.blog/articles/introducing-ax)（原文转载）· [The era of AX](https://www.netlify.com/blog/the-era-of-agent-experience-ax.md) · [Agent Experience](https://www.netlify.com/agent-experience.md) |
| llms.txt，Jeremy Howard，2024-09-03 提出 | 根目录一个 Markdown 文件：H1 站名（唯一必填）、一段摘要、若干 H2 链接清单，「Optional」一节可以跳过；每页另有 `.md` 版本，用 `rel="alternate" type="text/markdown"` 指过去。仍是征求意见的提案 | [llmstxt.org](https://llmstxt.org/) |
| Google 搜索中心，AI 优化指南（2026-07-10 更新） | Google 搜索不读 llms.txt；生成式 AI 搜索不需要结构化数据，但结构化数据仍让页面有资格出富结果；浏览器 Agent 读截图、DOM、无障碍树，所以语义 HTML 有用 | [AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) |
| Chrome Lighthouse「Agentic Browsing」类别（实验，Chrome 150+） | 7 项：已注册的 WebMCP 工具、表单缺少声明式 WebMCP、WebMCP schema 合法性、llms.txt（取文件时服务器报错才算失败，404 算不适用）、ard.json、给 Agent 的无障碍（名称和标签、树结构、可交互内容没有被藏起来）、版面稳定（CLS）。不给加权总分 | [评分说明](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring) · [llms.txt 审计](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt) |
| web.dev，Kulikowski 与 More（2026-04-01） | 不用透明覆盖层盖住可点元素；用 `<button>` `<a>`；做不到时加 role 和 tabindex；label 用 `for` 关联输入框；可点元素加 `cursor: pointer`；目标不小于 8 平方像素；版面稳定、同类页面的主按钮位置不变；DOM 嵌套反映归属；审一遍无障碍树；可以加 WebMCP 工具；购买这类敏感动作要人确认 | [Build agent-friendly websites](https://web.dev/articles/ai-agent-site-ux) |
| Claude 浏览器工具文档（稳定版） | `read_page` 读无障碍树并给每个元素一个引用；`find` 用自然语言找元素；`get_page_text` 读正文；截图和放大。引用在导航或 DOM 大改后失效；canvas、视频、跨域 iframe 只能退回坐标点击；后果大的动作（购买、改账号、发消息、接受条款）要人确认 | [Browser use tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool.md) |
| WebMCP，W3C 网络机器学习社区组，草案 2026-11-02 | 编辑来自微软和 Google。API 是 `document.modelContext`（不再是 `navigator.modelContext`）：`registerTool`、`getTools`、`executeTool`；受 `tools` 权限策略控制；安全章节讲提示注入、意图与实际不符、参数过多泄露隐私，提供 `consequentialHint`、`untrustedContentHint` 标注，但恶意站点可以不标。**不是 W3C 标准，不在标准轨道上** | [WebMCP 草案](https://webmachinelearning.github.io/webmcp) · [Chrome 149 源试用](https://developer.chrome.com/blog/ai-webmcp-origin-trial) |
| MCP 规范 2026-07-28（稳定版） | 改成无状态：去掉会话和握手，新增 `server/discover`；长任务移到官方扩展 `tasks`（轮询）；采样、根目录、日志标为弃用；工具列表要按固定顺序返回。MCP 已由 Anthropic 捐给 Linux 基金会下的 Agentic AI Foundation | [变更记录](https://modelcontextprotocol.io/specification/2026-07-28/changelog) · [AAIF 公告](https://openai.com/index/agentic-ai-foundation/) |
| AGENTS.md（OpenAI，2025-08；2025-12 捐给 AAIF） | 放在 README 旁、给编码 Agent 的项目说明；6 万多个开源项目采用 | [AAIF 公告](https://openai.com/index/agentic-ai-foundation/) |
| DESIGN.md（Google Stitch，2026-04，alpha，Apache 2.0） | 用 YAML 写设计 token，用正文写为什么；附 CLI 校验、比对、导出为 Tailwind 或 W3C DTCG（二手：The Decoder；原文 [github.com/google-labs-code/design.md](https://github.com/google-labs-code/design.md)） | [The Decoder 报道](https://the-decoder.com/googles-open-source-design-md-gives-ai-agents-a-prompt-ready-blueprint-for-brand-consistent-design/) |
| schema.org Actions | `potentialAction` 加 `urlTemplate` 和 `-input` 标注，描述某个东西上能做的动作（如站内搜索）；文档没说谁在消费 | [Potential Actions](https://schema.org/docs/actions.html) |
| W3C，Berners-Lee，1998 | 好的 URI 不变；地址里别放作者、主题分类、状态、文件扩展名、技术细节 | [Cool URIs don't change](https://w3.org/Provider/Style/URI) |
| IETF Web Bot Auth 工作组草案（-01，2026-10-29，标准轨道，未成 RFC） | 自动客户端用 HTTP 消息签名（RFC 9421）给请求签名；`Signature-Agent` 头指向密钥目录 | [draft-ietf-webbotauth-httpsig-protocol](https://datatracker.ietf.org/doc/html/draft-ietf-webbotauth-httpsig-protocol) |
| OpenAI，ChatGPT agent 放行说明 | 请求按 RFC 9421 签名，带 `Signature-Agent: https://chatgpt.com`；Cloudflare、Akamai 自动验证；Vercel 不用配置，识别为 `chatgpt-operator` | [ChatGPT agent allowlisting](https://help-lb.openai.com/en/articles/11845367-chatgpt-agent-allowlisting) |
| Cloudflare 已验证机器人（2026-07-01 起含签名 Agent） | 要求如实自报身份（签名、IP 清单或反查 DNS）并且不滥用（遵守 robots.txt、请求频率合理）；分「直接」和「中介」两类，中介类在试 `Forwarded` 头传终端用户信息 | [Verified bots](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/index.md) |
| Vercel BotID | `checkBotId()` 返回是否已验证、机器人名和类别，可以放行特定的 AI 助手、拦住其他机器人；Vercel 的验证支持 Web Bot Auth | [Handling verified bots](https://vercel.com/docs/botid/verified-bots) |

### 2.3 核心原则（8 条）

| # | 一句话 | 要解决的问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| X1 | **无障碍树就是 Agent 的接口** | 用 div 做的按钮、没名字的图标，Agent 认不出、点不到 | 可交互元素都是原生控件或带 role；每个都有可读名称；表单字段和 label 关联；装饰性的 canvas 从树里藏掉 | web.dev；Google AI 指南；Lighthouse「给 Agent 的无障碍」；Claude 浏览器工具 |
| X2 | **状态写进地址，地址永远有效** | Agent 和人都要能直达、复现、分享某个状态；改版后旧链接死了，Agent 记下的地址全部失效 | 语言、站、内容线、筛选、搜索词都在 URL；刷新、新标签打开得到同一状态；改地址一律 301 | W3C Cool URIs；PRD 第 6 节「稳定网址」 |
| X3 | **版面稳定，目标看得见** | 截图型 Agent 怕元素移动、怕透明层挡住、怕目标太小 | CLS ≤ 0.1；同类页面的主操作位置不变；没有透明层盖住可点元素 | web.dev；Lighthouse 版面稳定 |
| X4 | **正文不靠脚本也读得到** | 只靠客户端渲染的页面，读正文的工具和抓取器拿到空壳 | 服务端渲染出正文、标题、日期、作者 | Claude `get_page_text`；Google 搜索技术要求（AI 指南） |
| X5 | **给内容一份机器可读的平行版本，从同一来源生成** | 机器要从版面里抠结构，易错 | JSON-LD（Article 等）、sitemap、RSS 全文、可选的 `.md` 替身和 llms.txt，都由内容数据生成，不手写第二份 | llmstxt.org；Google AI 指南；PRD 第 6 节 SEO、F25 |
| X6 | **表单是最小的 API，确认点设在站点一侧** | Agent 可能被注入、可能误操作；站点不能只指望 Agent 自觉 | 表单字段有名字、有约束（`required`、`type`、`maxlength`）；不可逆的动作在站点一侧要求人确认（二次邮件、输入「删除」） | web.dev「敏感动作要确认」；WebMCP `consequentialHint`；Claude for Chrome |
| X7 | **认身份，不挡机器** | 验证码挡住代用户办事的合法 Agent，却挡不住专业的滥用 | 读内容和订阅不用验证码；防滥用靠频率限制、二次确认和签名验证；放行已验证的用户代理型 Agent | IETF Web Bot Auth；OpenAI 放行说明；Cloudflare、Vercel 文档 |
| X8 | **给开发 Agent 的说明书只放必须的** | 编码 Agent 找不到约定，或者被太长的说明淹没 | 根目录 AGENTS.md 指路；设计 token 机器可读（tokens.json 或 DESIGN.md）；规则能用脚本检查 | AGENTS.md（AAIF）；DESIGN.md |

### 2.4 能判对错的规则

| 规则 | 怎么查 | 脚本 |
|---|---|---|
| AX-1 每个可点元素是原生 `button`、`a[href]`、`input`、`select`、`summary`，或带 `role` 和 `tabindex`；每个都有可读名称（文字、`aria-label` 或 `aria-labelledby`） | axe 的 `button-name`、`link-name`、`label`；Lighthouse Agentic Browsing 的无障碍项；eslint `jsx-a11y/no-static-element-interactions`、`click-events-have-key-events` | ✓ |
| AX-2 每个输入框有关联的 label | axe `label` | ✓ |
| AX-3 原地展开的选项不依赖悬停：选项始终在 DOM 里，用 `aria-expanded` 控制显示，每个选项是带 `href` 的真链接；不悬停、只用点击或回车也能到达每个去处 | Playwright：不悬停，读无障碍树，所有去处的地址都能找到或一次点击可达 | ✓ |
| AX-4 主要状态都在 URL 里：语言（`/en/`）、站、内容线分段、筛选、搜索词；把当前 URL 在新的浏览器上下文打开，得到同一状态 | Playwright 往返测试：每次改状态后记 URL，新上下文打开，比较关键节点 | ✓ |
| AX-5 `<html lang>` 等于页面语言；中英页面互相标 `hreflang`；每页有 `canonical` | 脚本抓每页的 head | ✓ |
| AX-6 公开 URL 只增不删；改地址必须 301，旧地址表进测试（原同席博客的旧链接已经要求逐条跳转） | 重定向测试：旧地址清单逐条请求，状态 301、落点 200 | ✓ |
| AX-7 没有透明层盖住可点元素：每个可点元素中心点上的最上层元素是它自己或它的子元素 | Playwright `elementFromPoint` | ✓ |
| AX-8 CLS ≤ 0.1（已在 U8）；同类页面的主操作位置差不超过 8px（自定，沿用 U10 的阈值） | Lighthouse；截图比对 | ✓ |
| AX-9 不执行 JavaScript 时，文章页的 HTML 里有标题、作者、日期和完整正文 | `curl` 取页面，检查正文的首尾句都在 | ✓ |
| AX-10 文章页有 JSON-LD `Article`：`headline`、`author`、`datePublished`、`dateModified`、`inLanguage`、`url`，值和页面可见内容、内容数据一致；首页有 `WebSite` 和 `Organization` | 脚本解析 JSON-LD 并和内容数据比对；Google 富结果测试 | ✓ |
| AX-11 `sitemap.xml` 列出所有公开页面，`lastmod` 等于 `dateModified`；RSS 有全文和日期（F25） | 脚本 | ✓ |
| AX-12 `/llms.txt` 返回 200，格式符合 llmstxt.org（一个 H1、摘要、H2 链接清单），所列链接都返回 200；由内容数据生成 | 脚本 | ✓ |
| AX-13 读内容、订阅、搜索都不出验证码或 JavaScript 质询；订阅表单靠频率限制和邮件二次确认防滥用 | 端到端用无头浏览器走订阅；检查 Vercel 防火墙配置 | ✓ |
| AX-14 如果打开 Vercel 机器人防护，放行已验证的用户代理型 Agent（类别为 Agent、Search 的） | 读防火墙配置（评审） | |
| AX-15 埋点和统计把已验证机器人和人分开计数；订阅数、点击率只算人 | 查统计配置；用签名请求打一次，确认没进人的指标 | ✓ |
| AX-16 不可逆或对外有后果的动作，在站点一侧要求人确认，不能只靠 Agent 的自觉（删除账号输入「删除」、订阅要点确认邮件） | 端到端 | ✓ |
| AX-17 装饰性动效（「叶与网」的 canvas）带 `aria-hidden="true"`，它表达的入口另有真链接 | axe；读无障碍树 | ✓ |

### 2.5 批判

**还是提案、没有落地的**
- **WebMCP**：社区组草案，不在 W3C 标准轨道；只在 Chrome 149 源试用里有；一年内接口名已从 `navigator.modelContext` 改成 `document.modelContext`；Lighthouse 的 WebMCP 审计也要先报名源试用。草案自己承认恶意站点可以不标后果。**现在不做**，等它进标准轨道或至少两家浏览器默认开启再评估。
- **llms.txt**：提案。Google 搜索明说不读它；John Mueller 把它比作 keywords meta 标签（二手报道，见 [TechWyse](https://www.techwyse.com/news/ai-search/google-ai-search-optimization-guide-llms-txt-lighthouse-audit)）。Lighthouse 只在服务器报错时判失败，404 算不适用。我们的内容本来就是结构化数据，生成一份的成本是一个构建脚本，可以做，但不要期待流量。
- **Web Bot Auth**：IETF 草案，2027-05 到期前可能还会改；中介型 Agent 怎么带终端用户身份，Cloudflare 还在试。我们用 Vercel 的现成验证就够，不自己验签。
- **Lighthouse 的 ard.json** 审计：文档没有说明它检查什么，不采用。
- **schema.org `potentialAction`**：文档没有说谁在消费，不为 Agent 专门加。

**炒作的**
- 「AX」这个词来自 Netlify（托管平台），有推广自家平台的成分；它的「原则」没有成文清单，AXIS 评分也是自家框架。可取的是视角：把 Agent 当一类用户。
- 「GEO / 为 AI 搜索重写内容」：Google 的官方指南把内容切块、为 AI 改写、为 AI 堆结构化数据都列为不需要的做法。
- 「每个网站都该有 MCP 服务器」：MCP 2026-07-28 版刚做了一次大的不兼容修改（去掉会话、弃用采样）。一个内容站没有值得暴露的动作，做 MCP 是过度设计。Veli 以后如果要让外部 Agent 读训练安排，再按 ADR 评估。

**和面向人的体验冲突的地方，以及怎么取舍**

取舍的总原则：**一份 DOM，两种读法。表现层为人设计，结构层同时服务人和 Agent；只为机器加的东西必须从同一来源生成，不维护第二份。**

| 冲突 | 取舍 |
|---|---|
| PRD 的「原地展开」在桌面靠悬停 | 不冲突，前提是选项始终在 DOM 里、触发器是带 `aria-expanded` 的按钮、选项是真链接（AX-3）。悬停只是更快的显示方式，不是唯一的入口。PRD 已经要求键盘聚焦也能展开，这一条顺带满足 Agent |
| 玻璃导航、浮层压在内容上 | 玻璃本身不是透明覆盖层，只要不拦截下面元素的点击；检查 AX-7 |
| 「叶与网」是 canvas，Agent 看不懂 | canvas 只做装饰（AX-17）；三站入口另有真链接。Claude 文档说 canvas 只能退回坐标点击，所以入口不能只画在 canvas 上 |
| 「不用读就会用」，多用图标 | 只用图标的按钮也要有 `aria-label`（C10 已限定只用通行图标）；对人不显示的名字对 Agent 有用，不加视觉负担 |
| 悬停时预连接下一步、Google One Tap 自动登录 | Agent 不悬停、通常不登录。v1 读内容不需要登录，所以不受影响；登录相关的流程让人接管（OpenAI 的 takeover、Claude 的低权限账号建议），不为 Agent 改登录 |
| 不用验证码会多一些垃圾订阅 | 订阅本来就要二次确认，垃圾地址不会进入发送名单；加频率限制。验证码对人也是负担，不采用 |
| Agent 流量会污染「订阅数」「首页到三站的点击率」 | 分开计数（AX-15），否则 v1 的核心指标会失真 |

---

## 第三部分 我们的现状

### 3.1 结论

**主站的 PRD 和质量规则已经覆盖了 AX 的大部分：** 稳定网址、`/en/` 路径、hreflang、结构化数据、sitemap 和 RSS、WCAG 2.2 AA 加 axe、键盘操作、CLS ≤ 0.1、订阅二次确认加频率限制、删除账号的安全确认。缺的是三类：**写在 PRD 里、现有代码还没做到的**（语言进地址、`<html lang>`、sitemap 和 JSON-LD）；**规则里没写的**（筛选和搜索词进地址、展开选项不靠悬停存在、装饰 canvas 藏起来、机器人流量分开统计、不用验证码）；**还没有一个维度把它们集中起来检查**。Veli 的「威利提前安排、用户照做」本身就是 AUI 里自主等级偏高（批准者到观察者）的模式，它已有的 A/S/B/C/D 等级、打扰预算、B 级可撤销、数字由代码决定，和本报告的 A3、A4、A6 对得上。

### 3.2 已经对 Agent 友好的

| 项 | 在哪里 | 对应规则 |
|---|---|---|
| 每篇文章、里程碑、学习路径步骤都有独立页面和稳定网址；原同席博客的旧链接逐条跳转 | PRD 第 3 节、第 6 节「SEO」、第 10 节 | X2、AX-6 |
| 中英两版互标语言版本，英文走 `/en/` | PRD F06、第 8 节「国际化」 | AX-4、AX-5 |
| 内容类型有固定字段，存成结构化数据 | PRD 第 5 节、第 8 节「可维护」 | X5、AX-10 |
| 结构化数据（文章、课程）、站点地图、RSS 全文 | PRD 第 6 节、F25 | AX-10、AX-11 |
| WCAG 2.2 AA、axe 严重问题为 0、只用键盘能完成全部操作 | PRD 第 8 节；`quality-terms.md` A7、U11 | X1、AX-1 |
| 原地展开在键盘聚焦时也展开；触屏上选项直接摆出来 | PRD 第 4 节「原地展开」 | AX-3（部分） |
| 两条内容线的分段控件「地址跟着变」 | PRD 第 4 节「少一步的做法」 | AX-4（部分） |
| CLS ≤ 0.1；加载时占位保持版式 | PRD 第 8 节、页面状态；`quality-terms.md` U8 | X3、AX-8 |
| 按钮写结果，不写「了解更多」 | PRD 第 4 节；`quality-terms.md` U5、C4 | X1（名称有意义） |
| 视频有字幕和文字稿；图有文字说明；视频播不了直接显示文字稿 | PRD 第 8 节、页面状态 | X4 |
| 订阅只收邮箱、二次确认、频率限制；不提验证码 | PRD F07、第 8 节「安全」 | X7、AX-13、AX-16 |
| 删除账号要输入「删除」 | PRD 步数预算 | AX-16 |
| 能撤回的用「撤销」，不弹「确定吗」；不用操纵手段 | PRD 第 4 节；`quality-terms.md` U6、T9 | A3、AUI-3 |
| 超过 1 秒先显示进度 | PRD 第 4 节「一秒」；`quality-terms.md` U8、U9 | A5 |
| 事实有出处，链到原文 | `AGENTS.project.md` 第 6 条；`quality-terms.md` T1 | A6 |
| 仓库有 AGENTS.md、设计系统的 `system/README.md` 和 `tokens.json`；质量词能用脚本检查 | 仓库根目录；`docs/uiue/system/` | X8 |

### 3.3 还不友好的

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| 1 | 语言只在 React 状态里，不进地址；`<html lang>` 写死 `zh-CN` | `src/lib/lang.tsx` 第 8 行 `useState<Lang>("zh")`；`src/routes/__root.tsx` 第 35 行 | 英文状态没法分享、没法被搜索单独收录；读屏软件和 Agent 都把英文当中文读 |
| 2 | 没有 sitemap、robots.txt、JSON-LD | `public/` 下没有这些文件，`src/` 里搜不到 `ld+json` | PRD 已要求，还没实现 |
| 3 | 有用 `div` 加 `onClick` 的可点区域 | `src/components/feynman-film.tsx` 第 169 行 | Agent 和键盘用户都认不出它可点 |
| 4 | 规则没要求筛选、搜索词进地址 | F13「可按类型筛选」、搜索都没说地址 | 筛过的列表没法直达 |
| 5 | 规则没要求展开的选项始终在 DOM 里 | PRD「原地展开」只说了悬停、触屏、键盘怎么显示 | 实现成悬停时才挂载，Agent 就看不到选项 |
| 6 | 「叶与网」canvas 是否 `aria-hidden`，三站入口是否在 canvas 外有真链接，没写成规则 | 设计系统和 V7 只讲视觉 | Agent 只能按坐标点 canvas |
| 7 | 监测没区分机器人流量 | PRD 第 6 节「监测」 | 核心指标订阅数、点击率会被 Agent 流量抬高 |
| 8 | 没有明说「不用验证码」 | PRD 第 8 节只写了频率限制和二次确认 | 以后有人加验证码时没有规则拦 |
| 9 | `quality-terms.md` 第 4 节的五个维度里没有「Agent 能不能用」 | 第 4 节只有 U、C、V、T、A | 上面这些规则没有地方挂，评审不会系统地查 |

### 3.4 最小必要的改法

按「对人也有用、PRD 已要求、成本低」排序。前 3 项不需要新的产品决定。

1. **语言进地址（修问题 1）。** 按 PRD F06 改成 `/en/` 路由，语言从路径读，不放 React 状态；`<html lang>` 跟着路由；手动切换后记住选择，只影响第一次访问的跳转。加 AX-4、AX-5 的 Playwright 往返测试。这一项对人和 Agent 收益都最大。
2. **上线前的机器可读件，全部从内容数据生成（修问题 2）。** 一个构建脚本同时产出 `sitemap.xml`、RSS、每页的 JSON-LD；顺手产出 `/llms.txt`，成本几乎为零。不手写第二份内容。
3. **把 `div onClick` 换成 `button`，并在 eslint 打开 `jsx-a11y` 的两条规则（修问题 3）。** 修一处，用 lint 防同类问题，符合「一条意见代表一类问题」。
4. **在 `quality-terms.md` 第 4 节加一个维度「Agent 可用（X）」，只放 6 条，都用脚本查（修问题 4–9）：**
   - X1 主要状态都在 URL 里（AX-4，含筛选、搜索词）
   - X2 可点元素都有名称和语义（AX-1、AX-2，复用 axe 和 eslint）
   - X3 展开的选项始终在 DOM 里，不悬停也能到达（AX-3）；装饰 canvas 藏起来（AX-17）
   - X4 不执行脚本也能读到正文，机器可读件由内容数据生成（AX-9 到 AX-12）
   - X5 读内容和订阅不用验证码，后果大的动作在站点一侧确认（AX-13、AX-16）
   - X6 机器人流量和人分开统计（AX-15）

   放在第 4 节而不是另起一份文档：Agent 是一类用户，它的「好用」和人的好用平级。和 A 维度（无障碍）重叠的规则写「见 A7」，不重复写。关口四在预览部署上加跑 Lighthouse 的 Agentic Browsing 类别，作为参考信号，不设门槛（这个类别本身不打分，而且还是实验功能）。
5. **不做的事：** WebMCP、MCP 服务器、`potentialAction`、ard.json、自己验签。理由见 2.5。等 WebMCP 进入标准轨道再写 ADR 评估。

### 3.5 Veli：「威利替你提前安排，你照做」

**结论：这个模式是 AUI 里难度最高的一种，因为人没有主动发起，就更需要「看得见、改得了、撤得回」。** Veli 的工作手册在另一个仓库，这里只按模式和 Veli 仓库 `AGENTS.md` 写明的几条线判断，具体有没有做到，要在 Veli 仓库里核对。

| AUI 原则 | Veli 已有（据 Veli 仓库 `AGENTS.md`） | 要在 Veli 里核对或补的 |
|---|---|---|
| A3 按后果分级 | 每个主动动作先判自主等级 A/S/B/C/D，经过打扰预算和统一改期 | 等级是否写在带版本的配置里，并有 AUI-2 的 lint |
| A4 撤得回 | B 级可撤销 | 「威利替你做了什么」是否有一条活动记录，每条可以撤销（AUI-3） |
| A2 计划可预览、可改 | 用户「照做或到场」 | 今天的安排在开始前能不能改一项（换动作、改时间），改了威利是否明确确认改动生效（HIG：确认更正已生效） |
| A6 核对比相信省力 | 数字和安全只由代码决定，模型只提议、代码裁决；安全问题不经过模型 | 「为什么今天这样安排」是否有一句可点开的解释（微软 G11） |
| A5 长任务可恢复 | 未知 | 训练中断（来电、断网）后，回来是否从当前组继续，已完成的组是否保留（AUI-6） |
| A8 记忆可见 | 同意先于行动 | 有没有「威利记住了什么」的页面，每条能删（AUI-12） |
| 微软 G3 时机 | 打扰预算 | 已有 |

Veli 最该补的一件事是：**一条「威利替你做了什么」的活动记录，每条附原因和撤销。**它同时满足 A3、A4、A6、A8，而且 B 级可撤销已经有了，只差把这些动作集中摆出来。

---

## 附：来源清单

AUI
- [Microsoft Research：Guidelines for Human-AI Interaction](https://www.microsoft.com/research/blog/guidelines-for-human-ai-interaction-design/)
- [Google PAIR Guidebook](https://pair.withgoogle.com/guidebook-v2/) · [生成式 AI 修订](https://medium.com/people-ai-research/updating-the-people-ai-guidebook-in-the-age-of-generative-ai-cace6c846db4) · [PAIR codelab](https://codelabs.developers.google.com/codelabs/pair-guidebook)
- [Apple HIG：Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai.md)
- [NN/g：AI 是 60 年来第一个新范式](https://nngroup.com/articles/ai-paradigm) · [提示词建议](https://www.nngroup.com/articles/prompt-suggestions/) · [输入框控件](https://www.nngroup.com/articles/prompt-controls-genai/) · [聊天界面让人不核对](https://www.nngroup.com/articles/ai-chatbots-discourage-error-checking/) · [生成式界面](https://www.nngroup.com/articles/generative-ui/)
- [Feng 等：Levels of Autonomy for AI Agents](https://arxiv.org/abs/2506.12469)
- [Anthropic：Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy) · [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Claude for Chrome](https://claude.com/resources/articles/claude-for-chrome)
- [OpenAI：Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/)
- [Google Research：Generative UI](https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/) · [A2UI（SD Times）](https://sdtimes.com/ai/google-launches-a2ui-project-to-enable-agents-to-build-contextually-relevant-uis/) · [MCP Apps](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)

AX
- [Biilmann：Introducing AX](https://hn.jakechampion.name/reader/https://biilmann.blog/articles/introducing-ax) · [Netlify：The era of AX](https://www.netlify.com/blog/the-era-of-agent-experience-ax.md) · [Netlify：Agent Experience](https://www.netlify.com/agent-experience.md)
- [llmstxt.org](https://llmstxt.org/)
- [Google：AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) · [web.dev：Build agent-friendly websites](https://web.dev/articles/ai-agent-site-ux)
- [Lighthouse Agentic Browsing 评分](https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring) · [llms.txt 审计](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt)
- [WebMCP 草案](https://webmachinelearning.github.io/webmcp) · [Chrome WebMCP 源试用](https://developer.chrome.com/blog/ai-webmcp-origin-trial)
- [MCP 2026-07-28 变更记录](https://modelcontextprotocol.io/specification/2026-07-28/changelog) · [Agentic AI Foundation](https://openai.com/index/agentic-ai-foundation/)
- [Claude 浏览器工具文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool.md)
- [schema.org Potential Actions](https://schema.org/docs/actions.html) · [W3C：Cool URIs don't change](https://w3.org/Provider/Style/URI)
- [IETF Web Bot Auth 草案](https://datatracker.ietf.org/doc/html/draft-ietf-webbotauth-httpsig-protocol) · [OpenAI：ChatGPT agent 放行](https://help-lb.openai.com/en/articles/11845367-chatgpt-agent-allowlisting) · [Cloudflare：Verified bots](https://developers.cloudflare.com/bots/concepts/bot/verified-bots/index.md) · [Vercel：Handling verified bots](https://vercel.com/docs/botid/verified-bots)
- [The Decoder：DESIGN.md](https://the-decoder.com/googles-open-source-design-md-gives-ai-agents-a-prompt-ready-blueprint-for-brand-consistent-design/)（二手）· [TechWyse：Google 与 llms.txt](https://www.techwyse.com/news/ai-search/google-ai-search-optimization-guide-llms-txt-lighthouse-audit)（二手，仅用于 Mueller 的表态）
