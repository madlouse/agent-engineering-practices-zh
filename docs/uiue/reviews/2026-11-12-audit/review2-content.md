# 冷审：Velicoach 主站 UI v1.1 画板对外文字（中 / 英）

结论：修改后发布。阻塞 3 条，重要 15 条，建议 16 条。

范围：Main、Mind、Learn、Article、About、Build、Project、Body、States 九块画板脚本里的中英文案（COPY、SHELL、LISTS、MILESTONES、LEVELS、ART_*），对照了 Main-1440-light 截图（截图和源一致）。依据：`velicoach-content` 技能、`docs/GLOSSARY.md`、`docs/standards/quality-terms.md`、PRD 第 505 版。只读，没有改文件。

环境限制：WebFetch 只能打开搜索结果里出现过的地址。bjsm.bmj.com、bmj.com 正文、pubmed、addyosmani.com 的文章页、OUP 上的图灵论文这几处被权限拦下（报 PROVENANCE_REQUIRED），pmc.ncbi.nlm.nih.gov 返回人机验证页。所以这些原文是从同一篇论文的另一份全文（PDF 镜像、Cochrane 官方摘要页、PMC 摘要）核对的，没法打开的链接都在第 2 节标明了。

## 1. 阻塞

| # | 画板 · 位置 | 问题 | 建议改法 |
|---|---|---|---|
| B1 | Main · 研究卡「防摔」：「坚持运动的社区老人，跌倒次数减少 23%。」 | 数字没错（Cochrane CD012424，跌倒发生率降低 23%，59 项研究、12,981 人，高可信度），但这个数是**各类运动**和对照比的结果，以平衡和功能训练为主。Cochrane 原话是：主要做抗阻练习的项目，证据不足以判断效果。这张卡放在「为什么是肌肉」下面，读起来像力量训练能少摔 23%，超出了研究支持的范围。「坚持运动」也不准确：试验比的是参加运动项目和对照，没有比坚持与否。人群是 60 岁以上的社区居民 | 中文：「60 岁以上的社区居民参加运动锻炼项目，跌倒次数少 23%；效果最明确的是平衡和功能训练，再加力量练习。」英文同义：「Exercise programs, mostly balance and functional training, cut falls by 23% in adults 60+ living at home.」或者换一个力量训练单独作为干预的研究。出处：https://www.cochrane.org/CD012424/EXERCISE_exercise-preventing-falls-older-people-living-community |
| B2 | Article（开发日志版式）ART_LOG「两个产品，共用一个域名」：PR「velicoach #1：路由表，已合并」，日期 2026-11-03；Build 和 Project 的日志列表 one-domain 也链 PR #1 | 出处不对。velicoach PR #1 是「并入 Velicoach 主站：主站和看清的文章都放在这个仓库」，2026-11-04 创建、合并，只加文档和技能，里面没有路由表。PR 正文还写着「旧地址永久跳转」，和后来的决定相反。PRD 写的是路由在 thin-muscle-coach PR #84（ADR-0032） | 链到真正做路由表和分流的 PR 或提交（thin-muscle-coach#84 或对应的 ADR-0003 提交），日期按那个提交改；找不到就别用这条日志当样张 |
| B3 | Mind · POSTS 的 slug `harness-outlasts-model`、`super-agent` | 仓库 `src/content/engineering.ts` 里实际的 slug 是 `shopify-harness`、`deepseek-superagent`（也是 PRD F27 列的地址）；Main 和 Article 用的是 `shopify-harness`。看清页的两张文章卡会链到不存在的地址（404） | 改成 `shopify-harness`、`deepseek-superagent` |

## 2. 事实和出处，逐条核对

### 2.1 首页三张研究卡

| 卡 | 画板写的 | 核对 | 结论 |
|---|---|---|---|
| 防摔 | Cochrane 2019；随机对照试验的系统综述；59 项试验、12,981 人；高；少 23% | Cochrane 官方摘要：「Exercise reduces the rate of falls by 23%」，59 项研究、12,981 人，高可信度；人群 60 岁以上、居住在社区；只做抗阻练习的项目证据不足 | 数字、类型、样本量、可信度都对；结论句超出研究支持，见 B1。DOI https://doi.org/10.1002/14651858.CD012424.pub2 是正确的 DOI（页面被权限拦下，没能打开） |
| 长寿 | BJSM 2022；队列研究的系统综述（观察性）；7 项研究、263,058 人；很低；低 15%；30–60 分钟/周关联最强 | 原文 PDF：「Seven studies with 42 133 cases of all-cause mortality among 263 058 participants」，RR 0.85（95% CI 0.79–0.93）；「The overall quality of the evidence on all-cause mortality was rated as 'very low'」；剂量反应呈 J 形，最大降幅出现在每周约 30–60 分钟（全因死亡单看，最低点在每周约 40 分钟）。来源：https://observateperu.ins.gob.pe/sites/default/files/2025-02/755.full_.pdf ，二手转述 https://hospitalhealthcare.com/?p=25081 | 全部对。措辞用「有关」「is linked to」，符合观察性研究。建议把链接换成 DOI https://doi.org/10.1136/bjsports-2021-105061 （现在的出版方页面也合规，但被权限拦下，没能打开） |
| 情绪 | The BMJ 2024；随机对照试验的网状荟萃分析；218 项试验、14,170 人；力量训练这一项很低；中等幅度 | PMC10870815：「218 unique studies … 14 170 participants」；力量训练 g −0.49（−0.69 至 −0.29），和对照组比；纳入的是达到重度抑郁临床切点的人；「confidence … was low for walking or jogging and very low for other treatments」 | 数字、类型、可信度都对。还有两处缺：一是关键数字写的是「中等幅度」，不是数（技能要求有一个关键数字）；二是人群没写，原文是达到重度抑郁诊断标准的人，泛化成「情绪」偏宽。见 I3 |

研究卡在页面上都有「这些是人群研究的平均结果，不是对每个人的保证」；每页页脚都有「威利不是医生」，英文是「Veli isn’t a doctor」。另外，`npm run check:research` 还没交付（站点票 #52），这次没跑。

### 2.2 看清 · 里程碑（Mind 的 MILESTONES；States 里重复了前两条）

| 里程碑 | 年份 · 原文链接 | 结论 |
|---|---|---|
| 图灵《计算机器与智能》 | 1950 · OUP Mind 59(236):433 | 对（链接被权限拦下，没能打开） |
| 达特茅斯提案 | 1955 · jmc.stanford.edu PDF | 对：「人工智能」这个词公认是在 1955 年的提案里首次出现，研讨会在 1956 年夏天（https://www.phrases.org.uk/meanings/artificial-intelligence.html） |
| Rosenblatt 感知机 | 1958 · doi 10.1037/h0042519 | 对 |
| 反向传播 | 1986 · Nature 323:533 | 对 |
| LeCun 等 | 1998 · doi 10.1109/5.726791 | 对 |
| 深度信念网络 | 2006 · doi 10.1162/neco.2006.18.7.1527 | 链接对；「深的网络第一次训练得动」说过头了，见 S5 |
| ImageNet | 2009 · CVPR doi | 对 |
| AlexNet | 2012 · NIPS 摘要页 | 对 |
| Bahdanau 注意力 | 2014 · arXiv 1409.0473 | 对 |
| ResNet | 2015 · arXiv 1512.03385 | 对 |
| AlphaGo | 2016 · Nature nature16961 | 对：论文里打败的是职业二段樊麾 |
| Transformer | 2017 · arXiv 1706.03762 | 对 |
| 《苦涩的教训》 | 2019 · incompleteideas.net | 对：原文就写「70 years of AI research」 |
| Kaplan 规模定律 | 2020 · arXiv 2001.08361 | 对 |
| GPT-3 | 2020 · arXiv 2005.14165 | 事实对；「提示词工程由此而来」和同页范式表「2022–2024」矛盾，见 I8 |
| ReAct | 2022 · arXiv 2210.03629 | 对 |
| ChatGPT | 2022 · openai.com/index/chatgpt/ | 对 |
| 函数调用 | 2023 · openai.com 公告 | 对（2023 年 6 月） |
| o1 | 2024 · learning-to-reason-with-llms | 对 |
| MCP | 2024 · anthropic.com/news/model-context-protocol | 对 |
| Building effective agents | 2024 · anthropic.com/engineering/… | 链接对；「工程上的共识转向」是我们的理解，原文是 Anthropic 的建议，见 S6 |
| Claude Code | 2025 · Claude 3.7 Sonnet 公告 | 公告里确实首次发布了 Claude Code（研究预览），但标题写的是「Claude Code 与编程智能体」，链的是模型发布页，见 S7 |
| Manus 上下文工程 | 2025 · manus.im/blog/… | 链接存在（https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus）；「『上下文工程』成了通用的说法」把这个词流行起来归给了这一篇，见 S8 |
| Karpathy autoresearch | 2026 · github.com/karpathy/autoresearch | 存在。README：智能体改代码、每次训练 5 分钟、保留或丢弃；单张 NVIDIA GPU，一夜约 100 次实验，早上看实验日志。画板的说法对。仓库页面没显示提交日期，「2026 年 3 月」核对不到 |
| Addy Osmani《Loop Engineering》 | 2026 · addyosmani.com/blog/loop-engineering | 文章存在（站点首页能看到，地址带结尾斜杠 `/blog/loop-engineering/`）；日期 2026-06-07 核对不到（文章页被权限拦下）。建议把链接补上结尾斜杠 |

**年代分段**（1950–1979 / 1980–2011 / 2012–2016 / 2017–2022 / 2023–）：数据旁的注释自己写着「外壳样张里的那组，正式的由内容任务 T06 定」，术语表也说起止年份由内容票 #5 定。机器学习时代从 1980 年开始站不太住：1980 年代是专家系统（符号主义）商业化的高峰，从数据里学成为主流一般算在 1986 年反向传播之后，或者 1990 年代统计学习兴起之后。见 I6。

### 2.3 Article（Shopify 讲解）

对照原文 https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model 。作者 Zack Deveau，2026-07-29；评估约五个月；一次审计里 30 多个候选，验证后全部降为低、中危，或判为误报，或改记为纵深防御；分区占上下文窗口的 20–30%；80 多个应用、约六周、300 多个发现、2 个 Critical、保守估超过 40 万美元的等值赏金；Dispatch 是「a thin Ruby client」；9 个阶段的顺序也一致。**全部对**。授权写的是「讲解和摘要，不是全文翻译」，合规。仓库 `engineering.ts` 里这一篇的作者写成「Shopify Application Security」，和原文不一致，迁入时以原文为准。

### 2.4 学习路径（Learn）

CS50x、两门 DeepLearning.AI 专项课程、Agentic AI（四种模式：反思、工具调用、规划、多智能体，对）、Anthropic Academy（skilljar）、Zero to Hero、CS336（cs336.stanford.edu 存在）、CS25、autoresearch，说法都对。链接问题见 S11。小时数是估计，页面上写明了「我们的估计」，可以。

### 2.5 开发日志（Build、Project、Main、Article）

| 日志 | 引用 | 核对 |
|---|---|---|
| cold-review | 98a80d4 | 提交确实是「按冷评审改完 11 处」，但同一个提交里写着「基线 8 个失败的测试进前置票 #15」，没修完。标题「全部改完」说过头了，见 I10 |
| quality-terms | 3138a79 | 这个提交是「五个维度的对标和 46 条规则」；日志里的「对抗评审找出 8 类问题后重写」在 fc7fa5e，「一项自动检查」（check:vague）在 35ab42c，不在被引的这个提交里，见 I11 |
| two-reviewers | f1ad59f | 对：两份设计评审（Opus、Sonnet）互相看不到，另有一份内容评审 |
| home-motion | 53696b1 | 提交是「记录第 65、66 条：画板恢复叶与网动效」，可以 |
| one-domain | PR #1 | 错，见 B2 |

## 3. 重要

| # | 画板 · 位置 | 问题 | 建议 |
|---|---|---|---|
| I1 | Main · 研究卡 | F02 要求按第 5 节字段「全部显示」，字段里有「产品负责人看过的日期（首批必填）」，卡上没有；首批卡上线前也要在内容票 #9 里有产品负责人本人的回复 | 加一行「产品负责人看过：YYYY-MM-DD」，或者请 PRD 明确这个字段只记在数据里、不显示；#9 的回复在上线前核对 |
| I2 | Main · 三张卡的结论句 | 技能要求「数字写在句首」，三句的数字都在句尾 | 例：「少 23%：……」「低 15%：……」 |
| I3 | Main · 情绪卡：「力量训练让抑郁症状有中等幅度的减轻。」 | 关键数字不是数；没写人群和对照 | 关键数字写「g = −0.49」，或者「效应量 0.49（中等）」；句子改成「重度抑郁患者做力量训练，抑郁症状比对照组有中等幅度的减轻」，英文同义 |
| I4 | Main 的「最新文章」，对比 Mind 的 POSTS | 首页最新文章是 Shopify（2026-10-31），但看清列表里 Dan Koe 一篇的发布日期是 2026-11-04，更晚。这和 F03「按发布日期取最新」矛盾。仓库里 dan-koe 的 date 是 2026-01-12，那是原文日期 | 先定下五篇的发布日期（本站发布的日期），首页取最新的一篇，两块画板用同一份数据 |
| I5 | Mind · collabIntro：「每篇……文末有一个能自己动手验证的练习」 | 练习在 PRD 里是选填字段，现有文章（Dan Koe、Manus 等）不一定有，这是写不到的对外承诺 | 改成「有练习的文章，文末附一个能自己动手验证的练习」，或者删掉这半句 |
| I6 | Mind · ERAS 年代起止 | 是样张里的占位数（注释写着由 T06 定），却当成事实发布；1980 年开始机器学习时代也站不太住 | T06（#5）定稿前不能发布；建议机器学习时代从 1986 年或 1990 年起算，并在内容票里写明依据 |
| I7 | Mind · CARDS 的 pstack 链接是 theneuron.ai 的解读文章 | 二手报道，不是作者的官方地址 | 链官方：https://github.com/cursor/plugins/tree/main/pstack （出处 https://flaviocopes.com/pstack ）；「开源」两个字等核对许可证以后再写 |
| I8 | Mind · GPT-3：「提示词工程由此而来」，对比同页范式表「提示词工程 2022–2024」 | 同一页上自相矛盾 | 把范式表的「出现时间」改成 2020 年起，或者把里程碑的说法改成「为提示词工程打下基础」；PRD 第 5 节的表一起改 |
| I9 | Body · 一周安排的样张，对比「第一练只要 12 分钟」 | 热身 5 分钟加收尾 5 分钟，中间 3 个动作各 3 组，加上组间休息远超 12 分钟。图注和样张互相矛盾。另外这一页有动作和组数，是训练指导，按规矩要持证教练审 | 让样张和 12 分钟对上（例如每个动作 2 组、热身收尾各 2 分钟），交 Veli 的持证教练审核 |
| I10 | Main、Build、Project · cold-review 日志标题「……找出 11 处问题，全部改完」 | 基线里 8 个失败的测试转进了 #15，没修完 | 「……找出 11 处问题，10 处当场改完，1 处另开票」，英文同义 |
| I11 | Build、Project · quality-terms 日志 | 被引的提交 3138a79 不支撑「8 类问题」和「自动检查」 | 补引 fc7fa5e、35ab42c，或者把说法改成和 3138a79 一致 |
| I12 | Main、Article、States 英文的「Latest article」 | 术语表的英文是「Latest read」 | 改成「Latest read」；按钮可以保留「Read the latest article」，或者一起改 |
| I13 | Article · workoutLine：「威利已经排好了。」英文「Veli has it planned.」 | 主站 v1 不读登录状态，新用户并没有排好的训练，说过头了 | 「读完了，站起来练一练：去 Veli 开始今天的训练。」 |
| I14 | Build · 技能库的链接 `github.com/madlouse/velicoach/tree/feature/v1/.grok/skills` | feature/v1 是上线前的集成分支，上线后改走 site，这个地址会失效 | 链到默认分支，或者用不带分支名的稳定地址 |
| I15 | Article 的「接着读」（home-motion）：「首页动画为什么在设计稿里消失了」，对比 Build：「首页的『叶与网』动效回到设计稿里……」 | 同一条日志有两个标题，中英文都是 | 统一用一个标题 |

## 4. 建议

| # | 画板 · 位置 | 问题 | 建议 |
|---|---|---|---|
| S1 | Main · mindLead | 「：」后面藏了一个零宽空格（U+200B），Mobile、Tablet 也有 | 删掉，换行交给排版处理 |
| S2 | Build、Project 的 `gap`；States 的 whyTurn「为什么是转折　」 | 用全角空格排间距，违反第 6 节 | 间距交给样式 |
| S3 | Main、Mind 第一次出现「智能体」 | 术语表要求第一次写「智能体（agent）」 | 在首屏或第一次出现的地方补上 |
| S4 | Main 英文 bodyTitle、mindTitle 用了「See clearly」 | 口号可以用这个词，但「See clearly」在 stale-terms 清单里，进代码后 `check:terms` 会拦 | 在 allowed-phrases 里加上口号的写法 |
| S5 | Mind · 深度信念网络：「深的网络第一次训练得动」 | 说过头了：之前已经有能训练的深层网络 | 「逐层预训练让深层网络重新训练得动」 |
| S6 | Mind · Building effective agents：「工程上的共识从……转到……」 | 这是我们的理解 | 「Anthropic 建议先用最简单的搭法，而不是更全的框架」 |
| S7 | Mind · Claude Code 里程碑 | 链的是 Claude 3.7 Sonnet 的发布公告 | 标题注明「随 Claude 3.7 Sonnet 发布」，或者改链 Claude Code 的发布页 |
| S8 | Mind · Manus：「『上下文工程』成了通用的说法」 | 这个词 2025 年 6 月前后由多人带火，不只是这一篇 | 「让『上下文工程』流行起来的文章之一」 |
| S9 | SHELL 英文 subNote：「one workout」 | 邮件的「一练」不含训练动作 | 「one nudge to train」或者「one link to today’s workout」 |
| S10 | SHELL 中文 errRate：「提交太频繁，一小时后再试」 | PRD 细则第 6 条的原文是「提交太频繁，请一小时后再试」 | 照 PRD 写，或者改 PRD |
| S11 | Learn · Agentic AI 的链接 `/alpha/courses/agentic-ai`；Mind · Matt Pocock 的链接 claude.com/plugins | alpha 是测试路径；插件页不是作者的官方地址 | 改为 https://www.deeplearning.ai/courses/agentic-ai 、https://github.com/mattpocock/skills |
| S12 | About 英文 lead：「the more it pays to stand firm first」 | 和首页的「Get strong」不一致 | 「The faster AI moves, the more it pays to get strong first.」 |
| S13 | Main · 站稳一行：「身体撑得住其他所有事」 | 接近绝对化的承诺 | 「身体撑得住，别的事才做得下去」 |
| S14 | Article 英文 kicker：「Easy to mishear」 | 照「容易听错」直译，英文读者看不懂 | 「Common misreading」 |
| S15 | Body 英文：「“2 more reps than last week”.」 | 美式标点要把句号放进引号 | 「… last week.”」 |
| S16 | Body 英文的「Start with Google」，对比 Main 的「Start training with Google」 | 同一个按钮两种写法 | 统一用一种 |

## 5. 语气、健康表述和虚词

- 没有保证疗效的说法（只有 S13 偏绝对）；研究卡下面有群体平均的说明，每页页脚有「威利不是医生」。观察性研究那张卡只用了「有关」「linked to」。
- 拿 `scripts/vague-terms.mjs` 跑了九块画板的中文字符串：没有命中。可见文字里没有「适当」「尽量」「优化」「打磨」。「值得读」只用在「我们的判断」这个结论里，不是验收用语，可以保留。
- 没有占位符、「待定」「示例」「即将上线」、口头禅或登记过的转写错误。英文页面里只有语言切换的「中文」和原文图里不译的英文，没有中文正文。
- 英文整体是按英语读者重写的，句子短，不是逐句直译；例外见 S14。

## 6. 没改动、可以保留的

Article 正文里 Shopify 的数字，Learn 各步「怎么检验」的写法，About「谁在维护」的四项，以及订阅和状态页的文案：都核对过，可以保留。
