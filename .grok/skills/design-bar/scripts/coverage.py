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
  --data FILE.json    数据字段 → 画板：内容模型（例如研究卡片）里的每个字段，至少要有一块画板把它画出来。
                      「画出来」指画板的模板洞里用到这个字段（{{c.metric}}），或逻辑里按属性读它（c.zh.metric）；
                      只是把数据照抄进画板（"metric": "…"）不算。可以只给 --data、不给 --prd
  --fields a,b        只查这些字段，默认取数据里第一条记录的全部叶子字段（_ 开头的说明字段除外）
  --skip-fields a,b   不需要画出来的字段（例如 id、topic 这类内部字段）
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


def leaf_fields(rec, out=None):
    out = out if out is not None else []
    for k, v in rec.items():
        if k.startswith('_'):
            continue
        if isinstance(v, dict):
            leaf_fields(v, out)
        elif k not in out:
            out.append(k)
    return out


def first_record(data):
    if isinstance(data, list):
        return next((x for x in data if isinstance(x, dict)), None)
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v[0]
        return data
    return None


def data_fields(data_path, fields, skip, boards):
    """返回 (报告行, 没画出来的字段数)。boards：[(文件名, 源码)]，只看 .dc.html 画板。"""
    import json
    rec = first_record(json.load(open(data_path, encoding='utf-8')))
    names = [f for f in (fields.split(',') if fields else leaf_fields(rec or {})) if f and f not in skip.split(',')]
    lines = ['', f'## 数据字段 → 画板（{os.path.basename(data_path)}）', '', '| 字段 | 画出来的画板 |', '|---|---|']
    missing = 0
    for f in names:
        hit = []
        for fn, src in boards:
            body = re.sub(r'<script type="text/x-dc".*?</script>', '', src, flags=re.S)
            logic = ''.join(re.findall(r'<script type="text/x-dc"[^>]*>(.*?)</script>', src, flags=re.S))
            if re.search(r'\{\{[^}]*\b' + re.escape(f) + r'\b[^}]*\}\}', body) or re.search(r'\.' + re.escape(f) + r'\b', logic):
                hit.append(fn)
        missing += not hit
        lines.append(f'| {f} | {"、".join(hit) if hit else "**没有画板画出来**"} |')
    if missing:
        lines += ['', '处理：数据里有、画板上没有的字段，要么画出来（数字卡按「数字 → 结论 → 出处」排），要么写进 --skip-fields 并说明为什么不显示。']
    return lines, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--prd', default='')
    ap.add_argument('--canvas', nargs='+', required=True, help='画板目录或文件（可以包括生成脚本）')
    ap.add_argument('--map', default='')
    ap.add_argument('--id', default=r'F\d+')
    ap.add_argument('--batch', default='')
    ap.add_argument('--scope-section', default='')
    ap.add_argument('--scope-end', default='', help='范围在这段文字处结束（例如「**B2 以后**」）')
    ap.add_argument('--exclude', default='')
    ap.add_argument('--out', default='', help='报告目录（写 coverage.md）或文件')
    ap.add_argument('--data', default='')
    ap.add_argument('--fields', default='')
    ap.add_argument('--skip-fields', default='')
    a = ap.parse_args()
    if not a.prd and not a.data:
        ap.error('至少给 --prd 或 --data')

    prd = open(a.prd, encoding='utf-8').read() if a.prd else ''
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

    text, boards = '', []
    for p in a.canvas:
        files = [p] if os.path.isfile(p) else [x for x in glob.glob(os.path.join(p, '**', '*'), recursive=True)
                                               if x.endswith(('.html', '.py', '.json', '.jsx', '.js', '.md'))]
        for f in files:
            try:
                body = open(f, encoding='utf-8').read()
                text += body + '\n'
                if f.endswith('.dc.html'):
                    boards.append((os.path.basename(f), body))
            except Exception:
                pass
    mentioned = set(re.findall(r'\b(' + a.id + r')\b', text))
    mapped, no_ui = {}, {}
    if a.map and os.path.exists(a.map):
        for m in re.finditer(r'^\| (' + a.id + r') \| ([^|]*)\|([^|]*)\|', open(a.map, encoding='utf-8').read(), re.M):
            where, note = m.group(2).strip(), m.group(3).strip()
            (no_ui if where in ('—', '-', '') else mapped)[m.group(1)] = note if where in ('—', '-', '') else where

    missing = [f for f in scope if f not in mentioned and f not in mapped and f not in no_ui]
    lines = ['# 需求覆盖检查', '']
    if a.prd:
        lines += [f'范围：{len(scope)} 个功能；画板里提到 {len([f for f in scope if f in mentioned])}，覆盖表映射 {len([f for f in scope if f in mapped])}，'
                  f'写明无界面 {len([f for f in scope if f in no_ui])}；**没有着落 {len(missing)}**', '']
    if missing:
        lines += ['| 功能 | 名称 | 批次 |', '|---|---|---|']
        for f in missing:
            n, b = rows.get(f, ('（PRD 功能表里没找到）', ''))
            lines.append(f'| {f} | {n[:30]} | {b[:30]} |')
        lines += ['', '处理：画进画板（并在画板或生成脚本里写上编号），或在覆盖表里写一行「无界面：理由」。']
    data_missing = 0
    if a.data:
        more, data_missing = data_fields(a.data, a.fields, a.skip_fields, boards)
        lines += more
    out = '\n'.join(lines)
    if a.out:
        # 和 verify_canvas.py 一样可以给报告目录；给文件名时就写那个文件
        path = os.path.join(a.out, 'coverage.md') if os.path.isdir(a.out) or a.out.endswith('/') else a.out
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        open(path, 'w', encoding='utf-8').write(out)
    print(out)
    sys.exit(0 if not missing and not data_missing else 1)


if __name__ == '__main__':
    main()
