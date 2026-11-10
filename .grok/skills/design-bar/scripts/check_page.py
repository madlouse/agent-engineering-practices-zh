#!/usr/bin/env python3
"""渲染页面、截图，并运行确定性设计检查。

用法：
  python check_page.py <URL 或本地 HTML 路径> [--out 目录] [--widths 375,768,1440]
                       [--shots-only] [--dark] [--min-font 14] [--min-target 44]
                       [--max-font-sizes 8] [--max-text-colors 6]

输出：
  <out>/shot-<宽度>-viewport.png、shot-<宽度>-full.png（--dark 时另有 -dark 版本）
  <out>/report.json、<out>/report.md

依赖：pip install playwright && python -m playwright install chromium
"""
import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

MOBILE_MAX = 480

COLLECT_JS = r"""
(opts) => {
  const vw = document.documentElement.clientWidth;
  const out = {};

  // rgb() 直接读；oklab()、color-mix()、color(srgb …) 画到 1×1 画布上取像素
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', {willReadFrequently: true});
  const parse = (c) => {
    if (!c || c === 'transparent') return null;
    const m = c.match(/^rgba?\(([^)]+)\)$/);
    if (m) { const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; }
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    return {r: d[0], g: d[1], b: d[2], a: d[3] / 255};
  };
  const lum = ({r, g, b}) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const blend = (fg, bg) => ({
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1,
  });
  const effectiveBg = (el) => {
    const layers = [];
    let node = el;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null; // 图片或渐变背景，无法可靠计算
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
      node = node.parentElement;
    }
    let bg = {r: 255, g: 255, b: 255, a: 1};
    for (let i = layers.length - 1; i >= 0; i--) bg = blend(layers[i], bg);
    return bg;
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && Number(cs.opacity) > 0;
  };
  const sel = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    else if (el.classList.length) s += '.' + [...el.classList].slice(0, 2).join('.');
    const t = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 30);
    return t ? `${s} 「${t}」` : s;
  };

  // 横向溢出
  out.overflow = document.documentElement.scrollWidth > vw + 1;
  out.overflowers = [];
  if (out.overflow) {
    for (const el of document.querySelectorAll('body *')) {
      if (!visible(el)) continue;
      const r = el.getBoundingClientRect();
      if (r.right > vw + 1 || r.left < -1) {
        out.overflowers.push(`${sel(el)} 右边界 ${Math.round(r.right)}px`);
        if (out.overflowers.length >= 8) break;
      }
    }
  }

  // 文本：字号、颜色、字体、对比度
  const sizes = {}, colors = {}, families = {};
  out.smallText = []; out.lowContrast = []; out.contrastUnknown = 0;
  for (const el of document.querySelectorAll('body *')) {
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (!hasText || !visible(el)) continue;
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize);
    const fw = parseInt(cs.fontWeight, 10) || 400;
    sizes[fs] = (sizes[fs] || 0) + 1;
    colors[cs.color] = (colors[cs.color] || 0) + 1;
    const fam = cs.fontFamily.split(',')[0].trim().replace(/["']/g, '');
    families[fam] = (families[fam] || 0) + 1;
    if (fs < opts.minFont && out.smallText.length < 10) out.smallText.push(`${sel(el)} ${fs}px`);
    const fg = parse(cs.color);
    const bg = effectiveBg(el);
    if (!fg || !bg) { out.contrastUnknown++; continue; }
    const fgb = fg.a < 1 ? blend(fg, bg) : fg;
    const L1 = lum(fgb), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const large = fs >= 24 || (fs >= 18.66 && fw >= 700);
    const need = large ? 3 : 4.5;
    if (ratio < need && out.lowContrast.length < 12) out.lowContrast.push(`${sel(el)} ${ratio.toFixed(2)}:1（需要 ≥ ${need}）`);
  }
  out.fontSizes = Object.keys(sizes).map(Number).sort((a, b) => a - b);
  out.textColors = Object.keys(colors);
  out.fontFamilies = Object.keys(families);

  // 触控目标（仅移动宽度）
  out.smallTargets = [];
  if (vw <= opts.mobileMax) {
    const q = 'a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=link], [tabindex]:not([tabindex="-1"])';
    for (const el of document.querySelectorAll(q)) {
      if (!visible(el)) continue;
      const cs = getComputedStyle(el);
      // 段落内的行内文字链接按 WCAG 2.5.8 豁免
      if (el.tagName === 'A' && cs.display === 'inline' && el.parentElement && /^(P|LI|SPAN|TD|DD|BLOCKQUOTE)$/.test(el.parentElement.tagName)) continue;
      const r = el.getBoundingClientRect();
      if (r.width < opts.minTarget || r.height < opts.minTarget) {
        out.smallTargets.push(`${sel(el)} ${Math.round(r.width)}×${Math.round(r.height)}`);
        if (out.smallTargets.length >= 10) break;
      }
    }
  }

  // 语义
  out.lang = document.documentElement.getAttribute('lang') || '';
  out.imgNoAlt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).map(i => i.getAttribute('src') || '(no src)').slice(0, 10);
  const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(visible).map(h => Number(h.tagName[1]));
  out.h1Count = hs.filter(l => l === 1).length;
  out.headingSkips = [];
  for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i - 1] > 1) out.headingSkips.push(`h${hs[i - 1]} → h${hs[i]}`);

  // 动效与 reduced-motion
  let rm = false;
  for (const sh of document.styleSheets) {
    try { for (const rule of sh.cssRules) if (rule.cssText.includes('prefers-reduced-motion')) { rm = true; break; } } catch (e) {}
    if (rm) break;
  }
  out.hasReducedMotionQuery = rm;
  let animated = 0;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if ((cs.animationName && cs.animationName !== 'none') || parseFloat(cs.transitionDuration) > 0) animated++;
  }
  out.animatedCount = animated + (document.getAnimations ? document.getAnimations().length : 0);
  return out;
}
"""

FOCUS_JS = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const cs = getComputedStyle(el);
  const outline = cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0;
  const shadow = cs.boxShadow && cs.boxShadow !== 'none';
  const t = (el.innerText || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30);
  return {name: el.tagName.toLowerCase() + ' 「' + t + '」', visible: outline || shadow};
}
"""


def stylesheets_mention(page, needle):
    """读取页面引用的样式表和内联 <style> 的源文本，判断是否包含 needle。"""
    hrefs, inline = page.evaluate("""() => [
      [...document.querySelectorAll('link[rel~="stylesheet"]')].map(l => l.href),
      [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n')]""")
    if needle in inline:
        return True
    for h in hrefs:
        try:
            if h.startswith("file://"):
                from urllib.parse import unquote, urlparse
                text = pathlib.Path(unquote(urlparse(h).path)).read_text(encoding="utf-8", errors="ignore")
            else:
                text = page.request.get(h).text()
        except Exception:
            continue
        if needle in text:
            return True
    return False


def resolve_target(t):
    p = pathlib.Path(t)
    if p.exists():
        return p.resolve().as_uri()
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out", default="design-check")
    ap.add_argument("--widths", default="375,768,1440")
    ap.add_argument("--shots-only", action="store_true")
    ap.add_argument("--dark", action="store_true", help="另截一组深色模式截图")
    ap.add_argument("--min-font", type=float, default=14)
    ap.add_argument("--min-target", type=float, default=44)
    ap.add_argument('--targets-up-to', type=int, default=MOBILE_MAX, help='在不超过这个宽度的截图上检查触控目标（默认 480，只查手机）；全站要求可点区域都够大时设成最大宽度')
    ap.add_argument("--max-font-sizes", type=int, default=8)
    ap.add_argument("--max-text-colors", type=int, default=6)
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url = resolve_target(a.target)
    widths = [int(w) for w in a.widths.split(",")]
    report = {"target": url, "widths": {}, "console_errors": [], "focus": None}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        schemes = ["light", "dark"] if a.dark else ["light"]
        for scheme in schemes:
            for w in widths:
                h = 812 if w <= MOBILE_MAX else 900
                ctx = browser.new_context(viewport={"width": w, "height": h}, color_scheme=scheme,
                                          device_scale_factor=1)
                page = ctx.new_page()
                if scheme == "light" and w == widths[0]:
                    page.on("console", lambda m: report["console_errors"].append(m.text) if m.type == "error" else None)
                    page.on("pageerror", lambda e: report["console_errors"].append(str(e)))
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                except Exception:
                    page.goto(url, wait_until="load", timeout=30000)
                page.wait_for_timeout(600)
                suffix = "" if scheme == "light" else "-dark"
                page.screenshot(path=str(out / f"shot-{w}{suffix}-viewport.png"))
                page.screenshot(path=str(out / f"shot-{w}{suffix}-full.png"), full_page=True)
                if not a.shots_only and scheme == "light":
                    report["widths"][w] = page.evaluate(COLLECT_JS, {
                        "minFont": a.min_font, "minTarget": a.min_target, "mobileMax": a.targets_up_to})
                    if not report["widths"][w]["hasReducedMotionQuery"]:
                        # file:// 或跨域样式表的 cssRules 读不到：直接读样式表源文件
                        report["widths"][w]["hasReducedMotionQuery"] = stylesheets_mention(
                            page, "prefers-reduced-motion")
                    if w == widths[-1]:
                        focus = []
                        for _ in range(10):
                            page.keyboard.press("Tab")
                            r = page.evaluate(FOCUS_JS)
                            if r:
                                focus.append(r)
                        report["focus"] = focus
                ctx.close()
        browser.close()

    if a.shots_only:
        print(f"截图已保存到 {out}")
        return

    md = write_markdown(report, a)
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "report.md").write_text(md, encoding="utf-8")
    print(md)


def write_markdown(r, a):
    lines = [f"# 设计检查报告\n\n目标：{r['target']}\n"]
    issues = 0

    def item(ok, text, details=None):
        nonlocal issues
        if not ok:
            issues += 1
        lines.append(f"- {'✅' if ok else '❌'} {text}")
        for d in (details or [])[:8]:
            lines.append(f"    - {d}")

    for w, d in r["widths"].items():
        lines.append(f"\n## {w}px\n")
        item(not d["overflow"], "无横向溢出", d["overflowers"])
        item(not d["smallText"], f"没有小于 {a.min_font}px 的文字", d["smallText"])
        unknown = f"（另有 {d['contrastUnknown']} 处位于图片或渐变背景上，需人工检查）" if d["contrastUnknown"] else ""
        item(not d["lowContrast"], f"文本对比度达标{unknown}", d["lowContrast"])
        if int(w) <= a.targets_up_to:
            item(not d["smallTargets"], f"触控目标 ≥ {a.min_target}px", d["smallTargets"])

    widest = r["widths"][max(r["widths"], key=int)]
    lines.append("\n## 全局\n")
    item(bool(widest["lang"]), f"html 声明了语言：{widest['lang'] or '缺失'}")
    item(widest["h1Count"] == 1, f"有且只有一个 h1（当前 {widest['h1Count']} 个）")
    item(not widest["headingSkips"], "标题层级没有跳级", widest["headingSkips"])
    item(not widest["imgNoAlt"], "所有图片都有 alt 属性", widest["imgNoAlt"])
    sizes = widest["fontSizes"]
    item(len(sizes) <= a.max_font_sizes, f"字号种类 {len(sizes)} 种（上限 {a.max_font_sizes}）：{', '.join(f'{s:g}' for s in sizes)}")
    item(len(widest["textColors"]) <= a.max_text_colors,
         f"文本颜色 {len(widest['textColors'])} 种（上限 {a.max_text_colors}）", widest["textColors"])
    lines.append(f"- ℹ️ 声明的首选字体（未必实际加载成功，请对照截图）：{', '.join(widest['fontFamilies'])}")
    if widest["animatedCount"]:
        item(widest["hasReducedMotionQuery"], f"有 {widest['animatedCount']} 处动画或过渡，并提供 prefers-reduced-motion 处理")
    if r["focus"] is not None:
        bad = list(dict.fromkeys(f["name"] for f in r["focus"] if not f["visible"]))
        item(bool(r["focus"]) and not bad, "键盘聚焦时有可见的焦点样式" + ("" if r["focus"] else "（Tab 未聚焦到任何元素）"), bad)
    item(not r["console_errors"], "控制台没有报错", r["console_errors"])

    lines.insert(1, f"**{issues} 项未通过。** 机械检查只能发现已知的问题，构图、层级和品位仍需看截图判断。\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
