/* 页面状态画板：页面不存在是自己的一页；网络断开、订阅失败就是看清首页换状态（mindVals）；
   加载中、加载超过 10 秒、视频无法播放、文章暂无英文版就是文章页换状态（articleVals），加载只发生在视频（PRD 第 527 版「页面状态」）。这里只有「页面不存在」的文案 */
const ST_COPY = {
  zh: {
    nfTitle: '这一页不在这里', nfLead: '地址可能输错了，也可能这篇已经撤下或换了位置。从三站里选一个进去。',
    bodyLine: '每周两次力量训练。', mindLine: '读懂 AI 从哪里来。', buildLine: '和智能体一起做出东西。',
  },
  en: {
    nfTitle: 'This page isn’t here', nfLead: 'The link may be mistyped, or the piece was taken down or moved. Pick one of the three stations to carry on.',
    bodyLine: 'Strength training, twice a week.', mindLine: 'Understand where AI came from.', buildLine: 'Make things with agents.',
  },
};
class Component extends DCLogic {
  renderVals() {
    const page = this.props.page ?? '页面不存在';
    const noEnglish = page === '文章暂无英文版';
    const self = noEnglish ? { state: { ...(this.state || {}), lang: 'English' }, props: this.props, setState: (s) => this.setState(s) } : this;
    const VIDEO = { '加载中': '视频加载中', '加载超过 10 秒': '视频加载超过 10 秒', '视频无法播放': '视频无法播放' };
    const inArticle = !!VIDEO[page] || noEnglish;
    const isNotFound = page === '页面不存在';
    const v = shellVals(self, inArticle || isNotFound ? 'paper' : 'ink', isNotFound ? '/' : inArticle ? '/mind/shopify-harness' : '/mind');
    const a = articleVals(v, { kind: '文章', media: VIDEO[page] || '正常', english: noEnglish ? '暂无英文版' : '有英文版' });
    const m = mindVals(this, v, { line: 'AI 发展史（/mind）', network: page === '网络断开' ? '离线' : '在线', expand: '全部收起' });
    /* 订阅失败：页底订阅一定在，默认给「格式不对」，另两种原因用属性 subscribe 切换 */
    const subFail = page === '订阅失败';
    const sub = subFail && !v.subHasError ? { subOn: true, formShown: true, barDone: false, subHasError: true, subError: v.t.errFormat, subInvalid: 'true', subValue: 'name@', subButton: v.t.subscribe, subBusy: 'false' } : (subFail ? { subOn: true } : {});
    return {
      ...v, ...m, ...a, ...sub, c: inArticle ? a.c : m.c, p: ST_COPY[v.en ? 'en' : 'zh'],
      curMind: isNotFound ? 'false' : 'page', curBuild: 'false',
      isNotFound, inArticle, inList: !isNotFound && !inArticle,
    };
  }
  componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }
}
