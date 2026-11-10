import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseFence, findVoiceHits, traceGaps } from "./voice-terms.mjs";

const lists = {
  spoken: ["嗯", "对吧", "就是说", "[啊]", "[um]"],
  allowed: ["也就是说", "（不是阀值）"],
  transcription: ["阀值", "Value Coach"],
};
const words = (hits) => hits.map((h) => `${h.line}:${h.word}:${h.kind}`);

test("spoken markers and transcription errors are reported with their line", () => {
  assert.deepEqual(words(findVoiceHits("首屏两步完成。\n嗯，这个按钮对吧\n阈值改成阀值", lists)), ["2:嗯:spoken", "2:对吧:spoken", "3:阀值:transcription"]);
});

test("allowed phrases and a spoken marker quoted on its own are not hits", () => {
  assert.deepEqual(findVoiceHits("也就是说，按钮直达结果。\n口头禅（「嗯」“对吧”`um`）不进稿件。\n阈值（不是阀值）", lists), []);
});

test("transcription errors count inside quotes", () => {
  assert.deepEqual(words(findVoiceHits("品牌名是「Value Coach」。\n把「阀值」设成 1 秒。\n`阀值`是错字", lists)), [
    "1:Value Coach:transcription",
    "2:阀值:transcription",
    "3:阀值:transcription",
  ]);
});

test("a quoted sentence that contains a marker is still a hit", () => {
  assert.deepEqual(words(findVoiceHits("产品负责人说「就是说这里要快」", lists)), ["1:就是说:spoken"]);
});

test("bracketed markers only match standalone interjections", () => {
  assert.deepEqual(words(findVoiceHits("啊，这里要快。\n真好啊！\nUm, it is fast.", lists)), ["1:啊:spoken", "3:um:spoken"]);
});

test("ordinary English is not a hit", () => {
  const text = "Did you know strength training adds years?\nBuild on what you know.\nUh-oh, the build failed.\nDo you know your 1RM?\nTake an umbrella; the album is out.";
  assert.deepEqual(findVoiceHits(text, lists), []);
});

test("fences are scanned unless skipFences, and an unclosed fence is reported", () => {
  const text = "```spoken-markers\n嗯\n```\n正文";
  assert.deepEqual(findVoiceHits(text, lists, { skipFences: true }), []);
  assert.deepEqual(words(findVoiceHits(text, lists)), ["2:嗯:spoken"]);
  assert.deepEqual(words(findVoiceHits("正文\n```\n嗯\n", lists, { skipFences: true })), ["2:```:fence"]);
  assert.deepEqual(words(findVoiceHits("~~~\n对吧\n", lists)), ["2:对吧:spoken", "1:~~~:fence"]);
});

test("a four-backtick fence holds a three-backtick one and closes only on four", () => {
  const nested = "````md\n```\n嗯\n```\n````\n对吧";
  assert.deepEqual(words(findVoiceHits(nested, lists, { skipFences: true })), ["6:对吧:spoken"]);
  assert.deepEqual(words(findVoiceHits(nested, lists)), ["3:嗯:spoken", "6:对吧:spoken"]);
  assert.deepEqual(words(findVoiceHits("````\n```\n嗯", lists, { skipFences: true })), ["1:````:fence"]);
});

test("code files are not parsed for fences", () => {
  assert.deepEqual(words(findVoiceHits("const s = `\n```\n嗯`;", lists, { markdown: false })), ["3:嗯:spoken"]);
});

const head = "| 原句 | 日期 | 原话要点 | 理解与裁决 | 落在哪 | 状态 | 举一反三 |\n|---|---|---|---|---|---|---|\n";

test("every timeline entry from 84 on needs a trace row", () => {
  const timeline = "## 82\n\n> a\n\n## 84\n\n> b\n\n## 85\n\n> c\n";
  const trace = head + "| 82 | 11-09 | a | b | c | 已落实 |\n| 84 | 11-09 | a | b | c | 已落实 | 类别：口述输入流进正式文档；同类位置：技能、检查，都已改 |\n";
  assert.deepEqual(traceGaps(timeline, trace).map((g) => g.n), [85]);
});

test("「举一反三」 needs at least 10 characters without punctuation; 无, -, 同上 count as empty", () => {
  const timeline = "## 84\n## 85\n## 86\n## 87\n## 88\n";
  const trace =
    head +
    "| 84 | 11-09 | a | b | c | 已落实 | 类别：口述输入；同类位置：技能、检查 |\n" +
    "| 85 | 11-09 | a | b | c | 已落实 | 无 |\n" +
    "| 86 | 11-09 | a | b | c | 已落实 | - |\n" +
    "| 87 | 11-09 | a | b | c | 已落实 | 同上。、；——！ |\n" +
    "| 88 | 11-09 | a \\| b | b | c | 已落实 |\n";
  assert.deepEqual(traceGaps(timeline, trace).map((g) => g.n), [85, 86, 87, 88]);
});

test("the glossary holds the lists, and check-terms shares the transcription and allowed lists", () => {
  const glossary = readFileSync("docs/GLOSSARY.md", "utf8");
  for (const name of ["spoken-markers", "allowed-phrases", "transcription-errors", "stale-terms"]) assert.ok(parseFence(glossary, name).length > 0, name);
  const checkTerms = readFileSync("scripts/check-terms.mjs", "utf8");
  assert.match(checkTerms, /parseFence\(glossary, "transcription-errors"\)/);
  assert.match(checkTerms, /parseFence\(glossary, "allowed-phrases"\)/);
  assert.throws(() => parseFence("no block", "spoken-markers"), /no ```spoken-markers block/);
});

test("the repository's own trace and timeline pass", () => {
  assert.deepEqual(traceGaps(readFileSync("docs/requirements/timeline.md", "utf8"), readFileSync("docs/requirements/trace.md", "utf8")), []);
});

test("a spoken marker quoted in the middle of a sentence is treated as naming it (accepted gap, reviewers check)", () => {
  assert.deepEqual(findVoiceHits("这个按钮，「嗯」很快", lists), []);
});

test("timeline headings must be exactly «## N»", () => {
  const trace = "| 84 | a | b | c | d | e | 同类位置在流水线规则和检查脚本里都已改完 |";
  assert.deepEqual(traceGaps("## 84\n", trace), []);
  for (const bad of ["### 85\n", "## 85 补充\n", "#85\n"]) {
    assert.equal(traceGaps("## 84\n" + bad, trace).length, 1, bad);
  }
});
