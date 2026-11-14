# -*- coding: utf-8 -*-
from parts import *
# 站稳页的文案和列表（中英两版）在 body_copy.json 里：T 是文案，L 是列表
_copy = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'body_copy.json'), encoding='utf-8'))
T, L = _copy['T'], _copy['L']
CSS = '''/* 参考画板：站稳页是 Veli 的落地页，由 Veli 仓库实现，主站别的页面不用这些版式，所以留在这一页，不放进共享样式表。外壳、区块标题（.vc-head）、纸面卡片（.vc-card）、原地展开（.vc-pop）用共享的 */
/* 首屏：左边标题、导语和「开始训练」，右边一周安排的样张 */
.vc-bodypage-hero { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: var(--space-8); align-items: start; }
.vc-bodypage-text { display: grid; gap: var(--space-5); justify-items: start; }
.vc-bodypage-text .vc-type-lead { max-width: var(--text-max); color: var(--vc-sub); }
.vc-bodypage-actions { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2) var(--space-5); }
.vc-bodypage-direct { display: none; }
/* 「开始训练」的选项在按钮下方展开（.vc-pop.vc-pop-code：用 Google 和用邮箱上下排，右边是在手机上打开这一页的码） */
.vc-bodypage-plan { margin: 0; display: grid; gap: var(--space-3); }
.vc-bodypage-plan > figcaption { color: var(--vc-sub); }
.vc-bodypage-card { display: grid; gap: var(--space-4); }
.vc-bodypage-card > * { margin: 0; }
.vc-bodypage-plan-list { list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--vc-line); }
.vc-bodypage-plan-list li { display: flex; flex-wrap: wrap; justify-content: space-between; gap: var(--space-1) var(--space-4); padding: var(--space-3) 0; border-bottom: 1px solid var(--vc-line); }
.vc-bodypage-plan-kind { color: var(--vc-faint); }
.vc-bodypage-plan-list .mono { font-size: var(--type-meta-mono); line-height: var(--leading-body); color: var(--vc-status); white-space: nowrap; }
/* 三栏的行：标签或序号、名称、一句说明 */
.vc-bodypage-list { list-style: none; margin: 0; padding: 0; border-bottom: 1px solid var(--vc-line); }
.vc-bodypage-list li { display: grid; grid-template-columns: 96px 200px minmax(0, 1fr); gap: var(--space-1) var(--space-5); align-items: baseline; padding: var(--space-4) 0; border-top: 1px solid var(--vc-line); }
.vc-bodypage-list .mono { font-size: var(--type-meta-mono); color: var(--vc-status); }
.vc-bodypage-list h3 { font-family: var(--font-sans); }
.vc-bodypage-list p { margin: 0; color: var(--vc-sub); text-wrap: pretty; }
.vc-bodypage-branch { margin: var(--space-4) 0 0; }
.vc-bodypage-start { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-3) var(--space-5); }
.vc-bodypage-start .opt { padding-inline: var(--space-5); }
/* breakpoint-desktop 1180px */
@media (max-width: 1179px) { .vc-bodypage-hero { grid-template-columns: minmax(0, 1fr); gap: var(--space-7); } }
/* 触屏和窄于桌面版式：「用 Google 开始训练」实心按钮加「用邮箱开始」文字入口直接摆在按钮的位置，不用先点开（和首页同一断点；步数表「开始训练」：没登录过 2 步） */
@media (max-width: 1179px), (hover: none) {
  .vc-bodypage-start-anchor { display: none; }
  .vc-bodypage-direct { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-2) var(--space-5); }
}
/* breakpoint-tablet 744px：手机上按钮占满一行，文字入口在它下面 */
@media (max-width: 743px) {
  .vc-bodypage-direct { display: grid; gap: var(--space-1); width: 100%; }
  .vc-bodypage-direct .vc-quick { justify-self: start; }
  .vc-bodypage-text, .vc-bodypage-actions { justify-items: stretch; }
  .vc-bodypage-actions { display: grid; width: 100%; }
  .vc-bodypage-list li { grid-template-columns: minmax(0, 1fr); }
  .vc-bodypage-start { display: grid; justify-items: start; }
  .vc-bodypage-start .opt { justify-self: stretch; }
  /* 图缩到手机宽度后约是原来的 13/40：星期的字取脚注字号再放大 40/13，缩放后约等于脚注字号 */
  .vc-bodypage-branch svg { overflow: visible; margin-top: var(--space-4); }
  .vc-bodypage-branch text { font-size: calc(var(--type-footnote) * 40 / 13); }
}'''
BODY = '''<div class="vc-page" data-theme="{{themeAttr}}" lang="{{langAttr}}">
''' + indent(nav('body'), 2) + '''
  <main>
    <section class="vc-band vc-band-paper" data-first-screen="" aria-labelledby="bo-title">
      <div class="vc-container vc-bodypage-hero">
        <div class="vc-bodypage-text">
          <h1 id="bo-title" class="vc-type-title-1">{{c.h1}}</h1>
          <p class="vc-type-lead">{{c.lead}}</p>
          <div class="vc-bodypage-actions">
            <div class="vc-pop-anchor vc-bodypage-start-anchor" onMouseEnter="{{openStart}}" onMouseLeave="{{closeLater}}">
              <a class="btn vc-btn-action" href="{{c.appHref}}" aria-expanded="{{startExpanded}}" aria-controls="bo-start-options" onFocus="{{focusStart}}"><span>{{c.cta}}</span><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M4.5 2.5 L8 6 L4.5 9.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"></path></svg></a>
              <div id="bo-start-options" class="{{popClass}}" data-pop="" role="group" aria-label="{{c.startGroup}}">
                <div class="vc-pop-opts"><a class="opt" href="{{c.googleHref}}">{{c.google}}</a><a class="vc-quick" href="{{c.emailHref}}">{{c.email}}</a></div>
                <svg class="vc-start-code" data-encodes="{{codeTarget}}" role="img" aria-label="{{c.codeLabel}}" viewBox="-4 -4 29 29"><path fill="currentColor" d="M0 0h7v7H0zM1 1v5h5V1zM2 2h3v3H2zM14 0h7v7h-7zM15 1v5h5V1zM16 2h3v3h-3zM0 14h7v7H0zM1 15v5h5v-5zM2 16h3v3H2zM8 0h1v2H8zM10 1h2v1h-2zM9 3h2v2H9zM12 4h1v3h-1zM8 6h1v2H8zM10 8h3v1h-3zM0 8h2v1H0zM3 9h3v1H3zM14 8h2v2h-2zM17 9h4v1h-4zM8 10h1v3H8zM10 11h2v2h-2zM13 11h2v1h-2zM16 12h3v2h-3zM20 11h1v3h-1zM8 14h2v2H8zM11 15h3v1h-3zM15 15h1v3h-1zM17 15h2v2h-2zM8 17h1v4H8zM10 18h3v1h-3zM12 20h4v1h-4zM17 19h2v2h-2zM20 17h1v2h-1z"></path></svg>
                <p class="vc-pop-note">{{c.popNote}}</p>
              </div>
            </div>
            <div class="vc-bodypage-direct" role="group" aria-label="{{c.startGroup}}"><a class="btn vc-btn-action" href="{{c.googleHref}}">{{c.google}}</a><a class="vc-quick" href="{{c.emailHref}}">{{c.email}}</a></div>
            <a class="vc-quick" href="#how">{{c.how}}</a>
          </div>
        </div>
        <figure class="vc-bodypage-plan">
          <div class="vc-card vc-bodypage-card">
            <p class="vc-type-lead">{{c.planIntro}}</p>
            <ul class="vc-bodypage-plan-list">
              <sc-for list="{{ plan }}" as="p" hint-placeholder-count="5">
                <li><span><span class="vc-bodypage-plan-kind">{{ p.kind }} · </span>{{ p.name }}</span><span class="mono">{{ p.dose }}</span></li>
              </sc-for>
            </ul>
          </div>
          <figcaption class="vc-type-footnote">{{c.planCap}}</figcaption>
        </figure>
      </div>
    </section>

    <section id="what" class="vc-container vc-section vc-section-flush" aria-labelledby="bo-what-title">
      <div class="vc-head">
        <h2 id="bo-what-title" class="vc-type-title-2">{{c.whatTitle}}</h2>
        <p class="vc-type-body">{{c.whatLead}}</p>
      </div>
      <ol class="vc-bodypage-list">
        <sc-for list="{{ moves }}" as="m" hint-placeholder-count="3">
          <li><span class="mono">{{ m.tag }}</span><h3 class="vc-type-lead">{{ m.name }}</h3><p class="vc-type-body">{{ m.line }}</p></li>
        </sc-for>
      </ol>
    </section>

    <section id="how" class="vc-container vc-section vc-section-flush" aria-labelledby="bo-how-title">
      <div class="vc-head">
        <h2 id="bo-how-title" class="vc-type-title-2">{{c.how}}</h2>
        <p class="vc-type-body">{{c.howLead}}</p>
      </div>
      <ol class="vc-bodypage-list">
        <sc-for list="{{ steps }}" as="s" hint-placeholder-count="3">
          <li><span class="mono" aria-hidden="true">{{ s.n }}</span><h3 class="vc-type-lead">{{ s.title }}</h3><p class="vc-type-body">{{ s.line }}</p></li>
        </sc-for>
      </ol>
      <figure class="vc-card vc-bodypage-card vc-bodypage-branch">
        <h3 class="vc-type-title-3">{{c.branch}}</h3>
        <svg viewBox="0 0 980 110" width="100%" role="img" aria-label="{{c.branchAlt}}">
          <g font-family="var(--font-sans)" font-size="16" fill="var(--vc-text-2)" text-anchor="middle">
            <text x="70" y="20">{{c.d1}}</text><text x="210" y="20">{{c.d2}}</text><text x="350" y="20">{{c.d3}}</text><text x="490" y="20">{{c.d4}}</text><text x="630" y="20">{{c.d5}}</text><text x="770" y="20">{{c.d6}}</text><text x="910" y="20">{{c.d7}}</text>
          </g>
          <line x1="30" y1="88" x2="950" y2="88" stroke="var(--vc-moss)" stroke-width="3" stroke-linecap="round"></line>
          <path d="M70 88 C 52 74, 54 52, 70 46 C 86 52, 88 74, 70 88 Z" fill="var(--vc-moss)"></path>
          <circle cx="210" cy="88" r="5" fill="var(--vc-moss)"></circle>
          <path d="M350 88 C 332 74, 334 52, 350 46 C 366 52, 368 74, 350 88 Z" fill="var(--vc-moss)"></path>
          <path d="M490 88 C 472 74, 474 52, 490 46 C 506 52, 508 74, 490 88 Z" fill="var(--vc-paper-surface)" stroke="var(--vc-moss)" stroke-width="2"></path>
          <path d="M630 88 C 612 74, 614 52, 630 46 C 646 52, 648 74, 630 88 Z" fill="var(--vc-moss)"></path>
          <circle cx="770" cy="88" r="5" fill="var(--vc-moss)"></circle>
          <path d="M910 88 C 892 74, 894 52, 910 46 C 926 52, 928 74, 910 88 Z" fill="var(--vc-moss)"></path>
        </svg>
        <figcaption class="vc-type-body vc-sub">{{c.branchCap}}</figcaption>
      </figure>
    </section>

    <section id="start" class="vc-container vc-section" aria-labelledby="bo-start-title">
      <div class="vc-head">
        <h2 id="bo-start-title" class="vc-type-title-2">{{c.firstTitle}}</h2>
        <p class="vc-type-body">{{c.firstLead}}</p>
      </div>
      <div class="vc-bodypage-start" role="group" aria-label="{{c.startGroup}}">
        <a class="opt" href="{{c.googleHref}}">{{c.google}}</a>
        <a class="vc-quick" href="{{c.emailHref}}">{{c.email}}</a>
      </div>
    </section>
  </main>
''' + indent(FOOTER, 2) + '''
</div>
</x-dc>
'''
P = {k: PROPS[k] for k in ('theme', 'lang', 'nav')}
P['startMenu'] = {"editor": "enum", "options": ["收起", "展开"], "default": "收起"}
P['$preview'] = {'width': 1440, 'height': 2700}
SCRIPT = '''<script type="text/x-dc" data-dc-script data-props='%s'>
%s
/* ── 站稳页的文案和数据（参考画板：这一页由 Veli 仓库实现）。地址：/body（英文 /en/body）；「开始训练」主按钮直达 /app，鼠标停留或键盘聚焦时原地展开 /auth/google、用邮箱开始（/app）和扫码（编本页 /body）；这一页的去处和码都沿用当前页的 utm_source，没有时去处回落 velicoach、码回落 velicoach_qr（veliHref(path, pageSource())，PRD 第 528 版 F10）；英文页的码编 /en/body；点阵是示意，实现时按 codeTarget 生成并扫码核对；Apple 等 Veli B2 再加（#164） ── */
const COPY = %s;
const LISTS = %s;
class Component extends DCLogic {
  componentDidMount() {
    if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el));
    // 展开层打开时，Esc 在页面任何位置都能关上；焦点在展开层里时回到「开始训练」，这一次聚焦不再展开（重新聚焦或重新悬停才展开）
    this.onKey = (e) => {
      if (e.key !== 'Escape' || !this.isOpen()) return;
      const a = document.activeElement, btn = document.querySelector('.vc-bodypage-start-anchor > .btn');
      clearTimeout(this.timer);
      this.setState({ open: false });
      if (btn && a && a !== btn && a.closest && a.closest('.vc-pop-anchor')) { this.skipFocusOpen = true; btn.focus(); }
    };
    this.onOutside = (e) => { if (this.isOpen() && !(e.target.closest && e.target.closest('.vc-pop-anchor'))) this.setState({ open: false }); };
    document.addEventListener('keydown', this.onKey);
    document.addEventListener('pointerdown', this.onOutside);
  }
  componentWillUnmount() { clearTimeout(this.timer); document.removeEventListener('keydown', this.onKey); document.removeEventListener('pointerdown', this.onOutside); }
  hoverIntent() { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--delay-hover-intent')) || 0; }
  isOpen() { return this.state && this.state.open !== undefined ? this.state.open : (this.props.startMenu ?? '收起') === '展开'; }
  renderVals() {
    const v = shellVals(this, 'paper', '/body');
    const k = v.en ? 'en' : 'zh';
    const src = pageSource();
    const open = this.isOpen();
    return {
      ...v, c: { ...COPY[k], appHref: veliHref('/app', src), googleHref: veliHref('/auth/google', src), emailHref: veliHref('/app', src) }, ...LISTS[k],
      t: { ...v.t, bodyHref: veliHref(v.en ? '/en/body' : '/body', src) }, codeTarget: 'https://velicoach.com' + veliHref(v.en ? '/en/body' : '/body', src || 'velicoach_qr'),
      startExpanded: open ? 'true' : 'false', popClass: open ? 'vc-pop vc-pop-code' : 'vc-pop vc-pop-code is-closed',
      openStart: () => { clearTimeout(this.timer); this.timer = setTimeout(() => this.setState({ open: true }), this.hoverIntent()); },
      focusStart: () => { if (this.skipFocusOpen) { this.skipFocusOpen = false; return; } clearTimeout(this.timer); this.timer = setTimeout(() => this.setState({ open: true }), this.hoverIntent()); },
      closeLater: () => { clearTimeout(this.timer); this.timer = setTimeout(() => this.setState({ open: false }), 300); },
    };
  }
}
</script>
</body>
</html>
''' % (json.dumps(P, ensure_ascii=False, separators=(',', ':')), SHELL_JS, js(T), js(L))
open(U + '/boards/Body.dc.html', 'w', encoding='utf-8').write(HEAD % ('站稳 · 和威利一起练 · Velicoach', CSS) + BODY + SCRIPT)
print('ok', sorted(T['zh'].keys()))
