class Component extends DCLogic {
  renderVals() {
    const P = (k, d) => (this.state && this.state[k]) ?? this.props[k] ?? d;
    const kind = P('kind', '文章');
    const noEnglish = kind !== '开发日志' && P('english', '有英文版') === '暂无英文版';
    /* 「暂无英文版」只出现在英文页：页面语言定成英文，正文仍是中文 */
    const self = noEnglish ? { state: { ...(this.state || {}), lang: 'English' }, props: this.props, setState: (s) => this.setState(s) } : this;
    /* 语言切换链到本页的另一语言版本：文章是 /mind/<slug>，单条开发日志是 /build/<项目>/<slug> */
    const v = shellVals(self, 'paper', kind === '开发日志' ? '/build/velicoach/one-domain' : '/mind/shopify-harness');
    return { ...v, ...articleVals(v, { kind, media: P('media', '正常'), english: noEnglish ? '暂无英文版' : '有英文版', load: P('load', '正常'), frame: P('frame', '封面'), scrolled: P('nav', '首屏') === '吸顶' }) };
  }
  componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }
}
