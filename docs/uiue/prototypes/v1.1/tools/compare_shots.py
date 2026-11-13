#!/usr/bin/env python3
"""逐对比较两组截图。用法：compare_shots.py <合并前目录> <合并后目录> [--diff <差异图目录>]
每张图报告：尺寸是否相同、不同像素的占比、差异的包围盒；有差异的另存一张标红的差异图。"""
import sys
from pathlib import Path
from PIL import Image, ImageChops

a, b = Path(sys.argv[1]), Path(sys.argv[2])
dd = Path(sys.argv[sys.argv.index('--diff') + 1]) if '--diff' in sys.argv else None
if dd: dd.mkdir(parents=True, exist_ok=True)
same = diff = 0
for fa in sorted(a.glob('*.png')):
    fb = b / fa.name
    if not fb.exists(): print(f'缺少 {fa.name}'); continue
    ia, ib = Image.open(fa).convert('RGB'), Image.open(fb).convert('RGB')
    note = ''
    if ia.size != ib.size:
        note = f'尺寸 {ia.size[0]}x{ia.size[1]} → {ib.size[0]}x{ib.size[1]}；'
        w, h = max(ia.size[0], ib.size[0]), max(ia.size[1], ib.size[1])
        ca, cb = Image.new('RGB', (w, h), 'white'), Image.new('RGB', (w, h), 'white')
        ca.paste(ia, (0, 0)); cb.paste(ib, (0, 0)); ia, ib = ca, cb
    d = ImageChops.difference(ia, ib).convert('L').point(lambda v: 255 if v > 8 else 0)
    box = d.getbbox()
    if not box and not note: same += 1; continue
    diff += 1
    n = d.histogram()[255] if box else 0
    print(f'{fa.name}: {note}不同像素 {100 * n / (ia.size[0] * ia.size[1]):.2f}%，范围 {box}')
    if dd and box:
        red = Image.new('RGB', ia.size, (255, 0, 0))
        Image.composite(red, ib, d).save(dd / fa.name)
for fb in sorted(b.glob('*.png')):
    if not (a / fb.name).exists(): print(f'新增 {fb.name}')
print(f'相同 {same} 张，有差异 {diff} 张')
