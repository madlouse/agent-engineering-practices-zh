#!/usr/bin/env python3
"""需求覆盖检查：PRD 里每个要做的功能，要么在画板里有对应的场景，要么写明「没有界面」及理由。

为什么要有它：需求一直在加，画板跟不上时没人会发现，直到评审才看到一串缺口。
这个脚本把「哪些功能还没画」变成每次交付都能跑的一张清单。

怎么判断「画过了」（满足任一条）：
  1. 画板文件或生成脚本里出现了功能编号（如 F141）；
  2. 覆盖表（默认 <设计目录>/coverage.md）里有这一行：`| F141 | AI-Hello · 同意 | 备注 |`；
  3. 覆盖表里写明没有界面：`| F43 | — | 无界面：实验框架 |`。

用法：
  python coverage.py --prd docs/product/PRD.md --canvas tools/design-canvas \\
      --map docs/design/coverage.md --batch 'B1' [--scope-section '### 9.2'] [--out 报告.md]
选项：
  --id REGEX          功能编号的样子，默认 F\\d+
  --batch REGEX       只看「批次」这一列匹配的功能（PRD 功能表的倒数第一列），例如 'B1'
  --scope-section T   改用 PRD 里某一节（例如 B1 范围表）列出的编号作为要检查的范围
  --scope-end T       范围在这段文字处结束（和 --scope-section 一起用）
  --exclude REGEX     不检查批次列匹配的（例如 '取消|已上线'）
结论：全部覆盖时退出码 0，否则 1。
"""
import argparse
import glob
import os
import re
import sys


def feature_rows(prd, idre):
    rows = {}
    for m in re.finditer(r'^\| (~~)?(' + idre + r')(~~)? \| ([^|]+)\|(.*)$', prd, re.M):
        if m.group(1):  # 划掉的功能
            continue
        cells = [c.strip() for c in m.group(5).split('|')]
        batch = cells[-2] if len(cells) >= 2 else ''
        rows.setdefault(m.group(2), (m.group(4).strip(), batch))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--prd', required=True)
    ap.add_argument('--canvas', nargs='+', required=True, help='画板目录或文件（可以包括生成脚本）')
    ap.add_argument('--map', default='')
    ap.add_argument('--id', default=r'F\d+')
    ap.add_argument('--batch', default='')
    ap.add_argument('--scope-section', default='')
    ap.add_argument('--scope-end', default='', help='范围在这段文字处结束（例如「**B2 以后**」）')
    ap.add_argument('--exclude', default='')
    ap.add_argument('--out', default='', help='报告目录（写 coverage.md）或文件')
    a = ap.parse_args()

    prd = open(a.prd, encoding='utf-8').read()
    rows = feature_rows(prd, a.id)
    if a.scope_section:
        i = prd.index(a.scope_section)
        j = prd.find('\n## ', i + 1)
        k = prd.find('\n### ', i + 1)
        end = min(x for x in (j, k, len(prd)) if x > 0)
        if a.scope_end and a.scope_end in prd[i:end]:
            end = prd.index(a.scope_end, i)
        scope = list(dict.fromkeys(re.findall(a.id, prd[i:end])))
    else:
        scope = [f for f, (_, b) in rows.items() if not a.batch or re.search(a.batch, b)]
    if a.exclude:
        scope = [f for f in scope if not re.search(a.exclude, rows.get(f, ('', ''))[1])]

    text = ''
    for p in a.canvas:
        files = [p] if os.path.isfile(p) else [x for x in glob.glob(os.path.join(p, '**', '*'), recursive=True)
                                               if x.endswith(('.html', '.py', '.json', '.jsx', '.js', '.md'))]
        for f in files:
            try:
                text += open(f, encoding='utf-8').read() + '\n'
            except Exception:
                pass
    mentioned = set(re.findall(r'\b(' + a.id + r')\b', text))
    mapped, no_ui = {}, {}
    if a.map and os.path.exists(a.map):
        for m in re.finditer(r'^\| (' + a.id + r') \| ([^|]*)\|([^|]*)\|', open(a.map, encoding='utf-8').read(), re.M):
            where, note = m.group(2).strip(), m.group(3).strip()
            (no_ui if where in ('—', '-', '') else mapped)[m.group(1)] = note if where in ('—', '-', '') else where

    missing = [f for f in scope if f not in mentioned and f not in mapped and f not in no_ui]
    lines = ['# 需求覆盖检查', '',
             f'范围：{len(scope)} 个功能；画板里提到 {len([f for f in scope if f in mentioned])}，覆盖表映射 {len([f for f in scope if f in mapped])}，'
             f'写明无界面 {len([f for f in scope if f in no_ui])}；**没有着落 {len(missing)}**', '']
    if missing:
        lines += ['| 功能 | 名称 | 批次 |', '|---|---|---|']
        for f in missing:
            n, b = rows.get(f, ('（PRD 功能表里没找到）', ''))
            lines.append(f'| {f} | {n[:30]} | {b[:30]} |')
        lines += ['', '处理：画进画板（并在画板或生成脚本里写上编号），或在覆盖表里写一行「无界面：理由」。']
    out = '\n'.join(lines)
    if a.out:
        # 和 verify_canvas.py 一样可以给报告目录；给文件名时就写那个文件
        path = os.path.join(a.out, 'coverage.md') if os.path.isdir(a.out) or a.out.endswith('/') else a.out
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        open(path, 'w', encoding='utf-8').write(out)
    print(out)
    sys.exit(0 if not missing else 1)


if __name__ == '__main__':
    main()
