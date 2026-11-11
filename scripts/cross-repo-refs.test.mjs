import { test } from "node:test";
import assert from "node:assert/strict";
import { findSharedPrefixRefs, findSharedPrefixRefsInIssues } from "./cross-repo-refs.mjs";

test("a repo prefix shared across 顿号 is reported", () => {
  assert.deepEqual(findSharedPrefixRefs("等 thin-muscle-coach#185、#101 做完"), ["thin-muscle-coach#185、#101"]);
});

test("owner/repo prefix shared across a comma or 和 is reported", () => {
  assert.deepEqual(findSharedPrefixRefs("see madlouse/thin-muscle-coach#185, #101"), ["madlouse/thin-muscle-coach#185, #101"]);
  assert.deepEqual(findSharedPrefixRefs("thin-muscle-coach#185 和 #213"), ["thin-muscle-coach#185 和 #213"]);
});

test("each number with its own prefix passes", () => {
  assert.deepEqual(findSharedPrefixRefs("thin-muscle-coach#185、thin-muscle-coach#101、thin-muscle-coach#72"), []);
});

test("a list of this repo's own numbers passes", () => {
  assert.deepEqual(findSharedPrefixRefs("#49、#87、#88 和 #101"), []);
});

test("a cross-repo number followed by prose passes", () => {
  assert.deepEqual(findSharedPrefixRefs("thin-muscle-coach#185（/body），再做本仓库的 #54"), []);
});

test("a rubric item with a single capital before # is not a repository", () => {
  assert.deepEqual(findSharedPrefixRefs("评分 A#17、#27 两项不过"), []);
  assert.deepEqual(findSharedPrefixRefs("U#2、#3 和 V#5"), []);
});

test("several shared-prefix runs on one line are all reported", () => {
  assert.deepEqual(findSharedPrefixRefs("thin-muscle-coach#185、#101 留了言；另见 thin-muscle-coach#72、#213"), [
    "thin-muscle-coach#185、#101",
    "thin-muscle-coach#72、#213",
  ]);
});

test("a very long line without issue numbers returns quickly", () => {
  const line = "a".repeat(400000);
  const start = performance.now();
  assert.deepEqual(findSharedPrefixRefs(line), []);
  assert.ok(performance.now() - start < 1000, "took too long on a long line");
});

test("a very long line of prefixes and numbers stays fast", () => {
  const line = "thin-muscle-coach#1 ".repeat(20000) + "thin-muscle-coach#185、#101";
  const start = performance.now();
  assert.deepEqual(findSharedPrefixRefs(line), ["thin-muscle-coach#185、#101"]);
  assert.ok(performance.now() - start < 1000, "took too long on a long line");
});

test("issue bodies: only issues opened by the repository owner are checked", () => {
  const bad = "等 thin-muscle-coach#185、#101 做完";
  const { checked, hits } = findSharedPrefixRefsInIssues([
    { number: 1, author_association: "OWNER", body: "第一行\n" + bad },
    { number: 2, author_association: "NONE", body: bad },
    { number: 3, author_association: "CONTRIBUTOR", body: bad },
    { number: 4, author_association: "OWNER", body: bad, pull_request: { url: "x" } },
    { number: 5, author_association: "OWNER", body: null },
  ]);
  assert.equal(checked, 2);
  assert.deepEqual(hits, [{ number: 1, line: 2, ref: "thin-muscle-coach#185、#101" }]);
});
