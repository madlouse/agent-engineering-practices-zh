#!/usr/bin/env python3
"""WCAG 对比度。用法：contrast.py '#aaa' '#bbb' [...成对]；也可 import。"""
import sys
def lum(h):
    h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def cr(a,b):
    la,lb=lum(a),lum(b); hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)
def mix(fg,bg,a):
    fg=fg.lstrip('#'); bg=bg.lstrip('#')
    return '#'+''.join('%02x'%round(int(fg[i:i+2],16)*a+int(bg[i:i+2],16)*(1-a)) for i in (0,2,4))
if __name__=='__main__':
    a=sys.argv[1:]
    for i in range(0,len(a),2): print(a[i],a[i+1],round(cr(a[i],a[i+1]),2))
