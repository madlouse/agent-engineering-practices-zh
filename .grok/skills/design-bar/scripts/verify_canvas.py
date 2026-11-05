#!/usr/bin/env python3
"""画板验证：把 Claude Design 画布的每块画板、每个状态，按浅色和深色各渲染一次，只报真问题，最后给结论。

和 check_page.py 的分工：check_page 看真实页面（多宽度、响应式）；本脚本看固定尺寸的画板（390×844 之类），
所以不会把「画板比 375 宽」当成溢出，也不会把画板里有意写的内联样式当成问题。

检查项（都是会让用户看错、点不到、看不清的问题，不报审美意见）：
  1. 主按钮被挡住：宽度 ≥ 画板 60%、高度 ≥ 44 的实色按钮，底边落在底部输入区或画板外
  2. 文字被挤成竖排：一段文字的宽度不到两个字、高度却超过 2.5 行
  3. 内容超出画板：元素右边超出画板（画板会把它裁掉）
  4. 对比度：正文 < 4.5:1、大字 < 3:1（禁用态按钮除外；浅色、深色各查一次）
  5. 触控目标 < 44×44（段落里的文字链接除外）
  6. 引用了没定义的 token：var(--x) 在样式表里找不到
  11. 展开层超出所在区块：aria-expanded 的控件用 aria-controls 指向的展开层，要完整留在所在 <section> 里
  12. 可点元素被盖住：链接、按钮、输入框的中心点上面压着别的控件或浮层
  13. 首屏主操作在视口外：第一个 <section> 里的按钮和表单，底边超出视口（配合 --size 查 1280×720 这类常见高度）
  14. 深色下露出浅色底：主题只设在里层，画板比视口矮或有外边距时，外面露出浅色的 body
  15. 按钮文字折行：按钮里的字折成两行（伪语言那一遍最容易出现）
  16. 浮层没有出路：对话框、菜单里没有「关闭」按钮，画板逻辑也没处理 Esc
  17. 孤字成行：两行以上的标题和段落，最后一行只剩一个汉字或一个短词
  18. 词中断行：标题、按钮、标签这类 40 字以内的短文字里，中文词被拆到两行（Intl.Segmenter 分词）；正文段落只查孤字
  19. 文字冲出容器、短标签被挤成多行：文字超出所在的圆角条或卡片；一行控件里三个词以内的标签折成三行以上
  （另）占位文字：画板上出现「示例」「待定」「即将上线」「二维码」这类占位词（--placeholders 可改）
  7. 写死的颜色：画板源码里出现 #hex、rgb()、hsl()（token 文件除外）
  8. 页面报错：控制台 error、脚本异常（字体等网络资源加载失败只记为提示）
  9. 画出来就要能用（来自 baoyu-design「Accessible as drawn」）：<a> 没有 href、div/span 上挂点击、
     只有图标的按钮没有可读名称、输入框没有标签——静态稿也要用真的 <button> / <a href> / <label>
 10. 弹性布局吞掉空格：flex / grid 容器里的文字和元素挨着时，文字两头的空格会被吞掉（「还剩3天」）

另外列出「模板味信号」（来自 unslop 的信号清单里机器能看出的那部分：emoji、渐变文字、全大写加宽字距、
特粗标题、感叹号、按钮文字带句号、斜体强调、小字负字距、transition: all），只作提示，不影响结论；
要不要改按 unslop 的审计判断。

伪语言（--themes 里加 pseudo）：把每段文字加长 35%（PRD 常见的「德语比中文长 35%」口径），按浅色再查一遍
版式类问题（主按钮被挡或挤扁、竖排、超出画板、吞空格），看换语言以后会不会坏；对比度和 token 不在这一遍重复查。

属性和视口：data-props 里的枚举属性（theme 除外，主题由 --themes 管）每个非默认选项各查一遍，别的属性取默认，
报告里记作「lang=English」；--size 名称=宽x高 让一块自适应的画板在另一个视口下再查一遍（例如手机画板在 320 宽下）。

用法：
  python verify_canvas.py <画板目录或 .dc.html ...> --out <报告目录> [--themes light,dark,pseudo] [--only AI-Plans]
画板尺寸从同目录的 canvas.json 读（没有就用 390x844；带 expand 的说明文档页不查触控尺寸）；状态从 <sc-if value="{{ sN }}"> 自动发现。
结论：没有问题时 done（退出码 0），有问题时 needs_work（退出码 1）。需要 Python Playwright 和 Chromium。
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_dc import render_html, logic_values  # noqa: E402

PSEUDO_JS = r"""
() => {
  const root = document.querySelector('[data-theme]') || document.body;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) {
    const t = n.textContent; const core = t.trim();
    if (core.length < 2 || n.parentElement.closest('script, style, svg')) continue;
    const own = n.parentElement.closest('[lang]');
    if (own && own !== root && (own.getAttribute('lang') !== root.getAttribute('lang') || own.closest('button, .seg'))) continue;  // 语言切换按钮上的语言名不随翻译变长
    if (!/[A-Za-z\u4e00-\u9fff]/.test(core)) continue;  // 只有数字和符号（时间、页码）的不随翻译变长
    const extra = Math.ceil(core.length * 0.35);
    n.textContent = t.replace(core, core + core.repeat(2).slice(0, extra));
  }
}
"""

LAYOUT_TYPES = {'主按钮被挡住或在首屏外', '主按钮被挤扁', '文字被挤成竖排', '内容超出画板', '弹性布局吞掉了空格', '展开层超出所在区块', '可点元素被盖住', '首屏主操作在视口外', '按钮文字折行', '文字冲出容器', '短标签被挤成多行'}

CHECK_JS = r"""
() => {
  const issues = [];
  const root = document.querySelector('[data-theme]') || document.body;
  const R = root.getBoundingClientRect();
  const footers = [...root.querySelectorAll('footer')];
  const footer = footers.length ? footers[footers.length - 1] : null;
  const fTop = footer ? footer.getBoundingClientRect().top : R.bottom;
  const visible = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length > 0; };
  const name = el => ((el.getAttribute && el.getAttribute('aria-label')) || el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 36);
  const parseColor = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(x => parseFloat(x)); return (p.length > 3 ? p[3] : 1) > 0.05 ? p : null; };
  const parse = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(x => parseFloat(x)); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, under) => ({r: top.r * top.a + under.r * (1 - top.a), g: top.g * top.a + under.g * (1 - top.a), b: top.b * top.a + under.b * (1 - top.a), a: 1});
  const bgOf = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !/gradient/.test(cs.backgroundImage)) return null; // 图片上的字交给人看
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    let base = {r: 255, g: 255, b: 255, a: 1};
    for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base);
    return base;
  };
  const clipped = el => { for (let e = el.parentElement; e && e !== root; e = e.parentElement) { const ox = getComputedStyle(e).overflowX; if (ox === 'auto' || ox === 'scroll' || ox === 'hidden') return true; } return false; };

  // 1、5：按钮
  for (const el of root.querySelectorAll('button, a, [role="button"], input, label')) {
    if (!visible(el) || (footer && footer.contains(el) && el.tagName !== 'BUTTON')) continue;
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    const bg = parse(cs.backgroundColor);
    const filled = (bg && bg.a > 0.5) || (cs.backgroundImage && cs.backgroundImage !== 'none');
    let squashed = false;
    if ((el.tagName === 'BUTTON' || el.tagName === 'A') && !(footer && footer.contains(el)) && filled && r.width >= R.width * 0.6) {
      const limit = Math.min(fTop, R.bottom);
      if (r.bottom > limit + 1) issues.push({type: '主按钮被挡住或在首屏外', where: name(el), detail: `按钮底边 ${Math.round(r.bottom)}，可见到 ${Math.round(limit)}；首屏放不下时先删说明文字，再压缩卡片，不靠滚动`});
      if (r.height < 43.5) { squashed = true; issues.push({type: '主按钮被挤扁', where: name(el), detail: `高 ${Math.round(r.height)}：上面的内容太多，flex 把按钮压扁了（按钮加 flex: none，并按上一条压缩内容）`}); }
    }
    const interactive = el.tagName === 'BUTTON' || el.tagName === 'A' || el.getAttribute('role') === 'button';
    if (interactive && !name(el) && !el.getAttribute('title')) issues.push({type: '控件没有可读名称', where: el.tagName.toLowerCase(), detail: '只有图标的按钮要写 aria-label，读屏才念得出来'});
    if (el.tagName === 'INPUT' && !['checkbox', 'radio', 'hidden'].includes(el.type) && !el.getAttribute('aria-label') && !el.closest('label') && !(el.id && document.querySelector(`label[for="${el.id}"]`)))
      issues.push({type: '控件没有可读名称', where: el.placeholder || 'input', detail: '输入框要有 <label> 或 aria-label，占位文字不算'});
    if (interactive && !squashed && r.width > 0 && (r.width < 43.5 || r.height < 43.5) && !el.closest('p, li > span')) {
      issues.push({type: '触控目标小于 44', where: name(el) || el.tagName.toLowerCase(), detail: `${Math.round(r.width)}×${Math.round(r.height)}`});
    }
  }
  // 2、3、4：文字
  const seen = new Set();
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode; const text = t.textContent.trim();
    if (!text) continue;
    const el = t.parentElement;
    if (!el || seen.has(el) || !visible(el) || el.closest('[aria-hidden="true"], svg, script, style')) continue;
    seen.add(el);
    const cs = getComputedStyle(el); const fs = parseFloat(cs.fontSize); const lh = parseFloat(cs.lineHeight) || fs * 1.4;
    const r = el.getBoundingClientRect();
    const vertical = cs.writingMode.startsWith('vertical');  // 有意的竖排（书脊）不算
    if (!vertical && text.length >= 3 && r.width < fs * 2.2 && r.height > lh * 2.5) issues.push({type: '文字被挤成竖排', where: text.slice(0, 20), detail: `宽 ${Math.round(r.width)}、高 ${Math.round(r.height)}`});
    if (r.right > R.right + 1 && !clipped(el)) issues.push({type: '内容超出画板', where: text.slice(0, 20), detail: `右边 ${Math.round(r.right)} > ${Math.round(R.right)}`});
    if (el.closest('button[disabled], [aria-disabled="true"]')) continue;
    const fg = parse(cs.color); const bg = bgOf(el);
    if (fg && bg) {
      const f = fg.a < 1 ? blend(fg, bg) : fg;
      const L1 = lum(f), L2 = lum(bg); const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const large = fs >= 24 || (fs >= 18.66 && parseInt(cs.fontWeight) >= 700);
      const need = large ? 3 : 4.5;
      if (ratio < need - 0.05) issues.push({type: '对比度不够', where: text.slice(0, 20), detail: `${ratio.toFixed(2)}:1，要 ${need}:1`});
    }
  }
  // 11：展开层完整留在所在区块里（aria-expanded="true" 的控件用 aria-controls 指向它）
  for (const t of root.querySelectorAll('[aria-expanded="true"][aria-controls]')) {
    const layer = document.getElementById(t.getAttribute('aria-controls'));
    const sec = layer && layer.closest('section');
    if (!layer || !sec || !visible(layer)) continue;
    const a = layer.getBoundingClientRect(), b = sec.getBoundingClientRect();
    if (a.bottom > b.bottom + 1 || a.right > b.right + 1 || a.top < b.top - 1 || a.left < b.left - 1)
      issues.push({type: '展开层超出所在区块', where: name(t), detail: `展开层 ${Math.round(a.top)}–${Math.round(a.bottom)}，区块 ${Math.round(b.top)}–${Math.round(b.bottom)}`});
  }
  // 12：可点元素被别的东西盖住（看它中心那一点最上面是不是它自己）
  for (const el of root.querySelectorAll('a[href], button, input')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
    const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    if (!hit || el.contains(hit) || hit.contains(el)) continue;
    const owner = hit.closest('a[href], button, input, [role="group"], [role="dialog"], [role="menu"], form, header, nav');
    if (owner && !owner.contains(el) && !el.contains(owner)) issues.push({type: '可点元素被盖住', where: name(el), detail: `被「${name(owner) || owner.tagName.toLowerCase()}」盖住`});
  }
  // 13：首屏（第一个 section）里的按钮和表单完整留在视口里
  const hero = root.querySelector('section');
  if (hero) for (const el of hero.querySelectorAll('.btn, form, [role="switch"]')) {
    if (!visible(el) || el.closest('[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect();
    if (r.bottom > innerHeight + 1) issues.push({type: '首屏主操作在视口外', where: name(el), detail: `底边 ${Math.round(r.bottom)} > 视口 ${innerHeight}；首屏高度按 100svh 算，内容跟着视口压缩`});
  }
  // 14：深色主题下画板外露出浅色底
  {
    const opaque = el => { const c = parse(getComputedStyle(el).backgroundColor); return c && c.a > 0 ? c : null; };
    const page = opaque(document.body) || opaque(document.documentElement) || {r: 255, g: 255, b: 255, a: 1};  // 都透明时浏览器画白底
    const own = bgOf(root);
    const gap = R.top > 1 || R.left > 1 || R.bottom < Math.max(innerHeight, document.documentElement.scrollHeight) - 1;
    if (own && lum(own) < 0.2 && gap && page.a > 0 && lum(page) > 0.4) issues.push({type: '深色下露出浅色底', where: 'body', detail: '主题只设在里层，外面的 body 还是浅色；主题设到 :root，body 背景跟着主题'});
  }
  // 15：按钮文字折行（C4：一行放下，放不下改排法）
  for (const el of root.querySelectorAll('.btn, button, [role="button"]')) {
    if (!visible(el)) continue;
    const t = (el.innerText || '').trim(); if (!t) continue;
    const cs = getComputedStyle(el); const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3;
    const tops = [];
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (tw.nextNode()) { if (!tw.currentNode.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(tw.currentNode); for (const r of rg.getClientRects()) if (r.width > 1) tops.push(r.top); }
    tops.sort((a, b) => a - b);
    const lines = new Set(); let last = -1e9; for (const tp of tops) { if (tp - last > lh * 0.5) { lines.add(tp); last = tp; } }
    if (lines.size > 1) issues.push({type: '按钮文字折行', where: t.slice(0, 24), detail: `折成 ${lines.size} 行；按钮文字一行放下，放不下时改排法，不缩字号`});
  }
  // 16：浮层要有出路（U6）：展开的层、对话框、菜单里有关闭按钮，或画板逻辑处理了 Esc
  for (const layer of root.querySelectorAll('[role="dialog"], [role="menu"], [aria-modal="true"]')) {
    if (!visible(layer)) continue;
    const closer = [...layer.querySelectorAll('button, a[href]')].some(b => /关闭|收起|取消|完成|Close|Cancel|Done/i.test(name(b)));
    if (!closer && !window.__dcHandlesEscape) issues.push({type: '浮层没有出路', where: name(layer) || layer.getAttribute('role'), detail: '弹层里放一个「关闭」按钮，并处理 Esc 和点外面关闭'});
  }
  // 17：孤字成行（V9）：两行以上的段落，最后一行只有一个汉字或一个词
  for (const el of root.querySelectorAll('h1, h2, h3, h4, p, li, figcaption, dd, td, .lead, .row-title, .row-line')) {
    if (!visible(el) || el.closest('svg, [aria-hidden="true"]')) continue;
    if (/flex|grid|table/.test(getComputedStyle(el).display)) continue;  // 弹性和网格容器里各格并排，不是一段文字的多行
    if ([...el.children].some(c => !getComputedStyle(c).display.startsWith('inline'))) continue;  // 里面有块级子元素，最后一行属于别的块
    const rg = document.createRange(); rg.selectNodeContents(el);
    const rects = [...rg.getClientRects()].filter(r => r.width > 0.5);
    if (rects.length < 2) continue;
    const lastTop = Math.max(...rects.map(r => r.top));
    const firstTop = Math.min(...rects.map(r => r.top));
    if (lastTop - firstTop < 4) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const lastW = rects.filter(r => Math.abs(r.top - lastTop) < 3).reduce((a, r) => a + r.width, 0);
    const text = (el.innerText || '').trim();
    if (/[\/.:]\S*$/.test(text.split(/\s+/).pop() || '') && /\//.test(text)) continue;  // 网址、路径折到下一行不算孤字
    const cjk = /[一-鿿]$/.test(text.replace(/[。，、；：！？」』）)\]]+$/, ''));
    const endsPunct = /[。，、；：！？」』）]$/.test(text);
    if ((cjk && lastW < fs * (endsPunct ? 2.6 : 1.6)) || (!cjk && lastW < fs * 3 && !/\s/.test(text.slice(-12).trim().split(/\s+/).pop() || ' ')))
      issues.push({type: '孤字成行', where: text.slice(-16), detail: `最后一行只剩约 ${Math.round(lastW)}px；用 text-wrap: pretty 或调整断句`});
  }
  // 18：词中断行（V9）：标题、按钮、标签这类短文字里，中文词被拆到两行（「课 / 程」）；正文段落按中文排版习惯可以在字间断行，只查孤字
  if (typeof Intl !== 'undefined' && Intl.Segmenter) {
    const seg = new Intl.Segmenter('zh', {granularity: 'word'});
    const seenW = new Set();
    for (const el of root.querySelectorAll('h1, h2, h3, h4, a, button, dt, th, .row-title, .kicker, .who')) {
      if (!visible(el) || el.closest('svg, [aria-hidden="true"]') || (el.innerText || '').trim().length > 40) continue;
      for (const node of el.childNodes) {
        if (node.nodeType !== 3) continue;
        const t = node.textContent; if (t.length < 2 || !/[一-鿿]{2}/.test(t)) continue;
        const tops = []; const rg = document.createRange();
        for (let i = 0; i < t.length; i++) { rg.setStart(node, i); rg.setEnd(node, i + 1); const r = rg.getClientRects()[0]; tops.push(r ? r.top : null); }
        for (const w of seg.segment(t)) {
          if (!w.isWordLike || w.segment.length < 2 || !/^[一-鿿]+$/.test(w.segment)) continue;
          const a = tops[w.index], b = tops[w.index + w.segment.length - 1];
          if (a !== null && b !== null && Math.abs(b - a) > 4) {
            const key = w.segment + '|' + t.slice(0, 12);
            if (!seenW.has(key)) { seenW.add(key); issues.push({type: '词中断行', where: w.segment, detail: `「${t.slice(Math.max(0, w.index - 6), w.index + w.segment.length + 4)}」里的「${w.segment}」被拆到两行；调整断句、给词加 word-break: keep-all 的包裹，或改宽度`}); }
          }
        }
      }
    }
  }
  // 19：文字冲出所在的圆角容器（胶囊条、卡片），或短标签被挤成三行以上
  for (const el of root.querySelectorAll('span, time, a, button, p, small')) {
    if (!visible(el) || el.closest('svg')) continue;
    const t = (el.innerText || '').trim(); if (!t || el.children.length > 2) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 2 || r.height <= 2 || getComputedStyle(el).clip !== 'auto') continue;  // 只给读屏的隐藏标签
    let box = null;
    for (let e = el.parentElement; e && e !== root; e = e.parentElement) { const cs = getComputedStyle(e); if (parseFloat(cs.borderTopLeftRadius) >= 8 && (parseColor(cs.backgroundColor) || cs.backdropFilter !== 'none')) { box = e; break; } }
    if (box && /auto|scroll|hidden|clip/.test(getComputedStyle(box).overflowX + getComputedStyle(box).overflowY)) box = null;  // 能滚动或有意裁切的容器
    if (box) { const b = box.getBoundingClientRect(); if (r.right > b.right + 2 || r.bottom > b.bottom + 2 || r.left < b.left - 2) issues.push({type: '文字冲出容器', where: t.slice(0, 24), detail: '文字超出所在的圆角条或卡片；给它换一行，或让容器跟着内容长'}); }
    const words = t.split(/\s+/).length;
    if (words <= 3 && t.length <= 24 && !getComputedStyle(el).writingMode.startsWith('vertical') && el.parentElement && getComputedStyle(el.parentElement).display.includes('flex')) {
      const lh = parseFloat(getComputedStyle(el).lineHeight) || parseFloat(getComputedStyle(el).fontSize) * 1.3;
      const tops = []; const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      while (tw.nextNode()) { if (!tw.currentNode.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(tw.currentNode); for (const q of rg.getClientRects()) if (q.width > 1) tops.push(q.top); }
      tops.sort((a, b) => a - b); let n = 0, last = -1e9; for (const tp of tops) if (tp - last > lh * 0.5) { n++; last = tp; }
      if (n >= 3 && getComputedStyle(el).webkitLineClamp === 'none') issues.push({type: '短标签被挤成多行', where: t, detail: `折成 ${n} 行；标签加 white-space: nowrap，放不下就换到下一行`});
    }
  }
  // 10：弹性布局吞掉空格
  for (const el of root.querySelectorAll('*')) {
    if (!visible(el)) continue;
    const dcs = getComputedStyle(el); const d = dcs.display;
    if (!/flex|grid/.test(d) || parseFloat(dcs.columnGap) > 0) continue; // 有 gap 时空格本来就由 gap 代替
    const kids = [...el.childNodes];
    kids.forEach((n, i) => {
      if (n.nodeType !== 3 || !n.textContent.trim()) return;
      const prevEl = kids.slice(0, i).reverse().find(k => k.nodeType === 1 || (k.nodeType === 3 && k.textContent.trim()));
      const nextEl = kids.slice(i + 1).find(k => k.nodeType === 1 || (k.nodeType === 3 && k.textContent.trim()));
      if ((/^\s/.test(n.textContent) && prevEl && prevEl.nodeType === 1) || (/\s$/.test(n.textContent) && nextEl && nextEl.nodeType === 1))
        issues.push({type: '弹性布局吞掉了空格', where: (el.innerText || '').trim().replace(/\s+/g, '').slice(0, 24), detail: '容器是 flex/grid，文字和元素之间的空格不显示；改成 inline-block 或用 gap'});
    });
  }
  // 模板味信号（提示）
  const hints = [];
  const emoji = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B50}\u{2728}]/u;
  for (const el of root.querySelectorAll('*')) {
    if (!visible(el) || el.closest('svg')) continue;
    const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    const cs = getComputedStyle(el);
    if (own && emoji.test(own)) hints.push({sign: 'emoji', where: own.slice(0, 24)});
    if (own && /[!！]/.test(own)) hints.push({sign: '感叹号', where: own.slice(0, 24)});
    if (own && cs.textTransform === 'uppercase' && parseFloat(cs.letterSpacing) > 0.5) hints.push({sign: '全大写加宽字距', where: own.slice(0, 24)});
    if (own && parseInt(cs.fontWeight) >= 800) hints.push({sign: '特粗字重', where: own.slice(0, 24)});
    if (own && cs.fontStyle === 'italic') hints.push({sign: '斜体强调', where: own.slice(0, 24)});
    if (own && parseFloat(cs.fontSize) < 14 && parseFloat(cs.letterSpacing) < 0) hints.push({sign: '小字负字距', where: own.slice(0, 24)});
    if ((cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') && /gradient/.test(cs.backgroundImage)) hints.push({sign: '渐变文字', where: (el.innerText || '').trim().slice(0, 24)});
    if (/(^|,)\s*all\b/.test(cs.transitionProperty) && cs.transitionDuration !== '0s') hints.push({sign: 'transition: all', where: el.tagName.toLowerCase()});
    if ((el.tagName === 'BUTTON' || el.getAttribute('role') === 'button') && /[。.]$/.test((el.innerText || '').trim())) hints.push({sign: '按钮文字带句号', where: (el.innerText || '').trim().slice(0, 24)});
  }
  // 6：定义过的 token
  const defined = [];
  const walk = rules => { for (const r of rules || []) { if (r.style) for (const p of r.style) if (p.startsWith('--')) defined.push(p); try { walk(r.cssRules); } catch (e) {} } };
  for (const ss of document.styleSheets) { try { walk(ss.cssRules); } catch (e) {} }
  for (const el of root.querySelectorAll('[style]')) for (const p of el.style) if (p.startsWith('--')) defined.push(p);
  return {issues, hints, defined: [...new Set(defined)]};
}
"""


def discover_states(src):
    names = sorted(set(re.findall(r'<sc-if value="\{\{\s*(s\d+)\s*\}\}"', src)), key=lambda x: int(x[1:]))
    return names or [None]


def stage_labels(src):
    m = re.search(r'"options":\s*(\[[^\]]*\])', src)
    try:
        return json.loads(m.group(1)) if m else []
    except Exception:
        return []


def prop_variants(src, labels):
    """data-props 里的枚举属性（主题和画板状态的标签除外），每个非默认选项各算一个要查的变体，别的属性保持默认。"""
    m = re.search(r"data-props='([^']*)'", src)
    try:
        props = json.loads(m.group(1)) if m else {}
    except Exception:
        return []
    out = []
    for k, v in props.items():
        if k.startswith('$') or k == 'theme' or not isinstance(v, dict) or v.get('editor') != 'enum':
            continue
        if labels and v.get('options') == labels:
            continue
        out += [(f'{k}={o}', {k: o}) for o in v.get('options', []) if o != v.get('default')]
    return out


def board_meta(path):
    """返回 (宽, 高, 是否文档页)。canvas.json 里带 expand 的画板是说明文档（旅程图之类），不按产品界面查触控尺寸。"""
    cj = os.path.join(os.path.dirname(path), 'canvas.json')
    try:
        b = json.load(open(cj, encoding='utf-8'))['boards'][os.path.basename(path)]
        return int(b['w']), int(b['h']), bool(b.get('expand'))
    except Exception:
        return 390, 844, False


COLOR_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(')


def literal_colors(src):
    body = re.sub(r'<script type="text/x-dc".*?</script>', '', src, flags=re.S)
    body = re.sub(r'<link[^>]+>', '', body)
    hits = []
    for m in COLOR_RE.finditer(body):
        ctx = body[max(0, m.start() - 30):m.end() + 10]
        if 'var(--' in ctx[:30] and ',' in ctx:  # var(--x, #fff) 这样的兜底值
            continue
        if re.search(r'href=|src=|&#', ctx):
            continue
        hits.append(ctx.replace('\n', ' ').strip())
    return hits


INTERACTIVE_TAGS = ('a', 'button', 'input', 'select', 'textarea', 'label', 'summary')


def static_a11y(src):
    """源码里就能看出的「画出来不能用」：<a> 没有 href、非交互元素上挂点击、事件绑定写错。"""
    body = re.sub(r'<script.*?</script>', '', src, flags=re.S)
    out = []
    for m in re.finditer(r'<a\b([^>]*)>', body):
        if 'href=' not in m.group(1):
            text = re.sub(r'<[^>]*>?', '', body[m.end():m.end() + 120]).strip()[:20]
            out.append({'type': '控件不能用键盘到达', 'where': text or '<a>', 'detail': '<a> 没有 href，Tab 到不了；跳转用 <a href>，动作用 <button>'})
    for m in re.finditer(r'<(\w+)\b[^>]*\bonClick=', body, flags=re.I):
        if m.group(1).lower() not in INTERACTIVE_TAGS:
            out.append({'type': '控件不能用键盘到达', 'where': '<' + m.group(1) + '>', 'detail': '点击挂在非交互元素上；改成 <button>'})
    # 交互绑定写错：生成脚本把空值写成 {{ None }}，或 f-string 少了一层括号变成 { x }；点了没反应甚至报错
    for m in re.finditer(r'\bon[A-Z]\w*="(\{\{\s*(?:None|null|undefined)?\s*\}\}|\{(?!\{)[^"]*)"', body):
        out.append({'type': '交互绑定写错', 'where': m.group(0)[:40], 'detail': '事件绑定是空值或只有一层花括号；不跳转的按钮就不要写 onClick'})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--themes', default='light,dark')
    ap.add_argument('--only', default='', help='只查文件名包含这些词的画板，逗号分隔')
    ap.add_argument('--placeholders', default='示例,占位,待定,即将上线,敬请期待,TBD,TODO,Lorem,ipsum,二维码', help='出现在画板文字里就算问题的占位词，逗号分隔')
    ap.add_argument('--blob', action='append', default=[], metavar='ID=PATH',
                    help='画板里 /_blob/<ID> 引用的上传文件在本地的路径（例如共享样式表），可以写多次；不给的话这些样式读不到，会误报 token 没定义和触控过小')
    ap.add_argument('--size', action='append', default=[], metavar='NAME=WxH',
                    help='画板在另一个视口宽度下再查一遍（例如手机画板在 320 宽下），可以写多次；画板要按宽度自适应才有意义')
    a = ap.parse_args()
    extra_sizes = {}
    for m in a.size:
        name, _, wh = m.partition('=')
        try:
            extra_sizes.setdefault(name, []).append(tuple(int(x) for x in wh.lower().split('x')))
        except ValueError:
            sys.exit(f'--size {m}：写成 名称=宽x高，例如 Mobile.dc.html=320x700')

    files = []
    for p in a.paths:
        files += sorted(glob.glob(os.path.join(p, '*.dc.html'))) if os.path.isdir(p) else [p]
    if a.only:
        keys = a.only.split(',')
        files = [f for f in files if any(k in os.path.basename(f) for k in keys)]
    if not files:
        sys.exit('没有找到 .dc.html 画板')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('需要 Python Playwright：pip install playwright && playwright install chromium')

    os.makedirs(a.out, exist_ok=True)
    report, total = [], 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        logic_page = browser.new_page()  # 执行画板的 renderVals()，算出模板里的值
        for f in files:
            src = open(f, encoding='utf-8').read()
            for m in a.blob:
                bid, _, bpath = m.partition('=')
                if not bpath or not os.path.exists(bpath):
                    sys.exit(f'--blob {m}：本地文件不存在')
                src = src.replace('/_blob/' + bid, os.path.relpath(os.path.abspath(bpath), os.path.dirname(os.path.abspath(f))))
            w, h, is_doc = board_meta(f)
            labels = stage_labels(src)
            refs = set(re.findall(r'var\(--([\w-]+)', src))
            # file:// 下读不到外部样式表的规则，直接从链接的 css 文件和内联 <style> 里收集定义
            css_defined = set(re.findall(r'--([\w-]+)\s*:', re.sub(r'<script.*?</script>', '', src, flags=re.S)))
            for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', src):
                cp = os.path.join(os.path.dirname(os.path.abspath(f)), href)
                if not href.startswith(('http', '/')) and os.path.exists(cp):
                    css_defined |= set(re.findall(r'--([\w-]+)\s*:', open(cp, encoding='utf-8').read()))
            board_issues = [{'state': '源码', 'theme': '-', 'type': '写死的颜色', 'where': c, 'detail': ''} for c in literal_colors(src)]
            board_issues += [{'state': '源码', 'theme': '-', **i} for i in static_a11y(src)]
            board_hints = {}
            states = discover_states(src)
            variants = []
            for st in states:
                # 只打开这一个状态，别的状态显式关掉（renderVals() 算出的默认状态不能混进来）
                state = {k: k == st for k in states if k} if st else {}
                label = labels[int(st[1:])] if st and int(st[1:]) < len(labels) else (st or '默认')
                variants.append((label, state, {}, (w, h)))
            first_state = variants[0][1]
            variants += [(lbl, first_state, po, (w, h)) for lbl, po in prop_variants(src, labels if states[0] else [])]
            langs = [po for lbl, po in prop_variants(src, labels if states[0] else []) if 'lang' in po]
            for vw, vh in extra_sizes.get(os.path.basename(f), []):
                variants.append((f'{vw}×{vh}', first_state, {}, (vw, vh)))
                variants += [(f'{vw}×{vh} lang={po["lang"]}', first_state, po, (vw, vh)) for po in langs]  # 窄屏最容易坏在另一种语言上
            for label, state, props_override, (vw, vh) in variants:
                for theme in a.themes.split(','):
                    if theme == 'pseudo' and 'lang' in props_override:
                        continue  # 伪语言模拟「换成更长的语言」，已经切到另一种语言的变体不再叠加
                    html = render_html(src, state, logic_values(src, state, logic_page, props_override))
                    manual_dark = theme == 'dark' and 'data-theme="light"' in html
                    if manual_dark:  # 手动选了深色、系统是浅色：最容易露出浅色 body 的情形
                        html = html.replace('data-theme="light"', 'data-theme="dark"')
                    fd, tmp = tempfile.mkstemp(prefix='.verify_', suffix='.html', dir=os.path.dirname(os.path.abspath(f)))
                    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                        fh.write(html)
                    errors, net = [], []
                    pg = browser.new_page(viewport={'width': vw, 'height': vh}, reduced_motion='reduce',  # pseudo 按浅色查
                                          color_scheme='dark' if theme == 'dark' and not manual_dark else 'light')
                    pg.on('pageerror', lambda e: errors.append(str(e)[:120]))
                    pg.add_init_script('window.__dcHandlesEscape = ' + ('true' if 'Escape' in src else 'false'))
                    pg.on('console', lambda m: (net if 'net::' in m.text or 'Failed to load resource' in m.text else errors).append(m.text[:120]) if m.type == 'error' else None)
                    try:
                        pg.goto('file://' + tmp)
                        pg.wait_for_timeout(250)
                        if theme == 'pseudo':
                            pg.evaluate(PSEUDO_JS)
                            pg.wait_for_timeout(50)
                        res = pg.evaluate(CHECK_JS)
                        if theme == 'light':
                            shown = pg.evaluate('document.body.innerText')
                            for word in a.placeholders.split(','):
                                if word and word in shown:
                                    res['issues'].append({'type': '占位文字', 'where': word, 'detail': '对外页面不放占位符和过程说明'})
                        if theme == 'pseudo':
                            res['issues'] = [i for i in res['issues'] if i['type'] in LAYOUT_TYPES]
                            res['hints'] = []
                    finally:
                        pg.close()
                        os.remove(tmp)
                    for hnt in res.get('hints', []):
                        board_hints.setdefault((hnt['sign'], hnt['where']), set()).add(label)
                    for i in res['issues']:
                        if is_doc and i['type'] in ('触控目标小于 44', '首屏主操作在视口外'):  # 说明文档类画板（组件表、旅程图）没有首屏
                            continue
                        board_issues.append({'state': label, 'theme': theme, **i})
                    if theme == a.themes.split(',')[0]:
                        for name in sorted(refs - {d[2:] for d in res['defined']} - css_defined):
                            board_issues.append({'state': label, 'theme': theme, 'type': '没定义的 token', 'where': '--' + name, 'detail': ''})
                    for e in errors:
                        board_issues.append({'state': label, 'theme': theme, 'type': '页面报错', 'where': e, 'detail': ''})
            # 同一个问题在多个状态里重复出现时合并
            merged = {}
            for i in board_issues:
                k = (i['type'], i['where'], i['detail'])
                m = merged.setdefault(k, {**i, 'states': [], 'themes': []})
                m['states'].append(i['state'])
                if i['theme'] not in m['themes']:
                    m['themes'].append(i['theme'])
            items = list(merged.values())
            for i in items:
                i['theme'] = '、'.join(i['themes'])
            total += len(items)
            report.append((os.path.basename(f), items, board_hints))

        browser.close()

    verdict = 'done' if total == 0 else 'needs_work'
    lines = [f'# 画板验证报告', '', f'**结论：{verdict}**（{total} 个问题，{len(files)} 块画板，主题：{a.themes}）', '',
             '只报会让用户看错、点不到、看不清的问题。审美判断交给评审。', '']
    for name, items, hints in report:
        lines.append(f'## {name}' + ('（通过）' if not items else f'（{len(items)}）'))
        if items:
            lines += ['', '| 类型 | 位置 | 细节 | 主题 | 状态 |', '|---|---|---|---|---|']
            for i in sorted(items, key=lambda x: x['type']):
                st = '、'.join(dict.fromkeys(i['states']))
                lines.append(f"| {i['type']} | {i['where'].replace('|', '/')} | {i['detail']} | {i['theme']} | {st[:80]} |")
        if hints:
            lines += ['', '模板味信号（提示，不影响结论）：' + '；'.join(f'{k[0]}「{k[1]}」' for k in list(hints)[:12])]
        lines.append('')
    out = os.path.join(a.out, 'verify-canvas.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    json.dump({'verdict': verdict, 'boards': {n: it for n, it, _ in report},
               'hints': {n: [{'sign': k[0], 'where': k[1], 'states': sorted(v)} for k, v in h.items()] for n, _, h in report}}, open(os.path.join(a.out, 'verify-canvas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{verdict}: {total} 个问题 → {out}')
    sys.exit(0 if verdict == 'done' else 1)


if __name__ == '__main__':
    main()
