#!/usr/bin/env python3
"""从 parts/ 生成 Article、States、About 三块页面画板。样式全在共享样式表里，这里不带样式；手机画板由 ../../gen_device_boards.py 从页面画板生成。
外壳（SHELL、shellVals、导航、页底订阅、页脚）从 shell.md 的代码块原样取，不手抄。
用法：python3 build.py   （输出到 ../../boards/）"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, '..', '..')
OUT = os.path.join(U, 'boards')
P = lambda n: open(os.path.join(HERE, 'parts', n), encoding='utf-8').read().rstrip('\n')
blocks = [c for _, c in re.findall(r'```(\w*)\n(.*?)```', open(os.path.join(U, 'shell.md'), encoding='utf-8').read(), re.S)]
SHELL_JS, NAV, SUBSCRIBE, FOOTER = blocks[2].rstrip(), blocks[3].rstrip(), blocks[5].rstrip(), blocks[6].rstrip()
assert 'function shellVals' in SHELL_JS and 'vc-nav-wrap' in NAV and 'vc-subscribe' in SUBSCRIBE and 'vc-footer' in FOOTER

def nav(mode):
    """mode: 'none'（首页、关于、404 这类不属于任何一站的页）或 'dynamic'（由 curMind、curBuild 决定）"""
    s = NAV
    assert s.count(' aria-current="page"') == 1
    if mode == 'none':
        return s.replace(' aria-current="page"', '')
    s = s.replace('href="{{t.mindHref}}" aria-current="page"', 'href="{{t.mindHref}}" aria-current="{{curMind}}"')
    s = s.replace('href="{{t.buildHref}}">', 'href="{{t.buildHref}}" aria-current="{{curBuild}}">')
    assert 'curMind' in s and 'curBuild' in s
    return s

MIND = os.path.join(os.path.dirname(HERE), 'mind')
def mind_body():
    """看清首页的标记和数据（../mind），States 里列表页的状态直接用它，不另写一份"""
    r = lambda n: open(os.path.join(MIND, n), encoding='utf-8').read().rstrip('\n')
    return r('Mind.body.html').replace('<!--@MS-->', r('Mind.ms.html')), r('Mind.js')
MIND_BODY, MIND_JS = mind_body()

def include(t):
    t = t.replace('<!--@MIND-->', MIND_BODY)
    for _ in range(4):
        t = re.sub(r'<!--@PART:(\w+)-->', lambda m: P(m.group(1) + '.html'), t)
    assert '@PART' not in t
    return t

BASE = [
    ('theme', ['自动', '浅色', '深色'], '自动'), ('lang', ['中文', 'English'], '中文'), ('subscribeGate', ['开', '关'], '开'),
    ('subscribe', ['填写邮箱', '正在订阅', '订阅成功', '格式不对', '提交太频繁', '服务不可用'], '填写邮箱'), ('nav', ['首屏', '吸顶'], '首屏'),
]
def props(extra, w, h):
    d = {k: {'editor': 'enum', 'options': o, 'default': dv} for k, o, dv in extra + BASE}
    d['$preview'] = {'width': w, 'height': h}
    s = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
    assert "'" not in s
    return s

def page(title, body, js, propstr):
    return f'''<!doctype html>
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
{body}
{SUBSCRIBE}
{FOOTER}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{propstr}'>
{SHELL_JS}
{js}
</script>
</body>
</html>
'''

ART_EXTRA = [
    ('kind', ['文章', '开发日志'], '文章'), ('media', ['正常', '视频加载中', '视频加载超过 10 秒', '视频无法播放', '没有视频'], '正常'), ('frame', ['封面', '最亮一帧', '最暗一帧'], '封面'),
    ('english', ['有英文版', '暂无英文版'], '有英文版'),
    ('scrollAt', ['正文中段', '视频'], '正文中段'),
]
ST_EXTRA = [('page', ['页面不存在', '加载中', '加载超过 10 秒', '视频无法播放', '文章暂无英文版', '订阅失败', '网络断开', '退订成功', '退订链接失效'], '页面不存在')]
files = {
    'Article.dc.html': page('比模型更耐久的 Harness · 看清 · Velicoach', nav('dynamic') + '\n' + include(P('art_main.html')), P('article_data.js') + '\n' + P('article.js'), props(ART_EXTRA, 1440, 3750)),
    'States.dc.html': page('页面状态 · Velicoach', nav('dynamic') + '\n' + include(P('states_main.html')), P('article_data.js') + '\n' + MIND_JS + '\n' + P('states.js'), props(ST_EXTRA, 1440, 1760)),
    'About.dc.html': page('关于 · Velicoach', nav('none') + '\n' + include(P('about_main.html')), P('about.js'), props([], 1440, 2530)),
}
for n, s in files.items():
    assert 'fonts.googleapis' not in s
    open(os.path.join(OUT, n), 'w', encoding='utf-8').write(s)
    print(n, len(s))
