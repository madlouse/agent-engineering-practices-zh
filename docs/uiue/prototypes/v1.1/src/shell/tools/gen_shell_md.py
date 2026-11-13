#!/usr/bin/env python3
"""由验证页 ShellTest.dc.html 生成 shell.md，片段和验证过的那一页逐字相同。用法：gen_shell_md.py <ShellTest.dc.html> <shell.md>"""
import sys, re
src = open(sys.argv[1], encoding='utf-8').read()
def cut(a, b, inc_b=True):
    i = src.index(a); j = src.index(b, i) + (len(b) if inc_b else 0)
    return src[i:j].rstrip()
def dedent(t, n=2):
    return '\n'.join(l[n:] if l.startswith(' ' * n) else l for l in t.split('\n'))
nav = dedent(cut('  <div class="vc-nav-wrap">', '    </header>\n  </div>'))
slot = dedent(cut('        <div class="vc-subbar-slot">', '          </sc-if>\n        </div>'), 8)
sub = dedent(cut('  <sc-if value="{{subOn}}"', '    </section>\n  </sc-if>'))
foot = dedent(cut('  <footer class="vc-footer vc-container">', '  </footer>'))
shell_js = cut('/* ── 外壳：文案和取值', "\nconst COPY", False).rstrip()
props = re.search(r"data-props='([^']+)'", src).group(1)

md = f'''# 外壳的标准片段（v1.1 · 2026-11-12）

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
body{{margin:0}}
/* 默认只有上面这一行。真的只属于这一页的版式才写在这里，类名 vc-<页名>page-…，并写明为什么不共享；两块以上画板用到的并进 canvas.head.css */
</style>
</helmet>
<div class="vc-page" data-theme="{{{{themeAttr}}}}" lang="{{{{langAttr}}}}">
  <!-- ① 导航（第 3 节），必须是 .vc-page 的直接子元素 -->
  <!-- ② 首屏：分站用色带 <section class="vc-band vc-band-ink|vc-band-moss|vc-band-paper" data-first-screen=""> 里面放 <div class="vc-container vc-band-body">；文章这类阅读页没有色带，用 <main class="vc-container vc-read"> -->
  <!-- ③ 内容：<main class="vc-container vc-section"> 或几个 <section class="vc-container vc-section"> -->
  <!-- ④ 页底订阅（第 5 节），开关关着时不渲染 -->
  <!-- ⑤ 页脚（第 6 节），放在最后：verify 把最后一个 <footer> 以下的主按钮算作被挡住 -->
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='…见第 2 节…'>
/* SHELL 和 shellVals() 原样照抄（第 2 节），再写这一页自己的 COPY */
class Component extends DCLogic {{
  renderVals() {{
    const v = shellVals(this, 'ink', '/mind');   // 这页在首屏用哪种实色导航：'paper' | 'ink' | 'moss'；这一页的中文地址（语言切换链到本页的另一语言版本）
    return {{ ...v, c: COPY[v.en ? 'en' : 'zh'] }};   // 页面自己的文案放在 c 下，模板里写 {{{{c.xxx}}}}；外壳的在 t 下
  }}
  componentDidMount() {{ if (window.LiquidGlass) document.querySelectorAll('.lg[data-lens]').forEach((el) => window.LiquidGlass.attachLens(el)); }}
}}
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
{props}
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
{shell_js}
```

`shellVals(self, station, path)` 的第三个参数是这一页的中文地址：首页 `'/'`，看清 `'/mind'`，学习路径 `'/mind/learn'`，文章 `'/mind/<slug>'`，关于 `'/about'`，动手 `'/build'`，项目页 `'/build/<项目>'`，站稳 `'/body'`；页面状态这块画板写 `'/'`。英文地址是前面加 `/en`（首页 `/en/`）。

`shellVals()` 给模板的值：`t`（外壳文案）、`en`、`langAttr`、`zhHref` `enHref` `otherHref`（本页两种语言的地址，导航和页脚的语言控件用）、`themeAttr`、`navClass`、语言和外观控件的 `zhOn` `enOn`（也用在窄屏语言按钮两个字的 `data-on` 上）`themeAuto` `themeLight` `themeDark` 和各自的处理函数、订阅的 `subOn` `rssRow` `barClosed` `barOpen` `barDone` `formShown` `subButton` `subBusy` `subHasError` `subError` `subInvalid` `subValue` `openSub` `closeSub`。

## 3. 导航

```html
{nav}
```

- `navClass` 在首屏是 `vc-nav vc-nav-paper`、`vc-nav vc-nav-ink` 或 `vc-nav vc-nav-moss`（看这页首屏的底色），吸顶时是 `vc-nav lg`，吸顶时压在视频画面上再加 `lg-on-dark`（浅色字，和播放条一样）。`data-backdrop="scroll"` 一直写着，只有带 `lg` 时起作用；导航不写 `data-lens`（吸顶条不挂透镜）。实色换玻璃的时刻：首屏色带的底边滚过导航下沿时（没有色带的页面是标题区的底边），过渡用 `duration-base`、`ease-out`，样式表已经写好。
- 当前所在的站在对应的 `vc-nav-link` 上写 `aria-current="page"`（上面的例子是看清）；首页、关于、页面状态三个都不写。
- 首页的导航和别的页面一样居中，首屏倾斜时不动（它是全站唯一的固定参照）。
- 窄屏的收法样式表已经写好：< 744 只留叶子；< 360 语言分段控件换成 `.vc-lang-one`。两个语言控件都保留在标记里。
- 色带顶上给导航留位置：`.vc-band` 自带上内边距；不用 `.vc-band` 的首屏自己留 `calc(var(--nav-height) + var(--vc-nav-top) + …)`。

## 4. 订阅条和 RSS 行（首页首屏底部）

```html
{slot}
```

- 槽位 `.vc-subbar-slot` 高度固定（桌面、平板 52px，手机 72px），条贴底、向上长。宿主在槽位上方留出约 128px（手机约 150px），展开的条不压标题、主按钮和快捷入口。
- 开关关着时槽位里只有 RSS 行；它和收起的订阅条同高，版面不跳。
- 首页桌面版式上槽位跟着接缝走，和导航同一个变量。

## 5. 页底订阅

```html
{sub}
```

## 6. 页脚

```html
{foot}
```

## 7. 分段控件

- 语言、外观：`<div class="seg" role="group" aria-label="…">`，里面是 `<a aria-current="true|false">` 或 `<button aria-pressed="true|false">`。13px。
- 内容线（看清首页、学习路径页的「AI 发展史 | 人机协作」）：加 `vc-seg-tabs`，两项用 `<a>`（地址跟着变），选中的写 `aria-current="page"`：

```html
<div class="vc-band-switch">
  <div class="seg vc-seg-tabs" role="group" aria-label="{{{{c.linesLabel}}}}">
    <a href="{{{{c.histHref}}}}" aria-current="page">{{{{c.hist}}}}</a>
    <a href="{{{{c.collabHref}}}}">{{{{c.collab}}}}</a>
  </div>
  <a class="vc-quick" href="{{{{c.learnHref}}}}">{{{{c.learn}}}}</a>
</div>
```

  手机上它自动整宽、两项等分，最长的语言一行放不下时折两行。学习路径页上「AI 发展史」一段高亮（`aria-current="true"`，因为当前页不是它本身）。
'''
open(sys.argv[2], 'w', encoding='utf-8').write(md)
