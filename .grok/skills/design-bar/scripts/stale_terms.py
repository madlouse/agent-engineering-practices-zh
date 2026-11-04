#!/usr/bin/env python3
"""过时口径扫描：一个决定改了说法以后，找出文档、画板、代码里还在用旧说法的地方。

为什么要有它：决定改了，旧说法会散落在 PRD 的验收、工作手册、架构、设计系统、画板文案里，
一处一处靠记忆找一定会漏。把「废弃说法 → 现在的说法」记在词汇表里，每次交付前扫一遍。

词汇表（默认 <设计目录>/glossary.md）里的表格，每行一条：
  | 废弃说法 | 现在的说法 | 依据 |
  | 灰色预置问题 | 预置问题（输入框上方一行） | PRD J77 |
「废弃说法」可以是普通文字，也可以写成 /正则/。

不算问题的行：被划掉的（~~）、决策记录和修订历史里的（用 --skip-line 指定，默认跳过以「| J」「| D」「| 1x/xx」开头的表格行和含「原为」「取代」「废弃」「已改」的行）。

用法：
  python stale_terms.py --glossary docs/design/glossary.md docs src tools/design-canvas/gen_ai.py \\
      [--exclude 'archive/|reviews/'] [--out 报告.md]
结论：没有命中时退出码 0，否则 1。
"""
import argparse
import os
import re
import sys

DEFAULT_SKIP = r'~~|^\| ?[JD]\d+ |^\| \d{1,2}/\d{2} |原为|取代|废弃|已改|改为|旧说法|history|修订记录'
EXTS = ('.md', '.py', '.html', '.tsx', '.ts', '.jsx', '.js', '.json', '.css')


def load_glossary(path):
    rules = []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|', line)
        if not m or m.group(1) in ('废弃说法', '---') or set(m.group(1)) <= set('-: '):
            continue
        old = m.group(1)
        pat = re.compile(old[1:-1]) if len(old) > 2 and old.startswith('/') and old.endswith('/') else re.compile(re.escape(old))
        rules.append((old, m.group(2), m.group(3), pat))
    return rules


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--glossary', required=True)
    ap.add_argument('--exclude', default=r'archive/|/reviews/|decisions\.md|CHANGELOG|node_modules/|\.git/')
    ap.add_argument('--skip-line', default=DEFAULT_SKIP)
    ap.add_argument('--out', default='', help='报告目录（写 stale-terms.md）或文件')
    a = ap.parse_args()

    rules = load_glossary(a.glossary)
    gl = os.path.abspath(a.glossary)
    skip = re.compile(a.skip_line)
    excl = re.compile(a.exclude) if a.exclude else None
    files = []
    for p in a.paths:
        if os.path.isfile(p):
            files.append(p)
        else:
            for d, _, fs in os.walk(p):
                files += [os.path.join(d, f) for f in fs if f.endswith(EXTS)]
    hits = []
    for f in files:
        if os.path.abspath(f) == gl or (excl and excl.search(f.replace(os.sep, '/'))):
            continue
        try:
            lines = open(f, encoding='utf-8').read().split('\n')
        except Exception:
            continue
        for n, line in enumerate(lines, 1):
            if skip.search(line):
                continue
            for old, new, why, pat in rules:
                if pat.search(line):
                    hits.append((f, n, old, new, why, line.strip()[:80]))
    out = ['# 过时口径扫描', '', f'{len(rules)} 条词汇，{len(files)} 个文件；**命中 {len(hits)} 处**', '']
    if hits:
        out += ['| 文件:行 | 旧说法 | 现在的说法 | 依据 | 原文 |', '|---|---|---|---|---|']
        out += [f'| {f}:{n} | {o} | {nw} | {w} | {t.replace("|", "/")} |' for f, n, o, nw, w, t in hits]
    text = '\n'.join(out)
    if a.out:
        # 和 verify_canvas.py 一样可以给报告目录；给文件名时就写那个文件
        path = os.path.join(a.out, 'stale-terms.md') if os.path.isdir(a.out) or a.out.endswith('/') else a.out
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        open(path, 'w', encoding='utf-8').write(text)
    print(text)
    sys.exit(0 if not hits else 1)


if __name__ == '__main__':
    main()
