import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { buildFontsCss, FONTS_CSS } from "./gen-fonts.mjs";
import { TOKENS_JSON } from "./gen-tokens.mjs";

const root = fileURLToPath(new URL("..", import.meta.url));

test("重跑生成脚本，结果和提交的 src/fonts.css 逐字节一致", () => {
  assert.equal(Buffer.compare(Buffer.from(buildFontsCss()), readFileSync(FONTS_CSS)), 0);
  const r = spawnSync(process.execPath, ["scripts/gen-fonts.mjs", "--check"], { cwd: root, encoding: "utf8" });
  assert.equal(r.status, 0, r.stderr);
});

test("字体族名和设计系统字体栈里写的名字一致", () => {
  const stacks = Object.values(JSON.parse(readFileSync(TOKENS_JSON, "utf8")).type.families).join(",");
  const css = buildFontsCss();
  const families = new Set([...css.matchAll(/font-family: "([^"]+)"/g)].map((m) => m[1]));
  assert.deepEqual([...families].sort(), ["IBM Plex Mono", "Inter Tight", "Noto Sans SC", "Noto Serif SC"]);
  for (const f of families) assert.ok(stacks.includes(`"${f}"`), f);
});

test("字体文件都在本仓库的依赖里，不指向别的站点；每片都有 unicode-range，中文按片加载", () => {
  const css = buildFontsCss();
  assert.ok(!/https?:|\/\//.test(css.replace(/\/\*[\s\S]*?\*\//g, "")));
  const blocks = css.split("@font-face").slice(1);
  assert.ok(blocks.length > 150);
  for (const b of blocks) {
    assert.match(b, /unicode-range: U\+/);
    assert.match(b, /font-display: swap;/);
    const u = b.match(/url\("([^"]+)"\)/)[1];
    assert.ok(existsSync(fileURLToPath(new URL(`../src/${u}`, import.meta.url))), u);
  }
});
