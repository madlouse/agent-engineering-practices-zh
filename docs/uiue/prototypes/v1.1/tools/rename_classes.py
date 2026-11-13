#!/usr/bin/env python3
"""一次性的改名工具（合并 v1.1 样式时用过，留作记录）：把旧类名换成新类名。
用法：rename_classes.py <文件...>   原地改；打印每个文件改了几处。
三张表：
  WHOLE  不会和别的词撞的旧名：整词替换，哪里出现都换（class 属性、选择器、脚本里的字符串、说明文字）。
  ATTR   容易撞词的旧名（quick、field、art……）：只在 class="…" 的词里换，另换「.名字」形式的选择器。
  SPLIT  一个旧类拆成两个类（通用纸面卡片 vc-card 加组件自己的类）：只在 class 属性里换，样式表里不换。"""
import re, sys

WHOLE = {
    # 控件（verify_canvas.py 不按这些名字找元素，统一加前缀）
    'btn-action': 'vc-btn-action', 'btn-on-ink': 'vc-btn-on-ink', 'btn-on-moss': 'vc-btn-on-moss', 'btn-quiet': 'vc-btn-quiet',
    'navlink': 'vc-nav-link', 'msg-error': 'vc-error', 'surface-solid': 'vc-surface-solid', 'surface-ink': 'vc-surface-ink',
    'vc-type-kicker': 'kicker',
    # 看清、学习路径
    'mind-band': 'vc-band-body', 'learn-band': 'vc-band-body', 'about-band': 'vc-band-body', 'st-head': 'vc-band-body', 'pj-hero': 'vc-band-body',
    'mind-switch': 'vc-band-switch', 'learn-switch': 'vc-band-switch', 'st-tabs': 'vc-band-switch',
    'mind-ruler-bar': 'vc-ruler-bar', 'mind-ruler-seg': 'vc-ruler-seg', 'mind-ruler-dot': 'vc-ruler-dot', 'mind-ruler-years': 'vc-ruler-years',
    'mind-ruler-tail': 'vc-ruler-tail', 'mind-ruler-note': 'vc-ruler-note', 'mind-ruler': 'vc-ruler',
    'mind-nest-wrap': 'vc-nest', 'mind-nest-row': 'vc-nest-row', 'mind-nest-core': 'vc-nest-core', 'mind-nest': 'vc-nest-ring',
    'mind-intro': 'vc-intro', 'learn-intro': 'vc-intro',
    'mind-layer-head': 'vc-head', 'mind-layer': 'vc-layer',
    'mind-para-head': 'vc-paradigm-head', 'mind-para-n': 'vc-paradigm-when', 'mind-para-problem': 'vc-paradigm-problem', 'mind-para': 'vc-paradigm',
    'mind-cards': 'vc-card-grid', 'mind-card-facts': 'vc-card-facts', 'mind-era-jump': 'vc-era-jump',
    'learn-path-name': 'vc-path-name', 'learn-path-count': 'vc-path-count', 'learn-path': 'vc-path',
    # 文章、状态、关于
    'art-col': 'vc-read-col', 'art-wide': 'vc-read-wide', 'art-head': 'vc-read-head', 'art-body': 'vc-read-body',
    'art-meta-row': 'vc-meta-row', 'art-meta': 'vc-meta', 'art-take': 'vc-take',
    'art-video-fail': 'vc-notice-action', 'art-noen': 'vc-notice-action', 'art-video': 'vc-video', 'art-frame': 'vc-video-frame',
    'art-shot-title': 'vc-video-title', 'art-shot': 'vc-video-shot', 'art-scrim': 'vc-video-scrim',
    'art-playbar-label': 'vc-playbar-label', 'art-playbar-space': 'vc-playbar-space', 'art-playbar': 'vc-playbar', 'art-play': 'vc-playbar-play', 'art-cc': 'vc-playbar-cc',
    'art-fold': 'vc-fold', 'art-toc': 'vc-toc', 'art-transcript-open': 'vc-transcript-open', 'art-transcript': 'vc-transcript', 'art-nb': 'vc-nowrap',
    'art-go': 'vc-next-go', 'art-report': 'vc-colophon-report',
    'art-skel': 'vc-loading', 'art-slow': 'vc-loading-slow', 'art-fail-actions': 'vc-notice-actions', 'art-fail': 'vc-notice-block',
    'st-offline': 'vc-offline', 'st-band-offline': 'is-offline', 'st-skel-row': 'vc-loading-row', 'st-skel-body': 'vc-loading-row-body',
    'about-n': 'vc-deflist-n',
    # 动手、项目、站稳
    'bd-head': 'vc-head', 'pj-head': 'vc-head', 'bo-head': 'vc-head', 'vc-proof-head': 'vc-head',
    'bd-projects': 'vc-section-flush', 'bo-sec': 'vc-section-flush',
    'bd-how-title': 'vc-howto-title', 'bd-how': 'vc-howto', 'bd-steps': 'vc-howto-steps', 'bd-step-n': 'vc-howto-n', 'bd-step': 'vc-howto-step',
    'bd-top-side': 'vc-buildpage-side', 'bd-top': 'vc-buildpage-top', 'bd-part': 'vc-buildpage-part',
    'pj-facts': 'vc-facts', 'pj-roles': 'vc-deflist', 'pj-empty': 'vc-empty', 'pj-about-text': 'vc-projectpage-text', 'pj-about': 'vc-projectpage-about',
    'bo-hero-text': 'vc-bodypage-text', 'bo-hero': 'vc-bodypage-hero', 'bo-actions': 'vc-bodypage-actions', 'bo-direct': 'vc-bodypage-direct', 'bo-toggle': 'vc-bodypage-toggle',
    'bo-pop-closed': 'is-closed', 'bo-plan-list': 'vc-bodypage-plan-list', 'bo-plan-kind': 'vc-bodypage-plan-kind', 'bo-plan': 'vc-bodypage-plan',
    'bo-list': 'vc-bodypage-list', 'bo-branch': 'vc-bodypage-branch', 'bo-start': 'vc-bodypage-start',
    # 控件样张（只有 Controls 一页）
    'sheet-scroll': 'vc-sheet-scroll', 'sample-wide': 'vc-sheet-sample-wide', 'sample-label': 'vc-sheet-label', 'type-row': 'vc-sheet-type',
}
ATTR = {
    'quick': 'vc-quick', 'field': 'vc-field', 'notice': 'vc-notice', 'skeleton': 'vc-skeleton', 'on-dark': 'vc-on-dark',
    'art': 'vc-read', 'about': 'vc-read',
    'sheet': 'vc-sheet', 'samples': 'vc-sheet-samples', 'sample': 'vc-sheet-sample', 'swatch': 'vc-sheet-swatch', 'na': 'vc-sheet-na',
}
SPLIT = {
    'mind-card': 'vc-card vc-card-link', 'vc-study': 'vc-card vc-study', 'vc-project': 'vc-card vc-project', 'bo-card': 'vc-card vc-bodypage-card',
    'art-practice': 'vc-part vc-part-rule vc-practice', 'art-next': 'vc-part vc-next', 'art-colophon': 'vc-part vc-colophon',
    'about-keep': 'vc-part vc-part-rule', 'about-contact': 'vc-part vc-contact', 'about-start': 'vc-part vc-next',
    'about-four': 'vc-deflist vc-deflist-numbered', 'st-skel': 'vc-loading vc-loading-rows',
}
DROP = {'mind-aside', 'st-slow', 'st-fail', 'video-frame'}   # 并进别的规则以后不再需要的类

BOUND_L, BOUND_R = r'(?<![\w-])', r'(?![\w-])'
whole_re = re.compile(BOUND_L + '(' + '|'.join(sorted(map(re.escape, WHOLE), key=len, reverse=True)) + ')' + BOUND_R)
dot_re = re.compile(r'(?<![\w}\]])\.(' + '|'.join(sorted(map(re.escape, ATTR), key=len, reverse=True)) + ')' + BOUND_R)

def attr(m):
    out = []
    for tok in m.group(2).split(' '):
        if tok in DROP: continue
        tok = SPLIT.get(tok, ATTR.get(tok, tok))
        for t in tok.split(' '):
            if t not in out or not t: out.append(t)
    return m.group(1) + ' '.join(out) + m.group(3)

def convert(text):
    n = [0]
    def cnt(f):
        def g(m):
            r = f(m)
            if r != m.group(0): n[0] += 1
            return r
        return g
    text = whole_re.sub(cnt(lambda m: WHOLE[m.group(1)]), text)
    text = re.sub(r'(class=\\?["\'])([^"\'\\]*)(\\?["\'])', cnt(attr), text)
    text = dot_re.sub(cnt(lambda m: '.' + ATTR[m.group(1)]), text)
    return text, n[0]

if __name__ == '__main__':
    for p in sys.argv[1:]:
        src = open(p, encoding='utf-8').read()
        out, n = convert(src)
        if out != src: open(p, 'w', encoding='utf-8').write(out)
        print(f'{p}: {n} 处')
