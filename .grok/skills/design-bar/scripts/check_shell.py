#!/usr/bin/env python3
"""外壳检查：主题跟随系统、偏好记忆、产品家族的导航约定。读源码文本，不渲染。

约定写在 <设计目录>/shell.json（格式见 references/family.md 第 3 节）。没有配置时只查主题跟随系统。

查什么：
  主题跟随系统   源码里有深色主题（data-theme 的 dark、.dark、color-scheme: dark），却没有 prefers-color-scheme
  根元素写死主题 <html data-theme="light|dark">、documentElement 上把主题无条件设成 light 或 dark；
                 theme.fixedAllow 里列出的特例路径（正则）不算
  偏好记忆       theme.storageKey、family.langKey 和它们的取值在源码里都出现
  家族导航       family.home 有一个链到它的链接；family.links 每个地址都出现；有 aria-current
  「无条件」的判法：写入包在守卫之后才算有条件，守卫是带 prefers-color-scheme 的 matchMedia，或键等于 theme.storageKey 的 getItem(
  （没有配置就不限键）；位置是 if 块、if 行内、三元或 && 之前。matchMedia 的 .matches 取反（!matchMedia(…).matches、=== false、!== true）仍算守卫，
  因为 `if (!matchMedia('(prefers-color-scheme: dark)').matches) { 写 'light' }` 是跟随系统的正确写法。不算守卫的：对 matchMedia 函数本身取反（!window.matchMedia，特性检测）；
  getItem 的读被取反（!x、!(x)、=== null、== undefined、!== 'light'、null === x、'light' !== x）；读的结果包在 typeof、String( 里，或后面带 ?? 、|| '默认值'。!== null 算守卫。
  只在同一行里读了偏好、if 块已经关上、写在 else 里、守卫只出现在注释或写入之后、读了别的键、媒体查询不是 prefers-color-scheme，都照报。
判不了的形态，两类：
  误报（其实有守卫，却照报）：读到的偏好或 matchMedia 的结果先存进变量再 if；if 的条件跨多行；守卫写在函数外面（调用方先 if (!saved) return，
    或 if (守卫) apply()）；getItem 的键写成变量而不是字符串字面量。
  漏报（没有守卫，却不报）：条件里有 || 且其中一边是守卫；getItem(…) !== undefined 这类和 undefined 比较的形态；比较的两边都不是常量（getItem(a) === getItem(b)）；包在自己写的函数里（readTheme(getItem(…))）；
    一行里有不成对的引号（正则字面量里的 '、JSX 文本里的撇号）会吞掉后面的 }，把已经关上的守卫块当成还开着。字符串和模板字面量里成对的花括号能正确跳过。
运行时的行为（读了存储键却没生效、系统切换主题页面跟不跟着变）它判不了：上线前由项目的外壳验收在运行时兜底（切换系统外观，页面跟着变；写死的默认值过不了）。

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


MEDIA_CALL = re.compile(r'''matchMedia\(\s*["'`][^"'`]*prefers-color-scheme''')
MATCHES_TAIL = re.compile(r'''[^"'`]*["'`]\s*\)\s*\??\.matches''')
CHAIN_BEFORE = re.compile(r'(?:[\w$]+\??\.)*$')
WRAPPED_BEFORE = re.compile(r'(?:\btypeof\s+|\bString\(\s*)(?:[\w$]+\??\.)*$')
WRAPPED_AFTER = re.compile(r'''\s*(?:\?\?|\|\|\s*["'`])''')
CONST = r'''null|undefined|true|false|\d+|["'`][^"'`]*["'`]'''
CMP_LEFT = re.compile(r'(' + CONST + r')\s*(===?|!==?)\s*$')
CMP_RIGHT = re.compile(r'\s*(===?|!==?)\s*(' + CONST + r')')


def negated_before(prefix):
    """调用前面紧挨着的 ! 、!( 的个数是奇数：被取反了。"""
    prefix = CHAIN_BEFORE.sub('', prefix)
    run = re.search(r'[!\s(]*$', prefix).group(0)
    return run.count('!') % 2 == 1


def read_is_positive(cond, start, end):
    """getItem 的读在条件里是不是「读到了偏好才为真」：!x、=== null、!== 'light'、null === x 是反过来的。"""
    positive = not negated_before(cond[:start])
    left = CMP_LEFT.search(CHAIN_BEFORE.sub('', cond[:start]).rstrip('!( \t'))
    right = CMP_RIGHT.match(cond, end)
    cmp = (left.group(2), left.group(1)) if left else (right.group(1), right.group(2)) if right else None
    if cmp:
        op, val = cmp
        if val in ('null', 'undefined'):
            if not op.startswith('!'):
                positive = not positive
        elif op.startswith('!'):
            positive = not positive
    return positive


def is_guard(cond, key=None):
    """条件里有没有一个真正读了系统外观或存储偏好的调用。
    matchMedia 要带 prefers-color-scheme：它的 .matches 取反、=== false、!== true 仍算守卫（!matchMedia(…).matches 写 light 是跟随系统的正确写法）；
    对 matchMedia 函数本身取反（特性检测）、没有 .matches 却取反，不算。
    getItem( 的键要等于配置里的 theme.storageKey（没配置就不限键）；读的结果取反（!x、=== null、!== 'light'、null === x）不算，
    !== null 算；读的结果包在 typeof、String( 里或带 ?? 、|| '默认值' 的，读不出有没有偏好，不算。"""
    for m in MEDIA_CALL.finditer(cond):
        if WRAPPED_BEFORE.search(cond[:m.start()]):
            continue
        if MATCHES_TAIL.match(cond, m.end()):
            return True
        if not negated_before(cond[:m.start()]):
            return True
    item = re.compile(r'''getItem\(\s*["'`]''' + (re.escape(key) if key else r'''[^"'`]*''') + r'''["'`]\s*\)''')
    for m in item.finditer(cond):
        if WRAPPED_BEFORE.search(cond[:m.start()]) or WRAPPED_AFTER.match(cond, m.end()):
            continue
        if read_is_positive(cond, m.start(), m.end()):
            return True
    return False


COMMENT = re.compile(r'/\*.*?\*/|<!--.*?-->|(?<![:\\])//[^\n]*', re.S)


def blank_comments(text):
    return COMMENT.sub(lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text)


def last_if(seg):
    """seg 里最后一个 if (…)：返回（括号里的条件，括号后的剩余文本），括号没配平就返回 None。"""
    starts = [m.start() for m in re.finditer(r'\bif\s*\(', seg)]
    if not starts:
        return None
    i = seg.index('(', starts[-1])
    depth, quote = 0, ''
    for j in range(i, len(seg)):
        c = seg[j]
        if quote:
            quote = '' if c == quote else quote
        elif c in '\'"`':
            quote = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return seg[i + 1:j], seg[j + 1:]
    return None


def block_stack(text, end, key=None):
    """text[:end] 末尾还没关上的花括号块，每块一个标记：是不是由带守卫条件的 if 打开的。字符串里的花括号跳过。"""
    stack, quote, line_start = [], '', 0
    for i in range(end):
        c = text[i]
        if c == '\n':
            line_start, quote = i + 1, '' if quote != '`' else quote
        elif quote:
            quote = '' if c == quote else quote
        elif c in '\'"`':
            quote = c
        elif c == '{':
            cond = last_if(text[line_start:i])
            stack.append(bool(cond and not cond[1].strip() and is_guard(cond[0], key)))
        elif c == '}' and stack:
            stack.pop()
    return stack


def guarded(text, p, key=None):
    """text[p] 处的根主题写入是否真的包在跟随系统或读存储偏好的条件里。
    认的形态：还没关上的带守卫 if 块里；同一行 if (守卫) 后面没有分号、花括号、else 就接着写；守卫 ? 或 守卫 && 之后写；
    上一行是只有条件的 if (守卫)、这一行以写入开头。当前行以 else 开头、if 块已经关上、守卫只出现在条件之后或注释里，都不算。"""
    if any(block_stack(text, p, key)):
        return True
    line_start = text.rfind('\n', 0, p) + 1
    seg = re.sub(r'(?:window\.)?document\.$', '', text[line_start:p])
    cond = last_if(seg)
    if cond and is_guard(cond[0], key) and not re.search(r'[;{}]|\belse\b', cond[1]):
        return True
    op = re.search(r'(?:\?|&&)\s*$', seg)
    if op and re.search(r'matchMedia|getItem\(', seg) and is_guard(re.sub(r'[;{}]', ' ', seg[:op.start()]), key):
        return True
    if not seg.strip():
        prev = text[:line_start].rstrip('\n').rsplit('\n', 1)[-1]
        cond = last_if(prev)
        return bool(cond and is_guard(cond[0], key) and not cond[1].strip() and re.match(r'\s*(else\s+)?if\b', prev))
    return False


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
        body = blank_comments(text)
        for pat in FORCED:
            for m in pat.finditer(body):
                if pat is FORCED[0] or not guarded(body, m.start(), theme.get('storageKey')):
                    forced.append((body.count('\n', 0, m.start()) + 1, f))
    forced = [f'{f}:{n}' for n, f in sorted(set(forced), key=lambda x: (x[1], x[0]))]
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
            '读的是源码文本，运行时的行为（读了存储键是否生效、切换后跳到另一边是否还在）由项目的外壳验收在运行时兜底，见 design-bar `references/family.md` 第 4 节。']
    text = '\n'.join(out)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        open(os.path.join(a.out, 'shell.md'), 'w', encoding='utf-8').write(text + '\n')
    print(text)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
