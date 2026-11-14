class Component extends DCLogic {
  renderVals() {
    const P = (k, d) => (this.state && this.state[k]) ?? this.props[k] ?? d;
    const v = shellVals(this, 'ink', '/mind');
    return { ...v, ...mindVals(this, v, { line: P('line', 'AI 发展史（/mind）'), network: P('network', '在线'), expand: P('expand', '全部收起') }) };
  }
  componentDidMount() {
    if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el));
    /* 从别的页带锚点进来（/mind#<里程碑>、/mind/learn#<步骤>）：那一条原地展开并标出，滚到它（联审 C-08） */
    const id = decodeURIComponent((location.hash || '').slice(1));
    const t = id && document.getElementById(id);
    if (t && t.matches('.vc-ms, .vc-step')) { const d = t.querySelector('details'); if (d) d.open = true; t.classList.add('is-target'); t.scrollIntoView({ block: 'start' }); }
  }
}
