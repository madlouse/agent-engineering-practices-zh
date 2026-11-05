/* 液态玻璃的浏览器端工具（references/liquid-glass.md 第 3、4 节）。无依赖。
   普通 <script> 和 ES 模块（import './liquid-glass.js'）都能用，接口挂在 globalThis.LiquidGlass：
     attachLens(el, { split = 0.15 })   给表面加边缘透镜（只在 Chromium 上），返回取消函数
     sample(el, source)                 在 source（可读的 img / canvas / video）里取 el 背后的 5×3 网格，返回 {lum, texture, chroma} 或 null
     adaptInk(els, source, { dark })    按背后决定墨色和密度；一组相邻的表面共用一个决定
     supportsLens()                     这个浏览器能不能画 backdrop-filter 里的 url() */
(function () {
  'use strict';
  const tileCache = new Map();   // 按「圆角 × rim × 超椭圆指数」缓存角上的位移图
  let uid = 0;

  function supportsLens() {
    if (typeof CSS === 'undefined' || !CSS.supports('backdrop-filter', 'url(#a)')) return false;
    const ua = navigator.userAgent;
    if (/Firefox|FxiOS/.test(ua)) return false;                       // 认得写法，什么都不画
    const brands = navigator.userAgentData && navigator.userAgentData.brands;
    if (brands) return brands.some(b => /Chromium/.test(b.brand));
    return /Chrome\//.test(ua) && !/Version\/[\d.]+ .*Safari/.test(ua); // Safari 的 @supports 也会通过，却不画
  }

  function reducedTransparency() {
    return matchMedia('(prefers-reduced-transparency: reduce), (forced-colors: active)').matches;
  }

  // 边缘宽度：rim = max(4, min(44, 短边 / 3.5))
  const rimFor = (w, h) => Math.max(4, Math.min(44, Math.min(w, h) / 3.5));
  // 离边缘 d 的点向内看的距离：1.1 × rim × (1 - d / rim)^2.6；边上最狠，到 rim 内沿为 0
  const bend = (d, rim) => (d >= rim ? 0 : 1.1 * rim * Math.pow(1 - Math.max(d, 0) / rim, 2.6));

  /* 角上的一块位移图（左上角，大小 S×S）。d 是到圆角边的距离，n=2 是圆弧，n>2 近似 superellipse。
     红 = 横向偏移、绿 = 纵向偏移，128 不动；偏移按 maxOff 归一。 */
  function cornerTile(r, rim, n) {
    const key = r + '|' + rim + '|' + n;
    if (tileCache.has(key)) return tileCache.get(key);
    const S = Math.ceil(Math.max(r, rim)) + 1, maxOff = 1.1 * rim;
    const c = document.createElement('canvas'); c.width = c.height = S;
    const ctx = c.getContext('2d'), img = ctx.createImageData(S, S);
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      const px = x + 0.5, py = y + 0.5;
      let d, nx, ny;                      // 到边的距离、向内的单位法线
      const qx = r - px, qy = r - py;     // 在圆角区域里，qx、qy 都为正
      if (qx > 0 && qy > 0 && r > 0) {
        const len = Math.pow(Math.pow(qx, n) + Math.pow(qy, n), 1 / n);
        d = r - len;
        const gx = Math.pow(qx, n - 1), gy = Math.pow(qy, n - 1), gl = Math.hypot(gx, gy) || 1;
        nx = gx / gl; ny = gy / gl;       // 指向圆心方向的反面是向外；这里取向内：沿 +x、+y
      } else if (px < py) { d = px; nx = 1; ny = 0; } else { d = py; nx = 0; ny = 1; }
      const m = bend(d, rim) / maxOff;    // 0–1
      const i = (y * S + x) * 4;
      img.data[i] = 128 + Math.round(nx * m * 127);
      img.data[i + 1] = 128 + Math.round(ny * m * 127);
      img.data[i + 2] = 128; img.data[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    const tile = { canvas: c, S, maxOff };
    tileCache.set(key, tile);
    return tile;
  }

  /* 用角上的那一块拼出整张图：四个角翻转摆放，四条边拉伸角块的最后一列 / 行，中间平涂 128。
     尺寸变了只重新拼（很便宜），不重算像素。 */
  function composeMap(w, h, tile) {
    const { canvas: t, S } = tile;
    const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h));
    const ctx = c.getContext('2d');
    ctx.fillStyle = 'rgb(128,128,128)'; ctx.fillRect(0, 0, c.width, c.height);
    const W = c.width, H = c.height, s = Math.min(S, Math.floor(W / 2), Math.floor(H / 2));
    // 每个角：左上原样；右上水平翻转要把红色反过来，所以分通道处理——简单做法是逐角画像素
    const src = t.getContext('2d').getImageData(0, 0, S, S).data;
    const out = ctx.getImageData(0, 0, W, H), o = out.data;
    const put = (x, y, sx, sy, fx, fy) => {
      const si = (sy * S + sx) * 4, oi = (y * W + x) * 4;
      o[oi] = fx ? 256 - src[si] : src[si]; o[oi + 1] = fy ? 256 - src[si + 1] : src[si + 1];
      o[oi + 2] = 128; o[oi + 3] = 255;
    };
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const fx = x >= W / 2, fy = y >= H / 2;
      const lx = fx ? W - 1 - x : x, ly = fy ? H - 1 - y : y;  // 折到左上象限
      if (lx >= s && ly >= s) continue;                         // 中间：不动
      put(x, y, Math.min(lx, s - 1), Math.min(ly, s - 1), fx, fy);  // 角块；边上拉伸最后一列 / 行
    }
    ctx.putImageData(out, 0, 0);
    return c.toDataURL();
  }

  /* 独立的 <svg>、唯一 id。色散：红多偏 15%、蓝少偏 15%，各用 feColorMatrix 只留自己的通道，再用 screen 叠回。 */
  function buildFilter(id, w, h, scale, split) {
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('width', '0'); svg.setAttribute('height', '0'); svg.setAttribute('aria-hidden', 'true');
    svg.style.position = 'absolute';
    const ch = (k, s) => `<feDisplacementMap in="SourceGraphic" in2="map" scale="${(scale * s).toFixed(2)}" xChannelSelector="R" yChannelSelector="G" result="d${k}"/>` +
      `<feColorMatrix in="d${k}" type="matrix" values="${k === 'r' ? '1 0 0 0 0 0 0 0 0 0 0 0 0 0 0' : k === 'g' ? '0 0 0 0 0 0 1 0 0 0 0 0 0 0 0' : '0 0 0 0 0 0 0 0 0 0 0 0 1 0 0'} 0 0 0 1 0" result="${k}"/>`;
    // 滤镜区域比表面大一圈：区域只要比表面小一点（量的时候还没排完版、吸顶偏移、缩放取整），区域外的像素就变成透明，
    // 背后的正文会不经模糊直接透出来；表面以外的部分本来就被 backdrop-filter 裁掉，放大区域没有代价
    const pad = Math.max(w, h);
    svg.innerHTML = `<filter id="${id}" x="${-pad}" y="${-pad}" width="${w + 2 * pad}" height="${h + 2 * pad}" filterUnits="userSpaceOnUse" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">` +
      `<feImage result="map" x="0" y="0" width="${w}" height="${h}" preserveAspectRatio="none"/>` +
      (split > 0 ? ch('r', 1 + split) + ch('g', 1) + ch('b', 1 - split) +
        '<feBlend in="r" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b" mode="screen"/>'
        : `<feDisplacementMap in="SourceGraphic" in2="map" scale="${scale.toFixed(2)}" xChannelSelector="R" yChannelSelector="G"/>`) +
      '</filter>';
    document.body.appendChild(svg);
    return svg;
  }

  function radiusOf(el, w, h) {
    const v = getComputedStyle(el).borderTopLeftRadius;
    const r = v.endsWith('%') ? parseFloat(v) / 100 * Math.min(w, h) : parseFloat(v) || 0;
    return Math.min(r, w / 2, h / 2);
  }

  async function attachLens(el, opts = {}) {
    const split = opts.split == null ? 0.15 : opts.split;
    const n = opts.superellipse || 2;
    if (!supportsLens() || reducedTransparency()) return () => {};
    const cs = getComputedStyle(el);
    if (cs.willChange !== 'auto') return () => {};             // 自己的合成层：Chrome 可能把位移图本身画出来
    let { width: w, height: h } = el.getBoundingClientRect();
    if (Math.min(w, h) < 32) return () => {};
    const base = (cs.backdropFilter && cs.backdropFilter !== 'none') ? cs.backdropFilter : '';
    const id = 'lg-lens-' + (++uid);
    let r = radiusOf(el, w, h), rim = rimFor(w, h);
    let tile = cornerTile(Math.round(r), Math.round(rim), n);
    const svg = buildFilter(id, Math.round(w), Math.round(h), 2 * tile.maxOff, split);
    const fe = svg.querySelector('feImage');
    const setMap = async () => {
      const url = composeMap(w, h, tile);
      const img = new Image(); img.src = url;
      try { await img.decode(); } catch (e) { return false; }  // 没解码完就指过去，会画出没有模糊的样子
      fe.setAttribute('href', url);
      return true;
    };
    if (!(await setMap())) { svg.remove(); return () => {}; }
    el.style.backdropFilter = el.style.webkitBackdropFilter = (base + ' url(#' + id + ')').trim();
    const ro = new ResizeObserver(async () => {
      const b = el.getBoundingClientRect();
      if (Math.abs(b.width - w) < 1 && Math.abs(b.height - h) < 1) return;
      w = b.width; h = b.height;
      const r2 = radiusOf(el, w, h), rim2 = rimFor(w, h);
      if (Math.round(r2) !== Math.round(r) || Math.round(rim2) !== Math.round(rim)) { r = r2; rim = rim2; tile = cornerTile(Math.round(r), Math.round(rim), n); }
      const f = svg.querySelector('filter');
      const pad = Math.max(Math.round(w), Math.round(h));
      f.setAttribute('x', -pad); f.setAttribute('y', -pad); f.setAttribute('width', Math.round(w) + 2 * pad); f.setAttribute('height', Math.round(h) + 2 * pad);
      fe.setAttribute('width', Math.round(w)); fe.setAttribute('height', Math.round(h));
      await setMap();                                           // 只重新拼图，角块复用缓存
    });
    ro.observe(el);
    return () => { ro.disconnect(); svg.remove(); el.style.backdropFilter = el.style.webkitBackdropFilter = ''; };
  }

  /* 5×3 网格取样，去掉最暗、最亮各两点后平均。亮度 = (0.299R + 0.587G + 0.114B) / 255；纹理 = 最亮 - 最暗。
     source 读不到（跨域、没有像素）时返回 null。 */
  function sample(el, source) {
    if (!source) return null;
    const sr = source.getBoundingClientRect(), er = el.getBoundingClientRect();
    const sw = source.videoWidth || source.naturalWidth || source.width, sh = source.videoHeight || source.naturalHeight || source.height;
    if (!sw || !sh || !sr.width || !sr.height) return null;
    const c = document.createElement('canvas'); c.width = 64; c.height = 64;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    let data;
    try { ctx.drawImage(source, 0, 0, 64, 64); data = ctx.getImageData(0, 0, 64, 64).data; } catch (e) { return null; }
    const pts = [];
    for (let j = 0; j < 3; j++) for (let i = 0; i < 5; i++) {
      const x = er.left + er.width * (i + 0.5) / 5, y = er.top + er.height * (j + 0.5) / 3;
      const u = Math.min(63, Math.max(0, Math.floor((x - sr.left) / sr.width * 64)));
      const v = Math.min(63, Math.max(0, Math.floor((y - sr.top) / sr.height * 64)));
      const k = (v * 64 + u) * 4, R = data[k], G = data[k + 1], B = data[k + 2];
      const mx = Math.max(R, G, B), mn = Math.min(R, G, B);
      pts.push({ l: (0.299 * R + 0.587 * G + 0.114 * B) / 255, c: (mx - mn) / 255 });
    }
    pts.sort((a, b) => a.l - b.l);
    const mid = pts.slice(2, -2);
    const avg = f => mid.reduce((s, p) => s + f(p), 0) / mid.length;
    return { lum: avg(p => p.l), texture: pts[pts.length - 1].l - pts[0].l, chroma: avg(p => p.c), lo: mid[0].l, hi: mid[mid.length - 1].l };
  }

  /* 次墨压在玻璃上的对比度估算（只看亮度）：玻璃 = 背后和底色按透明度混合；
     深色字是 multiply（次墨 rgb(60 60 67) 70%），浅色字是 plus-lighter（次墨 rgb(235 235 245) 64%）。 */
  function contrastEstimate(bgLum, ink, density) {
    const lin = v => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
    const ratio = (a, b) => (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    if (ink === 'dark') {
      const a = 0.06 + 0.16 * density, glass = bgLum * (1 - a) + a;           // 白色底色
      const text = glass * (1 - 0.7 + 0.7 * 61 / 255);                         // multiply
      return ratio(lin(glass), lin(text));
    }
    const a = 0.10 + 0.20 * density, glass = bgLum * (1 - a) + a * 18 / 255;   // 深色底色
    const text = Math.min(1, glass + 0.64 * 236 / 255);                        // plus-lighter
    return ratio(lin(glass), lin(text));
  }

  /* 墨色和密度。浅色模式下亮度 < 0.5 用浅色字，±0.05 以内保持上一次的决定（不在线上闪）；深色模式一律浅色字。
     密度 = 0.55 × 背景和墨色亮度有多接近 + 0.7 × 纹理 + 0.3 × 色度，再按最不利那一点把次墨提到 4.5:1；保留饱和度 = max(0.45, 1 - 0.75 × 色度)。
     一组相邻的表面共用一个决定；读不到背景时按主题、取浓的一档。 */
  function adaptInk(els, source, opts = {}) {
    els = Array.isArray(els) ? els : [els];
    const dark = opts.dark != null ? opts.dark : matchMedia('(prefers-color-scheme: dark)').matches;
    const key = opts.storageKey || 'lg-ink';
    const stats = els.map(e => sample(e, source)).filter(Boolean);
    let prev = null;
    try { prev = localStorage.getItem(key); } catch (e) {}
    let ink, density, sat = 1, pass = true;
    if (!stats.length) {
      ink = dark ? 'light' : (prev || 'dark'); density = 1;
    } else {
      const m = f => stats.reduce((s, x) => s + f(x), 0) / stats.length;
      const lum = m(x => x.lum), texture = m(x => x.texture), chroma = m(x => x.chroma);
      if (dark) ink = 'light';
      else if (prev && Math.abs(lum - 0.5) <= 0.05) ink = prev;
      else ink = lum < 0.5 ? 'light' : 'dark';
      const inkLum = ink === 'light' ? 1 : 0;
      density = Math.min(1, Math.max(0, 0.55 * (1 - Math.abs(lum - inkLum)) + 0.7 * texture + 0.3 * chroma));
      sat = Math.max(0.45, 1 - 0.75 * chroma);
      // 次墨最先不够 4.5:1：按保留下来的最不利那一点估算，不够就提密度，不提墨色的透明度
      // 最不利的一点取「平均」和「保留下来的极值」的中间：2px 模糊会把细条纹抹掉一半，只按极值会把每块玻璃都推到最浓
      const worst = ink === 'dark' ? (lum + Math.min(...stats.map(x => x.lo))) / 2 : (lum + Math.max(...stats.map(x => x.hi))) / 2;
      while (density < 1 && contrastEstimate(worst, ink, density) < 4.5) density = Math.min(1, density + 0.05);
      pass = contrastEstimate(worst, ink, density) >= 4.5;
      if (!pass) console.warn('[liquid-glass] 最浓的一档也不够 4.5:1：这块背景太花，换成实色面或加大模糊', els[0]);
    }
    try { localStorage.setItem(key, ink); } catch (e) {}
    for (const e of els) {
      e.classList.toggle('lg-dark', dark);
      e.classList.toggle('lg-on-dark', !dark && ink === 'light');
      e.classList.toggle('lg-light', !dark && ink === 'dark');
      e.style.setProperty('--lg-density', density.toFixed(3));
      e.style.setProperty('--lg-base-density', density.toFixed(3));
      e.style.setProperty('--lg-sat', sat.toFixed(3));
    }
    return { ink, density, sat, pass };
  }

  globalThis.LiquidGlass = { attachLens, sample, adaptInk, supportsLens, rimFor, bend, contrastEstimate };
})();
