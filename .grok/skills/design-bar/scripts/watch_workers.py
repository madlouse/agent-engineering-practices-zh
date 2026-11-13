#!/usr/bin/env python3
"""看并行画稿的 Agent 有没有卡住：每个 Agent 一个进度记录，按它的修改时间判断多久没动了。

用法：python watch_workers.py <进度记录路径或通配符> [...] [--stale 分钟]
  每个 Agent 只认它自己的进度记录（progress-<组>.md），不要传画板文件：一个 Agent 管几块画板，
  画完的那块自然不再变，按画板文件判断会把在动的 Agent 误报为卡住。
  进度记录是心跳：Agent 每存一个状态就追加一行。整份任务做完时最后一行写「全部完成」，只有这一行算完成。
  协调者派活时先建好每个 Agent 的空进度记录，这样还没写出第一行就挂住的 Agent 也会按时间报出来。
  写明的路径不存在，按「缺失」报。有卡住或缺失的退出码为 1；通配符一个都没匹配到退出码为 2。
"""
import argparse
import glob
import os
import sys
import time

DONE = ('全部完成', 'all done')


def finished(path):
    try:
        lines = [l.strip() for l in open(path, encoding='utf-8') if l.strip()]
    except OSError:
        return False
    return bool(lines) and lines[-1].lstrip('-* ').lower() in DONE


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('patterns', nargs='+')
    ap.add_argument('--stale', type=float, default=10, help='多少分钟没动算卡住')
    a = ap.parse_args()
    files, missing = set(), []
    for p in a.patterns:
        if glob.has_magic(p):
            files.update(glob.glob(p))
        elif os.path.exists(p):
            files.add(p)
        else:
            missing.append(p)
    if not files and not missing:
        print('通配符一个文件都没匹配到：协调者派活时还没建进度记录，或者通配符写错了。')
        return 2
    now, stuck = time.time(), []
    for f in sorted(files):
        mins = (now - os.path.getmtime(f)) / 60
        state = '完成' if finished(f) else ('卡住' if mins > a.stale else '在动')
        if state == '卡住':
            stuck.append(f)
        print(f'{state}\t{mins:5.1f} 分钟前\t{f}')
    for f in missing:
        print(f'缺失\t     —    \t{f}')
    if stuck or missing:
        print(f'\n{len(stuck)} 个超过 {a.stale:g} 分钟没动，{len(missing)} 个进度记录缺失：停掉、按原说明重派一次，再卡就换模型。')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
