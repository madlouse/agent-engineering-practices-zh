#!/usr/bin/env python3
"""手写的页面画板（现在只有 Main.dc.html）和 shell.md 对齐：
  1. 脚本里的 SHELL 和 shellVals() 整段换成 shell.md 第 2 节的那一份；
  2. 核对导航、订阅条、页底订阅、页脚四段标记和 shell.md 逐字相同（只忽略缩进，以及导航里哪一站标了 aria-current），不同就报错退出。
用法：sync_shell.py <shell.md> <画板...>"""
import re, sys

md = open(sys.argv[1], encoding='utf-8').read()
def block(heading, lang):
    sec = md.split('\n## ' + heading, 1)[1].split('\n## ', 1)[0]
    return re.search(r'```' + lang + r'\n(.*?)```', sec, re.S).group(1).rstrip('\n')
SHELL_JS = block('2. ', 'js')
PARTS = {'导航': block('3. ', 'html'), '订阅条和 RSS 行': block('4. ', 'html'), '页底订阅': block('5. ', 'html'), '页脚': block('6. ', 'html')}
flat = lambda t: re.sub(r'\s+', ' ', re.sub(r'>\s+<', '><', t.replace(' aria-current="page"', ''))).strip()

bad = 0
for path in sys.argv[2:]:
    src = open(path, encoding='utf-8').read()
    i = src.index('/* ── 外壳：文案和取值')
    j = src.index('\n}\n', src.index('function shellVals', i)) + 3
    out = src[:i] + SHELL_JS + '\n' + src[j:]
    body = flat(out)
    for name, part in PARTS.items():
        if flat(part) not in body:
            bad += 1; print(f'{path}：「{name}」和 shell.md 不一致，照 shell.md 第 3–6 节改')
    if out != src: open(path, 'w', encoding='utf-8').write(out)
    print(f'{path}：SHELL 已{"更新" if out != src else "是最新的"}')
sys.exit(1 if bad else 0)
