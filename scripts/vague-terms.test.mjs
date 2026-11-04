import { test } from "node:test";
import assert from "node:assert/strict";
import { parseBlock, findViolations } from "./vague-terms.mjs";

const terms = { vague: ["体验友好", "高级感"], filler: ["适当", "尽量"] };

test("parseBlock reads one word per line and fails loudly when the block is missing", () => {
  assert.deepEqual(parseBlock("```vague-terms\n体验友好\n\n高级感\n```", "vague-terms"), ["体验友好", "高级感"]);
  assert.throws(() => parseBlock("no block here", "vague-terms"), /vague-terms/);
});

test("a checklist item with an undefined quality word fails, one that links the definition passes", () => {
  const v = findViolations("- [ ] 首页体验友好\n- [ ] 首页体验友好（quality-terms.md#好用）", terms);
  assert.deepEqual(v, [{ line: 1, word: "体验友好", kind: "vague" }]);
});

test("filler words fail even next to a definition link", () => {
  const v = findViolations("- [x] 尽量两步内完成（quality-terms.md#好用）", terms);
  assert.deepEqual(v, [{ line: 1, word: "尽量", kind: "filler" }]);
});

test("only acceptance columns of a table are checked", () => {
  const table = "| 功能 | 说明 | 验收标准 |\n|---|---|---|\n| 首页 | 要有高级感 | 首屏只有 1 个主操作 |\n| 文章 | 好读 | 适当留白 |";
  assert.deepEqual(findViolations(table, terms), [{ line: 4, word: "适当", kind: "filler" }]);
});

test("prose outside checklists and acceptance columns is not checked", () => {
  assert.deepEqual(findViolations("我们希望首页有高级感，体验友好。", terms), []);
});

test("a new table resets the header", () => {
  const md = "| 验收 |\n|---|\n| 体验友好 |\n\n| 说明 |\n|---|\n| 体验友好 |";
  assert.deepEqual(findViolations(md, terms), [{ line: 3, word: "体验友好", kind: "vague" }]);
});
