class Component extends DCLogic {
  renderVals() {
    const P = (k, d) => (this.state && this.state[k]) ?? this.props[k] ?? d;
    const kind = P('kind', '文章');
    const noEnglish = kind !== '开发日志' && P('english', '有英文版') === '暂无英文版';
    /* 「暂无英文版」只出现在英文页：页面语言定成英文，正文仍是中文 */
    const self = noEnglish ? { state: { ...(this.state || {}), lang: 'English' }, props: this.props, setState: (s) => this.setState(s) } : this;
    /* 语言切换链到本页的另一语言版本：文章是 /mind/<slug>，单条开发日志是 /build/<项目>/<slug> */
    const v = shellVals(self, 'paper', kind === '开发日志' ? '/build/velicoach/one-domain' : '/mind/shopify-harness');
    const a = articleVals(v, { kind, media: P('media', '正常'), english: noEnglish ? '暂无英文版' : '有英文版', load: P('load', '正常'), frame: P('frame', '封面'), scrolled: P('nav', '首屏') === '吸顶', scrollAt: P('scrollAt', '正文中段') });
    /* 吸顶玻璃压在视频上：和播放条一样换成 lg-on-dark（浅色字），浅色主题下黑字对暗画面不到 4.5:1 */
    return { ...v, ...a, navClass: a.atVideo ? v.navClass + ' lg-on-dark' : v.navClass };
  }
  componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }
}
