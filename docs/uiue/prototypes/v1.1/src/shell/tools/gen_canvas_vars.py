#!/usr/bin/env python3
"""把设计系统 tokens.json 生成 canvas.css 里「@tokens:start … @tokens:end」之间的变量部分。

  python3 gen_canvas_vars.py <tokens.json> <canvas.css>           # 原地重写变量部分，手写的类不动
  python3 gen_canvas_vars.py <tokens.json> <canvas.css> --check   # 只比较，不一致时退出码 1

和 design-bar 的 sync_tokens.py 的区别：画布的主题写在页面里层的 data-theme 上，所以深色块多一组 :has() 选择器；
字号另按「X-phone」「X-tablet」样式生成两档媒体查询里的覆盖（X 和 X-serif 一起改）。变量名和 token 名一致：
颜色 --vc-*，其余族 --<token 名>，文字样式 --type-<名>、--leading-<名>、--weight-<名>、--tracking-<名>，字体 --font-<键>。
"""
import json, re, sys

START, END = '/* @tokens:start */', '/* @tokens:end */'
SKIP = ('name', 'version', 'color', 'type', 'meta')

def build(t):
    themes = [x['id'] for x in t['color']['themes']]
    first = themes[0]
    root, dark = [], []
    for tok in t['color']['tokens']:
        v = tok['value']
        root.append(f"  --{tok['name']}:{v[first]};")
        if v.get('dark') != v[first]:
            dark.append(f"  --{tok['name']}:{v['dark']};")
    for fam, body in t.items():
        if fam in SKIP or not isinstance(body, dict):
            continue
        for tok in body.get('tokens', []):
            v = tok['value']
            if isinstance(v, dict):
                root.append(f"  --{tok['name']}:{v[first]};")
                if v.get('dark') != v[first]:
                    dark.append(f"  --{tok['name']}:{v['dark']};")
            else:
                root.append(f"  --{tok['name']}:{v};")
    for key, stack in t['type']['families'].items():
        root.append(f"  --font-{key}:{stack};")
    styles = [s for g in t['type']['groups'] for s in g['styles']]
    names = {s['name'] for s in styles}
    over = {'phone': [], 'tablet': []}
    for s in styles:
        m = re.match(r'(.+)-(phone|tablet)$', s['name'])
        if m:
            for base in (m.group(1), m.group(1) + '-serif'):
                if base in names:
                    over[m.group(2)].append(f"  --type-{base}:{s['fontSize']};")
                    if 'lineHeight' in s:
                        over[m.group(2)].append(f"  --leading-{base}:{s['lineHeight']};")
            continue
        root.append(f"  --type-{s['name']}:{s['fontSize']};")
        if 'lineHeight' in s: root.append(f"  --leading-{s['name']}:{s['lineHeight']};")
        if 'fontWeight' in s: root.append(f"  --weight-{s['name']}:{s['fontWeight']};")
        root.append(f"  --tracking-{s['name']}:{s.get('letterSpacing', '0')};")
    size = {x['name']: x['value'] for x in t['size']['tokens']}
    bt, bd = int(size['breakpoint-tablet'][:-2]), int(size['breakpoint-desktop'][:-2])
    rel = t.get('meta', {}).get('release', '')
    out = [START,
           f"/* 由 tokens.json 生成（{rel}），不要手改这一段；改 token 后重新生成。 */",
           ':root {', '  color-scheme: light dark;', *root, '}',
           f"/* 平板档 {bt}–{bd - 1}px（breakpoint-tablet、breakpoint-desktop） */",
           f"@media (min-width: {bt}px) and (max-width: {bd - 1}px) {{ :root {{", *over['tablet'], '} }',
           f"/* 手机档 < {bt}px（breakpoint-tablet） */",
           f"@media (max-width: {bt - 1}px) {{ :root {{", *over['phone'], '} }',
           '/* 主题写在页面里层的 data-theme 上时，:root 也跟着换（:has），body 的背景才不会露出另一套颜色 */',
           '@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]):not(:has([data-theme="light"])) {', *dark, '} }',
           ':root[data-theme="dark"], :root:has([data-theme="dark"]), [data-theme="dark"] {', *dark, '}',
           END]
    return '\n'.join(out)

def main():
    tokens, css = sys.argv[1], sys.argv[2]
    block = build(json.load(open(tokens, encoding='utf-8')))
    src = open(css, encoding='utf-8').read()
    i, j = src.find(START), src.find(END)
    if i < 0 or j < 0:
        sys.exit('canvas.css 里没有 @tokens:start / @tokens:end 标记')
    new = src[:i] + block + src[j + len(END):]
    if '--check' in sys.argv:
        if new != src:
            sys.exit('canvas.css 的变量部分和 tokens.json 不一致：重新生成')
        print('一致')
        return
    open(css, 'w', encoding='utf-8').write(new)
    print('已生成', len(block.splitlines()), '行')

if __name__ == '__main__':
    main()
