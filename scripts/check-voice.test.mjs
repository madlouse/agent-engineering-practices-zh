import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseFence, findVoiceHits, traceRowsMissingSiblings } from "./voice-terms.mjs";

const lists = { spoken: ["嗯", "对吧", "就是说", "um", "you know"], allowed: ["也就是说", "（不是阀值）"], transcription: ["阀值", "Value Coach"] };

test("spoken markers and transcription errors are reported with their line", () => {
  assert.deepEqual(findVoiceHits("首屏两步完成。\n嗯，这个按钮对吧\n阈值改成阀值", lists), [
    { line: 2, word: "嗯", kind: "spoken" },
    { line: 2, word: "对吧", kind: "spoken" },
    { line: 3, word: "阀值", kind: "transcription" },
  ]);
});

test("allowed phrases and a marker quoted on its own are not hits", () => {
  assert.deepEqual(findVoiceHits("也就是说，按钮直达结果。\n口头禅（「嗯」“对吧”`um`）不进稿件。\n阈值（不是阀值）", lists), []);
});

test("a quoted sentence that contains a marker is still a hit", () => {
  assert.deepEqual(findVoiceHits("产品负责人说「就是说这里要快」", lists), [{ line: 1, word: "就是说", kind: "spoken" }]);
});

test("ASCII markers match whole words, case-insensitive", () => {
  assert.deepEqual(findVoiceHits("Take an umbrella; the album is out.", lists), []);
  assert.deepEqual(findVoiceHits("Um, it is fast, you know.", lists), [
    { line: 1, word: "um", kind: "spoken" },
    { line: 1, word: "you know", kind: "spoken" },
  ]);
});

test("fenced blocks are skipped in markdown, not in code files", () => {
  const text = "```spoken-markers\n嗯\n```\n正文";
  assert.deepEqual(findVoiceHits(text, lists), []);
  assert.deepEqual(findVoiceHits(text, lists, { markdown: false }), [{ line: 2, word: "嗯", kind: "spoken" }]);
});

test("the glossary holds the three lists, and check-terms shares the transcription list", () => {
  const glossary = readFileSync("docs/GLOSSARY.md", "utf8");
  for (const name of ["spoken-markers", "voice-allowed", "transcription-errors", "stale-terms"]) assert.ok(parseFence(glossary, name).length > 0, name);
  assert.match(readFileSync("scripts/check-terms.mjs", "utf8"), /parseFence\(glossary, "transcription-errors"\)/);
  assert.throws(() => parseFence("no block", "spoken-markers"), /no ```spoken-markers block/);
});

test("trace rows from 84 on must fill 「举一反三」, older rows may leave it out", () => {
  const trace = [
    "| 原句 | 日期 | 原话要点 | 理解与裁决 | 落在哪 | 状态 | 举一反三 |",
    "|---|---|---|---|---|---|---|",
    "| 82 | 11-09 | a | b | c | 已落实 |",
    "| 84 | 11-09 | a | b | c | 已落实 | 同类位置：技能、检查 |",
    "| 85 | 11-09 | a | b | c | 已落实 |  |",
    "| 86 | 11-09 | a \\| b | b | c | 已落实 |",
  ].join("\n");
  assert.deepEqual(traceRowsMissingSiblings(trace), [85, 86]);
});
