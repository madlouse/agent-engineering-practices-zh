#!/usr/bin/env python3
"""真实浏览器里的无障碍实测（award-bar 第 3 节第 3 条）：读屏顺序、键盘路径、200% 字号、对比度数字。

用法：
  python a11y_probe.py <画板目录> --states states.json --out <输出目录> [--lang zh] [--theme light] [--size 390x844] [--max-tabs 40]
states.json：[{"board": "AI-Today", "state": "训练日"}, ...]（state 写状态名、下标都行）

每个状态查四件事：
 1. 读屏顺序：按 DOM 顺序列出读屏会读的角色和名称（标题、地标、按钮、链接、输入、图片、文字），没有名称的控件标出来；
    有 page.accessibility.snapshot（或 aria 快照）时把浏览器自己算的树也附上。
 2. 键盘路径：从页面顶部连按 Tab，记下焦点顺序和每一下有没有看得见的焦点样式（样式变化或像素差），截焦点那一帧；
    另列出点得到、但按 Tab 到不了的元素（div 上挂点击）。
 3. 200% 字号：根字号放大到 200%（font-size）和 CSS zoom 两种都试，报哪种真的把字放大了（生效），再查横向溢出、文字被裁、元素重叠，截图。
    放大前把撑满视口、overflow 隐藏的固定高度外框放开（真机页面竖着能滚，画板只是截了一屏）。
    根字号生效时（字号用 rem），CSS zoom 只当参考不算问题：固定宽度的画板整页放大必然横向溢出，那是浏览器缩放，不是字号放大。
 4. 对比度：每个有文字的元素的前景色和有效背景色算出对比度数字（正文 4.5:1，大字 3:1），列最低的几个；背景是图或渐变的量不了，标出来。
输出 <out>/a11y.md 和截图。测法：真实浏览器（Chromium）实测。
需要 Python Playwright + Chromium（没有就退出码 2）；截图像素差需要 Pillow（没有就只比样式）。
退出码：0 没发现问题；1 有；2 用法错误或缺 Playwright。
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canvas_common as cc  # noqa: E402

PAUSE = 150

COMMON_JS = r"""
const __cv = document.createElement('canvas').getContext('2d');
const __cache = {};
function parseColor(s) {
  if (!s) return null;
  if (__cache[s]) return __cache[s];
  let r = null;
  const m = s.match(/^rgba?\(([^)]+)\)$/);
  if (m) { const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); r = [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  else { __cv.clearRect(0, 0, 1, 1); __cv.fillStyle = '#000'; __cv.fillStyle = s; __cv.fillRect(0, 0, 1, 1); const d = __cv.getImageData(0, 0, 1, 1).data; r = [d[0], d[1], d[2], d[3] / 255]; }
  __cache[s] = r; return r;
}
function isVisible(el) {
  for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || e.getAttribute('aria-hidden') === 'true') return false;
  }
  const r = el.getBoundingClientRect();
  return r.width > 0 && r.height > 0;
}
function ownText(el) {
  let t = '';
  for (const n of el.childNodes) if (n.nodeType === 3) t += n.textContent;
  return t.replace(/\s+/g, ' ').trim();
}
function label(el) {
  return (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/)[0] : ''));
}
"""

READ_JS = "() => {" + COMMON_JS + r"""
  const out = [];
  const ROLE = {a: 'link', button: 'button', h1: 'heading 1', h2: 'heading 2', h3: 'heading 3', h4: 'heading 4', nav: 'navigation', main: 'main', header: 'banner',
    footer: 'contentinfo', img: 'image', input: 'textbox', textarea: 'textbox', select: 'combobox', li: 'listitem', ul: 'list', ol: 'list', p: 'text', label: 'label', section: 'region'};
  function textOf(el) { return (el.textContent || '').replace(/\s+/g, ' ').trim(); }
  function nameOf(el) {
    const lb = el.getAttribute('aria-labelledby');
    if (lb) { const t = lb.split(/\s+/).map(i => { const x = document.getElementById(i); return x ? textOf(x) : ''; }).join(' ').trim(); if (t) return t; }
    const al = el.getAttribute('aria-label'); if (al && al.trim()) return al.trim();
    const tag = el.tagName.toLowerCase();
    if (tag === 'img') return (el.getAttribute('alt') || '').trim();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') {
      if (el.id) { const l = document.querySelector('label[for="' + el.id + '"]'); if (l && textOf(l)) return textOf(l); }
      const w = el.closest('label'); if (w && textOf(w)) return textOf(w);
      return (el.getAttribute('title') || '').trim() || (el.getAttribute('placeholder') ? '（只有占位文字：' + el.getAttribute('placeholder') + '）' : '');
    }
    const t = textOf(el);
    if (t) return t;
    const imgs = [...el.querySelectorAll('img[alt]')].map(i => i.getAttribute('alt')).join(' ').trim();
    if (imgs) return imgs;
    return (el.getAttribute('title') || '').trim();
  }
  const NEEDS_NAME = el => { const t = el.tagName.toLowerCase(); const r = el.getAttribute('role');
    return t === 'button' || (t === 'a' && el.hasAttribute('href')) || t === 'input' || t === 'textarea' || t === 'select' || r === 'button' || r === 'link' || el.hasAttribute('data-go'); };
  const walk = el => {
    if (out.length >= 250) return;
    const tag = el.tagName.toLowerCase();
    if (['script', 'style', 'svg', 'head', 'meta', 'link', 'template'].includes(tag)) return;
    if (!isVisible(el) && !el.querySelector('*')) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || el.getAttribute('aria-hidden') === 'true') return;
    const role = el.getAttribute('role') || (el.hasAttribute('data-go') && !ROLE[tag] ? 'button（div 上挂点击）' : ROLE[tag]);
    const interactive = NEEDS_NAME(el);
    if (interactive || /^h[1-4]$/.test(tag) || ['nav', 'main', 'header', 'footer', 'img'].includes(tag)) {
      const name = nameOf(el);
      out.push({role: role || tag, name: name.slice(0, 60), unnamed: interactive && !name || (tag === 'img' && !el.hasAttribute('alt')), tag});
      if (interactive || tag === 'img' || /^h[1-4]$/.test(tag)) return;   // 名称已经包含了里面的文字
    } else {
      const t = ownText(el);
      if (t && !['li', 'ul', 'ol'].includes(tag)) out.push({role: '文字', name: t.slice(0, 60), unnamed: false, tag});
    }
    for (const c of el.children) walk(c);
  };
  walk(document.body);
  return out;
}"""

UNREACHABLE_JS = "() => {" + COMMON_JS + r"""
  const bad = [];
  for (const el of document.querySelectorAll('[data-go], [onclick], a, [role=button], [role=link]')) {
    if (!isVisible(el)) continue;
    const tag = el.tagName.toLowerCase();
    const native = tag === 'button' || tag === 'input' || tag === 'select' || tag === 'textarea' || (tag === 'a' && el.hasAttribute('href'));
    const ti = el.getAttribute('tabindex');
    if (el.disabled) continue;
    if (!native && !(ti !== null && parseInt(ti, 10) >= 0)) bad.push((el.getAttribute('aria-label') || ownText(el) || label(el)).slice(0, 40) + '（' + label(el) + '）');
    else if (ti !== null && parseInt(ti, 10) < 0) bad.push((el.getAttribute('aria-label') || ownText(el) || label(el)).slice(0, 40) + '（tabindex=-1）');
  }
  return bad;
}"""

RING_JS = r"""const ringOf = el => { const out = []; let e = el; for (let i = 0; e && e.nodeType === 1 && i < 4; i++, e = e.parentElement) { const cs = getComputedStyle(e); out.push(i ? [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow, cs.borderColor].join('|') : [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow, cs.borderColor, cs.backgroundColor, cs.color, cs.textDecorationLine, cs.transform].join('|')); } return out.join('#'); };"""

FOCUS_JS = "() => {" + COMMON_JS + RING_JS + r"""
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  window.__tabEl = el;
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  let n = el.getAttribute('aria-label') || ownText(el) || (el.textContent || '').replace(/\s+/g, ' ').trim() || el.getAttribute('placeholder') || el.getAttribute('title') || '';
  return {tag: label(el), name: n.slice(0, 40), rect: [r.left, r.top, r.width, r.height], vw: innerWidth, vh: innerHeight,
          style: ringOf(el),
          ring: cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0 && ((parseColor(cs.outlineColor) || [0, 0, 0, 0])[3] > 0.1)};
}"""

BLUR_STYLE_JS = "() => {" + RING_JS + " const el = window.__tabEl; if (!el) return null; el.blur(); return ringOf(el); }"
REFOCUS_JS = "() => { const el = window.__tabEl; if (el) el.focus({preventScroll: true}); }"

RELEASE_JS = """() => {
  const walk = (el, d) => {
    for (const c of el.children) {
      const cs = getComputedStyle(c);
      if (['hidden', 'clip'].includes(cs.overflowY) && c.getBoundingClientRect().height >= innerHeight - 1) {
        c.style.minHeight = c.getBoundingClientRect().height + 'px'; c.style.height = 'auto'; c.style.overflowY = 'visible';
      }
      if (d < 4) walk(c, d + 1);
    }
  };
  walk(document.body, 0);
}"""

ZOOM_JS = "(method) => {" + COMMON_JS + r"""
  const textEls = [...document.querySelectorAll('body *')].filter(e => ownText(e) && isVisible(e));
  const med = a => { a = a.slice().sort((x, y) => x - y); return a.length ? a[Math.floor(a.length / 2)] : 0; };
  return {n: textEls.length, h: med(textEls.map(e => e.getBoundingClientRect().height)), fs: med(textEls.map(e => parseFloat(getComputedStyle(e).fontSize)))};
}"""

OVERFLOW_JS = "() => {" + COMMON_JS + r"""
  const res = {hscroll: false, clipped: [], overlaps: [], offscreen: []};
  const de = document.documentElement;
  res.hscroll = de.scrollWidth > innerWidth + 1 || document.body.scrollWidth > innerWidth + 1;
  res.sw = Math.max(de.scrollWidth, document.body.scrollWidth); res.vw = innerWidth;
  const all = [...document.querySelectorAll('body *')].filter(e => isVisible(e) && !['script', 'style'].includes(e.tagName.toLowerCase()) && !e.closest('svg'));
  for (const e of all) {
    const cs = getComputedStyle(e);
    const hasText = ownText(e).length > 0;
    if (!hasText) continue;
    const clipX = e.scrollWidth > e.clientWidth + 1 && ['hidden', 'clip'].includes(cs.overflowX);
    const clipY = e.scrollHeight > e.clientHeight + 1 && ['hidden', 'clip'].includes(cs.overflowY);
    const ell = cs.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1;
    if (clipX || clipY || ell) res.clipped.push(label(e) + '「' + ownText(e).slice(0, 16) + '」' + (ell ? '（省略号截断）' : clipY ? '（竖向被裁）' : '（横向被裁）'));
    const r = e.getBoundingClientRect();
    if (!(clipX || clipY || ell) && cs.position !== 'fixed') {
      for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) {
        const pc = getComputedStyle(p);
        const hx = ['hidden', 'clip'].includes(pc.overflowX), hy = ['hidden', 'clip'].includes(pc.overflowY);
        if (!hx && !hy) continue;
        const pr = p.getBoundingClientRect();
        const meets = r.bottom > pr.top && r.top < pr.bottom && r.right > pr.left && r.left < pr.right;
        const outY = hy && (r.bottom > pr.bottom + 1 || r.top < pr.top - 1), outX = hx && (r.right > pr.right + 1 || r.left < pr.left - 1);
        if (meets && (outX || outY)) { res.clipped.push(label(e) + '「' + ownText(e).slice(0, 16) + '」（被外层 ' + label(p) + ' 裁掉）'); break; }
      }
    }
    if (r.right > innerWidth + 1 || r.left < -1) res.offscreen.push(label(e) + '「' + ownText(e).slice(0, 16) + '」right=' + Math.round(r.right));
  }
  const boxes = all.filter(e => ownText(e) || e.hasAttribute('data-go') || ['button', 'a', 'input'].includes(e.tagName.toLowerCase())).map(e => ({e, r: e.getBoundingClientRect()}));
  for (let i = 0; i < boxes.length && res.overlaps.length < 8; i++) for (let j = i + 1; j < boxes.length && res.overlaps.length < 8; j++) {
    const a = boxes[i], b = boxes[j];
    if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
    const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left), h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (w <= 2 || h <= 2) continue;
    const small = Math.min(a.r.width * a.r.height, b.r.width * b.r.height);
    if (small > 0 && (w * h) / small > 0.2) res.overlaps.push(label(a.e) + '「' + (ownText(a.e) || a.e.getAttribute('aria-label') || '').slice(0, 12) + '」× ' + label(b.e) + '「' + (ownText(b.e) || b.e.getAttribute('aria-label') || '').slice(0, 12) + '」');
  }
  res.clipped = res.clipped.slice(0, 8); res.offscreen = res.offscreen.slice(0, 8);
  return res;
}"""

CONTRAST_JS = "() => {" + COMMON_JS + r"""
  const dark = matchMedia('(prefers-color-scheme: dark)').matches;
  const lin = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const L = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const over = (f, b) => [f[0] * f[3] + b[0] * (1 - f[3]), f[1] * f[3] + b[1] * (1 - f[3]), f[2] * f[3] + b[2] * (1 - f[3]), 1];
  const opUp = el => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  function bgOf(el) {
    const layers = []; let unknown = '';
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') { unknown = '背景是图或渐变'; break; }
      let c = parseColor(cs.backgroundColor);
      if (c && c[3] > 0) { const op = opUp(e); c = [c[0], c[1], c[2], c[3] * op]; layers.push(c); if (c[3] >= 0.999) break; }
    }
    let base = layers.length && layers[layers.length - 1][3] >= 0.999 ? layers.pop() : (dark ? [0, 0, 0, 1] : [255, 255, 255, 1]);
    while (layers.length) base = over(layers.pop(), base);
    return {c: base, unknown};
  }
  const rows = [];
  for (const el of document.querySelectorAll('body *')) {
    const t = ownText(el);
    if (!t || !isVisible(el) || el.closest('svg, script, style')) continue;
    const cs = getComputedStyle(el);
    const op = opUp(el);
    if (op < 0.05) continue;
    let fg = parseColor(cs.color); if (!fg) continue;
    const bg = bgOf(el);
    fg = [fg[0], fg[1], fg[2], fg[3] * op];
    if (fg[3] < 1) fg = over(fg, bg.c);
    const l1 = L(fg), l2 = L(bg.c);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight, 10) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const isBtn = !!el.closest('button, a, [role=button], [data-go]');
    rows.push({text: t.slice(0, 20), kind: isBtn ? '按钮' : '正文', ratio: Math.round(ratio * 100) / 100, need: large ? 3 : 4.5, size, unknown: bg.unknown});
  }
  return rows;
}"""


def png_diff(a_bytes, b_bytes):
    """两张图有没有像素差（要 Pillow；没有返回 None）。"""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return None
    a = Image.open(io.BytesIO(a_bytes)).convert('RGB')
    b = Image.open(io.BytesIO(b_bytes)).convert('RGB')
    if a.size != b.size:
        return True
    return ImageChops.difference(a, b).getbbox() is not None


def probe_read(page, res):
    try:
        res['read'] = page.evaluate(READ_JS)
    except Exception as e:  # noqa: BLE001
        res['errors'].append(f'读屏顺序：{_first(e)}')
    tree = None
    try:
        snap = page.accessibility.snapshot(interesting_only=False)  # 新版 Playwright 已移除，走 aria 快照
        if snap:
            tree = ('page.accessibility.snapshot', _flatten(snap))
    except Exception:  # noqa: BLE001
        try:
            tree = ('locator.aria_snapshot', page.locator('body').aria_snapshot())
        except Exception as e:  # noqa: BLE001
            res['errors'].append(f'浏览器的可访问性树取不到：{_first(e)}')
    res['tree'] = tree


def _flatten(node, depth=0, out=None):
    out = [] if out is None else out
    if node.get('role') not in ('none', 'generic') or node.get('name'):
        out.append('  ' * depth + f'- {node.get("role")} "{node.get("name", "")}"')
    for c in node.get('children', []) or []:
        _flatten(c, depth + 1, out)
    return '\n'.join(out) if depth == 0 else out


def probe_keys(page, res, sdir, max_tabs):
    try:
        res['unreachable'] = page.evaluate(UNREACHABLE_JS)
    except Exception as e:  # noqa: BLE001
        res['errors'].append(f'键盘够不到的元素：{_first(e)}')
    seen, shots = set(), 0
    try:
        page.evaluate('() => { if (document.activeElement) document.activeElement.blur(); window.scrollTo(0, 0); }')
        for n in range(1, max_tabs + 1):
            page.keyboard.press('Tab')
            page.wait_for_timeout(60)
            info = page.evaluate(FOCUS_JS)
            if info is None:
                break
            key = (info['tag'], info['name'], tuple(round(x) for x in info['rect']))
            if key in seen:
                break
            seen.add(key)
            visible, how = bool(info['ring']), '轮廓' if info['ring'] else ''
            x, y, w, h = info['rect']
            pad = 12
            clip = {'x': max(0, x - pad), 'y': max(0, y - pad), 'width': 0, 'height': 0}
            clip['width'] = max(1, min(info['vw'] - clip['x'], w + 2 * pad))
            clip['height'] = max(1, min(info['vh'] - clip['y'], h + 2 * pad))
            png_on = None
            try:
                png_on = page.screenshot(clip=clip) if w > 0 and h > 0 and y < info['vh'] and y + h > 0 else None
            except Exception:  # noqa: BLE001
                png_on = None
            try:
                style_off = page.evaluate(BLUR_STYLE_JS)
                png_off = page.screenshot(clip=clip) if png_on is not None else None
                page.evaluate(REFOCUS_JS)
                if not visible and style_off is not None and style_off != info['style']:
                    visible, how = True, '样式变化'
                if not visible and png_on is not None and png_off is not None:
                    d = png_diff(png_on, png_off)
                    if d:
                        visible, how = True, '像素差'
            except Exception as e:  # noqa: BLE001
                res['errors'].append(f'第 {n} 下 Tab 的焦点样式没量成：{_first(e)}')
            if png_on is not None and (n <= 12 or not visible) and shots < 30:
                try:
                    with open(os.path.join(sdir, f'tab-{n:02d}.png'), 'wb') as f:
                        f.write(png_on)
                    shots += 1
                except OSError:
                    pass
            res['tabs'].append({'n': n, 'tag': info['tag'], 'name': info['name'], 'visible': visible, 'how': how})
    except Exception as e:  # noqa: BLE001
        res['errors'].append(f'Tab 路径：{_first(e)}')


def probe_zoom(page, url, res, sdir):
    for key, desc, js in (('fontsize', "根字号 200%（documentElement.style.fontSize='200%'）", "() => { document.documentElement.style.fontSize = '200%'; }"),
                          ('zoom', 'CSS zoom 2（documentElement.style.zoom=2）', "() => { document.documentElement.style.zoom = '2'; }")):
        r = {'key': key, 'desc': desc, 'effective': None, 'ratio': None, 'hscroll': None, 'clipped': [], 'overlaps': [], 'offscreen': [], 'error': ''}
        res['zoom'].append(r)
        try:
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_timeout(PAUSE)
            cc.settle(page)
            before = page.evaluate(ZOOM_JS, key)
            page.evaluate(RELEASE_JS)
            page.evaluate(js)
            page.wait_for_timeout(250)
            after = page.evaluate(ZOOM_JS, key)
            ratio = (after['h'] / before['h']) if before['h'] else 0
            fs_ratio = (after['fs'] / before['fs']) if before['fs'] else 0
            r['ratio'] = max(ratio, fs_ratio)
            r['effective'] = r['ratio'] >= 1.5
            try:
                page.screenshot(path=os.path.join(sdir, f'zoom-{key}.png'))
            except Exception:  # noqa: BLE001
                pass
            o = page.evaluate(OVERFLOW_JS)
            r['hscroll'] = o['hscroll']
            r['sw'], r['vw'] = o['sw'], o['vw']
            r['clipped'], r['overlaps'], r['offscreen'] = o['clipped'], o['overlaps'], o['offscreen']
        except Exception as e:  # noqa: BLE001
            r['error'] = _first(e)


def probe_contrast(page, res):
    try:
        res['contrast'] = page.evaluate(CONTRAST_JS)
    except Exception as e:  # noqa: BLE001
        res['errors'].append(f'对比度：{_first(e)}')


def _first(e):
    return (str(e).splitlines() or [''])[0][:140]


def state_issues(res):
    """这个状态有哪些问题（用于结论和退出码）。"""
    out = []
    for r in res['read']:
        if r['unnamed']:
            out.append(f'没有名称的控件：{r["role"]}（{r["tag"]}）')
    for u in res['unreachable']:
        out.append(f'键盘到不了：{u}')
    for t in res['tabs']:
        if not t['visible']:
            out.append(f'第 {t["n"]} 下 Tab（{t["name"] or t["tag"]}）没有看得见的焦点样式')
    effective = [z for z in res['zoom'] if z['effective']]
    text_resize = any(z['key'] == 'fontsize' and z['effective'] for z in res['zoom'])
    for z in res['zoom']:
        if z['error']:
            out.append(f'200%（{z["key"]}）没测成：{z["error"]}')
            continue
        if z['effective'] is False or (text_resize and z['key'] == 'zoom'):
            continue
        if z['hscroll']:
            out.append(f'200%（{z["key"]}）横向溢出：内容宽 {z.get("sw")} > 视口 {z.get("vw")}')
        for c in z['clipped']:
            out.append(f'200%（{z["key"]}）文字被裁：{c}')
        for c in z['overlaps']:
            out.append(f'200%（{z["key"]}）元素重叠：{c}')
    if res['zoom'] and not effective and all(z['error'] == '' for z in res['zoom']):
        out.append('200% 两种放大方式都没把字放大，没法证明放大后能用')
    for c in res['contrast']:
        if not c['unknown'] and c['ratio'] < c['need']:
            out.append(f'对比度 {c["ratio"]}:1 < {c["need"]}:1（{c["kind"]}「{c["text"]}」）')
    return out


def write_md(results, a, extra):
    lines = ['# 无障碍实测（a11y_probe）', '',
             f'测法：真实浏览器（Chromium）实测。视口 {a.size or '按 canvas.json 里画板的尺寸，没有就 390x844'}，语言 {a.lang}，主题 {a.theme}，Tab 最多 {a.max_tabs} 下。', '']
    total = 0
    for res in results:
        issues = state_issues(res) + [f'没测成：{e}' for e in res['errors']]
        total += len(issues)
        lines += [f'## {res["board"]}「{res["state"]}」', '', f'截图：`{res["dir"]}/`', '']
        lines += ['### 读屏顺序', '']
        if res['read']:
            lines += ['| 序 | 角色 | 名称 |', '|---|---|---|']
            for i, r in enumerate(res['read'], 1):
                nm = r['name'].replace('|', '\\|') or '—'
                lines.append(f'| {i} | {r["role"]} | {"**没有名称** " if r["unnamed"] else ""}{nm} |')
        else:
            lines.append('没取到。')
        lines.append('')
        if res.get('tree'):
            lines += [f'浏览器自己算的树（{res["tree"][0]}）：', '', '```', str(res['tree'][1])[:3000], '```', '']
        lines += ['### 键盘路径（从顶部连按 Tab）', '']
        if res['tabs']:
            lines += ['| 第几下 | 焦点在 | 看得见的焦点样式 |', '|---|---|---|']
            for t in res['tabs']:
                lines.append(f'| {t["n"]} | {(t["name"] or "—").replace("|", "/")}（{t["tag"]}） | {"有（" + t["how"] + "）" if t["visible"] else "**没有**"} |')
        else:
            lines.append('Tab 没有落到任何元素上。')
        lines.append('')
        if res['unreachable']:
            lines += ['点得到但按 Tab 到不了：', ''] + [f'- {u}' for u in res['unreachable']] + ['']
        lines += ['### 200% 字号', '']
        for z in res['zoom']:
            if z['error']:
                lines.append(f'- {z["desc"]}：没测成：{z["error"]}')
                continue
            lines.append(f'- {z["desc"]}：**{"生效" if z["effective"] else "没生效"}**（文字高度 ×{z["ratio"]:.2f}）'
                         + ('' if z['effective'] else '，下面的溢出、被裁数字不作数'))
            if z['effective']:
                lines.append(f'  - 横向溢出：{"有（内容宽 %s > 视口 %s）" % (z.get("sw"), z.get("vw")) if z["hscroll"] else "没有"}')
                lines.append(f'  - 文字被裁：{"；".join(z["clipped"]) or "没有"}')
                lines.append(f'  - 元素重叠：{"；".join(z["overlaps"]) or "没有"}')
                if z['offscreen']:
                    lines.append(f'  - 文字超出视口：{"；".join(z["offscreen"])}')
        lines.append('')
        lines += ['### 对比度（前景色对有效背景色）', '']
        rows = res['contrast']
        if rows:
            for kind in ('正文', '按钮'):
                ks = [r for r in rows if r['kind'] == kind and not r['unknown']]
                if ks:
                    worst = min(ks, key=lambda r: r['ratio'])
                    lines.append(f'- {kind}文字最低 **{worst["ratio"]}:1**（「{worst["text"]}」，{worst["size"]:g}px，要 {worst["need"]}:1）；共 {len(ks)} 处，不达标 {sum(1 for r in ks if r["ratio"] < r["need"])} 处')
            unk = [r for r in rows if r['unknown']]
            if unk:
                lines.append(f'- 量不了（背景是图或渐变）：{len(unk)} 处，如「{unk[0]["text"]}」，要人看')
            lines += ['', '最低的 5 处：', '', '| 类 | 文字 | 对比度 | 要求 |', '|---|---|---|---|']
            for r in sorted([r for r in rows if not r['unknown']], key=lambda r: r['ratio'])[:5]:
                lines.append(f'| {r["kind"]} | {r["text"].replace("|", "/")} | {r["ratio"]}:1 | {r["need"]}:1 |')
        else:
            lines.append('没取到。')
        lines += ['', '### 这个状态的问题', '']
        lines += [f'- {i}' for i in issues] or ['没发现问题。']
        lines.append('')
    lines += ['## 结论', '', f'**{"发现 %d 个问题" % total if total else "没发现问题"}**（{len(results)} 个状态）。' + ''.join('\n\n' + e for e in extra), '']
    return '\n'.join(lines), total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('canvas')
    ap.add_argument('--states', required=True, help='JSON：[{"board": "AI-Today", "state": "训练日"}]')
    ap.add_argument('--out', required=True)
    ap.add_argument('--lang', default='zh', choices=['zh', 'en'])
    ap.add_argument('--theme', default='light', choices=['light', 'dark'])
    ap.add_argument('--size', default=None, help='视口，默认取 canvas.json 里画板的尺寸，没有就 390x844')
    ap.add_argument('--max-tabs', type=int, default=40)
    a = ap.parse_args()

    sync_playwright = cc.need_playwright()
    try:
        wanted = json.load(open(a.states, encoding='utf-8'))
        assert isinstance(wanted, list)
    except (OSError, ValueError, AssertionError) as e:
        print(f'读不了 --states 文件 {a.states}：{e}', file=sys.stderr)
        sys.exit(2)
    boards = cc.load_boards(a.canvas, a.lang)
    sizes = cc.board_sizes(a.canvas)
    os.makedirs(a.out, exist_ok=True)
    stage = cc.Stage(a.canvas)
    results, extra = [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for n, w in enumerate(wanted, 1):
                key = cc.board_key(w.get('board', ''))
                board = boards.get(key)
                idx = board.index(w.get('state')) if board else None
                name = (board.names[idx] if board is not None and idx is not None else str(w.get('state')))
                sdir = f'{n:02d}-{cc.safe_name(key)}-{cc.safe_name(name)}'
                print(f'[{n}/{len(wanted)}] {key} · {name}', flush=True)
                res = {'board': key, 'state': name, 'dir': sdir, 'read': [], 'tree': None, 'tabs': [], 'unreachable': [], 'zoom': [], 'contrast': [], 'errors': []}
                results.append(res)
                if board is None or idx is None:
                    res['errors'].append(f'找不到画板或状态：{w}')
                    continue
                os.makedirs(os.path.join(a.out, sdir), exist_ok=True)
                full = os.path.join(a.out, sdir)
                vw, vh = cc.parse_size(a.size) if a.size else sizes.get(key, (390, 844))
                ctx = None
                try:
                    ctx = browser.new_context(viewport={'width': vw, 'height': vh}, color_scheme=a.theme,
                                              locale='zh-CN' if a.lang == 'zh' else 'en-US', device_scale_factor=1)
                    page = ctx.new_page()
                    url = stage.write(cc.themed(board.html(idx), a.theme))
                    page.goto(url, wait_until='domcontentloaded')
                    page.wait_for_timeout(PAUSE)
                    cc.settle(page)
                    try:
                        page.screenshot(path=os.path.join(full, 'base.png'))
                    except Exception:  # noqa: BLE001
                        pass
                    probe_read(page, res)
                    probe_contrast(page, res)
                    probe_keys(page, res, full, a.max_tabs)
                    probe_zoom(page, url, res, full)
                except Exception as e:  # noqa: BLE001
                    res['errors'].append(f'浏览器出错：{_first(e)}')
                finally:
                    if ctx:
                        try:
                            ctx.close()
                        except Exception:  # noqa: BLE001
                            pass
            browser.close()
    except Exception as e:  # noqa: BLE001
        extra.append(f'浏览器整体出错：{_first(e)}')
    finally:
        stage.close()
    md, total = write_md(results, a, extra)
    path = os.path.join(a.out, 'a11y.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(path)
    sys.exit(1 if total or extra else 0)


if __name__ == '__main__':
    main()
