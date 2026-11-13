#!/usr/bin/env python3
"""验证者自己的测试：在一块故意做坏的画板上跑 verify_canvas.py，确认每一类真问题都抓得到、好的状态不误报。

改了 verify_canvas.py 的检查规则以后先跑它。画板在 tests/fixtures/Selftest.dc.html，每个状态放一类过去真实踩过的坑：
主按钮被输入区挡住或被挤扁、两栏里一栏被挤成竖排、flex 吞掉空格、深色模式下品牌色做文字看不清、<a> 没有 href、事件绑定写成 {{ None }} 和
只有图标的按钮、触控目标太小、对外页面留着「示例」这类占位；另有一个状态放 unslop 的模板味信号（emoji、感叹号、全大写加宽字距、特粗字重）。

用法：python selftest.py        通过时退出码 0，有漏报或误报时退出码 1。
      python selftest.py --static  只跑不用浏览器的检查（gate.py、check_shell.py、stale_terms.py），没装 Playwright 时用。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, '..', 'tests', 'fixtures')

# 状态名 → 必须报出的问题类型（主题为 None 表示浅色或深色都行）
EXPECT = {
    '主按钮被挡': [('主按钮被挡住或在首屏外', None), ('主按钮被挤扁', None)],
    '文字挤成竖排': [('文字被挤成竖排', None)],
    '弹性布局吞空格': [('弹性布局吞掉了空格', None)],
    '深色下对比度不够': [('对比度不够', 'dark')],
    '不能用键盘': [('控件没有可读名称', None)],
    '触控目标太小': [('触控目标小于 44', None)],
    '占位文字': [('占位文字', None)],
    '源码': [('控件不能用键盘到达', None), ('写死的颜色', None), ('交互绑定写错', None)],
}


def project_config_checks():
    """项目配置（design-bar.json）：从路径往上找、design/ 下也认、命令行参数优先、--no-project-config 关掉、写错了报错、不越过仓库根。"""
    import argparse
    sys.path.insert(0, HERE)
    import verify_canvas as vc
    failures = []
    root = tempfile.mkdtemp(prefix='cfg-selftest-')
    cwd = os.getcwd()

    def parser():
        ap = argparse.ArgumentParser()
        ap.add_argument('--face-contrast', type=float, default=vc.FACE_MIN_CONTRAST)
        ap.add_argument('--tap-min', type=float, default=vc.TAP_MIN)
        vc.add_project_config_args(ap)
        return ap

    def write(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(text)

    try:
        os.chdir(root)  # 当前目录也在查找范围里，换到临时目录免得读到别处的配置
        write(os.path.join(root, 'a', '.git', 'HEAD'), '')
        write(os.path.join(root, 'a', 'docs', 'design-bar.json'), '{"thresholds": {"face-contrast": 1.8, "edge-tol": 1}}')
        write(os.path.join(root, 'a', 'docs', 'boards', 'x.dc.html'), '')
        board = os.path.join(root, 'a', 'docs', 'boards')
        ap = parser()
        found = vc.apply_project_config(ap, [board, '--out', 'o'])
        if not found or ap.parse_args([]).face_contrast != 1.8:
            failures.append('项目配置：从画板目录往上找到 design-bar.json，face-contrast 应该是 1.8（不带命令行参数）')
        mt = argparse.ArgumentParser()
        mt.add_argument('--min-target', type=float, default=44)
        vc.add_project_config_args(mt)
        write(os.path.join(root, 'd', 'design-bar.json'), '{"thresholds": {"tap-min": 56}}')
        write(os.path.join(root, 'd', 'x.html'), '')
        vc.apply_project_config(mt, ['--project-config', os.path.join(root, 'd', 'design-bar.json')])
        if mt.parse_args([]).min_target != 56:
            failures.append('项目配置：tap-min 要落到 check_page.py 的 --min-target 上')
        if ap.parse_args([]).tap_min != vc.TAP_MIN:
            failures.append('项目配置：没写的阈值保持默认')
        if ap.parse_args(['--face-contrast', '1.5']).face_contrast != 1.5:
            failures.append('项目配置：命令行参数优先于配置')
        ap = parser()
        if vc.apply_project_config(ap, [board, '--no-project-config']) is not None or ap.parse_args(['--no-project-config']).face_contrast != vc.FACE_MIN_CONTRAST:
            failures.append('项目配置：--no-project-config 不读配置')
        write(os.path.join(root, 'b', '.git', 'HEAD'), '')
        write(os.path.join(root, 'b', 'design', 'design-bar.json'), '{"thresholds": {"face-contrast": 2}}')
        write(os.path.join(root, 'b', 'src', 'page.html'), '')
        ap = parser()
        if not vc.apply_project_config(ap, [os.path.join(root, 'b', 'src', 'page.html')]) or ap.parse_args([]).face_contrast != 2:
            failures.append('项目配置：design/design-bar.json 也要认，传文件路径也能往上找')
        write(os.path.join(root, 'design-bar.json'), '{"thresholds": {"face-contrast": 9}}')
        write(os.path.join(root, 'c', '.git', 'HEAD'), '')
        write(os.path.join(root, 'c', 'boards', 'x.dc.html'), '')
        os.chdir(os.path.join(root, 'c'))
        ap = parser()
        if vc.apply_project_config(ap, [os.path.join(root, 'c', 'boards')]) is not None:
            failures.append('项目配置：查找到仓库根（有 .git 的目录）为止，不读仓库外的配置')
        write(os.path.join(root, 'c', 'design-bar.json'), '{"thresholds": {"face-contrats": 1.8}}')
        try:
            vc.apply_project_config(parser(), [os.path.join(root, 'c', 'boards')])
            failures.append('项目配置：写错阈值名要报错，不能悄悄忽略')
        except SystemExit:
            pass
        tighter = {'face-contrast': 1.8, 'tap-min': 48, 'tap-floor': 28, 'edge-tol': 1, 'empty-band': 0.2, 'max-font-sizes': 6, 'face-area': 0.1}
        looser = {'face-contrast': 1.0, 'tap-min': 40, 'tap-floor': 20, 'edge-tol': 5, 'empty-band': 0.5, 'max-font-sizes': 12, 'face-area': 0.5}
        if set(tighter) != set(vc.PROJECT_CONFIG_KEYS) or set(looser) != set(vc.PROJECT_CONFIG_KEYS):
            failures.append('项目配置：每个阈值键都要有「更严的被接受、更松的报错」两条用例')
        for key in vc.PROJECT_CONFIG_KEYS:
            write(os.path.join(root, 'c', 'design-bar.json'), json.dumps({'thresholds': {key: tighter[key]}}))
            try:
                if not vc.apply_project_config(parser(), [os.path.join(root, 'c', 'boards')]):
                    failures.append(f'项目配置：{key} 定成更严的 {tighter[key]} 没读到配置')
            except SystemExit as e:
                failures.append(f'项目配置：{key} 定成更严的 {tighter[key]} 应该接受，实际报错：{e.code}')
            write(os.path.join(root, 'c', 'design-bar.json'), json.dumps({'thresholds': {key: looser[key]}}))
            try:
                vc.apply_project_config(parser(), [os.path.join(root, 'c', 'boards')])
                failures.append(f'项目配置：{key} 定成 {looser[key]}，比通用下限松，要报错退出')
            except SystemExit as e:
                if key not in str(e.code) or '通用下限' not in str(e.code):
                    failures.append(f'项目配置：{key} 放宽的报错要说清哪个阈值、下限多少：{e.code}')
        write(os.path.join(root, 'c', 'design-bar.json'), '{"thresholds": {"face-contrast": 1.3, "tap-min": 44}}')
        if not vc.apply_project_config(parser(), [os.path.join(root, 'c', 'boards')]):
            failures.append('项目配置：等于通用下限的值照收')
    finally:
        os.chdir(cwd)
        shutil.rmtree(root, ignore_errors=True)
    return failures


def static_checks():
    """不用浏览器的检查：gate.py、check_shell.py、stale_terms.py 的通用词汇表。"""
    failures = []

    def run(script, *args):
        r = subprocess.run([sys.executable, os.path.join(HERE, script), *args], capture_output=True, text=True)
        return r.returncode, r.stdout

    gate = os.path.join(FIXTURES, 'gate')
    code, _ = run('gate.py', os.path.join(gate, 'good.md'))
    if code != 0:
        failures.append(f'gate.py：填全的记分卡应该过、退出码 0，实际 {code}')
    code, txt = run('gate.py', os.path.join(gate, 'bad.md'))
    for want in ('自评不算', 'Delight and Fun：弱', 'Social Impact：档位要写', 'Visuals and Graphics：中，但没写证据', '参照只有 1 个',
                 '入口第一屏：没填位置', '找不到 evidence/missing.mp4', '今天开练：3 步', '建档：测法是「画板估算」', '看回顾：点按次数要写一个整数'):
        if want not in txt:
            failures.append(f'gate.py：做坏的记分卡应该报「{want}」')
    if code != 1:
        failures.append(f'gate.py：做坏的记分卡应该退出码 1，实际 {code}')
    code, _ = run('gate.py', os.path.join(HERE, '..', 'assets', 'project-template', 'design', 'scorecard.md'))
    if code != 1:
        failures.append('gate.py：没填的模板不该过')

    for name, want in (('no-sign', '缺「动效原型：签名时刻」'), ('no-entry', '缺「动效原型：入口第一屏」'), ('blank-reviewer', '没写评审人')):
        code, txt = run('gate.py', os.path.join(gate, name + '.md'))
        if code != 1 or want not in txt:
            failures.append(f'gate.py：{name}.md 应该不过并报「{want}」，实际 {code}')

    shell = os.path.join(FIXTURES, 'shell')
    cfg = os.path.join(shell, 'shell.json')
    code, txt = run('check_shell.py', os.path.join(shell, 'good'), '--config', cfg)
    if code != 0:
        failures.append(f'check_shell.py：做对的外壳应该过（训练屏写死深色在 fixedAllow 里），实际 {code}：{txt[:300]}')
    code, txt = run('check_shell.py', os.path.join(shell, 'bad'), '--config', cfg)
    for want in ('| 主题跟随系统 |', '| 根元素写死主题 | ', '存储键 fam-theme', '存储键 fam-lang', '没有链到 / 的链接', '/b 在源码里没出现', '没有 aria-current'):
        if want not in txt.split('## 过')[0]:
            failures.append(f'check_shell.py：做坏的外壳应该报「{want.strip("| ")}」')
    if '/a 在源码里没出现' in txt or code != 1:
        failures.append(f'check_shell.py：做坏的外壳退出码应该是 1，/a 出现了不该报，实际 {code}')
    code, _ = run('check_shell.py', os.path.join(shell, 'bad'))
    if code != 1:
        failures.append('check_shell.py：不给配置时也要查主题跟随系统和根元素写死主题')

    code, txt = run('check_shell.py', os.path.join(shell, 'bad-classlist'))
    if code != 1 or '根元素写死主题' not in txt.split('## 过')[0]:
        failures.append('check_shell.py：顶层无条件 classList.add(\'dark\') 应该报根元素写死主题')

    must = {'negated-getitem', 'negated-bare-matchmedia', 'negated-null', 'other-key', 'other-media', 'not-equal-value', 'null-on-left', 'wrapped-typeof', 'wrapped-string', 'wrapped-default'}
    if not must <= set(os.listdir(os.path.join(shell, 'bad-guard'))):
        failures.append(f'check_shell.py：bad-guard 缺夹具 {"、".join(sorted(must - set(os.listdir(os.path.join(shell, "bad-guard")))))}')
    for name in sorted(os.listdir(os.path.join(shell, 'bad-guard'))):
        sub = os.path.join(shell, 'bad-guard', name)
        extra = ('--config', os.path.join(sub, 'shell.json')) if os.path.isfile(os.path.join(sub, 'shell.json')) else ()
        code, txt = run('check_shell.py', sub, *extra)
        if code != 1 or '| 根元素写死主题 |' not in txt.split('## 过')[0]:
            failures.append(f'check_shell.py：bad-guard/{name} 无条件写死根主题，应该报根元素写死主题，实际 {code}')

    good_guard = os.path.join(shell, 'good-guard')
    for name in sorted(os.listdir(good_guard)):
        sub = os.path.join(good_guard, name)
        code, txt = run('check_shell.py', sub)
        if code != 0 or '| 根元素写死主题 |' in txt.split('## 过')[0]:
            failures.append(f'check_shell.py：good-guard/{name} 的守卫是对的（含 !matchMedia(…).matches 写 light），不该报写死主题，实际 {code}')

    failures += project_config_checks()

    d = tempfile.mkdtemp(prefix='stale-selftest-')
    phrase = '不随' + '系统切换'  # 拆开写，免得技能自己的文件命中通用词汇表
    open(os.path.join(d, 'g.md'), 'w', encoding='utf-8').write('| 废弃说法 | 现在的说法 | 依据 |\n|---|---|---|\n| 旧名 | 新名 | x |\n')
    open(os.path.join(d, 'doc.md'), 'w', encoding='utf-8').write(f'浅色界面在根元素加 data-theme，{phrase}。\n')
    code, txt = run('stale_terms.py', '--glossary', os.path.join(d, 'g.md'), os.path.join(d, 'doc.md'))
    if code != 1 or phrase not in txt:
        failures.append('stale_terms.py：通用词汇表里的「主题不跟系统」应该命中')
    code, _ = run('stale_terms.py', '--glossary', os.path.join(d, 'g.md'), '--no-canon', os.path.join(d, 'doc.md'))
    if code != 0:
        failures.append('stale_terms.py：--no-canon 时不该再读通用词汇表')
    code, txt = run('stale_terms.py', '--glossary', os.path.join(d, 'g.md'), os.path.join(HERE, '..'))
    if code != 0:
        failures.append('stale_terms.py：技能自己的文件不该命中通用词汇表：' + txt[-300:])
    return failures


def main():
    if '--static' in sys.argv:
        failures = static_checks()
        if failures:
            print('selftest --static 不通过：\n  ' + '\n  '.join(failures))
            sys.exit(1)
        print('selftest --static 通过：gate.py（填全的、做坏的、没填的模板）、check_shell.py（做对的、做坏的、守卫形态的反例、不给配置）、stale_terms.py 的通用词汇表、项目配置（design-bar.json）都对')
        return
    out = tempfile.mkdtemp(prefix='verify-selftest-')
    subprocess.run([sys.executable, os.path.join(HERE, 'verify_canvas.py'), '--no-project-config', FIXTURES, '--out', out, '--size', 'SelftestProps.dc.html=320x600'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = json.load(open(os.path.join(out, 'verify-canvas.json'), encoding='utf-8'))
    items = data['boards']['Selftest.dc.html']
    found = {(st, i['type'], th) for i in items for st in i['states'] for th in i['theme'].split('、')}

    failures = []
    for state, wants in EXPECT.items():
        for typ, theme in wants:
            ok = any(s == state and t == typ and (theme is None or th == theme) for s, t, th in found)
            if not ok:
                failures.append(f'漏报：「{state}」应该报「{typ}」' + (f'（{theme}）' if theme else ''))
    hints = {(h['sign'], st) for h in data.get('hints', {}).get('Selftest.dc.html', []) for st in h['states']}
    for sign in ('emoji', '感叹号', '全大写加宽字距', '特粗字重'):
        if (sign, '模板味信号') not in hints:
            failures.append(f'漏提示：「模板味信号」应该提示「{sign}」')
    if any(st == '好的画板' for _, st in hints):
        failures.append('误提示：「好的画板」不该有模板味信号')
    false_pos = sorted({t for s, t, _ in found if s == '好的画板'})
    for t in false_pos:
        failures.append(f'误报：「好的画板」不该报「{t}」')

    # 属性的每个选项、额外视口各查一遍：英文版里的占位词、320 宽下超出画板；默认的中文、390 宽不误报
    props_items = data['boards']['SelftestProps.dc.html']
    pfound = {(st, i['type']) for i in props_items for st in i['states']}
    for st, typ in (('lang=English', '占位文字'), ('320×600', '内容超出画板')):
        if (st, typ) not in pfound:
            failures.append(f'漏报：SelftestProps「{st}」应该报「{typ}」')
    for st, typ in sorted(pfound):
        if st == '默认':
            failures.append(f'误报：SelftestProps 默认状态不该报「{typ}」')
    if any(st.startswith('theme=') for st, _ in pfound):
        failures.append('误查：theme 属性由 --themes 负责，不该再按属性查一遍')

    # 几何：展开层出区块、可点元素被盖住、首屏主操作在视口外、深色下露出浅色底
    g = data['boards']['SelftestGeometry.dc.html']
    gfound = {(st, i['type'], th) for i in g for st in i['states'] for th in i['theme'].split('、')}
    for st, typ, th in (('case=展开层超出', '展开层超出所在区块', None), ('case=被盖住', '可点元素被盖住', None),
                        ('case=首屏外', '首屏主操作在视口外', None), ('case=深色露底', '深色下露出浅色底', 'dark'),
                        ('case=按钮折行', '按钮文字折行', None), ('case=浮层无出路', '浮层没有出路', None), ('case=孤字', '孤字成行', None),
                        ('case=词中断行', '词中断行', None), ('case=冲出容器', '文字冲出容器', None),
                        ('case=玻璃平涂', '玻璃压在平涂底色上', None), ('case=背景声明不成立', '玻璃的背景声明不成立', None),
                        ('case=没有状态样式', '可点元素没有悬停或按下样式', None), ('case=混排断行', '词中断行', None),
                        ('case=展开挤动', '展开挤动了版面', None), ('case=写死宽度', '画板比视口宽', None), ('case=字太多', '首屏要读的字太多', None), ('case=站标不回首页', '站标不回首页', None), ('case=笼统进度', '笼统的进度文字', None),
                        ('case=头图后首屏外', '首屏主操作在视口外', None)):  # 固定尺寸的画板：第一个 section 从半屏以下开始也照查
        if not any(s_ == st and t_ == typ and (th is None or h_ == th) for s_, t_, h_ in gfound):
            failures.append(f'漏报：SelftestGeometry「{st}」应该报「{typ}」')
    if any(s_ == 'case=玻璃有图' and t_ == '玻璃压在平涂底色上' for s_, t_, _ in gfound):
        failures.append('误报：SelftestGeometry「case=玻璃有图」背后有图案，不该报「玻璃压在平涂底色上」')
    for st, typ in (('case=背景声明成立', '玻璃的背景声明不成立'), ('case=背景声明成立', '玻璃压在平涂底色上'), ('case=展开不挤', '展开挤动了版面'), ('case=新色彩写法', '对比度不够'), ('case=新色彩写法', '颜色算不了')):
        if any(s_ == st and t_ == typ for s_, t_, _ in gfound):
            failures.append(f'误报：SelftestGeometry「{st}」不该报「{typ}」')
    mixed = [i for i in g if 'case=混排断行' in i['states'] and i['type'] == '词中断行']
    if not any(i['detail'].startswith('手写') for i in mixed) or not any(i['detail'].startswith('「AI」') for i in mixed):
        failures.append('漏报：SelftestGeometry「case=混排断行」的手写 <br> 和自动折行都应该报「AI 发展史」被拆开')
    for s_, t_, h_ in sorted(gfound):
        if s_ == '默认' and t_ != '写死的颜色':
            failures.append(f'误报：SelftestGeometry 默认状态不该报「{t_}」')

    # 首屏、色面、点按区域、字号（SelftestSurface）：每个 case 只报它那一类，好的写法不报
    sf = data['boards']['SelftestSurface.dc.html']
    sfound = {(st, i['type'], th) for i in sf for st in i['states'] for th in i['theme'].split('、')}
    for st, typ, th in (('case=空白带', '首屏空白带', 'light'), ('case=骨架之外的空带', '首屏空白带', 'light'),  # 骨架只豁免它自己占的那一块，容器之外真空着的带照报
                         ('case=色面分不开', '相邻两大块色面分不开', 'light'), ('case=深色色面分不开', '相邻两大块色面分不开', 'dark'),
                        ('case=链接太矮', '触控目标小于 44', None), ('case=链接太矮', '点按区域小于 24', None), ('case=可点太小', '点按区域小于 24', None),
                        ('各状态合并', '字号种类过多', None)):
        if not any(s_ == st and t_ == typ and (th is None or h_ == th) for s_, t_, h_ in sfound):
            failures.append(f'漏报：SelftestSurface「{st}」应该报「{typ}」' + (f'（{th}）' if th else ''))
    # 行内例外的边界：只放过 p、li > span 里够长的句子中间的链接。短句、div、li > a 的行标题、td、页脚里的句子都照报；
    # 伪元素或子元素撑大的热区要真的点得到（pointer-events: none 的不算），并且盖得住目标尺寸的方块
    for st in ('case=短句链接', 'case=块里的句中链接', 'case=行标题链接', 'case=表格里的句中链接', 'case=页脚里的句子', 'case=热区点不到',
               'case=子元素点不到', 'case=细条热区', 'case=窄条热区', 'case=热区正中被盖住',
               'case=热区只到 40', 'case=十字形热区', 'case=偏心窄条', 'case=热区缺一块', 'case=内层滚动容器',  # 只撑到 40×40、四个角缺着、偏在一侧、上边缺 19px 的都盖不住目标方块；滚动容器里一屏以下的小链接也量得到
               # 子元素撑大的热区同样要点得到；只伸出一条 2px 或 22px 宽的条，盖不住目标方块；每条边正中那一点必须点得到
               'case=行内块链接', 'case=整段是链接', 'case=零高度的链接'):  # 行内显示才算句中；链接以外的字数不把链接自己的字算进去
        if not any(s_ == st and t_ in ('触控目标小于 44', '点按区域小于 24') for s_, t_, _ in sfound):
            failures.append(f'漏报：SelftestSurface「{st}」的链接应该报点按区域（不在行内例外里）')
    if any(s_ == 'case=加粗里的句中链接' and t_ in ('触控目标小于 44', '点按区域小于 24') for s_, t_, _ in sfound):
        failures.append('误报：SelftestSurface「case=加粗里的句中链接」verify_canvas.py 按祖先判（原来就是），p > strong > a 的句中链接不该报')
    for st in ('case=色面透明阴影', 'case=色面悬停阴影', 'case=色面同色描边'):  # 全透明的阴影（有模糊、有偏移的也一样）、和面同色的描边都没把边界画出来
        if not any(s_ == st and t_ == '相邻两大块色面分不开' for s_, t_, _ in sfound):
            failures.append(f'漏报：SelftestSurface「{st}」看不见的阴影或描边不算分开，应该报「相邻两大块色面分不开」')
    if any(s_ == 'case=色面有描边' and t_ == '相邻两大块色面分不开' for s_, t_, _ in sfound):
        failures.append('误报：SelftestSurface「case=色面有描边」带 box-shadow 的面算已经分开，不该报「相邻两大块色面分不开」')
    for st, typ, th in (('case=深色色面分不开', '相邻两大块色面分不开', 'light'), ('case=色面分不开', '相邻两大块色面分不开', 'dark'), ('case=动效带', '首屏空白带', None),
                        ('case=骨架加载态', '首屏空白带', None), ('case=骨架占位块', '首屏空白带', None),  # aria-busy 的容器、data-skeleton 和类名带 skeleton 的占位块都是加载态，不是空白
                        ('case=句中链接', '触控目标小于 44', None), ('case=句中链接', '点按区域小于 24', None), ('case=热区撑大', '触控目标小于 44', None), ('case=热区撑大', '点按区域小于 24', None),
                        ('case=子元素撑大热区', '触控目标小于 44', None), ('case=子元素撑大热区', '点按区域小于 24', None),
                        ('case=热区有细缝', '触控目标小于 44', None), ('case=热区有细缝', '点按区域小于 24', None),  # 两个取样点之间 3px 的缝在声明的精度以内，量不出来
                        ('case=内层滚动容器', '首屏空白带', None),  # 量完一屏以下的链接，滚动容器要放回原处
                        ('case=画成悬停态的块', '首屏空白带', None)):  # 本来就带 is-hover 的元素，查完悬停态以后类名还在
        if any(s_ == st and t_ == typ and (th is None or h_ == th) for s_, t_, h_ in sfound):
            failures.append(f'误报：SelftestSurface「{st}」不该报「{typ}」' + (f'（{th}）' if th else ''))
    for s_, t_, _ in sorted(sfound):
        if s_ == '默认' and t_ != '写死的颜色':
            failures.append(f'误报：SelftestSurface 默认状态不该报「{t_}」')
    sizes_item = next((i for i in sf if i['type'] == '字号种类过多'), None)
    if sizes_item and '11px×1' not in sizes_item['detail']:
        failures.append('「字号种类过多」要列出每种字号和次数')
    notes = {b: {n['type'] for n in ns} for b, ns in data.get('notices', {}).items()}
    if '首屏有一带只有动效画布' not in notes.get('SelftestSurface.dc.html', set()):
        failures.append('漏提示：SelftestSurface「case=动效带」只有 canvas 盖着的一带应该提示「首屏有一带只有动效画布」')
    if '向第三方取字体' not in notes.get('SelftestFluid.dc.html', set()) or '向第三方取字体' in notes.get('SelftestSurface.dc.html', set()):
        failures.append('「向第三方取字体」应该只提示 SelftestFluid（样式里引了 fonts.gstatic.com）')

    # 流式页面（SelftestFluid，canvas.json 里带 expand）：不加 --size 也在 390、320 宽下各查一遍，视口高度取一屏，一屏以下的链接也量
    fl = data['boards']['SelftestFluid.dc.html']
    ffound = {(st, i['type']) for i in fl for st in i['states']}
    if data['meta']['SelftestFluid.dc.html']['viewports'] != [[1200, 900], [390, 844], [320, 568]]:
        failures.append(f"流式页面应该查 1200×900、390×844、320×568，实际 {data['meta']['SelftestFluid.dc.html']['viewports']}")
    for st, typ in (('320×568', '内容超出画板'), ('默认', '触控目标小于 44'), ('默认', '可点元素被盖住')):  # 被盖住的入口在一屏以下：滚到视口里再量
        if (st, typ) not in ffound:
            failures.append(f'漏报：SelftestFluid「{st}」应该报「{typ}」')
    for st, typ in sorted(ffound):
        if typ not in ('写死的颜色', '触控目标小于 44', '可点元素被盖住') and st != '320×568':  # 流式页面里从半屏以下开始的 section 不算首屏，里面的按钮不报「首屏主操作在视口外」
            failures.append(f'误报：SelftestFluid「{st}」不该报「{typ}」')
    cross = data['boards'].get('（跨画板）', [])
    edge = next((i for i in cross if i['type'] == '跨画板的内容左边缘不一致' and i['where'] == '390 宽'), None)
    if not edge or 'SelftestFluid.dc.html 32px' not in edge['detail'] or 'SelftestSurface.dc.html 20px' not in edge['detail']:
        failures.append('漏报：390 宽下 SelftestFluid（32px）和 SelftestSurface（20px）的第一个标题左边缘不一致，要列出每块的值')
    if any(i['where'] != '390 宽' for i in cross):
        failures.append('误报：只有 390 宽下有两块以上的画板可比，别的宽度不该报左边缘不一致')

    # 画板尺寸从哪来（--size 没生效的那次）：没有 canvas.json 时读 $preview；都没有时写明，并拿第一个 --size 当基准，不悄悄按 390 宽跑
    def run_meta(board, *extra):
        d = tempfile.mkdtemp(prefix='verify-size-')
        shutil.copy(os.path.join(FIXTURES, board), d)
        o = os.path.join(d, 'out')
        r = subprocess.run([sys.executable, os.path.join(HERE, 'verify_canvas.py'), '--no-project-config', d, '--out', o, '--themes', 'light', *extra], capture_output=True, text=True)
        try:
            j = json.load(open(os.path.join(o, 'verify-canvas.json'), encoding='utf-8'))
        except OSError:
            return {'viewports': [], 'size_source': r.stderr.strip()[-200:]}, set()
        return j['meta'][board], {n['type'] for n in j.get('notices', {}).get(board, [])}
    # data-board="doc" 只在带 expand 的画板上认：固定尺寸的画板写了也照查
    d = tempfile.mkdtemp(prefix='verify-doc-')
    src = open(os.path.join(FIXTURES, 'SelftestSurface.dc.html'), encoding='utf-8').read().replace('data-first-screen', 'data-board="doc" data-first-screen', 1)
    open(os.path.join(d, 'SelftestSurface.dc.html'), 'w', encoding='utf-8').write(src)
    json.dump({'boards': {'SelftestSurface.dc.html': {'w': 390, 'h': 600}}}, open(os.path.join(d, 'canvas.json'), 'w', encoding='utf-8'))
    subprocess.run([sys.executable, os.path.join(HERE, 'verify_canvas.py'), '--no-project-config', d, '--out', os.path.join(d, 'out'), '--themes', 'light'], capture_output=True, text=True)
    try:
        j = json.load(open(os.path.join(d, 'out', 'verify-canvas.json'), encoding='utf-8'))
        if j['meta']['SelftestSurface.dc.html']['doc'] or not any(i['type'] == '点按区域小于 24' for i in j['boards']['SelftestSurface.dc.html']):
            failures.append('固定尺寸的画板写了 data-board="doc" 不该跳过检查（只在带 expand 的画板上认）')
    except (OSError, KeyError) as e:
        failures.append(f'data-board 的用例没跑出报告：{e}')
    if not data['meta']['SelftestSurface.dc.html'].get('doc') is False or '按说明文档跳过' not in open(os.path.join(out, 'verify-canvas.md'), encoding='utf-8').read():
        failures.append('报告开头要列出按说明文档跳过检查的画板（没有时写「没有」）')

    m, _ = run_meta('SelftestFluid.dc.html')
    if m['size_source'] != '$preview' or m['viewports'][:1] != [[1200, 900]] or [390, 844] not in m['viewports']:
        failures.append(f'没有 canvas.json 时应该按 $preview 的 1200 宽查、并自动加窄视口，实际 {m}')
    m, n = run_meta('SelftestProps.dc.html')
    if m['size_source'] is not None or '画板尺寸没找到' not in n:
        failures.append(f'没有 canvas.json 也没有 $preview 时应该提示「画板尺寸没找到」，实际 {m}、{n}')
    m, n = run_meta('SelftestProps.dc.html', '--size', 'SelftestProps=1200x800')
    if m['viewports'][:1] != [[1200, 800]] or [390, 844] in m['viewports'] or '画板尺寸没找到' in n:
        failures.append(f'尺寸没找到时 --size SelftestProps=1200x800 应该成为基准视口（名称可以不带 .dc.html），不再按 390 宽跑，实际 {m}')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'verify_canvas.py'), '--no-project-config', FIXTURES, '--out', out, '--size', 'Nope=320x600'], capture_output=True, text=True)
    if r.returncode == 0 or '没有对上' not in r.stderr:
        failures.append('--size 的画板名写错应该报错退出')

    # capture_motion.py --no-webgl：挂载代码拿不到 WebGL 改了 state，模板要按新的 state 重新渲染，兜底画面才截得到
    shot = os.path.join(out, 'nogl.png')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'capture_motion.py'), os.path.join(FIXTURES, 'motion', 'Fallback.dc.html'), shot,
                        '--no-webgl', '--expect', '[data-fallback]', '--wait', '100', '--size', '600x400'], capture_output=True, text=True)
    try:
        info = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        info = {}
    if r.returncode != 0 or info.get('rerendered') != ['noGL'] or not info.get('expect'):
        failures.append(f'capture_motion.py --no-webgl 应该截到兜底画面（rerendered 含 noGL，--expect 找得到），实际退出码 {r.returncode}：{(r.stdout + r.stderr).strip()[-200:]}')

    # check_page.py：同一套点按区域、首屏空白带、相邻色面在真实页面上也抓得到（tests/fixtures/pages/bad.html）
    cp = tempfile.mkdtemp(prefix='check-page-selftest-')
    subprocess.run([sys.executable, os.path.join(HERE, 'check_page.py'), '--no-project-config', os.path.join(FIXTURES, 'pages', 'bad.html'), '--out', cp, '--dark', '--widths', '375,1440'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        rep = json.load(open(os.path.join(cp, 'report.json'), encoding='utf-8'))
        w375, w1440 = rep['widths']['375'], rep['widths']['1440']
        if not any('关于' in t for t in w375['tinyTargets']) or not any('关于' in t for t in w1440['tinyTargets']):
            failures.append('check_page.py：页脚 16px 高的链接在手机和桌面宽度下都应该报短边 < 24')
        if any('更新记录' in t for t in w375['tinyTargets'] + w375['smallTargets']):
            failures.append('check_page.py：一句话中间的行内链接不该报点按区域')
        # 不到 12 个字的短句、div 里、页脚里、夹一层 strong / em（直接父元素不是原来放过的那几种）、inline-block、整段是链接：都不在行内例外里
        for name in ('短句里的链接', '块里的链接', '页脚句子里的链接', '加粗里的链接', '强调里的链接', '行内块链接', '整段就是一个很长的链接', '差一点',  # 43.7px 也算不到 44
                     '伪元素点不到', '子元素点不到', '细条热区', '窄条热区', '正中被盖住', '只到四十', '十字形热区', '偏心窄条', '缺一块的'):  # 撑大的部分点不到、只伸出一条比目标尺寸窄的条（2px、22px）、或上边正中被别的元素盖住，照盒子量
            if not any(name in t for t in w375['tinyTargets'] + w375['smallTargets']):
                failures.append(f'check_page.py：「{name}」应该报点按区域（不在行内例外里）')
        for name in ('伪元素撑大', '子元素撑大', '有细缝的'):  # 伪元素或子元素把热区撑到 44×44、点得到的，按撑大后的量；3px 的缝在声明的精度以内
            if any(name in t for t in w375['tinyTargets'] + w375['smallTargets']):
                failures.append(f'check_page.py：「{name}」的热区撑到了 44×44，不该报点按区域')
        if not w375['emptyBand'] or not w1440['emptyBand']:
            failures.append('check_page.py：首屏 50vh 的空带应该报「首屏空白带」')
        if w375['flatFaces'] or not rep['dark']['375'] or len(rep['dark']['375']) != 1:
            failures.append('check_page.py：相邻色面应该只在深色下报一条（浅色分得开）')
    except (OSError, KeyError) as e:
        failures.append(f'check_page.py 没有产出 report.json 或缺字段：{e}')

    # check_page.py 量热区会把元素滚到视口里：滚动发生在 main { overflow: auto } 里的应用外壳，量完要把容器放回原处，
    # 不然后面的首屏空白带是在滚过的画面上量的（铺满文字的首屏误报、真空着的首屏漏报）
    for page_name, want_band in (('shell-good.html', False), ('shell-empty.html', True)):
        sd = tempfile.mkdtemp(prefix='check-page-selftest-')
        subprocess.run([sys.executable, os.path.join(HERE, 'check_page.py'), '--no-project-config', os.path.join(FIXTURES, 'pages', page_name), '--out', sd, '--widths', '375'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            w375 = json.load(open(os.path.join(sd, 'report.json'), encoding='utf-8'))['widths']['375']
            if not any('更早' in t for t in w375['tinyTargets']):
                failures.append(f'check_page.py：{page_name} 滚动容器里一屏以下的 20×20 链接应该报短边 < 24')
            if bool(w375['emptyBand']) != want_band:
                failures.append(f'check_page.py：{page_name} ' + ('首屏真的空着，应该报「首屏空白带」（量热区滚过的容器要放回原处）' if want_band else '首屏铺满文字，不该报「首屏空白带」（量热区滚过的容器要放回原处）'))
        except (OSError, KeyError) as e:
            failures.append(f'check_page.py 没有产出 report.json 或缺字段（{page_name}）：{e}')

    # check_agent_ready.py：做对的小站必须项全过；做坏的每一项都抓到；连不上时报没查、不算过
    def agent_ready(target):
        o = tempfile.mkdtemp(prefix='agent-ready-selftest-')
        r = subprocess.run([sys.executable, os.path.join(HERE, 'check_agent_ready.py'), target, '--out', o], capture_output=True, text=True)
        try:
            its = json.load(open(os.path.join(o, 'agent-ready.json'), encoding='utf-8'))['items']
        except OSError:
            return r.returncode, set(), []
        return r.returncode, {(i['item'], i['status']) for i in its}, its
    code, got, _ = agent_ready(os.path.join(FIXTURES, 'site-good'))
    if code != 0 or any(st == '不过' for _, st in got):
        failures.append(f'check_agent_ready.py：做对的小站应该退出码 0、没有不过的项，实际 {code}：{sorted(x for x in got if x[1] != "过")}')
    for item in ('正文在原始 HTML 里', 'JSON-LD', 'llms.txt', 'Markdown 版正文', 'RSS / Atom', '列表状态在地址里', 'robots.txt 点名 AI 爬虫', 'sitemap.xml'):
        if (item, '过') not in got:
            failures.append(f'check_agent_ready.py：做对的小站「{item}」应该是过')
    code, got, its = agent_ready(os.path.join(FIXTURES, 'site-bad'))
    if code != 1:
        failures.append(f'check_agent_ready.py：做坏的小站应该退出码 1，实际 {code}')
    for item in ('正文在原始 HTML 里', 'title、canonical、lang', '标题层级', '可点元素是原生的', '图片 alt', 'JSON-LD', 'llms.txt', 'RSS / Atom', '列表状态在地址里'):
        if (item, '不过') not in got:
            failures.append(f'check_agent_ready.py：做坏的小站「{item}」应该是不过')
    # 必须项只管取不取得到、对不对：没有 robots.txt、没有 sitemap.xml 是没做；标题层级、图片 alt 不过只是提示
    for item in ('robots.txt', 'sitemap.xml'):
        if (item, '没做') not in got:
            failures.append(f'check_agent_ready.py：没有 {item} 应该记成没做，不是不过')
    if any(i['required'] for i in its if i['item'] in ('标题层级', '图片 alt', 'robots.txt', 'sitemap.xml')):
        failures.append('check_agent_ready.py：标题层级、图片 alt、缺 robots.txt、缺 sitemap.xml 不该算必须项')
    code, got, _ = agent_ready('http://127.0.0.1:9')
    if code != 2 or ('首页', '没查') not in got or any(st == '过' for _, st in got):
        failures.append(f'check_agent_ready.py：连不上的站点应该报没查、退出码 2，不能算过，实际 {code}：{sorted(got)}')

    def variant(change):
        d = os.path.join(tempfile.mkdtemp(prefix='agent-ready-site-'), 'site')
        shutil.copytree(os.path.join(FIXTURES, 'site-good'), d)
        change(d)
        return agent_ready(d)
    # 只少了 robots.txt 和 sitemap.xml 的小站仍然过
    def bare(d):
        for f in ('robots.txt', 'sitemap.xml'):
            os.remove(os.path.join(d, f))
        lp = os.path.join(d, 'llms.txt')  # llms.txt 里指向站点地图的那一行一起去掉，不然它就是一条打不开的链接
        kept = [ln for ln in open(lp, encoding='utf-8') if 'sitemap' not in ln]
        open(lp, 'w', encoding='utf-8').writelines(kept)
    code, got, _ = variant(bare)
    if code != 0:
        failures.append(f'check_agent_ready.py：只是没有 robots.txt 和 sitemap.xml 的小站应该退出码 0，实际 {code}：{sorted(x for x in got if x[1] == "不过")}')
    # 点名 AI 爬虫要写出允许还是禁止；替用户取页的被整站禁止是必须项不过，训练用的被禁止是提示
    code, got, its = variant(lambda d: open(os.path.join(d, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\nUser-agent: Claude-User\nDisallow: /\n'))
    ev = next((i['evidence'] for i in its if i['item'] == 'robots.txt 点名 AI 爬虫'), '')
    if code != 1 or 'Claude-User：禁止整站' not in ev:
        failures.append(f'check_agent_ready.py：Claude-User 被整站禁止应该是必须项不过，证据写明禁止，实际 {code}：{ev}')
    code, got, its = variant(lambda d: open(os.path.join(d, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n\nUser-agent: ClaudeBot\nAllow: /\n'))
    ev = next((i['evidence'] for i in its if i['item'] == 'robots.txt 点名 AI 爬虫'), '')
    if code != 0 or ('robots.txt 点名 AI 爬虫', '不过') not in got or 'GPTBot：禁止整站' not in ev or 'ClaudeBot：允许' not in ev:
        failures.append(f'check_agent_ready.py：GPTBot 被整站禁止应该报不过（提示，退出码仍是 0），逐个写出允许还是禁止，实际 {code}：{ev}')

    # robots.txt 对所有爬虫整站 Disallow：必须项不过
    code, got, _ = variant(lambda d: open(os.path.join(d, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n'))
    if code != 1 or ('robots.txt', '不过') not in got:
        failures.append(f'check_agent_ready.py：robots.txt 对 * 整站 Disallow 应该是必须项不过、退出码 1，实际 {code}')
    # llms.txt 里的链接带 %00 这类非法路径：不崩，记成打不开并给出那条链接
    code, got, its = variant(lambda d: open(os.path.join(d, 'llms.txt'), 'a', encoding='utf-8').write('\n- [坏链接](/a%00b.html)\n'))
    ev = next((i['evidence'] for i in its if i['item'] == 'llms.txt'), '')
    if ('llms.txt', '不过') not in got or '%00' not in ev:
        failures.append(f'check_agent_ready.py：llms.txt 里带 %00 的链接应该记成打不开并列出来，不能崩，实际 {code}：{ev or "没有报告"}')
    # 根域和 www. 之间的跳转算同站；别的域名、别的端口不算
    sys.path.insert(0, HERE)
    from check_agent_ready import same_site_url
    for a_, b_, want in (('https://example.com/', 'https://www.example.com/x', True), ('http://www.example.com/', 'https://example.com/', True),
                         ('https://example.com/', 'https://example.org/', False), ('https://example.com/', 'https://blog.example.com/', False),
                         ('http://127.0.0.1:8000/', 'http://127.0.0.1:9/', False)):
        if same_site_url(a_, b_) != want:
            failures.append(f'check_agent_ready.py：{a_} → {b_} 应该{"算" if want else "不算"}同站')

    # ../ 逃不出根目录：llms.txt 里指到同级目录（名字以站点目录名开头）的链接算打不开
    def escape(d):
        os.makedirs(d + '2')
        open(os.path.join(d + '2', 'secret.html'), 'w').write('<p>站点目录以外</p>')
        open(os.path.join(d, 'llms.txt'), 'a', encoding='utf-8').write('\n- [外面](../site2/secret.html)\n')
    code, got, _ = variant(escape)
    if ('llms.txt', '不过') not in got:
        failures.append('check_agent_ready.py：llms.txt 里用 ../ 指到站点目录以外的链接应该算打不开')

    # 站内地址被重定向到站外：不跟过去取，记成没查
    import http.server
    import threading

    class Redirect(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:9/elsewhere')
            self.end_headers()

        def log_message(self, *args):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Redirect)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    code, got, its = agent_ready(f'http://127.0.0.1:{srv.server_address[1]}')
    srv.shutdown()
    if code != 2 or not any(i['item'] == '首页' and i['status'] == '没查' and '站外' in i['evidence'] for i in its):
        failures.append(f'check_agent_ready.py：首页被重定向到站外应该不取、记成没查，实际 {code}：{[i["evidence"] for i in its][:3]}')

    # 数据字段 → 画板（coverage.py --data）：照抄进逻辑的字段不算画出来，模板洞里用到的算
    cov = tempfile.mkdtemp(prefix='coverage-selftest-')
    json.dump({'cards': [{'id': 'a', 'zh': {'metric': '−15%', 'claim': '结论'}}]}, open(os.path.join(cov, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(cov, 'Card.dc.html'), 'w', encoding='utf-8').write(
        '<p>{{ c.claim }}</p>\n<script type="text/x-dc">const CARDS = [{"metric": "−15%", "claim": "结论"}];</script>\n')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'coverage.py'), '--canvas', cov, '--data', os.path.join(cov, 'data.json'), '--skip-fields', 'id'],
                       capture_output=True, text=True)
    if r.returncode != 1 or '| metric | **没有画板画出来** |' not in r.stdout or '| claim | Card.dc.html |' not in r.stdout:
        failures.append('coverage.py --data：应该报 metric 没画出来、claim 画在 Card.dc.html 上，退出码 1')

    failures += static_checks()

    if failures:
        print('selftest 不通过：\n  ' + '\n  '.join(failures))
        print(f'报告：{out}/verify-canvas.md')
        sys.exit(1)
    print(f'selftest 通过：{sum(len(v) for v in EXPECT.values())} 类问题、4 种模板味信号、属性选项、额外视口和 14 类几何和排版问题（含玻璃平涂、背景声明、悬停按下样式、中英混排断行、展开挤动、画板比视口宽、首屏字太多、站标不回首页、笼统的进度文字）都抓到了，oklab 和 color-mix 写的底色也算得对，好的状态没有误报；'
          '首屏空白带、相邻色面（浅色、深色）、点按区域两级、字号种类、跨画板左边缘、第三方字体提示、流式页面自动加窄视口、画板尺寸的三种来源、--no-webgl 的兜底画面也对；check_page.py 和 check_agent_ready.py（做对的、做坏的、连不上的、被挡的、../ 和站外重定向）也对；coverage.py 的数据字段对照也对')


if __name__ == '__main__':
    main()
