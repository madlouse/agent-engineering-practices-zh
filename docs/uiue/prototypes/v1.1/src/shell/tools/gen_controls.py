#!/usr/bin/env python3
"""生成 Controls.dc.html：控件状态表加外壳和组件的样张（共享样式表的验证样张）。用法：gen_controls.py <输出路径>"""
import sys
STATES = [('默认', ''), ('悬停', 'is-hover'), ('按下', 'is-press'), ('焦点', 'is-focus')]
LEAF = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><g transform="rotate(45 12 12)"><path class="vc-leaf-body" d="M12 1.5 C 18.5 6.5, 18.5 17.5, 12 22.5 C 5.5 17.5, 5.5 6.5, 12 1.5 Z"></path><path class="vc-leaf-vein" d="M12 19.5 L 9.3 7.5 M12 19.5 L 14.7 7.5" fill="none" stroke-width="1.6" stroke-linecap="round"></path></g></svg>'
RSS = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M3 3 a10 10 0 0 1 10 10 M3 7.5 a5.5 5.5 0 0 1 5.5 5.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path><circle cx="3.6" cy="12.4" r="1.3" fill="currentColor"></circle></svg>'
CLOSE = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M3.5 3.5 L12.5 12.5 M12.5 3.5 L3.5 12.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path></svg>'
PAUSE = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><rect x="4" y="3" width="2.6" height="10" rx="1" fill="currentColor"></rect><rect x="9.4" y="3" width="2.6" height="10" rx="1" fill="currentColor"></rect></svg>'

def na(why): return f'<span class="vc-sheet-na">—<br>{why}</span>'
def row(label, tpl, disabled=None, only=None):
    """tpl 里的 {c} 换成状态类。disabled：禁用一格的 html 或不禁用的理由。"""
    cells = ''.join(f'<td>{tpl.replace("{c}", c)}</td>' for _, c in STATES)
    d = disabled if (disabled and disabled.startswith('<')) else na(disabled or '总能点')
    return f'<tr><th scope="row">{label}</th>{cells}<td>{d}</td></tr>'
def table(rows):
    head = ''.join(f'<th scope="col">{n}</th>' for n in ['控件', '默认', '悬停', '按下', '焦点', '禁用'])
    return f'<div class="vc-sheet-scroll"><table><thead><tr>{head}</tr></thead><tbody>\n' + '\n'.join(rows) + '\n</tbody></table></div>'

def seg(items, sel, c, label, extra=''):
    out = []
    for i, it in enumerate(items):
        if i == sel: out.append(f'<button type="button" aria-pressed="true">{it}</button>')
        elif i == sel + 1 or (sel == len(items) - 1 and i == 0): out.append(f'<button type="button" class="{c}" aria-pressed="false">{it}</button>')
        else: out.append(f'<button type="button" aria-pressed="false">{it}</button>')
    return f'<div class="seg{extra}" role="group" aria-label="{label}">' + ''.join(out) + '</div>'
def segrow(label, items, name, extra=''):
    cells = ''.join(f'<td>{seg(items, 0, c, name, extra)}</td>' for _, c in STATES)
    return f'<tr><th scope="row">{label}</th>{cells}<td>{na("各项总能切换")}</td></tr>'

ROW_MAIN = '<a class="vc-row-main {c}" href="#row" style="--vc-row-lead: 44px; margin-inline: 0; width: 240px;"><span class="vc-row-lead">2017</span><span class="vc-row-body"><span class="row-title vc-serif">Transformer</span></span></a>'
paper = [
 row('主按钮 .btn.vc-btn-action', '<button type="button" class="btn vc-btn-action {c}">开始训练</button>', '<button type="button" class="btn vc-btn-action" disabled>正在订阅</button>'),
 row('次按钮 .btn.vc-btn-quiet', '<button type="button" class="btn vc-btn-quiet {c}">订阅</button>', '<button type="button" class="btn vc-btn-quiet" disabled>正在订阅</button>'),
 row('选项 .opt', '<a class="opt {c}" href="#opt">用 Google 开始训练</a>', '去不了的选项不摆出来'),
 row('文字入口 .vc-quick', '<a class="vc-quick {c}" href="#q">为什么是肌肉</a>', '去不了就不放'),
 row('导航项 .vc-nav-link', '<a class="vc-nav-link {c}" href="#nav">动手</a>', '导航不禁用'),
 row('导航项 · 当前页', '<a class="vc-nav-link {c}" href="#nav" aria-current="page">看清</a>', '导航不禁用'),
 row('站标 .home', '<span class="vc-nav vc-nav-paper" style="display: inline-flex; padding: var(--space-1);"><a class="home {c}" href="#home" aria-label="Velicoach 首页">' + LEAF + '<span class="vc-wordmark">Velicoach</span></a></span>', '站标总能回首页'),
 segrow('分段控件 .seg（语言）', ['中文', 'EN'], '语言'),
 segrow('分段控件 .seg（外观）', ['自动', '浅色', '深色'], '外观'),
 segrow('分段控件 .seg.vc-seg-tabs（内容线，16px）', ['AI 发展史', '人机协作'], '内容线', '" style="font-size: var(--type-body);'),
 row('语言按钮 .vc-lang-one（窄于 360px）', '<a class="vc-lang-one {c}" href="#lang" aria-label="切换到英文，现在是中文" style="display: inline-flex;"><span lang="zh-CN" style="font-weight: 700;">中</span><span aria-hidden="true">/</span><span lang="en">EN</span></a>', '两种语言总能切换'),
 row('图标按钮 .icon-btn（收起）', '<button type="button" class="icon-btn {c}" aria-label="收起">' + CLOSE + '</button>', '展开层总能收起'),
 row('输入框 .vc-field', '<input class="vc-field {c}" type="email" aria-label="邮箱" placeholder="你的邮箱" style="width: 180px;">', '<input class="vc-field" type="email" aria-label="邮箱" placeholder="你的邮箱" style="width: 180px;" disabled>'),
 row('输入框 · 出错', '<span style="display: grid; gap: var(--space-2);"><input class="vc-field {c}" type="email" aria-label="邮箱" aria-invalid="true" value="name@" style="width: 180px;"><span class="vc-error">邮箱格式不对</span></span>', '出错时仍可改'),
 row('页脚链接 .vc-footer-links a', '<span class="vc-footer-links" style="font-size: var(--type-footnote);"><a class="{c}" href="#f">隐私政策</a></span>', '页脚链接总能点'),
 row('面包屑 .vc-crumb a', '<span class="vc-crumb"><a class="{c}" href="#c">人机协作</a></span>', '上一级总能回'),
 row('RSS 行 .vc-rss-row', '<a class="vc-rss-row vc-surface-solid {c}" href="#rss">' + RSS + '<span>用 RSS 订阅更新</span></a>', 'RSS 总能订'),
 row('整行可点的行 .vc-row-main', ROW_MAIN, '行总能打开'),
 row('里程碑的开关 .vc-ms-sum（整行点开、收起）', '<details class="vc-ms-fold" style="width: 280px;"><summary class="vc-ms-sum {c}" style="--vc-row-lead: 44px; margin-inline: 0;"><span class="vc-row-lead">2017</span><span class="row-title vc-serif">Transformer</span></summary></details>', '行总能点开'),
 row('时代跳转 .vc-era-jump a', '<span class="vc-era-jump" style="display: flex;"><a class="{c}" href="#era">深度学习</a></span>', '时代总能跳到'),
 row('时代索引 .vc-era-index a', '<span class="vc-era-index" style="position: static; width: 196px;"><a class="{c}" href="#era"><span>深度学习</span><span class="mono">2012–2016</span></a></span>', '时代总能跳到'),
 row('时代索引 · 当前时代', '<span class="vc-era-index" style="position: static; width: 196px;"><a class="{c}" href="#era" aria-current="true"><span>智能体</span><span class="mono">2023–</span></a></span>', '时代总能跳到'),
 row('步骤的开关 .vc-step-sum（整行点开、收起）', '<details class="vc-step-fold" style="width: 280px;"><summary class="vc-step-sum {c}" style="grid-template-columns: var(--space-6) minmax(0, 1fr) auto; margin-inline: 0;"><span class="vc-step-n">1.1</span><span class="vc-step-name">CS50x</span></summary></details>', '行总能点开'),
 row('三站入口 .vc-station（站稳）', '<a class="vc-station vc-station-body {c}" href="#b" style="min-height: var(--space-9); width: 196px;"><span class="vc-station-name">站稳</span></a>', '三站总能去'),
]
ink = [
 row('墨底主按钮 .btn.vc-btn-on-ink', '<button type="button" class="btn vc-btn-on-ink {c}">读最新文章</button>', '<button type="button" class="btn vc-btn-on-ink" disabled>读最新文章</button>'),
 row('次按钮 .btn.vc-btn-quiet', '<button type="button" class="btn vc-btn-quiet {c}">订阅</button>', '<button type="button" class="btn vc-btn-quiet" disabled>正在订阅</button>'),
 row('选项 .opt', '<a class="opt {c}" href="#opt">用 Apple 开始训练</a>', '去不了的选项不摆出来'),
 row('文字入口 .vc-quick', '<a class="vc-quick {c}" href="#q">AI 发展史</a>', '去不了就不放'),
 row('导航项 .vc-nav-link', '<a class="vc-nav-link {c}" href="#nav">动手</a>', '导航不禁用'),
 row('导航项 · 当前页', '<a class="vc-nav-link {c}" href="#nav" aria-current="page">看清</a>', '导航不禁用'),
 segrow('分段控件 .seg（语言）', ['中文', 'EN'], '语言'),
 segrow('分段控件 .seg.vc-seg-tabs（内容线，16px）', ['AI 发展史', '人机协作'], '内容线', '" style="font-size: var(--type-body);'),
 row('暂停按钮 .icon-btn.vc-surface-ink', '<button type="button" class="icon-btn vc-surface-ink {c}" aria-label="暂停首页动画">' + PAUSE + '</button>', '动画随时能停'),
 row('「动手」圆 .orb（带 1px 亮边）', '<a class="orb {c}" href="#build"><span style="font-weight: 600;">然后动手</span><span style="font-size: var(--type-footnote); color: var(--vc-on-moss-2);">看开发日志</span></a>', '开发日志总能看'),
 row('三站入口 .vc-station（看清）', '<a class="vc-station vc-station-mind {c}" href="#m" style="min-height: var(--space-9); width: 196px;"><span class="vc-station-name">看清</span></a>', '三站总能去'),
]
moss = [
 row('苔绿底主按钮 .btn.vc-btn-on-moss', '<button type="button" class="btn vc-btn-on-moss {c}">读最新开发日志</button>', '<button type="button" class="btn vc-btn-on-moss" disabled>读最新开发日志</button>'),
 row('文字入口 .vc-quick', '<a class="vc-quick {c}" href="#q">看这条日志</a>', '去不了就不放'),
 row('导航项 · 当前页', '<a class="vc-nav-link {c}" href="#nav" aria-current="page">动手</a>', '导航不禁用'),
 row('三站入口 .vc-station（动手）', '<a class="vc-station vc-station-build {c}" href="#b" style="min-height: var(--space-9); width: 196px;"><span class="vc-station-name">动手</span></a>', '三站总能去'),
]

def nav(cls, cur, attrs=''):
    def link(n): return f'<a class="vc-nav-link" href="#{n}"' + (' aria-current="page"' if n == cur else '') + f'>{n}</a>'
    return (f'<header class="{cls}"{attrs}><a class="home" href="#home" aria-label="Velicoach 首页">{LEAF}<span class="vc-wordmark">Velicoach</span></a>'
            f'<nav class="vc-nav-links" aria-label="三站">{link("站稳")}{link("看清")}{link("动手")}</nav>'
            '<div class="seg vc-nav-lang" role="group" aria-label="语言"><a href="#zh" lang="zh-CN" aria-current="true">中文</a><a href="#en" lang="en" aria-current="false">EN</a></div>'
            '<a class="vc-lang-one" href="#en" aria-label="切换到英文，现在是中文"><span lang="zh-CN" style="font-weight: 700;">中</span><span aria-hidden="true">/</span><span lang="en">EN</span></a></header>')

NOTE = '每周日一封：一读、一练、一个项目。可一键退订。<a href="#privacy">隐私政策</a>'
def form(idp, btn, state):
    busy = state == 'busy'; err = {'format': '邮箱格式不对', 'rate': '提交太频繁，一小时后再试', 'down': '订阅暂时不可用，稍后再试'}.get(state)
    val = 'name@' if state == 'format' else ('name@example.com' if (busy or err) else '')
    return (f'<form class="vc-sub-form" action="#subscribe" novalidate><label class="vc-sr-only" for="{idp}">邮箱</label>'
            f'<input id="{idp}" class="vc-field" type="email" autocomplete="email" placeholder="你的邮箱" value="{val}" aria-invalid="{"true" if err else "false"}">'
            f'<button type="submit" class="btn {btn}"' + (' disabled' if busy else '') + f'>{"正在订阅" if busy else "订阅"}</button>'
            + (f'<p class="vc-error" role="alert">{err}</p>' if err else '') + '</form>')
def subbar(i, state):
    if state == 'closed': return f'<div class="vc-subbar vc-surface-solid"><p class="vc-sub-note">{NOTE}</p><button type="button" class="btn vc-btn-quiet" aria-expanded="false">订阅</button></div>'
    if state == 'done': return '<div class="vc-subbar vc-surface-solid is-done"><p class="vc-sub-done" role="status">已订阅，每周日见</p></div>'
    return f'<div class="vc-subbar vc-surface-solid is-open"><p class="vc-sub-note">{NOTE}</p><button type="button" class="icon-btn" aria-label="收起">{CLOSE}</button>{form("bar-" + str(i), "vc-btn-quiet", state)}</div>'
def labeled(label, html, wide=False): return f'<div class="vc-sheet-sample{" vc-sheet-sample-wide" if wide else ""}"><p class="vc-sheet-label">{label}</p>{html}</div>'

TYPE = [('vc-type-hero', '80 / 手机 44', '先站稳'), ('vc-type-hero-serif', '80 / 手机 44', '再看清'), ('vc-type-title-1', '64 / 手机 36', '和智能体一起动手'),
        ('vc-type-title-2', '40 / 手机 28', 'AI 走得越快，越要先站稳'), ('vc-type-title-3', '24 / 手机 20', '卡片标题'), ('vc-type-metric', '56 / 手机 40', '少 23%'),
        ('vc-type-lead', '19 / 手机 17', '每周两次力量训练。威利替你排好时间和动作。'), ('vc-type-body-reading', '17', '文章正文：判断先行，这一篇值得读，因为它说清了代价。'),
        ('vc-type-body', '16', '界面正文、卡片说明、按钮和导航文字。'), ('vc-type-footnote', '13', '脚注、出处、页脚链接'), ('kicker', '13 · 字重 600 · 字距 0.06em', 'AGI 路上的陪练'), ('vc-type-meta-mono', '13 · 等宽只排数字和拉丁字母，中文落到正文字体、不加字距', '2017 · 论文 · 最后核对 2026-11-04 · commit 98a80d4')]

# ── 各页面并进共享样式表的组件，每个一份最小的样张（标记和页面画板里的一样，内容取自页面画板）──
def lab(label, html, wide=True): return labeled(label, html, wide)
INK = '<div class="vc-band-ink" style="padding: var(--space-5); border-radius: var(--radius-lg);">'
MOSS = '<div class="vc-band-moss" style="padding: var(--space-5); border-radius: var(--radius-lg);">'
# 样张的标记取自页面画板（extract_samples.py 存成的快照），内容和页面一致，不另写一份
import json, os, re
SM = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'controls_samples.json'), encoding='utf-8'))
def sm(name, **swap):
    """取一个样张；swap 是「原文 → 换成」的替换（去掉页面上才有的 id、把标题降一级这类）。
    快照里还没有这个样张时（页面画板新加了组件、还没重跑 extract_samples.py）先留空并提示，跑完再生成一次。"""
    if name not in SM:
        print('controls_samples.json 里还没有「' + name + '」：先跑 extract_samples.py 再重新生成', file=sys.stderr); return ''
    h = re.sub(r'\n\s*', '', SM[name])
    for a, b in swap.items(): 
        assert a in h, (name, a); h = h.replace(a, b)
    return h
def down(h):
    """标题降一级：样张放在「h2 区块」下面，页面上的 h2、h3 在这里是 h3、h4。"""
    return re.sub(r'<(/?)h([23])\b', lambda m: f'<{m.group(1)}h{int(m.group(2)) + 1}', h)
RULER = INK + sm('ruler', **{'<nav class="vc-era-jump" id="eras"': '<nav class="vc-era-jump" style="display: flex;"'}) + '</div>'
NEST = INK + sm('nest') + '</div>'
PATH = INK + sm('path') + '</div>'
PARADIGM = down(sm('paradigm')) + down(sm('paradigm_tool'))
META = sm('meta')
TAKE = down(sm('take'))
FOLD = sm('toc')
VIDEO = sm('video')
LOADING = sm('loading_slow') + sm('loading')
LOADROWS = sm('loading_rows')
NOTICES = sm('notice_action') + sm('notice_block')
HOWTO = MOSS + down(sm('howto')) + '</div>'
FACTS = MOSS + sm('facts') + '</div>'
DEFLIST = sm('deflist')
DEFNUM = sm('deflist_numbered')
EMPTY = sm('empty')
TAG = ('<div style="position: relative; display: grid; grid-template-columns: 1fr 1fr; height: var(--space-10); border-radius: var(--radius-lg); overflow: hidden; --seam: 50%;"><div style="background: var(--vc-hero-body);"></div><div style="background: var(--vc-ink);"></div>'
  + sm('tag', **{'<h1 id="vc-hero-tag" class="vc-hero-tag vc-type-lead" data-edge="free">': '<p class="vc-hero-tag vc-type-lead" style="top: calc(50% - var(--space-3));">', '</h1>': '</p>'}) + '</div>')
CLAIM = down(sm('claim_title')) + down(sm('claim'))
STUDY = down(sm('study'))
ERA_A = down(sm('era_origins'))
ERA_B = down(sm('era_llm_open'))
ERA_INDEX = sm('era_index')
LEVEL = down(sm('level'))
MORE = f'''
<section class="vc-container vc-section" aria-labelledby="s-mind">
<h2 id="s-mind" class="vc-type-title-3" style="margin-bottom: var(--space-5);">看清：数据图、时代跳转行、范式行和整张可点的卡</h2>
<div class="vc-sheet-samples">
{lab('时间尺 .vc-ruler（数据图：不可点，role="img" 加 aria-label）和时代跳转行 .vc-era-jump（只在手机和平板显示，这里为了看清楚摆出来）', RULER)}
{lab('套叠图 .vc-nest（数据图：不可点）', NEST, False)}
{lab('四级的路 .vc-path（学习路径页的索引，每站是链接）', PATH, False)}
{lab('范式行 .vc-paradigm 和整张可点的卡 .vc-card.vc-card-link（文章写一句话，工具和技能写三项事实）', PARADIGM)}
</div>
</section>

<section class="vc-container vc-section" aria-labelledby="s-read">
<h2 id="s-read" class="vc-type-title-3" style="margin-bottom: var(--space-5);">阅读页：元信息、判断块、视频和播放条、收起的块、加载中的灰块、提示条</h2>
<div class="vc-sheet-samples">
{lab('元信息两组 .vc-meta > .vc-meta-row（第一组谁写的、什么时候；第二组我们核对了什么）', META)}
{lab('判断块 .vc-take', TAKE, False)}
{lab('收起的块 .vc-fold（目录 .vc-toc）', FOLD, False)}
{lab('视频和播放条 .vc-video > .vc-video-frame > .vc-video-shot + .vc-playbar（玻璃，背后是视频画面）；下面是收起的文字稿 .vc-fold', VIDEO)}
{lab('加载中的灰块 .vc-loading（超过 10 秒加一行 .vc-loading-slow）；列表页 .vc-loading-rows', '<div style="display: grid; gap: var(--space-5);">' + LOADING + LOADROWS + '</div>', False)}
{lab('提示条的两种排法 .vc-notice.vc-notice-action、.vc-notice.vc-notice-block', '<div style="display: grid; gap: var(--space-4);">' + NOTICES + '</div>')}
</div>
</section>

<section class="vc-container vc-section" aria-labelledby="s-lists">
<h2 id="s-lists" class="vc-type-title-3" style="margin-bottom: var(--space-5);">动手、项目、关于：编号步骤、事实一行、定义列表、空状态</h2>
<div class="vc-sheet-samples">
{lab('编号步骤 .vc-howto（动手页首屏；对应的开发日志有才链）', HOWTO)}
{lab('事实一行 .vc-facts', FACTS, False)}
{lab('空状态 .vc-empty', EMPTY, False)}
{lab('定义列表 .vc-deflist', DEFLIST, False)}
{lab('带序号的定义列表 .vc-deflist.vc-deflist-numbered', DEFNUM, False)}
</div>
</section>

<section class="vc-container vc-section" aria-labelledby="s-home">
<h2 id="s-home" class="vc-type-title-3" style="margin-bottom: var(--space-5);">首页：定位句、论点三行</h2>
<div class="vc-sheet-samples">
{lab('定位句 .vc-hero-tag（正文字体、导语字号、墨色；桌面和平板骑在接缝上居中，左半按纸面取色、右半按墨面取色；页面上它是 h1，带 data-edge="free"）', TAG)}
{lab('论点三行 .vc-claim-list（整行可点，不是三张卡）', CLAIM)}
</div>
</section>
'''

html = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>控件状态和组件样张 · Velicoach</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="/_blob/2d0ccacf7377c5a050e285f270f25ffd">
<script src="/_blob/26c007f478ecf5fa646eda60cbc23992"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
/* 只属于这块样张页的版式（状态表、样张的格子和标签）：它是设计系统的说明页，不是产品页面，所以不放进共享样式表 */
.vc-sheet{{padding:var(--space-7) var(--gutter)}}
.vc-sheet-scroll{{overflow-x:auto}}
.vc-sheet table{{border-collapse:collapse;width:100%;min-width:1320px;table-layout:fixed}}
.vc-sheet th,.vc-sheet td{{text-align:left;vertical-align:middle;padding:var(--space-3) var(--space-4) var(--space-3) 0;border-top:1px solid var(--vc-line)}}
.vc-sheet thead th{{border-top:0;font-size:var(--type-footnote);font-weight:600;color:var(--vc-sub)}}
.vc-sheet tbody th{{width:208px;font-size:var(--type-footnote);font-weight:500;color:var(--vc-sub)}}
.vc-sheet .vc-sheet-na{{display:inline-block;font-size:var(--type-footnote);line-height:var(--leading-footnote);color:var(--vc-sub)}}
.vc-sheet .orb{{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;gap:var(--space-1);width:112px;height:112px;border-radius:50%}}
.vc-sheet-samples{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--space-7) var(--space-6);align-items:start}}
.vc-sheet-sample{{display:grid;gap:var(--space-3);min-width:0;align-content:start}}
.vc-sheet-sample-wide{{grid-column:1 / -1}}
.vc-sheet-label{{margin:0;overflow-wrap:anywhere;text-wrap:pretty;font-family:var(--font-mono);font-size:var(--type-meta-mono);letter-spacing:var(--tracking-meta-mono);color:var(--vc-faint)}}
.vc-sheet-swatch{{display:flex;justify-content:center;padding:var(--space-5) var(--space-4);border-radius:var(--radius-lg)}}
.vc-sheet-type{{display:grid;grid-template-columns:320px minmax(0,1fr);gap:var(--space-5);align-items:baseline;padding-block:var(--space-3);border-top:1px solid var(--vc-line)}}
@media (max-width: 1179px){{.vc-sheet-type{{grid-template-columns:minmax(0,1fr);gap:var(--space-1)}}}}
@media (max-width: 743px){{.vc-sheet-samples{{grid-template-columns:minmax(0,1fr)}}.vc-sheet-swatch{{padding-inline:0}}}}
</style>
</helmet>
<div class="vc-page" data-theme="{{{{themeAttr}}}}" lang="zh-CN" data-board="doc">
<header class="vc-container" style="padding-top: var(--space-8); padding-bottom: var(--space-5);">
<div style="display: grid; gap: var(--space-3); max-width: var(--text-max);">
<p class="vc-type-meta-mono vc-faint">设计系统 v1.1 · 2026-11-12</p>
<h1 class="vc-type-title-2">控件状态和组件样张</h1>
<p class="vc-type-body vc-sub">一套叠加层用在所有底色上：悬停叠一层 <span class="mono">vc-state-hover</span>，按下叠 <span class="mono">vc-state-press</span>、内容下移 1px、不缩放；焦点是 2px 焦点色外圈，墨底、苔绿底和强调面上自动换成浅的一档。触屏没有悬停；焦点只在键盘操作时出现。能不禁用就不禁用，去不了的入口直接不放，所以禁用一列很多是「—」。往下是外壳（导航、订阅、页脚）和内容组件的样张，页面画板只引用这些类。</p>
</div>
</header>

<main>
<section class="vc-sheet" aria-labelledby="s-paper">
<h2 id="s-paper" class="vc-type-title-3" style="margin-bottom: var(--space-5);">纸底（站稳、阅读区、页脚）</h2>
{table(paper)}
</section>

<section class="vc-sheet vc-band-ink" aria-labelledby="s-ink">
<h2 id="s-ink" class="vc-type-title-3" style="margin-bottom: var(--space-5);">墨底（看清首屏、首页右半）</h2>
{table(ink)}
</section>

<section class="vc-sheet vc-band-moss" aria-labelledby="s-moss">
<h2 id="s-moss" class="vc-type-title-3" style="margin-bottom: var(--space-5);">苔绿底（动手首屏）</h2>
{table(moss)}
</section>

<section class="vc-container vc-section" aria-labelledby="s-shell">
<h2 id="s-shell" class="vc-type-title-3" style="margin-bottom: var(--space-6);">外壳</h2>
<div class="vc-sheet-samples">
{labeled('导航 · 纸底 .vc-nav.vc-nav-paper（首页左半、关于、404）', '<div class="vc-sheet-swatch" style="background: var(--vc-hero-body);">' + nav('vc-nav vc-nav-paper', '站稳') + '</div>', True)}
{labeled('导航 · 墨底 .vc-nav.vc-nav-ink（看清首屏）', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);">' + nav('vc-nav vc-nav-ink', '看清') + '</div>', True)}
{labeled('导航 · 苔绿底 .vc-nav.vc-nav-moss（动手首屏）', '<div class="vc-sheet-swatch" style="background: var(--vc-moss-hero);">' + nav('vc-nav vc-nav-moss', '动手') + '</div>', True)}
{labeled('导航 · 吸顶玻璃 .vc-nav.lg（滚过首屏，压过正文）', '<div style="position: relative; overflow: hidden; border-radius: var(--radius-lg); padding: var(--space-4); background: var(--vc-paper-surface); box-shadow: 0 0 0 1px var(--vc-paper-line);"><p class="vc-type-body-reading" style="margin: 0;">上下文工程要回答的问题是：模型每一步该看到哪些信息。看到的太少，它只能猜；看到的太多，重点被淹没，成本也跟着涨。吸顶的导航压在这样的正文上，背后的字要糊成色块，导航上的字照样读得清。所以吸顶玻璃的模糊用 20px 一档，比压在视频上的小块玻璃重得多；系统要求降低透明度时，换成同色的实色面。</p><div style="position: sticky; top: 0; display: flex; justify-content: center; margin-top: calc(-1 * (var(--nav-height) + var(--space-7))); padding-bottom: var(--space-5);">' + nav('vc-nav lg', '看清', ' data-backdrop="scroll" data-lens=""') + '</div></div>', True)}
{labeled('订阅条 · 收起 .vc-subbar', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);">' + subbar(0, 'closed') + '</div>')}
{labeled('RSS 行 .vc-rss-row（订阅的上线开关关着时，订阅条的位置换成它）', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);"><a class="vc-rss-row vc-surface-solid" href="#rss">' + RSS + '<span>用 RSS 订阅更新</span></a></div>')}
{labeled('订阅条 · 填写邮箱 .is-open', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);">' + subbar(1, 'open') + '</div>')}
{labeled('订阅条 · 正在订阅', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);">' + subbar(2, 'busy') + '</div>')}
{labeled('订阅条 · 格式不对', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);">' + subbar(3, 'format') + '</div>')}
{labeled('订阅条 · 订阅成功 .is-done', '<div class="vc-sheet-swatch" style="background: var(--vc-ink);">' + subbar(4, 'done') + '</div>')}
{labeled('订阅表单 · 提交太频繁', form('f-rate', 'vc-btn-action', 'rate'))}
{labeled('订阅表单 · 服务不可用', form('f-down', 'vc-btn-action', 'down'))}
</div>
</section>


<section class="vc-container vc-section" aria-labelledby="s-type">
<h2 id="s-type" class="vc-type-title-3" style="margin-bottom: var(--space-5);">字号阶梯：8 级加 metric</h2>
''' + '\n'.join(f'<div class="vc-sheet-type"><p class="vc-sheet-label">.{c} · {n}</p><p class="{c}">{t}</p></div>' for c, n, t in TYPE) + f'''
</section>

<section class="vc-container vc-section" aria-labelledby="s-study">
<h2 id="s-study" class="vc-type-title-3" style="margin-bottom: var(--space-5);">数字卡（研究卡）</h2>
{STUDY}
<p class="vc-study-foot">这些是人群研究的平均结果，不是对每个人的保证。有伤病或疼痛，先问医生。</p>
</section>

<section class="vc-container vc-section" aria-labelledby="s-time">
<h2 id="s-time" class="vc-type-title-3" style="margin-bottom: var(--space-5);">时间线：时代段头、按年数留白的刻度、默认收起的里程碑（第二段里展开了一条）、时代索引</h2>
<div class="vc-with-aside">
<div class="vc-timeline">
{ERA_A}
{ERA_B}
</div>
<aside aria-label="时代索引">
{ERA_INDEX}
</aside>
</div>
</section>

<section class="vc-container vc-section" aria-labelledby="s-step">
<h2 id="s-step" class="vc-type-title-3" style="margin-bottom: var(--space-5);">学习路径步骤块（默认收起；这一级里展开了一步）</h2>
{LEVEL}
</section>

<section class="vc-container vc-section" aria-labelledby="s-build">
<h2 id="s-build" class="vc-type-title-3" style="margin-bottom: var(--space-5);">开发日志的行、项目卡</h2>
<div class="vc-sheet-samples">
<div class="vc-sheet-sample vc-sheet-sample-wide">
<ol class="vc-rows">
<li class="vc-row vc-log"><a class="vc-row-main" href="#log" aria-labelledby="log-one-domain-t"><time class="vc-row-lead" datetime="2026-11-03">2026-11-03</time><div class="vc-row-body"><p class="vc-row-kind">Velicoach 主站</p><h3 id="log-one-domain-t" class="row-title">两个产品，共用一个域名</h3><p class="vc-row-line"><b>分工</b>　产品负责人定哪些地址归主站、哪些归 Veli；智能体写路由表和分流规则。</p><p class="vc-row-line"><b>下一步</b>　主站接管根域名，其余地址转给 Veli。</p></div></a><p class="vc-row-more"><a class="vc-quick" href="https://github.com/madlouse/velicoach/pull/1">velicoach PR #1</a></p></li>
</ol>
</div>
<div class="vc-sheet-sample vc-sheet-sample-wide"><div class="vc-project-grid">
<article class="vc-card vc-project"><p class="vc-status">开发中</p><h3 class="vc-type-title-3">Veli</h3><p class="vc-sub">威利是 Veli 里的 AI 力量训练教练，替你排好什么时候练、练什么。</p><p class="vc-project-links"><a class="vc-quick" href="#veli-log">看开发日志</a><a class="vc-quick" href="/body">打开产品</a></p></article>
<article class="vc-card vc-project"><p class="vc-status">开发中</p><h3 class="vc-type-title-3">Velicoach 主站</h3><p class="vc-sub">这座站本身：三站的首页、看清的文章和这份开发日志。</p><p class="vc-project-links"><a class="vc-quick" href="#site-log">看开发日志</a><a class="vc-quick" href="/">打开产品</a></p></article>
</div></div>
</div>
</section>

<section class="vc-container vc-section" aria-labelledby="s-cards">
<h2 id="s-cards" class="vc-type-title-3" style="margin-bottom: var(--space-5);">强调卡、三站入口小色带、原地展开的卡片、面包屑</h2>
<div class="vc-sheet-samples">
<div class="vc-sheet-sample vc-sheet-sample-wide"><p class="vc-sheet-label">强调卡 .vc-feature（首页「最新文章」；深色下比页面底高一档，加 1px 描边）</p>
<article class="vc-feature"><p class="kicker">最新文章</p><h3 class="vc-type-title-2-serif">比模型更耐久的 Harness</h3><p class="vc-type-lead">模型每几个月换一代，围着它搭的工具、权限和验证环境却能一直用下去。</p><div class="vc-feature-actions"><a class="btn vc-btn-on-ink" href="#read">读最新文章</a><p class="vc-type-meta-mono">12 分钟 · 附 3 分钟视频</p></div></article></div>
<div class="vc-sheet-sample vc-sheet-sample-wide"><p class="vc-sheet-label">三站入口小色带 .vc-stations（404）</p>
<div class="vc-stations"><a class="vc-station vc-station-body" href="/body"><span class="vc-station-name">站稳</span><span class="vc-station-line">每周两次力量训练。</span></a><a class="vc-station vc-station-mind" href="/mind"><span class="vc-station-name">看清</span><span class="vc-station-line">读懂 AI 从哪里来。</span></a><a class="vc-station vc-station-build" href="/build"><span class="vc-station-name">动手</span><span class="vc-station-line">和智能体一起做出东西。</span></a></div></div>
<div class="vc-sheet-sample"><p class="vc-sheet-label">原地展开的卡片 .vc-pop（挂在 .vc-pop-anchor 上；这里为了看清楚摆在流里）</p>
<div class="vc-pop" data-pop="" style="position: static; width: auto;"><div class="vc-pop-opts"><a class="opt" href="/auth/google">用 Google 开始训练</a><a class="opt" href="/auth/apple">用 Apple 开始训练</a></div><p class="vc-pop-note">第一练 12 分钟。在 Veli 登录过的人直接到今天的安排；按 Esc 收起。</p></div></div>
<div class="vc-sheet-sample"><p class="vc-sheet-label">面包屑 .vc-crumb</p>
<nav class="vc-crumb" aria-label="所在位置"><a href="/mind">看清</a><span aria-hidden="true">/</span><a href="/mind/collaboration">人机协作</a></nav></div>
</div>
</section>

<section class="vc-container vc-section" aria-labelledby="s-prose">
<h2 id="s-prose" class="vc-type-title-3" style="margin-bottom: var(--space-5);">阅读版式（中文、英文）、侧注和文末脚注</h2>
<div class="vc-prose">
<h2>先说判断</h2>
<aside class="vc-sidenote" id="sn-1"><span class="mono">1</span>原文把 Harness 定义成「模型周围的一切」：工具、权限、上下文和验证。</aside>
<p>这一篇值得读，因为它说清了代价：模型换代很快，围着模型搭的环境<sup id="ref-1"><a class="vc-ref-side" href="#sn-1">1</a><a class="vc-ref-foot" href="#fn-1">1</a></sup>却要用很多年。先搭环境，再换模型，顺序不能反。</p>
<h3>适合谁</h3>
<p>已经在用智能体写代码、开始为「怎么验收」发愁的人。行内代码<span class="vc-nowrap">写成 <code>npm run verify</code>。</span></p>
<blockquote>把验证做成智能体自己能跑的命令，它才知道什么叫做完。</blockquote>
<pre><code>npm run verify   # 类型检查、单元测试、端到端测试</code></pre>
<ol class="vc-footnotes"><li id="fn-1"><span>原文把 Harness 定义成「模型周围的一切」：工具、权限、上下文和验证。&nbsp;<a href="#ref-1" aria-label="回到正文">↩</a></span></li></ol>
</div>
<div class="vc-prose" lang="en" style="margin-top: var(--space-7);">
<h2>Our verdict first</h2>
<p>Worth reading, because it is honest about the cost. Models turn over every few months; the tools, permissions, and checks you build around them stay for years. Build the environment first, then swap the model.</p>
</div>
</section>

{MORE}
</main>
<section class="vc-subscribe vc-container" aria-labelledby="s-sub">
<div class="vc-subscribe-text"><h2 id="s-sub" class="vc-type-title-3">订阅</h2><p class="vc-sub-note">{NOTE}</p></div>
{form('page-sub', 'vc-btn-action', '')}
</section>
<footer class="vc-footer vc-container">
<nav class="vc-footer-links" aria-label="页脚"><a href="#about">关于</a><a href="#contact">联系</a><a href="#copyright">版权与转载</a><a href="#privacy">隐私政策</a><a href="#health">健康数据政策</a><a href="#disclaimer">健康免责</a><a href="#terms">服务条款</a><a href="#feed">RSS</a></nav>
<div class="vc-footer-tools"><div class="seg" role="group" aria-label="外观"><button type="button" aria-pressed="{{{{themeAuto}}}}" onClick="{{{{setAuto}}}}">自动</button><button type="button" aria-pressed="{{{{themeLight}}}}" onClick="{{{{setLight}}}}">浅色</button><button type="button" aria-pressed="{{{{themeDark}}}}" onClick="{{{{setDark}}}}">深色</button></div><div class="seg" role="group" aria-label="语言"><a href="#zh" lang="zh-CN" aria-current="true">中文</a><a href="#en" lang="en" aria-current="false">EN</a></div></div>
<p class="vc-footer-note">威利不是医生。有伤病或疼痛，先停下来，问医生。</p>
</footer>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"theme":{{"editor":"enum","options":["自动","浅色","深色"],"default":"自动"}},"$preview":{{"width":1440,"height":19500}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    const theme = (this.state && this.state.theme) ?? this.props.theme ?? '自动';
    return {{
      themeAttr: theme === '深色' ? 'dark' : theme === '浅色' ? 'light' : '',
      themeAuto: theme === '自动' ? 'true' : 'false', themeLight: theme === '浅色' ? 'true' : 'false', themeDark: theme === '深色' ? 'true' : 'false',
      setAuto: () => this.setState({{ theme: '自动' }}), setLight: () => this.setState({{ theme: '浅色' }}), setDark: () => this.setState({{ theme: '深色' }}),
    }};
  }}
  componentDidMount() {{ if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }}
}}
</script>
</body>
</html>
'''
open(sys.argv[1], 'w', encoding='utf-8').write(html)
