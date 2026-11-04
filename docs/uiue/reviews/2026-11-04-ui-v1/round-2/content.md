# 关口三 a 第 2 轮 · 内容评审（画板文字，中英两版）

评审人：content-reviewer（冷评审，没看过制作过程）· 2026-11-04
材料：`canvas2/project/*.dc.html`（标签文字，以及 `renderVals` 和顶层 `COPY` 里会渲染到页面上的中英字典、数据数组）；截图 `shots-r2/`（抽看了 Main 英文、Article 暂无英文版、States 加载中）。
规则：quality-terms C1–C9、T1–T10；`docs/GLOSSARY.md`；PRD 快照第 4、5、12 节；`velicoach-content`。
上一轮：`../content.md`。

## 结论：要改

阻塞 13 条（B1–B13），建议 10 条（N1–N10）。可信度低于 80 的发现没有列出。Controls 是设计系统的控件状态板，不是对外页面，只查了有没有错字，没有按对外文字审。

上一轮的 18 条（含 G1）：已修 9 条，部分修 4 条，没修 5 条。新发现里最重要的是三处：站稳的 BJSM 卡片把五种结局合在一起的「10–17%」写成了全因死亡（B2）；原生 App 还没上架，页面就放了 App Store、Google Play 下载（B3）；Shopify 原文仍然打不开，文章页所有数字都还没核对（B1）。

## 一、上一轮问题的处理情况

| # | 上一轮的问题 | 这一轮 | 说明 |
|---|---|---|---|
| S1 | 文章页数字无法核对，页脚缺作者 | **没修** | 原文仍然打不开（见第二节）；页脚仍只写刊名，没有作者。转入 B1 |
| S2 | 「吸引力」研究卡 | 已修 | 换成 Cochrane 渐进抗阻训练与步速，研究类型、试验数、人数齐全 |
| S3 | 抑郁卡超出研究、缺样本量 | 已修 | Body、Main 都写了 g = −0.49、218 项、14,170 人和「证据确定性很低」；「年轻女性」已删 |
| S4 | Main 页脚写「Veli 不是医生」 | 已修 | 中文页全部是「威利不是医生」 |
| S5 | 「即将上线」 | **部分修** | 词已经没有了，但 Body 仍在预告睡眠和饮食（B4）；另有还没上架的 App 下载入口（B3） |
| M1 | 导语焦虑式说法 | 已修 | 「力量训练的好处有很多研究支持……写明了研究类型和样本量」 |
| M2 | 威利 / Veli 混用 | **部分修** | 中文页主语都改成「威利」；第一次出现时的一句说明仍没有（B12） |
| M3 | 「测试预言」没解释 | 已修 | 「用测试判定结论真假的『测试预言』（test oracle）」；但这一句变成 55 字（B9） |
| M4 | Harness 没有白话 | 已修 | 导语里加了「Harness 指套在模型外面的那层软件」 |
| M5 | 「分区」意思不明 | **没修** | 中英两版都还在（partitions），原文仍无法核对。转入 B9 |
| M6 | 判断缺代价、「往往」 | 已修 | 加了代价一句，「往往」改成「可能」 |
| M7 | 两句超过 40 字 | **没修** | 原句未动。转入 B9 |
| M8 | 划船「不需要器械」 | 已修 | 换成臀桥；「各三组」与别处「3 组」写法仍不一，教练审核记录没有看到（N8） |
| N1 | 「~」写法 | 已修 | 改成「−10–17%」，但这个数本身错了（B2） |
| N2 | 中文页夹 builder | **没修** | Build「一个 builder 的一周」仍在（N5） |
| N3 | Mobile 按钮少动词 | 已修 | 这个入口已经不在首页文案里 |
| N4 | 「带去动手」「Critical」 | **没修** | 两处原样（N5） |
| G1 | 没有英文版 | 已修 | 9 块对外画板都有英文；残留问题见 B5、B7、B11、N6 |
| 出处表 | 没有原句摘录和查询日期 | **部分修** | 每张研究卡、里程碑、学习路径都链到了原文；原句摘录和查询日期仍不在任何地方。下面第二节的表可以直接用作出处表的初稿 |

## 二、事实和出处核对（T1）

查询日期都是 2026-11-04。WebFetch 只能打开搜索结果里出现过的地址，其他地址的权限请求超时；`curl` 被出口代理拒绝（所有地址返回 000）。打不开的照实写。

| 位置 | 画板上的说法 | 核对结果 |
|---|---|---|
| Article 全文 | Shopify Engineering《Building an agentic harness that outlasts the model》：约五个月、30 多个候选、六周、80 多个应用、数千次、300 多个发现、2 个 Critical、超过 40 万美元、Dispatch 是 Ruby 客户端、2026-07-29、引语「模型会换。Harness 留下。」 | **打不开**。WebFetch 的权限请求超时，curl 被代理拒绝。所有数字、日期、引语，以及「分区」对应的原词，都**没有核对过**。引语用了 `blockquote`，看起来像原文引语，是不是原文的话也无法确认 |
| Main · WHO 2020 | 每周至少两天、中等强度以上、全身主要肌群；强推荐 · 证据可信度中等 | 一致。NCBI Bookshelf NBK566048（WHO Guidelines on Physical Activity and Sedentary Behaviour, 2020）：「Adults should also do muscle-strengthening activities at moderate or greater intensity that involve all major muscle groups…」，标注「Strong recommendation, moderate certainty evidence」。画板链接的 who.int 页面没打开 |
| Main · BJSM 2022 | 全因死亡风险低 15%；每周 30–60 分钟时关联最强；7 项研究、263,058 人；观察性，证据可信度很低 | 一致。bjsm.bmj.com/content/56/13/755：「Sixteen studies met the eligibility criteria」；全因死亡 RR 0.85（95% CI 0.79–0.93）；「Seven studies with 42 133 cases of all-cause mortality among 263 058 participants」；「The overall quality of the evidence on all-cause mortality was rated as 'very low'」；30–60 min/week 时风险下降最多 |
| Body · BJSM 2022 | 「全因死亡风险低 10–17%」，大数字「−10–17%」，只写「16 项前瞻性队列研究」 | **不一致**。原文的 10–17% 是全因死亡、心血管病、总癌症、糖尿病、肺癌五种结局合起来的范围；全因死亡单项是 15%。见 B2 |
| Body · Cochrane 跌倒 | 2019 · 59 项随机对照试验、12,981 人 · 高确定性，跌倒次数少 23% | 一致。PEDro 收录的同一综述摘要（Sherrington 等，BJSM 2020 版）：「Exercise reduces the rate of falls by 23% (rate ratio (RaR) 0.77, 95% CI 0.71 to 0.83; 12,981 participants, 59 studies; high-certainty evidence)」。画板链接的 PubMed 30703272 没打开 |
| Main、Body · Cochrane CD002759 | 2009 · 121 项试验、约 6,700 人；步速 +0.08 m/s（24 项、1,179 人）；力量明显提高 | 一致，**年份 2009 是对的**。Cochrane Library 版本历史只有两版：2003-04-22（CD002759）和 **2009-07-08（CD002759.pub2）**，没有 2022 年的更新版。cochrane.org 的摘要页写着「Cochrane Database of Systematic Reviews 2022, Issue 4 … CD002759.pub2」，这是同一个 pub2 在 2022 年重新发布，内容还是 2009 年那一版（编者注：检索做到 2008 年 5 月）。原句：「One hundred and twenty one trials with 6700 participants were included」；「(24 trials, 1179 participants, MD 0.08 m/s, 95% CI 0.04 to 0.12)」；「PRT had a large positive effect on muscle strength」 |
| Main、Body · BMJ 2024 | 218 项试验、14,170 人；力量训练 g = −0.49；力量训练证据可信度很低 | 一致。jyx.jyu.fi 收录的摘要：「218 unique studies with a total of 495 arms and 14 170 participants」；「strength training (n=643, κ=22, g −0.49, −0.69 to −0.29)」；「confidence … was low for walking or jogging and very low for other treatments」 |
| Mind · 1950 图灵 | academic.oup.com/mind/…/986238 | 年份、出处一致（Mind, LIX(236), 433）；链接没打开 |
| Mind · 1955 达特茅斯提案 | jmc.stanford.edu/…/dartmouth.pdf | 年份一致（提案日期 1955-08-31，「artificial intelligence」一词出自提案）；链接没打开。States 写成 1956，见 B6 |
| Mind · 1986 反向传播 | nature.com/articles/323533a0 | 年份、出处一致（Rumelhart、Hinton、Williams，Nature 323）；链接没打开；画板上没写作者（N4） |
| Mind · 2012 AlexNet | papers.nips.cc/…/c399862d…-Abstract.html | 链接对应的就是《ImageNet Classification with Deep Convolutional Neural Networks》，NeurIPS 2012（搜索结果核对）；没写作者（N4） |
| Mind · 2017、2019、2020、2022、2024 | arXiv 1706.03762；Sutton《The Bitter Lesson》；arXiv 2001.08361；openai.com/index/chatgpt；learning-to-reason-with-llms | 年份和地址与已知原文一致；这一轮都没打开 |
| Mind · 2025 智能体 | anthropic.com/news/claude-3-7-sonnet；一句话提到 Claude Code 和 Codex | 链接是 Claude 3.7 Sonnet 和 Claude Code 的发布公告，没有打开；Codex 不在这个出处里（N3） |
| Mind · 学习路径 9 个链接 | CS50x、ML Specialization、提示词工程交互教程、ChatGPT Prompt Engineering for Developers、Building effective agents、Agentic AI、Zero to Hero、nanoGPT | 都没打开（代理拒绝，WebFetch 超时）。Agentic AI：搜索结果里的官方地址是 `deeplearning.ai/alpha/courses/agentic-ai`（PRD 也用这个），画板写的是 `deeplearning.ai/courses/agentic-ai/`，能不能打开无法确认，上线前要点开核对。时长页面已注明「是我们的估计」 |

## 三、阻塞项

| # | 画板 · 位置（原文摘录） | 规则 | 为什么 | 改法 | 可信度 |
|---|---|---|---|---|---|
| B1 | Article 正文和页脚全部数字；页脚「原文：Building an agentic harness that outlasts the model，Shopify Engineering，2026-07-29，英文。本站是学习整理，版权归 Shopify。」；引语「模型会换。Harness 留下。」 | T1、T5；技能 §8 阻断「数字找不到出处」 | 这一轮原文仍然打不开，正文里没有一个数字核对到原句。页脚仍没有作者名。引语排成 `blockquote`，读者会当成原文的话，是不是原话也没法确认。T5 还缺「能不能转载、怎么引用」 | 由能打开原文的人逐条摘原句，写进出处表（原句 + 查询日期）；核对不上的数字删掉。页脚改成「原文：《Building an agentic harness that outlasts the model》，<作者>，Shopify Engineering，2026 年 7 月 29 日，英文。本页是学习整理，不转载原文；引用请链到原文。」引语如果不是原话，去掉 `blockquote`，改成正文里的一句我们的话 | 90 |
| B2 | Body ·「给以后的自己」：大数字「−10–17%」；「做力量训练的人，全因死亡风险低 10–17%；每周 30–60 分钟时下降最多。」出处「BJSM 系统综述，2022 · 16 项前瞻性队列研究」（英文同） | T1、T8；技能研究卡片验收「数字能在原文里找到」 | ① 10–17% 是五种结局合起来的范围，全因死亡单项是 15%（RR 0.85）。首页同一项研究写的是 15%，两页对同一个结论给了两个数。② 没写样本量（全因死亡 7 项研究、263,058 人）。③ 没写证据可信度，原文评为「very low」，而且都是观察性研究。首页三项都写了 | 大数字「−15%」；结论「做力量训练的人，全因死亡风险低 15%；每周 30–60 分钟时关联最强。」出处「BJSM 队列研究的系统综述，2022 · 全因死亡 7 项研究、263,058 人 · 观察性关联，证据可信度很低」。英文同改：「People who did muscle-strengthening activity had a 15% lower risk of death from any cause, most strongly at 30–60 minutes a week.」 | 92 |
| B3 | Body 首屏「在手机上」：App Store、Google Play 两个按钮；「扫码在手机上下载 Veli」「用手机相机扫一扫，下载 App」。Main、Tablet、Fold、Mobile「在手机上」：「iPhone 打开 App Store，安卓打开 Google Play。」（英文同） | PRD 第 4 节「Veli 的入口」；`trace.md` 第 51 条；T10「还没上线的功能不在对外页面出现」 | PRD 写明「原生 App 上架前，手机上不推荐下载，第一次训练结束后提示『添加到主屏幕』」，原生 App 在 B2 才上架。现在的画板把还没有的商店入口放在首屏，用户扫码会落空 | 上架前：二维码改成「扫码在手机上打开 Veli 网页版」，说明改成「用手机相机扫一扫，直接在手机上开始」；去掉两个商店按钮和「下载」。上架后再按设备只显示对应的商店按钮 | 88 |
| B4 | Body ·「练什么」导语：「睡眠和饮食以后会加进同一个计划，还是同一位威利。」英文「Sleep and nutrition will join the same plan later, with the same Veli.」 | T10；技能 §4「对外只放正式版」；`AGENTS.project.md` 第 1 条 | 「即将上线」换了说法还是在预告没上线的功能（PRD：睡眠、饮食 v2 开始） | 删掉这一句。导语只留「先把三个基本动作练稳，再慢慢加重量。」 | 85 |
| B5 | States 英文版：内容线「AI history」「Working with agents」；分组名「Series」；标题「Milestones that changed course」 | C3、C7；术语表 | 术语表的英文是 History of AI、Human–AI collaboration；Mind 画板写的是这两个，加上「Content lines」「Milestones that changed the road」。同一个页面在两块画板上叫法不一样 | States 英文全部照 Mind：「History of AI」「Human–AI collaboration」「Content lines」「Milestones that changed the road」 | 90 |
| B6 | States 里程碑：「1956 · 达特茅斯会议 ·『人工智能』这个名字诞生……」；英文「1956 · The Dartmouth workshop · The name “artificial intelligence” was coined…」 | T1、C3 | 这个词出自 1955 年 8 月的提案，不是 1956 年的会议。Mind 画板写的是「1955 · 达特茅斯人工智能提案」，两块画板的年份和事件也不一致 | 照 Mind：「1955 · 达特茅斯人工智能提案 ·『人工智能』这个名字第一次写进文献……」 | 85 |
| B7 | Article「暂无英文版」状态：「We wrote this piece in Chinese. … Below are our Chinese summary and other English articles from the same line.」 | PRD 第 4 节页面状态「文章暂无英文版：显示中文正文，开头写『这篇还没有英文』」；C5 | 截图上，下面只有一个「Read the Chinese summary」链接和两篇别的文章，没有中文正文。文案说「Below are our Chinese summary」不是事实，做法也和 PRD 不一样 | 二选一：照 PRD，在这段说明下面直接显示中文正文，说明改成「This piece is only in Chinese for now. The Chinese text is below, or read the original post in English.」；或者保留现在的做法，先改 PRD，并把这句改成「Read the Chinese summary, or try other English articles from the same line.」 | 85 |
| B8 | Mind 人机协作列表、Article「接着读」、Article 暂无英文版列表：《Claude Code 团队如何做 Code Review》标为「Loop 工程 / Loop engineering」 | PRD 第 5 节「线二」表；C3 | PRD 把「Claude Code 团队的代码审查」放在 Harness 工程这一行的首批内容里。画板标成 Loop 工程，读者按层筛选时会找错地方 | 改成「Harness 工程 / Harness engineering」；如果确实该放 Loop 工程，先改 PRD 的表，再改画板，在 `trace.md` 记一笔 | 82 |
| B9 | Article 正文：p1 第一句 55 字、第二句「它在软件里找漏洞……然后才交给开发者」55 字；p5「约六周内……记为 Critical」53 字；p2「一次审计中……纵深防御」42 字；p3「循环、工具、分区、证明和确定性脚本」（英文「partitions」） | C1；C3 | 上一轮 M5、M7 没改，M3 改了以后又多出一句 55 字的。「分区」仍然看不出指什么 | 拆句，例如：「Shopify 应用安全团队做了一套用智能体审代码的系统。它配了一种『测试预言』（test oracle）：用测试判定一条结论是真是假。」「它先在软件里找漏洞，再用真实的集成测试证明漏洞能被利用。之后给出符合 Shopify 代码习惯的修复，最后才交给开发者。」「约六周内，扫描覆盖了 80 多个应用，执行了数千次，产出 300 多个发现。其中 2 个按内部分级属于最高的『严重』（Critical）。」「分区」等原文能打开后换成说出作用的词，核对不了就删掉 | 85 |
| B10 | Mind 人机协作列表《比模型更耐久的 Harness》日期「2026-07-29」；Main「人机协作的最新三篇」「07-29」 | T3；C3 | 文章页的更新记录写「2026-10-31 发布」，2026-07-29 是 Shopify 原文的日期。列表里别的文章都是我们发布的日期，这一篇用了原文日期，排序和「最新三篇」都会错 | 列表统一用我们的发布日期：「2026-10-31」「10-31」；原文日期只放在文章页的元信息里 | 82 |
| B11 | 英文标题：Article、Mind「A harness that outlasts the model」，Main 本周卡片和「Continue:」写「The harness that outlasts the model」；Mind「Super-agent: hiding the sessions behind one conversation」，Main「Super-agents: hiding the session」 | C3（一个东西一个叫法）、C7 | 同一篇文章在三块画板上有两个英文标题，读者会以为是两篇 | 以文章页标题为准：「A harness that outlasts the model」「Super-agent: hiding the sessions behind one conversation」，Main 同改（含「Continue: A harness that outlasts the model」） | 85 |
| B12 | Main 首屏「威利提前排好……」、Body 首屏「威利提前排好……」：两页都没有说威利是谁 | 术语表「例外」：Velicoach、Veli 第一次出现时带一句说明；C3 | 第一次来的人看不出威利是人、是教练还是 App。只有 Build 写了「力量训练的教练兼管家」 | Body 导语：「威利是 Veli 的 AI 力量训练教练。它提前排好什么时候练、在哪练、练什么，你只需要到场。」英文「Veli is an AI strength coach. It plans when, where, and what you train ahead of time. You just show up.」Main 首屏字数紧，可以在首次出现处加同样的一句，或在「先站稳」的说明里写「AI 教练威利」 | 80 |
| B13 | Mind · 学习路径表：每一步只有名称、来源、形式、时间、「学会了是什么样」 | PRD 第 5 节「学习路径步骤」必填字段；技能「学习路径步骤」验收（为什么学、能说出前置步骤） | 必填的「为什么学」每一步都没有；前置步骤只能靠表格顺序猜 | 每一步加一句「为什么学」，例如 CS50x：「后面每一级都要写代码，这门课把编程的底子打好。」并在第 2 级起每级标出「先学完第 N 级」 | 85 |

## 四、建议项

| # | 画板 · 位置（原文摘录） | 规则 | 为什么 | 改法 | 可信度 |
|---|---|---|---|---|---|
| N1 | Main「力量训练和健康：四项研究」，第一张是 WHO 2020 指南 | T8；C3 | 指南不是研究，也没有样本量；标题和内容对不上 | 「力量训练和健康：一份指南，三项综述」，或者「四条证据」 | 82 |
| N2 | Main AI 发展史最新三篇：「规模定律：大就是不一样」「Scaling laws: bigger is different」 | T1；技能研究卡片「结论不超出研究」 | 「大就是不一样」让人想到涌现（More is different），Kaplan 2020 讲的是性能随规模按幂律可预测地变好，Mind 画板也是这么写的 | 「规模定律：越大，越可预测地变好」「Scaling laws: bigger is predictably better」 | 80 |
| N3 | Mind 2025：「Claude Code、Codex 这类编程智能体……」，链接 Claude 3.7 Sonnet 公告；中文这一句 43 字 | T1；C1 | Codex 不在这个出处里；句子超过 40 字 | 「Claude Code 这类编程智能体自己调用工具、检查结果。它们能把一件事从头做完。」要提 Codex 就另附 OpenAI 的出处 | 80 |
| N4 | Mind 里程碑 1986、2012、2017、2020 只有事件名，没有作者 | T1「写明作者」 | 1950、2019 写了作者，其余没写 | 「Rumelhart、Hinton、Williams《Learning representations by back-propagating errors》」，AlexNet 写 Krizhevsky、Sutskever、Hinton；2017 写 Vaswani 等；2020 写 Kaplan 等 | 82 |
| N5 | Build「一个 builder 的一周」「builder 不是职业……」；Article 按钮「带去动手」；Article「记为 Critical」 | C3、C4、U5 | 上一轮 N2、N4 没改。builder 在 PRD 第 5 节里也出现过，但术语表没有 | 先在术语表定 builder 的叫法再用，或改「动手的一周」；按钮「投稿你的结果」；「最高一级的『严重』（Critical）」 | 80 |
| N6 | 同一个东西多种叫法：订阅邮件「每周日一封邮件」（Main）/「每周日一封信」（Build、Article）/「A letter every Sunday」/「One email every Sunday」；英文页脚「Health data」（Main、States）/「Health data policy」；导航 aria「Stations」/「Sections」；免责「Veli isn’t a doctor … see one」/「Veli is not a doctor … see a doctor」；阅读时长 Article 英文「9 min read」，Main 英文卡片「12 min」 | C3 | 一个概念一个词；同一篇文章的阅读时长在两处不同 | 中文统一「每周日一封邮件」（术语表：订阅），英文「One email every Sunday」；页脚统一「Health data policy」；aria 统一「Stations」；免责统一「Veli isn’t a doctor. If you’re injured or in pain, stop and see a doctor.」；英文阅读时长两处一致 | 82 |
| N7 | Main BJSM 卡：标签「16 项队列研究」，下面又写「7 项研究、263,058 人」 | C1；T1 | 读者看不出 16 和 7 的关系 | 标签「BJSM 2022 · 队列研究综述」，说明「全因死亡：7 项研究、263,058 人 · 观察性关联，证据可信度很低」 | 80 |
| N8 | Main 本周一练「深蹲、俯卧撑、臀桥，各三组……不需要器械」；Body「练什么」是深蹲、俯卧撑、划船（哑铃或水瓶） | T8；技能 §6 数字 | 两页都叫「第一练」，动作不一样；训练指导要有持证教练审核记录，这一轮没看到；「各三组」与别处「3 组」写法不一 | 两页的第一练用同一组动作；「各 3 组」；审核记录贴在 #14 | 80 |
| N9 | Main「为什么是现在 · AI 走得越快，越要先站稳」 | T1；T9 | 下面四张卡都讲力量训练和健康，没有一张支持「AI 越快越要练」；这一句是品牌口号，放在研究卡片上方，像是研究得出的结论 | 标题改成不需要证据的说法，例如「先站稳：力量训练的四条证据」；口号留在首屏 | 80 |
| N10 | Mind 学习路径四级：基础、用好大语言模型、智能体、深入模型 | 冲突时以谁为准：PRD > 设计决定 | PRD 第 5 节是基础、智能体、模型、前沿；`docs/uiue/decisions.md` 改成了现在的四级，PRD 没有跟着改 | 以产品负责人的意见为准，改低的一方，在 `trace.md` 记一笔 | 80 |

## 五、查过、没有问题的地方

- **英文版**：9 块对外画板都有英文，按英语读者重写，没有逐句直译的痕迹（例如「Days off are just nodes: no penalty, no lost leaves.」）。美式拼写；标题 sentence case；列表用 serial comma（「when, where, and what」「usable, clear, good-looking, trustworthy, and comfortable」）。英文页上的中文只有语言按钮「中文」「中」，属于例外。没有 leverage、empower、journey 这类词。
- **页面状态**：订阅（填写、正在订阅、成功「去邮箱点一下确认，就订好了」、失败「这个邮箱地址不完整，看看 @ 后面是不是少了一段」）、离线、页面不存在（说明原因，给搜索和三站入口）、内容加载失败（说明其余部分不受影响，给重试和学习路径）、加载中、文章加载失败（给重试和原文）、视频无法播放（给文字稿），都说清了发生了什么、接下来能做什么。只有「暂无英文版」有问题（B7）。
- **健康内容**：所有带页脚的对外画板都有「威利不是医生」/「Veli isn’t a doctor」；研究卡片都写了研究类型和年份；除 B2 以外都写了样本量；抑郁卡写明证据确定性很低；没有讲身材的说法。
- **只放正式版**：没有「即将上线」「示例」「待定」「TODO」；States 的「画板说明」放在页面框外的说明条里，不算页面文字。
- **术语**：术语表「不再用的说法」清单里的词，在对外文字里一个都没有出现（「See clearly」只用作口号，不作站名，术语表允许）。

## 六、核对不了的地方（不是发现，上线前补）

- Shopify 原文（见 B1）。
- 画板链接的 who.int、PubMed 30703272、PubMed 19588334、PMC10870815、doi.org/10.1136/bmj-2023-075847 没有直接打开，用同一项研究的其他官方页面核对了数字；上线前要点开每个链接确认能打开。
- 学习路径的 9 个链接、里程碑的 9 个链接都没打开（代理拒绝）。
- 6 个里程碑和人机协作的 5 篇文章都标了「3 分钟视频」，这一轮只确认文章页有一个；其余视频要是还没做，标签要先去掉（T10）。
