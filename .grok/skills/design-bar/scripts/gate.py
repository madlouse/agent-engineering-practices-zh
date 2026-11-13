#!/usr/bin/env python3
"""「体验与美学」出口门槛：定稿前检查记分卡（<设计目录>/scorecard.md）齐不齐、够不够。

查四件事（口径见 references/award-bar.md 第 3 节）：
  1. 六维评分：六个维度都有档位（弱 / 中 / 强），都不低于「中」，每维都写了证据；评审人写了。
  2. 参照作品：至少两个，每个写了借什么、有并排截图。「未做」「无」「—」这类占位按没填算。
  3. 交付物：动效原型、核心旅程操作视频、无障碍实测报告都填了；写本地路径的要真的存在。
  4. 步数实测：至少一条核心旅程；每条的点按次数（不计意图步）不超过预算（核心 2、非核心 3；级别写「建档」的一次性旅程 10），测法是原型实测或真机实测，不是数画板。
证据属不属实它判不了，由独立评审核。

用法：
  python gate.py docs/design/scorecard.md [--out 报告目录] [--root 项目根目录] [--core 2] [--other 3] [--onboard 10]
结论：都过退出码 0；有不过退出码 1；记分卡读不了退出码 2。
"""
import argparse
import os
import re
import sys

DIMENSIONS = ('Delight', 'Inclusivity', 'Innovation', 'Interaction', 'Social Impact', 'Visuals')
GRADES = {'弱': 0, '中': 1, '强': 2}
DELIVERABLES = ('动效原型：签名时刻', '动效原型：入口第一屏', '操作视频', '无障碍实测报告')
MEASURED = re.compile(r'(原型|真机)实测')


def tables(text):
    """按「## 标题」分节，返回 {标题: [行的单元格列表]}，跳过表头和分隔行。"""
    out, title, header_seen = {}, '', False
    for line in text.split('\n'):
        if line.startswith('## '):
            title, header_seen = line[3:].strip(), False
            out.setdefault(title, [])
            continue
        if not line.lstrip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in cells):
            continue
        if not header_seen:
            header_seen = True
            continue
        out.setdefault(title, []).append(cells)
    return out


def section(tabs, keyword):
    for title, rows in tabs.items():
        if keyword in title:
            return rows
    return None


def field(text, name):
    m = re.search(rf'^{name}[：:][ \t]*(.*)$', text, re.M)
    return m.group(1).strip() if m else ''


PLACEHOLDER = re.compile(r'^\s*(未做|没做|未填|待补|待定|无|没有|暂无|n/?a|tbd|todo|[-—–]+)(\s|[:：（(，,。]|$)', re.I)


def filled(value):
    """填了真东西：非空，也不是「未做」「无」「—」这类占位。"""
    return bool(value) and not PLACEHOLDER.match(value)


def is_local(ref):
    return ref and not re.match(r'^[a-z][a-z0-9+.-]*://', ref, re.I)


def check(path, root, core_budget, other_budget, onboard_budget=10):
    text = open(path, encoding='utf-8').read()
    tabs = tables(text)
    base = os.path.dirname(os.path.abspath(path))
    fails, passes = [], []

    reviewer = field(text, '评审人')
    if not reviewer or reviewer.startswith('（'):
        fails.append(('评审', '没写评审人：要一个没看过制作过程的独立评审'))
    elif re.search(r'自评|制作者', reviewer):
        fails.append(('评审', f'评审人是「{reviewer}」：自评不算'))
    else:
        passes.append(('评审', reviewer))

    rows = section(tabs, '六维') or []
    for dim in DIMENSIONS:
        row = next((r for r in rows if dim.lower() in r[0].lower()), None)
        if not row:
            fails.append(('六维评分', f'缺「{dim}」这一维'))
            continue
        grade = row[1] if len(row) > 1 else ''
        evidence = row[2] if len(row) > 2 else ''
        if grade not in GRADES:
            fails.append(('六维评分', f'{row[0]}：档位要写弱、中或强，现在是「{grade or "空"}」'))
        elif GRADES[grade] < GRADES['中']:
            fails.append(('六维评分', f'{row[0]}：{grade}，门槛是不低于中'))
        elif not filled(evidence):
            fails.append(('六维评分', f'{row[0]}：{grade}，但没写证据；没有证据按不满足算'))
        else:
            passes.append(('六维评分', f'{row[0]}：{grade}'))

    refs = [r for r in (section(tabs, '参照') or []) if r and r[0]]
    good_refs = [r for r in refs if len(r) >= 4 and filled(r[2]) and filled(r[3])]
    if len(good_refs) < 2:
        fails.append(('参照作品', f'写全了「借什么」和「并排截图」的参照只有 {len(good_refs)} 个，至少要 2 个'))
    else:
        passes.append(('参照作品', '、'.join(r[0] for r in good_refs)))

    drows = section(tabs, '交付物') or []
    for name in DELIVERABLES:
        hits = [r for r in drows if name in re.sub(r'\s*[:：]\s*', '：', r[0])]
        if not hits:
            fails.append(('交付物', f'缺「{name}」这一行'))
            continue
        for r in hits:
            ref = r[1] if len(r) > 1 else ''
            if not filled(ref):
                fails.append(('交付物', f'{r[0]}：没填位置（现在是「{ref or "空"}」）'))
            elif is_local(ref) and not any(os.path.exists(os.path.join(b, ref)) for b in (base, root)):
                fails.append(('交付物', f'{r[0]}：找不到 {ref}'))
            else:
                passes.append(('交付物', f'{r[0]}：{ref}'))

    jrows = [r for r in (section(tabs, '步数') or []) if r and r[0]]
    if not any(len(r) > 1 and '核心' in r[1] and '非核心' not in r[1] for r in jrows):
        fails.append(('步数实测', '没有一条核心旅程'))
    for r in jrows:
        name, tier = r[0], (r[1] if len(r) > 1 else '')
        taps = r[2] if len(r) > 2 else ''
        how = r[5] if len(r) > 5 else ''
        budget = other_budget if '非核心' in tier else core_budget if '核心' in tier else onboard_budget if '建档' in tier else None
        if budget is None:
            fails.append(('步数实测', f'{name}：级别要写核心、非核心或建档'))
            continue
        if not re.fullmatch(r'\d+', taps):
            fails.append(('步数实测', f'{name}：点按次数要写一个整数，现在是「{taps or "空"}」'))
            continue
        if not MEASURED.search(how):
            fails.append(('步数实测', f'{name}：测法是「{how or "空"}」，要在可点原型或真机上实测，数画板不算'))
        elif int(taps) > budget:
            fails.append(('步数实测', f'{name}：{taps} 步，{tier}预算是 {budget} 步（意图步不计）'))
        else:
            passes.append(('步数实测', f'{name}：{taps} 步（{tier}，{how}）'))
    return fails, passes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scorecard')
    ap.add_argument('--out', default='', help='报告目录（写 gate.md）')
    ap.add_argument('--root', default='.', help='交付物写相对路径时，也在这个目录下找')
    ap.add_argument('--core', type=int, default=2, help='核心旅程的步数预算')
    ap.add_argument('--other', type=int, default=3, help='非核心旅程的步数预算')
    ap.add_argument('--onboard', type=int, default=10, help='建档（一次性）旅程的步数预算')
    a = ap.parse_args()
    try:
        fails, passes = check(a.scorecard, os.path.abspath(a.root), a.core, a.other, a.onboard)
    except OSError as e:
        print(f'读不了记分卡：{e}', file=sys.stderr)
        sys.exit(2)
    out = ['# 体验与美学出口门槛', '', f'记分卡：{a.scorecard}；步数预算：核心 {a.core}、非核心 {a.other}、建档 {a.onboard}（意图步不计）', '',
           f'**结论：{"过" if not fails else "不过"}**（不过 {len(fails)} 项，过 {len(passes)} 项）', '']
    if fails:
        out += ['## 不过', '', '| 项 | 问题 |', '|---|---|'] + [f'| {k} | {v} |' for k, v in fails] + ['']
    if passes:
        out += ['## 过', '', '| 项 | 内容 |', '|---|---|'] + [f'| {k} | {v} |' for k, v in passes] + ['']
    out += ['证据属不属实由独立评审核，这里只查齐不齐、够不够。口径见 design-bar `references/award-bar.md`。']
    text = '\n'.join(out)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        open(os.path.join(a.out, 'gate.md'), 'w', encoding='utf-8').write(text + '\n')
    print(text)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
