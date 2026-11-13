/* 关于页的文案（PRD F23 和第 1、6 节；事实只用 PRD 和 docs/standards/pipeline.md 里有的） */
const COPY = {
  zh: {
    kicker: '关于 Velicoach', title: 'AGI 路上的陪练',
    lead: 'AI 走得越快，越要先站稳。Velicoach 陪你做两件事：把身体练强，学会和 AI 一起做事。',
    whoTitle: '我们是谁',
    who: 'Velicoach 有三站，各管一件事。站稳：把身体练强。看清：弄懂 AI 是怎么一步步走到今天的。动手：和智能体一起把东西做出来。站稳一站的产品叫 Veli，里面的 AI 力量训练教练叫威利。',
    whyTitle: '为什么做这件事',
    why1: 'AGI 正在到来，让人兴奋，也让人不安。我们看到三个问题。屏幕前的时间越来越长，身体在走下坡，却很少有人系统地练力量。AI 资讯太多，不知道该读什么、学什么，也不知道该把哪些事交给智能体。想用 AI 做点东西的人，缺少可以照着做的方法和真实案例。',
    why2: '所以我们做陪练，不做媒体：陪你练，陪你学，陪你动手。我们也做一份见证：记下 AI 的路线是怎么变的，也记下我们自己怎样和智能体一起把东西做出来。',
    keepTitle: '谁在维护',
    keep: [
      { n: '1', q: '谁在维护', a: '这个站由一位产品负责人和 AI 智能体一起维护。' },
      { n: '2', q: '哪些内容由智能体起草', a: '文章、里程碑、学习路径步骤和开发日志由智能体起草；每周的订阅邮件只用已发布的内容拼成。训练指导只在 Veli 里。新开栏目，以及法律、付费和对外承诺，由产品负责人决定。' },
      { n: '3', q: '怎么核对', a: '发布前，另一个没看过写作过程的智能体独立评审：核对事实、数字和出处，确认英文是按英语读者重写的。健康内容只引用系统综述和大样本研究，并写明研究类型和样本量。文章、里程碑和学习路径步骤都标最后核对日期。' },
      { n: '4', q: '错了怎么纠正', a: '每篇文章末尾有纠错入口，你也可以直接写信。改正后记进那一篇的更新记录。产品负责人可以撤下任何一篇；撤下后，那个地址显示「页面不存在」，首页和 RSS 随之更新。' },
    ],
    contactTitle: '联系', contact: '发现错误、想转载，或者想告诉我们一件事，都可以写信。', contactCta: '写信给我们',
    startTitle: '从一站开始', bodyLine: '每周两次力量训练。', mindLine: '读懂 AI 从哪里来。', buildLine: '和智能体一起做出东西。',
  },
  en: {
    kicker: 'About Velicoach', title: 'An AGI-era training partner',
    lead: 'The faster AI moves, the more it pays to get strong first. Velicoach trains with you on two things: a stronger body, and working well with AI.',
    whoTitle: 'Who we are',
    who: 'Velicoach has three stations, each with one job. Body: get stronger. Mind: understand how AI got here, step by step. Build: make things with agents. Body’s product is Veli, an AI strength coach.',
    whyTitle: 'Why we do this',
    why1: 'AGI is arriving, and it is both exciting and unsettling. We see three problems. Screen time keeps growing and bodies keep declining, yet few people train strength with any system. There is too much AI news to know what to read, what to learn, or which work to hand to an agent. And people who want to build with AI lack methods they can follow and real cases to learn from.',
    why2: 'So we set out to be a training partner, not a media outlet: we train with you, learn with you, and build with you. We also keep a record of how AI’s direction has changed, and of how we ourselves build things with agents.',
    keepTitle: 'Who maintains this site',
    keep: [
      { n: '1', q: 'Who maintains it', a: 'One product owner and AI agents maintain this site together.' },
      { n: '2', q: 'What agents draft', a: 'Agents draft the articles, milestones, learning-path steps, and devlog entries. The weekly email is assembled only from published content. Training guidance lives only in Veli. Opening a new section, and anything legal, paid, or promised in public, is the product owner’s call.' },
      { n: '3', q: 'How we check', a: 'Before anything is published, a second agent that never saw the drafting reviews it independently. It checks facts, numbers, and sources, and confirms the English was rewritten for English readers. Health content cites only systematic reviews and large studies, and states the study type and sample size. Articles, milestones, and learning-path steps all show the date we last checked them.' },
      { n: '4', q: 'How we correct mistakes', a: 'Every article ends with a link for corrections, or you can email us. Each fix is logged in that article’s change list. The product owner can take down any piece. After that its URL shows “Page not found,” and the home page and RSS update to match.' },
    ],
    contactTitle: 'Contact', contact: 'Found a mistake, want to republish something, or have something to tell us? Email us.', contactCta: 'Email us',
    startTitle: 'Start at a station', bodyLine: 'Strength training, twice a week.', mindLine: 'Understand where AI came from.', buildLine: 'Make things with agents.',
  },
};
class Component extends DCLogic {
  renderVals() {
    const v = shellVals(this, 'paper', '/about');
    return { ...v, c: COPY[v.en ? 'en' : 'zh'] };
  }
  componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }
}
