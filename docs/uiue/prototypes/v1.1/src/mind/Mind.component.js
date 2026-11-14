class Component extends DCLogic {
  renderVals() {
    const P = (k, d) => (this.state && this.state[k]) ?? this.props[k] ?? d;
    const v = shellVals(this, 'ink', '/mind');
    return { ...v, ...mindVals(this, v, { line: P('line', 'AI 发展史（/mind）'), network: P('network', '在线'), expand: P('expand', '全部收起'), words: P('words', '未配置') }) };
  }
  componentDidMount() {
    if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el));
    revealHashTarget();
    window.addEventListener('hashchange', revealHashTarget);
  }
  componentWillUnmount() { window.removeEventListener('hashchange', revealHashTarget); }
}
