/* ── 看清首页的数据和取值：/mind（AI 发展史）和 /mind/collaboration（人机协作）。Mind 和 States 两块画板共用这一份（States 由 pa-out/build.py 把同一份标记和这份数据拼进去）── */
const MIND_NOW_YEAR = 2026;            // 时间尺的右端：画板核对的这一年
const MIND_CHECKED = '2026-11-04';     // 里程碑的最后核对日期
/* WordS（种星词）的地址在站点配置 SITE_CONFIG.wordsUrl：空着就不显示入口（PRD 第 3 节，联审 C-01）。画板属性「已配置」用这个示例子域名，实际地址等 WordS 上线后写进站点配置 */
const MIND_WORDS_SAMPLE = 'https://words.velicoach.com/';
const MIND_COPY = {
  zh: {
    lead: '写给想跟上 AI 的人：AI 是怎么一步步走到今天的，人和智能体（agent）又该怎么一起工作。',
    linesLabel: '内容线', hist: 'AI 发展史', collab: '人机协作', histHref: '/mind', collabHref: '/mind/collaboration',
    learn: '学习路径 →', words: '种星词：记英语单词 ↗', learnHref: '/mind/learn', learnBase: '/mind/learn#', postBase: '/mind/',
    rulerNote: (a, b) => `一格一个时代，宽度按年数，圆点是里程碑。前两个时代走了 ${a} 年，后三个时代到今年一共 ${b} 年。`,
    rulerAlt: (parts) => `时间尺：1950 年到 ${MIND_NOW_YEAR} 年，五个时代按年数排开。${parts}。`, rulerPart: (n, y) => `${n} ${y} 年`, rulerSep: '，',
    histIntro: '只收让路线拐弯的事：它之前大家怎么做，它之后为什么换了做法。点开一条，看它为什么是转折，再去读原始论文或文章。',
    checked: '发现错误，', report: '直接告诉我们', checkedEnd: '。',
    routeLabel: '这个时代的路线：', whyLabel: '为什么是转折', checkedLabel: '最后核对', source: '读原文', follow: '跟着学：', hasPost: '有站内讲解', readPost: '读站内讲解',
    indexLabel: '时代索引', jumpLabel: '跳到某个时代', erasLabel: '五个时代', open: '至今', toIndex: '时代索引 ↑', toIndexLabel: '回到时代索引',
    offline: '网络断开了。已经打开的内容可以接着读；重新连上以后，这条提示会自己消失。',
    kinds: { paper: '论文', event: '事件', product: '产品', essay: '文章', code: '代码' },
    nestAlt: '五种工程范式一层包一层：提示词工程在最里面，往外依次是上下文工程、Harness 工程、Loop 工程、Graph 工程。',
    nestNote: '后一层把前一层包在里面，最里面的最早：人从写每一句指令，转向设计让智能体自己运转的系统。',
    collabIntro: '只收真正落地过、写了代价的实践。每篇开头先给我们的判断：值不值得学、适合谁；有练习的文章，文末附一个能自己动手验证的练习。',
    layers: { eng: '工程', org: '团队与组织', me: '个人' },
    layerIntro: { eng: '从提示词到多个智能体组成的系统，每一层都在解决上一层留下的问题。', org: '智能体进到团队以后，分工和组织怎样跟着改。', me: '一个人怎样用智能体安排自己的工作和生活。' },
    usesLoop: '用到的工程：Loop 工程', devlog: '我们自己的实践：开发日志', devlogHref: '/build#devlog',
    alsoManus: '另见：《用 Manus 重建 Manus》里的闭环',
    factWhat: '是什么', factHow: '怎么用', factWho: '适合谁', published: '发布于', originLabel: '智能体起草，独立评审', originShort: '智能体起草',
    typePost: '文章', typeTool: '工具', typeSkill: '技能', langOf: { zh: '原文中文', en: '原文英文' }, cardLang: { en: '英文' }, video: '3 分钟视频', sep: ' · ',
  },
  en: {
    lead: 'For anyone who wants to keep up with AI: how it got here, step by step, and how people and agents can work together.',
    linesLabel: 'Content lines', hist: 'History of AI', collab: 'Human–AI collaboration', histHref: '/en/mind', collabHref: '/en/mind/collaboration',
    learn: 'Learning path →', words: 'WordS: English vocabulary for kids ↗', learnHref: '/en/mind/learn', learnBase: '/en/mind/learn#', postBase: '/en/mind/',
    rulerNote: (a, b) => `One block per era, drawn to scale. Each dot is a milestone. The first two eras took ${a} years; the last three have taken ${b}\u00a0so\u00a0far.`,
    rulerAlt: (parts) => `Time ruler from 1950 to ${MIND_NOW_YEAR}, five eras drawn to scale: ${parts}.`, rulerPart: (n, y) => `${n}, ${y} years`, rulerSep: '; ',
    histIntro: 'Only the turns: how people worked before, and why they switched after. Open a row to see why it mattered, then read the original paper or post. ',
    checked: 'Found a mistake? ', report: 'Tell us', checkedEnd: '.',
    routeLabel: 'The road in this era: ', whyLabel: 'Why it mattered', checkedLabel: 'Last checked', source: 'Read the original', follow: 'Learn it: ', hasPost: 'Explained on this site', readPost: 'Read our explainer',
    indexLabel: 'Era index', jumpLabel: 'Jump to an era', erasLabel: 'Five eras', open: 'now', toIndex: 'Eras ↑', toIndexLabel: 'Back to the list of eras',
    offline: 'You’re offline. Keep reading what’s already open. This notice clears once you reconnect.',
    kinds: { paper: 'Paper', event: 'Event', product: 'Product', essay: 'Essay', code: 'Code' },
    nestAlt: 'Five engineering paradigms, each wrapping the one before: prompt engineering at the center, then context, harness, loop, and graph engineering.',
    nestNote: 'Each layer wraps the one before it, with the earliest at the center. People move from writing every instruction to designing systems that agents run on their own.',
    collabIntro: 'Only practices that shipped and wrote down what they cost. Each article opens with our take: whether it’s worth learning and who it’s for. Where an article has an exercise, it comes at the end, and you can check the result yourself.',
    layers: { eng: 'Engineering', org: 'Teams and organizations', me: 'Personal' },
    layerIntro: { eng: 'From prompts to systems of several agents, each layer solves a problem the last one left open.', org: 'How teams and organizations change once agents join the work.', me: 'How one person uses agents to run their work and life.' },
    usesLoop: 'Engineering layer used: Loop engineering', devlog: 'Our own practice: the devlog', devlogHref: '/en/build#devlog',
    alsoManus: 'See also: the closed loop in “Rebuilding Manus with Manus”',
    factWhat: 'What it is', factHow: 'How to use it', factWho: 'Who it’s for', published: 'Published', originLabel: 'AI-drafted, independently reviewed', originShort: 'AI-drafted',
    typePost: 'Article', typeTool: 'Tool', typeSkill: 'Skill', langOf: { zh: 'Original in Chinese', en: 'Original in English' }, cardLang: { en: 'English' }, video: '3-minute video', sep: ' · ',
  },
};
/* 五个时代的起止年份：机器学习从 1986 年（反向传播让「从数据里学」回到台前）起算，1980 年代前半仍是专家系统的高峰，算在起源里。最终以内容票 T06 为准 */
const ERAS = [
  { id: 'era-origins', start: 1950, end: 1985, zh: ['起源', '把知识写成规则和逻辑，让机器照着推理。'], en: ['Origins', 'Write knowledge down as rules and logic, and have the machine reason from them.'] },
  { id: 'era-ml', start: 1986, end: 2011, zh: ['机器学习', '不再手写规则，让机器从数据里学；看什么特征，还要人来设计。'], en: ['Machine learning', 'Stop writing rules and let the machine learn from data, though people still design the features it looks at.'] },
  { id: 'era-dl', start: 2012, end: 2016, zh: ['深度学习', '特征也交给网络自己学：更深的网络，加上 GPU 和大数据。'], en: ['Deep learning', 'Let the network learn the features too: deeper networks, GPUs, and big data.'] },
  { id: 'era-llm', start: 2017, end: 2022, zh: ['大语言模型', '一种通用的结构，加上更多的数据和算力。'], en: ['Large language models', 'One general architecture, plus more data and more compute.'] },
  { id: 'era-agents', start: 2023, end: null, zh: ['智能体', '模型不只回答，还自己调用工具、检查结果，把一件事做完。'], en: ['Agents', 'The model does more than answer. It calls tools, checks its results, and finishes the job.'] },
];
/* 里程碑只写到年份：autoresearch、《Loop Engineering》的月份和日期没有核对到，不写。
   里程碑：slug、年份、类型、原文链接、可以跟着学的学习路径步骤（step）；zh / en：标题、发生了什么、为什么是转折 */
const MILESTONES = [
  { slug: 'turing-1950', year: 1950, type: 'paper', url: 'https://academic.oup.com/mind/article/LIX/236/433/986238',
    zh: ['图灵《计算机器与智能》', '不再争论「机器能不能思考」，改问它能不能在对话里让人分不出来。', '一个哲学问题变成了可以检验的问题。'],
    en: ['Turing, “Computing Machinery and Intelligence”', 'Stops arguing over whether machines can think and asks whether one can pass for a person in conversation.', 'A philosophical question became one you could test.'] },
  { slug: 'dartmouth-1955', year: 1955, type: 'paper', url: 'http://jmc.stanford.edu/articles/dartmouth/dartmouth.pdf',
    zh: ['McCarthy 等：达特茅斯人工智能提案', '「人工智能」这个名字第一次写进文献。', '第二年夏天的研讨会，让符号主义（用规则和逻辑表示知识）成了主路线。'],
    en: ['McCarthy et al., the Dartmouth proposal', 'The term “artificial intelligence” first appears in print.', 'The workshop it proposed, held the next summer, made symbolic AI, knowledge written as rules and logic, the main road.'] },
  { slug: 'perceptron-1958', year: 1958, type: 'paper', url: 'https://doi.org/10.1037/h0042519',
    zh: ['Rosenblatt：感知机', '一个能从例子里调整连接权重的模型，不靠人写规则。', '「从数据里学」这条路线从这里开始；它先被冷落，到 1986 年才回到台前。'],
    en: ['Rosenblatt, the perceptron', 'A model that adjusts its connection weights from examples instead of following hand-written rules.', 'Learning from data starts here as a rival road. It fell out of favor and did not return until 1986.'] },
  { slug: 'backprop-1986', year: 1986, type: 'paper', url: 'https://www.nature.com/articles/323533a0', step: 'machine-learning-specialization',
    zh: ['Rumelhart、Hinton、Williams：反向传播', '把误差一层层往回传，多层神经网络终于能训练。', '从数据里学的连接主义回到台前，手写规则开始让位。'],
    en: ['Rumelhart, Hinton, and Williams: backpropagation', 'Passing the error backward, layer by layer, makes multilayer neural networks trainable.', 'Learning from data returns to center stage, and hand-written rules begin to give way.'] },
  { slug: 'lenet-1998', year: 1998, type: 'paper', url: 'https://doi.org/10.1109/5.726791',
    zh: ['LeCun 等：用卷积网络识别手写字符', '卷积网络直接从像素学会认手写数字。', '特征不用人来设计，网络自己学得出来；只是当时的数据和算力还撑不起更大的网络。'],
    en: ['LeCun et al., convolutional networks for document recognition', 'A convolutional network learns to read handwritten digits straight from pixels.', 'Features no longer had to be designed by hand, though the data and compute of the day could not support bigger networks.'] },
  { slug: 'deep-belief-nets-2006', year: 2006, type: 'paper', url: 'https://doi.org/10.1162/neco.2006.18.7.1527',
    zh: ['Hinton、Osindero、Teh：深度信念网络', '一层一层地预先训练，让深层网络重新训练得动。', '「深度学习」从这里重新被认真对待。'],
    en: ['Hinton, Osindero, and Teh: deep belief nets', 'Pretraining one layer at a time makes deep networks trainable again.', 'From here on, deep learning is taken seriously again.'] },
  { slug: 'imagenet-2009', year: 2009, type: 'paper', url: 'https://doi.org/10.1109/CVPR.2009.5206848',
    zh: ['Deng 等：ImageNet', '按 WordNet 的层级整理出的大规模带标注图像数据集。', '数据集本身成了路线的一部分：三年后，深度网络就是在它上面拉开差距的。'],
    en: ['Deng et al., ImageNet', 'A large labeled image dataset organized along the WordNet hierarchy.', 'The dataset itself becomes part of the road. Three years later it is where deep networks pull ahead.'] },
  { slug: 'alexnet-2012', year: 2012, type: 'paper', url: 'https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html', step: 'deep-learning-specialization',
    zh: ['Krizhevsky、Sutskever、Hinton：AlexNet', '深度网络在 ImageNet 比赛上大幅领先。', 'GPU 加大数据成了新的做法，视觉研究随后整体转向深度学习。'],
    en: ['Krizhevsky, Sutskever, and Hinton: AlexNet', 'A deep network wins the ImageNet competition by a wide margin.', 'GPUs plus big data become the new way to work, and vision research moves to deep learning.'] },
  { slug: 'attention-2014', year: 2014, type: 'paper', url: 'https://arxiv.org/abs/1409.0473',
    zh: ['Bahdanau、Cho、Bengio：注意力机制', '翻译每个词的时候，让模型自己去看原句里相关的位置。', '注意力从这里进入主流，三年后成了 Transformer 的主体。'],
    en: ['Bahdanau, Cho, and Bengio: attention', 'While translating each word, the model learns where to look in the source sentence.', 'Attention enters the mainstream here. Three years later it is the core of the Transformer.'] },
  { slug: 'resnet-2015', year: 2015, type: 'paper', url: 'https://arxiv.org/abs/1512.03385',
    zh: ['He 等：残差网络（ResNet）', '每隔几层加一条直通的连接，上百层的网络也能训练。', '深度不再是障碍；这种直通连接后来也用进了 Transformer。'],
    en: ['He et al., residual networks (ResNet)', 'Shortcut connections around every few layers make networks over a hundred layers deep trainable.', 'Depth stops being the obstacle, and the same shortcut later goes into the Transformer.'] },
  { slug: 'alphago-2016', year: 2016, type: 'paper', url: 'https://www.nature.com/articles/nature16961',
    zh: ['Silver 等：AlphaGo', '深度网络加上树搜索，在围棋上战胜了职业棋手。', '学出来的直觉加上搜索，解决了一个原本以为还要等很多年的问题。'],
    en: ['Silver et al., AlphaGo', 'Deep networks combined with tree search beat a professional Go player.', 'Learned intuition plus search cracks a problem most people expected to stand for many more years.'] },
  { slug: 'transformer-2017', year: 2017, type: 'paper', url: 'https://arxiv.org/abs/1706.03762', step: 'zero-to-hero',
    zh: ['Vaswani 等《Attention Is All You Need》', 'Transformer 用注意力取代循环，训练可以大规模并行。', '从这里起，模型的规模可以跟着算力一起长。'],
    en: ['Vaswani et al., “Attention Is All You Need”', 'The Transformer replaces recurrence with attention, so training can run in parallel at scale.', 'From here on, model size can grow as fast as compute does.'] },
  { slug: 'bitter-lesson-2019', year: 2019, type: 'essay', url: 'http://www.incompleteideas.net/IncIdeas/BitterLesson.html',
    zh: ['萨顿《苦涩的教训》', '七十年的经验：通用方法加上算力，最终胜过人写进去的知识。', '给「只管放大规模」这条路线说清了理由。'],
    en: ['Sutton, “The Bitter Lesson”', 'Seventy years of evidence: general methods plus compute beat knowledge built in by hand.', 'It gave the scale-it-up road its argument.'] },
  { slug: 'scaling-laws-2020', year: 2020, type: 'paper', url: 'https://arxiv.org/abs/2001.08361', step: 'cs336',
    zh: ['Kaplan 等：规模定律', '模型、数据、算力一起变大，效果按可预测的规律变好。', '「继续放大」从一种信念变成了算得出来的投入。'],
    en: ['Kaplan et al., scaling laws', 'Grow the model, the data, and the compute together, and performance improves on a predictable curve.', 'Scaling up turns from a belief into an investment you can calculate.'] },
  { slug: 'gpt-3-2020', year: 2020, type: 'paper', url: 'https://arxiv.org/abs/2005.14165',
    zh: ['Brown 等：GPT-3《Language Models are Few-Shot Learners》', '一个足够大的模型，只看提示里的几个例子，就能做没有专门训练过的任务。', '不用再为每个任务训练一个模型，改提示词就行。后来的提示词工程，是在这个做法上长出来的。'],
    en: ['Brown et al., GPT-3: “Language Models are Few-Shot Learners”', 'A large enough model handles tasks it was never trained for, given only a few examples in the prompt.', 'No more training one model per task. You change the prompt instead, the practice prompt engineering later grew out of.'] },
  { slug: 'react-2022', year: 2022, type: 'paper', url: 'https://arxiv.org/abs/2210.03629', step: 'agentic-ai',
    zh: ['Yao 等：ReAct', '让模型交替着推理和行动：想一步，调用一次工具，看结果，再想。', '智能体的基本循环从这里定型。'],
    en: ['Yao et al., ReAct', 'The model alternates reasoning and acting: think, call a tool, read the result, think again.', 'The basic agent loop takes its shape here.'] },
  { slug: 'chatgpt-2022', year: 2022, type: 'product', url: 'https://openai.com/index/chatgpt/',
    zh: ['OpenAI：ChatGPT', '对话成了界面，大语言模型走进日常工作。', '用它的人从研究者变成了所有人。'],
    en: ['OpenAI, ChatGPT', 'Conversation becomes the interface, and large language models enter everyday work.', 'The users go from researchers to everyone.'] },
  { slug: 'function-calling-2023', year: 2023, type: 'product', url: 'https://openai.com/index/function-calling-and-other-api-updates/',
    zh: ['OpenAI：函数调用', '模型可以按约定的格式提出「调用哪个函数、传什么参数」，由程序去执行。', '调用工具从提示词里的技巧变成了接口的一部分。'],
    en: ['OpenAI, function calling', 'The model can ask, in a fixed format, for a function to be called with given arguments, and the program runs it.', 'Tool use moves from a prompting trick into the API itself.'] },
  { slug: 'reasoning-models-2024', year: 2024, type: 'product', url: 'https://openai.com/index/learning-to-reason-with-llms/',
    zh: ['OpenAI：推理模型 o1', '先想再答，用更多的推理时间换更好的结果。', '除了把模型做大，多了一个方向：让它想得更久。'],
    en: ['OpenAI, the o1 reasoning models', 'Think before answering: more time at inference buys better results.', 'Besides making models bigger, there is now a second lever: letting them think longer.'] },
  { slug: 'mcp-2024', year: 2024, type: 'event', url: 'https://www.anthropic.com/news/model-context-protocol', step: 'anthropic-academy',
    zh: ['Anthropic：模型上下文协议（MCP）', '一个开放的协议，规定智能体怎样连接外部的工具和数据。', '接一个工具，不用再为每个模型、每个应用各写一遍。'],
    en: ['Anthropic, the Model Context Protocol (MCP)', 'An open protocol for how agents connect to outside tools and data.', 'Connecting a tool no longer means rewriting it for every model and every app.'] },
  { slug: 'building-effective-agents-2024', year: 2024, type: 'essay', url: 'https://www.anthropic.com/engineering/building-effective-agents', step: 'building-effective-agents',
    zh: ['Anthropic《Building effective agents》', '把工作流和智能体分开，给出几种简单、能组合的搭法。', 'Anthropic 的建议是先用最简单的搭法，不够用再加，而不是一上来就用更全的框架。'],
    en: ['Anthropic, “Building effective agents”', 'Separates workflows from agents and lays out a few simple, composable patterns.', 'Anthropic’s advice: start with the simplest pattern that works and add only when it falls short, instead of reaching for a bigger framework.'] },
  { slug: 'claude-code-2025', year: 2025, type: 'product', url: 'https://www.anthropic.com/news/claude-3-7-sonnet', step: 'anthropic-academy', post: 'claude-code-review',
    zh: ['Anthropic：Claude Code（随 Claude 3.7 Sonnet 发布）', 'Claude Code 这类编程智能体自己调用工具、检查结果，能把一件事从头做完。', '人的工作从写每一行，转到写清目标和验收结果。'],
    en: ['Anthropic, Claude Code (released with Claude 3.7 Sonnet)', 'Coding agents such as Claude Code call tools, check their own results, and finish a task end to end.', 'People’s work shifts from writing every line to stating the goal and checking the result.'] },
  { slug: 'context-engineering-2025', year: 2025, type: 'essay', url: 'https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus',
    zh: ['Manus《AI\u00a0智能体的上下文工程》', '一个智能体产品总结的经验：模型每一步看到什么，比提示词怎么写更要紧。', '让「上下文工程」这个说法流行起来的文章之一：工程的重心从一句提示词移到整段上下文。'],
    en: ['Manus, “Context Engineering for AI Agents”', 'Lessons from building an agent product: what the model sees at each step matters more than how the prompt is worded.', 'One of the posts that made “context engineering” a common term: the work moves from one prompt to the whole context.'] },
  { slug: 'autoresearch-2026', year: 2026, type: 'code', url: 'https://github.com/karpathy/autoresearch', step: 'autoresearch',
    zh: ['Karpathy：autoresearch', '一个开源项目：智能体自己设计实验、跑实验、记录结果。', '智能体开始接手研究里的循环，人负责定方向和看结果。'],
    en: ['Karpathy, autoresearch', 'An open-source project in which an agent designs, runs, and logs its own experiments.', 'Agents start to take over the loop inside research, while people set the direction and read the results.'] },
  { slug: 'loop-engineering-2026', year: 2026, type: 'essay', url: 'https://addyosmani.com/blog/loop-engineering/',
    zh: ['Addy Osmani《Loop Engineering》', '给智能体一个可以验证的目标，让它自己执行、自己检查，直到达成。', '人从盯着每一步，转到设计让智能体自己运转的循环。'],
    en: ['Addy Osmani, “Loop Engineering”', 'Give the agent a goal it can verify, then let it run and check itself until it gets there.', 'People stop watching every step and start designing the loop the agent runs in.'] },
];
/* 学习路径步骤的名称（「跟着学」入口的文字），和 Learn 画板的步骤一一对应 */
const STEP_NAMES = {
  'machine-learning-specialization': { zh: '机器学习专项课程', en: 'Machine Learning Specialization' },
  'deep-learning-specialization': { zh: '深度学习专项课程', en: 'Deep Learning Specialization' },
  'zero-to-hero': { zh: 'Neural Networks: Zero to Hero', en: 'Neural Networks: Zero to Hero' },
  'cs336': { zh: 'CS336: Language Modeling from Scratch', en: 'CS336: Language Modeling from Scratch' },
  'agentic-ai': { zh: 'Agentic AI', en: 'Agentic AI' },
  'anthropic-academy': { zh: 'Claude Code、MCP、Agent\u00a0Skills\u00a0课程', en: 'Claude Code, MCP, and Agent Skills courses' },
  'building-effective-agents': { zh: 'Building effective agents', en: 'Building effective agents' },
  'autoresearch': { zh: 'autoresearch', en: 'autoresearch' },
};
/* 人机协作 · 工程：五种范式（PRD 第 5 节「线二」的表） */
const PARADIGMS = [
  { id: 'prompt-engineering', zh: ['提示词工程', '2022–2024', '怎样把指令写清楚。'], en: ['Prompt engineering', '2022–2024', 'How to write instructions clearly.'] },
  { id: 'context-engineering', zh: ['上下文工程', '2025', '模型每一步该看到哪些信息。'], en: ['Context engineering', '2025', 'What the model should see at each step.'] },
  { id: 'harness-engineering', zh: ['Harness 工程', '2026 年初', '智能体周围的工具、权限和验证环境怎么搭。Harness 指套在模型外面的那层软件。'], en: ['Harness engineering', 'Early 2026', 'How to build the tools, permissions, and checks around an agent. A harness is the software that wraps the model.'] },
  { id: 'loop-engineering', also: true, zh: ['Loop 工程', '2026 年', '让智能体自己执行、自己检查，直到达成可以验证的目标。'], en: ['Loop engineering', '2026', 'Let the agent run and check itself until it reaches a goal you can verify.'] },
  { id: 'graph-engineering', zh: ['Graph 工程', '正在出现', '多个智能体和共享状态怎样组织成一个系统。'], en: ['Graph engineering', 'Emerging', 'How several agents and shared state fit into one system.'] },
];
/* 文章卡：group 是层（eng 工程 / org 团队与组织 / me 个人），para 是所在的范式。slug 和仓库 src/content/ 一致。
   date 是本站的发布日期，画板示例：仓库现在只有一个 date 字段，Shopify、Dan Koe 两篇填的是原文日期，五篇的发布日期由内容票定；
   首页的「最新文章」取这里最新的一篇（Shopify，2026-10-31），两块画板用同一组日期 */
const POSTS = [
  { date: '2026-10-31', group: 'eng', para: 'harness-engineering', lang: 'en', video: true, slug: 'shopify-harness',
    zh: ['比模型更耐久的 Harness', 'Shopify 用测试证明漏洞，而不是收集模型给出的候选清单。'], en: ['A harness that outlasts the model', 'Shopify proves vulnerabilities with tests instead of collecting a model’s candidate list.'] },
  { date: '2026-10-15', group: 'eng', para: 'harness-engineering', lang: 'en', video: false, slug: 'claude-code-review',
    zh: ['Claude Code 团队如何做 Code Review', '阅读交给机器，判断留在人这里；自动通过不等于没有人负责。'], en: ['How the Claude Code team does code review', 'Machines do the reading, people keep the judgment, and automatic approval doesn’t mean nobody is responsible.'] },
  { date: '2026-10-29', group: 'eng', para: 'graph-engineering', lang: 'zh', video: false, slug: 'deepseek-superagent',
    zh: ['Super-agent：把会话藏起来', 'DeepSeek 把多个子智能体藏在一个对话后面，用户只和一个智能体说话。'], en: ['Super-agent: hiding the sessions behind one conversation', 'DeepSeek puts several subagents behind one chat, so people talk to a single agent.'] },
  { date: '2026-10-30', group: 'org', para: null, lang: 'zh', video: false, slug: 'manus-rebuilding',
    zh: ['用 Manus 重建 Manus', '一家公司用自己的智能体重写自己的产品，组织怎样跟着改。'], en: ['Rebuilding Manus with Manus', 'A company rewrites its own product with its own agent, and the organization changes with it.'] },
  { date: '2026-10-22', group: 'me', para: null, lang: 'en', video: false, slug: 'dan-koe-one-day',
    zh: ['如何在一天内彻底改变你的人生', 'Dan Koe 谈怎样用一天想清楚自己要什么，再把生活改过来。'], en: ['How to fix your entire life in 1 day', 'Dan Koe on spending one day working out what you want, then rebuilding your days around it.'] },
];
/* 工具卡和技能卡（PRD 第 5 节「工具与技能卡片」的字段：名称、是什么、怎么用、适合谁、原文链接、语言、类型） */
const CARDS = [
  { slug: 'anthropic-prompt-guide', para: 'prompt-engineering', type: 'tool', lang: 'en', url: 'https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview',
    zh: ['Anthropic 提示词工程指南', '官方文档里讲提示词的一章：把指令写清楚、给例子、让模型先想再答、用标签把内容分段。', '拿一条自己正在用的提示词，照着逐条改，对比改前改后的输出。', '刚开始写提示词，或者输出不稳定、不知道从哪里改起的人。'],
    en: ['Anthropic’s prompt engineering guide', 'The prompting chapter of the official docs: be clear and direct, give examples, let the model think first, and separate content with tags.', 'Take a prompt you already use, revise it one technique at a time, and compare the output before and after.', 'Anyone new to prompting, or getting unsteady output and unsure where to start fixing it.'] },
  { slug: 'anthropic-agent-skills', para: 'context-engineering', type: 'tool', lang: 'en', url: 'https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview',
    zh: ['Anthropic Agent Skills', '把一件事的做法写成一个文件夹：一份 SKILL.md 说明，加上脚本和资料；智能体用到的时候才加载。', '把反复交代的做法写成技能放进项目，智能体按说明里的描述判断什么时候用。', '同一件事要反复向智能体交代的人和团队。'],
    en: ['Anthropic Agent Skills', 'A way to package how a job is done as a folder: a SKILL.md with instructions, plus scripts and reference files, loaded only when the agent needs them.', 'Write the instructions you keep repeating as a skill in your project. The agent reads each skill’s description to decide when to use it.', 'People and teams who explain the same job to an agent again and again.'] },
  { slug: 'mattpocock-skills', para: 'context-engineering', type: 'skill', lang: 'en', url: 'https://github.com/mattpocock/skills',
    zh: ['Matt Pocock 的 Skills', '一组公开的技能，管开工前后的几步：逐题追问需求、写成规格、拆成票、测试先行。', '装进编程智能体；新需求先用 grill-with-docs 追问，再用 to-spec、to-tickets 写成规格和票。', '已经在用编程智能体，想让它先问清楚再动手的人。'],
    en: ['Matt Pocock’s Skills', 'A public set of skills for the steps around the coding: question the requirement, write the spec, split it into tickets, test first.', 'Install them in your coding agent. Start a new requirement with grill-with-docs, then turn it into a spec and tickets with to-spec and to-tickets.', 'People already using a coding agent who want it to ask before it builds.'] },
  { slug: 'pstack', para: 'loop-engineering', type: 'skill', lang: 'en', url: 'https://github.com/cursor/plugins/tree/main/pstack',
    zh: ['pstack', 'poteto（Lauren Tan）公开的一组技能和原则：让智能体把工作拆成能验证的小步，做完自己证明它能用。', '装进编程智能体；任务开始时加载对应的原则，要求它对着真实的结果验证过才算完成。', '想让智能体长时间自己跑，又要信得过结果的人。'],
    en: ['pstack', 'A public set of skills and principles from poteto (Lauren Tan): the agent breaks work into small verifiable steps and proves the result works.', 'Install it in your coding agent and load the matching principle at the start of a task, so nothing counts as done until it is checked against the real result.', 'People who want agents to run on their own for a long time and still trust what comes back.'] },
];
/* v：shellVals() 的结果；o：{ line, network, expand }。看清首页和列表在构建时静态生成，没有加载中和加载失败（PRD 第 527 版「页面状态」）；
   network：在线 / 离线；expand：全部收起 / 展开一条（展开 Transformer 那一条，看原地展开的样子） */
const MIND_OPEN_SLUG = 'transformer-2017';
function mindVals(self, v, o) {
  const L = v.en ? 'en' : 'zh';
  const c = MIND_COPY[L];
  const line = o.line || 'AI 发展史（/mind）';
  const isCollab = line.indexOf('人机协作') === 0;
  const fmt = (iso) => v.en ? new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' }) : iso;
  /* 时代、里程碑、时间尺 */
  const eras = ERAS.map((e, i) => {
    const end = e.end ?? MIND_NOW_YEAR;
    const span = end - e.start + 1;
    const list = MILESTONES.filter((m) => m.year >= e.start && m.year <= end);
    const seen = {};
    const items = list.map((m, k) => {
      const arrive = o.expand === '从链接到达';
      const open = (o.expand === '展开一条' || arrive) && m.slug === MIND_OPEN_SLUG;
      return {
        slug: m.slug, year: m.year, url: m.url, kind: c.kinds[m.type], title: m[L][0], what: m[L][1], why: m[L][2],
        gap: k === 0 ? 0 : m.year - list[k - 1].year, open, closed: !open, target: open && arrive ? ' is-target' : '',
        srcLabel: c.source + (v.en ? ': ' : '：') + m[L][0],
        hasStep: !!m.step, stepHref: c.learnBase + (m.step || ''), stepLabel: m.step ? c.follow + STEP_NAMES[m.step][L] : '',
        hasPost: !!m.post, postHref: c.postBase + (m.post || ''),
      };
    });
    const dots = list.map((m) => { const n = seen[m.year] = (seen[m.year] || 0) + 1; return { left: (((m.year - e.start) + 0.25 * n) / span * 100).toFixed(2) + '%' }; });
    return {
      id: e.id, name: e[L][0], route: e[L][1], start: e.start, span, items, dots,
      years: e.end ? `${e.start}–${e.end}` : `${e.start}–`, yearClass: i > 2 ? 'is-tight' : '', current: i === 0 ? 'true' : 'false',
    };
  });
  const first = eras[0].span + eras[1].span;
  const rest = eras.slice(2).reduce((s, e) => s + e.span, 0);
  /* 人机协作 */
  const post = (p) => ({ isPost: true, isCard: false, slug: p.slug, href: c.postBase + p.slug, title: p[L][0], dek: p[L][1], ai: p.ai !== false, date: p.date, dateText: fmt(p.date),
    meta: [c.typePost, c.langOf[p.lang]].concat(p.video ? [c.video] : []).join(c.sep) });
  const card = (k) => ({ isPost: false, isCard: true, slug: k.slug, href: k.url, title: k[L][0], what: k[L][1], how: k[L][2], who: k[L][3],
    meta: [k.type === 'tool' ? c.typeTool : c.typeSkill, c.cardLang[k.lang]].join(c.sep) });
  const paradigms = PARADIGMS.map((p) => ({
    id: p.id, name: p[L][0], when: p[L][1], problem: p[L][2], hasAlso: !!p.also, also: c.alsoManus, alsoHref: '#manus-rebuilding',
    cards: CARDS.filter((k) => k.para === p.id).map(card).concat(POSTS.filter((x) => x.para === p.id).map(post)),
  }));
  const layers = ['org', 'me'].map((g) => ({
    id: 'layer-' + g, title: c.layers[g], intro: c.layerIntro[g], hasUses: g === 'org', uses: c.usesLoop, usesHref: '#loop-engineering', hasDevlog: g === 'org',
    cards: POSTS.filter((x) => x.group === g).map(post),
  }));
  const offline = o.network === '离线';
  return {
    c, isHist: !isCollab, isCollab, histCur: isCollab ? 'false' : 'page', collabCur: isCollab ? 'page' : 'false',
    showHist: (e) => { e.preventDefault(); self.setState({ line: 'AI 发展史（/mind）' }); },
    showCollab: (e) => { e.preventDefault(); self.setState({ line: '人机协作（/mind/collaboration）' }); },
    eras, checkedIso: MIND_CHECKED, checkedText: fmt(MIND_CHECKED),
    rulerNote: c.rulerNote(first, rest),
    rulerAlt: c.rulerAlt(eras.map((e) => c.rulerPart(e.name, e.span)).join(c.rulerSep)),
    paradigms, layers, nest: Object.assign({}, paradigms.map((p) => ({ name: p.name, when: p.when }))),
    isOffline: offline, bandClass: offline ? 'is-offline' : '',
    ...(() => { const w = o.words === '已配置（示例地址）' ? MIND_WORDS_SAMPLE : SITE_CONFIG.wordsUrl; return { hasWords: !!w, wordsHref: w || '' }; })(),
  };
}
