/* ── 文章页的数据：界面字（随页面语言）、正文（随内容语言）、一条开发日志。Article 和 States 共用，由 pa-out/build.py 写进两块画板 ── */
const ART_SRC = 'https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model';
const ART_UI = {
  zh: {
    crumbLabel: '所在位置', lineHref: '/mind/collaboration', line: '人机协作', layer: 'Harness 工程',
    takeLabel: '我们的判断', shotKicker: '用大白话', sceneLabels: ['用大白话', '容易听错', '一个比喻', '不能译的原件', '一句话'],
    metaWho: '谁写的、什么时候', metaCheck: '我们核对了什么',
    dtAuthor: '作者', author: 'Zack Deveau，Shopify Engineering', dtOriginal: '原文', dOriginal: '2026-07-29', readOriginal: '读原文',
    dtPublished: '发布', dPublished: '2026-10-31', dtChecked: '最后核对', dChecked: '2026-11-04',
    dtApplies: '适用于', applies: 'Harness 工程，和具体模型无关', dtRights: '授权', rights: '讲解和摘要，不是全文翻译', dtOrigin: '起草', origin: '智能体起草，独立评审',
    dtLength: '时长', readTime: '12 分钟', hasVideo: '有 3 分钟视频',
    toc: '目录', tocPractice: '练习', notesLabel: '注释', backToText: '回到正文',
    play: '播放 3 分钟视频', video: '3 分钟视频', seek: '播放进度', videoTime: '0:00 / 2:24', capt: '字幕', transcript: '文字稿', voice: '旁白用合成音色「晓晓」。',
    videoFailTitle: '视频没能播放。', videoFailBody: '文字稿讲的是同一件事，就在下面。', retry: '重试',
    loading: '正在加载视频',
    noEnTitle: '', noEnBody: '', noEnCta: '', noEnEnd: '',
    next: '接着读', nextLead: '下一篇', nextKind: '人机协作 · Harness 工程', nextTitle: 'Claude Code 团队如何做 Code Review', nextHref: '/mind/claude-code-review',
    allLine: '人机协作的全部文章',
    workout: '今天的训练', workoutLine: '读完了，站起来练一练。第一次来，第一练 12 分钟；已经在练的，接着今天这一练。', workoutHref: '/app',
    toBuild: '去动手一站', toBuildLine: '把这个练习带过去，和智能体一起做一遍。',
    colophon: '更新记录和版权', changes: '更新记录', change2: '补充两处数字的来源说明', change1: '发布',
    source: '原文和授权', sourcePre: '原文：《', sourcePost: '》，Zack Deveau，Shopify Engineering，2026 年 7 月 29 日，英文。',
    reuse: '授权状态：本页是讲解和摘要，不是原文的译文，原文版权归 Shopify。转述和引用请链到原文；整页转载请先联系我们。',
    cite: '引用本文：Velicoach 看清，《比模型更耐久的 Harness》，2026 年 10 月 31 日，', citeUrl: 'velicoach.com/mind/shopify-harness', citeHref: '/mind/shopify-harness',
    report: '发现错误或过时的地方？改正后会记进更新记录。', reportLink: '写信指出', reportSubject: '纠错：https://velicoach.com/mind/shopify-harness',
  },
  en: {
    crumbLabel: 'Breadcrumb', lineHref: '/en/mind/collaboration', line: 'Human–AI collaboration', layer: 'Harness engineering',
    takeLabel: 'Our take', shotKicker: 'In plain words', sceneLabels: ['In plain words', 'Common misreading', 'An analogy', 'The original figures', 'In one sentence'],
    metaWho: 'Author and dates', metaCheck: 'What we checked',
    dtAuthor: 'Author', author: 'Zack Deveau, Shopify Engineering', dtOriginal: 'Original', dOriginal: 'Jul 29, 2026', readOriginal: 'Read the original',
    dtPublished: 'Published', dPublished: 'Oct 31, 2026', dtChecked: 'Last checked', dChecked: 'Nov 4, 2026',
    dtApplies: 'Applies to', applies: 'Harness engineering, any model', dtRights: 'Rights', rights: 'Summary and commentary, not a translation', dtOrigin: 'Drafting', origin: 'AI-drafted, independently reviewed',
    dtLength: 'Length', readTime: '9 min read', hasVideo: '3-minute video',
    toc: 'Contents', tocPractice: 'Exercise', notesLabel: 'Notes', backToText: 'Back to the text',
    play: 'Play the 3-minute video', video: '3-minute video', seek: 'Playback position', videoTime: '0:00 / 2:21', capt: 'Captions', transcript: 'Transcript', voice: 'Narrated by Andrew, a synthetic voice.',
    videoFailTitle: 'The video didn’t play. ', videoFailBody: 'The transcript below covers the same ground.', retry: 'Try again',
    loading: 'Loading the video',
    noEnTitle: 'Only in Chinese for now. ', noEnBody: 'The 3-minute video has English narration and captions; the write-up below is in Chinese, and ', noEnCta: 'the original post', noEnEnd: ' is in English.',
    next: 'Keep reading', nextLead: 'Next', nextKind: 'Human–AI collaboration · Harness engineering', nextTitle: 'How the Claude Code team does code review', nextHref: '/en/mind/claude-code-review',
    allLine: 'Everything in Human–AI collaboration',
    workout: 'Today’s workout', workoutLine: 'Done reading? Get up and train. New here: your first session takes 12 minutes. Already training: pick up today’s.', workoutHref: '/app',
    toBuild: 'Go to Build', toBuildLine: 'Take this exercise with you and run it with an agent.',
    colophon: 'Changes and rights', changes: 'Changes', change2: 'Added sources for two figures', change1: 'Published',
    source: 'Source and rights', sourcePre: 'Original: “', sourcePost: '” by Zack Deveau, Shopify Engineering, July 29, 2026.',
    reuse: 'Rights: this page is a summary with commentary, not a translation. The original is copyright Shopify. Quote it with a link to the original, and ask us before republishing the page.',
    cite: 'Cite as: Velicoach Mind, “A harness that outlasts the model,” October 31, 2026, ', citeUrl: 'velicoach.com/en/mind/shopify-harness', citeHref: '/en/mind/shopify-harness',
    report: 'Spotted an error or something out of date? We log every fix in the change list.', reportLink: 'Email a correction', reportSubject: 'Correction: https://velicoach.com/en/mind/shopify-harness',
  },
};
/* 正文沿用旧稿，不改；视频第一幕的标题和文字稿来自仓库 src/content/explainers.ts 的 shopify-harness。
   「我们的判断」、视频封面的眉标、文字稿每一幕的小标是界面字（ART_UI），跟页面语言走，不跟内容语言走：「暂无英文版」的英文页上它们是英文。
   视频也跟页面语言走（第一幕的标题、文字稿、旁白，explainers.ts 两种语言都有）：「暂无英文版」的英文页放英文旁白，字幕默认打开（联审 C-06） */
const ART_CONTENT = {
  zh: {
    title: '比模型更耐久的 Harness',
    dek: 'Shopify 团队用测试证明漏洞，而不是收集模型给出的候选清单。Harness 指套在模型外面的那层软件：工具、权限、检查和脚本。',
    takeHead: '值得读。', take: '适合在做代码审查、安全扫描自动化的工程师。它讲清了一件容易被忽略的事。换一个更强的模型，可能只带来更多要人确认的候选。真正留得下来的，是能证明结论的那层软件。代价是先要写出能证明问题的测试，前期投入比直接让模型去找大。',
    shotTitle: '证明不了，就不算发现',
    scenes: [
      { say: 'Shopify 应用安全团队做的不是让模型列出可能的漏洞。他们要一张能证明漏洞真的可以被利用的测试。证明不了，就不算发现。理论上的发现不计。模型会换。Harness 留下。' },
      { say: '更强的模型不等于更少的噪声。他们评估了大约五个月。新模型更能提出候选，也制造更多要确认的东西。有一次审计，三十多个候选，验证之后全部被降级、判成误报，或改记为纵深防御。所以耐久的资产不是当周的模型，而是周围那层软件：循环、工具、分区、证明和确定性脚本。' },
      { say: '模型像会换的筛网。Harness 是筛子的框、阶段和记录。框比网耐用。Dispatch 是那个轻的 Ruby 编排器。扫描按阶段走：引导测试、写架构、编目、分区、搜寻、验证、后处理、报告、修复。不能用真实集成测试证明可利用性的发现不被接受。' },
      { say: '原文有一张头图和三张手绘图，图里的英文不译。头图没有图注。一张图题是 DISPATCH，画了 Ruby、sandbox、proxy 和允许的主机。一张画了 PARALLEL 的搜寻和 SEQUENTIAL 的验证。一张画了 shared scope 和 partition scope。阶段名 Test bootstrap、Hunting、Verification 也保留英文。这些图按原文件嵌在正文里。' },
      { say: '模型会换。留下的是循环、分区、证明和确定性脚本。原文里的六周账是内部估算：八十多个应用，三百多个发现，其中两个按内部严重性会记为 Critical，总价值保守估在超过四十万美元的等值赏金。这不是公开赏金的支付记录，也不是本站复测。' },
    ],
    p1: '智能体报出来的漏洞，怎么知道是真的？Shopify 团队的回答是「测试预言」（test oracle）。它用一个测试来判定一条结论是真是假。',
    p1b: '他们的智能体先在软件里找漏洞，再用真实的集成测试证明漏洞能被利用。之后给出符合 Shopify 代码习惯的修复，最后才交给开发者。',
    h2a: '更强的模型带来更多噪声',
    p2: '团队在这套 Harness 里评估安全方向的前沿模型，前后约五个月。新模型比基线更能提出候选发现，但更好的搜索也带来更多要确认的噪声。一次审计中，模型提出了 30 多个候选漏洞。验证之后，没有一个保住原来的级别。它们要么降为中低危，要么判为误报，要么改记为纵深防御。纵深防御是多加的一层防护，本身不算', p2e: '漏洞。',
    n1: '数字来自原文描述的一次内部审计，不是公开数据集上的结果。',
    p3: '所以耐久的资产不是当周的模型，而是模型周围那层软件：循环、工具、代码分区、证明和确定性脚本。分区是把同一领域或功能的文件分成一组，每组约占模型上下文窗口的两三成。',
    h2b: '编排器 Dispatch',
    p4: '内部的编排器叫 Dispatch，是一个轻量的 Ruby 客户端。写扫描的人可以很快写出专找某一类缺陷的智能体，和通用的智能体一起跑。智能体按固定顺序的几个阶段运行。用真实的集成测试证明不了的发现，要么不接受，要么降成「低」或「中」。',
    h2c: '六周的账',
    p5: '到目前为止，团队完整扫描了 80 多个应用。约六周里，扫描跑了数千次，产出 300 多个发现。其中 2 个按 Shopify 内部的严重性分级，会记为「严重」（Critical）。团队保守估计，这批发现相当于超过 40 万美元的漏洞', p5e: '赏金。',
    n2: '这是原文给出的内部估算，不是公开赏金的支付记录。',
    practiceKicker: '练习 · 约 1 小时', practiceTitle: '先写证明，再让智能体去找',
    practiceBody: '在自己的项目里挑一类问题，比如越权访问。先写一个只在问题真实存在时才会失败的集成测试，再让智能体去找。只接受能让这个测试失败的发现。最后数一数：它提出了多少条，有几条真的成立。',
  },
  en: {
    title: 'A harness that outlasts the model',
    dek: 'Shopify’s team proves vulnerabilities with tests instead of collecting candidate lists from a model. A harness is the software around the model: tools, permissions, checks, and scripts.',
    takeHead: 'Worth reading. ', take: 'It’s for engineers automating code review or security scanning, and it makes a point that’s easy to miss. A stronger model may only hand you more candidates to confirm; what lasts is the software that proves a finding. The cost comes up front: you write tests that prove a problem exists before the model starts looking.',
    shotTitle: 'No proof, no finding',
    scenes: [
      { say: 'Shopify’s application security team doesn’t ask a model to list possible vulnerabilities. It asks for a test that proves a vulnerability can really be exploited. No proof, no finding. Theoretical findings don’t count. The model will change. The harness stays.' },
      { say: 'A stronger model doesn’t mean less noise. The team evaluated models for about five months. Newer models proposed more candidates, and left more to confirm. In one audit, more than 30 candidates were all downgraded, ruled false positives, or reclassified as defense in depth once they were validated. So the durable asset isn’t this week’s model. It’s the software around it: loops, tools, partitions, proofs, and deterministic scripts.' },
      { say: 'Think of the model as the mesh of a sieve, the part you replace. The harness is the frame, the stages, and the records, and the frame outlasts the mesh. Dispatch is the lightweight Ruby orchestrator. A scan moves through stages: test bootstrap, architecture, cataloging, partitioning, hunting, verification, post-processing, reporting, and fixing. A finding that a real integration test can’t prove exploitable is not accepted.' },
      { say: 'The original has a header image and three hand-drawn diagrams. One is titled DISPATCH and shows Ruby, the sandbox, the proxy, and the allowed hosts. One shows PARALLEL hunting and SEQUENTIAL verification. One shows shared scope and partition scope. They appear in the article as the original files.' },
      { say: 'The model will change. What stays is the loops, the partitions, the proofs, and the deterministic scripts. The six-week numbers are the post’s own estimate: more than 80 apps, more than 300 findings, two that would rate Critical internally, conservatively valued at more than $400,000 in equivalent bounties. That is not a record of bounties paid, and we did not re-test it.' },
    ],
    p1: 'How do you know a vulnerability an agent reports is real? Shopify’s team answers with a test oracle: a test that decides whether a finding is true.',
    p1b: 'Their agent looks for vulnerabilities, then proves each one is exploitable with a real integration test. Next it proposes a fix that follows Shopify’s conventions. Only then does a developer see it.',
    h2a: 'Stronger models, more noise',
    p2: 'The team spent about five months evaluating frontier security models inside this harness. Newer models proposed more candidate findings than the baseline, but better search also produced more noise to confirm. In one audit the model proposed more than 30 candidate vulnerabilities. After validation, none kept its original rating: each was downgraded to low or medium, found to be a false positive, or reclassified as defense in depth, an extra layer of protection rather than a ', p2e: 'vulnerability.',
    n1: 'The figure comes from one internal audit described in the post, not from a public dataset.',
    p3: 'So the durable asset isn’t this week’s model. It’s the software around it: loops, tools, code partitions, proofs, and deterministic scripts. A partition groups files from the same domain or feature, sized to about 20–30% of the model’s context window.',
    h2b: 'Dispatch, the orchestrator',
    p4: 'The internal orchestrator, Dispatch, is a lightweight Ruby client. Scan authors can quickly build agents that hunt one class of bug, and these run alongside generalist agents. Agents run through stages in a fixed order. Findings that a real integration test can’t prove are either rejected or downgraded to Low or Medium.',
    h2c: 'Six weeks in numbers',
    p5: 'So far the team has fully scanned more than 80 apps. In roughly six weeks it ran thousands of scans and produced more than 300 findings. Two would rate Critical on Shopify’s internal severity scale. The team conservatively values the findings at more than $400,000 in equivalent bug ', p5e: 'bounties.',
    n2: 'This is the post’s internal estimate, not a record of bounties paid.',
    practiceKicker: 'Exercise · about 1 hour', practiceTitle: 'Write the proof first, then let an agent search',
    practiceBody: 'Pick one class of bug in your own project, such as broken access control. Write an integration test that fails only when the bug really exists. Then let an agent search, and accept only findings that make the test fail. Count what it proposes and how much of it holds up.',
  },
};
/* 单条开发日志（PRD F19，复用文章页的版式）。这一条的出处是 thin-muscle-coach PR #84 的合并提交 eb70c77（路由表，ADR-0032，2026-11-04 合并）；这个仓库不公开，只写提交号、不带链接（PRD F19）；标题、日期和动手页、项目页的同一条日志（build-out/gen/parts.py 的 one-domain）一致。
   字段：字段是日期、项目、做了什么、和智能体怎么分工、下一步、PR 或提交链接 */
const ART_LOG = {
  zh: {
    crumbLabel: '所在位置', projectHref: '/build/velicoach', project: 'Velicoach 主站',
    title: '两个产品共用一个域名：按路径分给主站和 Veli', dek: '主站和 Veli 按路径分一个域名：哪些地址归主站，哪些归 Veli。',
    metaLabel: '日期、项目和链接', dtDate: '日期', dDate: '2026-11-04', dtProject: '项目', dtPr: '提交', pr: 'thin-muscle-coach 提交 eb70c77',
    hDid: '做了什么',
    did1: 'velicoach.com 下面有两个产品，各在一个仓库里：主站和 Veli。我们按路径把地址分开。首页、看清、动手和关于归主站。站稳页、Veli 网页版、登录和法务页归 Veli。',
    did2: '规则按顺序匹配，具体的前缀写在前面。英文路径里站稳页和法务页归 Veli，所以它们的规则写在主站的英文路径前面。',
    hSplit: '和智能体怎么分工', split: '产品负责人定哪些地址归主站、哪些归 Veli；智能体写路由表和分流规则。',
    hNext: '下一步', nextStep: '主站接管根域名，其余地址转给 Veli。在那之前，根路径临时跳转到站稳页。',
    hLinks: 'PR 和提交', linkNote: '：路由表（ADR-0032），在 Veli 的仓库里，已合并。这个仓库不公开，所以只写提交号。',
    next: '接着读', nextDate: '2026-11-04', nextTitle: '首页的「叶与网」动效回到设计稿里：约 6000 个点在叶子和网之间变形', nextHref: '/build/velicoach/home-motion',
    allProject: 'Velicoach 主站的全部开发日志', allLogs: '全部项目的开发日志', allLogsHref: '/build#devlog',
    colophon: '纠错', report: '发现错误或过时的地方？', reportLink: '写信指出', reportSubject: '纠错：https://velicoach.com/build/velicoach/one-domain',
  },
  en: {
    crumbLabel: 'Breadcrumb', projectHref: '/en/build/velicoach', project: 'Velicoach',
    title: 'Two products now share one domain, split by path between this site and Veli', dek: 'How the main site and Veli split one domain by path, and which URLs belong to which.',
    metaLabel: 'Date, project, and links', dtDate: 'Date', dDate: 'Nov 4, 2026', dtProject: 'Project', dtPr: 'Commit', pr: 'thin-muscle-coach commit eb70c77',
    hDid: 'What we did',
    did1: 'velicoach.com hosts two products, each in its own repository: the main site and Veli. We split the URLs by path. The home page, Mind, Build, and About belong to the main site. The Body page, the Veli web app, sign-in, and the legal pages belong to Veli.',
    did2: 'Rules match in order, so the specific prefixes come first. In English, the Body page and the legal pages still belong to Veli, so their rules sit ahead of the main site’s English paths.',
    hSplit: 'How we split the work with agents', split: 'The product owner decided which URLs belong to the main site and which to Veli. Agents wrote the routing table and the rewrite rules.',
    hNext: 'Next', nextStep: 'The main site takes over the root domain and hands every other URL to Veli. Until then, the root path redirects to the Body page.',
    hLinks: 'Pull requests and commits', linkNote: ': the routing table (ADR-0032), in Veli’s repository, merged. That repository is private, so only the commit hash is shown.',
    next: 'Keep reading', nextDate: 'Nov 4, 2026', nextTitle: 'The home page’s leaf-and-web animation is back in the design file: about 6,000 points morph between a leaf and a web', nextHref: '/en/build/velicoach/home-motion',
    allProject: 'All Velicoach devlog entries', allLogs: 'The devlog for every project', allLogsHref: '/en/build#devlog',
    colophon: 'Corrections', report: 'Spotted an error or something out of date?', reportLink: 'Email a correction', reportSubject: 'Correction: https://velicoach.com/en/build/velicoach/one-domain',
  },
};
/* v：shellVals() 的结果；o：{ kind, media, english, frame, scrolled, scrollAt }。「暂无英文版」时调用方先把页面语言定成英文 */
function articleVals(v, o) {
  const L = v.en ? 'en' : 'zh';
  const isLog = o.kind === '开发日志';
  const noEnglish = !isLog && o.english === '暂无英文版';
  const CL = noEnglish ? 'zh' : L;
  const u = { ...ART_UI[L] };
  const g = { ...ART_LOG[L] };
  const mail = (s) => 'mailto:' + SITE_CONFIG.contactEmail + '?subject=' + encodeURIComponent(s);
  u.reportHref = mail(u.reportSubject); g.reportHref = mail(g.reportSubject); u.srcHref = ART_SRC;
  const media = isLog ? '没有视频' : (o.media || '正常');
  const hasVideo = media !== '没有视频';
  const scrolled = !!o.scrolled;
  const atVideo = scrolled && hasVideo && o.scrollAt === '视频';
  const frame = o.frame || '封面';
  const readTime = noEnglish ? '12 min read, in Chinese' : u.readTime;
  return {
    u, g, c: ART_CONTENT[CL], contentLang: CL === 'en' ? 'en' : 'zh-CN',
    vc: ART_CONTENT[L], videoLang: L === 'en' ? 'en' : 'zh-CN', ccOn: noEnglish ? 'true' : 'false',
    scenes: ART_CONTENT[L].scenes.map((s, i) => ({ k: u.sceneLabels[i], say: s.say })),
    isArticle: !isLog, isLog, noEnglish,
    curMind: isLog ? 'false' : 'page', curBuild: isLog ? 'page' : 'false',
    artClass: scrolled ? 'is-scrolled' : '', atTop: !scrolled, scrolled, atVideo,
    videoOk: media === '正常', videoLoading: media === '视频加载中' || media === '视频加载超过 10 秒', videoSlow: media === '视频加载超过 10 秒', videoQuick: media === '视频加载中', videoFailed: media === '视频无法播放',
    length: hasVideo ? readTime + ' · ' + u.hasVideo : readTime,
    videoTime: u.videoTime,
    voice: u.voice,
    frameText: frame !== '最暗一帧', frameKey: { '最亮一帧': 'brightest', '最暗一帧': 'darkest' }[frame] || 'cover', frameClass: frame === '最亮一帧' ? 'is-bright' : '', frameHidden: frame === '封面' ? 'false' : 'true',
  };
}
