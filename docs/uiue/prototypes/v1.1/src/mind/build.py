#!/usr/bin/env python3
"""从 shell.md 的标准片段和本目录的页面片段（<名字>.body.html、<名字>.js）拼出 Mind、Learn 两块页面画板。
样式全在共享样式表里，这里不带样式；手机画板由 ../../gen_device_boards.py 从页面画板生成。
用法：python3 build.py   （输出到 ../../boards/）"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, '..', '..')
OUT = os.path.join(U, 'boards')
shell = open(os.path.join(U, 'shell.md'), encoding='utf-8').read()

def block(heading, lang):
    sec = shell.split('\n## ' + heading, 1)[1].split('\n## ', 1)[0]
    return re.search(r'```' + lang + r'\n(.*?)```', sec, re.S).group(1).rstrip('\n')

SHELL_JS = block('2. ', 'js')
NAV = block('3. ', 'html')
SUB = block('5. ', 'html')
FOOT = block('6. ', 'html')
assert 'aria-current="page">{{t.mind}}' in NAV

def indent(s, n=2):
    return '\n'.join((' ' * n + l) if l else l for l in s.split('\n'))

def page(name, title, props):
    read = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read().rstrip('\n')
    body = read(name + '.body.html')
    if '<!--@MS-->' in body: body = body.replace('<!--@MS-->', read(name + '.ms.html'))   # 里程碑一行的内容只写一份，收起、展开两个分支都用它
    js = read(name + '.js')
    if os.path.exists(os.path.join(HERE, name + '.component.js')): js += '\n' + read(name + '.component.js')
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="/_blob/2d0ccacf7377c5a050e285f270f25ffd">
<script src="/_blob/26c007f478ecf5fa646eda60cbc23992"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
</style>
</helmet>
<div class="vc-page" data-theme="{{{{themeAttr}}}}" lang="{{{{langAttr}}}}">
{indent(NAV)}
{body}
{indent(SUB)}
{indent(FOOT)}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
{SHELL_JS}
{js}
</script>
</body>
</html>
'''
    open(os.path.join(OUT, name + '.dc.html'), 'w', encoding='utf-8').write(html)

COMMON = '"theme":{"editor":"enum","options":["自动","浅色","深色"],"default":"自动"},"lang":{"editor":"enum","options":["中文","English"],"default":"中文"},'
TAIL = '"subscribeGate":{"editor":"enum","options":["开","关"],"default":"开"},"subscribe":{"editor":"enum","options":["填写邮箱","正在订阅","订阅成功","格式不对","提交太频繁","服务不可用"],"default":"填写邮箱"},"nav":{"editor":"enum","options":["首屏","吸顶"],"default":"首屏"},'
LINE = '"line":{"editor":"enum","options":["AI 发展史（/mind）","人机协作（/mind/collaboration）"],"default":"AI 发展史（/mind）"},"expand":{"editor":"enum","options":["全部收起","展开一条","从链接到达"],"default":"全部收起"},"words":{"editor":"enum","options":["未配置","已配置（示例地址）"],"default":"未配置"},"network":{"editor":"enum","options":["在线","离线"],"default":"在线"},'

page('Mind', '看清 · Velicoach', '{' + COMMON + LINE + TAIL + '"$preview":{"width":1440,"height":4200}}')
page('Learn', '学习路径 · 看清 · Velicoach', '{' + COMMON + '"expand":{"editor":"enum","options":["全部收起","展开一条","从链接到达"],"default":"全部收起"},' + TAIL + '"$preview":{"width":1440,"height":2720}}')
print('ok')
