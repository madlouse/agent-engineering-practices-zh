import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { buildTokensCss, TOKENS_JSON, TOKENS_CSS } from "./gen-tokens.mjs";

const root = fileURLToPath(new URL("..", import.meta.url));
const tokens = JSON.parse(readFileSync(TOKENS_JSON, "utf8"));

test("重跑生成脚本，结果和提交的 src/tokens.css 逐字节一致", () => {
  const first = buildTokensCss(tokens);
  const second = buildTokensCss(JSON.parse(readFileSync(TOKENS_JSON, "utf8")));
  assert.equal(first, second);
  assert.equal(Buffer.compare(Buffer.from(first), readFileSync(TOKENS_CSS)), 0);
});

test("命令行 --check：文件与生成结果一致时退出码为 0，不写文件", () => {
  const r = spawnSync(process.execPath, ["scripts/gen-tokens.mjs", "--check"], { cwd: root, encoding: "utf8" });
  assert.equal(r.status, 0, r.stderr + r.stdout);
});

test("每个变量都带 vc- 前缀", () => {
  const css = buildTokensCss(tokens);
  const names = [...css.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]);
  assert.ok(names.length > 100);
  for (const n of names) assert.match(n, /^--vc-/, n);
});

test("每个颜色 token 在浅色块有变量；深色值不同的 token 在两个深色块里都有", () => {
  const css = buildTokensCss(tokens);
  const rootBlock = css.slice(css.indexOf(":root {"), css.indexOf("@media"));
  const mediaBlock = css.slice(css.indexOf("@media"), css.indexOf(':root[data-theme="dark"]'));
  const attrBlock = css.slice(css.indexOf(':root[data-theme="dark"]'));
  let differing = 0;
  for (const t of tokens.color.tokens) {
    const name = `--${t.name}`;
    assert.ok(rootBlock.includes(`${name}: ${t.value.light};`), `${name} 浅色值缺失`);
    if (t.value.dark !== t.value.light) {
      differing++;
      assert.ok(mediaBlock.includes(`${name}: ${t.value.dark};`), `${name} 不在系统深色块`);
      assert.ok(attrBlock.includes(`${name}: ${t.value.dark};`), `${name} 不在手动深色块`);
    } else {
      assert.ok(!attrBlock.includes(`${name}:`), `${name} 两种主题相同，不该重复写`);
    }
  }
  assert.ok(differing > 10);
});

test("手动选浅色时，系统深色块不生效；手动选深色时一定生效", () => {
  const css = buildTokensCss(tokens);
  assert.match(css, /@media \(prefers-color-scheme: dark\) \{\n {2}:root:not\(\[data-theme="light"\]\) \{/);
  assert.match(css, /:root\[data-theme="dark"\] \{/);
});

test("间距、圆角、尺寸、时长、缓动、字体、字号也生成了变量", () => {
  const css = buildTokensCss(tokens);
  for (const n of ["--vc-space-5", "--vc-radius-lg", "--vc-control-height", "--vc-duration-base", "--vc-ease-out", "--vc-font-sans", "--vc-type-body-size", "--vc-type-hero-body-leading", "--vc-shadow-card", "--vc-opacity-disabled"]) {
    assert.ok(css.includes(`${n}:`), n);
  }
});
