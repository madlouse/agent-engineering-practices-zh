#!/usr/bin/env python3
"""按旅程文件在画板上走一遍，数点按次数：不靠人数画板，也不用起服务，纯文本模式不需要浏览器。

旅程文件（JSON）：
  [{"name": "开始训练", "level": "核心", "board": "AI-Today", "start": "状态名",
    "steps": [{"tap": "开始训练", "to": "状态名"},
              {"intent": "说一句：今天有点累"},
              {"tap": "照这个练", "board": "Train", "to": "状态名"}]}]
- level：核心（预算 --core，默认 2）、非核心（--other，默认 3）、建档（--onboard，默认 10）。
- tap：按可见文字或 aria-label「包含」匹配当前状态里的可点元素（data-go 或 <a href>）；有文字完全相等的就只在它们里选。
  tap_en 可选，--lang en 时优先用它。
- to：点完应该到的状态名，可省。board：点完应该在的画板（跨画板的 <a href> 写它）；跳到另一块画板落在它的默认状态，
  画布链接打不开指定状态时写 lands（落点状态名，报告里注明「上线时用深链接」）。
- stay：true 表示原地生效的选择控件（单选、多选、开关、分段，role 或 aria-pressed），点了状态不变；不写 stay 时只找会跳转的元素，
  所以没接跳转的普通按钮（点了没反应）一定报「没找到」。
- intent：说话、输入这类意图步，不计点按次数，只记录。

纯文本模式（默认）：把当前状态渲染出来，在里面找可点元素。没找到、找到多个且去向不同、去向和 to 不一致都算失败。
  输出 <out>/walk.md：每条旅程一张步骤表，末尾一张和 gate.py 同列的步数表（测法写「原型实测（画板跳转，walk_canvas 纯文本）」）。
  超预算或任何一步失败，退出码 1。
--browser：同样的步骤在 Chromium 里做（需要 Playwright；没有就报错退出码 2）：
  390×844（--size 改），--lang zh|en，--theme light|dark；每步把渲染页面加载进同一个页面，用 locator 找到元素，
  查可见、没被盖住、点按区域 ≥ 44×44（小了记下来），真的点一下（点击不会跳转，脚本按 data-go 换下一个状态）；
  每步截图 <out>/<旅程>/<NN>.png，每条旅程一段视频 <out>/<旅程>.webm（每步停 --pause 秒，默认 2.5，按真人看清一屏的节奏），用时是脚本量的毫秒数（不含停顿）；
  另把所有旅程连成 journeys.webm（要 ffmpeg，没有就跳过并写明原因）。测法写「原型实测（Chromium，walk_canvas）」。

退出码：0 全部走通且在预算内；1 有失败或超预算；2 用法错误或缺 Playwright。
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canvas_common as cc  # noqa: E402

PAUSE_MS = 2500
HOW_TEXT = '原型实测（画板跳转，walk_canvas 纯文本）'
HOW_BROWSER = '原型实测（Chromium，walk_canvas）'


def plan_journey(j, boards, lang):
    """纯文本地走一遍：返回 (步骤列表, 失败信息或 None)。每步 {n, kind, label, fb, fs, tb, ts, ok, msg, target}。"""
    steps, fail = [], None
    bkey = cc.board_key(j.get('board', ''))
    board = boards.get(bkey)
    if not board:
        return steps, f'旅程「{j.get("name")}」的起点画板「{j.get("board")}」不存在'
    idx = board.index(j.get('start', board.names[board.default]))
    if idx is None:
        return steps, f'起点状态「{j.get("start")}」在 {bkey} 里找不到（状态：{"、".join(board.names)}）'
    n, left = 0, False
    for raw in j.get('steps', []):
        n += 1
        if left:
            steps.append({'n': n, 'kind': 'intent' if 'intent' in raw else 'tap', 'label': raw.get('intent') or raw.get('tap', ''), 'fb': '站外', 'fs': '',
                          'tb': '站外', 'ts': '', 'ok': False, 'msg': '前面已经离开画板（拨号或外链），后面的步骤走不了', 'target': None})
            fail = fail or f'第 {n} 步：{steps[-1]["msg"]}'
            break
        if 'intent' in raw:
            steps.append({'n': n, 'kind': 'intent', 'label': raw['intent'], 'fb': board.key, 'fs': board.names[idx],
                          'tb': board.key, 'ts': board.names[idx], 'ok': True, 'msg': '', 'target': None})
            continue
        tap = (raw.get('tap_en') if lang == 'en' else None) or raw.get('tap', '')
        st = {'n': n, 'kind': 'tap', 'label': tap, 'fb': board.key, 'fs': board.names[idx], 'tb': board.key, 'ts': board.names[idx],
              'ok': False, 'msg': '', 'target': None}
        steps.append(st)
        items = cc.clickables(board.html(idx))
        hits = cc.match_taps(items, tap, stay=bool(raw.get('stay')))
        dests = {c.dest() for c in hits}
        if not hits:
            st['msg'] = f'在 {board.key}「{board.names[idx]}」里没找到可点的「{tap}」'
            fail = fail or f'第 {n} 步：{st["msg"]}'
            break
        if len(dests) > 1:
            ds = '、'.join(sorted(_dest_text(d, board) for d in dests))
            st['msg'] = f'「{tap}」找到 {len(hits)} 个，去向不同：{ds}'
            fail = fail or f'第 {n} 步：{st["msg"]}'
            break
        target = hits[0]
        st['target'] = target
        kind, val = target.dest()
        if kind == 'stay':
            nb, ni = board, idx
        elif kind == 'go':
            if val >= len(board.names):
                st['msg'] = f'去向 go{val} 超出状态数 {len(board.names)}'
                fail = fail or f'第 {n} 步：{st["msg"]}'
                break
            nb, ni = board, val
        else:
            tk = cc.href_board(val)
            if not tk and re.match(r'^(tel|mailto|https?):', val or '') and 'to' not in raw and 'board' not in raw:
                st['tb'], st['ts'], st['ok'], st['left'] = '站外', val, True, True   # 拨号、外链：旅程在这里结束，后面再点就算失败
                left = True
                continue
            if not tk or tk not in boards:
                st['msg'] = f'去向 {val} 不是已知画板（锚点或站外），走不下去'
                fail = fail or f'第 {n} 步：{st["msg"]}'
                break
            nb = boards[tk]
            ni = nb.default
            if 'lands' in raw:
                li = nb.index(raw['lands'])
                if li is None:
                    st['msg'] = f'旅程文件里的落点「{raw["lands"]}」在 {nb.key} 里找不到'
                    fail = fail or f'第 {n} 步：{st["msg"]}'
                    break
                ni = li
                st['note'] = f'画布的链接只能打开 {nb.key} 的第一个状态，落点「{raw["lands"]}」按旅程文件（上线时用深链接）'
        st['tb'], st['ts'] = nb.key, nb.names[ni]
        want_board = raw.get('board')
        if want_board and cc.board_key(want_board) != nb.key:
            st['msg'] = f'点完在 {nb.key}，旅程文件写的是 {cc.board_key(want_board)}'
            fail = fail or f'第 {n} 步：{st["msg"]}'
            break
        if 'to' in raw:
            want = nb.index(raw['to'])
            if want is None:
                st['msg'] = f'旅程文件里的状态「{raw["to"]}」在 {nb.key} 里找不到'
                fail = fail or f'第 {n} 步：{st["msg"]}'
                break
            if want != ni:
                st['msg'] = f'点完在「{nb.names[ni]}」，旅程文件写的是「{nb.names[want]}」'
                fail = fail or f'第 {n} 步：{st["msg"]}'
                break
        st['ok'] = True
        board, idx = nb, ni
    return steps, fail


def _dest_text(d, board):
    kind, val = d
    if kind == 'go':
        return board.names[val] if val < len(board.names) else f'go{val}'
    return val


# ---------- 浏览器 ----------

TAG_JS = """(wid) => {
  document.querySelectorAll('[data-walk-target]').forEach(e => e.removeAttribute('data-walk-target'));
  const el = document.querySelector(`[data-walk-id="${wid}"]`);
  if (!el) return 0;
  el.setAttribute('data-walk-target', '1');
  return 1;
}"""

MEASURE_JS = """() => {
  const el = document.querySelector('[data-walk-target]');
  if (!el) return null;
  el.scrollIntoView({block: 'center', inline: 'center'});
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const visible = r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0.01;
  const x = r.left + r.width / 2, y = r.top + r.height / 2;
  const top = document.elementFromPoint(x, y);
  const covered = !top || !(el === top || el.contains(top) || top.contains(el));
  return {w: r.width, h: r.height, visible, covered, cover: covered && top ? (top.tagName + (top.className && top.className.baseVal === undefined ? '.' + String(top.className).split(' ')[0] : '')) : ''};
}"""


def locate_and_click(page, target):
    """找元素、量、点。返回 (毫秒, 问题列表, 备注列表)。出任何错都记下来，不抛出。"""
    issues, notes = [], []
    t0 = time.perf_counter()
    try:
        count = page.evaluate(TAG_JS, target.wid)
        if not count:
            issues.append('浏览器里没找到这个元素')
        else:
            m = page.evaluate(MEASURE_JS)
            if m is None:
                issues.append('浏览器里没找到这个元素')
            else:
                if not m['visible']:
                    issues.append('元素不可见')
                if m['covered']:
                    issues.append(f'点按位置被别的元素盖住（{m["cover"]}）')
                if m['w'] < 44 or m['h'] < 44:
                    notes.append(f'点按区域 {m["w"]:.0f}×{m["h"]:.0f}，小于 44×44')
                if not issues:
                    page.evaluate("() => { if (!window.__walkNoNav) { window.__walkNoNav = 1; document.addEventListener('click', e => e.preventDefault(), true); } }")
                    page.locator('[data-walk-target]').first.click(timeout=3000)
    except Exception as e:  # noqa: BLE001  浏览器的任何错都记进报告，继续走
        issues.append(f'点按出错：{str(e).splitlines()[0][:120]}')
    return int((time.perf_counter() - t0) * 1000), issues, notes


def run_browser(journeys, plans, boards, canvas, out, a):
    """返回 {旅程名: {ms, issues, notes, videos, shots, secs}} 和全局备注。"""
    sync_playwright = cc.need_playwright()
    w, h = cc.parse_size(a.size)
    stage = cc.Stage(canvas)
    results, extra = {}, []
    vdir = os.path.join(out, '.video')
    os.makedirs(vdir, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for j in journeys:
                name = j['name']
                print(f'走 {name}', flush=True)
                steps, _ = plans[name]
                res = {'ms': 0, 'issues': [], 'notes': [], 'video': None, 'shots': 0, 'secs': 0.0, 'step_issues': {}}
                results[name] = res
                jdir = os.path.join(out, cc.safe_name(name))
                os.makedirs(jdir, exist_ok=True)
                t_start = time.perf_counter()
                ctx = page = None
                try:
                    ctx = browser.new_context(viewport={'width': w, 'height': h}, color_scheme=a.theme, locale='zh-CN' if a.lang == 'zh' else 'en-US',
                                              device_scale_factor=1, record_video_dir=vdir, record_video_size={'width': w, 'height': h})
                    try:
                        ctx.route(re.compile(r'^https?://'), lambda route: route.abort())  # 外部字体不等，结果可重复
                    except Exception:  # noqa: BLE001
                        pass
                    page = ctx.new_page()
                    bkey = cc.board_key(j['board'])
                    board = boards[bkey]
                    idx = board.index(j.get('start', board.names[board.default]))

                    def load(b, i):
                        page.goto(stage.write(cc.with_walk_ids(cc.themed(b.html(i), a.theme))), wait_until='domcontentloaded')
                        page.wait_for_timeout(250)

                    def shot(n):
                        try:
                            page.screenshot(path=os.path.join(jdir, f'{n:02d}.png'))
                            res['shots'] += 1
                        except Exception as e:  # noqa: BLE001
                            res['issues'].append(f'截图 {n:02d} 失败：{str(e).splitlines()[0][:100]}')

                    load(board, idx)
                    shot(0)
                    page.wait_for_timeout(PAUSE_MS)
                    for st in steps:
                        if st['kind'] == 'intent':
                            page.wait_for_timeout(PAUSE_MS)
                            shot(st['n'])
                            continue
                        if st['target'] is not None:
                            ms, issues, notes = locate_and_click(page, st['target'])
                            res['ms'] += ms
                            for s in issues:
                                res['issues'].append(f'第 {st["n"]} 步「{st["label"]}」：{s}')
                            for s in notes:
                                res['notes'].append(f'第 {st["n"]} 步「{st["label"]}」：{s}')
                        if not st['ok'] or st.get('left'):
                            break
                        nb = boards[st['tb']]
                        ni = nb.index(st['ts'])
                        page.wait_for_timeout(200)
                        load(nb, ni)
                        page.wait_for_timeout(PAUSE_MS)
                        shot(st['n'])
                except Exception as e:  # noqa: BLE001
                    res['issues'].append(f'浏览器出错：{str(e).splitlines()[0][:150]}')
                finally:
                    res['secs'] = time.perf_counter() - t_start
                    try:
                        vid = page.video if (ctx and page) else None
                        if ctx:
                            ctx.close()
                        if vid:
                            src = vid.path()
                            dst = os.path.join(out, cc.safe_name(name) + '.webm')
                            shutil.move(src, dst)
                            res['video'] = dst
                    except Exception as e:  # noqa: BLE001
                        res['issues'].append(f'视频没存下来：{str(e).splitlines()[0][:100]}')
            browser.close()
    except Exception as e:  # noqa: BLE001
        extra.append(f'浏览器整体出错：{str(e).splitlines()[0][:200]}')
    finally:
        stage.close()
        shutil.rmtree(vdir, ignore_errors=True)
    return results, extra


def concat_videos(results, out):
    """把各旅程视频连成 journeys.webm；返回一行说明。"""
    vids = [r['video'] for r in results.values() if r.get('video') and os.path.exists(r['video'])]
    if not vids:
        return '没有 journeys.webm：没有录到任何旅程视频'
    ff = cc.find_ffmpeg()
    if not ff:
        return '没有 journeys.webm：找不到 ffmpeg（装 ffmpeg，或用 Playwright 自带的 ffmpeg）'
    lst = os.path.join(out, '.concat.txt')
    dst = os.path.join(out, 'journeys.webm')
    try:
        with open(lst, 'w', encoding='utf-8') as f:
            for v in vids:
                f.write("file '%s'\n" % os.path.abspath(v).replace("'", "'\\''"))
        base = [ff, '-y', '-nostdin', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-an']
        r = subprocess.run(base + ['-c', 'copy', dst], capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(dst):
            r = subprocess.run(base + ['-c:v', 'libvpx', '-deadline', 'realtime', '-cpu-used', '8', '-b:v', '1M', dst],
                               capture_output=True, text=True, timeout=300)
        if r.returncode != 0 or not os.path.exists(dst):
            return '没有 journeys.webm：ffmpeg 连接失败：' + (r.stderr.strip().splitlines() or ['未知错误'])[-1][:150]
    except Exception as e:  # noqa: BLE001
        return f'没有 journeys.webm：{str(e)[:150]}'
    finally:
        if os.path.exists(lst):
            os.remove(lst)
    total = sum(r['secs'] for r in results.values())
    note = f'journeys.webm：{len(vids)} 段连在一起，约 {total:.0f} 秒'
    if total < 120:
        note += '（不足 2 分钟，旅程少或步子少；需要 2–3 分钟时多加旅程）'
    return note


# ---------- 报告 ----------

def level_budget(level, a):
    if '非核心' in level:
        return a.other
    if '建档' in level:
        return a.onboard
    if '核心' in level:
        return a.core
    return None


def main():
    global PAUSE_MS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('journeys', help='旅程文件（JSON）')
    ap.add_argument('--canvas', required=True, help='画板目录（*.dc.html，上两级内要有 .manifest.zh.json）')
    ap.add_argument('--out', required=True, help='输出目录')
    ap.add_argument('--browser', action='store_true', help='用 Chromium 实走并录像、截图')
    ap.add_argument('--lang', default='zh', choices=['zh', 'en'])
    ap.add_argument('--theme', default='light', choices=['light', 'dark'])
    ap.add_argument('--size', default='390x844')
    ap.add_argument('--core', type=int, default=2, help='核心旅程的点按预算')
    ap.add_argument('--other', type=int, default=3, help='非核心旅程的点按预算')
    ap.add_argument('--onboard', type=int, default=10, help='建档旅程的点按预算')
    ap.add_argument('--only', help='只走名字里含这段文字的旅程')
    ap.add_argument('--pause', type=float, default=PAUSE_MS / 1000, help='录像里每步停几秒（默认 2.5）')
    a = ap.parse_args()
    PAUSE_MS = int(a.pause * 1000)

    if a.browser:
        cc.need_playwright()  # 没有就在这里报错退出 2，不先白跑一遍
    try:
        journeys = json.load(open(a.journeys, encoding='utf-8'))
        assert isinstance(journeys, list)
    except (OSError, ValueError, AssertionError) as e:
        print(f'读不了旅程文件 {a.journeys}：{e}（要一个 JSON 数组）', file=sys.stderr)
        sys.exit(2)
    if a.only:
        journeys = [j for j in journeys if a.only in j.get('name', '')]
    if not os.path.isdir(a.canvas):
        print(f'画板目录不存在：{a.canvas}', file=sys.stderr)
        sys.exit(2)
    os.makedirs(a.out, exist_ok=True)
    boards = cc.load_boards(a.canvas, a.lang)
    if not boards:
        print(f'{a.canvas} 里没有 *.dc.html 画板', file=sys.stderr)
        sys.exit(2)

    names = [j.get('name', '') for j in journeys]
    dup = sorted({x for x in names if names.count(x) > 1})
    if dup or '' in names:
        print(f'旅程名要唯一且不能空，重复或空的：{"、".join(dup) or "（空名字）"}', file=sys.stderr)
        sys.exit(2)
    plans = {j['name']: plan_journey(j, boards, a.lang) for j in journeys}
    results, extra = ({}, [])
    if a.browser:
        results, extra = run_browser(journeys, plans, boards, a.canvas, a.out, a)
    how = HOW_BROWSER if a.browser else HOW_TEXT

    lines = ['# 旅程实测（walk_canvas）', '',
             f'模式：{"Chromium（" + a.size + "，" + a.lang + "，" + a.theme + "）" if a.browser else "纯文本（画板跳转，没有开浏览器）"}。'
             f'预算：核心 {a.core}、非核心 {a.other}、建档 {a.onboard}（意图步不计）。', '']
    problems, rows = [], []
    for j in journeys:
        name = j['name']
        steps, fail = plans[name]
        level = j.get('level', '')
        taps = sum(1 for s in j.get('steps', []) if 'tap' in s)
        intents = sum(1 for s in j.get('steps', []) if 'intent' in s)
        budget = level_budget(level, a)
        lines += [f'## {name}（{level}）', '', f'起点：{j.get("board")}「{j.get("start", "默认状态")}」', '',
                  '| 第几下 | 点什么 | 从哪个状态 | 到哪个状态 | 结果 |', '|---|---|---|---|---|']
        k = 0
        for s in steps:
            if s['kind'] == 'intent':
                lines.append(f'| — | 意图步：{s["label"]}（不计） | {s["fb"]}「{s["fs"]}」 | 不变 | 记录 |')
                continue
            k += 1
            frm = f'{s["fb"]}「{s["fs"]}」'
            to = f'{s["tb"]}「{s["ts"]}」' if s['ok'] else '—'
            res = ('走通' + (f'（{s["note"]}）' if s.get('note') else '')) if s['ok'] else '**失败：' + s['msg'] + '**'
            lines.append(f'| {k} | {s["label"]}{"（原地选择）" if s["target"] is not None and s["target"].stay else ""} | {frm} | {to} | {res} |')
        lines.append('')
        if fail:
            problems.append(f'{name}：{fail}')
        if budget is None:
            problems.append(f'{name}：级别「{level}」要写 核心、非核心 或 建档')
        elif taps > budget:
            problems.append(f'{name}：{taps} 次点按，{level}预算是 {budget}')
        ms = '—'
        if a.browser:
            r = results.get(name)
            if r:
                ms = f'{r["ms"]} ms'
                problems += [f'{name}：{s}' for s in r['issues']]
                if r['notes']:
                    lines += ['备注（不影响结论）：', ''] + [f'- {s}' for s in r['notes']] + ['']
                if r['video']:
                    lines += [f'视频：`{os.path.basename(r["video"])}`；截图：`{cc.safe_name(name)}/NN.png`（{r["shots"]} 张）', '']
        rows.append((name, level, taps, intents, ms))

    lines += ['## 步数', '', '| 旅程 | 级别 | 点按次数 | 意图步 | 用时 | 测法 |', '|---|---|---|---|---|---|']
    for name, level, taps, intents, ms in rows:
        lines.append(f'| {name} | {level} | {taps} | {intents} | {ms} | {how} |')
    lines.append('')
    if a.browser:
        lines += [f'用时是脚本量的毫秒数（找元素、量尺寸、点按），不含每步 {PAUSE_MS / 1000:g} 秒的停顿和页面载入。', '']
        lines.append(concat_videos(results, a.out) + '。')
        lines.append('')
    for e in extra:
        problems.append(e)
    lines += ['## 结论', '']
    if problems:
        lines += [f'**不通过**：{len(problems)} 个问题。', ''] + [f'- {p}' for p in problems]
    else:
        lines.append('全部旅程走通，点按次数都在预算内。')
    lines.append('')
    path = os.path.join(a.out, 'walk.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(path)
    print('\n'.join(l for l in lines[lines.index('## 步数'):]))
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
