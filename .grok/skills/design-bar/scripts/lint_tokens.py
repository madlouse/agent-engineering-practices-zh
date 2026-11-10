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
退出码：发现问题时为 1，便于接入 CI。
"""
import argparse
import pathlib
import re
import sys

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--tokens", default="design/tokens.css")
    ap.add_argument("--max", type=int, default=200)
    a = ap.parse_args()

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
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
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
