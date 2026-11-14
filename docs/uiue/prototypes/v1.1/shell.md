# 外壳的标准片段（v1.1 · 2026-11-12）

给做页面画板的人：导航、订阅条、RSS 行、页底订阅、页脚、分段控件每页都是同一份，**原样照抄下面的片段**（生成脚本直接从这份文件里取），不要在自己的 `<helmet>` 里重写它们的样式。全部画板只有一份样式：共享样式表 `canvas.css`（来源 `canvas.head.css`），每个组件上方有一行注释写用法和必须的子结构；样张在画板 `Controls.dc.html`。这些片段在 320、390、744、820、1180、1440 六个宽度和浅色、深色、伪语言（文字加长 35%）下跑过 `verify_canvas.py`，结论 `done`。

## 1. 页面画板的骨架

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>看清 · Velicoach</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="/_blob/2d0ccacf7377c5a050e285f270f25ffd">
<script src="/_blob/26c007f478ecf5fa646eda60cbc23992"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{margin:0}
/* 默认只有上面这一行。真的只属于这一页的版式才写在这里，类名 vc-<页名>page-…，并写明为什么不共享；两块以上画板用到的并进 canvas.head.css */
</style>
</helmet>
<div class="vc-page" data-theme="{{themeAttr}}" lang="{{langAttr}}">
  <!-- ① 导航（第 3 节），必须是 .vc-page 的直接子元素 -->
  <!-- ② 首屏：分站用色带 <section class="vc-band vc-band-ink|vc-band-moss|vc-band-paper" data-first-screen=""> 里面放 <div class="vc-container vc-band-body">；文章这类阅读页没有色带，用 <main class="vc-container vc-read"> -->
  <!-- ③ 内容：<main class="vc-container vc-section"> 或几个 <section class="vc-container vc-section"> -->
  <!-- ④ 页底订阅（第 5 节），开关关着时不渲染 -->
  <!-- ⑤ 页脚（第 6 节），放在最后：verify 把最后一个 <footer> 以下的主按钮算作被挡住 -->
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='…见第 2 节…'>
/* SHELL 和 shellVals() 原样照抄（第 2 节），再写这一页自己的 COPY */
class Component extends DCLogic {
  renderVals() {
    const v = shellVals(this, 'ink', '/mind');   // 这页在首屏用哪种实色导航：'paper' | 'ink' | 'moss'；这一页的中文地址（语言切换链到本页的另一语言版本）
    return { ...v, c: COPY[v.en ? 'en' : 'zh'] };   // 页面自己的文案放在 c 下，模板里写 {{c.xxx}}；外壳的在 t 下
  }
  componentDidMount() { if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }
}
</script>
</body>
</html>
```

要点：

- `<head>` 里的两行引用（样式表、液态玻璃脚本）保持这两个 `/_blob/…` 地址，主会话发布时统一换。不放 Google Fonts 的 `<link>`。
- 根节点 `.vc-page` 不写宽度和高度（样式表里是 `width: 100%`），画板在 `canvas.json` 里标 `"expand": "fill"`。页面里不用 `position: fixed`，吸顶用 `sticky`。
- 一份标记三档宽度：手机 < 744、平板 744–1179、桌面 ≥ 1180。媒体查询里断点写死 `743px`、`1179px`、`359px`，并注明来自 `breakpoint-tablet`、`breakpoint-desktop`、`breakpoint-nav-compact`。
- 字号只用 `vc-type-*` 类或 `var(--type-*)`，间距只用 `var(--space-*)`，颜色只用 `var(--vc-*)`。随底色变的地方用别名 `--vc-sub`（次要文字）、`--vc-faint`（辅助文字）、`--vc-line`（分隔线）、`--vc-accent`（强调色），放进墨底、苔绿底会自动换。
- 内容容器只用 `.vc-container`；首页首屏的两半用 `.vc-half-start`、`.vc-half-end`（或变量 `--vc-edge`、`--gutter`）对到同一条栅格。
- 对 Agent 友好（简报第 8 节）：每页一个 `h1`，区块 `h2`，条目 `h3`，不跳级；地标齐全（导航在 `<header>` 里，内容在 `<main>`，页脚 `<footer>`）；日期写成 `<time datetime="YYYY-MM-DD">`；整行可点的行用一个 `<a aria-labelledby="标题的 id">` 包住，读屏只读一次标题；分段控件的两段是两个地址；锚点用稳定的 slug；装饰性的 canvas 和 svg 加 `aria-hidden="true"`。
- 类名：块 `vc-xxx`，子元素 `vc-xxx-yyy`，状态 `is-xxx`。不带前缀的只有 `.btn`、`.opt`、`.icon-btn`、`.orb`、`.seg`、`.home`、`.mono`、`.kicker`、`.row-title`、`.lg*` 和 `.is-hover`、`.is-press`、`.is-focus`：它们是 `design-bar` 检查脚本和液态玻璃脚本的约定名，不能改。
- 共用组件的类和子结构看 `canvas.css` 每个组件上方的注释（第 5 节色带、第 6 节控件、第 9 节内容组件、9b 首页），标记照 `Controls.dc.html` 里的样张或已有的页面画板写。改完跑 `tools/audit_classes.py`：画板用到的类都要在样式表里，样式表里的类都要有画板用到。

## 2. 共用的属性和 `renderVals()`

`data-props`（没有订阅条的页面，`subscribe` 的选项去掉「收起」、默认「填写邮箱」；页面自己的属性加在后面）：

```
{"theme":{"editor":"enum","options":["自动","浅色","深色"],"default":"自动"},"lang":{"editor":"enum","options":["中文","English"],"default":"中文"},"subscribeGate":{"editor":"enum","options":["开","关"],"default":"开"},"subscribe":{"editor":"enum","options":["收起","填写邮箱","正在订阅","订阅成功","格式不对","提交太频繁","服务不可用"],"default":"收起"},"nav":{"editor":"enum","options":["首屏","吸顶"],"default":"首屏"},"$preview":{"width":1440,"height":1500}}
```

| 属性 | 选项 | 说明 |
| --- | --- | --- |
| `theme` | 自动 / 浅色 / 深色 | 默认自动：`data-theme=""`，跟随系统。页脚的外观分段控件改的是它 |
| `lang` | 中文 / English | 导航和页脚的语言控件改的是它 |
| `subscribeGate` | 开 / 关 | 订阅的上线开关。关：不渲染订阅条和页底订阅，订阅条的位置换成 RSS 行 |
| `subscribe` | 收起 / 填写邮箱 / 正在订阅 / 订阅成功 / 格式不对 / 提交太频繁 / 服务不可用 | 订阅条和页底订阅共用一个状态 |
| `nav` | 首屏 / 吸顶 | 首屏：实色导航；吸顶：滚过首屏后的玻璃导航 |

脚本里原样照抄（文案中英两版都在这里，英文按英语读者重写）：

```js
/* ── 外壳：文案和取值，每块页面画板原样照抄（shell.md）── */
/* 站点配置（PRD F23）：联系邮箱和隐私邮箱只从这里取，页面和邮件不写死；生产构建时任一项为空即构建失败 */
const SITE_CONFIG = { contactEmail: 'hello@velicoach.com', privacyEmail: 'privacy@velicoach.com', wordsUrl: '' };
const SHELL = {
  zh: {
    home: '/', homeLabel: 'Velicoach 首页', bodyHref: '/body', mindHref: '/mind', buildHref: '/build',
    navLabel: '三站', body: '站稳', mind: '看清', build: '动手',
    langLabel: '语言', langSwitch: '切换到英文，现在是中文', otherLang: 'en',
    subTitle: '订阅', subNote: '每周日一封：一读、一练、一个项目。可一键退订。', privacy: '隐私政策',
    subscribe: '订阅', subBusy: '正在订阅', subDone: '已订阅，每周日见', emailLabel: '邮箱', emailPh: '你的邮箱', collapse: '收起',
    subAction: '/api/site/subscribe', errFormat: '邮箱格式不对', errRate: '提交太频繁，请一小时后再试', errDown: '订阅暂时不可用，请稍后再试',
    rssRow: '用 RSS 订阅更新',
    footerLabel: '页脚', about: '关于', contact: '联系', copyright: '版权与转载', health: '健康数据政策', disclaimerLink: '健康免责', terms: '服务条款',
    aboutHref: '/about', contactHref: '/about#contact', copyrightHref: '/legal/copyright', privacyHref: '/legal/privacy', healthHref: '/data-usage', disclaimerHref: '/legal/health-disclaimer', termsHref: '/legal/terms', feedHref: '/feed.xml',
    appearance: '外观', auto: '自动', light: '浅色', dark: '深色',
    disclaimer: '威利不是医生。有伤病或疼痛，先停下来，问医生。',
  },
  en: {
    home: '/en/', homeLabel: 'Velicoach home', bodyHref: '/en/body', mindHref: '/en/mind', buildHref: '/en/build',
    navLabel: 'Stations', body: 'Body', mind: 'Mind', build: 'Build',
    langLabel: 'Language', langSwitch: 'Switch to Chinese, currently English', otherLang: 'zh-CN',
    subTitle: 'Newsletter', subNote: 'Every Sunday: one read, one workout, one project. One-click unsubscribe. ', privacy: 'Privacy policy',
    subscribe: 'Subscribe', subBusy: 'Subscribing', subDone: 'Subscribed. See you Sunday.', emailLabel: 'Email', emailPh: 'Your email', collapse: 'Close',
    subAction: '/api/site/subscribe', errFormat: 'That email doesn’t look right.', errRate: 'Too many tries. Try again in an hour.', errDown: 'Sign-up is down. Try again later.',
    rssRow: 'Follow updates by RSS',
    footerLabel: 'Footer', about: 'About', contact: 'Contact', copyright: 'Copyright and reuse', health: 'Health data policy', disclaimerLink: 'Health disclaimer', terms: 'Terms',
    aboutHref: '/en/about', contactHref: '/en/about#contact', copyrightHref: '/en/legal/copyright', privacyHref: '/en/legal/privacy', healthHref: '/en/data-usage', disclaimerHref: '/en/legal/health-disclaimer', termsHref: '/en/legal/terms', feedHref: '/en/feed.xml',
    appearance: 'Appearance', auto: 'Auto', light: 'Light', dark: 'Dark',
    disclaimer: 'Veli isn’t a doctor. If you’re injured or in pain, stop and see a doctor.',
  },
};
/* station：这页在首屏用哪种实色导航，'paper' | 'ink' | 'moss'。
   path：这一页的中文地址（'/'、'/mind'、'/mind/learn'……）；英文版在前面加 /en。语言切换链到本页的另一语言版本，不回首页 */
function shellVals(self, station, path) {
  const pick = (k, d) => (self.state && self.state[k]) ?? self.props[k] ?? d;
  const en = pick('lang', '中文') === 'English';
  const theme = pick('theme', '自动');
  const gate = pick('subscribeGate', '开') === '开';
  const sub = pick('subscribe', '收起');
  const t = SHELL[en ? 'en' : 'zh'];
  const err = { '格式不对': t.errFormat, '提交太频繁': t.errRate, '服务不可用': t.errDown }[sub] || '';
  const zhHref = path, enHref = path === '/' ? '/en/' : '/en' + path;
  const done = sub === '订阅成功';
  const busy = sub === '正在订阅';
  return {
    t, en, langAttr: en ? 'en' : 'zh-CN',
    site: SITE_CONFIG, contactMail: 'mailto:' + SITE_CONFIG.contactEmail, privacyMail: 'mailto:' + SITE_CONFIG.privacyEmail,
    zhHref, enHref, otherHref: en ? zhHref : enHref,
    zhOn: en ? 'false' : 'true', enOn: en ? 'true' : 'false',
    setZh: (e) => { e.preventDefault(); self.setState({ lang: '中文' }); }, setEn: (e) => { e.preventDefault(); self.setState({ lang: 'English' }); },
    toggleLang: (e) => { e.preventDefault(); self.setState({ lang: en ? '中文' : 'English' }); },
    themeAttr: theme === '深色' ? 'dark' : theme === '浅色' ? 'light' : '',
    themeAuto: theme === '自动' ? 'true' : 'false', themeLight: theme === '浅色' ? 'true' : 'false', themeDark: theme === '深色' ? 'true' : 'false',
    setAuto: () => self.setState({ theme: '自动' }), setLight: () => self.setState({ theme: '浅色' }), setDark: () => self.setState({ theme: '深色' }),
    navClass: pick('nav', '首屏') === '吸顶' ? 'vc-nav lg' : 'vc-nav vc-nav-' + station,
    subOn: gate, rssRow: !gate,
    barClosed: gate && sub === '收起', barOpen: gate && sub !== '收起' && !done, barDone: gate && done, formShown: !done,
    openSub: () => self.setState({ subscribe: '填写邮箱' }), closeSub: () => self.setState({ subscribe: '收起' }),
    subButton: busy ? t.subBusy : t.subscribe, subBusy: busy ? 'true' : 'false',
    subHasError: !!err, subError: err, subInvalid: err ? 'true' : 'false',
    subValue: sub === '格式不对' ? 'name@' : (busy || err) ? 'name@example.com' : '',
  };
}
```

`shellVals(self, station, path)` 的第三个参数是这一页的中文地址：首页 `'/'`，看清 `'/mind'`，学习路径 `'/mind/learn'`，文章 `'/mind/<slug>'`，关于 `'/about'`，动手 `'/build'`，项目页 `'/build/<项目>'`，站稳 `'/body'`；页面状态这块画板写 `'/'`。英文地址是前面加 `/en`（首页 `/en/`）。

`shellVals()` 给模板的值：`t`（外壳文案）、`en`、`langAttr`、`zhHref` `enHref` `otherHref`（本页两种语言的地址，导航和页脚的语言控件用）、`themeAttr`、`navClass`、语言和外观控件的 `zhOn` `enOn`（也用在窄屏语言按钮两个字的 `data-on` 上）`themeAuto` `themeLight` `themeDark` 和各自的处理函数、订阅的 `subOn` `rssRow` `barClosed` `barOpen` `barDone` `formShown` `subButton` `subBusy` `subHasError` `subError` `subInvalid` `subValue` `openSub` `closeSub`。

## 3. 导航

```html
<div class="vc-nav-wrap">
  <header class="{{navClass}}" data-backdrop="scroll">
    <a class="home" href="{{t.home}}" aria-label="{{t.homeLabel}}">
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><g transform="rotate(45 12 12)"><path class="vc-leaf-body" d="M12 1.5 C 18.5 6.5, 18.5 17.5, 12 22.5 C 5.5 17.5, 5.5 6.5, 12 1.5 Z"></path><path class="vc-leaf-vein" d="M12 19.5 L 9.3 7.5 M12 19.5 L 14.7 7.5" fill="none" stroke-width="1.6" stroke-linecap="round"></path></g></svg>
      <span class="vc-wordmark">Velicoach</span>
    </a>
    <nav class="vc-nav-links" aria-label="{{t.navLabel}}">
      <a class="vc-nav-link" href="{{t.bodyHref}}">{{t.body}}</a>
      <a class="vc-nav-link" href="{{t.mindHref}}" aria-current="page">{{t.mind}}</a>
      <a class="vc-nav-link" href="{{t.buildHref}}">{{t.build}}</a>
    </nav>
    <div class="seg vc-nav-lang" role="group" aria-label="{{t.langLabel}}">
      <a href="{{zhHref}}" lang="zh-CN" hreflang="zh-CN" aria-current="{{zhOn}}" onClick="{{setZh}}">中文</a>
      <a href="{{enHref}}" lang="en" hreflang="en" aria-current="{{enOn}}" onClick="{{setEn}}">EN</a>
    </div>
    <a class="vc-lang-one" href="{{otherHref}}" hreflang="{{t.otherLang}}" aria-label="{{t.langSwitch}}" onClick="{{toggleLang}}"><span lang="zh-CN" data-on="{{zhOn}}">中</span><span aria-hidden="true">/</span><span lang="en" data-on="{{enOn}}">EN</span></a>
  </header>
</div>
```

- `navClass` 在首屏是 `vc-nav vc-nav-paper`、`vc-nav vc-nav-ink` 或 `vc-nav vc-nav-moss`（看这页首屏的底色），吸顶时是 `vc-nav lg`，吸顶时压在视频画面上再加 `is-over-video`（浓的一档，胶囊下垫一层墨色），浅色主题另加 `lg-on-dark`（浅色字，和播放条一样；深色主题本来是浅色字，不加）。`data-backdrop="scroll"` 一直写着，只有带 `lg` 时起作用；导航不写 `data-lens`（吸顶条不挂透镜）。实色换玻璃的时刻：首屏色带的底边滚过导航下沿时（没有色带的页面是标题区的底边），过渡用 `duration-base`、`ease-out`，样式表已经写好。
- 当前所在的站在对应的 `vc-nav-link` 上写 `aria-current="page"`（上面的例子是看清）；首页、关于、页面状态三个都不写。
- 首页的导航和别的页面一样居中，首屏倾斜时不动（它是全站唯一的固定参照）。
- 窄屏的收法样式表已经写好：< 744 只留叶子；< 360 语言分段控件换成 `.vc-lang-one`。两个语言控件都保留在标记里。
- 色带顶上给导航留位置：`.vc-band` 自带上内边距；不用 `.vc-band` 的首屏自己留 `calc(var(--nav-height) + var(--vc-nav-top) + …)`。

## 4. 订阅条和 RSS 行（首页首屏底部）

```html
<div class="vc-subbar-slot">
  <sc-if value="{{rssRow}}" hint-placeholder-val="{{ false }}">
    <a class="vc-rss-row vc-surface-solid" href="{{t.feedHref}}">
      <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M3 3 a10 10 0 0 1 10 10 M3 7.5 a5.5 5.5 0 0 1 5.5 5.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path><circle cx="3.6" cy="12.4" r="1.3" fill="currentColor"></circle></svg>
      <span>{{t.rssRow}}</span>
    </a>
  </sc-if>
  <sc-if value="{{barClosed}}" hint-placeholder-val="{{ true }}">
    <div class="vc-subbar vc-surface-solid">
      <p class="vc-sub-note">{{t.subNote}}<a href="{{t.privacyHref}}">{{t.privacy}}</a></p>
      <button type="button" class="btn vc-btn-quiet" aria-expanded="false" aria-controls="vc-subbar-form" onClick="{{openSub}}">{{t.subscribe}}</button>
    </div>
  </sc-if>
  <sc-if value="{{barOpen}}" hint-placeholder-val="{{ false }}">
    <div class="vc-subbar vc-surface-solid is-open">
      <p class="vc-sub-note">{{t.subNote}}<a href="{{t.privacyHref}}">{{t.privacy}}</a></p>
      <button type="button" class="icon-btn" aria-expanded="true" aria-controls="vc-subbar-form" aria-label="{{t.collapse}}" onClick="{{closeSub}}"><svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M3.5 3.5 L12.5 12.5 M12.5 3.5 L3.5 12.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"></path></svg></button>
      <form id="vc-subbar-form" class="vc-sub-form" action="{{t.subAction}}" method="post" novalidate>
        <label class="vc-sr-only" for="vc-subbar-email">{{t.emailLabel}}</label>
        <input id="vc-subbar-email" class="vc-field" type="email" name="email" autocomplete="email" placeholder="{{t.emailPh}}" value="{{subValue}}" aria-invalid="{{subInvalid}}" aria-describedby="vc-subbar-error">
        <button type="submit" class="btn vc-btn-quiet" aria-disabled="{{subBusy}}">{{subButton}}</button>
        <sc-if value="{{subHasError}}" hint-placeholder-val="{{ false }}">
          <p id="vc-subbar-error" class="vc-error" role="alert">{{subError}}</p>
        </sc-if>
      </form>
    </div>
  </sc-if>
  <sc-if value="{{barDone}}" hint-placeholder-val="{{ false }}">
    <div class="vc-subbar vc-surface-solid is-done">
      <p class="vc-sub-done" role="status"><svg class="vc-sub-leaf" viewBox="0 0 24 24" aria-hidden="true"><g transform="rotate(45 12 12)"><path class="vc-leaf-body" d="M12 1.5 C 18.5 6.5, 18.5 17.5, 12 22.5 C 5.5 17.5, 5.5 6.5, 12 1.5 Z"></path><path class="vc-leaf-vein" pathLength="1" d="M12 19.5 L 9.3 7.5" fill="none" stroke-width="1.6" stroke-linecap="round"></path><path class="vc-leaf-vein" pathLength="1" d="M12 19.5 L 14.7 7.5" fill="none" stroke-width="1.6" stroke-linecap="round"></path></g></svg><span>{{t.subDone}}</span></p>
    </div>
  </sc-if>
</div>
```

- 槽位 `.vc-subbar-slot` 高度固定（桌面、平板 52px，手机 72px），条贴底、向上长。宿主在槽位上方留出约 128px（手机约 150px），展开的条不压标题、主按钮和快捷入口。
- 开关关着时槽位里只有 RSS 行；它和收起的订阅条同高，版面不跳。
- 首页桌面版式上槽位跟着接缝走，和导航同一个变量。

## 5. 页底订阅

```html
<sc-if value="{{subOn}}" hint-placeholder-val="{{ true }}">
  <section class="vc-subscribe vc-container" aria-labelledby="vc-sub-title">
    <div class="vc-subscribe-text">
      <h2 id="vc-sub-title" class="vc-type-title-3">{{t.subTitle}}</h2>
      <p class="vc-sub-note">{{t.subNote}}<a href="{{t.privacyHref}}">{{t.privacy}}</a></p>
    </div>
    <sc-if value="{{formShown}}" hint-placeholder-val="{{ true }}">
      <form class="vc-sub-form" action="{{t.subAction}}" method="post" novalidate>
        <label class="vc-sr-only" for="vc-sub-email">{{t.emailLabel}}</label>
        <input id="vc-sub-email" class="vc-field" type="email" name="email" autocomplete="email" placeholder="{{t.emailPh}}" value="{{subValue}}" aria-invalid="{{subInvalid}}" aria-describedby="vc-sub-error">
        <button type="submit" class="btn vc-btn-action" aria-disabled="{{subBusy}}">{{subButton}}</button>
        <sc-if value="{{subHasError}}" hint-placeholder-val="{{ false }}">
          <p id="vc-sub-error" class="vc-error" role="alert">{{subError}}</p>
        </sc-if>
      </form>
    </sc-if>
    <sc-if value="{{barDone}}" hint-placeholder-val="{{ false }}">
      <p class="vc-sub-done" role="status"><svg class="vc-sub-leaf" viewBox="0 0 24 24" aria-hidden="true"><g transform="rotate(45 12 12)"><path class="vc-leaf-body" d="M12 1.5 C 18.5 6.5, 18.5 17.5, 12 22.5 C 5.5 17.5, 5.5 6.5, 12 1.5 Z"></path><path class="vc-leaf-vein" pathLength="1" d="M12 19.5 L 9.3 7.5" fill="none" stroke-width="1.6" stroke-linecap="round"></path><path class="vc-leaf-vein" pathLength="1" d="M12 19.5 L 14.7 7.5" fill="none" stroke-width="1.6" stroke-linecap="round"></path></g></svg><span>{{t.subDone}}</span></p>
    </sc-if>
  </section>
</sc-if>
```

## 6. 页脚

```html
<footer class="vc-footer vc-container">
  <nav class="vc-footer-links" aria-label="{{t.footerLabel}}">
    <a href="{{t.aboutHref}}">{{t.about}}</a>
    <a href="{{t.contactHref}}">{{t.contact}}</a>
    <a href="{{t.copyrightHref}}">{{t.copyright}}</a>
    <a href="{{t.privacyHref}}">{{t.privacy}}</a>
    <a href="{{t.healthHref}}">{{t.health}}</a>
    <a href="{{t.disclaimerHref}}">{{t.disclaimerLink}}</a>
    <a href="{{t.termsHref}}">{{t.terms}}</a>
    <a href="{{t.feedHref}}">RSS</a>
  </nav>
  <div class="vc-footer-tools">
    <div class="seg" role="group" aria-label="{{t.appearance}}">
      <button type="button" aria-pressed="{{themeAuto}}" onClick="{{setAuto}}">{{t.auto}}</button>
      <button type="button" aria-pressed="{{themeLight}}" onClick="{{setLight}}">{{t.light}}</button>
      <button type="button" aria-pressed="{{themeDark}}" onClick="{{setDark}}">{{t.dark}}</button>
    </div>
    <div class="seg" role="group" aria-label="{{t.langLabel}}">
      <a href="{{zhHref}}" lang="zh-CN" hreflang="zh-CN" aria-current="{{zhOn}}" onClick="{{setZh}}">中文</a>
      <a href="{{enHref}}" lang="en" hreflang="en" aria-current="{{enOn}}" onClick="{{setEn}}">EN</a>
    </div>
  </div>
  <p class="vc-footer-note">{{t.disclaimer}}</p>
</footer>
```

## 7. 分段控件

- 语言、外观：`<div class="seg" role="group" aria-label="…">`，里面是 `<a aria-current="true|false">` 或 `<button aria-pressed="true|false">`。13px。
- 内容线（看清首页、学习路径页的「AI 发展史 | 人机协作」）：加 `vc-seg-tabs`，两项用 `<a>`（地址跟着变），选中的写 `aria-current="page"`：

```html
<div class="vc-band-switch">
  <div class="seg vc-seg-tabs" role="group" aria-label="{{c.linesLabel}}">
    <a href="{{c.histHref}}" aria-current="page">{{c.hist}}</a>
    <a href="{{c.collabHref}}">{{c.collab}}</a>
  </div>
  <a class="vc-quick" href="{{c.learnHref}}">{{c.learn}}</a>
</div>
```

  手机上它自动整宽、两项等分，最长的语言一行放不下时折两行。学习路径页上「AI 发展史」一段高亮（`aria-current="true"`，因为当前页不是它本身）。
