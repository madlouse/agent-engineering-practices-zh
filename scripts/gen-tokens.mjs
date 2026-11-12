#!/usr/bin/env node
// 把设计系统的 token 文件生成为 CSS 变量：docs/uiue/system/tokens.json → src/tokens.css。
// 变量一律带 vc- 前缀（颜色 token 本来就叫 vc-xxx，其余加上）。
// 用法：node scripts/gen-tokens.mjs（写文件）；node scripts/gen-tokens.mjs --check（只比较，不一致退出码为 1）。
import { readFileSync, realpathSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const TOKENS_JSON = fileURLToPath(new URL("../docs/uiue/system/tokens.json", import.meta.url));
export const TOKENS_CSS = fileURLToPath(new URL("../src/tokens.css", import.meta.url));

const varName = (name) => (name.startsWith("vc-") ? `--${name}` : `--vc-${name}`);

/** 带浅色、深色两个值的 token：深色值写在另一组里。 */
function themed(tokens) {
  const light = [];
  const dark = [];
  for (const t of tokens) {
    const v = t.value;
    if (v !== null && typeof v === "object") {
      light.push([varName(t.name), v.light]);
      if (v.dark !== v.light) dark.push([varName(t.name), v.dark]);
    } else {
      light.push([varName(t.name), v]);
    }
  }
  return { light, dark };
}

const decls = (pairs, indent) => pairs.map(([k, v]) => `${indent}${k}: ${v};`).join("\n");

export function buildTokensCss(tokens) {
  const plain = [];
  for (const [key, stack] of Object.entries(tokens.type.families)) plain.push([`--vc-font-${key}`, stack]);
  for (const g of tokens.type.groups) {
    for (const s of g.styles) {
      plain.push([`--vc-type-${s.name}-size`, s.fontSize]);
      plain.push([`--vc-type-${s.name}-leading`, s.lineHeight]);
      plain.push([`--vc-type-${s.name}-weight`, s.fontWeight]);
      if (s.letterSpacing !== undefined) plain.push([`--vc-type-${s.name}-tracking`, s.letterSpacing]);
    }
  }
  const colors = themed(tokens.color.tokens);
  const shadows = themed(tokens.shadow.tokens);
  for (const family of ["spacing", "radius", "size", "duration", "easing", "opacity"]) {
    for (const t of tokens[family].tokens) plain.push([varName(t.name), t.value]);
  }
  const light = [...plain, ...colors.light, ...shadows.light];
  const dark = [...colors.dark, ...shadows.dark];

  return [
    "/* Velicoach 设计 token：由 scripts/gen-tokens.mjs 从 docs/uiue/system/tokens.json 生成，不要手改。",
    " * 重新生成：npm run gen:tokens。主题：默认浅色；系统是深色且没选浅色时用深色；手动选深色时一定用深色（data-theme，见 src/lib/theme-init.mjs）。 */",
    ":root {",
    "  color-scheme: light;",
    decls(light, "  "),
    "}",
    "",
    "@media (prefers-color-scheme: dark) {",
    '  :root:not([data-theme="light"]) {',
    "    color-scheme: dark;",
    decls(dark, "    "),
    "  }",
    "}",
    "",
    ':root[data-theme="dark"] {',
    "  color-scheme: dark;",
    decls(dark, "  "),
    "}",
    "",
  ].join("\n");
}

function main() {
  const css = buildTokensCss(JSON.parse(readFileSync(TOKENS_JSON, "utf8")));
  if (process.argv.includes("--check")) {
    let current = "";
    try {
      current = readFileSync(TOKENS_CSS, "utf8");
    } catch {
      // 文件不存在，按不一致处理
    }
    if (current !== css) {
      console.error("src/tokens.css 和 tokens.json 生成的结果不一致：运行 npm run gen:tokens");
      process.exit(1);
    }
    return;
  }
  writeFileSync(TOKENS_CSS, css);
}

if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) main();
