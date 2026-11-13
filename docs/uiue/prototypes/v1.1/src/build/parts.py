# -*- coding: utf-8 -*-
"""动手、项目页、站稳三块画板共用的片段：外壳照 shell.md 原样；日志数据只写一份。"""
import re, json
U = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..')
shell = open(U + '/shell.md', encoding='utf-8').read()
def block(after, lang):
    i = shell.index(after)
    m = re.search(r'```' + lang + r'\n(.*?)```', shell[i:], re.S)
    return m.group(1).rstrip('\n')
SHELL_JS = block('脚本里原样照抄', 'js')
NAV = block('## 3. 导航', 'html')
SUBSCRIBE = block('## 5. 页底订阅', 'html')
FOOTER = block('## 6. 页脚', 'html')
def nav(current):
    s = NAV.replace(' aria-current="page"', '')
    key = {'body': '{{t.body}}</a>', 'mind': '{{t.mind}}</a>', 'build': '{{t.build}}</a>'}[current]
    href = {'body': 'href="{{t.bodyHref}}"', 'mind': 'href="{{t.mindHref}}"', 'build': 'href="{{t.buildHref}}"'}[current]
    assert href in s
    return s.replace(href, href + ' aria-current="page"')
HEAD = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>%s</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="/_blob/2d0ccacf7377c5a050e285f270f25ffd">
<script src="/_blob/26c007f478ecf5fa646eda60cbc23992"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{margin:0}
%s
</style>
</helmet>
'''
PROPS = {"theme":{"editor":"enum","options":["自动","浅色","深色"],"default":"自动"},"lang":{"editor":"enum","options":["中文","English"],"default":"中文"},"subscribeGate":{"editor":"enum","options":["开","关"],"default":"开"},"subscribe":{"editor":"enum","options":["填写邮箱","正在订阅","订阅成功","格式不对","提交太频繁","服务不可用"],"default":"填写邮箱"},"nav":{"editor":"enum","options":["首屏","吸顶"],"default":"首屏"}}
def props(extra, w, h):
    p = dict(PROPS); p.update(extra); p['$preview'] = {'width': w, 'height': h}
    s = json.dumps(p, ensure_ascii=False, separators=(',', ':'))
    assert "'" not in s
    return s
MOUNT = "componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }"

# 开发日志：一份数据，动手页列全部，项目页按项目筛。链接只用核对过存在的（gh api，2026-11-12；复评后对照本地 git log 又核了一遍标题和出处）。
# refs 是这一条引的 PR 或提交，可以有几个：(kind, repo, ref)。标题和首页、单条日志样张（../pages/parts/article_data.js）里的同一条一致
REPO = 'https://github.com/madlouse/velicoach'
LOGS = [
 dict(slug='cold-review', iso='2026-11-04', proj='velicoach', refs=[('commit', 'velicoach', '98a80d4')],
  zh=('合并前，一位没参与制作的评审找出 11 处问题：10 处当场改完，基线里失败的测试另开一张票',
      '一个智能体写协作规范；另一个没看过写作过程的智能体来评审；产品负责人确认方案。',
      '规范里写的每条命令都实际跑一次；在另开的那张票里把基线的 8 个失败测试修到通过。'),
  en=('A reviewer who wasn’t involved found 11 issues before the merge: 10 fixed on the spot, the failing baseline tests moved to their own ticket.',
      'One agent wrote the team rules. A second agent, which never saw the drafting, reviewed them. The product owner approved the plan.',
      'Run every command the rules mention, and fix the 8 failing baseline tests in their own ticket.')),
 dict(slug='quality-terms', iso='2026-11-04', proj='velicoach', refs=[('commit', 'velicoach', '3138a79'), ('commit', 'velicoach', 'fc7fa5e'), ('commit', 'velicoach', '35ab42c')],   # 规则、按对抗评审重写、check:vague 检查，各在一个提交里
  zh=('「体验友好」拆成五类能判对错的规则，并做成一项自动检查',
      '产品负责人提出：说不清的标准要照对标产品写成能评审的规则。智能体起草规则和检查脚本；另一个智能体做对抗评审，找出 8 类问题后重写。',
      '用这些规则对照现有设计，找出的四处冲突逐个处理。'),
  en=('“User-friendly” is now five groups of rules you can check, plus one automated check.',
      'The product owner asked for vague standards to become reviewable rules, based on benchmark products. An agent drafted the rules and the checker. Another agent attacked the draft, found 8 kinds of problems, and we rewrote it.',
      'Hold the current design against the rules and settle the four conflicts they exposed.')),
 dict(slug='two-reviewers', iso='2026-11-04', proj='velicoach', refs=[('commit', 'velicoach', 'f1ad59f')],
  zh=('两个模型各审一遍设计，互相看不到结论',
      '智能体出设计稿；两位评审智能体只拿到截图和需求，各交一份问题清单；主会话合并两份结论再改。',
      '按合并后的结论改设计稿，再评一轮，直到两份评审都通过。'),
  en=('Two different models now review each design, and neither sees the other’s findings.',
      'An agent produces the design. Two reviewer agents get only screenshots and requirements, and each files its own list. The lead session merges the two lists and makes the fixes.',
      'Revise the design from the merged list and review again until both reviewers pass it.')),
 dict(slug='home-motion', iso='2026-11-04', proj='velicoach', refs=[('commit', 'velicoach', '53696b1')],
  zh=('首页的「叶与网」动效回到设计稿里：约 6000 个点在叶子和网之间变形',
      '产品负责人发现动效不见了；智能体查出原因（设计稿的工具加载不了 three.js，上一版用静态圆点代替），改成直接用 WebGL2 画。',
      '正式站点用 three.js 实现同一个动效；评审的截图覆盖动效的几个状态。'),
  en=('The home page’s leaf-and-web animation is back in the design file: about 6,000 points morph between a leaf and a web.',
      'The product owner noticed it was gone. An agent traced the cause (the design tool couldn’t load three.js, so the last version showed static dots) and redrew it directly in WebGL2.',
      'Build the same animation with three.js on the live site, and have review screenshots cover each of its states.')),
 dict(slug='one-domain', iso='2026-11-04', proj='velicoach', refs=[('pr', 'thin-muscle-coach', '84')],   # 路由表在 Veli 的仓库：thin-muscle-coach PR #84（ADR-0032），2026-11-04 合并
  zh=('两个产品共用一个域名：按路径分给主站和 Veli',
      '产品负责人定哪些地址归主站、哪些归 Veli；智能体在 Veli 的仓库里写路由表和分流规则。',
      '主站接管根域名，其余地址转给 Veli。'),
  en=('Two products now share one domain, split by path between this site and Veli.',
      'The product owner decided which URLs belong to the site and which to Veli. An agent wrote the routing table and the split rules.',
      'Point the root domain at this site and pass every other path through to Veli.')),
]
PROJ = {'velicoach': {'zh': 'Velicoach 主站', 'en': 'Velicoach'}}
MONTH = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def logs(lang):
    out = []
    for l in LOGS:
        y, m, d = l['iso'].split('-')
        title, split, nxt = l[lang]
        base = '' if lang == 'zh' else '/en'
        refs = []
        for kind, repo, ref in l['refs']:
            root = 'https://github.com/madlouse/' + repo
            if kind == 'commit':
                refs.append(dict(href=root + '/commit/' + ref, label=repo + (' 提交 ' if lang == 'zh' else ' commit ') + ref))
            else:
                refs.append(dict(href=root + '/pull/' + ref, label=repo + ' PR #' + ref))
        out.append(dict(id='log-' + l['slug'], tid='log-' + l['slug'] + '-t', href=base + '/build/' + l['proj'] + '/' + l['slug'],
            iso=l['iso'], date=l['iso'] if lang == 'zh' else '%s %d, %s' % (MONTH[int(m)-1], int(d), y),
            project=PROJ[l['proj']][lang], title=title, split=split, next=nxt, refs=refs))
    return out
LOG_ROWS = '''<ol class="vc-rows">
        <sc-for list="{{ logs }}" as="l" hint-placeholder-count="5">
          <li class="vc-row vc-log" id="{{ l.id }}">
            <a class="vc-row-main" href="{{ l.href }}" aria-labelledby="{{ l.tid }}">
              <time class="vc-row-lead" datetime="{{ l.iso }}">{{ l.date }}</time>
              <div class="vc-row-body">
                <p class="vc-row-kind">{{ l.project }}</p>
                <h3 id="{{ l.tid }}" class="row-title">{{ l.title }}</h3>
                <p class="vc-row-line"><b>{{c.splitLabel}}</b>{{ l.split }}</p>
                <p class="vc-row-line"><b>{{c.nextLabel}}</b>{{ l.next }}</p>
              </div>
            </a>
            <p class="vc-row-more"><sc-for list="{{ l.refs }}" as="r" hint-placeholder-count="1"><a class="vc-quick" href="{{ r.href }}">{{ r.label }}</a></sc-for></p>
          </li>
        </sc-for>
      </ol>'''
def js(o): return json.dumps(o, ensure_ascii=False, indent=1)
def indent(s, n): return '\n'.join((' ' * n + ln if ln else ln) for ln in s.split('\n'))
