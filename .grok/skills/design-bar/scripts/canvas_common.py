"""walk_canvas.py、shoot_canvas.py、a11y_probe.py 共用的画板读取和渲染。

画板的状态是 <sc-if value="{{ sN }}">，可点元素写 onClick="{{ goK }}"（点了切到状态 K）。
这里只用画板文件和状态名清单就能把任意状态渲染成普通 HTML，不执行画板里的 renderVals()：
sN 填 真/假，onClick="{{ goK }}" 换成 data-go="K"（页面里没有脚本，点击不会跳转，由调用方按 data-go 换下一个状态）。
"""
import glob
import json
import os
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_dc import render_html  # noqa: E402

BOARD_EXT = '.dc.html'


def safe_name(s):
    return re.sub(r'[\\/:*?"<>|\s]+', '_', s).strip('_') or 'x'


def board_key(name):
    """AI-Today、AI-Today.dc.html、AI-Today.en.dc.html 都归成 AI-Today。"""
    n = os.path.basename(name)
    n = re.sub(r'\.dc\.html$', '', n)
    return re.sub(r'\.en$', '', n)


def board_file(canvas, board, lang='zh'):
    """画板文件的路径：英文稿是 X.en.dc.html，没有英文稿就回退到中文稿。"""
    key = board_key(board)
    zh = os.path.join(canvas, key + BOARD_EXT)
    en = os.path.join(canvas, key + '.en' + BOARD_EXT)
    if lang == 'en' and os.path.exists(en):
        return en
    return zh if os.path.exists(zh) else None


def list_boards(canvas, lang='zh'):
    """这个语言下的全部画板：[(key, path)]。英文稿缺的画板不列（调用方想回退可以自己用 board_file）。"""
    out = []
    for p in sorted(glob.glob(os.path.join(canvas, '*' + BOARD_EXT))):
        is_en = p.endswith('.en' + BOARD_EXT)
        if (lang == 'en') == is_en:
            out.append((board_key(p), p))
    return out


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def load_manifest(canvas):
    """状态名清单 {画板 key: [状态名]}：在画板目录和它的上两级找 .manifest.zh.json；找不到返回 {}。"""
    d = os.path.abspath(canvas)
    for _ in range(3):
        p = os.path.join(d, '.manifest.zh.json')
        if os.path.exists(p):
            try:
                data = json.load(open(p, encoding='utf-8'))
                return {board_key(k): v for k, v in (data.get('states') or {}).items()}
            except ValueError:
                return {}
        d = os.path.dirname(d)
    return {}


def board_sizes(canvas):
    """canvas.json 里每块画板自己的 w×h：{画板 key: (w, h)}。"""
    p = os.path.join(canvas, 'canvas.json')
    if not os.path.exists(p):
        return {}
    try:
        data = json.load(open(p, encoding='utf-8'))
    except ValueError:
        return {}
    boards = data.get('boards') or data.get('meta') or {}
    out = {}
    for k, v in boards.items():
        if isinstance(v, dict) and v.get('w') and v.get('h'):
            out[board_key(k)] = (int(v['w']), int(v['h']))
    return out


def state_count(src):
    idx = [int(m) for m in re.findall(r'<sc-if value="\{\{\s*s(\d+)\s*\}\}"', src)]
    return max(idx) + 1 if idx else 1


class Board:
    """一块画板：源码、状态名、默认状态。"""

    def __init__(self, path, names=None):
        self.path = path
        self.key = board_key(path)
        self.src = read(path)
        n = state_count(self.src)
        self.names = list(names) if names else [f's{i}' for i in range(n)]
        if len(self.names) < n:
            self.names += [f's{i}' for i in range(len(self.names), n)]
        self.default = self._default()

    def _default(self):
        m = re.search(r'"stage"\s*:\s*\{[^}]*?"default"\s*:\s*"([^"]*)"', self.src)
        if m and m.group(1) in self.names:
            return self.names.index(m.group(1))
        return 0

    def index(self, name):
        """状态名（或下标、sN）→ 下标；找不到或不唯一返回 None。"""
        if isinstance(name, int):
            return name if 0 <= name < len(self.names) else None
        name = str(name).strip()
        if name in self.names:
            return self.names.index(name)
        if re.fullmatch(r's?\d+', name):
            i = int(name.lstrip('s'))
            return i if i < len(self.names) else None
        hits = [i for i, n in enumerate(self.names) if name and name in n]
        return hits[0] if len(hits) == 1 else None

    def html(self, idx):
        """第 idx 个状态的页面 HTML；onClick="{{ goK }}" 换成 data-go="K"。"""
        s = re.sub(r'onClick="\{\{\s*go(\d+)\s*\}\}"', r'data-go="\1"', self.src)
        state = {f's{i}': i == idx for i in range(len(self.names))}
        return render_html(s, state)


def load_boards(canvas, lang='zh'):
    """{key: Board}，状态名取清单，英文稿同下标。"""
    manifest = load_manifest(canvas)
    out = {}
    for key, _ in list_boards(canvas, 'zh'):
        p = board_file(canvas, key, lang)
        out[key] = Board(p, manifest.get(key))
    return out


class Stage:
    """放渲染页面的临时目录：画板目录里除画板外的文件（tokens.css、字体、图片）用符号链接放进来，
    相对路径的样式才加载得到。write() 写一个页面并返回 file:// 地址。"""

    def __init__(self, canvas):
        self.dir = tempfile.mkdtemp(prefix='dc-stage-')
        canvas = os.path.abspath(canvas)
        for name in os.listdir(canvas):
            if name.endswith(BOARD_EXT) or name.startswith('.'):
                continue
            try:
                os.symlink(os.path.join(canvas, name), os.path.join(self.dir, name))
            except OSError:
                pass
        self.n = 0

    def write(self, html):
        self.n += 1
        p = os.path.join(self.dir, f'_page{self.n}.html')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(html)
        return 'file://' + p

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


# ---------- 在渲染出的 HTML 里找可点元素 ----------

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
SKIP = {'script', 'style', 'svg'}


SELECT_ROLES = ('radio', 'checkbox', 'switch', 'tab')


class Clickable:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.go = attrs.get('data-go')
        self.href = attrs.get('href')
        self.aria = (attrs.get('aria-label') or attrs.get('title') or '').strip()
        self.stay = self.go is None and not self.href
        self.option = attrs.get('aria-pressed') is not None or attrs.get('role') in SELECT_ROLES
        self.text = ''

    @property
    def label(self):
        return norm(self.text) or self.aria

    def dest(self):
        """('go', K) 或 ('href', 目标)。"""
        if self.stay:
            return ('stay', None)
        return ('go', int(self.go)) if self.go is not None else ('href', self.href)


def norm(s):
    return re.sub(r'\s+', ' ', s or '').strip()


class _Finder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []      # [(tag, Clickable 或 None)]
        self.skip = 0
        self.items = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        click = None
        is_go = a.get('data-go') is not None
        is_link = tag == 'a' and a.get('href') and not a['href'].startswith('javascript:')
        is_select = not is_go and not is_link and (a.get('role') in SELECT_ROLES or a.get('aria-pressed') is not None)
        if (is_go or is_link or is_select) and 'disabled' not in a and a.get('aria-hidden') != 'true':
            click = Clickable(tag, a)
            click.wid, click.pos = len(self.items), self.getpos()
            self.items.append(click)
        if tag == 'img' and a.get('alt'):
            self._text(a['alt'])
        if tag not in VOID:
            self.stack.append((tag, click))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in SKIP:
            self.skip -= 1
        elif tag not in VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def _text(self, t):
        for _, c in reversed(self.stack):
            if c is not None:
                c.text += ' ' + t   # 文字只算给最里面的可点元素
                return

    def handle_data(self, data):
        if not self.skip:
            self._text(data)


class _Hidden(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.starts = [0]
        for line in text.splitlines(keepends=True):
            self.starts.append(self.starts[-1] + len(line))
        self.text, self.stack, self.cuts = text, [], []

    def _off(self):
        line, col = self.getpos()
        return self.starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        hide = 'inert' in a or a.get('aria-hidden') == 'true'
        start = self._off()
        if tag in VOID:
            if hide:
                self.cuts.append((start, start + len(self.get_starttag_text())))
            return
        self.stack.append((tag, start, hide))

    def handle_startendtag(self, tag, attrs):
        if 'inert' in dict(attrs) or dict(attrs).get('aria-hidden') == 'true':
            start = self._off()
            self.cuts.append((start, start + len(self.get_starttag_text())))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                _, start, hide = self.stack[i]
                del self.stack[i:]
                if hide:
                    end = self.text.find('>', self._off()) + 1
                    self.cuts.append((start, end))
                return


def drop_hidden(html):
    """去掉 inert 或 aria-hidden="true" 的整棵子树：浮层后面的衬底、装饰图形，读屏和用户都不把它们当成这一页说的话。"""
    f = _Hidden(html)
    f.feed(html)
    f.close()
    out, pos = [], 0
    for start, end in sorted(f.cuts):
        if start < pos:
            continue
        out.append(html[pos:start])
        pos = end
    out.append(html[pos:])
    return ''.join(out)


def visible_text(html):
    """页面上看得见的文字（去掉脚本、样式和标签）。"""
    h = re.sub(r'<(script|style|helmet|title)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    return norm(re.sub(r'<[^>]+>', ' ', h))


def echo_issues(board, min_len=3):
    """回执复述了别的入口的话：一个状态从两个以上文字不同的按钮进来，状态页上却只出现其中一部分按钮的原话（自己的按钮、标题和导航里的字不算：落地页标题等于入口按钮是常态；浮层后面 inert、aria-hidden 的衬底也不算）。中文按包含算，英文要整段或加引号复述才算。
    选项组（aria-pressed、单选多选）里的选项按惯例只画一个代表，不算。返回 [{'state', 'detail'}]。"""
    inbound = {}
    for i in range(len(board.names)):
        for c in clickables(board.html(i)):
            d = c.dest()
            if d[0] == 'go' and d[1] != i and not c.option and len(c.label) >= min_len:
                inbound.setdefault(d[1], {}).setdefault(c.label, board.names[i])
    out = []
    for k, labels in sorted(inbound.items()):
        if len(labels) < 2 or not 0 <= k < len(board.names):
            continue
        html = drop_hidden(board.html(k))
        body = re.sub(r'<(h[1-6]|nav|header|button|a|script|style|helmet|title)\b.*?</\1>', ' ', html, flags=re.S | re.I)
        text = visible_text(body)
        for c in clickables(html):
            if c.label:
                text = text.replace(c.label, ' ')
        nodes = {re.sub(r'[。.!！?？]+$', '', n) for n in (norm(x) for x in re.split(r'<[^>]+>', body)) if n}

        def echoed(label):
            if re.search(r'[\u3400-\u9fff]', label):
                return label in text
            return label in nodes or any(q % label in text for q in ('“%s”', '"%s"', '「%s」'))
        said = [l for l in labels if echoed(l)]
        if said and len(said) < len(labels):
            miss = [l for l in labels if l not in said]
            out.append({'state': board.names[k],
                        'detail': f'页上复述了「{"」「".join(said)}」，但从「{labels[miss[0]]}」点「{miss[0]}」也会到这里；两个回答拆成两个状态，或回执不复述原话'})
    return out


def clickables(html):
    f = _Finder()
    f.feed(html)
    f.close()
    return f.items


def with_walk_ids(html):
    """给 clickables() 找到的每个元素加 data-walk-id（和 Clickable.wid 同号），浏览器按它找元素，不再按文字二次匹配。"""
    starts = [0]
    for line in html.split('\n'):
        starts.append(starts[-1] + len(line) + 1)
    out = html
    for c in sorted(clickables(html), key=lambda c: c.pos, reverse=True):
        at = starts[c.pos[0] - 1] + c.pos[1] + 1 + len(c.tag)
        out = out[:at] + f' data-walk-id="{c.wid}"' + out[at:]
    return out


def themed(html, theme):
    """画板根元素写死 data-theme="light/dark" 时，换成要拍的主题；只改第一个（根），刻意固定主题的局部不动。"""
    m = re.search(r'\bdata-theme="(light|dark)"', html)
    if not m or m.group(1) == theme or theme not in ('light', 'dark'):
        return html
    return html[:m.start(1)] + theme + html[m.end(1):]


def match_taps(items, tap, stay=False):
    """按可见文字或 aria-label 包含匹配；有完全相等的就只留它们。stay=True 只在原地生效的选择控件（单选、多选、开关、分段）里找，否则只在会跳转的元素里找。"""
    t = norm(tap).lower()
    hits = [c for c in items if c.stay == stay and t and (t in norm(c.text).lower() or t in c.aria.lower())]
    exact = [c for c in hits if norm(c.text).lower() == t or c.aria.lower() == t]
    return exact or hits


def href_board(href):
    """画板之间的跳转 → 画板 key；别的（外链、锚点）→ None。"""
    h = (href or '').split('#')[0].split('?')[0]
    if re.search(r'\.dc\.html$', h):
        return board_key(h)
    return None


# ---------- 浏览器 ----------

SETTLE_JS = """() => {
  for (const a of document.getAnimations()) {
    try { if (a.effect && a.effect.getComputedTiming().iterations === Infinity) a.pause(); else a.finish(); } catch (e) {}
  }
}"""


def settle(page):
    """进场动画直接放到最后一帧、循环动画停住，截图和取色量的是落定的样子，不是动画中途的半透明。"""
    try:
        page.evaluate(SETTLE_JS)
    except Exception:  # noqa: BLE001
        pass


def need_playwright():
    """有 Playwright 就返回 sync_playwright，没有就给清楚的报错、退出码 2。"""
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        print('错误：浏览器模式需要 Python Playwright 和 Chromium（CI 里装：pip install playwright && playwright install chromium）。'
              '本机没有，不会自动安装。', file=sys.stderr)
        sys.exit(2)


def find_ffmpeg():
    p = shutil.which('ffmpeg')
    if p:
        return p
    for pat in ('~/.cache/ms-playwright/ffmpeg-*/ffmpeg-*', '/ms-playwright/ffmpeg-*/ffmpeg-*', '/root/.cache/ms-playwright/ffmpeg-*/ffmpeg-*'):
        for c in sorted(glob.glob(os.path.expanduser(pat))):
            if os.access(c, os.X_OK) and os.path.isfile(c):
                return c
    return None


def parse_size(s):
    w, h = (int(x) for x in s.lower().split('x'))
    return w, h
