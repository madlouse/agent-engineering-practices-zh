#!/usr/bin/env python3
"""手机、平板、折叠屏画板：不另写标记，也不用 <dc-import>，就是对应页面画板的同一份标记，只改 <title> 和 data-props 里 $preview 的宽高，<x-dc> 后面加一行说明。
页面画板改了以后重跑。高度先取下面表里的值；画板内容变长或变短以后，用 --measure 量出来的高度改表（并同步 canvas.json 里那块画板的 h）。

用法：python3 gen_device_boards.py [<project 目录>]      默认 ./boards
      python3 gen_device_boards.py --check [<project 目录>]   只比较，不写；有一块和页面画板对不上就退出码 1
"""
import json, re, sys
from pathlib import Path

# 设备画板: (页面画板, 标题, 宽, 高)。宽高和 canvas.json 里这块画板的 w、h 一致
BOARDS = {
    'Tablet': ('Main', '首页 · 平板 · Velicoach', 820, 3570),
    'Mobile': ('Main', '首页 · 手机 · Velicoach', 390, 4210),
    'Fold': ('Main', '首页 · 折叠屏内屏 · Velicoach', 984, 3460),
    'MindMobile': ('Mind', '看清 · 手机 · Velicoach', 390, 4320),
    'LearnMobile': ('Learn', '学习路径 · 手机 · Velicoach', 390, 3110),
    'ArticleMobile': ('Article', '文章页 · 手机 · Velicoach', 390, 4560),
    'AboutMobile': ('About', '关于 · 手机 · Velicoach', 390, 3350),
    'BuildMobile': ('Build', '动手 · 手机 · Velicoach', 390, 4450),
}

def derive(src, page, title, w, h):
    out, n = re.subn(r'<title>.*?</title>', lambda _: f'<title>{title}</title>', src, count=1)
    assert n == 1, page + '：没有 <title>'
    assert out.count('<x-dc>\n') == 1, page + '：没有独占一行的 <x-dc>'
    out = out.replace('<x-dc>\n', f'<x-dc>\n<!-- 由 {page}.dc.html 生成的同一份标记（只改了标题和预览尺寸），不要手改；改 {page} 后重新生成 -->\n')
    def props(m):
        p = json.loads(m.group(1)); p['$preview'] = {'width': w, 'height': h}
        s = json.dumps(p, ensure_ascii=False, separators=(',', ':'))
        assert "'" not in s
        return "data-props='" + s + "'"
    out, n = re.subn(r"data-props='([^']*)'", props, out, count=1)
    assert n == 1, page + '：没有 data-props'
    assert '<dc-import' not in out
    return out

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    check = '--check' in sys.argv
    proj = Path(args[0]) if args else Path(__file__).resolve().parent / 'boards'
    bad = 0
    for name, (page, title, w, h) in BOARDS.items():
        text = derive((proj / f'{page}.dc.html').read_text(encoding='utf-8'), page, title, w, h)
        dest = proj / f'{name}.dc.html'
        if check:
            same = dest.exists() and dest.read_text(encoding='utf-8') == text
            bad += not same
            print(f'{name}: {"一致" if same else "和 " + page + " 对不上，重跑 gen_device_boards.py"}')
        else:
            dest.write_text(text, encoding='utf-8')
            print(f'{name}.dc.html ← {page}.dc.html（{w}×{h}）')
    sys.exit(1 if bad else 0)

main()
