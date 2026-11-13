#!/usr/bin/env python3
"""检查源码里绕开设计令牌的写法，防止样式逐渐失控。

报告以下问题（tokens 文件本身不检查）：
  - 写死的颜色：#hex、rgb()/hsl()/oklch()
  - 写死的字号、间距、圆角：font-size/margin/padding/gap/border-radius 等使用 px/rem 数值
  - Tailwind 任意值：text-[13px]、bg-[#111]、p-[17px] 等
  - 内联样式：style="..."、style={{...}}
  - !important
  - 引用了 tokens 文件中未定义的 CSS 变量

用法：
  python lint_tokens.py <源码目录或文件...> [--tokens design/tokens.css] [--max 200]
                        [--exclude <路径前缀>]... [--project-config FILE | --no-project-config]
  --exclude 可重复，相对仓库根（往上找 .git，找不到就相对当前目录）写，绝对路径也行；路径前缀下的文件不报（目录写到目录名即可，不会误中同名前缀的兄弟目录）。
  排除前缀盖住了要检查的路径时报错退出（退出码 2），不然什么都不查；每次运行都会写明排除了多少个文件。
  项目配置 design-bar.json 里 {"lint-tokens": {"exclude": ["路径前缀", ...]}} 作默认值，查找和开关同 check_page.py、verify_canvas.py；
  命令行给了 --exclude 就只用命令行的，没给才用配置的。
退出码：发现问题时为 1，便于接入 CI。
"""
import argparse
import os
import pathlib
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from verify_canvas import add_project_config_args, load_project_config, locate_project_config  # noqa: E402

EXTS = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".jsx", ".tsx", ".js", ".ts",
        ".vue", ".svelte", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "out", "coverage", ".turbo",
             "vendor", ".claude", ".agents", "reviews"}

PROPS = r"(?:font-size|line-height|letter-spacing|margin(?:-[a-z]+)?|padding(?:-[a-z]+)?|gap|row-gap|column-gap|border-radius|inset|z-index|transition(?:-duration)?|animation(?:-duration|-delay)?)"
DECL = re.compile(r"(?<![\w-])(" + PROPS + r")\s*:\s*([^;{}]+)")
JSX_DECL = re.compile(r"\b(fontSize|lineHeight|letterSpacing|margin\w*|padding\w*|gap|borderRadius|zIndex)\s*:\s*['\"]?(\d+(?:\.\d+)?(?:px|rem|em)?)")
NUM = re.compile(r"\b\d*\.?\d+(?:px|rem|em|ms|s)\b")
RULES = [
    ("写死颜色", re.compile(r"(?<![\w&-])#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")),
    ("写死颜色", re.compile(r"\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\(\s*[\d.]")),
    ("Tailwind 任意值", re.compile(r"\b[a-z-]+-\[(?:#|\d|rgb|hsl|oklch)[^\]]*\]")),
    ("!important", re.compile(r"!important")),
]


def numeric_hits(line):
    """返回写死的数值声明：允许 0、1px 细线、百分比、auto 等。"""
    hits = []
    for prop, val in DECL.findall(line):
        v = val.replace("!important", "").strip()
        if "var(" in v or "calc(var" in v:
            continue
        if prop == "z-index":
            if re.fullmatch(r"-?\d+", v) and abs(int(v)) > 10:
                hits.append(f"{prop}: {v}")
            continue
        nums = [n for n in NUM.findall(v) if n not in ("0px", "1px", "0s", "0ms")]
        if nums:
            hits.append(f"{prop}: {v}")
    for prop, v in ([] if "style={{" in line.replace(" ", "") else JSX_DECL.findall(line)):
        if v not in ("0", "0px", "1px"):
            hits.append(f"{prop}: {v}")
    return list(dict.fromkeys(hits))

JSX_STYLE = re.compile(r"\bstyle\s*=\s*\{\{(.*?)\}\}")
HTML_STYLE = re.compile(r"\bstyle\s*=\s*([\"'])(.*?)\1")


def static_inline_style(line):
    """内联样式中写死的部分。允许两种合理用法：传 CSS 变量（'--c': ...），
    以及由数据计算的值（模板字符串、变量、表达式）。"""
    bad = []
    for body in JSX_STYLE.findall(line):
        for entry in re.split(r",(?![^(]*\))", body):
            if ":" not in entry:
                continue
            key, val = (x.strip() for x in entry.split(":", 1))
            if key.strip("'\"").startswith("--"):
                continue
            if "`" in val or "${" in val or re.fullmatch(r"[A-Za-z_][\w.?()\[\]]*", val):
                continue
            bad.append(f"{key}: {val}")
    for _, body in HTML_STYLE.findall(line):
        for decl in body.split(";"):
            if ":" in decl and not decl.strip().startswith("--") and "var(" not in decl:
                bad.append(decl.strip())
    return bad


VAR_USE = re.compile(r"var\(\s*(--[\w-]+)")
VAR_DEF = re.compile(r"(--[\w-]+)\s*:")


def iter_files(paths):
    for p in paths:
        p = pathlib.Path(p)
        if p.is_file():
            yield p
            continue
        for f in p.rglob("*"):
            if f.is_file() and f.suffix in EXTS and not (set(f.parts) & SKIP_DIRS):
                yield f


LINT_CONFIG_KEYS = ("exclude",)


def configured_excludes(argv):
    path = locate_project_config(argv)
    if not path:
        return []
    cfg = load_project_config(path).get("lint-tokens", {})
    bad = sorted(set(cfg) - set(LINT_CONFIG_KEYS)) if isinstance(cfg, dict) else None
    if bad is None or bad or not isinstance(cfg.get("exclude", []), list) or not all(isinstance(x, str) and x for x in cfg.get("exclude", [])):
        sys.exit(f'{path}：lint-tokens 要写成 {{"exclude": ["路径前缀", ...]}}，可用的键：{"、".join(LINT_CONFIG_KEYS)}')
    return cfg.get("exclude", [])


def repo_root():
    d = os.getcwd()
    while not os.path.exists(os.path.join(d, ".git")):
        if os.path.dirname(d) == d:
            return os.getcwd()
        d = os.path.dirname(d)
    return d


def under(path, prefix):
    return path == prefix or path.startswith(prefix + os.sep)


def resolve_prefixes(prefixes):
    root = repo_root()
    return [os.path.normpath(os.path.join(root, x)) for x in prefixes]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--tokens", default="design/tokens.css")
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--exclude", action="append", metavar="PREFIX", help="路径前缀下的文件不检查，可重复；给了就不读项目配置里的 exclude")
    add_project_config_args(ap)
    a = ap.parse_args()
    given = a.exclude if a.exclude else configured_excludes(sys.argv[1:])
    excludes = resolve_prefixes(given)
    covering = [x for x in a.paths for e in excludes if under(os.path.abspath(x), e)]
    if covering:
        print(f"排除前缀盖住了要检查的路径 {'、'.join(covering)}：这样什么都不会被检查，请缩小排除范围。", file=sys.stderr)
        return 2
    skipped = 0
    checked = 0

    tokens = pathlib.Path(a.tokens)
    defined = set()
    if tokens.exists():
        defined = set(VAR_DEF.findall(tokens.read_text(encoding="utf-8")))
    else:
        print(f"提示：未找到 {tokens}，跳过“未定义变量”检查。")

    findings = []
    for f in iter_files(a.paths):
        if tokens.exists() and f.resolve() == tokens.resolve():
            continue
        if any(under(os.path.abspath(f), e) for e in excludes):
            skipped += 1
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        checked += 1
        local_defs = set(VAR_DEF.findall(text))
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if not s or s.startswith(("//", "/*", "*", "<!--")) or "lint-tokens-ignore" in s:
                continue
            names = []
            # token 定义本身（--x: 值）不算写死
            s = re.sub(r"(?<![\w-])--[\w-]+\s*:\s*[^;{}]+;?", "", s).strip() or s
            if not s or s in ("}", "{"):
                continue
            for name, rx in RULES:
                if rx.search(s) and name not in names:
                    names.append(name)
            st = static_inline_style(s)
            if st:
                names.append("内联样式 " + "，".join(st[:3]))
            nh = numeric_hits(s)
            if nh:
                names.append("写死数值 " + "，".join(nh[:3]))
            for name in names:
                findings.append((name, f, i, s[:120]))
            if defined:
                for v in VAR_USE.findall(s):
                    if v not in defined and v not in local_defs:
                        findings.append(("未定义变量 " + v, f, i, s[:120]))

    if checked == 0:
        print(f"没有检查任何文件（扫描路径 {'、'.join(a.paths)} 下没有可检查的文件，或全被排除）：路径可能写错，这样「没有问题」不算数。", file=sys.stderr)
        return 2
    if excludes:
        print(f"已排除 {skipped} 个文件（前缀：{'、'.join(given)}）。")
    if not findings:
        print("✅ 没有发现绕开设计令牌的写法。")
        return 0
    by = {}
    for n, *_ in findings:
        key = n.split(" ")[0]
        by[key] = by.get(key, 0) + 1
    print(f"❌ 发现 {len(findings)} 处问题：" + "，".join(f"{k} {v}" for k, v in by.items()))
    for n, f, i, s in findings[: a.max]:
        print(f"  {f}:{i}  [{n}]  {s}")
    if len(findings) > a.max:
        print(f"  ……其余 {len(findings) - a.max} 处省略")
    print("\n确有必要的例外，在该行加注释 lint-tokens-ignore 并在 design/decisions.md 说明理由。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
