/* ── 学习路径页：/mind/learn。四级，每级不超过 3 项（一位作者或一家机构的一个系列算一项），课程用 PRD 第 5 节的表 ── */
const CHECKED = '2026-11-04';     // 步骤的最后核对日期
const COPY = {
  zh: {
    crumbLabel: '所在位置', title: '学习路径', hist: 'AI 发展史', collab: '人机协作', histHref: '/mind', collabHref: '/mind/collaboration', linesLabel: '内容线', msBase: '/mind#',
    lead: '先学会用智能体，再回头弄懂模型。四级排成一条路，每一步都写清为什么学、学到什么程度、怎么检验自己学会了。', openCourse: '打开课程',
    pathLabel: '四级', lvN: (n) => `第 ${n} 级`, count: (n) => `${n} 项`,
    intro: '每级不超过 3 项，后一级默认你学完了前一级。点开一步，看学到什么程度、怎么检验。时间是我们的估计，按每一项从头学到能通过检验来算。',
    goalLabel: '学完能做到：', why: '为什么学', level: '学到什么程度', check: '怎么检验', checkedLabel: '最后核对', related: '相关里程碑：', hours: (h) => `约\u00a0${h}\u00a0小时`, sep: ' · ',
  },
  en: {
    crumbLabel: 'You are here', title: 'Learning path', hist: 'History of AI', collab: 'Human–AI collaboration', histHref: '/en/mind', collabHref: '/en/mind/collaboration', linesLabel: 'Content lines', msBase: '/en/mind#',
    lead: 'Learn to work with agents first, then go back and understand the models. Four levels in one path, and every step says why it’s there, how far to take it, and how to check you’ve got it.', openCourse: 'Open the course',
    pathLabel: 'Four levels', lvN: (n) => `Level ${n}`, count: (n) => (n === 1 ? '1 step' : `${n} steps`),
    intro: 'Each level has three steps at most and assumes you finished the one before. Open a step to see how far to take it and how to check. The hours are our estimate of going from the start to passing the check.',
    goalLabel: 'After this level you can ', why: 'Why learn it', level: 'How far to go', check: 'How to check', checkedLabel: 'Last checked', related: 'Related milestone: ', hours: (h) => `about\u00a0${h}\u00a0hours`, sep: ' · ',
  },
};
/* 相关里程碑的标题，和 Mind 画板的里程碑一一对应 */
const MS_NAMES = {
  'backprop-1986': { zh: '反向传播（1986）', en: 'Backpropagation (1986)' },
  'alexnet-2012': { zh: 'AlexNet（2012）', en: 'AlexNet (2012)' },
  'transformer-2017': { zh: '《Attention Is All You Need》（2017）', en: '“Attention Is All You Need” (2017)' },
  'scaling-laws-2020': { zh: '规模定律（2020）', en: 'Scaling laws (2020)' },
  'react-2022': { zh: 'ReAct（2022）', en: 'ReAct (2022)' },
  'mcp-2024': { zh: '模型上下文协议（2024）', en: 'The Model Context Protocol (2024)' },
  'building-effective-agents-2024': { zh: '《Building effective agents》（2024）', en: '“Building effective agents” (2024)' },
  'autoresearch-2026': { zh: 'autoresearch（2026）', en: 'autoresearch (2026)' },
};
/* 每步：slug、链接、大概时间（time 是写好的文字时用它，否则用 hours）、相关里程碑（ms）；zh / en：名称、来源、形式、为什么学、学到什么程度、怎么检验 */
const LEVELS = [
  { zh: ['基础', '会编程，懂机器学习的基本概念。'], en: ['Foundations', 'program, and understand the basic ideas of machine learning.'], steps: [
    { slug: 'cs50x', hours: 100, url: 'https://cs50.harvard.edu/x/',
      zh: ['CS50x 计算机科学导论', '哈佛大学', '课程', '后面每一级都要写代码，这门课把编程的底子打好。', '能用一门语言把一个小问题从头写到能运行。', '独立写完最后的项目。'],
      en: ['CS50x: Introduction to Computer Science', 'Harvard University', 'Course', 'Every later level involves code, and this course gives you a solid footing.', 'You can take a small problem from nothing to running code in one language.', 'Finish the final project on your own.'] },
    { slug: 'machine-learning-specialization', hours: 90, url: 'https://www.deeplearning.ai/courses/machine-learning-specialization/', ms: 'backprop-1986',
      zh: ['机器学习专项课程', '吴恩达 · DeepLearning.AI', '课程', '先弄懂模型怎样从数据里学，后面才看得懂智能体和大模型在做什么。', '用自己的话说得清训练、验证、过拟合各是什么。', '自己训练出一个能用的分类模型，并说明它在没见过的数据上表现怎样。'],
      en: ['Machine Learning Specialization', 'Andrew Ng · DeepLearning.AI', 'Course', 'Knowing how a model learns from data makes everything about agents and LLMs easier to follow.', 'You can explain training, validation, and overfitting in your own words.', 'Train a working classifier yourself and report how it does on data it hasn’t seen.'] },
  ] },
  { zh: ['智能体', '会把任务交给智能体，也能自己搭一个简单的智能体。'], en: ['Agents', 'hand tasks to agents, and build a simple agent yourself.'], steps: [
    { slug: 'building-effective-agents', hours: 1, url: 'https://www.anthropic.com/engineering/building-effective-agents', ms: 'building-effective-agents-2024',
      zh: ['Building effective agents', 'Anthropic', '文章', '先分清工作流和智能体，知道什么时候不该用智能体。', '分得清工作流和智能体，知道文中几种搭法各适合什么样的任务。', '为自己的一件任务选工作流或智能体，写下理由。'],
      en: ['Building effective agents', 'Anthropic', 'Article', 'It separates workflows from agents and says when to skip the agent.', 'You can tell a workflow from an agent and know which pattern suits which kind of task.', 'Pick a workflow or an agent for one of your own tasks and write down why.'] },
    { slug: 'agentic-ai', hours: 10, url: 'https://www.deeplearning.ai/courses/agentic-ai', ms: 'react-2022',
      zh: ['Agentic AI', '吴恩达 · DeepLearning.AI', '课程', '把反思、调用工具、规划、多个智能体分工这几种做法，一个个亲手搭一遍。', '四种做法各搭过一遍，说得出每种在什么时候值得用。', '搭出一个会调用工具、会检查自己结果的智能体。'],
      en: ['Agentic AI', 'Andrew Ng · DeepLearning.AI', 'Course', 'You build reflection, tool use, planning, and multi-agent setups one at a time, by hand.', 'You have built each of the four patterns once and can say when each is worth using.', 'Build an agent that calls tools and checks its own results.'] },
    { slug: 'anthropic-academy', hours: 8, url: 'https://anthropic.skilljar.com/', ms: 'mcp-2024',
      zh: ['Claude Code、MCP、Agent Skills 课程', 'Anthropic Academy', '课程', '把智能体接进自己每天用的工具和代码库。', '会用 Claude Code 做完一件多步的任务，会接一个 MCP 服务，会写一个 Agent Skill。', '给自己的项目写一个 Agent Skill，让 Claude Code 照着它把一件事做完。'],
      en: ['Claude Code, MCP, and Agent Skills courses', 'Anthropic Academy', 'Course', 'They connect agents to the tools and codebases you already use every day.', 'You can finish a multi-step task in Claude Code, connect an MCP server, and write an Agent Skill.', 'Write an Agent Skill for your own project and have Claude Code follow it to finish a task.'] },
  ] },
  { zh: ['模型', '亲手训练一个小模型，理解大语言模型怎么工作。'], en: ['Models', 'train a small model yourself, and understand how large language models work.'], steps: [
    { slug: 'zero-to-hero', url: 'https://karpathy.ai/zero-to-hero.html', ms: 'transformer-2017',
      zh: ['Neural Networks: Zero to Hero（含 nanoGPT、nanochat）', 'Andrej Karpathy', '视频、代码', '亲手从零写出一个小的语言模型，才知道大模型里每一层在做什么。', '不看视频，自己写出 nanoGPT 的训练循环。', '用自己的一份文本训练出一个能续写的小模型；再把 nanochat 从头到尾跑通，讲清每个阶段在做什么。', '约 40 小时，nanochat 另约 20 小时'],
      en: ['Neural Networks: Zero to Hero (with nanoGPT and nanochat)', 'Andrej Karpathy', 'Videos and code', 'Writing a small language model from scratch shows you what each layer of a large one is doing.', 'You can write the nanoGPT training loop without the video.', 'Train a small model on your own text until it can continue it. Then run nanochat end to end and explain what each stage does.', 'about 40 hours, plus about 20 for nanochat'] },
    { slug: 'deep-learning-specialization', hours: 120, url: 'https://www.deeplearning.ai/courses/deep-learning-specialization/', ms: 'alexnet-2012',
      zh: ['深度学习专项课程', '吴恩达 · DeepLearning.AI', '课程', '把神经网络的常用结构和训练技巧系统地学一遍，读论文时不再卡在基本概念上。', '说得清卷积网络、序列模型和注意力各解决什么问题，知道训练不收敛时先查什么。', '不照抄作业，自己搭一个网络，把它训练到收敛。'],
      en: ['Deep Learning Specialization', 'Andrew Ng · DeepLearning.AI', 'Course', 'A systematic pass through the standard architectures and training techniques, so papers stop tripping you on the basics.', 'You can say what convolutional networks, sequence models, and attention are each for, and what to check first when training won’t converge.', 'Build a network without copying the assignments and train it until it converges.'] },
    { slug: 'cs336', hours: 150, url: 'https://cs336.stanford.edu/', ms: 'scaling-laws-2020',
      zh: ['CS336: Language Modeling from Scratch', '斯坦福大学', '课程', '从分词器到训练循环，把语言模型的每个部件亲手实现一遍。', '不调用现成的模型库，写出分词器、Transformer 和训练循环。', '完成第一次作业：用自己写的代码训练出一个能生成文字的小模型。'],
      en: ['CS336: Language Modeling from Scratch', 'Stanford University', 'Course', 'From the tokenizer to the training loop, you implement every part of a language model yourself.', 'You can write a tokenizer, a Transformer, and a training loop without a model library.', 'Complete the first assignment: train a small text-generating model with code you wrote.'] },
  ] },
  { zh: ['前沿', '跟上研究和新方法。'], en: ['Frontier', 'keep up with research and new methods.'], steps: [
    { slug: 'cs25', hours: 15, url: 'https://web.stanford.edu/class/cs25/',
      zh: ['CS25: Transformers United', '斯坦福大学', '视频', '一线研究者每周讲一个正在发生的方向。', '听得懂一讲里的方法，说得出它和 Transformer 原来的做法差在哪里。', '选一讲，写一页说清它解决什么问题、代价是什么。'],
      en: ['CS25: Transformers United', 'Stanford University', 'Videos', 'Each week a working researcher covers a direction that is moving right now.', 'You can follow the method in a talk and say how it departs from the original Transformer.', 'Pick one talk and write a page on the problem it solves and what it costs.'] },
    { slug: 'autoresearch', hours: 8, url: 'https://github.com/karpathy/autoresearch', ms: 'autoresearch-2026',
      zh: ['autoresearch', 'Andrej Karpathy', '代码', '看智能体怎样自己设计实验、跑实验、记结果。', '读得懂它的代码结构：智能体在哪一步提出实验，在哪一步判断结果。', '在一张 GPU 上跑通一晚的实验，读懂它留下的记录。'],
      en: ['autoresearch', 'Andrej Karpathy', 'Code', 'It shows an agent designing, running, and logging its own experiments.', 'You can read its code and point to where the agent proposes an experiment and where it judges the result.', 'Run it overnight on one GPU and read the log it leaves.'] },
  ] },
];
class Component extends DCLogic {
  renderVals() {
    const v = shellVals(this, 'ink', '/mind/learn');
    const L = v.en ? 'en' : 'zh';
    const c = COPY[L];
    const fmt = (iso) => v.en ? new Date(iso + 'T00:00:00Z').toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' }) : iso;
    const expand = (this.state && this.state.expand) ?? this.props.expand ?? '全部收起';   /* 展开一条：展开「Agentic AI」那一步，看原地展开的样子 */
    const levels = LEVELS.map((lv, i) => ({
      id: 'level-' + (i + 1), n: c.lvN(i + 1), name: lv[L][0], head: c.lvN(i + 1) + c.sep + lv[L][0], goal: lv[L][1], count: c.count(lv.steps.length),
      steps: lv.steps.map((s, k) => ({
        slug: s.slug, n: (i + 1) + '.' + (k + 1), url: s.url, name: s[L][0], why: s[L][3], level: s[L][4], check: s[L][5],
        open: expand === '展开一条' && s.slug === 'agentic-ai', closed: !(expand === '展开一条' && s.slug === 'agentic-ai'), openLabel: c.openCourse + (v.en ? ': ' : '：') + s[L][0],
        factList: [s[L][1], s[L][2], s[L][6] || c.hours(s.hours)].map((t, k) => ({ t: k ? '·\u00a0' + t : t })),   /* 间隔号跟着后一项走，不会单独落在行尾 */
        hasMs: !!s.ms, msHref: c.msBase + (s.ms || ''), msLabel: s.ms ? c.related + MS_NAMES[s.ms][L] : '',
      })),
    }));
    return { ...v, c, levels, checkedIso: CHECKED, checkedText: fmt(CHECKED) };
  }
  componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }
}
