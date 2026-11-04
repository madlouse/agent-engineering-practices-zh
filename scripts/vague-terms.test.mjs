import { test } from "node:test";
import assert from "node:assert/strict";
import { parseBlock, parseRuleIds, parseDimensions, findViolations } from "./vague-terms.mjs";

const dimensions = new Map([["好看", "V"], ["高级感", "V"], ["好用", "U"]]);
const terms = {
  vague: ["体验友好", "高级感", "好看", "好用"],
  filler: ["适当", "尽量", "待定", "合理"],
  allowed: ["合理使用"],
  ruleIds: new Set(["U1", "V3"]),
  dimensions,
};

test("parseBlock reads one word per line and fails loudly when the block is missing", () => {
  assert.deepEqual(parseBlock("```vague-terms\n体验友好\n\n高级感\n```", "vague-terms"), ["体验友好", "高级感"]);
  assert.throws(() => parseBlock("no block here", "vague-terms"), /vague-terms/);
});

test("parseRuleIds reads rule ids from the first column of rule tables", () => {
  assert.deepEqual([...parseRuleIds("| U1 两步 | 数 |\n| V3 首屏 | 数 |\n| 说明 | x |")], ["U1", "V3"]);
});

test("parseDimensions maps each covered word to its rule letter", () => {
  const md = "| 维度 | 问题 | 词 | 规则 |\n|---|---|---|---|\n| 好用 | 能做成吗 | 好用、易用 | U1–U12 |\n| 好看 | 用心吗 | 好看、高级感 | V1–V10 |";
  assert.deepEqual([...parseDimensions(md)], [["好用", "U"], ["易用", "U"], ["好看", "V"], ["高级感", "V"]]);
});

test("a quality word passes only with a rule of its own dimension", () => {
  const v = findViolations("- [ ] 首页好看（quality-terms V3）\n- [ ] 首页好看、高级感（quality-terms U1）\n- [ ] 首页好看（`quality-terms.md` V3）", terms);
  assert.deepEqual(v, [
    { line: 2, word: "高级感", kind: "vague" },
    { line: 2, word: "好看", kind: "vague" },
  ]);
});

test("a missing rule id is reported", () => {
  assert.deepEqual(findViolations("- [ ] 首页好看（quality-terms V99）", terms), [
    { line: 1, word: "V99", kind: "bad-ref" },
    { line: 1, word: "好看", kind: "vague" },
  ]);
});

test("a combined word needs the §2.2 definition, a single rule is not enough", () => {
  const v = findViolations("- [ ] 体验友好（quality-terms U1）\n- [ ] 体验友好（quality-terms §2.2）", terms);
  assert.deepEqual(v, [{ line: 1, word: "体验友好", kind: "combo" }]);
});

test("quoting does not hide a quality word, but it does name a filler word", () => {
  const v = findViolations("- [ ] 达到「高级感」\n- [ ] 不出现「待定」「适当」\n- [ ] 写明合理使用的范围", terms);
  assert.deepEqual(v, [{ line: 1, word: "高级感", kind: "vague" }]);
});

test("filler words fail even next to a rule reference", () => {
  assert.deepEqual(findViolations("- [x] 尽量两步内完成（quality-terms U1）", terms), [{ line: 1, word: "尽量", kind: "filler" }]);
});

test("acceptance-like columns are checked, other columns are not, and escaped pipes stay in one cell", () => {
  const table = "| 功能 | 说明 | 验收标准 | 交付物 |\n|---|---|---|---|\n| 语言 | 要有高级感 | 分段控件「中文 \\| EN」，好用 | 一份表 |\n| 文章 | 好读 | 首屏 1 个主操作 | 适当的说明 |";
  assert.deepEqual(findViolations(table, terms), [
    { line: 3, word: "好用", kind: "vague" },
    { line: 4, word: "适当", kind: "filler" },
  ]);
});

test("lists under an acceptance heading are checked, including its sub-headings, until a heading at the same level", () => {
  const md = "## 验收\n\n- 好看\n### 手机\n1. 适当留白\n\n## 背景\n\n- 好看";
  assert.deepEqual(findViolations(md, terms), [
    { line: 3, word: "好看", kind: "vague" },
    { line: 5, word: "适当", kind: "filler" },
  ]);
});

test("prose outside checklists, acceptance lists and acceptance columns is not checked", () => {
  assert.deepEqual(findViolations("我们希望首页有高级感，体验友好。", terms), []);
});

test("a new table resets the header", () => {
  const md = "| 验收 |\n|---|\n| 好看 |\n\n| 说明 |\n|---|\n| 好看 |";
  assert.deepEqual(findViolations(md, terms), [{ line: 3, word: "好看", kind: "vague" }]);
});
