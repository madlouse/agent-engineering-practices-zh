#!/usr/bin/env python3
"""对 Agent 友好的检查：不执行脚本去取一个站点（或读本地构建产物），看 AI 来访时拿不拿得到高质量的数据。

做什么、为什么，见 references/agent-ready.md；本脚本只管「怎么查」。每项给出 过 / 不过 / 没做 / 没查 和证据。

用法：
  python check_agent_ready.py <站点地址或本地目录> [--out 目录] [--pages /,/post/hello] [--max-pages 5] [--no-render]
  站点地址：https://example.com（普通 HTTP 请求，不执行脚本；连不上的项报「没查」，不算过。根域和 www. 之间的跳转算同站，
            跳到别的域名不跟过去取，记成没查）
  本地目录：构建产物（dist、out、public 这类静态文件）。不联网也能跑；/a/b 依次找 a/b、a/b.html、a/b/index.html
  --pages       要查的页面路径，逗号分隔。不给就查首页，再从 sitemap.xml（没有就从首页的站内链接）里取几页，共 --max-pages 页
  --no-render   不开浏览器。「原始 HTML 里有没有正文」要和执行脚本后的正文比，这一项会报「没查」
  --body-ratio  原始 HTML 的正文长度至少是执行脚本后的多少（默认 0.8）

必须项（不过时退出码 1）。划分只看两件事：Agent 取不取得到内容，取到的对不对。
  正文        原始 HTML 里的正文长度 ≥ 执行脚本后的 80%（多数爬虫和取页工具不执行脚本，靠脚本渲染的正文它们取不到）
  身份        <title>、<link rel="canonical">（绝对地址）、<html lang>：缺了会取到错的版本、认错语言、说不出这页叫什么
  可点元素    都是原生的 a[href]、button（不在 div、span 上挂点击，a 都有 href）：不是原生的，Agent 找不到也点不到
  没被挡住    robots.txt 没有对所有爬虫整站 Disallow；也没有把替用户取页的（ChatGPT-User、Claude-User、Perplexity-User）整站挡掉：
              按惯例它们会被挡，用户让 Agent 读这个站时多半取不到。没有 robots.txt 按惯例是全部允许，不算不过（记成没做）
  做了就要对  下面的可选项一旦做了却是坏的（JSON-LD 解析不了、声明的 RSS 或 Markdown 取不到、llms.txt 里的站内链接打不开），
              也算必须项不过：坏的机器可读件比没有更糟，Agent 会照着它走，取到的就是错的

可选项（没做或不过只提示，不影响退出码）。没有它们 Agent 仍然取得到正文，它们管的是好不好找、省不省、准不准：
  sitemap.xml         发现性：页面从首页一路链接得到就取得到，没有站点地图只是不容易取全（单页小站可以没有）
  标题层级            一个 h1、不跳级：正文取得到，只是切分段落和摘要时不准
  图片 alt            正文取得到；图里的信息读不到。信息只在图里的那种，评审时人判
  描述、Open Graph    摘要和分享卡片用；没有时 Agent 自己从正文里取
  JSON-LD（列出类型）、<link rel="alternate"> 的 RSS / Atom（是不是全文）、Markdown 版正文、/llms.txt、
  hreflang（只有一种语言的站不需要）、文章页的作者和日期
  robots.txt 点名 AI 爬虫：逐个写出允许还是禁止。训练和搜索用的爬虫（GPTBot、ClaudeBot、Google-Extended 等）被整站禁止时报不过：
              这可以是有意的决定，但后果是这些产品里搜不到、引不到这个站，报出来让人确认
  列表状态在不在地址里（筛选、分页、标签页是带地址的链接，还是没有地址的按钮；报告里给出判断依据）

退出码：0 必须项都过；1 有必须项不过；2 没有不过的，但有必须项没查成（连不上、没装浏览器）。
需要 Python 3；「正文」一项另需 Playwright 和 Chromium。
"""
import argparse
import json
import os
import re
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BODY_RATIO = 0.8        # 原始 HTML 的正文至少是执行脚本后的多少
MAX_PAGES = 5           # 默认查几页
MAX_LINKS = 60          # llms.txt 里最多核对多少个站内链接
FULL_TEXT_CHARS = 600   # RSS 每条平均超过这么多字算全文
UA = 'design-bar-agent-ready/1.0'
USER_FETCHERS = ('ChatGPT-User', 'Claude-User', 'Perplexity-User')  # 替用户取页的：被挡 = 用户的 Agent 取不到
AI_BOTS = ('GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'PerplexityBot', 'Perplexity-User',
           'Google-Extended', 'Applebot-Extended', 'CCBot', 'Bytespider', 'meta-externalagent', 'Amazonbot')
NATIVE = {'a', 'button', 'input', 'select', 'textarea', 'summary', 'label', 'option', 'details'}
SKIP_TEXT = {'script', 'style', 'noscript', 'template', 'svg', 'head'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
FEED_TYPES = ('application/rss+xml', 'application/atom+xml', 'application/feed+json')
PASS, FAIL, NONE, SKIP = '过', '不过', '没做', '没查'


class Page(HTMLParser):
    """从原始 HTML 里取检查要用的东西；不执行脚本。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang, self.title, self.metas, self.links = '', '', {}, []
        self.headings, self.imgs_no_alt, self.fake_controls, self.anchors = [], [], [], []
        self.jsonld, self.text, self.times = [], [], 0
        self.state_links, self.state_buttons = [], []
        self._stack, self._skip, self._cap = [], 0, None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or '') for k, v in attrs}
        if tag not in VOID:
            self._stack.append(tag)
            if tag in SKIP_TEXT:
                self._skip += 1
        if tag == 'html':
            self.lang = a.get('lang', '')
        elif tag == 'title':
            self._cap = ('title', [])
        elif tag == 'meta':
            key = a.get('name') or a.get('property')
            if key:
                self.metas[key.lower()] = a.get('content', '')
        elif tag == 'link':
            self.links.append(a)
        elif re.fullmatch(r'h[1-6]', tag):
            self._cap = ('h', [int(tag[1])])
        elif tag == 'img' and 'alt' not in a:
            self.imgs_no_alt.append(a.get('src', '(没有 src)')[:80])
        elif tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
            self._cap = ('ld', [])
        elif tag == 'time' and a.get('datetime'):
            self.times += 1
        if tag == 'a':
            self.anchors.append(a)
            if 'href' not in a and 'name' not in a and 'id' not in a:
                self.fake_controls.append('<a> 没有 href')
        # 在非原生元素上挂点击，或者拿 div、span 冒充按钮和链接
        if tag not in NATIVE and ('onclick' in a or a.get('role') in ('button', 'link')):
            self.fake_controls.append(f'<{tag}' + (f' role="{a["role"]}"' if a.get('role') else '') + (' onclick' if 'onclick' in a else '') + '>')
        # 列表状态：筛选、标签页、分页。带地址的链接算「状态在地址里」，没有地址的按钮不算
        statey = a.get('role') == 'tab' or 'aria-pressed' in a or 'aria-selected' in a or a.get('rel') in ('next', 'prev') or 'aria-current' in a
        if tag == 'a' and a.get('href') and (statey or re.search(r'\?[\w-]+=', a['href'])):
            self.state_links.append(a['href'][:80])
        elif tag in ('button', 'div', 'span', 'li') and statey:
            self.state_buttons.append(f'<{tag}' + ''.join(f' {k}="{a[k]}"' for k in ('role', 'aria-pressed', 'aria-selected') if k in a) + '>')
        elif tag == 'select' and not self._in('form'):
            self.state_buttons.append('<select>（不在表单里，选了以后地址不会变）')

    def _in(self, tag):
        return tag in self._stack

    def handle_endtag(self, tag):
        if self._cap and ((self._cap[0] == 'title' and tag == 'title') or (self._cap[0] == 'ld' and tag == 'script') or (self._cap[0] == 'h' and re.fullmatch(r'h[1-6]', tag))):
            kind, buf = self._cap
            self._cap = None
            if kind == 'title':
                self.title = ''.join(buf).strip()
            elif kind == 'ld':
                self.jsonld.append(''.join(buf))
            else:
                self.headings.append((buf[0], ''.join(buf[1:]).strip()[:40]))
        if tag in self._stack:
            while self._stack:
                t = self._stack.pop()
                if t in SKIP_TEXT:
                    self._skip -= 1
                if t == tag:
                    break

    def handle_data(self, data):
        if self._cap:
            self._cap[1].append(data)
        if not self._skip and data.strip():
            self.text.append(data)

    def body_text(self):
        return re.sub(r'\s+', '', ''.join(self.text))


class OffSite(Exception):
    """站内地址被重定向到了站外：不跟过去取。"""


def same_site_url(a, b):
    """两个地址算不算同一个站：主机名相同（根域和 www. 互相算同站），端口相同；http 和 https 不分。"""
    ua, ub = urllib.parse.urlparse(a), urllib.parse.urlparse(b)
    bare = lambda u: (u.hostname or '').lower().removeprefix('www.')  # noqa: E731
    return bool(ua.hostname) and bare(ua) == bare(ub) and ua.port == ub.port


class SameSiteRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not same_site_url(req.full_url, newurl):
            raise OffSite(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(SameSiteRedirect)


class Site:
    """站点地址或本地目录：同一套 get(path) → (状态, 内容)。状态：'ok'、'missing'、'unreachable'。"""

    def __init__(self, target):
        self.local = os.path.isdir(target)
        self.root = os.path.abspath(target) if self.local else target.rstrip('/')
        self.origin = None if self.local else '{0.scheme}://{0.netloc}'.format(urllib.parse.urlparse(self.root))
        self.why = ''

    def _file(self, path):
        rel = urllib.parse.unquote(path.split('?')[0].split('#')[0]).lstrip('/')
        for cand in (rel, rel + '.html', os.path.join(rel, 'index.html')):
            try:
                p = os.path.realpath(os.path.join(self.root, cand))
            except ValueError:  # 路径里有 %00 这类非法字符：当成找不到，不让脚本崩
                return None
            if os.path.commonpath([p, os.path.realpath(self.root)]) == os.path.realpath(self.root) and os.path.isfile(p):  # ../ 逃不出根目录
                return p
        return None

    def get(self, path):
        if self.local:
            p = self._file(path)
            if not p:
                return 'missing', ''
            return 'ok', open(p, encoding='utf-8', errors='replace').read()
        url = path if path.startswith('http') else self.root + '/' + path.lstrip('/')
        try:
            with OPENER.open(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'}), timeout=20) as r:
                return 'ok', r.read().decode('utf-8', errors='replace')
        except OffSite as e:
            self.why = f'被重定向到站外 {str(e)[:80]}，不取'
            return 'unreachable', ''
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return 'missing', ''
            self.why = f'HTTP {e.code}'
            return 'unreachable', ''
        except (urllib.error.URLError, OSError, ValueError) as e:
            self.why = str(getattr(e, 'reason', e))[:80]
            return 'unreachable', ''

    def same_site(self, url):
        """llms.txt、sitemap 里的地址 → 站内路径；站外的返回 None。本地目录没有域名，绝对地址一律按路径在目录里找。"""
        u = urllib.parse.urlparse(url)
        if not u.scheme:
            return '/' + url.lstrip('/')
        if u.scheme not in ('http', 'https'):
            return None
        if self.local or same_site_url(url, self.origin):
            return (u.path or '/') + ('?' + u.query if u.query else '')
        return None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # 不往终端刷访问日志
        pass


def rendered_lengths(site, paths):
    """执行脚本后每页正文的长度（去掉空白）。本地目录临时起一个只听 127.0.0.1 的静态服务。装不了浏览器或打不开时返回 {}。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {}, '没装 Playwright'
    server = None
    base = site.root
    if site.local:
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=site.root))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{server.server_address[1]}'
    out, why = {}, ''
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for p in paths:
                rel = p
                if site.local:  # 静态服务不会自己补 .html
                    f = site._file(p)
                    rel = '/' + os.path.relpath(f, site.root).replace(os.sep, '/') if f else p
                pg = b.new_page(user_agent=UA)
                try:
                    pg.goto(base + rel, wait_until='networkidle', timeout=20000)
                    out[p] = len(re.sub(r'\s+', '', pg.evaluate('document.body ? document.body.innerText : ""')))
                except Exception as e:  # noqa: BLE001  打不开就没查，不当成过
                    why = str(e).split('\n')[0][:80]
                pg.close()
            b.close()
    except Exception as e:  # noqa: BLE001
        why = str(e).split('\n')[0][:80]
    finally:
        if server:
            server.shutdown()
    return out, why


def md_links(text):
    return list(dict.fromkeys(re.findall(r'\]\((\S+?)\)', text) + re.findall(r'(?<![(\w])(https?://[^\s)>\]]+)', text)))


def pick_pages(site, home, sitemap_locs, limit):
    paths = ['/']
    pool = [site.same_site(u) for u in sitemap_locs]
    if not any(pool):
        pool = [site.same_site(a.get('href', '')) for a in home.anchors if a.get('href') and not a['href'].startswith(('#', 'mailto:', 'tel:', 'javascript:'))]
    seen_prefix = set()
    for p in [p for p in pool if p and '?' not in p and p.rstrip('/') not in ('', '/index.html') and not re.search(r'\.(xml|txt|md|json|png|jpe?g|svg|pdf)$', p)]:
        prefix = p.strip('/').split('/')[0]
        if p not in paths and prefix not in seen_prefix:  # 每种路径前缀先取一页，覆盖不同的页面类型
            paths.append(p)
            seen_prefix.add(prefix)
        if len(paths) >= limit:
            break
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target', help='站点地址（https://…）或本地构建产物的目录')
    ap.add_argument('--out', help='报告目录：写 agent-ready.md 和 agent-ready.json')
    ap.add_argument('--pages', default='', help='要查的页面路径，逗号分隔；不给就自己挑')
    ap.add_argument('--max-pages', type=int, default=MAX_PAGES)
    ap.add_argument('--no-render', action='store_true', help='不开浏览器；「正文」一项报没查')
    ap.add_argument('--body-ratio', type=float, default=BODY_RATIO)
    a = ap.parse_args()
    if not os.path.isdir(a.target) and not re.match(r'https?://', a.target):
        sys.exit(f'{a.target}：不是目录，也不是 http(s) 地址')
    site = Site(a.target)
    items = []  # {'item', 'page', 'required', 'status', 'evidence'}

    def add(item, required, status, evidence, page='全站'):
        items.append({'item': item, 'page': page, 'required': required, 'status': status, 'evidence': evidence})

    # ---- 全站文件 ----
    st, robots = site.get('/robots.txt')
    if st == 'unreachable':
        add('robots.txt', True, SKIP, f'没取到：{site.why}')
    elif st == 'missing':
        add('robots.txt', False, NONE, '没有 /robots.txt：按惯例是全部允许，取得到；做的话写明站点地图的地址和对 AI 爬虫的态度')
    else:
        groups, cur, fresh = {}, [], True  # User-agent → 规则；连着的几行 User-agent 共用一组
        for line in robots.splitlines():
            k, _, v = line.split('#')[0].partition(':')
            k, v = k.strip().lower(), v.strip()
            if k == 'user-agent':
                cur = cur if fresh and cur else []
                cur.append(v.lower())
                fresh = True
                for u in cur:
                    groups.setdefault(u, [])
            elif k in ('allow', 'disallow'):
                fresh = False
                for u in cur:
                    groups[u].append((k, v))

        def whole_site(rules):
            return any(k == 'disallow' and v in ('/', '/*') for k, v in rules) and not any(k == 'allow' and v in ('/', '/*') for k, v in rules)
        blocked = whole_site(groups.get('*', []))
        add('robots.txt', True, FAIL if blocked else PASS, '对所有爬虫整站 Disallow: /' if blocked else f'在；对 * 的规则 {len(groups.get("*", []))} 条' + ('，写了 Sitemap' if re.search(r'(?im)^sitemap:', robots) else '，没写 Sitemap 一行'))
        named = [b for b in AI_BOTS if b.lower() in groups]
        if not named:
            add('robots.txt 点名 AI 爬虫', False, NONE, '没有点名任何 AI 爬虫，它们跟着 * 的规则走；想区分「训练」和「替用户取页」就分开写（例如 GPTBot / ChatGPT-User、ClaudeBot / Claude-User）')
        else:
            def stance(b):
                rules = groups[b.lower()]
                if whole_site(rules):
                    return '禁止整站'
                n = sum(1 for k, v in rules if k == 'disallow' and v)
                return f'允许（另禁止 {n} 条路径）' if n else '允许'
            stances = {b: stance(b) for b in named}
            shut = [b for b in named if stances[b] == '禁止整站']
            users = [b for b in shut if b in USER_FETCHERS]
            ev = '；'.join(f'{b}：{v}' for b, v in stances.items())
            if users:
                ev += '。' + '、'.join(users) + ' 是替用户取页的：按惯例会被挡，用户让 Agent 读这个站时多半取不到（有的厂商说明用户发起的取页不一定照 robots.txt）'
            elif shut:
                ev += '。被禁止的是训练或搜索用的爬虫：这些产品里搜不到、引不到这个站；是有意的决定就保留'
            add('robots.txt 点名 AI 爬虫', bool(users), FAIL if shut else PASS, ev)

    st, sm = site.get('/sitemap.xml')
    locs = []
    if st == 'unreachable':
        add('sitemap.xml', False, SKIP, f'没取到：{site.why}')
    elif st == 'missing':
        add('sitemap.xml', False, NONE, '没有 /sitemap.xml（可选）：页面从首页链接得到就取得到；页面多了以后给一份，Agent 才取得全')
    else:  # 做了就要对：解析不了或是空的，Agent 会照着一份坏的清单走
        try:
            locs = [e.text.strip() for e in ET.fromstring(sm.encode('utf-8')).iter() if e.tag.endswith('loc') and e.text]
            add('sitemap.xml', not locs, PASS if locs else FAIL, f'{len(locs)} 个地址' if locs else '能解析，但一个地址也没有')
        except ET.ParseError as e:
            add('sitemap.xml', True, FAIL, f'解析不了：{e}')

    st, home_html = site.get('/')
    if st != 'ok':
        add('首页', True, SKIP if st == 'unreachable' else FAIL, f'没取到：{site.why}' if st == 'unreachable' else '取不到首页')
        return finish(a, site, items, [])
    home = Page()
    home.feed(home_html)
    paths = [p if p.startswith('/') else '/' + p for p in a.pages.split(',') if p] or pick_pages(site, home, locs, a.max_pages)

    st, llms = site.get('/llms.txt')
    if st == 'unreachable':
        add('llms.txt', False, SKIP, f'连不上：{site.why}')
    elif st == 'missing':
        add('llms.txt', False, NONE, '没有 /llms.txt（可选）：做的话由内容数据生成，写清站点是什么、主要页面、内容入口、RSS 和站点地图的地址')
    else:
        links = md_links(llms)
        inner = [(u, site.same_site(u)) for u in links]
        dead, unchecked = [], 0
        for u, p in [x for x in inner if x[1]][:MAX_LINKS]:
            s2, _ = site.get(p)
            if s2 == 'missing':
                dead.append(u)
            elif s2 == 'unreachable':
                unchecked += 1
        outer = sum(1 for _, p in inner if not p)
        head = llms.lstrip().startswith('# ')
        ev = f'{len(links)} 个链接，站内 {len(links) - outer} 个' + (f'，打不开的 {len(dead)} 个：' + '、'.join(dead[:5]) if dead else '都打得开') \
             + (f'；{unchecked} 个没查成' if unchecked else '') + (f'；站外 {outer} 个没查' if outer else '') + ('' if head else '；第一行不是「# 站点名」')
        # 做了就要对：链接打不开算必须项不过
        add('llms.txt', bool(dead), FAIL if dead or not head else PASS, ev)

    # ---- 逐页 ----
    pages = {}
    for p in paths:
        s2, html = (st, home_html) if p == '/' else site.get(p)
        if s2 != 'ok':
            add('页面', True, SKIP if s2 == 'unreachable' else FAIL, f'连不上：{site.why}' if s2 == 'unreachable' else '取不到（404）', p)
            continue
        pg = Page()
        pg.feed(html)
        pages[p] = pg
    rendered, why = ({}, '加了 --no-render') if a.no_render else rendered_lengths(site, list(pages))
    multilingual = any(l.get('hreflang') for pg in pages.values() for l in pg.links)
    feeds, state_links, state_buttons = {}, [], []
    for p, pg in pages.items():
        raw = len(pg.body_text())
        if p in rendered:
            ratio = raw / rendered[p] if rendered[p] else 1.0
            add('正文在原始 HTML 里', True, PASS if ratio >= a.body_ratio and raw > 0 else FAIL, f'原始 HTML 正文 {raw} 字，执行脚本后 {rendered[p]} 字，{ratio:.0%}（要 ≥ {a.body_ratio:.0%}）', p)
        else:
            add('正文在原始 HTML 里', True, SKIP, f'原始 HTML 正文 {raw} 字；执行脚本后的没量到（{why or "页面没打开"}）', p)
        canon = next((l.get('href', '') for l in pg.links if 'canonical' in l.get('rel', '').lower().split()), '')
        miss = [n for n, ok in (('title', pg.title), ('canonical', re.match(r'https?://', canon)), ('html lang', pg.lang)) if not ok]
        add('title、canonical、lang', True, FAIL if miss else PASS, ('缺 ' + '、'.join(miss) + ('（canonical 要写绝对地址）' if 'canonical' in miss and canon else '')) if miss else f'title「{pg.title[:30]}」，lang={pg.lang}，canonical={canon[:60]}', p)
        levels = [lv for lv, _ in pg.headings]
        skips = [f'h{levels[i - 1]} → h{levels[i]}（「{pg.headings[i][1]}」）' for i in range(1, len(levels)) if levels[i] - levels[i - 1] > 1]
        h1 = levels.count(1)
        add('标题层级', False, PASS if h1 == 1 and not skips else FAIL, f'h1 {h1} 个' + ('；跳级：' + '、'.join(skips[:4]) if skips else '，不跳级') + f'；共 {len(levels)} 个标题', p)
        add('可点元素是原生的', True, FAIL if pg.fake_controls else PASS, (f'{len(pg.fake_controls)} 处：' + '、'.join(dict.fromkeys(pg.fake_controls))[:160]) if pg.fake_controls else f'{len(pg.anchors)} 个链接都有 href，没有在 div、span 上挂点击', p)
        add('图片 alt', False, FAIL if pg.imgs_no_alt else PASS, (f'{len(pg.imgs_no_alt)} 张没有 alt：' + '、'.join(pg.imgs_no_alt[:4])) if pg.imgs_no_alt else '都有 alt（装饰图写 alt=""）', p)
        # JSON-LD：没做是可选；做了解析不了算不过
        types, bad = [], 0
        for blob in pg.jsonld:
            try:
                d = json.loads(blob)
                for node in (d if isinstance(d, list) else d.get('@graph', [d]) if isinstance(d, dict) else []):
                    t = node.get('@type') if isinstance(node, dict) else None
                    types += t if isinstance(t, list) else [t] if t else []
            except ValueError:
                bad += 1
        if not pg.jsonld:
            add('JSON-LD', False, NONE, '没有结构化数据（可选）：做的话由内容数据生成，文章用 Article / BlogPosting，带作者、发布和更新日期', p)
        else:
            add('JSON-LD', bool(bad), FAIL if bad else PASS, (f'{bad} 段解析不了；' if bad else '') + '类型：' + ('、'.join(dict.fromkeys(types)) or '没有 @type'), p)
        og = [k for k in ('description', 'og:title', 'og:description', 'og:type', 'og:url') if not pg.metas.get(k)]
        add('描述、Open Graph', False, PASS if not og else NONE, '齐全' if not og else '缺 ' + '、'.join(og), p)
        if multilingual:
            hl = [l.get('hreflang') for l in pg.links if l.get('hreflang')]
            add('hreflang', False, PASS if len(hl) >= 2 and pg.lang.split('-')[0] in {h.split('-')[0] for h in hl} else FAIL, '声明了 ' + '、'.join(hl) if hl else '这一页没有 hreflang，别的页有', p)
        is_article = pg.metas.get('og:type') == 'article' or any(t in ('Article', 'BlogPosting', 'NewsArticle', 'TechArticle') for t in types)
        if is_article:
            has_date = pg.times or pg.metas.get('article:published_time') or 'datePublished' in ''.join(pg.jsonld)
            has_author = pg.metas.get('author') or '"author"' in ''.join(pg.jsonld)
            add('文章的作者和日期机器可读', False, PASS if has_date and has_author else NONE, f'日期：{"有" if has_date else "没有"}（<time datetime>、article:published_time 或 JSON-LD datePublished）；作者：{"有" if has_author else "没有"}', p)
        for l in pg.links:
            rel, typ = l.get('rel', '').lower().split(), l.get('type', '').lower()
            if 'alternate' in rel and typ in FEED_TYPES:
                feeds.setdefault(l.get('href', ''), p)
            if 'alternate' in rel and typ == 'text/markdown':
                target = site.same_site(urllib.parse.urljoin((site.origin or 'http://local') + p, l.get('href', '')))
                s3, md = site.get(target) if target else ('missing', '')
                ok = s3 == 'ok' and md.strip() and not md.lstrip().lower().startswith(('<!doctype', '<html'))
                add('Markdown 版正文', s3 != 'unreachable' and not ok, SKIP if s3 == 'unreachable' else PASS if ok else FAIL, f'{l.get("href")}：' + ('取到了，' + str(len(md)) + ' 字' if ok else '连不上' if s3 == 'unreachable' else '声明了却取不到，或者取到的是 HTML'), p)
        if not any('alternate' in l.get('rel', '').lower().split() and l.get('type', '').lower() == 'text/markdown' for l in pg.links) and is_article:
            add('Markdown 版正文', False, NONE, '文章页没有 <link rel="alternate" type="text/markdown">（可选）：给了的话 Agent 不用从 HTML 里剥正文', p)
        state_links += pg.state_links
        state_buttons += pg.state_buttons

    # ---- RSS / Atom ----
    if not feeds:
        guess = next((f for f in ('/rss.xml', '/feed.xml', '/atom.xml', '/index.xml', '/feed') if site.get(f)[0] == 'ok'), None)
        add('RSS / Atom', False, NONE, (f'{guess} 在，但没有哪一页用 <link rel="alternate"> 指过去，Agent 发现不了' if guess else '没有订阅源（可选）'))
    for href, p in feeds.items():
        target = site.same_site(urllib.parse.urljoin((site.origin or 'http://local') + p, href))
        s3, xml = site.get(target) if target else ('missing', '')
        if s3 == 'unreachable':
            add('RSS / Atom', False, SKIP, f'{href}：连不上（{site.why}）', p)
            continue
        try:
            root = ET.fromstring(xml.encode('utf-8')) if s3 == 'ok' else None
        except ET.ParseError:
            root = None
        if root is None:
            add('RSS / Atom', True, FAIL, f'{href}：声明了却取不到或解析不了', p)
            continue
        entries = [e for e in root.iter() if e.tag.split('}')[-1] in ('item', 'entry')]
        body = [max((len(''.join(c.itertext())) for c in e if c.tag.split('}')[-1] in ('encoded', 'content', 'description', 'summary')), default=0) for e in entries]
        avg = sum(body) / len(body) if body else 0
        add('RSS / Atom', False, PASS, f'{href}：{len(entries)} 条，每条正文平均 {avg:.0f} 字' + ('（全文）' if avg >= FULL_TEXT_CHARS else '（只有摘要；给全文 Agent 就不用再逐页取）'), p)

    # ---- 列表状态在不在地址里（判断依据写出来）----
    sl, sb = list(dict.fromkeys(state_links)), list(dict.fromkeys(state_buttons))
    if not sl and not sb:
        add('列表状态在地址里', False, NONE, '查的页面上没发现筛选、标签页、分页（依据：没有 role="tab"、aria-pressed、aria-selected、rel="next/prev"、带查询参数的链接、表单外的 select）')
    else:
        add('列表状态在地址里', False, FAIL if sb else PASS,
            f'带地址的链接 {len(sl)} 个（例：{"、".join(sl[:3]) or "无"}）；没有地址的控件 {len(sb)} 个（例：{"、".join(sb[:3]) or "无"}）。'
            + ('没有地址的那些，换了状态以后地址不变，Agent 和别人都链接不到这个状态：改成 <a href="?type=…">，或者切换时同步地址' if sb else '每个状态都能直接链接'))
    return finish(a, site, items, paths)


def finish(a, site, items, paths):
    req_fail = [i for i in items if i['required'] and i['status'] == FAIL]
    req_skip = [i for i in items if i['required'] and i['status'] == SKIP]
    code = 1 if req_fail else 2 if req_skip else 0
    verdict = {0: '必须项都过', 1: f'{len(req_fail)} 个必须项不过', 2: f'没有不过的，但 {len(req_skip)} 个必须项没查成'}[code]
    lines = ['# 对 Agent 友好的检查', '', f'目标：{site.root}（{"本地目录" if site.local else "站点"}）；查的页面：{"、".join(paths) or "没取到首页"}', '',
             f'**结论：{verdict}。** 必须项只管「取不取得到、取到的对不对」；可选项没做或不过只是提示；没查的项不算过。', '', '| 项 | 页面 | 必须 | 结果 | 证据 |', '|---|---|---|---|---|']
    order = {FAIL: 0, SKIP: 1, NONE: 2, PASS: 3}
    for i in sorted(items, key=lambda x: (not x['required'], order[x['status']])):
        lines.append(f"| {i['item']} | {i['page']} | {'必须' if i['required'] else '可选'} | {i['status']} | {i['evidence'].replace('|', '/')} |")
    md = '\n'.join(lines) + '\n'
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        open(os.path.join(a.out, 'agent-ready.md'), 'w', encoding='utf-8').write(md)
        json.dump({'target': site.root, 'pages': paths, 'exit': code, 'items': items}, open(os.path.join(a.out, 'agent-ready.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(md)
    sys.exit(code)


if __name__ == '__main__':
    main()
