#!/usr/bin/env python3
"""画板验证：把 Claude Design 画布的每块画板、每个状态，按浅色和深色各渲染一次，只报真问题，最后给结论。

和 check_page.py 的分工：check_page 看真实页面（多宽度、响应式）；本脚本看固定尺寸的画板（390×844 之类），
所以不会把「画板比 375 宽」当成溢出，也不会把画板里有意写的内联样式当成问题。

检查项（都是会让用户看错、点不到、看不清的问题，不报审美意见）：
  1. 主按钮被挡住：宽度 ≥ 画板 60%、高度 ≥ 44 的实色按钮，底边落在底部输入区或画板外
  2. 文字被挤成竖排：一段文字的宽度不到两个字、高度却超过 2.5 行
  3. 内容超出画板：元素右边超出画板（画板会把它裁掉）
  4. 对比度：正文 < 4.5:1、大字 < 3:1（禁用态按钮除外；浅色、深色各查一次）
  5. 点按区域（A2）：独立成行的链接和按钮 < 44×44 报「触控目标小于 44」；任何可点元素短边 < 24 报更重的「点按区域小于 24」
     （WCAG 2.2 的 2.5.8 底线）。页脚、面包屑、整行链接都查。只放过一句话中间的行内链接（2.5.8 的行内例外）：在 p 里或 li > span 里，
     行内显示，不在 nav / header / footer 里，所在的块里链接以外还有 ≥ 12 个字；div、td 里的句中链接和 li > a 的行标题链接照报。
     伪元素或子元素把热区撑大的（::before / ::after、溢出盒子的子元素），按撑大后的量（2.5.8 量的是目标区域，不是文字盒）。
     撑大的部分要真的点得到，并且盖得住目标尺寸的方块：方块每条边取 9 点，全部要点到它或它的子元素；
     写了 pointer-events: none、被别的东西盖住、只伸出一条比目标尺寸窄的条、偏在一侧、缺一块、圆形或圆角 ≥ 2px、或取样点在视口外量不了的，照盒子量。
     量不出来的：两个取样点之间比间距窄的缝（44 下 5.4px、24 下 2.9px）；每个方向撑到超过 43px（23px）就算撑到；盒子和方块的边之间不取样
  6. 引用了没定义的 token：var(--x) 在样式表里找不到
  11. 展开层超出所在区块：aria-expanded 的控件用 aria-controls 指向的展开层，要完整留在所在 <section> 里
  12. 可点元素被盖住：链接、按钮、输入框的中心点上面压着别的控件或浮层
  13. 首屏主操作在视口外：第一个 <section> 里的按钮和表单，底边超出视口（配合 --size 查 1280×720 这类常见高度）；
      流式页面里第一个 <section> 从视口下半才开始的不算首屏（固定尺寸的画板不加这个条件）
  14. 深色下露出浅色底：主题只设在里层，画板比视口矮或有外边距时，外面露出浅色的 body
  15. 按钮文字折行：按钮里的字折成两行（伪语言那一遍最容易出现）
  16. 浮层没有出路：对话框、菜单里没有「关闭」按钮，画板逻辑也没处理 Esc
  17. 孤字成行：两行以上的标题和段落，最后一行只剩一个汉字或一个短词
  18. 词中断行：标题、按钮、标签这类 40 字以内的短文字里，中文词被拆到两行（Intl.Segmenter 分词）；
      西文词和紧跟的中文词被拆开（「AI / 发展史」，自动折行和手写 <br> 都算）也报；正文段落只查孤字
  19. 文字冲出容器、短标签被挤成多行：文字超出所在的圆角条或卡片；一行控件里三个词以内的标签折成三行以上
  21. 玻璃压在平涂底色上：用了 backdrop-filter 的元素，背后 5×3 网格的亮度极差 < 0.04（浅色那一遍，需要 Pillow）；
      背后是静态截图画不出来的动效、视频、滚动内容时，在元素或祖先上写 data-backdrop="motion|video|scroll"，这一项跳过
  22. 玻璃的背景声明不成立：data-backdrop="motion" 的元素要和一个 canvas（或 [data-motion] 区域）重叠；"video" 要和 video、
      [data-video]、.video-frame 重叠或在它里面；"scroll" 要它自己或祖先是 sticky / fixed。声明只是让 21 跳过，不成立就报。
      声明成立也只说明位置对得上，背后的内容会不会真的变，用 capture_motion.py --probe 量
  23. 可点元素没有悬停或按下样式：链接、按钮、带 role 的控件，样式表里找不到作用到它（或它里面、只包着它的外层）的
      :hover / .is-hover 和 :active / .is-press 规则；段落里的文字链接只要求悬停
  24. 展开挤动了版面：某个变体比同尺寸、同语言的第一个变体多展开了一个 aria-expanded 控件时，展开层以外的标题、按钮、
      链接、输入框位移超过 8px 就报（浅色那一遍）。展开就该把下面的列表推开的（折叠列表），在触发控件或祖先上写
      data-expand="inline" 跳过
  20. 标点在行首：中文的逗号、句号、顿号等落到一行开头
  25. 画板比视口宽：根节点写死的宽度超出视口（超出画板也按视口量）
  26. 首屏要读的字太多（C10「不用读就会用」）：标了 data-first-screen 的首屏区域里，标题、按钮、链接、导航、图（figure）、
      浮层以外要读的说明超过中文 80 字或英文 50 词（自定：约 5 秒扫完）
  28. 笼统的进度文字：看得见的文字只有「加载中」「处理中」「Loading…」这类词，没说在做什么
  27. 站标不回首页：导航里的站标（.brand、.home、aria-label 写着首页 / home 的链接）链到别处；回本页顶部另放控件
  29. 跨画板的内容左边缘不一致：同一视口宽度下，各画板第一个 h1（没有就取第一屏第一个标题）的左边缘相差 > 2px，列出每块的值；
      居中这类有意不对齐的标题在它或祖先上写 data-edge="free"
  30. 首屏空白带：入口页的第一屏（标了 data-first-screen 的区域，或流式页面的第一屏；固定尺寸的 App 界面不量）里，
      连续没有文字、控件、图片的横向空带高度 > 视口的 30%（canvas、video、[data-motion] 盖住的不算空；加载态的骨架也不算空：
      aria-busy="true" 的容器整块、[data-skeleton] 和类名带 skeleton 的占位块；
      只被动效画布盖住的另记一条提示：静态截图看不到它，要用 capture_motion.py 截出动效帧和兜底帧）
  31. 相邻两大块色面分不开：两块各占视口 ≥ 20%、彼此相邻（并排、上下相接或一块套一块）的平涂色面，对比 < 1.3:1（浅色、深色各查）。
      边界已经画出来的面算分开，不报：有一层看得见的柔和阴影（不透明度 > 0.1、模糊 > 0；全透明的不算），或者描边
      （边框、outline、没有模糊的 box-shadow 圈）和两块面里至少一块对比 ≥ 阈值（和面同色的描边不算）。1.3 是通用的下限；项目定了更高的门槛就用 --face-contrast 调高
  32. 字号种类过多：一块画板在基准视口下不同的字号 > 8 种，列出每种和用到的次数
  （提示）向第三方取字体：画板源码或运行时请求里出现 Google Fonts 这类第三方字体地址。不影响结论，理由写在报告里
  （另）颜色算不了：oklab()、color-mix() 这类写法画到画布上也取不到像素时报出来，不拿外层背景顶替
  按下和悬停：浅色那一遍另外把所有按钮、液态玻璃控件设成按下（.is-press）、悬停（.is-hover）各算一次对比度
  （另）占位文字：画板上出现「示例」「待定」「即将上线」「二维码」这类占位词（--placeholders 可改）
  7. 写死的颜色：画板源码里出现 #hex、rgb()、hsl()（token 文件除外）
  8. 页面报错：控制台 error、脚本异常（字体等网络资源加载失败只记为提示）
  9. 画出来就要能用（来自 baoyu-design「Accessible as drawn」）：<a> 没有 href、div/span 上挂点击、
     只有图标的按钮没有可读名称、输入框没有标签——静态稿也要用真的 <button> / <a href> / <label>
 10. 弹性布局吞掉空格：flex / grid 容器里的文字和元素挨着时，文字两头的空格会被吞掉（「还剩3天」）

另外列出「模板味信号」（来自 unslop 的信号清单里机器能看出的那部分：emoji、渐变文字、全大写加宽字距、
特粗标题、感叹号、按钮文字带句号、斜体强调、小字负字距、transition: all），只作提示，不影响结论；
要不要改按 unslop 的审计判断。

伪语言（--themes 里加 pseudo）：把每段文字加长 35%（PRD 常见的「德语比中文长 35%」口径），按浅色再查一遍
版式类问题（主按钮被挡或挤扁、竖排、超出画板、吞空格），看换语言以后会不会坏；对比度和 token 不在这一遍重复查。

属性和视口：data-props 里的枚举属性（theme 除外，主题由 --themes 管）每个非默认选项各查一遍，别的属性取默认，
报告里记作「lang=English」。每块画板实际查了哪些视口、尺寸从哪来，写在报告里每块画板的标题下面。
  基准视口：canvas.json 里的 w×h → 没有就读画板 data-props 的 $preview → 都没有时用 390×844 并在报告里写明「画板尺寸没找到」
            （这时给了 --size 就拿第一个 --size 当基准，不再按 390 宽跑）。
  流式页面（canvas.json 里带 expand，或没有 canvas.json、根节点不写死宽度且 $preview 比一屏高得多）：视口高度取一屏
            （宽 ≥ 1024 用 900，≥ 744 用 1180，其余 844），首屏类的检查才有意义；并自动在 390×844、320×568 下各再查一遍。
  根节点不写死宽度的手机画板（宽 < 744）自动加查 320×568。--no-auto-sizes 关掉自动加的视口。
  --size 名称=宽x高 再加一个视口（名称可以不带 .dc.html，写 * 表示全部画板）。
  说明文档类画板（组件表、旅程图）不查触控、首屏、空白带、色面、字号种类、左边缘。只有 canvas.json 里带 expand 的画板才可能算文档：
            根节点写了 data-board="doc"，或者没有 nav / main / footer / data-first-screen。固定尺寸的画板写了 data-board="doc" 也照查。
            按文档跳过的画板和原因列在报告开头。产品页面被误判时写 data-board="page"。

可配的阈值（都有同名的命令行参数）：
  --edge-tol 2          29 的左边缘容差（px）
  --empty-band 0.30     30 的空白带上限（占视口高度的比例）
  --face-area 0.20      31 一块色面至少占视口的比例
  --face-contrast 1.3   31 相邻色面的最低对比
  --tap-min 44          5 独立成行的可点元素的最小边长（px）
  --tap-floor 24        5 任何可点元素的最小边长（px）
  --max-font-sizes 8    32 一块画板里字号种类的上限

用法：
  python verify_canvas.py <画板目录或 .dc.html ...> --out <报告目录> [--themes light,dark,pseudo] [--only AI-Plans]
状态从 <sc-if value="{{ sN }}"> 自动发现。
结论：没有问题时 done（退出码 0），有问题时 needs_work（退出码 1）。需要 Python Playwright 和 Chromium。
"""
import argparse
import glob
import json
import math
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_dc import render_html, logic_values  # noqa: E402

PSEUDO_JS = r"""
() => {
  const root = document.querySelector('[data-theme]') || document.body;
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  for (const n of nodes) {
    const t = n.textContent; const core = t.trim();
    if (core.length < 2 || n.parentElement.closest('script, style, svg')) continue;
    const own = n.parentElement.closest('[lang]');
    if (own && own !== root && (own.getAttribute('lang') !== root.getAttribute('lang') || own.closest('button, .seg'))) continue;  // 语言切换按钮上的语言名不随翻译变长
    if (!/[A-Za-z\u4e00-\u9fff]/.test(core)) continue;  // 只有数字和符号（时间、页码）的不随翻译变长
    const extra = Math.ceil(core.length * 0.35);
    n.textContent = t.replace(core, core + core.repeat(2).slice(0, extra));
  }
}
"""

# 可配的阈值：命令行同名参数可改，帮助里列出
EDGE_TOL = 2            # 29：跨画板内容左边缘的容差（px）
EMPTY_BAND_MAX = 0.30   # 30：首屏空白带上限（占视口高度）
FACE_MIN_AREA = 0.20    # 31：一块色面至少占视口的比例
FACE_MIN_CONTRAST = 1.3  # 31：相邻色面的最低对比
TAP_MIN = 44            # 5：独立成行的可点元素
TAP_FLOOR = 24          # 5：任何可点元素（WCAG 2.2 2.5.8）
MAX_FONT_SIZES = 8      # 32：字号种类上限
PROSE_MIN_CHARS = 12    # 5：块里链接以外的字数达到它，行内链接才算「在一句话中间」


# 项目配置：项目自己的阈值（例如设计系统定了更严的色面对比）写在 design-bar.json 里，命令不带参数也生效；命令行参数优先。
# 查找：从命令行里给出的路径（画板目录、页面文件）往上，再从当前目录往上，每层看 design-bar.json 和 design/design-bar.json，到仓库根（有 .git）为止。
# 格式：{"thresholds": {"face-contrast": 1.8}}，键就是上面那些阈值的同名命令行参数（去掉 --）。--project-config <文件> 指定，--no-project-config 不读。
PROJECT_CONFIG_NAME = 'design-bar.json'
PROJECT_CONFIG_DEST_ALIASES = {'tap-min': 'min_target'}  # check_page.py 把同一个阈值叫 --min-target
PROJECT_CONFIG_LOOSER = {'edge-tol': (EDGE_TOL, '>'), 'empty-band': (EMPTY_BAND_MAX, '>'), 'face-area': (FACE_MIN_AREA, '>'), 'face-contrast': (FACE_MIN_CONTRAST, '<'),
                         'tap-min': (TAP_MIN, '<'), 'tap-floor': (TAP_FLOOR, '<'), 'max-font-sizes': (MAX_FONT_SIZES, '>')}  # why: 配置只许收紧，比通用下限松的值报错
PROJECT_CONFIG_KEYS = ('edge-tol', 'empty-band', 'face-area', 'face-contrast', 'tap-min', 'tap-floor', 'max-font-sizes')


def find_project_config(starts):
    for start in starts:
        d = os.path.abspath(start)
        if os.path.isfile(d):
            d = os.path.dirname(d)
        while True:
            for cand in (os.path.join(d, PROJECT_CONFIG_NAME), os.path.join(d, 'design', PROJECT_CONFIG_NAME)):
                if os.path.isfile(cand):
                    return cand
            if os.path.exists(os.path.join(d, '.git')) or os.path.dirname(d) == d:
                break
            d = os.path.dirname(d)
    return None


def add_project_config_args(ap):
    ap.add_argument('--project-config', metavar='FILE', help=f'项目配置文件（默认从给出的路径和当前目录往上找 {PROJECT_CONFIG_NAME}），里面的阈值作默认值，命令行参数优先')
    ap.add_argument('--no-project-config', action='store_true', help='不读项目配置（技能自测用）')


def apply_project_config(ap, argv):
    """把项目配置里的阈值设成 ap 的默认值（命令行参数仍然优先），返回读到的配置文件路径，没有则返回 None。"""
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument('--project-config')
    pre.add_argument('--no-project-config', action='store_true')
    known, _ = pre.parse_known_args(argv)
    if known.no_project_config:
        return None
    path = known.project_config or find_project_config([x for x in argv if not x.startswith('-') and os.path.exists(x)] + [os.getcwd()])
    if not path:
        return None
    try:
        th = json.load(open(path, encoding='utf-8'))['thresholds']
        assert isinstance(th, dict)
    except (OSError, ValueError, KeyError, AssertionError):
        sys.exit(f'{path}：项目配置要写成 {{"thresholds": {{"face-contrast": 1.8}}}}')
    bad = sorted(set(th) - set(PROJECT_CONFIG_KEYS))
    if bad:
        sys.exit(f'{path}：不认识的阈值 {"、".join(bad)}，可用：{"、".join(PROJECT_CONFIG_KEYS)}')
    for k, v in th.items():
        limit, loose = PROJECT_CONFIG_LOOSER[k]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
            sys.exit(f'{path}：{k} 是 {v}，要写成有限的数字')
        if (v > limit if loose == '>' else v < limit):
            sys.exit(f'{path}：{k} 是 {v}，通用下限是{"不超过" if loose == ">" else "不低于"} {limit:g}：项目配置只能收紧，放宽只能在命令行用参数临时调')
    actions = {act.dest: act for act in ap._actions}
    for k, v in th.items():
        dest = k.replace('-', '_')
        if dest not in actions:
            dest = PROJECT_CONFIG_DEST_ALIASES.get(k, dest)
        if dest in actions:  # 这个脚本没有的阈值（check_page.py 没有 --edge-tol）跳过
            ap.set_defaults(**{dest: actions[dest].type(v)})
    return path
FLUID_SIZES = [(390, 844), (320, 568)]  # 流式页面自动加查的窄视口
FONT_HOSTS = ('fonts.googleapis.com', 'fonts.gstatic.com', 'use.typekit.net', 'p.typekit.net', 'fonts.bunny.net', 'fast.fonts.net',
              'cloud.typography.com', 'use.fontawesome.com', 'fonts.cdnfonts.com', 'fonts.loli.net', 'fonts.font.im')
FIRST_SCREEN_TYPES = ('触控目标小于 44', '点按区域小于 24', '首屏主操作在视口外', '玻璃压在平涂底色上', '展开挤动了版面')  # 说明文档类画板不查


def fold_height(w):
    """流式页面的一屏有多高（和「首屏要读的字」用同一组数）。"""
    return 900 if w >= 1024 else 1180 if w >= 744 else 844


LAYOUT_TYPES = {'主按钮被挡住或在首屏外', '主按钮被挤扁', '文字被挤成竖排', '内容超出画板', '弹性布局吞掉了空格', '展开层超出所在区块', '可点元素被盖住', '首屏主操作在视口外', '按钮文字折行', '文字冲出容器', '短标签被挤成多行'}

STATE_JS = None  # 在 CHECK_JS 定义之后生成

CHECK_JS = r"""
() => {
  const issues = [];
  const O = window.__vcOpts || {};
  const TAP_MIN = O.tapMin || 44, TAP_FLOOR = O.tapFloor || 24, PROSE_MIN = O.proseMin || 12;
  const root = document.querySelector('[data-theme]') || document.body;
  const R0 = root.getBoundingClientRect(); const VW = document.documentElement.clientWidth;
  // 比的是视口，不是画板：画板写死了比视口还宽的宽度时，超出视口的部分用户看不到
  const R = {top: R0.top, left: R0.left, bottom: R0.bottom, height: R0.height, width: Math.min(R0.width, VW), right: Math.min(R0.right, VW)};
  const footers = [...root.querySelectorAll('footer')];
  const footer = footers.length ? footers[footers.length - 1] : null;
  const fTop = footer ? footer.getBoundingClientRect().top : R.bottom;
  const visible = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length > 0; };
  const name = el => ((el.getAttribute && el.getAttribute('aria-label')) || el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 36);
  // rgb() 直接读；oklab()、color-mix()、color(srgb …) 这类先画到 1×1 画布上取像素，算不了的记下来报错，不悄悄往外层找
  const __cv = document.createElement('canvas'); __cv.width = __cv.height = 1; const __cx = __cv.getContext('2d', { willReadFrequently: true });
  window.__vcUnparsed = window.__vcUnparsed || new Set();
  const toRGBA = c => {
    if (!c || c === 'transparent') return null;
    const m = c.match(/^rgba?\(([^)]+)\)$/);
    if (m) { const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(x => parseFloat(x)); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    __cx.clearRect(0, 0, 1, 1); __cx.fillStyle = '#000'; __cx.fillStyle = c; __cx.fillRect(0, 0, 1, 1);
    const d = __cx.getImageData(0, 0, 1, 1).data;
    if (d[3] === 0 && !/\/\s*0(\.0*)?\)|,\s*0\)$/.test(c)) window.__vcUnparsed.add(c);
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const parseColor = c => { const p = toRGBA(c); return p && p[3] > 0.05 ? p : null; };
  const parse = c => { const p = toRGBA(c); return p && {r: p[0], g: p[1], b: p[2], a: p[3]}; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, under) => ({r: top.r * top.a + under.r * (1 - top.a), g: top.g * top.a + under.g * (1 - top.a), b: top.b * top.a + under.b * (1 - top.a), a: 1});
  const bgOf = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !/gradient/.test(cs.backgroundImage)) return null; // 图片上的字交给人看
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    let base = {r: 255, g: 255, b: 255, a: 1};
    for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base);
    return base;
  };
  const clipped = el => { for (let e = el.parentElement; e && e !== root; e = e.parentElement) { const ox = getComputedStyle(e).overflowX; if (ox === 'auto' || ox === 'scroll' || ox === 'hidden') return true; } return false; };

  // 一屏以下的元素滚到视口里量，量完把窗口和各层滚动容器放回原处
  const inView = (el, fn) => {
    const wx = scrollX, wy = scrollY, sc = [];
    for (let e = el.parentElement; e; e = e.parentElement) sc.push([e, e.scrollLeft, e.scrollTop]);
    el.scrollIntoView({block: 'center', behavior: 'instant'});
    try { return fn(el.getBoundingClientRect()); }
    finally { for (const [e, x, y] of sc) e.scrollTo({left: x, top: y, behavior: 'instant'}); window.scrollTo({left: wx, top: wy, behavior: 'instant'}); }  // 写了 scroll-behavior: smooth 的容器也要立刻放回
  };
  // 5：一句话中间的行内链接（WCAG 2.5.8 的行内例外）。只放过 p 里和 li > span 里的（原来就放过的范围），而且要同时满足：
  // 行内、不在 nav / header / footer 里、所在的块里链接以外还有 ≥ PROSE_MIN 个字。div、td 里的句中链接和 li > a 的行标题链接照报
  const inSentence = el => {
    if (el.tagName !== 'A' || !el.closest('p, li > span') || getComputedStyle(el).display !== 'inline' || el.closest('nav, header, footer, [role="navigation"], menu')) return false;
    let blk = el.parentElement;
    while (blk && blk !== root && getComputedStyle(blk).display.startsWith('inline')) blk = blk.parentElement;
    if (!blk) return false;
    let n = 0; const tw = document.createTreeWalker(blk, NodeFilter.SHOW_TEXT);
    while (tw.nextNode()) { const pe = tw.currentNode.parentElement; if (pe && !pe.closest('a, button, [role="button"], [role="link"]')) n += (tw.currentNode.textContent.match(/[A-Za-z0-9\u4e00-\u9fff]/g) || []).length; }
    return n >= PROSE_MIN;
  };
  // 5：热区。伪元素或子元素撑大的热区（::before / ::after、溢出盒子的子元素）量不到盒子上：在盒子外按目标尺寸取点，
  // 点到的是它自己或它的子元素就算点得到。撑大的部分写了 pointer-events: none、或被别的东西盖住时点不到，照盒子量；取样点在视口外量不了的也照盒子量
  const hitSize = (el, r, want) => {
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const own = (x, y) => { if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) return false; const h = document.elementFromPoint(x, y); return !!h && (h === el || el.contains(h)); };
    let w = r.width, h = r.height;
    const out = (size) => size / 2 + Math.max((want - size) / 2 - 0.5, 1);  // 取样点至少在盒子外 1px：盒子自己差一点的不算撑到
    // 撑大的热区要盖得住以盒子中心为中心、目标尺寸的方块：方块的每条边取 EDGE_POINTS 个点（两端在边线内 0.5px，中间等距），全部要点得到。
    // 只伸出一条比目标尺寸窄的条、偏在一侧、缺一块、圆形或圆角 ≥ 2px 的，都有点落空，照盒子量。
    // 量不出来的：相邻两点之间比间距（(want - 1) / 8：44 下 5.4px，24 下 2.9px）窄的缝；每个方向撑到超过 want - 1 就算撑到；
    // 只量方块的四条边，盒子和边之间不取样
    const EDGE_POINTS = 9;
    const spread = Array.from({length: EDGE_POINTS}, (_, i) => (i / (EDGE_POINTS - 1) - 0.5) * (want - 1));
    const covers = (at) => spread.every(d => own(...at(d)));
    const tall = h < want && covers(d => [cx + d, cy - out(h)]) && covers(d => [cx + d, cy + out(h)]);
    const wide = w < want && covers(d => [cx - out(w), cy + d]) && covers(d => [cx + out(w), cy + d]);
    if (tall) h = want;
    if (wide) w = want;
    return [w, h];
  };
  // 1、5：按钮
  for (const el of root.querySelectorAll('button, a, [role="button"], [role="link"], [role="tab"], [role="switch"], summary, input, label')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    const bg = parse(cs.backgroundColor);
    const filled = (bg && bg.a > 0.5) || (cs.backgroundImage && cs.backgroundImage !== 'none');
    let squashed = false;
    if ((el.tagName === 'BUTTON' || el.tagName === 'A') && !(footer && footer.contains(el)) && filled && r.width >= R.width * 0.6) {
      const limit = Math.min(fTop, R.bottom);
      if (r.bottom > limit + 1) issues.push({type: '主按钮被挡住或在首屏外', where: name(el), detail: `按钮底边 ${Math.round(r.bottom)}，可见到 ${Math.round(limit)}；首屏放不下时先删说明文字，再压缩卡片，不靠滚动`});
      if (r.height < 43.5) { squashed = true; issues.push({type: '主按钮被挤扁', where: name(el), detail: `高 ${Math.round(r.height)}：上面的内容太多，flex 把按钮压扁了（按钮加 flex: none，并按上一条压缩内容）`}); }
    }
    const interactive = el.tagName === 'BUTTON' || el.tagName === 'A' || el.tagName === 'SUMMARY' || ['button', 'link', 'tab', 'switch'].includes(el.getAttribute('role'));
    if (interactive && !name(el) && !el.getAttribute('title')) issues.push({type: '控件没有可读名称', where: el.tagName.toLowerCase(), detail: '只有图标的按钮要写 aria-label，读屏才念得出来'});
    if (el.tagName === 'INPUT' && !['checkbox', 'radio', 'hidden'].includes(el.type) && !el.getAttribute('aria-label') && !el.closest('label') && !(el.id && document.querySelector(`label[for="${el.id}"]`)))
      issues.push({type: '控件没有可读名称', where: el.placeholder || 'input', detail: '输入框要有 <label> 或 aria-label，占位文字不算'});
    if (interactive && !squashed && r.width > 0 && (r.width < TAP_MIN - 0.5 || r.height < TAP_MIN - 0.5) && !inSentence(el)) {
      const measure = q => [hitSize(el, q, TAP_FLOOR), hitSize(el, q, TAP_MIN)];  // 热区要在视口里才量得到
      const [[fw, fh], [mw, mh]] = (r.bottom > innerHeight || r.top < 0) ? inView(el, measure) : measure(r);
      const size = `${Math.round(r.width)}×${Math.round(r.height)}`;
      if (Math.min(fw, fh) < TAP_FLOOR - 0.5) issues.push({type: '点按区域小于 24', where: name(el) || el.tagName.toLowerCase(), detail: `${size}，任何可点元素短边至少 ${TAP_FLOOR}px（WCAG 2.2 的 2.5.8）；独立成行的要 ${TAP_MIN}px`});
      else if (mw < TAP_MIN - 0.5 || mh < TAP_MIN - 0.5) issues.push({type: '触控目标小于 44', where: name(el) || el.tagName.toLowerCase(), detail: `${size}，要 ${TAP_MIN}×${TAP_MIN}：给它加内边距或最小高度，整行可点的让链接包住整行`});
    }
  }
  // 2、3、4：文字
  const seen = new Set();
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode; const text = t.textContent.trim();
    if (!text) continue;
    const el = t.parentElement;
    if (!el || seen.has(el) || !visible(el) || el.closest('[aria-hidden="true"], svg, script, style')) continue;
    seen.add(el);
    const cs = getComputedStyle(el); const fs = parseFloat(cs.fontSize); const lh = parseFloat(cs.lineHeight) || fs * 1.4;
    const r = el.getBoundingClientRect();
    const vertical = cs.writingMode.startsWith('vertical');  // 有意的竖排（侧边的竖排标签）不算
    if (!vertical && text.length >= 3 && r.width < fs * 2.2 && r.height > lh * 2.5) issues.push({type: '文字被挤成竖排', where: text.slice(0, 20), detail: `宽 ${Math.round(r.width)}、高 ${Math.round(r.height)}`});
    if (r.right > R.right + 1 && !clipped(el)) issues.push({type: '内容超出画板', where: text.slice(0, 20), detail: `右边 ${Math.round(r.right)} > ${Math.round(R.right)}`});
    if (el.closest('button[disabled], [aria-disabled="true"]')) continue;
    const fg = parse(cs.color); const bg = bgOf(el);
    if (fg && bg) {
      const f = fg.a < 1 ? blend(fg, bg) : fg;
      const L1 = lum(f), L2 = lum(bg); const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const large = fs >= 24 || (fs >= 18.66 && parseInt(cs.fontWeight) >= 700);
      const need = large ? 3 : 4.5;
      if (ratio < need - 0.05) issues.push({type: '对比度不够', where: text.slice(0, 20), detail: `${ratio.toFixed(2)}:1，要 ${need}:1`});
    }
  }
  // 11：展开层完整留在所在区块里（aria-expanded="true" 的控件用 aria-controls 指向它）
  for (const t of root.querySelectorAll('[aria-expanded="true"][aria-controls]')) {
    const layer = document.getElementById(t.getAttribute('aria-controls'));
    const sec = layer && layer.closest('section');
    if (!layer || !sec || !visible(layer)) continue;
    const a = layer.getBoundingClientRect(), b = sec.getBoundingClientRect();
    if (a.bottom > b.bottom + 1 || a.right > b.right + 1 || a.top < b.top - 1 || a.left < b.left - 1)
      issues.push({type: '展开层超出所在区块', where: name(t), detail: `展开层 ${Math.round(a.top)}–${Math.round(a.bottom)}，区块 ${Math.round(b.top)}–${Math.round(b.bottom)}`});
  }
  // 12：可点元素被别的东西盖住（看它中心那一点最上面是不是它自己）
  for (const el of root.querySelectorAll('a[href], button, input')) {
    if (!visible(el)) continue;
    const r0 = el.getBoundingClientRect();
    if (r0.width < 2 || r0.height < 2 || r0.right < 0 || r0.left > innerWidth) continue;
    const below = r0.top + r0.height / 2 >= innerHeight && r0.top < Math.max(R.bottom, document.documentElement.scrollHeight);  // 一屏以下的滚到视口里再量
    if (!below && (r0.bottom < 0 || r0.top > innerHeight)) continue;
    const probe = r => document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    const hit = below ? inView(el, probe) : probe(r0);
    if (!hit || el.contains(hit) || hit.contains(el)) continue;
    const owner = hit.closest('a[href], button, input, [role="group"], [role="dialog"], [role="menu"], form, header, nav');
    if (owner && !owner.contains(el) && !el.contains(owner)) issues.push({type: '可点元素被盖住', where: name(el), detail: `被「${name(owner) || owner.tagName.toLowerCase()}」盖住`});
  }
  // 13：首屏（第一个 section）里的按钮和表单完整留在视口里
  const hero = root.querySelector('section');
  if (hero && (!window.__vcFluid || hero.getBoundingClientRect().top < innerHeight / 2)) for (const el of hero.querySelectorAll('.btn, form, [role="switch"]')) {  // 流式页面里，第一个 section 从半屏以下才开始的不是首屏；固定尺寸的画板照原判法
    if (!visible(el) || el.closest('[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect();
    if (r.bottom > innerHeight + 1) issues.push({type: '首屏主操作在视口外', where: name(el), detail: `底边 ${Math.round(r.bottom)} > 视口 ${innerHeight}；首屏高度按 100svh 算，内容跟着视口压缩`});
  }
  // 14：深色主题下画板外露出浅色底
  {
    const opaque = el => { const c = parse(getComputedStyle(el).backgroundColor); return c && c.a > 0 ? c : null; };
    const page = opaque(document.body) || opaque(document.documentElement) || {r: 255, g: 255, b: 255, a: 1};  // 都透明时浏览器画白底
    const own = bgOf(root);
    const gap = R.top > 1 || R.left > 1 || R.bottom < Math.max(innerHeight, document.documentElement.scrollHeight) - 1;
    if (own && lum(own) < 0.2 && gap && page.a > 0 && lum(page) > 0.4) issues.push({type: '深色下露出浅色底', where: 'body', detail: '主题只设在里层，外面的 body 还是浅色；主题设到 :root，body 背景跟着主题'});
  }
  // 15：按钮文字折行（C4：一行放下，放不下改排法）
  for (const el of root.querySelectorAll('.btn, button, [role="button"]')) {
    if (!visible(el)) continue;
    const t = (el.innerText || '').trim(); if (!t) continue;
    const cs = getComputedStyle(el); const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3;
    const tops = [];
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (tw.nextNode()) { if (!tw.currentNode.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(tw.currentNode); for (const r of rg.getClientRects()) if (r.width > 1) tops.push(r.top); }
    tops.sort((a, b) => a - b);
    const lines = new Set(); let last = -1e9; for (const tp of tops) { if (tp - last > lh * 0.5) { lines.add(tp); last = tp; } }
    if (lines.size > 1) issues.push({type: '按钮文字折行', where: t.slice(0, 24), detail: `折成 ${lines.size} 行；按钮文字一行放下，放不下时改排法，不缩字号`});
  }
  // 16：浮层要有出路（U6）：展开的层、对话框、菜单里有关闭按钮，或画板逻辑处理了 Esc
  for (const layer of root.querySelectorAll('[role="dialog"], [role="menu"], [aria-modal="true"]')) {
    if (!visible(layer)) continue;
    const closer = [...layer.querySelectorAll('button, a[href]')].some(b => /关闭|收起|取消|完成|Close|Cancel|Done/i.test(name(b)));
    if (!closer && !window.__dcHandlesEscape) issues.push({type: '浮层没有出路', where: name(layer) || layer.getAttribute('role'), detail: '弹层里放一个「关闭」按钮，并处理 Esc 和点外面关闭'});
  }
  // 17：孤字成行（V9）：两行以上的段落，最后一行只有一个汉字或一个词
  for (const el of root.querySelectorAll('h1, h2, h3, h4, p, li, figcaption, dd, td, .lead, .row-title, .row-line, .meta-part, .meta > span, .card-meta > span')) {
    if (!visible(el) || el.closest('svg, [aria-hidden="true"]')) continue;
    if (/flex|grid|table/.test(getComputedStyle(el).display)) continue;  // 弹性和网格容器里各格并排，不是一段文字的多行
    if ([...el.children].some(c => !getComputedStyle(c).display.startsWith('inline'))) continue;  // 里面有块级子元素，最后一行属于别的块
    const rg = document.createRange(); rg.selectNodeContents(el);
    const rects = [...rg.getClientRects()].filter(r => r.width > 0.5);
    if (rects.length < 2) continue;
    const lastTop = Math.max(...rects.map(r => r.top));
    const firstTop = Math.min(...rects.map(r => r.top));
    if (lastTop - firstTop < 4) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const lastW = rects.filter(r => Math.abs(r.top - lastTop) < 3).reduce((a, r) => a + r.width, 0);
    const text = (el.innerText || '').trim();
    if (/[\/.:]\S*$/.test(text.split(/\s+/).pop() || '') && /\//.test(text)) continue;  // 网址、路径折到下一行不算孤字
    const cjk = /[一-鿿]$/.test(text.replace(/[。，、；：！？」』）)\]]+$/, ''));
    const endsPunct = /[。，、；：！？」』）]$/.test(text);
    if ((cjk && lastW < fs * (endsPunct ? 2.6 : 1.6)) || (!cjk && lastW < fs * 3 && !/\s/.test(text.slice(-12).trim().split(/\s+/).pop() || ' ')))
      issues.push({type: '孤字成行', where: text.slice(-16), detail: `最后一行只剩约 ${Math.round(lastW)}px；用 text-wrap: pretty 或调整断句`});
  }
  // 18：词中断行（V9）：标题、按钮、标签这类短文字里，中文词被拆到两行（「课 / 程」）；正文段落按中文排版习惯可以在字间断行，只查孤字
  if (typeof Intl !== 'undefined' && Intl.Segmenter) {
    const seg = new Intl.Segmenter('zh', {granularity: 'word'});
    const seenW = new Set();
    for (const el of root.querySelectorAll('h1, h2, h3, h4, a, button, dt, th, .row-title, .kicker, .who')) {
      if (!visible(el) || el.closest('svg, [aria-hidden="true"]') || (el.innerText || '').trim().length > 40) continue;
      const kids = [...el.childNodes];
      kids.forEach((node, k) => {  // 手写的 <br> 把西文词和后面的中文词拆开
        if (node.nodeName !== 'BR' || k === 0 || k === kids.length - 1) return;
        const before = (kids[k - 1].textContent || '').trimEnd(), after = (kids[k + 1].textContent || '').trimStart();
        const m = before.match(/([A-Za-z0-9][\w.+-]*)$/);
        if (m && /^[一-鿿]/.test(after) && !seenW.has('br|' + before)) { seenW.add('br|' + before); issues.push({type: '词中断行', where: m[1] + ' ' + after.slice(0, 4), detail: `手写的换行把「${m[1]}」和后面的「${after.slice(0, 4)}」拆开了；去掉 <br>，让词组整体换行`}); }
      });
      for (const node of el.childNodes) {
        if (node.nodeType !== 3) continue;
        const t = node.textContent; if (t.length < 2 || !/[一-鿿A-Za-z]/.test(t)) continue;
        const tops = []; const rg = document.createRange();
        for (let i = 0; i < t.length; i++) { rg.setStart(node, i); rg.setEnd(node, i + 1); const r = rg.getClientRects()[0]; tops.push(r ? r.top : null); }
        const segs = [...seg.segment(t)];
        for (let k = 0; k < segs.length; k++) {  // 中英混排：西文词后面（隔着空格也算）紧跟中文词，两者落在两行
          const w = segs[k]; if (!w.isWordLike || !/^[A-Za-z0-9][\w.+-]*$/.test(w.segment)) continue;
          let n = k + 1; while (n < segs.length && /^\s+$/.test(segs[n].segment)) n++;
          if (n >= segs.length || !/^[一-鿿]/.test(segs[n].segment)) continue;
          const a = tops[w.index + w.segment.length - 1], b = tops[segs[n].index];
          const key = w.segment + segs[n].segment + '|' + t.slice(0, 12);
          if (a !== null && b !== null && Math.abs(b - a) > 4 && !seenW.has(key)) { seenW.add(key); issues.push({type: '词中断行', where: w.segment + ' ' + segs[n].segment, detail: `「${w.segment}」和后面的「${segs[n].segment}」被拆到两行：中英混排的词组要放在同一行，用不断行空格或 keep-all 的包裹`}); }
        }
        for (const w of segs) {
          if (!w.isWordLike || w.segment.length < 2 || !/^[一-鿿]+$/.test(w.segment)) continue;
          const a = tops[w.index], b = tops[w.index + w.segment.length - 1];
          if (a !== null && b !== null && Math.abs(b - a) > 4) {
            const key = w.segment + '|' + t.slice(0, 12);
            if (!seenW.has(key)) { seenW.add(key); issues.push({type: '词中断行', where: w.segment, detail: `「${t.slice(Math.max(0, w.index - 6), w.index + w.segment.length + 4)}」里的「${w.segment}」被拆到两行；调整断句、给词加 word-break: keep-all 的包裹，或改宽度`}); }
          }
        }
      }
    }
  }
  // 19：文字冲出所在的圆角容器（胶囊条、卡片），或短标签被挤成三行以上
  for (const el of root.querySelectorAll('span, time, a, button, p, small')) {
    if (!visible(el) || el.closest('svg')) continue;
    const t = (el.innerText || '').trim(); if (!t || el.children.length > 2) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 2 || r.height <= 2 || getComputedStyle(el).clip !== 'auto') continue;  // 只给读屏的隐藏标签
    let box = null;
    for (let e = el.parentElement; e && e !== root; e = e.parentElement) { const cs = getComputedStyle(e); if (parseFloat(cs.borderTopLeftRadius) >= 8 && (parseColor(cs.backgroundColor) || cs.backdropFilter !== 'none')) { box = e; break; } }
    if (box && /auto|scroll|hidden|clip/.test(getComputedStyle(box).overflowX + getComputedStyle(box).overflowY)) box = null;  // 能滚动或有意裁切的容器
    if (box) { const b = box.getBoundingClientRect(); if (r.right > b.right + 2 || r.bottom > b.bottom + 2 || r.left < b.left - 2) issues.push({type: '文字冲出容器', where: t.slice(0, 24), detail: '文字超出所在的圆角条或卡片；给它换一行，或让容器跟着内容长'}); }
    const words = t.split(/\s+/).length;
    if (words <= 3 && t.length <= 24 && !getComputedStyle(el).writingMode.startsWith('vertical') && el.parentElement && getComputedStyle(el.parentElement).display.includes('flex')) {
      const lh = parseFloat(getComputedStyle(el).lineHeight) || parseFloat(getComputedStyle(el).fontSize) * 1.3;
      const tops = []; const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      while (tw.nextNode()) { if (!tw.currentNode.textContent.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(tw.currentNode); for (const q of rg.getClientRects()) if (q.width > 1) tops.push(q.top); }
      tops.sort((a, b) => a - b); let n = 0, last = -1e9; for (const tp of tops) if (tp - last > lh * 0.5) { n++; last = tp; }
      if (n >= 3 && getComputedStyle(el).webkitLineClamp === 'none') issues.push({type: '短标签被挤成多行', where: t, detail: `折成 ${n} 行；标签加 white-space: nowrap，放不下就换到下一行`});
    }
  }
  // 20：标点在行首（V9）：逗号、句号、顿号这类不该出现在一行的开头
  for (const el of root.querySelectorAll('h1, h2, h3, h4, p, li, figcaption, dd, td, a, button, span')) {
    if (!visible(el) || el.closest('svg, [aria-hidden="true"]')) continue;
    for (const node of el.childNodes) {
      if (node.nodeType !== 3) continue;
      const t = node.textContent; if (t.length < 2 || t.length > 400 || !/[，。、；：！？）」』]/.test(t)) continue;
      const rg = document.createRange(); let prevTop = null;
      for (let i = 0; i < t.length; i++) {
        rg.setStart(node, i); rg.setEnd(node, i + 1); const r = rg.getClientRects()[0]; if (!r) continue;
        if (prevTop !== null && r.top - prevTop > 4 && /[，。、；：！？）」』]/.test(t[i])) { issues.push({type: '标点在行首', where: t.slice(Math.max(0, i - 8), i + 4), detail: '标点落到了下一行开头；检查是不是 word-break: keep-all 用在了带标点的长文字上'}); break; }
        prevTop = r.top;
      }
    }
  }
  // 10：弹性布局吞掉空格
  for (const el of root.querySelectorAll('*')) {
    if (!visible(el)) continue;
    const dcs = getComputedStyle(el); const d = dcs.display;
    if (!/flex|grid/.test(d) || parseFloat(dcs.columnGap) > 0) continue; // 有 gap 时空格本来就由 gap 代替
    const kids = [...el.childNodes];
    kids.forEach((n, i) => {
      if (n.nodeType !== 3 || !n.textContent.trim()) return;
      const prevEl = kids.slice(0, i).reverse().find(k => k.nodeType === 1 || (k.nodeType === 3 && k.textContent.trim()));
      const nextEl = kids.slice(i + 1).find(k => k.nodeType === 1 || (k.nodeType === 3 && k.textContent.trim()));
      if ((/^\s/.test(n.textContent) && prevEl && prevEl.nodeType === 1) || (/\s$/.test(n.textContent) && nextEl && nextEl.nodeType === 1))
        issues.push({type: '弹性布局吞掉了空格', where: (el.innerText || '').trim().replace(/\s+/g, '').slice(0, 24), detail: '容器是 flex/grid，文字和元素之间的空格不显示；改成 inline-block 或用 gap'});
    });
  }
  // 22：玻璃的背景声明要成立
  for (const el of root.querySelectorAll('[data-backdrop]')) {
    if (!visible(el)) continue;
    const kind = el.getAttribute('data-backdrop'), r = el.getBoundingClientRect();
    const overlaps = sel => [...document.querySelectorAll(sel)].some(c => {
      if (c === el || el.contains(c) || !visible(c)) return false;
      const b = c.getBoundingClientRect(); return b.left < r.right && b.right > r.left && b.top < r.bottom && b.bottom > r.top;
    });
    let ok = false, why = '';
    if (kind === 'motion') { ok = overlaps('canvas, [data-motion]'); why = '背后没有和它重叠的 canvas 或 [data-motion] 区域'; }
    else if (kind === 'video') { ok = overlaps('video, [data-video], .video-frame') || !!el.parentElement?.closest('[data-video], .video-frame'); why = '背后没有和它重叠的视频'; }
    else if (kind === 'scroll') { for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const p = getComputedStyle(e).position; if (p === 'sticky' || p === 'fixed') { ok = true; break; } } why = '它和祖先都不是 sticky / fixed，内容不会从它后面滚过'; }
    else why = `「${kind}」不是 motion、video、scroll 之一`;
    if (!ok) issues.push({type: '玻璃的背景声明不成立', where: name(el) || kind, detail: `data-backdrop="${kind}"：${why}；声明不成立时背后就是平涂，改成实色面`});
  }
  // 23：可点元素要有悬停和按下样式（:hover / .is-hover、:active / .is-press）
  {
    const STATE = /:hover|:active|\.is-hover|\.is-press/;
    const sels = [];
    const collect = rules => { for (const r of rules || []) {
      if (r.selectorText && STATE.test(r.selectorText)) for (const part of r.selectorText.split(/,(?![^(]*\))/)) {
        const base = part.replace(/::?(before|after|placeholder|marker|selection)\b/g, '').replace(/:hover|:active|\.is-hover|\.is-press/g, ':where(*)').trim();
        if (/:hover|\.is-hover/.test(part)) sels.push(['h', base]);
        if (/:active|\.is-press/.test(part)) sels.push(['p', base]);
      }
      try { collect(r.cssRules); } catch (e) {}
    } };
    for (const ss of document.styleSheets) { try { collect(ss.cssRules); } catch (e) {} }
    const CLICK = 'a[href], button, [role="button"], [role="switch"], [role="tab"], [role="link"], [role="menuitem"], [role="option"], summary';
    const hits = (el, kind) => sels.some(([k, b]) => {
      if (k !== kind) return false;
      try {
        if (el.matches(b) || el.querySelector(b)) return true;
        const up = el.parentElement && el.parentElement.closest(b);  // 外层的悬停样式只算只包着这一个可点元素的外层
        return !!up && up !== root && up.querySelectorAll(CLICK).length === 1;
      } catch (e) { return false; }
    });
    const seenS = new Set();
    for (const el of root.querySelectorAll(CLICK)) {
      if (!visible(el) || el.disabled || el.getAttribute('aria-disabled') === 'true' || el.closest('svg, [aria-hidden="true"], [inert]')) continue;
      const prose = el.tagName === 'A' && el.closest('p, li, dd, blockquote, figcaption') && getComputedStyle(el).display === 'inline';
      const miss = [];
      if (!hits(el, 'h')) miss.push('悬停');
      if (!prose && !hits(el, 'p')) miss.push('按下');
      const key = name(el) + '|' + miss.join();
      if (miss.length && !seenS.has(key)) { seenS.add(key); issues.push({type: '可点元素没有悬停或按下样式', where: name(el) || el.tagName.toLowerCase(), detail: `缺${miss.join('、')}：给它的类写 :hover 和 :active（或 .is-hover / .is-press）；玻璃控件按 liquid-glass.md 提亮底色，不叠灰`}); }
    }
  }
  // 模板味信号（提示）
  const hints = [];
  const emoji = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B50}\u{2728}]/u;
  for (const el of root.querySelectorAll('*')) {
    if (!visible(el) || el.closest('svg')) continue;
    const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    const cs = getComputedStyle(el);
    if (own && emoji.test(own)) hints.push({sign: 'emoji', where: own.slice(0, 24)});
    if (own && /[!！]/.test(own)) hints.push({sign: '感叹号', where: own.slice(0, 24)});
    if (own && cs.textTransform === 'uppercase' && parseFloat(cs.letterSpacing) > 0.5) hints.push({sign: '全大写加宽字距', where: own.slice(0, 24)});
    if (own && parseInt(cs.fontWeight) >= 800) hints.push({sign: '特粗字重', where: own.slice(0, 24)});
    if (own && cs.fontStyle === 'italic') hints.push({sign: '斜体强调', where: own.slice(0, 24)});
    if (own && parseFloat(cs.fontSize) < 14 && parseFloat(cs.letterSpacing) < 0) hints.push({sign: '小字负字距', where: own.slice(0, 24)});
    if ((cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') && /gradient/.test(cs.backgroundImage)) hints.push({sign: '渐变文字', where: (el.innerText || '').trim().slice(0, 24)});
    if (/(^|,)\s*all\b/.test(cs.transitionProperty) && cs.transitionDuration !== '0s') hints.push({sign: 'transition: all', where: el.tagName.toLowerCase()});
    if ((el.tagName === 'BUTTON' || el.getAttribute('role') === 'button') && /[。.]$/.test((el.innerText || '').trim())) hints.push({sign: '按钮文字带句号', where: (el.innerText || '').trim().slice(0, 24)});
  }
  // 6：定义过的 token
  const defined = [];
  const walk = rules => { for (const r of rules || []) { if (r.style) for (const p of r.style) if (p.startsWith('--')) defined.push(p); try { walk(r.cssRules); } catch (e) {} } };
  for (const ss of document.styleSheets) { try { walk(ss.cssRules); } catch (e) {} }
  for (const el of root.querySelectorAll('[style]')) for (const p of el.style) if (p.startsWith('--')) defined.push(p);
  if (R0.right > VW + 1) issues.push({type: '画板比视口宽', where: (root.className || root.tagName).toString().slice(0, 30), detail: `画板 ${Math.round(R0.width)}px，视口 ${VW}px：自适应的画板根节点用 width: 100%（或 min(100%, …)），不写死像素宽度`});
  // 不用读就会用（C10）：首屏里要读的说明文字有上限；站标回首页
  {
    // 只量入口页的首屏：画板在首屏区域上标 data-first-screen（首页、三站首屏）；文章这类阅读页不标、不量。
    // 图（figure）里的东西按图看，浮层（data-pop、dialog）是用户自己打开的，都不算
    const hero = root.matches('[data-first-screen]') ? root : root.querySelector('[data-first-screen]');
    const VH = Math.min(window.innerHeight, innerWidth >= 1024 ? 900 : innerWidth >= 744 ? 1180 : 844); let zh = 0, en = 0;
    const walker = document.createTreeWalker(hero || document.createElement('div'), NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) {
      const el = t.parentElement; if (!el || !t.textContent.trim()) continue;
      if (el.closest('h1, h2, h3, button, a, nav, header, footer, label, input, [role="button"], [aria-hidden="true"], svg, script, style, .mono, figure, [data-pop], [role="dialog"], [role="group"]')) continue;
      if (!visible(el)) continue;
      const r = el.getBoundingClientRect(); if (r.top >= Math.min(VH, R.bottom) || r.bottom <= 0) continue;
      const tx = t.textContent;
      zh += (tx.match(/[\u4e00-\u9fff]/g) || []).length;
      en += (tx.replace(/[\u4e00-\u9fff]/g, ' ').match(/[A-Za-z][A-Za-z'’-]*/g) || []).length;
    }
    window.__vcReadLoad = {zh, en};
    const ZH_MAX = 80, EN_MAX = 50;  // 自定：约 5 秒扫完（中文每分钟约 500 字、英文约 300 词的速读）
    if (zh > ZH_MAX || en > EN_MAX) issues.push({type: '首屏要读的字太多', where: `中文 ${zh} 字、英文 ${en} 词`, detail: `首屏里标题、按钮、导航、图以外要读的说明不超过中文 ${ZH_MAX} 字、英文 ${EN_MAX} 词（C10）：能用图标和位置说清的删掉说明，必须写的一处一句`});
    for (const a of root.querySelectorAll('nav a, header a, .brand, .home, [aria-label*="首页"], [aria-label*="home" i]')) {
      const lbl = ((a.getAttribute('aria-label') || '') + ' ' + (a.innerText || '')).trim();
      const isBrand = a.matches('.brand, .home') || /(首页|home ?page|^home\b|主页)/i.test(lbl);
      if (!isBrand || a.tagName !== 'A' || !visible(a)) continue;  // 只看链接：「暂停首页动画」这类按钮不是站标
      const h = a.getAttribute('href') || '';
      if (!/^(\/|#home|https?:\/\/[^/]+\/?$|\/index|Main\.dc\.html)/.test(h)) issues.push({type: '站标不回首页', where: lbl.slice(0, 20) || h, detail: `站标链到「${h}」：照通行约定，左上角的站标回首页；回到本页顶部用另一个控件`});
    }
  }
  // 笼统的进度文字（ux-canon 原则 4）：超过 1 秒的状态写「动词 + 对象」，不写「加载中」
  for (const el of root.querySelectorAll('*')) {
    if (el.children.length || !visible(el)) continue;
    const tx = (el.textContent || '').trim();
    if (/^(加载中|处理中|请稍候|请稍等|Loading|Processing|Please wait)[.…。]*$/i.test(tx)) issues.push({type: '笼统的进度文字', where: tx, detail: '进度写成「动词 + 对象」：「正在订阅」「在挑今天的动作」「Loading milestones」；骨架屏可以不写字'});
  }
  for (const c of window.__vcUnparsed) issues.push({type: '颜色算不了', where: c.slice(0, 40), detail: '检查读不出这个颜色，对比度和背景判断会失真；换成浏览器能解析的写法，或在 verify_canvas.py 的 parseColor 里补上'});
  return {issues, hints, defined: [...new Set(defined)]};
}
"""


STATE_JS = '''(cls) => {
  // 只给原来没有这个类的元素加，量完只摘掉自己加的：画板里本来就画成悬停或按下态的元素（class 里写了 is-hover）保持原样
  const els = [...document.querySelectorAll('.btn, .liquid, .opt, .icon-btn, .orb')].filter(e => !e.classList.contains(cls));
  els.forEach(e => e.classList.add(cls));
  try { return (''' + CHECK_JS.strip() + ''')().issues; }
  finally { els.forEach(e => e.classList.remove(cls)); }
}'''


GLASS_JS = r"""
() => {
  const out = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el), bf = cs.backdropFilter || cs.webkitBackdropFilter;
    if (!bf || bf === 'none' || cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 24 || r.bottom < 0 || r.top > innerHeight) continue;
    if (el.closest('[data-backdrop]')) continue;  // 声明了背后是动效、视频或滚动内容：静态截图看不到，交给人在画布上看
    el.setAttribute('data-vc-glass', out.length);
    out.push({i: out.length, x: r.left, y: r.top, w: r.width, h: r.height,
              name: ((el.getAttribute('aria-label') || el.innerText || el.tagName).trim().replace(/\s+/g, ' ').slice(0, 30))});
  }
  return out;
}
"""


METRICS_JS = r"""
() => {
  // 29–32 用的量：第一个标题的左边缘、首屏空白带、相邻的平涂色面、字号种类。只量，不判；阈值在 Python 一侧
  const O = window.__vcOpts || {};
  const root = document.querySelector('[data-theme]') || document.body;
  const R = root.getBoundingClientRect(), VW = innerWidth, VH = innerHeight;
  const vis = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) > 0.01 && el.getClientRects().length > 0; };
  const label = el => { if (el === document.body) return '页面底色（body）'; if (el === root) return '画板底色'; const full = ((el.getAttribute('aria-label') || '') || (el.innerText || '')).trim().replace(/\s+/g, ' '); const t = full.length <= 14 ? full : ''; const c = (el.className && el.className.baseVal === undefined ? String(el.className) : '').trim().split(/\s+/).filter(Boolean).slice(0, 2).join('.'); return el.tagName.toLowerCase() + (c ? '.' + c : '') + (t ? '「' + t + '」' : ''); };
  const out = {};
  // 29：第一个 h1 的左边缘；没有 h1 取第一屏第一个标题
  {
    const ok = h => vis(h) && !h.closest('[data-edge="free"], [aria-hidden="true"], [role="dialog"]');
    let h = [...root.querySelectorAll('h1')].find(ok);
    if (!h) h = [...root.querySelectorAll('h2, h3, [role="heading"]')].find(x => ok(x) && x.getBoundingClientRect().top < VH);
    if (h) { const r = h.getBoundingClientRect(); out.edge = {left: Math.round(r.left * 10) / 10, tag: h.tagName.toLowerCase(), text: (h.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 16)}; }
  }
  // 30：首屏空白带。内容 = 文字、控件、图片（img、svg、video、背景图）；动效 = canvas、[data-motion]
  // 只量入口页的首屏：标了 data-first-screen 的区域，或流式页面的第一屏；固定尺寸的 App 界面（内容在上、按钮贴底）不量
  const fsEl = root.matches('[data-first-screen]') ? root : root.querySelector('[data-first-screen]');
  const scope = fsEl ? fsEl.getBoundingClientRect() : (window.__vcFluid ? R : null);
  if (scope) {
    const top0 = Math.max(0, scope.top), bot0 = Math.min(VH, scope.bottom);
    const solid = [], motion = [];
    const add = (arr, r) => { const a = Math.max(r.top, top0), b = Math.min(r.bottom, bot0); if (b - a > 1 && r.width > 1 && r.right > 0 && r.left < VW) arr.push([a, b]); };
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (tw.nextNode()) {
      const n = tw.currentNode, pe = n.parentElement;
      if (!n.textContent.trim() || !pe || pe.closest('script, style') || !vis(pe)) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) add(solid, r);
    }
    for (const el of root.querySelectorAll('img, picture, video, [data-video], svg, [role="img"], a[href], button, input, select, textarea, [role="button"]')) if (vis(el)) add(solid, el.getBoundingClientRect());
    for (const el of root.querySelectorAll('*')) { const bi = getComputedStyle(el).backgroundImage; if (bi && /url\(/.test(bi) && vis(el)) add(solid, el.getBoundingClientRect()); }
    // 加载态的骨架不是空白：aria-busy="true" 的容器整块算（它底下的灰块不论怎么画都算），[data-skeleton] 和类名带 skeleton 的占位块各算一块
    for (const el of root.querySelectorAll('[aria-busy="true"], [data-skeleton], [class*="skeleton" i]')) if (vis(el)) add(solid, el.getBoundingClientRect());
    for (const el of root.querySelectorAll('canvas, [data-motion]')) if (vis(el)) add(motion, el.getBoundingClientRect());
    const gap = ivs => { let best = [0, top0, top0], cur = top0; for (const [a, b] of [...ivs].sort((x, y) => x[0] - y[0])) { if (a - cur > best[0]) best = [a - cur, cur, a]; cur = Math.max(cur, b); } if (bot0 - cur > best[0]) best = [bot0 - cur, cur, bot0]; return best.map(Math.round); };
    out.band = {vh: VH, all: gap(solid.concat(motion)), solid: gap(solid)};
  }
  // 32：字号种类
  {
    const sizes = {};
    for (const el of root.querySelectorAll('*')) {
      if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || el.closest('script, style, svg') || !vis(el)) continue;
      const fs = Math.round(parseFloat(getComputedStyle(el).fontSize) * 10) / 10;
      sizes[fs] = (sizes[fs] || 0) + 1;
    }
    out.sizes = sizes;
  }
  // 31：相邻的平涂色面
  {
    const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', {willReadFrequently: true});
    const rgba = c => { if (!c || c === 'transparent') return null; const m = c.match(/^rgba?\(([^)]+)\)$/); if (m) { const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; } cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
    const flat = el => {  // 这个元素自己画出来的平涂底色（和下面各层混合后）；有背景图、渐变或透到图片上的不算平涂
      const layers = [];
      for (let e = el; e; e = e.parentElement) {
        const cs = getComputedStyle(e);
        if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
        const c = rgba(cs.backgroundColor);
        if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
      }
      let b = [255, 255, 255];
      for (let i = layers.length - 1; i >= 0; i--) { const t = layers[i]; b = [0, 1, 2].map(k => t[k] * t[3] + b[k] * (1 - t[3])); }
      return b;
    };
    const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
    const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
    const hex = c => '#' + c.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
    const minA = (O.faceArea || 0.2) * VW * VH;
    let cands = [];
    for (const el of new Set([document.body, root, ...root.querySelectorAll('*')])) {
      if (!vis(el) || el.closest('svg')) continue;
      const own = rgba(getComputedStyle(el).backgroundColor);
      if (!own || own[3] <= 0.5) continue;
      const r = el.getBoundingClientRect();
      const x0 = Math.max(0, r.left), y0 = Math.max(0, r.top), x1 = Math.min(VW, r.right), y1 = Math.min(VH, r.bottom);
      if (x1 - x0 <= 0 || y1 - y0 <= 0 || (x1 - x0) * (y1 - y0) < minA) continue;
      const c = flat(el); if (!c) continue;
      cands.push({el, x0, y0, x1, y1, area: (x1 - x0) * (y1 - y0), c});
    }
    cands = cands.filter((b, i) => !cands.some((a, j) => j !== i && a.el !== b.el && a.el.contains(b.el) && ratio(a.c, b.c) < 1.005));  // 套在同色的外层里：同一块面
    const inside = (b, a) => a.el !== b.el && a.el.contains(b.el);
    for (const a of cands) {  // 露在外面的面积：减掉直接套在里面的面
      const kids = cands.filter(b => inside(b, a) && !cands.some(m => inside(b, m) && inside(m, a)));
      a.left = a.area - kids.reduce((s, k) => s + k.area, 0); a.kids = kids;
    }
    // 边界已经画出来的面算分得开。两种画法：
    //   柔和的阴影：有一层不透明度 > 0.1、模糊 > 0 的 box-shadow；全透明的不算（shadow-none 生成的 0 0 #0000、悬停才显出来的 0 8px 24px rgba(0,0,0,0)）
    //   描边：边框、outline、或没有模糊的 box-shadow（0 0 0 1px 这类圈）。描边的颜色（叠在这块面上以后）要和两块面里至少一块
    //         对比 ≥ 阈值才算；和面同色的描边看不出来，不算
    const need = O.faceContrast || 1.3;
    const over = (c, base) => [0, 1, 2].map(k => c[k] * c[3] + base[k] * (1 - c[3]));
    const stroke = (col, a, b) => { const p = rgba(col); if (!p || p[3] <= 0.1) return false; const c = over(p, a.c); return ratio(c, a.c) >= need || ratio(c, b.c) >= need; };
    const edged = (a, b) => { const cs = getComputedStyle(a.el);
      for (const layer of (cs.boxShadow && cs.boxShadow !== 'none' ? cs.boxShadow.split(/,(?![^(]*\))/) : [])) {
        const col = (layer.match(/(rgba?|color|oklab|oklch|lab|lch|hsla?|hwb)\([^)]*\)|#[0-9a-f]+/i) || [''])[0];
        const n = (layer.replace(col, '').match(/-?[\d.]+(?=px)/g) || []).map(Number);  // x、y、模糊、扩散
        const p = rgba(col); if (!p || p[3] <= 0.1) continue;
        if ((n[2] || 0) > 0) return true;
        if (((n[3] || 0) !== 0 || (n[0] || 0) !== 0 || (n[1] || 0) !== 0) && stroke(col, a, b)) return true;
      }
      if (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0 && stroke(cs.outlineColor, a, b)) return true;
      return ['Top', 'Right', 'Bottom', 'Left'].some(k => cs['border' + k + 'Style'] !== 'none' && parseFloat(cs['border' + k + 'Width']) > 0 && stroke(cs['border' + k + 'Color'], a, b)); };
    const pairs = [];
    for (let i = 0; i < cands.length; i++) for (let j = i + 1; j < cands.length; j++) {
      const a = cands[i], b = cands[j]; let adj = false;
      if (inside(b, a)) adj = a.kids.includes(b) && a.left >= minA && !edged(b, a);
      else if (inside(a, b)) adj = b.kids.includes(a) && b.left >= minA && !edged(a, b);
      else {
        const ov = (p0, p1, q0, q1) => Math.min(p1, q1) - Math.max(p0, q0);
        const side = (Math.abs(a.x1 - b.x0) <= 2 || Math.abs(b.x1 - a.x0) <= 2) && ov(a.y0, a.y1, b.y0, b.y1) >= VH * 0.2;
        const stack = (Math.abs(a.y1 - b.y0) <= 2 || Math.abs(b.y1 - a.y0) <= 2) && ov(a.x0, a.x1, b.x0, b.x1) >= VW * 0.2;
        adj = (side || stack) && a.left >= minA && b.left >= minA && !edged(a, b) && !edged(b, a);
      }
      if (!adj) continue;
      const k = ratio(a.c, b.c);
      if (k >= 1.005) pairs.push({a: label(a.el), b: label(b.el), ca: hex(a.c), cb: hex(b.c), ratio: Math.round(k * 100) / 100, pa: Math.round(a.area / VW / VH * 100), pb: Math.round(b.area / VW / VH * 100)});
    }
    out.faces = pairs;
  }
  return out;
}
"""


POS_JS = r"""
() => {
  const vis = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length > 0; };
  const nm = el => ((el.getAttribute('aria-label') || el.innerText || el.placeholder || '').trim().replace(/\s+/g, ' ').slice(0, 30));
  const open = [...document.querySelectorAll('[aria-expanded="true"]')].filter(t => vis(t) && !t.closest('[data-expand="inline"]'));
  const layers = open.map(t => document.getElementById(t.getAttribute('aria-controls') || '')).filter(Boolean);
  const pos = {}, seen = {};
  for (const el of document.querySelectorAll('h1, h2, h3, .btn, button, a[href], input, textarea, select')) {
    if (!vis(el) || layers.some(l => l.contains(el)) || el.closest('[role="dialog"], [aria-modal="true"], [role="menu"], [role="listbox"]')) continue;
    const t = nm(el); if (!t) continue;
    const k = el.tagName.toLowerCase() + '「' + t + '」'; seen[k] = (seen[k] || 0) + 1;
    const r = el.getBoundingClientRect();
    pos[k + (seen[k] > 1 ? '#' + seen[k] : '')] = [r.left + scrollX, r.top + scrollY];
  }
  return {open: open.map(t => nm(t) || t.getAttribute('aria-controls') || 'trigger'), pos};
}
"""


def expansion_shift(base, cur):
    """24：比默认状态多展开了一个控件，展开层以外的主要元素位移超过 8px。"""
    added = [o for o in cur['open'] if o not in base['open']]
    if not added:
        return []
    moved = []
    for k, (x, y) in cur['pos'].items():
        if k in base['pos']:
            bx, by = base['pos'][k]
            d = max(abs(x - bx), abs(y - by))
            if d > 8:
                moved.append((d, k))
    if not moved:
        return []
    moved.sort(reverse=True)
    names = '、'.join(f'{k} {round(d)}px' for d, k in moved[:3])
    return [{'type': '展开挤动了版面', 'where': '、'.join(added)[:36],
             'detail': f'展开后 {len(moved)} 个元素移动了（{names}）：展开层用覆盖层或预留空间，下方放不下时向上翻转；本来就该推开下面列表的折叠列表，在触发控件上写 data-expand="inline"'}]


def flat_glass(pg):
    """玻璃压在平涂底色上：把玻璃（连同里面的东西）临时藏起来，截它背后那块，5×3 网格取样；
    亮度极差 < 0.04 且颜色几乎不变，就是一块平涂底色，玻璃在那里只会是一块灰。"""
    import io
    try:
        from PIL import Image
    except ImportError:
        return []
    issues = []
    vw, vh = pg.viewport_size['width'], pg.viewport_size['height']
    for g in pg.evaluate(GLASS_JS):
        x0, y0 = max(0, g['x']), max(0, g['y'])
        x1, y1 = min(vw, g['x'] + g['w']), min(vh, g['y'] + g['h'])
        if x1 - x0 < 8 or y1 - y0 < 8:
            continue
        # 藏之前记下内联的 visibility（值和优先级），截完原样放回
        pg.evaluate("i => { const e = document.querySelector(`[data-vc-glass=\"${i}\"]`); e.__vcVis = [e.style.getPropertyValue('visibility'), e.style.getPropertyPriority('visibility')]; e.style.setProperty('visibility', 'hidden', 'important'); }", g['i'])
        try:
            png = pg.screenshot(clip={'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0})
        finally:
            pg.evaluate("i => { const e = document.querySelector(`[data-vc-glass=\"${i}\"]`); const [v, p] = e.__vcVis; if (v) e.style.setProperty('visibility', v, p); else e.style.removeProperty('visibility'); delete e.__vcVis; }", g['i'])
        im = Image.open(io.BytesIO(png)).convert('RGB')
        W, H = im.size
        pts = [im.getpixel((min(W - 1, int(W * (i + 0.5) / 5)), min(H - 1, int(H * (j + 0.5) / 3)))) for j in range(3) for i in range(5)]
        lum = [(0.299 * r + 0.587 * gg + 0.114 * b) / 255 for r, gg, b in pts]
        hue = max(max(abs(p[k] - pts[0][k]) for k in range(3)) for p in pts) / 255
        if max(lum) - min(lum) < 0.04 and hue < 0.06:
            issues.append({'type': '玻璃压在平涂底色上', 'where': g['name'] or 'glass',
                           'detail': f'背后亮度极差 {max(lum) - min(lum):.3f}：背后是一种颜色时玻璃只是一块灰，改成实色面；只给压在图片、视频、动效、滚动内容上的表面用玻璃'})
    pg.evaluate("() => document.querySelectorAll('[data-vc-glass]').forEach(e => e.removeAttribute('data-vc-glass'))")  # 做记号用的属性摘掉
    return issues


def metric_issues(m, theme, opts):
    """30、31：按阈值把 METRICS_JS 量到的数变成问题和提示（29、32 要跨变体、跨画板，在 main 里汇总）。"""
    issues, notices = [], []
    if theme == 'light' and m.get('band'):
        vh = m['band']['vh']
        g, a, b = m['band']['all']
        if vh and g / vh > opts['band']:
            issues.append({'type': '首屏空白带', 'where': f'y {a}–{b}', 'detail': f'连续 {g}px 没有文字、控件、图片，占视口高度 {vh} 的 {round(g / vh * 100)}%，上限 {round(opts["band"] * 100)}%：把内容或画面放进来，或者把首屏收矮'})
        else:
            g2, a2, b2 = m['band']['solid']
            if vh and g2 / vh > opts['band']:
                notices.append({'type': '首屏有一带只有动效画布', 'size': g2, 'where': f'y {a2}–{b2}', 'detail': f'连续 {g2}px（视口的 {round(g2 / vh * 100)}%）只被 canvas / [data-motion] 盖着：静态截图看不到它画了什么，用 capture_motion.py 截出动效帧、--reduced-motion 的静止帧和 --no-webgl 的兜底帧，确认这一带不是空的'})
    for f in m.get('faces', []):
        if f['ratio'] < opts['face_contrast']:
            issues.append({'type': '相邻两大块色面分不开', 'where': f"{f['a']} / {f['b']}"[:60], 'detail': f"{f['ca']} 和 {f['cb']} 对比 {f['ratio']:.2f}:1，要 ≥ {opts['face_contrast']:g}:1（各占视口 {f['pa']}%、{f['pb']}%）：两块是不同的面就把明度拉开或加描边，是同一块面就用同一个颜色"})
    return issues, notices


def third_party_fonts(src, requests):
    """向第三方取字体：源码里的链接和运行时的请求里出现已知的字体服务，或跨域的字体文件。只作提示。"""
    hosts = set()
    for u in re.findall(r'https?://[^\s"\'()<>]+', re.sub(r'<script type="text/x-dc".*?</script>', '', src, flags=re.S)) + list(requests):
        host = re.sub(r'^https?://', '', u).split('/')[0].lower()
        if host in FONT_HOSTS or (re.search(r'\.(woff2?|ttf|otf)(\?|$)', u) and u.startswith('http')):
            hosts.add(host)
    return [{'type': '向第三方取字体', 'where': h, 'detail': '访客每打开一次，浏览器就把 IP 和浏览器信息发给这家第三方（隐私；2022 年德国慕尼黑地方法院判过未经同意加载 Google Fonts 违反 GDPR）；多一次外部连接，连不上时掉回备用字体，截图和产品就不一样。把字体文件放到自己的域名下，或用系统字体栈'} for h in sorted(hosts)]


def discover_states(src):
    names = sorted(set(re.findall(r'<sc-if value="\{\{\s*(s\d+)\s*\}\}"', src)), key=lambda x: int(x[1:]))
    return names or [None]


def stage_labels(src):
    m = re.search(r'"options":\s*(\[[^\]]*\])', src)
    try:
        return json.loads(m.group(1)) if m else []
    except Exception:
        return []


def prop_variants(src, labels):
    """data-props 里的枚举属性（主题和画板状态的标签除外），每个非默认选项各算一个要查的变体，别的属性保持默认。"""
    m = re.search(r"data-props='([^']*)'", src)
    try:
        props = json.loads(m.group(1)) if m else {}
    except Exception:
        return []
    out = []
    for k, v in props.items():
        if k.startswith('$') or k == 'theme' or not isinstance(v, dict) or v.get('editor') != 'enum':
            continue
        if labels and v.get('options') == labels:
            continue
        out += [(f'{k}={o}', {k: o}) for o in v.get('options', []) if o != v.get('default')]
    return out


def board_meta(path, src):
    """画板的基准尺寸和类别：{'w', 'h', 'source', 'expand', 'fixed_root', 'fluid', 'doc', 'doc_why'}。
    尺寸：canvas.json → data-props 的 $preview → 390×844（source 记成 None，报告里写明）。
    fluid（流式页面）：canvas.json 里带 expand；或没有 canvas.json 条目、根节点不写死宽度、$preview 比一屏高出一半以上。
    doc（说明文档：组件表、旅程图）：只在带 expand 的画板上认。根节点写了 data-board="doc"，或没有 nav / main / footer / data-first-screen。"""
    m = {'w': 390, 'h': 844, 'source': None, 'expand': False}
    cj = os.path.join(os.path.dirname(os.path.abspath(path)), 'canvas.json')
    entry = None
    try:
        entry = json.load(open(cj, encoding='utf-8'))['boards'][os.path.basename(path)]
        m.update(w=int(entry['w']), h=int(entry['h']), source='canvas.json', expand=bool(entry.get('expand')))
    except Exception:
        pv = re.search(r'"\$preview"\s*:\s*\{\s*"width"\s*:\s*(\d+)\s*,\s*"height"\s*:\s*(\d+)', src)
        if pv:
            m.update(w=int(pv.group(1)), h=int(pv.group(2)), source='$preview')
    root = re.search(r'<[a-zA-Z][^<>]*\bdata-theme=[^<>]*>', src)
    root_tag = root.group(0) if root else ''
    m['fixed_root'] = bool(re.search(r'(?:^|[;"\s])width:\s*(?:[\d.]+|\{\{[^}]*\}\})px', root_tag))  # width: 390px 或 width: {{ w }}px
    m['fluid'] = m['expand'] or (entry is None and m['source'] == '$preview' and not m['fixed_root'] and m['h'] > fold_height(m['w']) * 1.5)
    kind = re.search(r'data-board="(doc|page)"', root_tag)
    landmarks = re.search(r'<(nav|main|footer)\b|data-first-screen', src)
    if kind:  # 只在带 expand 的画板上认：固定尺寸的产品画板不能靠写一个属性跳过检查
        m['doc'], m['doc_why'] = m['expand'] and kind.group(1) == 'doc', '带 expand，根节点写了 data-board="doc"'
    else:
        m['doc'] = m['expand'] and not landmarks
        m['doc_why'] = '带 expand，又没有 nav / main / footer / data-first-screen；是产品页面的话在根节点写 data-board="page"'
    return m


COLOR_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(')


def literal_colors(src):
    body = re.sub(r'<script type="text/x-dc".*?</script>', '', src, flags=re.S)
    body = re.sub(r'<link[^>]+>', '', body)
    hits = []
    for m in COLOR_RE.finditer(body):
        ctx = body[max(0, m.start() - 30):m.end() + 10]
        if 'var(--' in ctx[:30] and ',' in ctx:  # var(--x, #fff) 这样的兜底值
            continue
        if re.search(r'href=|src=|&#', ctx):
            continue
        hits.append(ctx.replace('\n', ' ').strip())
    return hits


INTERACTIVE_TAGS = ('a', 'button', 'input', 'select', 'textarea', 'label', 'summary')


def static_a11y(src):
    """源码里就能看出的「画出来不能用」：<a> 没有 href、非交互元素上挂点击、事件绑定写错。"""
    body = re.sub(r'<script.*?</script>', '', src, flags=re.S)
    out = []
    for m in re.finditer(r'<a\b([^>]*)>', body):
        if 'href=' not in m.group(1):
            text = re.sub(r'<[^>]*>?', '', body[m.end():m.end() + 120]).strip()[:20]
            out.append({'type': '控件不能用键盘到达', 'where': text or '<a>', 'detail': '<a> 没有 href，Tab 到不了；跳转用 <a href>，动作用 <button>'})
    for m in re.finditer(r'<(\w+)\b[^>]*\bonClick=', body, flags=re.I):
        if m.group(1).lower() not in INTERACTIVE_TAGS:
            out.append({'type': '控件不能用键盘到达', 'where': '<' + m.group(1) + '>', 'detail': '点击挂在非交互元素上；改成 <button>'})
    # 交互绑定写错：生成脚本把空值写成 {{ None }}，或 f-string 少了一层括号变成 { x }；点了没反应甚至报错
    for m in re.finditer(r'\bon[A-Z]\w*="(\{\{\s*(?:None|null|undefined)?\s*\}\}|\{(?!\{)[^"]*)"', body):
        out.append({'type': '交互绑定写错', 'where': m.group(0)[:40], 'detail': '事件绑定是空值或只有一层花括号；不跳转的按钮就不要写 onClick'})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--themes', default='light,dark')
    ap.add_argument('--only', default='', help='只查文件名包含这些词的画板，逗号分隔')
    ap.add_argument('--placeholders', default='示例,占位,待定,即将上线,敬请期待,TBD,TODO,Lorem,ipsum,二维码', help='出现在画板文字里就算问题的占位词，逗号分隔')
    ap.add_argument('--blob', action='append', default=[], metavar='ID=PATH',
                    help='画板里 /_blob/<ID> 引用的上传文件在本地的路径（例如共享样式表），可以写多次；不给的话这些样式读不到，会误报 token 没定义和触控过小')
    ap.add_argument('--size', action='append', default=[], metavar='NAME=WxH',
                    help='画板在另一个视口下再查一遍（例如手机画板在 320 宽下），可以写多次；名称可以不带 .dc.html，写 * 表示全部画板。'
                         '画板尺寸没找到（没有 canvas.json 也没有 $preview）时，第一个 --size 就是基准视口')
    ap.add_argument('--no-auto-sizes', action='store_true', help='不给流式页面自动加 390×844、320×568，不给手机画板自动加 320×568')
    ap.add_argument('--edge-tol', type=float, default=EDGE_TOL, help=f'跨画板内容左边缘的容差，px（默认 {EDGE_TOL}）')
    ap.add_argument('--empty-band', type=float, default=EMPTY_BAND_MAX, help=f'首屏空白带上限，占视口高度的比例（默认 {EMPTY_BAND_MAX}）')
    ap.add_argument('--face-area', type=float, default=FACE_MIN_AREA, help=f'一块色面至少占视口的比例（默认 {FACE_MIN_AREA}）')
    ap.add_argument('--face-contrast', type=float, default=FACE_MIN_CONTRAST, help=f'相邻色面的最低对比（默认 {FACE_MIN_CONTRAST}）')
    ap.add_argument('--tap-min', type=float, default=TAP_MIN, help=f'独立成行的可点元素的最小边长，px（默认 {TAP_MIN}）')
    ap.add_argument('--tap-floor', type=float, default=TAP_FLOOR, help=f'任何可点元素的最小边长，px（默认 {TAP_FLOOR}）')
    ap.add_argument('--max-font-sizes', type=int, default=MAX_FONT_SIZES, help=f'一块画板里字号种类的上限（默认 {MAX_FONT_SIZES}）')
    add_project_config_args(ap)
    cfg_path = apply_project_config(ap, sys.argv[1:])
    a = ap.parse_args()
    opts = {'band': a.empty_band, 'face_contrast': a.face_contrast}
    js_opts = json.dumps({'tapMin': a.tap_min, 'tapFloor': a.tap_floor, 'proseMin': PROSE_MIN_CHARS, 'faceArea': a.face_area, 'faceContrast': a.face_contrast})
    size_args = []
    for m in a.size:
        name, _, wh = m.partition('=')
        try:
            w_, h_ = (int(x) for x in wh.lower().split('x'))
        except ValueError:
            sys.exit(f'--size {m}：写成 名称=宽x高，例如 Mobile.dc.html=320x700')
        size_args.append((name, (w_, h_)))

    files = []
    for p in a.paths:
        files += sorted(glob.glob(os.path.join(p, '*.dc.html'))) if os.path.isdir(p) else [p]
    if a.only:
        keys = a.only.split(',')
        files = [f for f in files if any(k in os.path.basename(f) for k in keys)]
    if not files:
        sys.exit('没有找到 .dc.html 画板')
    extra_sizes, unknown = {}, []
    bases = [os.path.basename(f) for f in files]
    for name, wh in size_args:
        hit = bases if name == '*' else [b for b in bases if b in (name, name + '.dc.html')]
        if not hit:
            unknown.append(name)
        for b in hit:
            extra_sizes.setdefault(b, []).append(wh)
    if unknown:
        sys.exit('--size 的画板名没有对上：' + '、'.join(sorted(unknown)) + '（写文件名，例如 Main.dc.html 或 Main；* 表示全部）')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('需要 Python Playwright：pip install playwright && playwright install chromium')

    os.makedirs(a.out, exist_ok=True)
    report, total = [], 0
    edges = {}  # 视口宽度 → [(画板, 左边缘, 标题)]，查 29
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--allow-file-access-from-files'])  # 本地样式表的 cssRules 才读得到（查 23、查 token）
        logic_page = browser.new_page()  # 执行画板的 renderVals()，算出模板里的值
        for f in files:
            src = open(f, encoding='utf-8').read()
            for m in a.blob:
                bid, _, bpath = m.partition('=')
                if not bpath or not os.path.exists(bpath):
                    sys.exit(f'--blob {m}：本地文件不存在')
                src = src.replace('/_blob/' + bid, os.path.relpath(os.path.abspath(bpath), os.path.dirname(os.path.abspath(f))))
            meta = board_meta(f, src)
            is_doc = meta['doc']
            mine = list(extra_sizes.get(os.path.basename(f), []))
            if meta['source'] is None and mine:  # 尺寸没找到：第一个 --size 当基准，不按 390 宽跑
                meta.update(w=mine[0][0], h=mine[0][1], source='--size')
                mine = mine[1:]
            w, h = (meta['w'], fold_height(meta['w'])) if meta['fluid'] else (meta['w'], meta['h'])
            if not a.no_auto_sizes and not is_doc and not meta['fixed_root']:
                auto = FLUID_SIZES if meta['fluid'] else [sz for sz in FLUID_SIZES[-1:] if w < 744]
                mine += [sz for sz in auto if sz[0] < w and sz not in mine]
            notices = third_party_fonts(src, [])
            if meta['source'] is None:
                notices.append({'type': '画板尺寸没找到', 'where': '390×844', 'detail': '同目录没有 canvas.json（或里面没有这块画板），data-props 里也没有 $preview，按 390×844 查的；桌面画板这样查出来的竖排、超出画板都是假象。把 canvas.json 放到画板旁边，或用 --size 名称=宽x高 给出基准视口'})
            font_sizes, font_reqs = {}, set()
            labels = stage_labels(src)
            refs = set(re.findall(r'var\(--([\w-]+)', src))
            # file:// 下读不到外部样式表的规则，直接从链接的 css 文件和内联 <style> 里收集定义
            css_defined = set(re.findall(r'--([\w-]+)\s*:', re.sub(r'<script.*?</script>', '', src, flags=re.S)))
            for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', src):
                cp = os.path.join(os.path.dirname(os.path.abspath(f)), href)
                if not href.startswith(('http', '/')) and os.path.exists(cp):
                    css_defined |= set(re.findall(r'--([\w-]+)\s*:', open(cp, encoding='utf-8').read()))
            board_issues = [{'state': '源码', 'theme': '-', 'type': '写死的颜色', 'where': c, 'detail': ''} for c in literal_colors(src)]
            board_issues += [{'state': '源码', 'theme': '-', **i} for i in static_a11y(src)]
            board_hints = {}
            states = discover_states(src)
            variants = []
            for st in states:
                # 只打开这一个状态，别的状态显式关掉（renderVals() 算出的默认状态不能混进来）
                state = {k: k == st for k in states if k} if st else {}
                label = labels[int(st[1:])] if st and int(st[1:]) < len(labels) else (st or '默认')
                variants.append((label, state, {}, (w, h)))
            first_state = variants[0][1]
            variants += [(lbl, first_state, po, (w, h)) for lbl, po in prop_variants(src, labels if states[0] else [])]
            langs = [po for lbl, po in prop_variants(src, labels if states[0] else []) if 'lang' in po]
            for vw, vh in mine:
                variants.append((f'{vw}×{vh}', first_state, {}, (vw, vh)))
                variants += [(f'{vw}×{vh} lang={po["lang"]}', first_state, po, (vw, vh)) for po in langs]  # 窄屏最容易坏在另一种语言上
            pos_base = {}  # (宽, 高, 语言) → 第一个变体的元素位置，查 24
            for label, state, props_override, (vw, vh) in variants:
                for theme in a.themes.split(','):
                    if theme == 'pseudo' and 'lang' in props_override:
                        continue  # 伪语言模拟「换成更长的语言」，已经切到另一种语言的变体不再叠加
                    html = render_html(src, state, logic_values(src, state, logic_page, props_override))
                    manual_dark = theme == 'dark' and 'data-theme="light"' in html
                    if manual_dark:  # 手动选了深色、系统是浅色：最容易露出浅色 body 的情形
                        html = html.replace('data-theme="light"', 'data-theme="dark"')
                    fd, tmp = tempfile.mkstemp(prefix='.verify_', suffix='.html', dir=os.path.dirname(os.path.abspath(f)))
                    with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                        fh.write(html)
                    errors, net = [], []
                    pg = browser.new_page(viewport={'width': vw, 'height': vh}, reduced_motion='reduce',  # pseudo 按浅色查
                                          color_scheme='dark' if theme == 'dark' and not manual_dark else 'light')
                    pg.on('pageerror', lambda e: errors.append(str(e)[:120]))
                    pg.on('request', lambda rq: font_reqs.add(rq.url) if rq.url.startswith('http') else None)
                    pg.add_init_script('window.__vcOpts = ' + js_opts + '; window.__vcFluid = ' + ('true' if meta['fluid'] else 'false') + '; window.__dcHandlesEscape = ' + ('true' if 'Escape' in src else 'false'))
                    pg.on('console', lambda m: (net if 'net::' in m.text or 'Failed to load resource' in m.text else errors).append(m.text[:120]) if m.type == 'error' else None)
                    try:
                        pg.goto('file://' + tmp)
                        pg.wait_for_timeout(250)
                        if theme == 'pseudo':
                            pg.evaluate(PSEUDO_JS)
                            pg.wait_for_timeout(50)
                        res = pg.evaluate(CHECK_JS)
                        if theme == 'light':
                            for cls, lbl in (('is-press', '按下'), ('is-hover', '悬停')):
                                more = pg.evaluate(STATE_JS, cls)
                                res['issues'] += [{**i, 'type': '对比度不够（' + lbl + '）'} for i in more if i['type'] == '对比度不够']
                            pos = pg.evaluate(POS_JS)
                            pkey = (vw, vh, props_override.get('lang'))
                            if pkey in pos_base:
                                res['issues'] += expansion_shift(pos_base[pkey], pos)
                            else:
                                pos_base[pkey] = pos
                            shown = pg.evaluate('document.body.innerText')
                            for word in a.placeholders.split(','):
                                if word and word in shown:
                                    res['issues'].append({'type': '占位文字', 'where': word, 'detail': '对外页面不放占位符和过程说明'})
                        if theme == 'pseudo':
                            res['issues'] = [i for i in res['issues'] if i['type'] in LAYOUT_TYPES]
                            res['hints'] = []
                        elif not is_doc:  # 29–32：量一次，按阈值判
                            met = pg.evaluate(METRICS_JS)
                            more, note = metric_issues(met, theme, opts)
                            res['issues'] += more
                            for n in note:  # 同一类提示一块画板只留量到最大的那条
                                old = next((x for x in notices if x['type'] == n['type']), None)
                                if old is None:
                                    notices.append(n)
                                elif n['size'] > old['size']:
                                    notices[notices.index(old)] = n
                            if theme == 'light' and (vw, vh) == (w, h):  # 32：基准视口下各状态合并
                                for k, n in met['sizes'].items():
                                    font_sizes[k] = max(font_sizes.get(k, 0), n)
                            if theme == 'light' and not props_override and state == first_state and met.get('edge'):  # 29：每个视口的默认状态
                                edges.setdefault(vw, []).append((os.path.basename(f), met['edge']))
                        if theme == 'light':
                            if meta['fluid'] and (vw, vh) == (w, h):
                                pg.set_viewport_size({'width': vw, 'height': meta['h']})  # 一屏以下的玻璃也要查：整页高度下截
                                pg.wait_for_timeout(50)
                            res['issues'] += flat_glass(pg)
                    finally:
                        pg.close()
                        os.remove(tmp)
                    for hnt in res.get('hints', []):
                        board_hints.setdefault((hnt['sign'], hnt['where']), set()).add(label)
                    for i in res['issues']:
                        if is_doc and i['type'] in FIRST_SCREEN_TYPES:  # 说明文档类画板（组件表、旅程图）没有首屏
                            continue
                        board_issues.append({'state': label, 'theme': theme, **i})
                    if theme == a.themes.split(',')[0]:
                        for name in sorted(refs - {d[2:] for d in res['defined']} - css_defined):
                            board_issues.append({'state': label, 'theme': theme, 'type': '没定义的 token', 'where': '--' + name, 'detail': ''})
                    for e in errors:
                        board_issues.append({'state': label, 'theme': theme, 'type': '页面报错', 'where': e, 'detail': ''})
            if len(font_sizes) > a.max_font_sizes:
                kinds = sorted(font_sizes.items(), key=lambda kv: -float(kv[0]))
                board_issues.append({'state': '各状态合并', 'theme': 'light', 'type': '字号种类过多', 'where': f'{len(kinds)} 种',
                                     'detail': f'上限 {a.max_font_sizes} 种（{w}×{h}，各状态合并）：' + '、'.join(f'{float(k):g}px×{n}' for k, n in kinds) + '；把相近的并成一档，层级靠字号和字重拉开'})
            notices += [n for n in third_party_fonts('', font_reqs) if n not in notices]
            # 同一个问题在多个状态里重复出现时合并
            merged = {}
            for i in board_issues:
                k = (i['type'], i['where'], i['detail'])
                m = merged.setdefault(k, {**i, 'states': [], 'themes': []})
                m['states'].append(i['state'])
                if i['theme'] not in m['themes']:
                    m['themes'].append(i['theme'])
            items = list(merged.values())
            for i in items:
                i['theme'] = '、'.join(i['themes'])
            total += len(items)
            sizes_txt = '、'.join(f'{x}×{y}' for x, y in dict.fromkeys(v[3] for v in variants))
            info = {'viewports': [list(x) for x in dict.fromkeys(v[3] for v in variants)], 'size_source': meta['source'], 'fluid': meta['fluid'], 'doc': is_doc, 'doc_why': meta['doc_why'] if is_doc else '',
                    'line': f'查的视口：{sizes_txt}（基准来自 {meta["source"] or "默认值，尺寸没找到"}' + ('；流式页面，视口高度取一屏' if meta['fluid'] else '') + '）'
                            + (f'；按说明文档查（{meta["doc_why"]}），不查触控、首屏、空白带、色面、字号种类、左边缘' if is_doc else '')}
            report.append((os.path.basename(f), items, board_hints, notices, info))

        # 29：跨画板的内容左边缘。同一视口宽度下，各画板第一个 h1（没有就取第一屏第一个标题）的左边缘要一致
        cross = []
        for vw_, rows in sorted(edges.items(), reverse=True):
            lefts = [e['left'] for _, e in rows]
            if len(rows) > 1 and max(lefts) - min(lefts) > a.edge_tol:
                cross.append({'type': '跨画板的内容左边缘不一致', 'where': f'{vw_} 宽', 'theme': 'light', 'states': ['默认'], 'themes': ['light'],
                              'detail': f'相差 {max(lefts) - min(lefts):g}px，容差 {a.edge_tol:g}px：' + '；'.join(f'{b} {e["left"]:g}px（{e["tag"]}「{e["text"]}」）' for b, e in rows)
                                        + '。各页的内容容器用同一条边距公式；有意不对齐的标题写 data-edge="free"'})
        if cross:
            total += len(cross)
            report.append(('（跨画板）', cross, {}, [], {'line': '同一视口宽度下比各画板第一个标题的左边缘'}))

        browser.close()

    verdict = 'done' if total == 0 else 'needs_work'
    lines = [f'# 画板验证报告', '', f'**结论：{verdict}**（{total} 个问题，{len(files)} 块画板，主题：{a.themes}）', '',
             '只报能判对错的问题，每条给出位置和量出的数：会让用户看错、点不到、看不清的，以及带阈值的版面量度（首屏空白带、相邻色面、跨画板左边缘、字号种类）。构图和审美交给评审。', '',
             f'阈值：相邻色面 ≥ {a.face_contrast:g}:1（' + ('通用的下限，项目定了更高的门槛用 --face-contrast 调高' if a.face_contrast == FACE_MIN_CONTRAST else f'项目的门槛，高于通用的下限 {FACE_MIN_CONTRAST:g}:1' if a.face_contrast > FACE_MIN_CONTRAST else f'命令行放宽到低于通用的下限 {FACE_MIN_CONTRAST:g}:1') + f'）；首屏空白带 ≤ 视口的 {a.empty_band:.0%}；左边缘容差 {a.edge_tol:g}px；字号 ≤ {a.max_font_sizes} 种；点按区域 {a.tap_min:g} / {a.tap_floor:g}px。' + (f'阈值取自项目配置 {os.path.relpath(cfg_path)}，命令行参数优先。' if cfg_path else ''), '',
             '按说明文档跳过触控、首屏、空白带、色面、字号种类、左边缘的画板：' + ('；'.join(f'{n}（{inf["doc_why"]}）' for n, *_, inf in report if inf.get('doc')) or '没有') + '。', '']
    for name, items, hints, notices, info in report:
        lines.append(f'## {name}' + ('（通过）' if not items else f'（{len(items)}）'))
        lines += ['', info['line']]
        if notices:
            lines += ['', '提示（不影响结论）：'] + [f"- {n['type']}：{n['where']}。{n['detail']}" for n in notices]
        if items:
            lines += ['', '| 类型 | 位置 | 细节 | 主题 | 状态 |', '|---|---|---|---|---|']
            for i in sorted(items, key=lambda x: x['type']):
                st = '、'.join(dict.fromkeys(i['states']))
                lines.append(f"| {i['type']} | {i['where'].replace('|', '/')} | {i['detail']} | {i['theme']} | {st[:80]} |")
        if hints:
            lines += ['', '模板味信号（提示，不影响结论）：' + '；'.join(f'{k[0]}「{k[1]}」' for k in list(hints)[:12])]
        lines.append('')
    out = os.path.join(a.out, 'verify-canvas.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    json.dump({'verdict': verdict, 'boards': {n: it for n, it, *_ in report},
               'notices': {n: nt for n, _, _, nt, _ in report if nt}, 'meta': {n: inf for n, *_, inf in report},
               'hints': {n: [{'sign': k[0], 'where': k[1], 'states': sorted(v)} for k, v in h.items()] for n, _, h, *_ in report}}, open(os.path.join(a.out, 'verify-canvas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{verdict}: {total} 个问题 → {out}')
    sys.exit(0 if verdict == 'done' else 1)


if __name__ == '__main__':
    main()
