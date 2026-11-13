#!/usr/bin/env python3
"""组装 canvas.css：canvas.head.css（手写的类）+ canvas.glass.css（design-bar 的液态玻璃模板和本站的接入）+ 由 tokens.json 生成的变量。
用法：build_css.py <输出的 canvas.css> <tokens.json>"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
out, tokens = sys.argv[1], sys.argv[2]
read = lambda n: open(os.path.join(here, n), encoding='utf-8').read().rstrip('\n') + '\n'
open(out, 'w', encoding='utf-8').write(read('canvas.head.css') + '\n' + read('canvas.glass.css'))
subprocess.check_call([sys.executable, os.path.join(here, 'gen_canvas_vars.py'), tokens, out])
