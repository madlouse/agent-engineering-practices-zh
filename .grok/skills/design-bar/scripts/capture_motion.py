#!/usr/bin/env python3
"""动效截图：把画板按状态渲染成页面，再执行画板自己的 componentDidMount（WebGL、透镜、墨色自适应），等它画出来再截。

画板截图工具（render_dc.py、verify_canvas.py）只填模板，不跑挂载代码，所以截不到 canvas 里的动效，也截不到
liquid-glass.js 的边缘透镜。动效、透镜、「玻璃背后会变」的证据（标杆卡 P4、liquid-glass.md §7）都用本脚本截。

做法：
  1. 按 --state、--props 渲染静态页面（和 render_dc.py 同一套），模板里的 ref="{{x}}" 和 onXxx="{{x}}" 先换成标记；
  2. 页面里新建画板的 Component，算一次 renderVals()，把 ref 回调接到对应元素、把事件处理接到对应元素，
     再执行完整的 componentDidMount（不是只调某一个启动函数）；
  3. 等 window.LiquidGlass.attachLens 返回的位移图全部解码、字体就绪，再等 --wait 毫秒截图。
  模板只渲染一次：布局随状态变化（比如倾斜后两半的宽度）要用 --state 给出；--hover 移动真实的指针，
  触发 :hover 样式和画板的 onMouseEnter / onMouseMove 处理（WebGL 循环读的 this.state 会跟着变）。

用法：
  python capture_motion.py Main.dc.html out.png --state '{"lean":"body"}' --hover 400,450 \\
      --blob 0499e9ec...=vc.css --blob 1b0051af...=liquid-glass.js --size 1440x900
  python capture_motion.py Main.dc.html still.png --reduced-motion
  python capture_motion.py Main.dc.html nogl.png --no-webgl
  python capture_motion.py Main.dc.html orb.png --probe '.orb'      # 量玻璃背后会不会变
选项：
  --state JSON / --props JSON   同 render_dc.py
  --size WxH                    视口，默认 1440x900；--dsf 截图倍率，默认 2
  --hover X,Y                   截图前把指针移到这里（可写多次，按顺序移动）
  --reduced-motion              prefers-reduced-motion: reduce（静止帧）
  --no-webgl                    让 getContext('webgl'/'webgl2') 返回 null（兜底画面）
  --blob ID=PATH                把 /_blob/ID 换成本地文件（样式表、脚本都行，可写多次）
  --wait MS                     挂载完成后再等多久截图，默认 3000
  --probe SELECTOR|X,Y,W,H      把匹配的元素藏起来（或直接给一块区域），在它的矩形里按 5×3 网格隔 --probe-interval 毫秒取 --probe-frames 帧，
                                报每个取样点亮度随时间的最大变化；< 0.04 判为「背后几乎不变」（等于平涂，改实色面），退出码 2。
                                data-backdrop="scroll" 的表面按取样点之间的差别判（≥ 0.1 说明此刻有正文压在后面），配合「正文压在导航下」这类状态用

需要 Python Playwright 和 Chromium（WebGL 用 SwiftShader 软件渲染）；量亮度需要 Pillow。
"""
import argparse
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render_dc import logic_values, render_html  # noqa: E402

HARNESS = r"""
<script>
(() => {
  const code = %s, props = %s, state = %s;
  class DCLogic {
    constructor(p) { this.props = p; this.state = {}; }
    setState(u) { Object.assign(this.state, typeof u === 'function' ? u(this.state, this.props) : u); if (this.componentDidUpdate) try { this.componentDidUpdate(); } catch (e) {} }
    forceUpdate() {}
  }
  window.__mount = async () => {
    const Component = new Function('DCLogic', code + '\n;return Component;')(DCLogic);
    const c = new Component(props);
    Object.assign(c.state, state);
    const lens = [];
    if (window.LiquidGlass) { const orig = window.LiquidGlass.attachLens; window.LiquidGlass.attachLens = (...a) => { const p = orig(...a); lens.push(p); return p; }; }
    const vals = c.renderVals ? c.renderVals() : {};
    for (const el of document.querySelectorAll('[data-cm-ref]')) { const f = vals[el.getAttribute('data-cm-ref')]; if (typeof f === 'function') f(el); }
    for (const el of document.querySelectorAll('[data-cm-on]')) {
      for (const pair of el.getAttribute('data-cm-on').split(';')) {
        const [ev, key] = pair.split('='); const f = vals[key];
        if (typeof f === 'function') el.addEventListener(ev, e => f(e));
      }
    }
    if (c.componentDidMount) c.componentDidMount();
    await Promise.all(lens.map(p => Promise.resolve(p).catch(() => null)));
    await document.fonts.ready;
    window.__c = c;
    return { lenses: lens.length, gl: !!c.gl, noGL: !!(c.state && c.state.noGL) };
  };
})();
</script>
"""

NO_WEBGL = """(() => { const g = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (t, o) { return /^webgl/.test(t) ? null : g.call(this, t, o); }; })();"""

EVENTS = {'onMouseEnter': 'mouseenter', 'onMouseLeave': 'mouseleave', 'onMouseMove': 'mousemove', 'onPointerEnter': 'pointerenter',
          'onPointerLeave': 'pointerleave', 'onPointerMove': 'pointermove', 'onMouseOver': 'mouseover', 'onFocus': 'focus', 'onBlur': 'blur'}


def mark_bindings(src):
    """ref="{{x}}" → data-cm-ref="x"；onMouseEnter="{{x}}" 这类 → data-cm-on="mouseenter=x"（一个元素上多个用分号拼）。"""
    src = re.sub(r'\sref="\{\{\s*([\w.]+)\s*\}\}"', r' data-cm-ref="\1"', src)

    def tag(m):
        t = m.group(0)
        pairs = []
        for attr, ev in EVENTS.items():
            mm = re.search(r'\s' + attr + r'="\{\{\s*([\w.]+)\s*\}\}"', t)
            if mm:
                pairs.append(f'{ev}={mm.group(1)}')
                t = t.replace(mm.group(0), '')
        return t[:-1] + f' data-cm-on="{";".join(pairs)}">' if pairs else t
    return re.sub(r'<[a-zA-Z][^<>]*\son[A-Z]\w*="\{\{[^}]*\}\}"[^<>]*>', tag, src)


def probe(pg, selector, frames, interval):
    try:
        from PIL import Image
    except ImportError:
        sys.exit('--probe 需要 Pillow：pip install pillow')
    if re.fullmatch(r'\d+,\d+,\d+,\d+', selector):  # 直接给一块区域 x,y,w,h（还没画玻璃、想先量一块位置时用）
        x, y, w, h = (int(v) for v in selector.split(','))
        rect = {'x': x, 'y': y, 'w': w, 'h': h, 'el': False}
    else:
        rect = pg.evaluate("""(sel) => { const els = [...document.querySelectorAll(sel)].filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden'); if (!els.length) return null;
      const r = els[0].getBoundingClientRect(); els.forEach(e => e.style.setProperty('visibility', 'hidden', 'important'));
      return {scroll: els[0].closest('[data-backdrop]')?.getAttribute('data-backdrop') === 'scroll', x: Math.max(0, r.left), y: Math.max(0, r.top), w: Math.min(innerWidth, r.right) - Math.max(0, r.left), h: Math.min(innerHeight, r.bottom) - Math.max(0, r.top)}; }""", selector)
    if not rect or rect['w'] < 4 or rect['h'] < 4:
        sys.exit(f'--probe {selector}：页面上没有这个元素，或它在视口外')
    GX, GY = 24, 6
    series = []
    for _ in range(frames):
        im = Image.open(io.BytesIO(pg.screenshot(clip={'x': rect['x'], 'y': rect['y'], 'width': rect['w'], 'height': rect['h']}))).convert('RGB')
        W, H = im.size
        # 24 × 6 个取样点：5 × 3 会漏掉稀疏的一行字（标题只占条的一角时）
        pts = [im.getpixel((min(W - 1, int(W * (i + 0.5) / GX)), min(H - 1, int(H * (j + 0.5) / GY)))) for j in range(GY) for i in range(GX)]
        series.append([(0.299 * r + 0.587 * g + 0.114 * b) / 255 for r, g, b in pts])
        pg.wait_for_timeout(interval)
    if 'el' not in rect:
        pg.evaluate("(sel) => document.querySelectorAll(sel).forEach(e => e.style.removeProperty('visibility'))", selector)
    temporal = max(max(f[k] for f in series) - min(f[k] for f in series) for k in range(GX * GY))
    spatial = max(max(f) - min(f) for f in series)
    # scroll 的表面在截图里不会自己动，背后会变的证据是「此刻有正文压在后面」：按取样点之间的差别判
    changes = spatial >= 0.1 if rect.get('scroll') else temporal >= 0.04
    return {'probe': selector, 'frames': frames, 'temporal_range': round(temporal, 3), 'spatial_range': round(spatial, 3),
            'basis': 'spatial（scroll：正文压在后面）' if rect.get('scroll') else 'temporal',
            'verdict': '背后会变' if changes else '背后几乎不变'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('out')
    ap.add_argument('--state', default='{}')
    ap.add_argument('--props', default='{}')
    ap.add_argument('--size', default='1440x900')
    ap.add_argument('--dsf', type=float, default=2)
    ap.add_argument('--hover', action='append', default=[], metavar='X,Y')
    ap.add_argument('--reduced-motion', action='store_true')
    ap.add_argument('--no-webgl', action='store_true')
    ap.add_argument('--blob', action='append', default=[], metavar='ID=PATH')
    ap.add_argument('--wait', type=int, default=3000)
    ap.add_argument('--scroll', type=int, default=0, metavar='Y', help='截图前把页面滚到 Y（看吸顶玻璃压在真实正文上的样子）')
    ap.add_argument('--focus', metavar='SELECTOR', help='截图前用键盘焦点（focus-visible）聚焦这个元素，看焦点圈')
    ap.add_argument('--probe')
    ap.add_argument('--probe-frames', type=int, default=8)
    ap.add_argument('--probe-interval', type=int, default=250)
    a = ap.parse_args()

    board = os.path.abspath(a.board)
    src = open(board, encoding='utf-8').read()
    for m in a.blob:
        bid, _, path = m.partition('=')
        if not os.path.exists(path):
            sys.exit(f'--blob {m}：本地文件不存在')
        src = src.replace('/_blob/' + bid, 'file://' + os.path.abspath(path))
    state, props = json.loads(a.state), json.loads(a.props)
    logic = re.search(r'<script type="text/x-dc"([^>]*)>(.*?)</script>', src, re.S)
    code = logic.group(2) if logic else 'class Component extends DCLogic {}'
    dp = re.search(r"data-props='([^']*)'", logic.group(1)) if logic else None
    full_props = {}
    if dp:
        try:
            full_props = {k: v.get('default') for k, v in json.loads(dp.group(1)).items() if isinstance(v, dict) and not k.startswith('$')}
        except ValueError:
            pass
    full_props.update(props)
    w, h = (int(x) for x in a.size.lower().split('x'))
    from playwright.sync_api import sync_playwright
    tmp = None
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
            vals = logic_values(src, state, b.new_page(), props)
            html = render_html(mark_bindings(src), state, vals)
            html = html.replace('</body>', HARNESS % (json.dumps(code), json.dumps(full_props, ensure_ascii=False), json.dumps(state, ensure_ascii=False)) + '</body>')
            fd, tmp = tempfile.mkstemp(prefix='.motion_', suffix='.html', dir=os.path.dirname(board))
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)
            pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=a.dsf,
                            reduced_motion='reduce' if a.reduced_motion else 'no-preference')
            errors = []
            pg.on('pageerror', lambda e: errors.append(str(e)[:160]))
            if a.no_webgl:
                pg.add_init_script(NO_WEBGL)
            pg.goto('file://' + tmp)
            pg.wait_for_timeout(200)
            info = pg.evaluate('() => window.__mount()')
            if a.scroll:
                pg.evaluate('(y) => window.scrollTo(0, y)', a.scroll)
            if a.focus:
                if not pg.evaluate('(s) => { const e = document.querySelector(s); if (!e) return false; e.focus({focusVisible: true}); return e.matches(":focus-visible"); }', a.focus):
                    sys.exit(f'--focus {a.focus}：找不到元素，或聚焦后不是 :focus-visible')
            for xy in a.hover:
                x, y = (float(v) for v in xy.split(','))
                pg.mouse.move(x, y, steps=8)
            pg.wait_for_timeout(a.wait)
            result = {'out': a.out, **info}
            if a.probe:
                result.update(probe(pg, a.probe, a.probe_frames, a.probe_interval))
            pg.screenshot(path=a.out)
            if errors:
                result['errors'] = errors
            b.close()
    finally:
        if tmp:
            os.remove(tmp)
    print(json.dumps(result, ensure_ascii=False))
    if a.probe and result.get('verdict') == '背后几乎不变':
        sys.exit(2)


if __name__ == '__main__':
    main()
