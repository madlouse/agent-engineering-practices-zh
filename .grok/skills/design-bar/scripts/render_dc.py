#!/usr/bin/env python3
"""把 Claude Design 画布的 .dc.html 画板按给定状态渲染成普通页面并截图，用于本地核对高保真稿。

只支持画板常用的语法：{{ 路径 }} 洞、<sc-if value="{{ x }}">、<sc-for list="{{ xs }}" as="it">（可以嵌套）。
画板的 renderVals() 会在浏览器里执行一次（props 取 data-props 的默认值，--state 同时作为组件的 state），
算出的值填进模板；函数和引用类的值丢掉。--state 里写的值优先。

用法：
  python render_dc.py Main.dc.html out.png --state '{"cardPending": true}'
  python render_dc.py Web.dc.html web.png --size 1440x900 --full
选项：
  --state JSON     模板里洞和条件用到的值
  --props JSON     覆盖 data-props 的默认值（例如切到深色主题）
  --size WxH       视口，默认 390x844
  --full           整页截图
  --still          prefers-reduced-motion: reduce（看静止的最终状态）
  --wait MS        截图前等待，默认 400（看动画中间帧时调大或调小）
  --scroll Y       滚动到 Y（先找 .scroll 容器，没有就滚动窗口）
  --dark-os        模拟系统深色模式（检查画板是否锁定了主题）
  --keep-html P    同时保存渲染后的 HTML

画板引用的 /_blob/ 资源请先下载到画板旁边，再把链接改成相对路径。需要 Python Playwright 和 Chromium。
"""
import argparse
import json
import os
import re
import sys
import tempfile


def lookup(path, scope):
    cur = scope
    for key in path.strip().split('.'):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def fill_holes(text, scope):
    def rep(m):
        v = lookup(m.group(1), scope)
        if v is None:
            return {'true': 'true', 'false': 'false'}.get(m.group(1).strip(), '')
        return str(v)
    return re.sub(r'\{\{\s*([^}]+?)\s*\}\}', rep, text)


def _matching_end(text, start, tag):
    """从 start 处的 <tag ...> 开始，找到和它配对的 </tag> 的位置（支持嵌套）。"""
    depth, i = 0, start
    pat = re.compile(r'<(/?)' + tag + r'\b[^>]*>')
    for m in pat.finditer(text, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.start(), m.end()
    return len(text), len(text)


def expand(text, scope):
    out, pos = [], 0
    open_for = re.compile(r'<sc-for([^>]*)>')
    while True:
        m = open_for.search(text, pos)
        if not m:
            out.append(text[pos:])
            break
        out.append(text[pos:m.start()])
        end_start, end_end = _matching_end(text, m.start(), 'sc-for')
        body = text[m.end():end_start]
        lst = re.search(r'list="\{\{\s*([^}]+?)\s*\}\}"', m.group(1))
        name = re.search(r'as="([^"]+)"', m.group(1))
        items = lookup(lst.group(1), scope) if lst else None
        out.append(''.join(expand(body, {**scope, name.group(1): it, '$index': i})
                           for i, it in enumerate(items or [])))
        pos = end_end
    text = ''.join(out)
    inner_if = re.compile(r'<sc-if value="\{\{\s*([^}]+?)\s*\}\}"[^>]*>((?:(?!<sc-if).)*?)</sc-if>', re.S)
    while inner_if.search(text):
        text = inner_if.sub(lambda m: m.group(2) if lookup(m.group(1), scope) else '', text)
    return fill_holes(text, scope)


LOGIC_JS = r"""([code, props, state]) => {
  class DCLogic {
    constructor(p) { this.props = p; this.state = {}; }
    setState(u) { Object.assign(this.state, typeof u === 'function' ? u(this.state, this.props) : u); }
    forceUpdate() {}
  }
  try {
    const Component = new Function('DCLogic', code + '\n;return Component;')(DCLogic);
    const c = new Component(props);
    Object.assign(c.state, state);
    const vals = c.renderVals ? c.renderVals() : {};
    return JSON.parse(JSON.stringify(vals, (k, v) => (typeof v === 'function' ? undefined : v)));
  } catch (e) { return { __error: String(e) }; }
}"""


def logic_values(src, state, page, props_override=None):
    """在浏览器里执行画板的 renderVals()，返回能填进模板的值；没有逻辑或出错时返回 {}。"""
    m = re.search(r'<script type="text/x-dc"([^>]*)>(.*?)</script>', src, flags=re.S)
    if not m:
        return {}
    props = {}
    dp = re.search(r"data-props='([^']*)'", m.group(1))
    if dp:
        try:
            props = {k: v.get('default') for k, v in json.loads(dp.group(1)).items() if isinstance(v, dict) and not k.startswith('$')}
        except ValueError:
            pass
    props.update(props_override or {})
    vals = page.evaluate(LOGIC_JS, [m.group(2), props, state])
    if '__error' in vals:
        print(f'renderVals() 执行出错，按 --state 渲染：{vals["__error"]}', file=sys.stderr)
        return {}
    return vals


def render_html(src, state, vals=None):
    s = re.sub(r'<script src="\./support\.js"></script>', '', src)
    s = re.sub(r'<script type="text/x-dc".*?</script>', '', s, flags=re.S)
    for tag in ('<helmet>', '</helmet>', '<x-dc>', '</x-dc>'):
        s = s.replace(tag, '')
    return expand(s, {**(vals or {}), **state})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('out')
    ap.add_argument('--state', default='{}')
    ap.add_argument('--props', default='{}', help='覆盖 data-props 的默认值，例如 \'{"theme": "深色"}\'')
    ap.add_argument('--size', default='390x844')
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--still', action='store_true')
    ap.add_argument('--wait', type=int, default=400)
    ap.add_argument('--scroll', type=int, default=0)
    ap.add_argument('--dark-os', action='store_true')
    ap.add_argument('--keep-html')
    a = ap.parse_args()

    board = os.path.abspath(a.board)
    src = open(board, encoding='utf-8').read()
    state = json.loads(a.state)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('需要 Python Playwright：pip install playwright && playwright install chromium')
    w, h = (int(x) for x in a.size.lower().split('x'))
    tmp = None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            vals = logic_values(src, state, b.new_page(), json.loads(a.props))
            html = render_html(src, state, vals)
            # 写在画板旁边，相对路径的样式表才能加载
            fd, tmp = tempfile.mkstemp(prefix='.render_', suffix='.html', dir=os.path.dirname(board))
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(html)
            if a.keep_html:
                with open(a.keep_html, 'w', encoding='utf-8') as f:
                    f.write(html)
            pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2,
                            reduced_motion='reduce' if a.still else 'no-preference',
                            color_scheme='dark' if a.dark_os else 'light')
            pg.goto('file://' + tmp)
            pg.wait_for_timeout(a.wait)
            if a.scroll:
                pg.evaluate('(y)=>{const s=document.querySelector(".scroll"); if(s) s.scrollTop=y; else window.scrollTo(0,y)}', a.scroll)
                pg.wait_for_timeout(100)
            pg.screenshot(path=a.out, full_page=a.full)
            b.close()
    finally:
        if tmp:
            os.remove(tmp)
    print(a.out)


if __name__ == '__main__':
    main()
