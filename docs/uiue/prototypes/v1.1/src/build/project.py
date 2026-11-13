# -*- coding: utf-8 -*-
from parts import *
CSS = '''/* 只属于项目页的版式：项目说明在左，「和智能体怎么分工」在右。这是项目页比动手页多出来的一段，别的页面没有左文右表的区块，所以不放进共享样式表 */
.vc-projectpage-about { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: var(--space-6) var(--space-8); align-items: start; }
.vc-projectpage-text { display: grid; gap: var(--space-4); }
.vc-projectpage-text p { color: var(--vc-sub); }
/* breakpoint-desktop 1180px */
@media (max-width: 1179px) { .vc-projectpage-about { grid-template-columns: minmax(0, 1fr); } }'''
BODY = '''<div class="vc-page" data-theme="{{themeAttr}}" lang="{{langAttr}}">
''' + indent(nav('build'), 2) + '''
  <main>
    <section class="vc-band vc-band-moss" data-first-screen="" aria-labelledby="pj-title">
      <div class="vc-container vc-band-body">
        <nav class="vc-crumb" aria-label="{{c.crumbLabel}}"><a href="{{c.buildHref}}">{{t.build}}</a><span aria-hidden="true">/</span><a href="{{c.projectsHref}}">{{c.crumbProjects}}</a></nav>
        <h1 id="pj-title" class="vc-type-title-1">{{c.name}}</h1>
        <p class="vc-type-lead vc-sub">{{c.lead}}</p>
        <dl class="vc-facts">
          <div><dt class="vc-sr-only">{{c.statusLabel}}</dt><dd class="vc-status">{{c.status}}</dd></div>
          <div><dt>{{c.addrLabel}}</dt><dd><a class="vc-quick" href="{{c.addrHref}}">{{c.addr}}</a></dd></div>
        </dl>
        <sc-if value="{{hasLogs}}" hint-placeholder-val="{{ true }}">
          <a class="btn vc-btn-on-moss" href="#devlog">{{c.cta}}</a>
        </sc-if>
      </div>
    </section>

    <section class="vc-container vc-section vc-section-flush vc-projectpage-about" aria-labelledby="pj-about-title">
      <div class="vc-projectpage-text">
        <h2 id="pj-about-title" class="vc-type-title-2">{{c.aboutTitle}}</h2>
        <p class="vc-type-body">{{c.about1}}</p>
        <p class="vc-type-body">{{c.about2}}</p>
      </div>
      <div>
        <h3 class="vc-type-title-3" style="margin-bottom: var(--space-4);">{{c.rolesTitle}}</h3>
        <dl class="vc-deflist">
          <sc-for list="{{ roles }}" as="r" hint-placeholder-count="4">
            <div><dt>{{ r.who }}</dt><dd>{{ r.what }}</dd></div>
          </sc-for>
        </dl>
      </div>
    </section>

    <section id="devlog" class="vc-container vc-section" aria-labelledby="pj-log-title">
      <div class="vc-head">
        <h2 id="pj-log-title" class="vc-type-title-2">{{c.logTitle}}</h2>
        <sc-if value="{{hasLogs}}" hint-placeholder-val="{{ true }}"><p class="vc-type-body">{{c.logLead}}</p></sc-if>
      </div>
      <sc-if value="{{hasLogs}}" hint-placeholder-val="{{ true }}">
      ''' + LOG_ROWS + '''
      </sc-if>
      <sc-if value="{{noLogs}}" hint-placeholder-val="{{ false }}">
        <div class="vc-empty">
          <p class="vc-type-body">{{c.empty}}</p>
          <a class="vc-quick" href="{{c.allLogsHref}}">{{c.allLogs}}</a>
        </div>
      </sc-if>
    </section>
  </main>
''' + indent(SUBSCRIBE, 2) + '\n' + indent(FOOTER, 2) + '''
</div>
</x-dc>
'''
COPY = {
 'zh': dict(
  crumbLabel='所在位置', buildHref='/build', projectsHref='/build#projects', crumbProjects='在做的项目',
  name='Velicoach 主站', lead='这座站本身：三站的首页、看清的文章库和动手的开发日志，都和智能体一起做。',
  statusLabel='状态', status='开发中', addrLabel='产品地址', addr='velicoach.com', addrHref='/',
  cta='读这个项目的开发日志',
  aboutTitle='这个项目',
  about1='Velicoach 是 AGI 路上的陪练：先站稳，再看清，然后动手。这个项目做的是它的主站：首页、看清的文章和里程碑、动手的开发日志。站稳一站的产品 Veli 是另一个项目。',
  about2='整座站由一位产品负责人和一组智能体一起做。怎么做的、哪里走了弯路，都写进下面的开发日志。',
  rolesTitle='和智能体怎么分工',
  logTitle='开发日志', logLead='只列这个项目的日志，最新的在最上面。',
  empty='这个项目还没有开发日志。第一条写好后会出现在这里。', allLogs='看全部项目的开发日志', allLogsHref='/build#devlog',
  splitLabel='分工', nextLabel='下一步'),
 'en': dict(
  crumbLabel='You are here', buildHref='/en/build', projectsHref='/en/build#projects', crumbProjects='What we’re building',
  name='Velicoach', lead='This site itself: the home page, Mind’s article library, and Build’s devlog, all made with agents.',
  statusLabel='Status', status='In development', addrLabel='Product', addr='velicoach.com', addrHref='/en/',
  cta='Read this project’s devlog',
  aboutTitle='About this project',
  about1='Velicoach is a training partner for the AGI era: get strong, see clearly, then build. This project is its main site: the home page, Mind’s articles and milestones, and Build’s devlog. Veli, the strength-training product, is a separate project.',
  about2='One product owner and a team of agents build the whole site. How we did it, wrong turns included, goes into the devlog below.',
  rolesTitle='How we split the work with agents',
  logTitle='Devlog', logLead='Entries for this project only, newest first.',
  empty='This project has no devlog entries yet. The first one will appear here.', allLogs='Read the devlog for all projects', allLogsHref='/en/build#devlog',
  splitLabel='Who did what', nextLabel='Next'),
}
ROLES = {
 'zh': [('产品负责人', '定做什么；确认需求、设计和上线；发布后可以撤下任何内容。'),
        ('写的智能体', '按拆好的任务实现功能、起草内容，每次改动都带上检查结果。'),
        ('审的智能体', '另起一个没看过制作过程的智能体来评审；设计由两个不同的模型各审一遍。'),
        ('自动检查', '术语、质量词和设计稿的检查通过以后才能合并；合并只走合并脚本。')],
 'en': [('Product owner', 'Decides what to build, signs off on requirements, design, and launch, and can pull anything after it ships.'),
        ('Agents that write', 'Build each task and draft the content. Every change comes with its check results.'),
        ('Agents that review', 'A fresh agent that never saw the work reviews it. Designs get two reviews, from two different models.'),
        ('Automated checks', 'Terminology, quality-word, and design-file checks must pass before a merge. Merges go through one script.')],
}
LISTS = {k: dict(logs=[l for l in logs(k)], roles=[dict(who=w, what=x) for w, x in ROLES[k]]) for k in ('zh', 'en')}
SCRIPT = '''<script type="text/x-dc" data-dc-script data-props='%s'>
%s
/* ── 项目页自己的文案和数据。地址：/build/velicoach（英文 /en/build/velicoach）；#devlog 是本项目的开发日志；属性「开发日志」= 还没有日志时是同一个地址的空状态 ── */
const COPY = %s;
const LISTS = %s;
class Component extends DCLogic {
  renderVals() {
    const v = shellVals(this, 'moss', '/build/velicoach');
    const k = v.en ? 'en' : 'zh';
    const has = (this.props.devlog ?? '有日志') === '有日志';
    return { ...v, c: COPY[k], ...LISTS[k], hasLogs: has, noLogs: !has };
  }
  %s
}
</script>
</body>
</html>
''' % (props({"devlog": {"editor": "enum", "options": ["有日志", "还没有日志"], "default": "有日志"}}, 1440, 2600), SHELL_JS, js(COPY), js(LISTS), MOUNT)
open(U + '/boards/Project.dc.html', 'w', encoding='utf-8').write(HEAD % ('Velicoach 主站 · 动手 · Velicoach', CSS) + BODY + SCRIPT)
print('ok')
