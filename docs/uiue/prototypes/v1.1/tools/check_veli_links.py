#!/usr/bin/env python3
"""主站去 Veli 的链接（/body、/app、/auth/*，含 /en 和 https://velicoach.com 开头）一律带 utm_source（velicoach-mono map/repos.md、PRD F10）。
扫画板成品里所有写死的 href、xxxHref 和 data-encodes，找出不带 utm_source 的；有一处就退出码 1。用法：check_veli_links.py <boards 目录>"""
import re, sys, pathlib

PAT = re.compile(r'''(?:href|Href|data-encodes)\\?["']?\s*[=:]\s*\\?["'](?P<url>(?:https://velicoach\.com)?(?:/en)?/(?:body|app|auth/[\w-]+)(?![\w/-])(?P<rest>[^"'\\\s]*))''')

def scan(text):
    for m in PAT.finditer(text):
        if not m.group('rest').startswith('?') or 'utm_source=' not in m.group('rest'):
            yield text.count('\n', 0, m.start()) + 1, m.group('url')

def main(d):
    bad = [(f.name, n, u) for f in sorted(pathlib.Path(d).glob('*.dc.html')) for n, u in scan(f.read_text(encoding='utf-8'))]
    for name, n, u in bad:
        print(f'  {name}:{n} {u}：去 Veli 的链接没带 utm_source，改用外壳的 veliHref()')
    print(f'去 Veli 的链接：问题 {len(bad)} 处')
    return 1 if bad else 0

if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        cases = [('href="/body"', 1), ('href="/en/body#x"', 1), ("workoutHref: '/app'", 1), ('"href": "/auth/google"', 1), ('href=\\"/body\\"', 1),
                 ('data-encodes="https://velicoach.com/body"', 1), ('href="/body?utm_source=velicoach"', 0), ("href: veliHref('/body')", 0),
                 ('href="/build/veli"', 0), ('href="/mind"', 0), ('href="/application"', 0), ('href="/body?x=1"', 1)]
        fails = [(c, w) for c, w in cases if len(list(scan(c))) != w]
        for c, w in fails: print(f'  自测不对：{c} 应找出 {w} 处')
        print('自测通过' if not fails else '自测没过'); sys.exit(1 if fails else 0)
    sys.exit(main(sys.argv[1]))
