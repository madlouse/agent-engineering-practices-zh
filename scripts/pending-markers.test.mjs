import assert from "node:assert/strict";
import { test } from "node:test";
import { findPending, stripPending } from "./pending-markers.mjs";
import { findViolations } from "./vague-terms.mjs";

test("findPending lists every marker with its line and topic", () => {
  const text = ["第一行没有", "这件事〔Resend 留存：待定〕见 #13", "同一行两个〔甲：待定〕和〔乙：待定〕"].join("\n");
  assert.deepEqual(findPending(text), [
    { line: 2, topic: "Resend 留存" },
    { line: 3, topic: "甲" },
    { line: 3, topic: "乙" },
  ]);
});

test("findPending ignores the bare word, other brackets and a marker broken across lines", () => {
  assert.deepEqual(findPending("待定，见 #13\n「Resend 留存：待定」\n〔Resend 留存：已定〕\n〔Resend 留存：\n待定〕"), []);
});

test("stripPending keeps the topic and drops only the brackets and the suffix; line numbers stay", () => {
  assert.equal(stripPending("第一行\n还没有定〔Resend 留存：待定〕，见 #13\n第三行待定"), "第一行\n还没有定Resend 留存，见 #13\n第三行待定");
});

test("check-vague: a sentence with a marker passes, the same word outside a marker is still reported", () => {
  const terms = { vague: [], filler: ["待定"], allowed: [], ruleIds: new Set(), dimensions: new Map() };
  const text = "- [ ] 删除以后怎么处理还没有核对完〔Resend 留存：待定〕\n- [ ] 处理时限待定\n- [ ] 写成〔Resend 留存：待定〕以后仍然待定";
  assert.deepEqual(findViolations(text, terms).map((v) => v.line), [1, 2, 3], "without stripping every line is reported");
  assert.deepEqual(findViolations(stripPending(text), terms), [
    { line: 2, word: "待定", kind: "filler" },
    { line: 3, word: "待定", kind: "filler" },
  ]);
});

test("check-vague: a filler or quality word used as the topic of a marker is still reported", () => {
  const terms = { vague: ["体验友好"], filler: ["待定", "适当", "尽量"], allowed: [], ruleIds: new Set(), dimensions: new Map() };
  const text = "- [ ] 做得好〔适当优化、体验友好：待定〕\n- [ ] 验收〔尽量：待定〕\n- [ ] 正常的主题〔Resend 留存：待定〕";
  const words = findViolations(stripPending(text), terms).map((v) => `${v.line}:${v.word}`);
  assert.deepEqual(words.sort(), ["1:体验友好", "1:适当", "2:尽量"]);
});
