import json, sys, collections
p = sys.argv[1]
t = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)

def tok(group, name):
    for x in t[group]['tokens']:
        if x['name'] == name: return x
    raise KeyError(name)
def insert_after(group, after, new):
    L = t[group]['tokens']
    i = [x['name'] for x in L].index(after)
    L.insert(i + 1, collections.OrderedDict(new))

# ---- 颜色
tok('color', 'vc-hero-body')['value']['dark'] = '#48443b'
tok('color', 'vc-hero-body')['usage'] = '首页首屏左半（站稳）的底色。浅色下就是纸色；深色下降成暗纸，夜里不刺眼，和右半的墨色 vc-ink 至少 1.8:1（现在 1.88:1）。上面只放 vc-text（深色下 8.1:1）、vc-text-2（5.7:1）和 vc-moss（5.6:1）；vc-text-3 在深色的暗纸上只有 3.5:1，不用。'
tok('color', 'vc-paper')['usage'] = '站稳页和所有阅读区的底色（晨练），跟随浅色、深色主题。首页左半用 vc-hero-body。'
tok('color', 'vc-moss-hero')['usage'] = '动手页首屏色带和「动手」圆的底色。一屏最多一块。'
tok('color', 'vc-cinnabar')['usage'] = '看清页的强调色：链接、站内收录标记、当前所在的时代。只在墨底和强调面上用。墨底 6:1，深色的强调面 4.6:1。'
tok('color', 'vc-focus-on-dark')['usage'] = '深色底（首页墨色一半、看清和动手的首屏色带、强调面）上的焦点外圈；浅色主题下 vc-focus 在墨色上只有 2.96:1，换成这一档 ≥ 7:1。色带类（vc-band-ink、vc-band-moss、vc-nav-ink、vc-nav-moss、vc-feature）自带，别处用 .on-dark 套上。'
tok('color', 'vc-state-selected')['usage'] = '当前所在：导航的当前页、时代索引的当前时代、加载中的骨架块。'
tok('color', 'vc-seg-selected')['usage'] = '分段控件选中的一项（语言、外观、内容线），同时加粗。深色下纸面色和底几乎一样，所以提亮一档；上面的正文色 7.9:1。'
tok('color', 'vc-action')['usage'] = '纸底上的主按钮，胶囊形。一个区域最多一个。'
insert_after('color', 'vc-ink-line', [('name', 'vc-accent-surface'), ('value', collections.OrderedDict([('light', '#1d1b15'), ('dark', '#2c2d27')])),
    ('usage', '强调面：纸底页面上的强调卡（首页「最新文章」）。浅色下是墨色面（对纸 15:1）；深色下比页面底高一档，和 vc-paper 至少 1.3:1（现在 1.34:1），再加 1px vc-accent-line 描边。上面的字用 vc-on-ink 一组（深色下正文 11:1、次要 7.9:1、辅助 5.8:1），强调用 vc-cinnabar。')])
insert_after('color', 'vc-accent-surface', [('name', 'vc-accent-line'), ('value', collections.OrderedDict([('light', '#2e2a22'), ('dark', '#4b4c43')])),
    ('usage', '强调面和 404 三站入口色带（看清、动手两块）的 1px 描边。深色下对页面底 2.1:1，让墨色和苔绿的面在深色页面上有边。')])
insert_after('color', 'vc-amber', [('name', 'vc-orb-ring'), ('value', collections.OrderedDict([('light', '#b9d0b3'), ('dark', '#b9d0b3')])),
    ('usage', '「动手」圆的一圈 1px 亮边（内描边）。圆的苔绿对墨色只有 1.5:1、对深色的暗纸 1.2:1；亮边对墨色 11:1、对暗纸 6.1:1、对圆自己 7.3:1，图形边界 ≥ 3:1。')])

# ---- 字体
fam = t['type']['families']
t['type']['groups'] = [
 collections.OrderedDict([('name', '标题 · 无衬线（站稳、动手、首页左半）'), ('family', 'display'), ('styles', [
  collections.OrderedDict([('name','hero'),('fontSize','80px'),('lineHeight',1.08),('fontWeight',700),('letterSpacing','-0.025em'),('usage','第 1 级。首页左半的主标题。平板 64px（hero-tablet），手机 44px（hero-phone）。首屏倾斜时展开的一侧保持 80px，收起的一侧缩到 64px。'),('sample','先站稳')]),
  collections.OrderedDict([('name','title-1'),('fontSize','64px'),('lineHeight',1.12),('fontWeight',700),('letterSpacing','-0.02em'),('usage','第 2 级。分站首屏标题。手机 36px。'),('sample','和智能体一起，把想法做成能用的东西')]),
  collections.OrderedDict([('name','title-2'),('fontSize','40px'),('lineHeight',1.2),('fontWeight',700),('letterSpacing','-0.02em'),('usage','第 3 级。区块标题。手机 28px。'),('sample','AI 走得越快，越要先站稳')]),
  collections.OrderedDict([('name','title-3'),('fontSize','24px'),('lineHeight',1.3),('fontWeight',600),('usage','第 4 级。卡片标题、文章里的二级标题。手机 20px。'),('sample','Veli')]),
  collections.OrderedDict([('name','metric'),('fontSize','56px'),('lineHeight',1),('fontWeight',700),('letterSpacing','-0.03em'),('usage','阶梯以外唯一的一级：数字卡的大字（外行读得懂的量）。无衬线、tabular-nums，不用等宽。手机 40px。中文不超过 6 个字，英文不超过 12 个字符。'),('sample','少 23%')]),
 ])]),
 collections.OrderedDict([('name', '标题 · 衬线（看清、首页右半）'), ('family', 'serif'), ('styles', [
  collections.OrderedDict([('name','hero-serif'),('fontSize','80px'),('lineHeight',1.1),('fontWeight',600),('letterSpacing','-0.01em'),('usage','第 1 级。首页右半的主标题。平板 64px，手机 44px。'),('sample','再看清')]),
  collections.OrderedDict([('name','title-1-serif'),('fontSize','64px'),('lineHeight',1.12),('fontWeight',600),('usage','第 2 级。看清首屏色带上的站名。手机 36px。'),('sample','看清')]),
  collections.OrderedDict([('name','title-2-serif'),('fontSize','40px'),('lineHeight',1.25),('fontWeight',600),('usage','第 3 级。看清的区块标题、文章标题、强调卡的标题。手机 28px。'),('sample','改变路线的里程碑')]),
  collections.OrderedDict([('name','title-3-serif'),('fontSize','24px'),('lineHeight',1.35),('fontWeight',600),('usage','第 4 级。时代名、里程碑和文章卡片标题、文章里的二级标题。手机 20px。'),('sample','《Attention Is All You Need》')]),
 ])]),
 collections.OrderedDict([('name', '正文'), ('family', 'sans'), ('styles', [
  collections.OrderedDict([('name','lead'),('fontSize','19px'),('lineHeight',1.7),('fontWeight',400),('usage','第 5 级。首屏导语与区块开头的说明。每行不超过 32 个汉字。手机 17px。'),('sample','从 1950 年图灵的提问，到今天和智能体一起写代码。')]),
  collections.OrderedDict([('name','body-reading'),('fontSize','17px'),('lineHeight',1.8),('fontWeight',400),('usage','第 6 级。文章正文。中文版心 text-max 640px（每行约 37 字）、行高 1.8；英文同样 17px、行高 leading-latin 1.45、版心 text-max-en 580px（每行约 68 个字符）。'),('sample','判断先行：这一篇值得读，因为它说清了代价。')]),
  collections.OrderedDict([('name','body'),('fontSize','16px'),('lineHeight',1.7),('fontWeight',400),('usage','第 7 级。界面正文、卡片说明、按钮和导航文字。三档宽度都是 16px，不缩小。'),('sample','肌肉是存得下来的健康：老了少摔跤，现在更有精神。')]),
  collections.OrderedDict([('name','footnote'),('fontSize','13px'),('lineHeight',1.5),('fontWeight',400),('usage','第 8 级。出处、日期、页脚链接、分段控件、侧注和脚注。全站最小的字号。'),('sample','Cochrane 系统综述，2019 · 59 项试验')]),
  collections.OrderedDict([('name','kicker'),('fontSize','13px'),('lineHeight',1.4),('fontWeight',600),('letterSpacing','0.06em'),('usage','第 8 级的眉标：和脚注同号，靠字重 600 和字距 0.06em 区分。一屏最多一行。'),('sample','AGI 路上的陪练')]),
 ])]),
 collections.OrderedDict([('name', '等宽'), ('family', 'mono'), ('styles', [
  collections.OrderedDict([('name','meta-mono'),('fontSize','13px'),('lineHeight',1.4),('fontWeight',400),('letterSpacing','0.04em'),('usage','第 8 级的等宽元信息：年份、日期、类型、起止年份、代码块。和脚注同号，靠等宽字体和字距 0.04em 区分。'),('sample','2017 · 论文')]),
 ])]),
 collections.OrderedDict([('name', '手机和平板档（只改字号和行高，其余同上）'), ('family', 'display'), ('styles', [
  collections.OrderedDict([('name','hero-tablet'),('fontSize','64px'),('lineHeight',1.1),('fontWeight',700),('usage','744–1179px：hero 和 hero-serif 用这一档。'),('sample','先站稳')]),
  collections.OrderedDict([('name','hero-phone'),('fontSize','44px'),('lineHeight',1.15),('fontWeight',700),('usage','小于 744px：hero 和 hero-serif 用这一档。'),('sample','先站稳')]),
  collections.OrderedDict([('name','title-1-phone'),('fontSize','36px'),('lineHeight',1.2),('fontWeight',700),('usage','小于 744px：title-1 和 title-1-serif。'),('sample','看清')]),
  collections.OrderedDict([('name','title-2-phone'),('fontSize','28px'),('lineHeight',1.3),('fontWeight',700),('usage','小于 744px：title-2 和 title-2-serif。'),('sample','AI 走得越快，越要先站稳')]),
  collections.OrderedDict([('name','title-3-phone'),('fontSize','20px'),('lineHeight',1.4),('fontWeight',600),('usage','小于 744px：title-3 和 title-3-serif。'),('sample','Veli')]),
  collections.OrderedDict([('name','lead-phone'),('fontSize','17px'),('lineHeight',1.7),('fontWeight',400),('usage','小于 744px：lead。'),('sample','每周两次力量训练。')]),
  collections.OrderedDict([('name','metric-phone'),('fontSize','40px'),('lineHeight',1),('fontWeight',700),('usage','小于 744px：metric。'),('sample','少 23%')]),
 ])]),
]

# ---- 间距说明
tok('spacing','space-7')['usage'] = '桌面的页面边距（gutter-desktop）、正文和侧注之间。'
tok('spacing','space-8')['usage'] = '手机和平板上区块之间；页脚下方。'
tok('spacing','space-9')['usage'] = '桌面上区块之间。'
tok('spacing','space-10')['usage'] = '首屏的上下留白。'

# ---- 阴影
tok('shadow','shadow-modal')['usage'] = '原地展开的选项卡片、展开成表单的订阅条。'

# ---- 模糊
t['blur']['tokens'] = [
 collections.OrderedDict([('name','lg-blur'),('value','2px'),('usage','压在视频上的小块液态玻璃（播放条）的模糊。')]),
 collections.OrderedDict([('name','lg-blur-scroll'),('value','20px'),('usage','吸顶玻璃导航的模糊：背后滚过的是正文，要糊成色块。')]),
]

# ---- 尺寸
L = t['size']['tokens']
L[:] = [x for x in L if x['name'] != 'spine-width']
tok('size','control-height')['usage'] = '控件（按钮、导航项、分段控件、输入框、图标按钮）的最小高度。'
insert_after('size','control-height-lg',[('name','size-tap-min'),('value','44px'),('usage','点按区域的最小宽和高：页脚链接、面包屑、里程碑和日志的行（整行可点）、时代索引、文内独立成行的链接。句子里的链接不算。')])
tok('size','content-max')['usage'] = '页面内容的最大宽度。统一栅格的公式：内容容器的左右内边距 = max(gutter, (100vw − content-max) / 2)。'
tok('size','text-max-en')['value'] = '580px'
tok('size','text-max-en')['usage'] = '英文正文的版心。英文正文 17px、行高 1.45，每行约 68 个字符（A6：60–75）。中文仍用 text-max 640px、17px、行高 1.8，每行约 37 字。'
tok('size','breakpoint-tablet')['usage'] = '平板版式的起点：iPad mini 竖屏的宽度。低于它是手机版式。媒体查询里写死同值，并注明来自此 token。'
insert_after('size','breakpoint-desktop',[('name','breakpoint-nav-compact'),('value','360px'),('usage','导航窄于它时，语言分段控件收成一个按钮「中 / EN」。站标的叶子不收。')])
tok('size','nav-height')['usage'] = '胶囊导航的高度：44px 的控件加上下各 4px 内边距。'
tok('size','sidenote-width')['usage'] = '看清文章的侧注宽度。只在桌面版式（1180px 以上）出现，和正文之间隔 space-7；手机和平板放回文末作脚注。'

# ---- 行高（新族）
new = collections.OrderedDict()
for k, v in t.items():
    new[k] = v
    if k == 'easing':
        new['leading'] = collections.OrderedDict([('tokens', [collections.OrderedDict([('name','leading-latin'),('value','1.45'),('usage','英文导语、正文和文章正文的行高（A6：字号的 1.2–1.45 倍）。中文用各样式自己的行高。')])])])
t = new
t['meta']['release'] = 'v1.1 · 2026-11-12'
json.dump(t, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
