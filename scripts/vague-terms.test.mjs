import { test } from "node:test";
import assert from "node:assert/strict";
import { parseBlock, parseRuleIds, findViolations } from "./vague-terms.mjs";

const terms = { vague: ["体验友好", "高级感"], filler: ["适当", "尽量", "待定", "合理"], allowed: ["合理使用"], ruleIds: new Set(["U1", "V3"]) };

test("parseBlock reads one word per line and fails loudly when the block is missing", () => {
  assert.deepEqual(parseBlock("```vague-terms\n体验友好\n\n高级感\n```", "vague-terms"), ["体验友好", "高级感"]);
  assert.throws(() => parseBlock("no block here", "vague-terms"), /vague-terms/);
});

test("parseRuleIds reads rule ids from the first column of rule tables", () => {
  assert.deepEqual([...parseRuleIds("| U1 两步 | 数 |\n| V3 首屏 | 数 |\n| 说明 | x |")], ["U1", "V3"]);
});

test("an undefined quality word fails; one that cites an existing rule passes; a missing rule id fails", () => {
  const v = findViolations("- [ ] 首页体验友好\n- [ ] 首页体验友好（quality-terms U1）\n- [ ] 首页体验友好（quality-terms.md#U9）", terms);
  assert.deepEqual(v, [
    { line: 1, word: "体验友好", kind: "vague" },
    { line: 3, word: "U9", kind: "bad-ref" },
    { line: 3, word: "体验友好", kind: "vague" },
  ]);
});

test("filler words fail even next to a rule reference", () => {
  assert.deepEqual(findViolations("- [x] 尽量两步内完成（quality-terms U1）", terms), [{ line: 1, word: "尽量", kind: "filler" }]);
});

test("quoted words and allowed phrases are named, not used", () => {
  assert.deepEqual(findViolations("- [ ] 不出现「待定」「适当」\n- [ ] 写明合理使用的范围", terms), []);
});

test("acceptance-like columns are checked, other columns are not, and escaped pipes stay in one cell", () => {
  const table = "| 功能 | 说明 | 验收标准 | 交付物 |\n|---|---|---|---|\n| 语言 | 要有高级感 | 分段控件「中文 \\| EN」，体验友好 | 一份表 |\n| 文章 | 好读 | 首屏 1 个主操作 | 适当的说明 |";
  assert.deepEqual(findViolations(table, terms), [
    { line: 3, word: "体验友好", kind: "vague" },
    { line: 4, word: "适当", kind: "filler" },
  ]);
});

test("plain list items under an acceptance heading are checked until the next heading", () => {
  const md = "## 验收\n\n- 体验友好\n1. 适当留白\n\n## 背景\n\n- 体验友好";
  assert.deepEqual(findViolations(md, terms), [
    { line: 3, word: "体验友好", kind: "vague" },
    { line: 4, word: "适当", kind: "filler" },
  ]);
});

test("prose outside checklists, acceptance lists and acceptance columns is not checked", () => {
  assert.deepEqual(findViolations("我们希望首页有高级感，体验友好。", terms), []);
});

test("a new table resets the header", () => {
  const md = "| 验收 |\n|---|\n| 体验友好 |\n\n| 说明 |\n|---|\n| 体验友好 |";
  assert.deepEqual(findViolations(md, terms), [{ line: 3, word: "体验友好", kind: "vague" }]);
});
