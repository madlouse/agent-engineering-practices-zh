import { test } from "node:test";
import assert from "node:assert/strict";
import { findSharedPrefixRefs } from "./cross-repo-refs.mjs";

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
