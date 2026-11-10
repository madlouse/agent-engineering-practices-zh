# 苹果与迪士尼的体验设计思想：可复用原则

调研日期：2026-11-05。范围：网页 GUI，以及人与 AI Agent 一起做事的界面。每条结论都附出处；引用的原文不超过 15 个字，其余是转述。

## 0. 结论

1. **苹果的「现行原则」已经换过一次。** HIG 在 2026-06-08 重新发布了 8 条设计原则：Purpose、Agency、Responsibility、Familiarity、Flexibility、Simplicity、Craft、Delight。Hierarchy、Harmony、Consistency 是 2025 年随 Liquid Glass 提出的三条，已经不是现行版本。2014 年的三个主题（Deference、Clarity、Depth）和六条原则（Aesthetic integrity、Consistency、Direct manipulation、Feedback、Metaphors、User control）是更早的一版。三版说法不同，不变的内核有四条：内容优先、用户掌控、反馈即时、沿用熟悉的约定。
2. **做 Agent 界面，现成最完整的规则在苹果的 Generative AI 和 Machine learning 两页 HIG 里。** 要点包括：标明哪里用了 AI；生成结果旁边放编辑、撤销、重试；进度文案写清正在做什么；不可逆的动作先征得同意；置信度转成能照着做的话；置信度低时不主动推送。我们的 `quality-terms.md` 里还没有这一类规则。
3. **「零步」「步数最少」是神话。** Apple Pay 用了 Face ID 以后，苹果有意加了一步「双击侧键」来确认付款意图。迪士尼在 2024 年把 Lightning Lane 改成入园前预订，理由是游客不想在游玩当天做规划。两家真正的做法是：去掉不承载意图的步骤，把负担挪出关键时刻。要的不是点按次数最少。
4. **迪士尼可以借的是「有序的取舍」和「等待设计」，不是「沉浸」。** Four Keys 给冲突时的决策排了先后（安全在礼貌之前）。等待体验背后的心理学（Maister）可以直接用到 Agent 的长任务上。主题乐园的沉浸感靠的是藏起外部世界、操纵尺度感，搬到工具类产品上就成了隐藏系统状态和暗黑模式。
5. **对我们原则最需要挑战的一条**是 U1 和 `velicoach-layout` §3 的「超出预算就改设计，不改预算」。现在只数点按次数：确认意图、同意、不可逆前的确认被当成要消灭的成本，「感知负担」和「出错代价」不进账。详见 §5。

## 1. 方法与来源

- 一手来源：Apple HIG（用 `.md` 版本读取）、Apple Newsroom、WWDC 讲座（文字稿来自 nonstrict.eu 收录的官方视频）、Apple 白皮书（经 Daring Fireball 转引）；Disney Parks Blog、D23、Walt Disney Family Museum；Maister 的原文；Lasseter 1987 年的 SIGGRAPH 论文。
- 权威二手：Nielsen Norman Group、Touring Plans（多年等候时间数据）、Theme Park Insider、TidBITS、MacRumors、Fast Company。
- **没读到的页面**（权限请求超时或页面报错，结论没有用到它们的正文）：
  - HIG 首页、Materials 页的 HTML 版
  - Liquid Glass 新闻稿的第一次请求（第二次成功）
  - Disney Institute 博客文章《Why Courtesy Is Not Always Our First Priority》（只用了它的标题）
  - Disney Institute 博客首页（需要 JavaScript）
- 迪士尼的 Imagineering 内部文件不公开。「Mickey's Ten Commandments」「onstage/backstage」等说法只查到转引，下文逐条注明证据强度。

---

## 2. 苹果

### 2.1 核心思想（7 条）

结论：苹果三版原则的共同内核是「界面退后、内容向前；用户随时掌控；每个动作立刻有回应」。Liquid Glass 是把这个内核做成材质的最新一次尝试，在可读性上付了代价。

| # | 一句话原则 | 要解决的问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| A1 | **内容优先，控件是浮在内容上的一层** | 界面装饰和内容抢注意力 | 导航和控件集中在一层，悬浮在内容之上；内容层不用玻璃；着色只给主操作；不叠玻璃 | 2014 年 HIG 的 Deference（[iOS HIG 2014 镜像](https://www.evl.uic.edu/datsoupi/420_14/docs/MobileHIG.pdf)）；[Liquid Glass 新闻稿](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/)称控件是一层 "functional layer"；[WWDC25《Meet Liquid Glass》](https://nonstrict.eu/wwdcindex/wwdc2025/219/)："glass on glass" 要避免，颜色放进内容层 |
| A2 | **层级靠结构，不靠装饰** | 用户不知道自己在哪、下一步是什么 | 主次一眼可见；常用的放在最上层，高级的默认收起；一个视图最多一个展开按钮 | [HIG 设计原则 · Simplicity](https://developer.apple.com/design/human-interface-guidelines/design-principles.md)（Establish hierarchy）；[HIG Disclosure controls](https://developer.apple.com/design/human-interface-guidelines/disclosure-controls.md) |
| A3 | **和硬件、系统协调（同心）** | 软件和设备、窗口的形状各说各话 | 嵌套元素的圆角同心，贴合窗口和屏幕的圆角 | 新闻稿："perfectly concentric"；《Meet Liquid Glass》谈 concentricity |
| A4 | **用户掌控，能探索、能反悔** | 用户怕点错，不敢动 | 引导流程能跳过、能退出；操作可撤销；不锁进模式；破坏性操作先确认 | 2014 年 HIG 的 User Control；[2026 HIG · Agency](https://developer.apple.com/design/human-interface-guidelines/design-principles.md)（Help people recover from mistakes） |
| A5 | **响应即时、可打断、跟手** | 界面「卡」「黏」，和手不同步 | 点按也要查延迟；手势中途能改方向；拖动 1:1 跟手；松手按速度推算落点；从哪来回哪去 | [WWDC18《Designing Fluid Interfaces》](https://nonstrict.eu/wwdcindex/wwdc2018/803)（Karunamuni、Alonso、de Vries）；[HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion.md)：Let people cancel motion |
| A6 | **默认值做对，能推断的不问** | 设置太多、上手要先配置 | 默认就适合大多数人；能检测的（深色模式、外接设备）不问；和任务相关的选项放在任务里，不进设置页 | [HIG Settings](https://developer.apple.com/design/human-interface-guidelines/settings.md)：开篇就说人们期望应用 "just work" |
| A7 | **少而好，不是极简** | 把「少」误解成「什么都藏起来」 | 每个元素都有存在的理由；重要的放在手边；不把装饰当成惊喜 | [Vitsœ：Rams 十条](https://vitsoe.com/us/about/good-design)（Less, but better）；HIG Simplicity 明说简单不是极简（"isn't minimalism"）；HIG Delight："Don't mistake delight for decoration" |

补充两个常被提到的点：

- **「It just works」**：出自 2011 年 WWDC 上乔布斯介绍 iCloud（[TechCrunch](https://techcrunch.com/?p=311653)）。它是发布会口号，不是设计原则。能落到设计上的版本是 HIG Settings 里的「默认值让大多数人不用调」。
- **Dieter Rams 对苹果的影响**：能核实的一手关联是 Jony Ive 为 Phaidon 出版的 Rams 作品集写了序（[Phaidon](https://www.phaidon.com/en-gb/products/dieter-rams-as-little-design-as-possible)）。Vitsœ 的原则页没有提到苹果。具体产品之间的「传承」大多来自媒体和粉丝的比对，本次没有找到苹果官方的说法。

### 2.2 能直接用在网页或 App 上的规则

结论：苹果给的大多是方向，下面把它们写成能判对错的规则。数值标了来源，没有数值来源的写「自定」。

| 规则 | 怎么判 | 为什么 | 出处 |
|---|---|---|---|
| R1 每个可点元素按下后 100ms 内有视觉变化 | 录屏或 Playwright trace，看按下到第一帧变化的时间 | 0.1 秒是「感觉即时」的界限；苹果说点按也要查延迟 | [NN/g 响应时间](https://www.nngroup.com/articles/response-times-3-important-limits/)；WWDC18 803 |
| R2 任何过渡动画播放时，新的输入立刻生效，不等动画播完 | 在动画中途点返回或另一个入口，结果应该直接去新目标 | 让人等动画，重复几次就会烦 | HIG Motion：Let people cancel motion；WWDC18：redirectable |
| R3 拖动时，元素和指针的相对位置不变 | 拖动过程中截几帧，量指针到元素锚点的距离 | 1:1 跟手才有直接操作的感觉 | WWDC18（Alonso） |
| R4 浮层从哪里出现，就回到哪里 | 对比打开和关闭两条动画的路径 | 空间一致，用户才不迷路 | WWDC18（spatial consistency） |
| R5 反馈动画 100–300ms，大范围移动不超过 400ms；进入比退出长；高频操作不加自定义动效 | 读 token 里的时长；列出高频控件 | 超过 500ms 就拖沓；看得越多，动画越该短 | [NN/g 动画时长](https://www.nngroup.com/articles/animation-duration/)；HIG Motion |
| R6 重要信息不只靠动效或颜色传达 | 关掉动效、换成灰度后，信息仍然在 | 不是每个人都能或愿意看动效 | HIG Motion：Make motion optional |
| R7 一个视图最多一个「展开更多」按钮；最常用的控件不藏 | 数每屏的展开入口 | 多个展开按钮增加复杂度 | HIG Disclosure controls |
| R8 玻璃只用在导航和控件层；不叠玻璃；着色只给主操作；系统「降低透明度」时变成实色 | 列出所有玻璃元素和它们所在的层 | 防止玻璃抢内容、降低可读性 | 《Meet Liquid Glass》；HIG Materials（标题可见，正文未读到） |
| R9 嵌套圆角同心：内层圆角 = 外层圆角 − 两层之间的内边距（下限 0） | 读样式，逐层算 | 同心圆角是 Harmony 的可见形态；公式是从同心推出来的，**自定** | 新闻稿；《Meet Liquid Glass》 |
| R10 新用户不改任何设置就能完成核心任务；能从系统读到的（深浅色、语言、减弱动态）不在应用里再问一遍 | 用全新账号走核心路径，数被问到的设置项 | 默认值决定了大多数人的体验 | HIG Settings |
| R11 任务相关的选项（筛选、排序、显示/隐藏）放在它影响的那一屏 | 看设置页里有没有任务内选项 | 进设置页等于打断任务 | HIG Settings |
| R12 不可逆的动作（付款、删除、对外发送）前有一个明确的意图动作；可逆的用撤销 | 列出不可逆动作，逐个看有没有意图动作 | 苹果宁可给 Apple Pay 加一步，也要防止误付 | Face ID 白皮书（[经 Daring Fireball 转引](https://daringfireball.net/linked/2017/09/27/face-id-white-paper)）：店内付款要先双击侧键确认意图；HIG Generative AI |
| R13 请求权限时说明理由和好处，在需要时再请求 | 看每个权限请求出现的时机和旁边的文案 | 先讲清楚，才能赢得信任 | HIG 设计原则 · Responsibility；HIG Machine learning · Calibration |

### 2.3 对 AI Agent 界面的启发

结论：苹果把 Agent 界面的核心定为「人始终掌控」。具体手段是可见的 AI 标识、结果旁的修正控件、具体的进度、不可逆前的确认，以及对主动行为更严格的门槛。下面每条都能直接写进验收标准。

1. **标明哪里用了 AI，不让人误以为是人写的。** 新闻摘要出错以后，苹果把摘要改成斜体，并标明是 Apple Intelligence 生成的（[MacRumors](https://www.macrumors.com/2025/01/16/ios-18-3-news-notifications-removed/)）。规则：Agent 生成的内容和人写的内容在视觉上能区分。（[HIG Generative AI · Transparency](https://developer.apple.com/design/human-interface-guidelines/generative-ai.md)）
2. **结果旁边放修正控件，修正生效时给信号。** 编辑、撤销、重试、调整都放在生成内容附近；用户一调整，界面要显示「改好了」。规则：每个 Agent 产出都有一步撤销和一步重试。（HIG Generative AI · Outputs）
3. **进度写清在做什么。** 不写「处理中…」，写「正在汇总笔记里的主题」这样的具体动作；出错时用白话说发生了什么，并给出下一步。规则：Agent 运行超过 1 秒时，状态文案是「动词 + 对象」，不是通用词。
4. **不可逆或可能出问题的动作，先征得同意。** 不自动执行破坏性的动作（如删照片），也不替人做难撤销的事（如付款）。规则：Agent 的动作按可逆性分级，不可逆的必须有人确认。（HIG Generative AI · Inputs）
5. **主动行为的门槛更高。** 主动推送的功能，用户对它出错的容忍度更低，也更容易觉得失去了控制。置信度低时不展示结果。规则：Agent 主动打扰要有置信度阈值，并且受打扰次数的预算约束。（[HIG Machine learning · Mistakes、Confidence](https://developer.apple.com/design/human-interface-guidelines/machine-learning.md)）
6. **置信度转成能照着做的话。** 不显示「97% 匹配」，写「因为你常听流行乐」；或者按可能性排序，最可能的放第一并默认选中。归因只写事实，不揣测情绪（写「因为你读过」，不写「因为你爱」）。
7. **反馈是自愿的，立刻生效，并且记住。** 选项写清后果（「少推流行乐」，不写「不喜欢」）。用户的修正要马上体现，下次不用再改一遍。
8. **可打断。** 对应 Fluid Interfaces 的 redirectable：Agent 运行中，用户随时能停下、改方向，不用等它跑完。
9. **AI 不可用时仍然能用。** 尽量提供不经过 AI 的路径。（HIG Generative AI · Best practices）
10. **指令只来自开发者。** 不要把不可信的内容或用户输入混进模型指令；安全要多层叠加（[WWDC25 248](https://developer.apple.com/videos/play/wwdc2025/248)）。对界面的含义是：Agent 引用的外部内容要和它自己的判断分开展示。

### 2.4 批判

结论：苹果的原则大体可信，但要分清口号和规则，并注意苹果自己也会违反自己的规则。

- **口号不等于原则。** 「It just works」「only Apple can achieve」（新闻稿原话）是营销语，不能拿来做验收。
- **原则版本在变。** 2014、2025、2026 三版的名字和条数都不一样，每一版都在为当时的视觉语言服务。不要把任何一版当成永恒的规范，要找三版共同的内核（见 §0 第 1 条）。
- **Liquid Glass 的可读性代价有实证。** NN/g 评价 iOS 26 把视觉效果放在了可用性前面，「更难读、更难预测」（[NN/g](https://www.nngroup.com/articles/liquid-glass/)，经 [anderegg.ca](https://anderegg.ca/2025/10/12/nielsen-norman-group-on-ios-26-usability) 转引）。苹果在 iOS 26.1 加了 Clear/Tinted 开关（[TidBITS](https://tidbits.com/2025/10/21/ios-26-1-to-add-optional-opacity-to-liquid-glass/)），说明原来的默认值牺牲了可读性。网页借用玻璃时，要按最差的那块背景算对比度。
- **「零步」是误读。** Face ID 给 Apple Pay 加了一个双击确认（[Miessler 的分析](https://danielmiessler.com/blog/faceid-removes-an-authentication-step-except-for-apple-pay)，加上白皮书原文）。苹果去掉的是不承载意图的步骤，不是所有步骤。
- **苹果也会违反自己的 AI 规则。** 2025 年 1 月，新闻摘要生成了错误的 BBC 标题，苹果暂停了这一功能（MacRumors）。这说明 HIG 的「幻觉要防」靠界面写一句提示是不够的。对后果严重的内容（新闻、健康），要么不生成，要么由代码把关。
- **不适用的场景。**
  - 触觉反馈、物理手势、系统级材质在网页上大多没有，或者代价高。
  - 「沿用平台约定」在网页上，指的是网页的约定（链接、返回键、地址栏），不是 iOS 的约定。
  - Rams 的「尽可能少的设计」用在内容站上，容易变成「把导航藏起来」。HIG 自己也说简单不是极简。

---

## 3. 迪士尼

### 3.1 核心思想（7 条）

结论：迪士尼的强项是把一段完整的经历当成一件作品来设计：一个故事，一条被视觉牵引的动线，冲突时有序取舍，把等待也设计进去，开园以后不断加料。这些可以借到产品里。主题乐园特有的「沉浸」和「错觉」大多不能直接搬。

| # | 一句话原则 | 要解决的问题 | 可观察的特征 | 出处与证据强度 |
|---|---|---|---|---|
| D1 | **先有故事，一次只讲一个，不自相矛盾** | 体验东拼西凑，没有一条主线 | 一个区域里的建筑、音乐、员工服装、商品都服务同一个主题；不同主题之间的区域有过渡 | Sklar 的「Mickey's Ten Commandments」第 7、8 条（1991 年提出，[Outreach 转引](https://outreachmagazine.com/ideas/25681-storytelling-3-dimensions.html)；原书 [One Little Spark!](https://www.prince-books.com/book/9781484737637)）。证据：二手转引 |
| D2 | **用视觉锚点（wienie）牵引动线** | 游客不知道往哪走 | 远处有一个高耸醒目的地标（城堡），从入口就能看见；走到了有回报 | 戒律第 4 条；Imagineer John Hench 在《Designing Disney》里写过，人会朝吸引人的东西走（[MousePlanet 考据](https://mouseplanet.com/the-origin-of-the-disneyland-wienie/5245/)）；[D23：沿着美国小镇大街能望见城堡](https://d23.com/a-to-z/main-street-u-s-a/)。证据：词源故事是轶事，设计手法可信 |
| D3 | **用尺度和视觉语言说话，不靠标牌** | 靠文字指路，又累又出戏 | 强迫透视：美国小镇大街的楼越往上越小，城堡的石块越往上越小，显得更高更大 | [D23 美国小镇大街](https://d23.com/a-to-z/main-street-u-s-a/)、[D23 睡美人城堡](https://d23.com/a-to-z/sleeping-beauty-castle/)；戒律第 5 条「visual literacy」 |
| D4 | **避免过载，制造兴奋点；体验要多于处理** | 信息一次给太多；为了效果牺牲内容 | 信息分段出现；「For every ounce of treatment, provide a ton of treat」 | 戒律第 6、9 条。证据：二手转引 |
| D5 | **冲突时按 Keys 的顺序取舍** | 员工遇到冲突不知道听谁的 | Safety、Courtesy、Show、Efficiency，2021 年加入 Inclusion（「at the heart」） | [D'Amaro，Disney Parks Blog 2021-04-13](https://disneyparksblog.com/disney-experiences/a-place-where-everyone-is-welcome/)。**注意**：这篇文章按这个次序列出，但没有明说是优先级。Disney Institute 有一篇题为「礼貌不总是第一优先」的文章（正文未读到），说明顺序有意义。常见的五键排序「Safety, Courtesy, Inclusion, Show, Efficiency」本次没有找到一手原文 |
| D6 | **等待是体验的一部分** | 排队是乐园最大的负面体验 | 排队区有主题、有东西可看；告知等多久；排队公平可见 | [Maister《The Psychology of Waiting Lines》](https://davidmaister.com/blog/201/The-Psychology-of-Waiting-Lines.html)的 8 条命题：有事做的等待显得短；不确定、没解释、不公平的等待显得长；焦虑让等待变长。迪士尼的排队设计常被当成例子，但本次没有取到迪士尼的一手原文 |
| D7 | **永不完工，不断加料（plussing）** | 开业就停止改进 | 定期回头改已有的项目；Walt 说乐园 "never be finished" | [Walt Disney Family Museum](https://www.waltdisney.org/blog/walts-own-words-plussing-disneyland)（1956 年前后 Walt 接受 Pete Martin 采访的原话）；戒律第 10 条「Keep it up」 |

**「Guest」而不是「user」，以及 touchpoint 怎么连成旅程**：MyMagic+ 和 MagicBand 用一个手环串起门票、付款、房卡、预订和角色互动（[Fast Company 2013](https://www.fastcompany.com/1671616/a-1-billion-project-to-remake-the-disney-world-experience-using-rfid)）。这是把多个接触点做成一条旅程的典型例子。称呼上「游客、演职人员、台前、幕后」这套说法流传很广，但本次只查到 Disney Institute 的课程页面，没有取到定义原文。

### 3.2 迪士尼动画十二法则：哪些适用于界面动效

结论：十二法则是为了让角色的动作可信而总结的。界面能直接用的只有 4 条：Slow in/out（缓动）、Timing（时长）、Anticipation（预备）、Staging（舞台调度）。Follow through 和 Secondary action 只能少量用。Squash and stretch、Arcs、Exaggeration 在控件和文字上基本不该用。

- **出处**：Thomas 和 Johnston 1981 年的《The Illusion of Life》。可查的一手转述是 [Lasseter 1987 年的 SIGGRAPH 论文](https://education.siggraph.org/static/HyperGraph/animation/character_animation/principles/prin_trad_anim.htm)：Anticipation 是动作前的准备，Staging 要让意图清楚无误。
- **适用性的反方**：UX in Motion 的专栏《UI Animation Principles: Disney is Dead》认为，界面动效是另一种媒介，只有缓动适用于所有界面动画（[Medium](https://medium.com/ux-in-motion/ui-animation-principles-disney-is-dead-8bf6c66207f9)）。

| 法则 | 界面上怎么用 | 能判对错的规则 |
|---|---|---|
| Slow in / slow out | 所有界面动画都用缓动，进场用 ease-out | 动效 token 里没有 `linear`（进度条除外） |
| Timing | 时长表达分量：小反馈短，大变化稍长 | 见 R5（NN/g） |
| Anticipation | 按下态就是预备：按下立刻变化，结果随后出现 | 见 R1 |
| Staging | 同一时刻只有一个主要变化吸引视线 | 每屏最多一个主动效（我们的 V7 已有） |
| Follow through / overlapping | 列表依次入场、抽屉轻微回弹 | 错开的总时长不超过 R5 的上限（自定） |
| Secondary action | 主动作伴随的小变化，比如图标随状态变化 | 次要动效不能比主动效更显眼（设计评审） |
| Squash & stretch、Arcs、Exaggeration、Appeal | 只用在角色和插画上；文字和控件不变形 | 文字和控件没有缩放形变动画（自定） |
| Straight ahead / pose to pose、Solid drawing | 属于制作方法，和界面规则无关 | — |

### 3.3 能直接用在网页或 App 上的规则

| 规则 | 怎么判 | 为什么 | 出处 |
|---|---|---|---|
| R14 每屏有一个视觉锚点指向主操作，任何滚动位置都看得见下一步去哪 | 截图，5 秒内答出「下一步点哪」 | wienie：人会朝吸引人的东西走 | D2 |
| R15 一页一个主题：换掉站名，这一页就不成立；同一页里没有风格冲突的组件 | 换名测试，加上组件风格对照 | 一次讲一个故事，不自相矛盾 | D1 |
| R16 规则冲突时按固定顺序裁决：安全和隐私 > 尊重用户 > 包容和无障碍 > 呈现 > 效率 | 评审记录里每个冲突都写明依据哪一级 | 有序的 Keys 让一线不用临场猜 | D5（这个顺序是**自定**，参照 Keys 的列出次序，把 Inclusion 放在 Show 前面） |
| R17 超过 1 秒的等待说明在等什么；超过 10 秒给出剩余量（步数、比例或时间）；等待期间用户能离开去做别的，完成后通知 | 逐个触发长操作 | 没解释、不确定的等待显得更长 | Maister；NN/g 响应时间 |
| R18 付费或特权的快速通道，不能让免费主路径变差 | 上线前后对比免费路径的耗时和步数 | Lightning Lane 的教训，见 §3.5 | §3.5 |
| R19 规划和准备挪到关键时刻之前，关键时刻里只剩「照做」 | 数关键时刻里要做的决定 | 迪士尼把预订挪到入园前，理由是游客不想在当天做规划 | [Disney Parks Blog 2024-06-25](https://disneyparksblog.com/wdw/plan-ahead-with-lightning-lane-entry-at-walt-disney-world-starting-july-24/) |
| R20 后台不上台：错误码、内部 ID、过程说明不出现在对外界面 | 搜界面文案 | 台前只放演出 | 台前、幕后的说法（证据强度见 §3.1） |
| R21 每个版本至少回头修一处来自真实使用的已有体验问题 | 看发版记录 | plussing | D7 |

### 3.4 对 AI Agent 界面的启发

结论：迪士尼的模型是「台前演出、幕后运转」加上「有序的取舍」，正好对应 Agent 界面的两件难事：展示多少过程，以及冲突时听谁的。

1. **台前和幕后。** 用户默认看到的是结果和下一步。推理过程、工具调用和日志放在幕后，一键能展开。展开后的内容要能核对，不是装饰。
2. **安全在礼貌之前。** Agent 讨好用户（顺着说、硬着头皮做）是礼貌压过了安全。规则：涉及安全、隐私和不可逆的情况，Agent 宁可停下来问，也不顺从。
3. **把等待设计进去。** Agent 的长任务按 Maister 的命题来做：
   - 告诉用户在等什么（有解释）
   - 显示进度和剩余量（让等待有限）
   - 允许离开、做完了再通知（等待期间用户有别的事做）
   - 先给一个能看的初步结果（人们想尽快开始）
4. **一次讲一个故事。** 一次只推荐一个首选行动，附一句理由。其他选项收在后面。
5. **wienie 就是「下一步」。** 每个 Agent 回合结束时，界面上要有一个明确的下一步：确认、修改，或者到此为止。
6. **准备做在前面。** Agent 的价值在于提前把准备做完，让用户在关键时刻只需照做（对应 R19）。
7. **快速通道不能变成新负担。** Genie+ 本来是帮游客省排队时间的，结果变成游客要一直盯着手机抢时段（见 §3.5）。规则：Agent 要替用户省事，不能变成一个要用户盯着管的系统。

### 3.5 批判

结论：迪士尼的很多说法来自传记、演讲和培训课，属于经验总结，不是实证研究。「沉浸」和「错觉」用在工具类产品上会适得其反。

- **证据强度。** 「Mickey's Ten Commandments」是 Sklar 1991 年的演讲，网上流传的都是转引。wienie 的词源（Walt 拿热狗逗狗）来自家人回忆。Disney Institute 是迪士尼卖培训课的业务，它的文章带营销性质。这些都可以当启发，不能当证据。
- **Keys 的「优先顺序」被说得比原文更确定。** D'Amaro 的原文只说 Inclusion 在「核心」，没有给五键排名次。
- **FastPass 和 Lightning Lane 的证据其实不一致。** Touring Plans 在 FastPass+ 上线头几周的数据显示，普通排队的时间平均只多了不到 1 分钟（[Touring Plans](https://touringplans.com/blog/fastpass-affecting-your-wait-in-line-disney-world/)，作者自己也说只是初步观察）。对 Genie+ 的批评主要在价格和「越多人买，快速通道越慢」的循环（[Theme Park Insider 2024-05](https://www.themeparkinsider.com/flume/202405/10203)，是评论，不是数据）。迪士尼官方把它改成入园前预订，给的理由是减轻游客当天的规划负担。所以能确定的教训是「把规划负担塞进体验当天是错的」，「付费通道拖慢普通排队」证据不足。
- **沉浸用在工具上会适得其反。**
  - 乐园刻意让人看不见外部世界、忘掉时间。工具类产品正相反，用户要随时看到系统状态、随时能退出（NN/g 启发式第 1、3 条，我们的 U6、U9 已采用）。
  - 强迫透视本质上是操纵感知。界面上用尺度表达主次可以；用尺度夸大价值、制造紧迫感，就是暗黑模式。
  - 主题化的排队区会掩盖真实的等待时长。产品要先缩短真实的等待，再改善感知；不能拿「感觉不长」代替「真的不长」。
- **一个接触点连起整条旅程，代价是追踪。** MagicBand 的便利建立在追踪游客行踪之上。超过 50 美元的消费要输 PIN，这又打破了「魔法」（Fast Company）。
- **「Guest」心态的边界。** 东道主心态容易滑向家长作风，替客人做决定。苹果的 Agency 原则在这里是更好的平衡：周到地准备，但决定权在用户手里。
- **十二法则不是界面法则。** 见 §3.2。

---

## 4. 两家合起来：可复用的原则

| 原则 | 苹果的说法 | 迪士尼的说法 | 落到界面上 |
|---|---|---|---|
| 内容和任务优先 | Deference、内容层与控件层 | story first、treat 多于 treatment | 一屏一个主操作；装饰要证明自己有用 |
| 下一步永远可见 | Establish hierarchy | wienie | 每屏和每个 Agent 回合都有明确的下一步 |
| 即时、可打断的回应 | Fluid Interfaces | — | 100ms 内有反馈；动画不阻塞输入 |
| 设计等待 | 具体的进度文案、后台生成 | Maister 的等待心理学 | 说清在等什么、还要多久；允许离开 |
| 有序取舍 | Responsibility 在 Delight 之前 | Safety 在 Courtesy 之前 | 写下冲突时的裁决顺序 |
| 用户掌控 | Agency、撤销、不可逆前确认 | （迪士尼较弱） | 可逆的用撤销，不可逆的要确认 |
| 持续打磨 | Maintain your craft | plussing | 每版修一处真实的体验问题 |

---

## 5. 对照我们现有的原则

结论：我们的规则大多有研究支持。需要改的有三处：

- **步数预算**（U1，以及 §3「超出预算就改设计，不改预算」）：不能把所有步骤一视同仁。
- **「一秒」**（U8）：没有分清「回应」和「完成」。
- **缺少 Agent 界面的规则**：AI 标识、修正控件、具体进度、主动行为的门槛。

另有几处小补充：动画可打断、同心圆角、不可逆前确认。

### 5.1 `quality-terms.md` §4.1 好用（U）

| 规则 | 结论 | 理由 |
|---|---|---|
| U1 一键（两步、三步） | **挑战** | 只数点按，把承载意图的步骤也当成成本。Apple Pay 有意加一步确认付款意图；HIG 要求不可逆前确认；迪士尼的经验是负担落在什么时刻比步数更要紧。建议：同意、付款、不可逆这几类意图步骤单独列出，不计入预算，也不许省掉；预算之外再记一项「关键时刻里要做的决定数」 |
| U2 首屏回答三件事 | 支持 | 对应 wienie 和 Know your audience，以及 HIG 的 Purpose。「5 人中 4 人」的数没有外部依据（已标自定） |
| U3 一个区域 1 个主操作 | 支持 | Liquid Glass 只给主操作着色；wienie 是单一锚点 |
| U4 导航不超过 6 项 | 支持方向，数字没有新证据 | HIG「Include just what's necessary」；6 这个数仍然来自对标站点 |
| U5 标签说出去处或结果 | 支持 | HIG Machine learning 要求选项写清后果，例如「少推流行乐」，不写「不喜欢」 |
| U6 能退出；撤销代替「确定吗」 | 支持，建议补半句 | 和 HIG 一致。建议补上「不能撤回的操作（付款、删除、对外发送）要有一个确认意图的动作」，否则「撤销代替确认」容易被套用到不可逆的操作上 |
| U7 一站 | 支持 | MagicBand 把接触点串成一条旅程；HIG 要求任务内选项不离开当前页；能从系统读到的不再问 |
| U8 一秒（P95 ≤ 1 秒） | **部分挑战** | Fluid Interfaces 和 NN/g 说的「即时」指的是回应（0.1 秒），不是完成。生成式 AI 天然做不到 1 秒完成，HIG 要求为它设计加载过程或在后台生成。建议把 U8 拆成两条：「回应 ≤ 0.1 秒」对所有操作；「完成 P95 ≤ 1 秒」只对非生成类的操作，生成类的走 U9 的进度规则 |
| U9 反馈（0.1、1、10 秒） | 支持，建议补一句 | 建议加上：超过 1 秒的状态文案写成「动词 + 对象」，不用「加载中」「处理中」（HIG Generative AI；Maister：有解释的等待显得短） |
| U10 渐进披露、展开不挤动版面、同一操作同一位置 | 支持 | HIG Disclosure controls（常用的放在顶层，一个视图最多一个展开按钮）；HIG Flexibility 要求内容和控件位置一致、可预期；Fluid 的空间一致 |
| U11 键盘能做完全部操作 | 支持 | HIG Flexibility：考虑多种输入方式 |
| U12 出错有出路 | 支持 | HIG Machine learning：不能让人没有下一步，也不能暗示是用户的错；要有不经过 AI 的后备路径 |
| U13 换姿态不打断 | 支持 | HIG Flexibility：保留用户的上下文；HIG 有专门的 iPhone Duo 一页（未细读） |

### 5.2 §4.2 好懂（C）

| 规则 | 结论 | 理由 |
|---|---|---|
| C1 句长 | 本研究没有新证据 | 苹果只说「Be concise」，没给数值 |
| C2 段落 | 本研究没有新证据 | 同上 |
| C3 术语表、一段不超过两个新术语 | 支持方向 | 迪士尼「Avoid overload」；HIG「Use concepts that people know」 |
| C4 按钮写成「动词 + 对象」 | 支持 | HIG Machine learning 要求选项描述后果 |
| C5 错误说清怎么办，不怪用户 | 支持 | HIG 校准一节：不能暗示是用户的错，要给出明确的下一步 |
| C6 不造词、不说空话 | 支持方向 | HIG Simplicity：Choose exactly the words |
| C7 中英两版 | 本研究没有新证据 | — |
| C8 一图一意、不放装饰图 | 支持 | HIG「Don't mistake delight for decoration」；迪士尼戒律第 9 条 |
| C9 文章结构 | 本研究没有新证据 | — |
| C10 不用读就会用 | 支持，补一个边界 | 对应 HIG Familiarity 和迪士尼戒律第 5 条。HIG 提醒，图标单独用说不清粒度和后果；我们「其余图标带文字」的规则正好对上 |

### 5.3 §4.3 好看（V）

| 规则 | 结论 | 理由 |
|---|---|---|
| V1 字体三种 | 支持（没有新证据） | 沿用已引的 HIG |
| V2 强调色只给主操作、链接和当前位置 | 支持 | 《Meet Liquid Glass》：着色只给主操作；颜色放进内容层 |
| V3 一个区域只放标题、一句说明和操作 | 支持方向 | 迪士尼「Avoid overload」；HIG「Include just what's necessary」 |
| V4 同一层级用同一种排法 | 支持 | 2014 年 HIG 的 Consistency；迪士尼「Avoid contradictions」 |
| V5 玻璃 | 支持，**有一处要警惕** | 分层、不叠玻璃、着色、降低透明度这几条都和《Meet Liquid Glass》一致。但「看得出背后的内容」这一条会把设计推向更透明的 Clear。苹果说 Clear 要同时满足三个条件才能用，iOS 26.1 还补了 Tinted 开关。建议：阅读站的玻璃默认偏 Tinted 或厚玻璃，「透得出背后」只作为允许用玻璃的门槛，不作为目标 |
| V6 只用 token、留白分组、栅格对齐 | 支持，建议补一条 | 补「嵌套圆角同心」（见 R9；Harmony 一条的可见形态） |
| V7 动效有含义、每屏一个主动效 | 支持，建议补一条 | 补「动画进行中输入立刻生效（可打断）；高频交互不加自定义动效」（HIG Motion；WWDC18）。缓动规则可以写成「token 里没有 linear」 |
| V8 元信息克制 | 支持方向 | 迪士尼「treat 多于 treatment」 |
| V9 排版细节 | 本研究没有新证据 | — |
| V10 没有模板味、换名测试 | 支持 | 迪士尼「Tell one story」；HIG Purpose：说清你和别人的不同 |

### 5.4 §4.5 舒适（A）

| 规则 | 结论 | 理由 |
|---|---|---|
| A1 对比度 | 支持 | Liquid Glass 的可读性批评，以及 iOS 26.1 的 Tinted 开关，都说明玻璃上的对比度必须按最差的那块背景实测 |
| A2 可点区域 ≥ 44px | 支持（没有新证据） | — |
| A3 320px 宽、放大 200% | 支持 | HIG Flexibility：Design for everyone |
| A4 动效不晕、能停 | 支持，可选补充 | HIG Motion：动效要可选；系统减弱动态时去掉弹性效果。可选补一条「循环摆动避开 0.2Hz 左右」，HIG 是在 visionOS 一节里说的，用在平面网页上证据弱 |
| A5 不打扰 | 支持 | HIG Machine learning：用户对主动功能的出错容忍度更低；迪士尼「Avoid overload」 |
| A6 读起来不累 | 本研究没有新证据 | — |
| A7 媒体有替代 | 支持 | HIG Motion：重要信息不只靠动效传达 |
| A8 折痕上不放按钮和文字 | 本研究没有新证据 | — |

### 5.5 `velicoach-layout` §3「一站、一键、一秒」

| 条目 | 结论 | 理由 |
|---|---|---|
| 一站 | 支持 | 同 U7 |
| 一键，以及「超出预算就改设计，不改预算」 | **挑战（最需要改的一条）** | 同 U1。「不改预算」把步数当成唯一的度量；苹果和迪士尼的证据都说明，意图确认和「负担落在什么时刻」比点按次数更要紧。建议改成：「超出预算先删掉不承载意图的步骤；剩下的是意图步骤（同意、付款、不可逆），就在步数表里标明是哪一类，不算超预算」 |
| 一秒 | 部分挑战 | 同 U8：分清回应和完成 |
| 不用读就会用 | 支持 | 同 C10 |
| 首屏就是操作台 | 支持 | wienie；HIG「Stay out of the way」 |
| 按钮直达结果 | 支持 | 同 U5 |
| 原地展开（悬停 80ms 展开、离开 300ms 收起） | 支持渐进披露；80ms 没有外部依据 | HIG Disclosure 支持原地展开；Fluid 的可打断性支持「能移进卡片、能 Esc 收起」。80ms 和 300ms 是自定的数，太短容易被路过的鼠标误触发，建议在关口四用真实鼠标路径验证。另外，HIG 主张一个视图最多一个展开按钮，可以检查首屏有几个带展开的入口 |
| 展开不挤动版面 | 支持 | HIG Flexibility 要求位置可预期；Fluid 的空间一致 |
| 少一步的其他做法（撤销代替确认等） | 支持，有前提 | 只对能撤回的操作成立；不可逆的要确认（同 U6） |
| 登录原地完成 | 支持 | Face ID 和 Apple Pay 都是在当前情境里完成认证 |
| 分清登录前后，位置预留 | 支持 | HIG：保留用户的上下文，控件位置一致 |
| 在对的时刻提示 | 支持，补一个门槛 | HIG Machine learning：用户对主动提示的出错容忍度更低。建议给交叉提示加上频率和相关性的门槛，并且能一步关掉 |
| 不用操纵手段 | 支持 | 迪士尼的强迫透视、Genie+ 的付费压力都是反面教材；HIG Responsibility |
| 交付时逐条数步数 | 支持，前提是改了上面的预算口径 | 同 U1 |

### 5.6 建议新增（Agent 界面，目前没有对应的规则）

放进 `quality-terms.md` 时，先按金字塔定位：这几条最可能挂在 U（掌控、反馈）和 T（可信）两组下面。

1. AI 生成的内容在视觉上能和人写的内容区分。（HIG Generative AI；苹果新闻摘要事件）
2. 每个 Agent 产出旁边有撤销和重试；用户的修正立刻生效，并且被记住。（HIG Generative AI、Machine learning）
3. Agent 的动作按可逆性分级；不可逆的必须由人确认。（HIG Generative AI）
4. Agent 主动打扰要有置信度阈值，并受打扰次数的预算约束；置信度用能照着做的话表达，不显示百分比。（HIG Machine learning）
5. Agent 运行中随时能停下、改方向。（WWDC18 的可打断，推到 Agent 上）

---

## 6. 出处

苹果：
- [HIG 设计原则（2026-06-08 重新发布）](https://developer.apple.com/design/human-interface-guidelines/design-principles.md)
- [HIG Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai.md)
- [HIG Machine learning](https://developer.apple.com/design/human-interface-guidelines/machine-learning.md)
- [HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion.md)
- [HIG Settings](https://developer.apple.com/design/human-interface-guidelines/settings.md)
- [HIG Disclosure controls](https://developer.apple.com/design/human-interface-guidelines/disclosure-controls.md)
- [iOS HIG 2014（iOS 7，镜像）](https://www.evl.uic.edu/datsoupi/420_14/docs/MobileHIG.pdf)
- [Create with Swift 转引的 2025 版 Hierarchy、Harmony、Consistency](https://www.createwithswift.com/liquid-glass-redefining-design-through-hierarchy-harmony-and-consistency/)
- [Apple Newsroom：Liquid Glass](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/)
- [WWDC25 219《Meet Liquid Glass》文字稿](https://nonstrict.eu/wwdcindex/wwdc2025/219/)
- [WWDC25 248](https://developer.apple.com/videos/play/wwdc2025/248)
- [WWDC18 803《Designing Fluid Interfaces》文字稿](https://nonstrict.eu/wwdcindex/wwdc2018/803)
- [Face ID 白皮书（经 Daring Fireball）](https://daringfireball.net/linked/2017/09/27/face-id-white-paper)
- [Miessler 谈 Apple Pay 多出的一步](https://danielmiessler.com/blog/faceid-removes-an-authentication-step-except-for-apple-pay)
- [TechCrunch「It Just Works」](https://techcrunch.com/?p=311653)
- [Vitsœ：Rams 十条](https://vitsoe.com/us/about/good-design)
- [Phaidon：Rams 作品集（Ive 作序）](https://www.phaidon.com/en-gb/products/dieter-rams-as-little-design-as-possible)
- [NN/g 评 Liquid Glass](https://www.nngroup.com/articles/liquid-glass/)（经 [anderegg.ca](https://anderegg.ca/2025/10/12/nielsen-norman-group-on-ios-26-usability) 转引）
- [TidBITS：iOS 26.1 加入 Tinted](https://tidbits.com/2025/10/21/ios-26-1-to-add-optional-opacity-to-liquid-glass/)
- [MacRumors：新闻摘要暂停](https://www.macrumors.com/2025/01/16/ios-18-3-news-notifications-removed/)

迪士尼：
- [D'Amaro：Five Keys（Disney Parks Blog 2021）](https://disneyparksblog.com/disney-experiences/a-place-where-everyone-is-welcome/)
- [Disney Parks Blog：Lightning Lane 改为入园前预订（2024）](https://disneyparksblog.com/wdw/plan-ahead-with-lightning-lane-entry-at-walt-disney-world-starting-july-24/)
- [Walt Disney Family Museum：plussing](https://www.waltdisney.org/blog/walts-own-words-plussing-disneyland)
- [D23 美国小镇大街](https://d23.com/a-to-z/main-street-u-s-a/)
- [D23 睡美人城堡](https://d23.com/a-to-z/sleeping-beauty-castle/)
- [MousePlanet：wienie 的来历](https://mouseplanet.com/the-origin-of-the-disneyland-wienie/5245/)
- [Outreach：Mickey's Ten Commandments 转引](https://outreachmagazine.com/ideas/25681-storytelling-3-dimensions.html)
- [One Little Spark!](https://www.prince-books.com/book/9781484737637)
- [Maister：等待的心理学](https://davidmaister.com/blog/201/The-Psychology-of-Waiting-Lines.html)
- [Touring Plans：FastPass+ 对普通排队的影响](https://touringplans.com/blog/fastpass-affecting-your-wait-in-line-disney-world/)
- [Theme Park Insider：Genie+ 定价](https://www.themeparkinsider.com/flume/202405/10203)
- [Fast Company：MyMagic+ 与 MagicBand](https://www.fastcompany.com/1671616/a-1-billion-project-to-remake-the-disney-world-experience-using-rfid)
- [Lasseter 1987（SIGGRAPH）](https://education.siggraph.org/static/HyperGraph/animation/character_animation/principles/prin_trad_anim.htm)
- [UX in Motion：Disney is Dead](https://medium.com/ux-in-motion/ui-animation-principles-disney-is-dead-8bf6c66207f9)

通用：
- [NN/g 响应时间](https://www.nngroup.com/articles/response-times-3-important-limits/)
- [NN/g 动画时长](https://www.nngroup.com/articles/animation-duration/)
