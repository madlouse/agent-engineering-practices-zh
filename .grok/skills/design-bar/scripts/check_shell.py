#!/usr/bin/env python3
"""外壳检查：主题跟随系统、偏好记忆、产品家族的导航约定。读源码文本，不渲染。

约定写在 <设计目录>/shell.json（格式见 references/family.md 第 3 节）。没有配置时只查主题跟随系统。

查什么：
  主题跟随系统   源码里有深色主题（data-theme 的 dark、.dark、color-scheme: dark），却没有 prefers-color-scheme
  根元素写死主题 <html data-theme="light|dark">、documentElement 上把主题无条件设成 light 或 dark；
                 theme.fixedAllow 里列出的特例路径（正则）不算
  偏好记忆       theme.storageKey、family.langKey 和它们的取值在源码里都出现
  家族导航       family.home 有一个链到它的链接；family.links 每个地址都出现；有 aria-current
它判不了运行时的行为（例如读了存储键却没生效），上线前照 references/family.md 第 4 节点一遍。

用法：
  python check_shell.py src [更多源码目录] [--config docs/design/shell.json] [--out 报告目录]
结论：都过退出码 0，有不过退出码 1，配置写错退出码 2。
"""
import argparse
import json
import os
import re
import sys

EXTS = ('.css', '.scss', '.html', '.tsx', '.ts', '.jsx', '.js', '.mjs', '.vue', '.svelte', '.astro')
SKIP_DIRS = re.compile(r'(^|/)(node_modules|\.next|dist|build|out|coverage|\.git)(/|$)')
DARK = re.compile(r'''data-theme\s*=\s*["'`]?dark|\[data-theme=["']?dark|\.dark\b|color-scheme:\s*dark''')
FOLLOWS = re.compile(r'prefers-color-scheme')
FORCED = [
    re.compile(r'''<html\b[^>]*\bdata-theme\s*=\s*["'](light|dark)["']'''),
    re.compile(r'''documentElement\.dataset\.theme\s*=\s*["'](light|dark)["']'''),
    re.compile(r'''documentElement\.setAttribute\(\s*["']data-theme["']\s*,\s*["'](light|dark)["']'''),
    re.compile(r'''documentElement\.classList\.add\(\s*["'](light|dark)["']'''),
]


def load_sources(paths):
    files = []
    for p in paths:
        if os.path.isfile(p):
            files.append(p)
            continue
        for d, dirs, fs in os.walk(p):
            dirs[:] = [x for x in dirs if not SKIP_DIRS.search(os.path.join(d, x).replace(os.sep, '/'))]
            files += [os.path.join(d, f) for f in fs if f.endswith(EXTS)]
    out = {}
    for f in files:
        try:
            out[f.replace(os.sep, '/')] = open(f, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
    return out


def quoted(value):
    return re.compile(r'''["'`]''' + re.escape(value) + r'''["'`]''')


def where(srcs, pat, limit=3):
    hits = []
    for f, text in srcs.items():
        for n, line in enumerate(text.split('\n'), 1):
            if pat.search(line):
                hits.append(f'{f}:{n}')
                if len(hits) >= limit:
                    return hits
    return hits


def check(srcs, cfg):
    fails, passes = [], []
    theme = (cfg or {}).get('theme') or {}
    family = (cfg or {}).get('family')
    allow = [re.compile(x) for x in theme.get('fixedAllow') or []]

    dark = where(srcs, DARK, 1)
    follows = where(srcs, FOLLOWS, 1)
    if dark and not follows:
        fails.append(('主题跟随系统', f'有深色主题（{dark[0]}），源码里却没有 prefers-color-scheme：默认要跟随系统'))
    elif dark:
        passes.append(('主题跟随系统', follows[0]))
    else:
        passes.append(('主题跟随系统', '没有深色主题，不适用'))

    forced = []
    for f, text in srcs.items():
        if any(a.search(f) for a in allow):
            continue
        for n, line in enumerate(text.split('\n'), 1):
            if any(p.search(line) for p in FORCED):
                forced.append(f'{f}:{n}')
    if forced:
        fails.append(('根元素写死主题', '、'.join(forced[:5]) + '（特例屏写进 shell.json 的 theme.fixedAllow）'))
    else:
        passes.append(('根元素写死主题', '没有'))

    def remembered(label, key, values):
        if not key:
            return
        if not where(srcs, quoted(key), 1):
            fails.append((label, f'存储键 {key} 在源码里没出现'))
            return
        missing = [v for v in values or [] if not where(srcs, quoted(v), 1)]
        if missing:
            fails.append((label, f'{key} 的取值 {"、".join(missing)} 在源码里没出现'))
        else:
            passes.append((label, f'{key}：{"、".join(values or [])}'))

    remembered('外观记忆', theme.get('storageKey'), theme.get('values'))
    if family:
        remembered('语言记忆', family.get('langKey'), family.get('langValues'))
        home = family.get('home')
        if home:
            pat = re.compile(r'''(href|to)\s*=\s*\{?\s*["'`]''' + re.escape(home) + r'''["'`]''')
            hit = where(srcs, pat, 1)
            (passes if hit else fails).append(('站标回家族首页', hit[0] if hit else f'没有链到 {home} 的链接'))
        for link in family.get('links') or []:
            hit = where(srcs, quoted(link), 1)
            (passes if hit else fails).append(('同级产品链接', f'{link}：{hit[0]}' if hit else f'{link} 在源码里没出现'))
        hit = where(srcs, re.compile(r'aria-current|ariaCurrent'), 1)
        (passes if hit else fails).append(('当前所在高亮', hit[0] if hit else '没有 aria-current：当前所在只靠颜色，读屏和 Agent 看不出'))
    return fails, passes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--config', default='', help='shell.json；不给时只查主题跟随系统和根元素写死主题')
    ap.add_argument('--out', default='', help='报告目录（写 shell.md）')
    a = ap.parse_args()
    cfg = None
    if a.config:
        try:
            cfg = json.load(open(a.config, encoding='utf-8'))
            for x in (cfg.get('theme') or {}).get('fixedAllow') or []:
                re.compile(x)
        except (OSError, ValueError, re.error, AttributeError) as e:
            print(f'shell.json 读不了或写错了：{e}', file=sys.stderr)
            sys.exit(2)
    srcs = load_sources(a.paths)
    if not srcs:
        print(f'没有找到源码文件：{" ".join(a.paths)}', file=sys.stderr)
        sys.exit(2)
    fails, passes = check(srcs, cfg)
    out = ['# 外壳检查', '', f'{len(srcs)} 个源码文件；配置：{a.config or "没有（只查主题）"}', '',
           f'**结论：{"过" if not fails else "不过"}**（不过 {len(fails)} 项）', '']
    if fails:
        out += ['## 不过', '', '| 项 | 问题 |', '|---|---|'] + [f'| {k} | {v} |' for k, v in fails] + ['']
    out += ['## 过', '', '| 项 | 依据 |', '|---|---|'] + [f'| {k} | {v} |' for k, v in passes] + ['',
            '读的是源码文本，运行时的行为（读了存储键是否生效、切换后跳到另一边是否还在）上线前照 design-bar `references/family.md` 第 4 节点一遍。']
    text = '\n'.join(out)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        open(os.path.join(a.out, 'shell.md'), 'w', encoding='utf-8').write(text + '\n')
    print(text)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
