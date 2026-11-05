# 术语表

中英文案、代码命名、文档都按这张表用词。PRD 第 12 节是同一张表的在线版本，两边一起改。

**原则**

- **用行业通用、用户已经熟悉的词。** 有通行中文译名的用中文（智能体、提示词工程、上下文工程）；还没有通行译名的保留英文，第一次出现时带一句白话（Harness 工程、Loop 工程、Graph 工程）。
- **谨慎造词。** 表里没有的新名字，先查业界怎么叫；确实要新起，先加进这张表再用。
- **一个概念一个词。** 不为了变化换同义词。
- **例外**：三个站名站稳、看清、动手就是品牌口号「先站稳，再看清，然后动手」里的动作；品牌和产品名 Velicoach、Veli 第一次出现时带一句说明。
- 对外文案和内容按这张表写。内部文档里说到我们自己的开发 agent（写代码、跑流水线的那些）可以写 agent。

## 站点用语

| 中文 | English | 含义 |
|---|---|---|
| Velicoach | Velicoach | 主站品牌：AGI 路上的陪练 |
| 站稳 | Body | 第一站：力量训练与长期健康，产品是 Veli。路径 `/body` |
| 看清 | Mind | 第二站：AI 发展史与人机协作。不另起刊名。路径 `/mind` |
| 动手 | Build | 第三站：和智能体一起做出能用的东西，附开发日志。路径 `/build` |
| builder | builder | 和智能体一起，把想法做成能用的东西的人；不一定会写代码。动手一站的读者。第一次出现时带一句说明 |
| AI 发展史 | History of AI | 看清的第一条线：以里程碑为主线，像科技史一样讲路线怎么转折 |
| 里程碑 | Milestone | AI 发展史上改变路线的一件事：年份、事件、为什么是转折、原始论文或文章 |
| 学习路径 | Learning path | 挂在里程碑上的课程和代码，按顺序排成一页：为什么学、学到什么程度、怎么检验、要花多久 |
| 人机协作 | Human–AI collaboration | 看清的第二条线：人和 AI 一起工作的实践，分工程、团队与组织、个人三类 |
| 工程实践 | Engineering practice | 人机协作里的工程部分：提示词工程 → 上下文工程 → Harness 工程 → Loop 工程 → Graph 工程 |
| 开发日志 | Devlog | 公开记录我们怎样和智能体一起做产品 |
| 威利 | Veli | AI 力量训练教练，品牌与教练同名 |
| 薄肌计划 | 以 Veli PRD 为准 | Veli 的训练计划名，只在中文里用 |
| 订阅 | Newsletter（按钮 Subscribe） | 每周日一封邮件：一读、一练、一个可以动手做的项目 |
| 本周文章 | This week's read | 订阅邮件和首页里本周推荐的一篇 |
| 今天的训练 | Today's workout | 站稳给出的当天训练入口 |
| 3 分钟视频 | 3-minute video | 文章开头的讲解视频，中文旁白晓晓，英文旁白 Andrew |
| 外观 | Appearance | 主题设置：自动（跟随系统）、浅色、深色 |

口号「先站稳，再看清，然后动手」（Get strong. See clearly. Build.）用在首页；三个动作就是三个站名。

设计和工程内部用语（不出现在界面上）：叶与网（首页主动效）、书脊（进入一站后另一站收成的窄条）、一站一键一秒（交互总原则：不离开不再登录、核心两步、操作 P95 ≤ 1 秒）、步数预算（「一键」的逐场景表）、不用读就会用（C10）、原地展开。

协作用语（只在文档和票里用，和 Veli 仓库同义；定义见 `docs/standards/pipeline.md`）：关口（阶段之间的出口检查）、车道（站点、内容两条，按路径分工）、冷评审（没看过制作过程的新 Agent 做的评审）、票推进器（推进一条车道的定时任务）、观察者（从外面看整条流水线的 Agent）、运行锁、交接评论、集成分支（`feature/v1`）。

## AI 术语

写法一栏是对外文案里的写法；括号里的英文只在第一次出现时写。

| 中文 | English | 写法 | 白话 |
|---|---|---|---|
| 人工智能 | AI | AI | 让机器做需要智能的事 |
| 通用人工智能 | AGI | 通用人工智能（AGI），之后写 AGI | 在大多数任务上达到或超过人的 AI |
| 大语言模型 | Large language model, LLM | 大语言模型（LLM），之后可写 LLM | 用海量文本训练、能理解和生成语言的模型 |
| 智能体 | Agent | 智能体（agent） | 能自己调用工具、把一件事做完的 AI |
| 多智能体系统 | Multi-agent system | 多智能体系统 | 多个智能体分工合作 |
| 个人智能体 | Personal agent | 个人智能体 | 替一个人长期打理事情的智能体 |
| 提示词 | Prompt | 提示词 | 交给模型的指令和材料 |
| 提示词工程 | Prompt engineering | 提示词工程 | 设计提示词，让模型一次回答得更好 |
| 上下文 | Context | 上下文 | 模型这一次能看到的全部信息 |
| 上下文窗口 | Context window | 上下文窗口 | 模型一次能看到的信息上限 |
| 上下文工程 | Context engineering | 上下文工程 | 决定给模型看什么、怎么组织和压缩 |
| Harness 工程 | Harness engineering | Harness 工程 | 给智能体搭运行框架：工具、权限、记忆、检查和反馈 |
| Loop 工程 | Loop engineering | Loop 工程 | 让智能体在循环里自己执行、检查、修正，直到达到目标 |
| Graph 工程 | Graph engineering | Graph 工程 | 把多个智能体和步骤编排成图，控制分工和流转 |
| 工具调用 | Tool use / function calling | 工具调用 | 模型调用外部工具和接口 |
| 模型上下文协议 | Model Context Protocol, MCP | 模型上下文协议（MCP） | 把工具和数据接给模型的开放协议 |
| 检索增强生成 | Retrieval-augmented generation, RAG | 检索增强生成（RAG） | 先查资料再回答 |
| 技能 | Skills | 技能（skills） | 交给智能体的一包可复用的做法说明 |
| 预训练 | Pre-training | 预训练 | 用海量数据先训出通用能力 |
| 微调 | Fine-tuning | 微调 | 在通用模型上用少量数据再训练 |
| 基于人类反馈的强化学习 | RLHF | 基于人类反馈的强化学习（RLHF） | 用人的评价来调整模型 |
| 规模定律 | Scaling laws | 规模定律 | 模型、数据、算力变大，效果按规律变好 |
| 推理模型 | Reasoning model | 推理模型 | 先想再答、能做多步推理的模型 |
| 思维链 | Chain of thought | 思维链 | 把推理步骤写出来 |
| 幻觉 | Hallucination | 幻觉 | 模型编出不存在的内容 |
| 评测 | Evaluation, evals | 评测 | 用固定题目衡量模型或智能体做得好不好 |
| 词元 | Token | 词元（token） | 模型处理文本的最小单位 |
| 向量嵌入 | Embedding | 向量嵌入 | 把文字变成能比较远近的一串数字 |
| 注意力机制 | Attention | 注意力机制 | 让模型决定该看哪些内容 |
| Transformer | Transformer | Transformer，不译 | 2017 年提出、今天大模型的基础架构 |
| 深度学习 | Deep learning | 深度学习 | 用多层神经网络从数据里学 |
| 符号主义 | Symbolic AI | 符号主义 | 用规则和逻辑表示知识的路线 |
| 连接主义 | Connectionism | 连接主义 | 用神经网络从数据里学的路线 |
| 专家系统 | Expert system | 专家系统 | 把专家规则写进程序 |
| AI 寒冬 | AI winter | AI 寒冬 | AI 投入和期望大幅回落的时期 |
| AI 原生组织 | AI-native organization | AI 原生组织 | 从一开始就按人和智能体协作来设计的组织 |
| 人机协作 | Human–AI collaboration | 人机协作 | 人和 AI 分工合作完成一件事 |

文章和论文名用书名号，例如《苦涩的教训》（The Bitter Lesson）、《Attention Is All You Need》。

## 不再用的说法

| 不再用 | 改用 | 原因 |
|---|---|---|
| Stand strong、See clearly（作英文站名） | Body、Mind、Build | 英文站名用一个常见词 |
| 同席、With（作名字） | 不另起刊名，就是看清（Mind）；说历史时写「原同席博客」 | 听起来奇怪；With 太泛，搜不到 |
| 心智站 | 看清 | 一个概念一个词 |
| 每周邮件、周信、Weekly email | 订阅、Newsletter | 用常见说法；「周信」是自造词 |
| build 日志、Build log | 开发日志、Devlog | 用常见说法 |
| 大事记、时间线节点 | 里程碑 | 产品负责人的说法，也是业界通用的说法 |
| 专业进阶、路径步骤 | 学习路径、学习路径步骤 | 用常见说法 |
| 看清的三条内容线 | 两条线：AI 发展史、人机协作 | 学习路径挂在里程碑上，工程实践归入人机协作 |
| prompt → context → loop → graph | 提示词工程 → 上下文工程 → Harness 工程 → Loop 工程 → Graph 工程 | 用行业通用的名字，补上漏掉的 Harness 工程 |
| 对外文案里的 agent | 智能体（agent） | 业界通用的中文说法 |
| 提示工程学 | 提示词工程 | 业界通用的说法 |
| 今日一练 | 今天的训练 | 用常见说法 |
| 今日一读 | 本周文章 | 和「今天的训练」分开，按实际更新节奏叫 |
| 讲解短片 | 3 分钟视频 | 用常见说法 |
| `with.velicoach.com` | `velicoach.com/mind` | 并入主站；旧地址永久跳转 |
| 搏击、搏击教练 | 力量训练、薄肌、Veli | 产品做的是健身薄肌，不是对抗性的搏击 |
| worrycoach、Value Coach | Velicoach | 语音转写和早期设想 |
| 落地实践 | 不再使用 | 原同席博客最早的名字 |
| xAI 的 prompt | （删除） | 语音转写错误 |
| 了解更多 | 写点了之后得到什么 | 两步原则：按钮直达结果 |

`npm run check:terms` 会按下面的清单检查文档、技能和代码里有没有不再用的说法和常见错字。清单改了，表也一起改。

```stale-terms
同席
心智站
每周邮件
周信
Weekly email
build 日志
Build log
大事记
时间线节点
专业进阶
路径步骤
三条内容线
提示工程学
今日一练
今日一读
讲解短片
落地实践
搏击
worrycoach
Value Coach
Stand strong
See clearly
阀值
布署
反回
回朔
做为
embeding
天马星空
```
