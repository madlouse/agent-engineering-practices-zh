#!/usr/bin/env python3
"""类名审计：共享样式表和各画板 <helmet> 里的类，对照全部画板里用到的类。
用法：audit_classes.py <canvas.css> <project 目录> [--strict]
查五件事：
  1. 共享样式表里同一条规则的选择器（整条，同一个 @media / @container 条件下）写了两遍。「.a, .b { } 再加 .a { }」这种合写不算；
  2. 某块画板的 <helmet> 重写共享的类（选择器里没有一个这一页自己的类）；
  3. <helmet> 里自己的类不带 vc- 前缀，或定义了但这一页没用到；
  4. 画板用了、样式表和 <helmet> 里都没有的类；
  5. 共享样式表里定义、哪块画板都没用到的类。
--strict：有任何一项就退出码 1。
画板里「用到」的类 = class 属性里的词 + 脚本的字符串里形如 vc-xxx、is-xxx、lg-xxx 的词；字符串以「-」结尾再拼变量的（'vc-claim-chip-' + id），按前缀算。"""
import re, sys
from pathlib import Path

# 由脚本在运行时加上、标记里看不到的类：canvas.js 的液态玻璃状态；画板上静态展示状态用的 is-*（verify_canvas.py 也会加）
RUNTIME = {'lg-dark', 'lg-light', 'lg-on-dark', 'is-hover', 'is-press', 'is-focus'}

def rules(css):
    """[(条件, 选择器, 整条规则的选择器)]，条件是外层 @media / @container / @supports 的文字。"""
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, stack, buf, i = [], [], '', 0
    for ch in css:
        if ch == '{':
            head = buf.strip(); buf = ''
            if head.startswith('@') and not head.startswith(('@property', '@font-face')):
                stack.append(head)
            else:
                stack.append(None)
                if not head.startswith('@'):
                    for sel in split_selectors(head): out.append((' '.join(s for s in stack if s), sel, ', '.join(split_selectors(head))))
        elif ch == '}':
            buf = ''
            if stack: stack.pop()
        elif ch == ';' and (not stack or stack[-1] is None):
            buf = ''
        else:
            buf += ch
    return out

def split_selectors(head):
    parts, depth, cur = [], 0, ''
    for ch in head:
        if ch == '(': depth += 1
        if ch == ')': depth -= 1
        if ch == ',' and depth == 0: parts.append(cur.strip()); cur = ''
        else: cur += ch
    parts.append(cur.strip())
    return [re.sub(r'\s+', ' ', p) for p in parts if p]

classes = lambda sel: set(re.findall(r'\.(-?[A-Za-z_][\w-]*)', re.sub(r'"[^"]*"|\'[^\']*\'', '', sel)))

def used(html):
    out, prefixes = set(), set()
    for m in re.finditer(r'class="([^"]*)"', html):
        for tok in m.group(1).split():
            if '{' not in tok and '}' not in tok: out.add(tok)
    script = ''.join(re.findall(r'<script type="text/x-dc".*?</script>', html, re.S))
    for lit in re.findall(r"'([^'\n]*)'|\"([^\"\n]*)\"|`([^`]*)`", script):
        for tok in re.split(r"[\s.+'\",>()\[\]#:]+", ''.join(lit)):
            if re.fullmatch(r'(vc|is|lg)-[a-z0-9-]*[a-z0-9]', tok): out.add(tok)
            elif re.fullmatch(r'(vc|is|lg)-[a-z0-9-]*-', tok): prefixes.add(tok)
    return out, prefixes

def main():
    css_path, proj = Path(sys.argv[1]), Path(sys.argv[2])
    shared_rules = rules(css_path.read_text(encoding='utf-8'))
    shared = set().union(*(classes(s) for _, s, _ in shared_rules))
    problems = 0
    seen = {}
    prev = None
    for cond, sel, head in shared_rules:
        if (cond, head) == prev and sel != head.split(', ')[0]: continue   # 同一条规则的后几个选择器
        if sel == head.split(', ')[0]: seen[(cond, head)] = seen.get((cond, head), 0) + 1
        prev = (cond, head)
    dups = sorted(f'{sel}' + (f'（{cond}）' if cond else '') for (cond, sel), n in seen.items() if n > 1 and sel != ':root')   # :root 的变量分三处：生成的、手写的、玻璃模板的
    if dups: problems += 1; print(f'[共享样式表里写了两遍]（{len(dups)}）：' + '；'.join(dups))
    all_used, all_prefixes = set(), set()
    for f in sorted(proj.glob('*.dc.html')):
        html = f.read_text(encoding='utf-8')
        helmet = ''.join(re.findall(r'<helmet>(.*?)</helmet>', html, re.S))
        local_rules = rules(''.join(re.findall(r'<style>(.*?)</style>', helmet, re.S)))
        local_all = set().union(set(), *(classes(s) for _, s, _ in local_rules))
        own = local_all - shared
        u, pre = used(html)
        all_used |= u; all_prefixes |= pre
        rewrites = sorted({s for _, s, _ in local_rules if classes(s) and not (classes(s) & own)})
        noprefix = sorted(c for c in own if not c.startswith('vc-'))
        unused_own = sorted(c for c in own if c not in u and not any(c.startswith(p) for p in pre))
        undef = sorted(c for c in u if c not in shared and c not in own)
        if rewrites: problems += 1; print(f'[重写共享的类] {f.name}：' + '；'.join(rewrites))
        if noprefix: problems += 1; print(f'[没有 vc- 前缀] {f.name}：' + ', '.join(noprefix))
        if unused_own: problems += 1; print(f'[本页定义了没用到] {f.name}：' + ', '.join(unused_own))
        if undef: problems += 1; print(f'[没有定义] {f.name}：' + ', '.join(undef))
        print(f'  {f.name}：<helmet> 里自己的类 {len(own)} 个' + ('：' + ', '.join(sorted(own)) if own else ''))
    unused = sorted(c for c in shared if c not in all_used and c not in RUNTIME and not any(c.startswith(p) for p in all_prefixes))
    if unused: problems += 1; print(f'[没有用到] 共享样式表里定义、哪块画板都没用到（{len(unused)}）：' + ', '.join(unused))
    print(f'共享样式表 {len(shared)} 个类、{len(shared_rules)} 条选择器；画板共用到 {len(all_used)} 个类；问题 {problems} 组')
    if '--strict' in sys.argv and problems: sys.exit(1)

main()
