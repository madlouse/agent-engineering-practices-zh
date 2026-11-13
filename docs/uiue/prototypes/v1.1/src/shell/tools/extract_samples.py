#!/usr/bin/env python3
"""给 Controls 的组件样张取真实的标记：把页面画板渲染出来，按选择器取出组件的 outerHTML，存成 controls_samples.json（gen_controls.py 读它）。
样张的内容和页面画板一致，不另写一份。页面画板里这些组件的内容或结构改了以后重跑：python3 extract_samples.py
（rebuild.sh 不跑这一步：它要起浏览器；JSON 是一份快照，随源一起留着。）"""
import json, os, re, subprocess, sys, tempfile
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, '..', '..', '..')
R = os.path.join(U, '..', '..', '..', '..', '.grok', 'skills', 'design-bar', 'scripts', 'render_dc.py')   # 仓库里的 design-bar 技能
# 名字: (画板, 属性, 选择器)
WANT = {
    'ruler': ('Mind', {}, '.vc-ruler'), 'nest': ('Mind', {'line': '人机协作（/mind/collaboration）'}, '.vc-nest'),
    'paradigm': ('Mind', {'line': '人机协作（/mind/collaboration）'}, '#harness-engineering'),
    'paradigm_tool': ('Mind', {'line': '人机协作（/mind/collaboration）'}, '#prompt-engineering'),
    'path': ('Learn', {}, '.vc-path'), 'level': ('Learn', {'expand': '展开一条'}, '#level-2'),
    'meta': ('Article', {}, '.vc-meta'), 'take': ('Article', {}, '.vc-take'), 'toc': ('Article', {}, '.vc-toc'), 'video': ('Article', {}, 'figure.vc-video'),
    'loading_slow': ('Article', {'load': '加载超过 10 秒'}, '.vc-loading-slow'), 'loading': ('Article', {'load': '加载超过 10 秒'}, '.vc-loading'),
    'loading_rows': ('Mind', {'load': '加载中'}, '.vc-loading-rows'),
    'notice_action': ('Article', {'media': '视频无法播放'}, '.vc-notice-action'), 'notice_block': ('Mind', {'load': '加载失败'}, '.vc-notice-block'),
    'howto': ('Build', {}, '.vc-howto'), 'facts': ('Project', {}, '.vc-facts'), 'deflist': ('Project', {}, '.vc-deflist'),
    'empty': ('Project', {'devlog': '还没有日志'}, '.vc-empty'), 'deflist_numbered': ('About', {}, '.vc-deflist-numbered'),
    'study': ('Main', {}, '.vc-study-set'), 'era_origins': ('Mind', {}, '#era-origins'), 'era_llm_open': ('Mind', {'expand': '展开一条'}, '#era-llm'), 'era_index': ('Mind', {}, '.vc-era-index'),
    'tag': ('Main', {}, '.vc-hero-tag'), 'claim_title': ('Main', {}, '.vc-claim-title'), 'claim': ('Main', {}, '.vc-claim-list'),
}
out, cache = {}, {}
tmp = tempfile.mkdtemp()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, (board, props, sel) in WANT.items():
        key = board + json.dumps(props, ensure_ascii=False, sort_keys=True)
        if key not in cache:
            html = os.path.join(tmp, f'{len(cache)}.html')
            props = dict(props, theme='浅色')
            subprocess.check_call([sys.executable, R, os.path.join(U, 'boards', board + '.dc.html'), os.path.join(tmp, 'x.png'), '--size', '1440x900', '--still',
                                   '--props', json.dumps(props, ensure_ascii=False), '--keep-html', html], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cache[key] = html
        pg = b.new_page(); pg.goto('file://' + cache[key])
        h = pg.evaluate('(s) => { const e = document.querySelector(s); return e ? e.outerHTML : null; }', sel)
        pg.close()
        assert h, f'{name}：{board} 里没有 {sel}'
        h = re.sub(r'\s+(onclick|onmouseenter|onmouseleave|onfocus|ref|data-reactroot)="[^"]*"', '', h, flags=re.I)
        out[name] = h
    b.close()
json.dump(out, open(os.path.join(HERE, 'controls_samples.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已取', len(out), '个样张')
