# -*- coding: utf-8 -*-
from parts import *
CSS = '''/* 只属于动手页的版式（BuildMobile 是同一份标记）：首屏标题在左、一句话和主按钮在右下，别的页面的首屏都是一栏，所以不放进共享样式表。
   .vc-buildpage-top > h1（两段 span.vc-buildpage-part，各自不拆开）+ .vc-buildpage-side（导语 + 主按钮）。下面的四步是共享的 .vc-howto，四步在桌面首屏内全部可见（PRD F19） */
.vc-buildpage-top { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 4fr); gap: var(--space-5) var(--space-8); align-items: end; }
.vc-buildpage-side { display: grid; gap: var(--space-5); justify-items: start; }
.vc-buildpage-part { display: inline-block; }
/* breakpoint-desktop 1180px：标题和右侧上下叠；breakpoint-tablet 744px：主按钮整宽 */
@media (max-width: 1179px) { .vc-buildpage-top { grid-template-columns: minmax(0, 1fr); align-items: start; } }
@media (max-width: 743px) { .vc-buildpage-side { justify-items: stretch; } }'''
BODY = '''<div class="vc-page" data-theme="{{themeAttr}}" lang="{{langAttr}}">
''' + indent(nav('build'), 2) + '''
  <main>
    <section class="vc-band vc-band-moss" data-first-screen="" aria-labelledby="bd-title">
      <div class="vc-container">
        <div class="vc-buildpage-top">
          <h1 id="bd-title" class="vc-type-title-1"><span class="vc-buildpage-part">{{c.h1a}}</span><span class="vc-buildpage-part">{{c.h1b}}</span></h1>
          <div class="vc-buildpage-side">
            <p class="vc-type-lead vc-sub">{{c.lead}}</p>
            <a class="btn vc-btn-on-moss" href="#devlog">{{c.cta}}</a>
          </div>
        </div>
        <section class="vc-howto" aria-labelledby="vc-howto-title">
          <h2 id="vc-howto-title" class="kicker vc-howto-title">{{c.howTitle}}</h2>
          <ol class="vc-howto-steps">
            <sc-for list="{{ steps }}" as="s" hint-placeholder-count="4">
              <li class="vc-howto-step">
                <span class="vc-howto-n" aria-hidden="true">{{ s.n }}</span>
                <h3 class="vc-type-title-3">{{ s.title }}</h3>
                <p class="vc-type-body">{{ s.line }}</p>
                <a class="vc-quick vc-quick-small" href="{{ s.href }}">{{ s.log }}</a>
              </li>
            </sc-for>
          </ol>
        </section>
      </div>
    </section>

    <section id="projects" class="vc-container vc-section vc-section-flush" aria-labelledby="bd-proj-title">
      <div class="vc-head">
        <h2 id="bd-proj-title" class="vc-type-title-2">{{c.projTitle}}</h2>
        <p class="vc-type-body">{{c.projLead}}</p>
      </div>
      <div class="vc-project-grid">
        <sc-for list="{{ projects }}" as="p" hint-placeholder-count="3">
          <article class="vc-card vc-project">
            <p class="vc-status">{{c.status}}</p>
            <h3 class="vc-type-title-3"><a class="vc-project-name" href="{{ p.logHref }}">{{ p.name }}</a></h3>
            <p class="vc-sub">{{ p.line }}</p>
            <sc-if value="{{ p.hasOpen }}" hint-placeholder-val="{{ true }}"><p class="vc-project-links"><a class="vc-quick" href="{{ p.href }}" aria-label="{{ p.openLabel }}">{{ p.openText }}</a></p></sc-if>
          </article>
        </sc-for>
      </div>
    </section>

    <section id="devlog" class="vc-container vc-section" aria-labelledby="bd-log-title">
      <div class="vc-head">
        <h2 id="bd-log-title" class="vc-type-title-2">{{c.logTitle}}</h2>
        <p class="vc-type-body">{{c.logLead}}</p>
      </div>
      ''' + LOG_ROWS + '''
    </section>
  </main>
''' + indent(SUBSCRIBE, 2) + '\n' + indent(FOOTER, 2) + '''
</div>
</x-dc>
'''
COPY = {
 'zh': dict(
  h1a='和智能体一起，', h1b='把想法做成能用的东西',
  lead='写给想自己动手的人：你定问题，智能体出力，你来验收。',
  cta='读最新开发日志', howTitle='怎么做：四步',
  projTitle='在做的项目', projLead='三个项目都在开发中，进度写在各自的开发日志里。',
  status='开发中', projOpen='打开产品',
  logTitle='开发日志', logLead='这座站是和智能体一起做的。每条写做成了什么、和智能体怎么分工、下一步。',
  splitLabel='分工', nextLabel='下一步'),
 'en': dict(
  h1a='Turn ideas into things that work, ', h1b='with agents',
  lead='For people who want to build: you pick the problem, agents do the work, you check it.',
  cta='Read the latest devlog', howTitle='How it works: four steps',
  projTitle='What we’re building', projLead='Three projects, all in development. Each one keeps its own devlog.',
  status='In development', projOpen='Open the product',
  logTitle='Devlog', logLead='We build this site with agents. Each entry says what got done, who did what, and what’s next.',
  splitLabel='Who did what', nextLabel='Next'),
}
def steps(lang):
    b = '' if lang == 'zh' else '/en'
    S = {'zh': [
      ('挑一件真事', '一件做完就能用的小事。', '日志：找回首页的动效', 'home-motion'),
      ('写清楚目标', '做到什么算完成，怎么检查。', '日志：把「体验友好」写成规则', 'quality-terms'),
      ('交给智能体，自己验收', '它出力，你判断；错了就改要求。', '日志：两个模型各审一遍', 'two-reviewers'),
      ('公开记一笔', '哪里快、哪里卡，都写下来。', '日志：评审找出 11 处问题', 'cold-review')],
     'en': [
      ('Pick a real task', 'Something small you’ll use once it’s done.', 'Log: the home animation returns', 'home-motion'),
      ('Define done', 'Say what finished means and how you’ll check.', 'Log: “user-friendly” as rules', 'quality-terms'),
      ('Hand off, then check', 'The agent works; you judge and fix the brief.', 'Log: two blind reviews', 'two-reviewers'),
      ('Write it up in public', 'Note what went fast and what got stuck.', 'Log: a review finds 11 issues', 'cold-review')]}[lang]
    return [dict(n=str(i + 1), title=t, line=l, log=g, href=b + '/build/velicoach/' + s) for i, (t, l, g, s) in enumerate(S)]
def projects(lang):
    b = '' if lang == 'zh' else '/en'
    P = {'zh': [
      ('Veli', '威利是 Veli 里的 AI 力量训练教练，替你排好什么时候练、练什么。', 'veli', veli_href(b + '/body')),
      ('Velicoach 主站', '这座站本身：三站的首页、看清的文章库和这份开发日志。', 'velicoach', None),   # 产品就是你正在看的这座站，不放「打开产品」
      ('智能体技能库', '把做产品、做设计的方法写成智能体能反复调用的技能，公开分享。', 'agent-skills', REPO + '/tree/HEAD/.grok/skills')],
     'en': [
      ('Veli', 'Veli is an AI strength coach. It plans when you train and what you do.', 'veli', veli_href(b + '/body')),
      ('Velicoach', 'This site itself: the home page, Mind’s article library, and this devlog.', 'velicoach', None),
      ('Agent skills library', 'Our product and design methods, written as skills that agents can reuse, shared in the open.', 'agent-skills', REPO + '/tree/HEAD/.grok/skills')]}[lang]
    op = COPY[lang]['projOpen']
    sep = '：' if lang == 'zh' else ': '
    return [dict(name=n, line=l, logHref=b + '/build/' + s, href=h or '', hasOpen=bool(h), openText=op + (' ↗' if (h or '').startswith('http') else ' →'), openLabel=op + sep + n) for n, l, s, h in P]   # 技能库的地址用 tree/HEAD，跟着默认分支走，不写死集成分支
LISTS = {k: dict(steps=steps(k), projects=projects(k), logs=logs(k)) for k in ('zh', 'en')}
SCRIPT = '''<script type="text/x-dc" data-dc-script data-props='%s'>
%s
/* ── 动手页自己的文案和数据。地址：/build（英文 /en/build）；#devlog 是开发日志列表；每条日志 /build/<项目>/<slug>，项目页 /build/<项目> ── */
const COPY = %s;
const LISTS = %s;
class Component extends DCLogic {
  renderVals() {
    const v = shellVals(this, 'moss', '/build');
    const k = v.en ? 'en' : 'zh';
    return { ...v, c: COPY[k], ...LISTS[k] };
  }
  %s
}
</script>
</body>
</html>
''' % (props({}, 1440, 2740), SHELL_JS, js(COPY), js(LISTS), MOUNT)
open(U + '/boards/Build.dc.html', 'w', encoding='utf-8').write(HEAD % ('动手 · Velicoach', CSS) + BODY + SCRIPT)
print('ok')
