#!/usr/bin/env python3
"""一个浏览器进程拍完画板目录里所有画板的所有状态（主题 × 语言），不用每张图启动一次浏览器。

用法：
  python shoot_canvas.py <画板目录> --out <输出目录> [--themes light,dark] [--langs zh,en] [--size 390x844]
画板在 canvas.json 里有自己的 w×h 就按它拍，没有才用 --size。状态名来自 .manifest.zh.json（英文稿同下标）。
输出：
  <out>/<lang>-<theme>/<画板>-<NN>-<状态名>.png
  <out>/<lang>-<theme>/overview.png   每组一张总览（每块画板另起一行，每行 12 张，图下写状态名；找不到中文字体时只写序号）
  <out>/index.md                      每块画板几张、哪些渲染出错
某张出错只记进 index.md，继续拍别的。需要 Python Playwright + Chromium（没有就退出码 2）；总览需要 Pillow（没有就跳过并写明）。
退出码：0 全拍了；1 有渲染出错的；2 用法错误或缺 Playwright。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canvas_common as cc  # noqa: E402

PER_ROW = 12
CELL_W = 150
FONT_CANDIDATES = ['/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                   '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc', '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                   '/System/Library/Fonts/PingFang.ttc', '/System/Library/Fonts/STHeiti Light.ttc', '/Library/Fonts/Arial Unicode.ttf',
                   '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf']


def cjk_font(size):
    from PIL import ImageFont
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return None


def overview(group_dir, shots, label):
    """shots：[(画板, 序号, 状态名, 图片路径)]；拼成 overview.png，返回一行说明。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return '没有总览图：没装 Pillow'
    if not shots:
        return '没有总览图：没有拍到任何图'
    font = cjk_font(11)
    title_font = cjk_font(14) or ImageFont.load_default()
    names_ok = font is not None
    font = font or ImageFont.load_default()
    pad, label_h, head_h = 8, 30, 24
    rows, cur, last = [], [], None
    for b, i, name, path in shots:   # 每块画板另起一行，超过 12 张折行
        if b != last or len(cur) == PER_ROW:
            if cur:
                rows.append(cur)
            cur = []
            if b != last:
                cur.append(('head', b))
            last = b
        cur.append(('img', i, name, path))
    if cur:
        rows.append(cur)
    thumbs = []
    for row in rows:
        items = []
        for it in row:
            if it[0] == 'head':
                items.append(it)
                continue
            try:
                im = Image.open(it[3]).convert('RGB')
                im.thumbnail((CELL_W, 10 ** 5))
                items.append(('img', it[1], it[2], im))
            except Exception:  # noqa: BLE001
                items.append(('img', it[1], it[2], None))
        thumbs.append(items)
    width = PER_ROW * (CELL_W + pad) + pad
    # 行高 = 这一行最高的缩略图（总览里的画板可能尺寸各不同）
    heights = []
    for items in thumbs:
        hs = [it[3].height for it in items if it[0] == 'img' and it[3] is not None]
        heads = head_h if items and items[0][0] == 'head' else 0
        heights.append(heads + (max(hs) if hs else 40) + label_h + pad)
    total_h = sum(heights) + pad
    if total_h > 60000:
        return f'没有总览图：太高（{total_h}px），缩小范围再拍'
    canvas = Image.new('RGB', (width, total_h), (245, 245, 247))
    d = ImageDraw.Draw(canvas)
    y = pad
    for items, rh in zip(thumbs, heights):
        x = pad
        top = y
        if items and items[0][0] == 'head':
            d.text((pad, y), items[0][1], fill=(60, 60, 60), font=title_font)
            top += head_h
            items = items[1:]
        for it in items:
            _, i, name, im = it
            if im is not None:
                canvas.paste(im, (x, top))
                d.rectangle([x - 1, top - 1, x + im.width, top + im.height], outline=(210, 210, 214))
                h = im.height
            else:
                d.rectangle([x, top, x + CELL_W, top + 40], outline=(200, 80, 80))
                h = 40
            txt = f'{i:02d} {name}' if names_ok else f'{i:02d}'
            d.text((x, top + h + 3), txt[:14], fill=(90, 90, 95), font=font)
            x += CELL_W + pad
        y += rh
    canvas.save(os.path.join(group_dir, 'overview.png'))
    return '总览 overview.png' + ('' if names_ok else '（没找到中文字体，图下只写序号）')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('canvas', help='画板目录')
    ap.add_argument('--out', required=True)
    ap.add_argument('--themes', default='light,dark')
    ap.add_argument('--langs', default='zh,en')
    ap.add_argument('--size', default='390x844', help='画板在 canvas.json 里没有尺寸时用它')
    ap.add_argument('--only', help='只拍名字里含这段文字的画板')
    a = ap.parse_args()

    sync_playwright = cc.need_playwright()
    if not os.path.isdir(a.canvas):
        print(f'画板目录不存在：{a.canvas}', file=sys.stderr)
        sys.exit(2)
    themes = [t for t in a.themes.split(',') if t]
    langs = [x for x in a.langs.split(',') if x]
    default_size = cc.parse_size(a.size)
    sizes = cc.board_sizes(a.canvas)
    stage = cc.Stage(a.canvas)
    os.makedirs(a.out, exist_ok=True)
    index = ['# 画板截图', '', f'画板目录：`{a.canvas}`；主题：{"、".join(themes)}；语言：{"、".join(langs)}；没有 canvas.json 尺寸的画板按 {a.size}。', '']
    errors_total = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for lang in langs:
                boards = cc.load_boards(a.canvas, lang)
                for theme in themes:
                    group = f'{lang}-{theme}'
                    print(f'截图 {group}', flush=True)
                    gdir = os.path.join(a.out, group)
                    os.makedirs(gdir, exist_ok=True)
                    shots, rows, errs = [], [], []
                    ctx = None
                    try:
                        ctx = browser.new_context(viewport={'width': default_size[0], 'height': default_size[1]}, color_scheme=theme,
                                                  locale='zh-CN' if lang == 'zh' else 'en-US', device_scale_factor=1)
                        page = ctx.new_page()
                        for key, board in boards.items():
                            if a.only and a.only not in key:
                                continue
                            if lang == 'en' and not board.path.endswith('.en' + cc.BOARD_EXT):
                                rows.append((key, 0, '没有英文稿，跳过'))
                                continue
                            w, h = sizes.get(key, default_size)
                            ok = 0
                            try:
                                page.set_viewport_size({'width': w, 'height': h})
                            except Exception as e:  # noqa: BLE001
                                errs.append((key, '-', f'设视口失败：{str(e).splitlines()[0][:100]}'))
                            for i, name in enumerate(board.names):
                                path = os.path.join(gdir, f'{key}-{i:02d}-{cc.safe_name(name)}.png')
                                try:
                                    page.goto(stage.write(cc.themed(board.html(i), theme)), wait_until='domcontentloaded')
                                    try:
                                        page.evaluate('() => document.fonts && document.fonts.ready')
                                    except Exception:  # noqa: BLE001
                                        pass
                                    cc.settle(page)
                                    page.wait_for_timeout(150)
                                    page.screenshot(path=path)
                                    shots.append((key, i, name, path))
                                    ok += 1
                                except Exception as e:  # noqa: BLE001
                                    errs.append((key, f'{i:02d} {name}', str(e).splitlines()[0][:120]))
                            rows.append((key, ok, f'{w}×{h}，共 {len(board.names)} 个状态'))
                    except Exception as e:  # noqa: BLE001
                        errs.append(('（整组）', '-', str(e).splitlines()[0][:150]))
                    finally:
                        if ctx:
                            try:
                                ctx.close()
                            except Exception:  # noqa: BLE001
                                pass
                    try:
                        ov = overview(gdir, shots, group)
                    except Exception as e:  # noqa: BLE001
                        ov = f'没有总览图：{str(e)[:120]}'
                    errors_total += len(errs)
                    index += [f'## {group}', '', f'{sum(r[1] for r in rows)} 张；{ov}', '', '| 画板 | 拍到几张 | 说明 |', '|---|---|---|']
                    index += [f'| {k} | {n} | {note} |' for k, n, note in rows]
                    index.append('')
                    if errs:
                        index += ['渲染出错：', ''] + [f'- {k} {s}：{m}' for k, s, m in errs] + ['']
                    else:
                        index += ['没有渲染出错。', '']
            browser.close()
    except Exception as e:  # noqa: BLE001
        index += [f'浏览器整体出错：{str(e).splitlines()[0][:200]}', '']
        errors_total += 1
    finally:
        stage.close()
    with open(os.path.join(a.out, 'index.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(index))
    print(os.path.join(a.out, 'index.md'))
    sys.exit(1 if errors_total else 0)


if __name__ == '__main__':
    main()
