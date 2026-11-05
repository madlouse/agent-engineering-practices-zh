#!/usr/bin/env python3
"""验证者自己的测试：在一块故意做坏的画板上跑 verify_canvas.py，确认每一类真问题都抓得到、好的状态不误报。

改了 verify_canvas.py 的检查规则以后先跑它。画板在 tests/fixtures/Selftest.dc.html，每个状态放一类过去真实踩过的坑：
主按钮被输入区挡住或被挤扁、两栏里一栏被挤成竖排、flex 吞掉空格、深色模式下品牌色做文字看不清、<a> 没有 href、事件绑定写成 {{ None }} 和
只有图标的按钮、触控目标太小、对外页面留着「示例」这类占位；另有一个状态放 unslop 的模板味信号（emoji、感叹号、全大写加宽字距、特粗字重）。

用法：python selftest.py        通过时退出码 0，有漏报或误报时退出码 1。
"""
import json
import os
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


def main():
    out = tempfile.mkdtemp(prefix='verify-selftest-')
    subprocess.run([sys.executable, os.path.join(HERE, 'verify_canvas.py'), FIXTURES, '--out', out, '--size', 'SelftestProps.dc.html=320x600'],
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
                        ('case=展开挤动', '展开挤动了版面', None), ('case=写死宽度', '画板比视口宽', None), ('case=字太多', '首屏要读的字太多', None), ('case=站标不回首页', '站标不回首页', None)):
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

    # 数据字段 → 画板（coverage.py --data）：照抄进逻辑的字段不算画出来，模板洞里用到的算
    cov = tempfile.mkdtemp(prefix='coverage-selftest-')
    json.dump({'cards': [{'id': 'a', 'zh': {'metric': '−15%', 'claim': '结论'}}]}, open(os.path.join(cov, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    open(os.path.join(cov, 'Card.dc.html'), 'w', encoding='utf-8').write(
        '<p>{{ c.claim }}</p>\n<script type="text/x-dc">const CARDS = [{"metric": "−15%", "claim": "结论"}];</script>\n')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'coverage.py'), '--canvas', cov, '--data', os.path.join(cov, 'data.json'), '--skip-fields', 'id'],
                       capture_output=True, text=True)
    if r.returncode != 1 or '| metric | **没有画板画出来** |' not in r.stdout or '| claim | Card.dc.html |' not in r.stdout:
        failures.append('coverage.py --data：应该报 metric 没画出来、claim 画在 Card.dc.html 上，退出码 1')

    if failures:
        print('selftest 不通过：\n  ' + '\n  '.join(failures))
        print(f'报告：{out}/verify-canvas.md')
        sys.exit(1)
    print(f'selftest 通过：{sum(len(v) for v in EXPECT.values())} 类问题、4 种模板味信号、属性选项、额外视口和 14 类几何和排版问题（含玻璃平涂、背景声明、悬停按下样式、中英混排断行、展开挤动、画板比视口宽、首屏字太多、站标不回首页）都抓到了，oklab 和 color-mix 写的底色也算得对，好的状态没有误报；coverage.py 的数据字段对照也对')


if __name__ == '__main__':
    main()
