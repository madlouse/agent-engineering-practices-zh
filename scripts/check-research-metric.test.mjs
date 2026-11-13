import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { findProblems, run } from "./check-research-metric.mjs";

const card = (cred, extra = "") =>
  `<section data-research-card ${cred === null ? "" : `data-credibility="${cred}"`}>\n<p data-research-metric>少 23%</p>${extra}</section>`;

test("高过", () => assert.deepEqual(findProblems(card("高")), []));
test("中过", () => assert.deepEqual(findProblems(card("中")), []));
test("英文 high 和 moderate 过", () => {
  assert.deepEqual(findProblems(card("high")), []);
  assert.deepEqual(findProblems(card("moderate")), []);
});
test("低拦", () => {
  const p = findProblems(card("低"));
  assert.equal(p.length, 1);
  assert.equal(p[0].line, 2);
  assert.match(p[0].why, /不放大字/);
});
test("很低拦", () => assert.equal(findProblems(card("很低")).length, 1));
test("low 和 very-low 拦", () => {
  assert.equal(findProblems(card("low")).length, 1);
  assert.equal(findProblems(card("very-low")).length, 1);
});
test("缺可信度拦", () => assert.match(findProblems(card(null))[0].why, /没有标/));
test("非法值拦", () => assert.match(findProblems(card("极高"))[0].why, /不合法/));
test("没有大数字的文件不报", () => {
  assert.deepEqual(findProblems(`<section data-research-card data-credibility="低"><p>x</p></section>`), []);
  assert.deepEqual(findProblems("<p>plain</p>"), []);
});
test("元素自带两个属性", () => {
  assert.deepEqual(findProblems(`<p data-research-card data-research-metric data-credibility="中">x</p>`), []);
  assert.equal(findProblems(`<p data-research-metric>x</p>`).length, 1);
});
test("最近的研究卡祖先决定可信度", () => {
  const html = `<div data-research-card data-credibility="高"><div data-research-card data-credibility="低"><b data-research-metric>1</b></div></div>`;
  assert.equal(findProblems(html).length, 1);
});
test("目录递归并只看指定扩展名", () => {
  const dir = mkdtempSync(join(tmpdir(), "rm-"));
  mkdirSync(join(dir, "a", "b"), { recursive: true });
  writeFileSync(join(dir, "a", "b", "x.html"), card("低"));
  writeFileSync(join(dir, "a", "ok.tsx"), card("高"));
  writeFileSync(join(dir, "a", "skip.css"), card("低"));
  const r = run([dir]);
  assert.equal(r.files, 2);
  assert.equal(r.lines.length, 1);
  assert.match(r.lines[0], /x\.html:2:/);
});
test("属性里的 JSX 表达式含 > 时不提前结束标签", () => {
  const jsx = `<section data-research-card data-credibility="低"><p title={n > 1 ? "more" : "less"} data-research-metric>23%</p></section>`;
  assert.equal(findProblems(jsx).length, 1);
  const nested = `<section data-research-card data-credibility="很低"><p style={{ a: b > c ? "}" : "{" }} data-research-metric>23%</p></section>`;
  assert.equal(findProblems(nested).length, 1);
});
test("可信度写成 JSX 字符串字面量也认", () => {
  assert.deepEqual(findProblems(`<section data-research-card data-credibility={"高"}><p data-research-metric>1</p></section>`), []);
  assert.equal(findProblems(`<section data-research-card data-credibility={"低"}><p data-research-metric>1</p></section>`).length, 1);
  assert.match(findProblems(`<section data-research-card data-credibility={level}><p data-research-metric>1</p></section>`)[0].why, /不合法/);
});
test("表达式里的单词不算属性", () => {
  assert.deepEqual(findProblems(`<p title={"data-research-metric"}>x</p>`), []);
});
