#!/usr/bin/env python3
"""把 Claude Design 设计系统的 tokens.json 生成为代码用的 tokens.css。

设计系统（Design System 类型的产物）是唯一来源；代码里的 tokens.css 由本脚本生成，不手改。
先用 Artifact 工具读出设计系统的 project/tokens.json 存到本地，再运行：

  python sync_tokens.py <tokens.json> --out src/app/tokens.css [--source <设计系统链接>] [--check]

--check：只比较，不写入；生成结果与现有文件不同则退出码为 1（可放进提交前检查）。

生成规则：
  颜色    第一个主题写进 :root，其余主题写进 prefers-color-scheme 与 [data-theme] 块；别名 {x} → var(--x)
  字号    每个文字样式 type-X 生成 --type-X（字号）、--leading-X（行高）、--weight-X（字重）、--tracking-X（字距）
  字体    type.families 的每个键生成 --font-<键>
  其他    spacing、radius、size、shadow、duration、easing 等族按名字生成变量
  附加    降低透明度、减弱动态效果两个媒体查询（只引用上面的变量）
"""
import argparse
import json
import pathlib
import re
import sys

ALIAS = re.compile(r"^\{([A-Za-z0-9][A-Za-z0-9_.-]*)\}$")


def val(v):
    m = ALIAS.match(str(v).strip())
    return f"var(--{m.group(1)})" if m else str(v)


def theme_value(tok, theme, first):
    v = tok.get("value")
    if isinstance(v, dict):
        return v.get(theme, v.get(first))
    return v if theme == first else None


def build(tokens, source):
    out = [f"/* {tokens.get('name', 'Design system')} 设计令牌：由设计系统生成，不要手改。"]
    if source:
        out.append(f" * 来源：{source}")
    out.append(" * 重新生成：python <design-bar>/scripts/sync_tokens.py <tokens.json> --out <本文件>")
    out.append(" */")

    color = tokens.get("color", {})
    themes = [t["id"] for t in color.get("themes", [])] or ["light"]
    first = themes[0]
    root = []

    t = tokens.get("type", {})
    for key, stack in t.get("families", {}).items():
        root.append(f"  --font-{key}: {stack};")
    for g in t.get("groups", []):
        for s in g.get("styles", []):
            base = s["name"][5:] if s["name"].startswith("type-") else s["name"]
            root.append(f"  --type-{base}: {s['fontSize']};")
            if "lineHeight" in s:
                root.append(f"  --leading-{base}: {s['lineHeight']};")
            if "fontWeight" in s:
                root.append(f"  --weight-{base}: {s['fontWeight']};")
            if "letterSpacing" in s:
                root.append(f"  --tracking-{base}: {s['letterSpacing']};")

    for tok in color.get("tokens", []):
        v = theme_value(tok, first, first)
        if v is not None:
            root.append(f"  --{tok['name']}: {val(v)};")

    themed_other = {}
    for fam, body in tokens.items():
        if fam in ("name", "version", "color", "type", "meta") or not isinstance(body, dict):
            continue
        for tok in body.get("tokens", []):
            v = tok.get("value")
            if isinstance(v, dict):
                root.append(f"  --{tok['name']}: {val(v.get(first, next(iter(v.values()))))};")
                for th, tv in v.items():
                    if th != first:
                        themed_other.setdefault(th, []).append(f"  --{tok['name']}: {val(tv)};")
            else:
                root.append(f"  --{tok['name']}: {val(v)};")

    out.append(":root {")
    out += root
    out.append(f"  color-scheme: {first if first in ('light', 'dark') else 'light'};")
    out.append("}")

    for th in themes[1:]:
        lines = []
        for tok in color.get("tokens", []):
            v = tok.get("value")
            if isinstance(v, dict) and th in v:
                lines.append(f"  --{tok['name']}: {val(v[th])};")
        lines += themed_other.get(th, [])
        scheme = f"  color-scheme: {th};" if th in ("light", "dark") else None
        body = lines + ([scheme] if scheme else [])
        if th == "dark":
            out.append("@media (prefers-color-scheme: dark) {")
            out.append('  :root:not([data-theme="light"]) {')
            out += ["  " + l for l in body]
            out.append("  }")
            out.append("}")
        # 也可以只给一块区域换主题（例：训练模式固定深色）：在容器上加 data-theme
        out.append(f':root[data-theme="{th}"], [data-theme="{th}"] {{')
        out += body
        out.append("}")

    if len(themes) > 1:
        # 系统是深色时，标了 data-theme="<首个主题>" 的区域仍按首个主题显示
        first_lines = [f"  --{t['name']}: {val(theme_value(t, first, first))};"
                       for t in color.get("tokens", []) if isinstance(t.get("value"), dict)]
        for fam, body in tokens.items():
            if fam in ("name", "version", "color", "type", "meta") or not isinstance(body, dict):
                continue
            for t in body.get("tokens", []):
                v = t.get("value")
                if isinstance(v, dict):
                    first_lines.append(f"  --{t['name']}: {val(v.get(first, next(iter(v.values()))))};")
        out.append(f'[data-theme="{first}"] {{')
        out += first_lines
        out.append(f"  color-scheme: {first if first in ('light', 'dark') else 'light'};")
        out.append("}")

    names = {tok["name"] for fam in tokens.values() if isinstance(fam, dict) for tok in fam.get("tokens", [])}
    if any(n.startswith("duration-") for n in names):
        zero = " ".join(f"--{n}: 0ms;" for n in sorted(names) if n.startswith("duration-"))
        out.append(f"@media (prefers-reduced-motion: reduce) {{\n  :root {{ {zero} }}\n}}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens_json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", default="")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    tokens = json.loads(pathlib.Path(a.tokens_json).read_text(encoding="utf-8"))
    css = build(tokens, a.source)
    out = pathlib.Path(a.out)
    if a.check:
        same = out.exists() and out.read_text(encoding="utf-8") == css
        print("✅ tokens.css 与设计系统一致" if same else "❌ tokens.css 与设计系统不一致，请重新生成")
        return 0 if same else 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(css, encoding="utf-8")
    print(f"已生成 {out}（{css.count(chr(10))} 行）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
