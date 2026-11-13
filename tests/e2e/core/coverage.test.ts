import { test } from "node:test";
import assert from "node:assert/strict";
import { bytes, coveredRanges, firstParty, summarize, union } from "./coverage.ts";

test("覆盖率：没执行的分支从执行过的函数里扣掉", () => {
  const entry = { url: "x", functions: [{ ranges: [{ startOffset: 0, endOffset: 100, count: 1 }, { startOffset: 40, endOffset: 60, count: 0 }] }, { ranges: [{ startOffset: 70, endOffset: 80, count: 0 }] }] };
  assert.deepEqual(coveredRanges(entry, 100), [[0, 40], [60, 70], [80, 100]]);
});

test("覆盖率：没被调用的函数整段不算", () => {
  assert.deepEqual(coveredRanges({ url: "x", functions: [{ ranges: [{ startOffset: 0, endOffset: 50, count: 0 }] }] }, 50), []);
});

test("覆盖率：几条案例走到的区间取并集，不重复计", () => {
  assert.deepEqual(union([[0, 10], [20, 30]], [[5, 25], [40, 50]]), [[0, 30], [40, 50]]);
  const s = summarize([[{ url: "/a.js", total: 100, covered: [[0, 10]] }], [{ url: "/a.js", total: 100, covered: [[5, 30]] }, { url: "/b.js", total: 100, covered: [] }]]);
  assert.equal(s.covered, 30);
  assert.equal(s.total, 200);
  assert.equal(s.ratio, 0.15);
  assert.equal(bytes([[0, 3], [5, 6]]), 4);
});

test("覆盖率：只算被测站点自己构建出的脚本", () => {
  assert.equal(firstParty("https://velicoach.test/assets/index-Bfsmh4x3.js", "https://velicoach.test"), true);
  assert.equal(firstParty("https://velicoach.test/assets/index-Bfsmh4x3.js?v=1", "https://velicoach.test"), true);
  assert.equal(firstParty("https://velicoach.test/assets/styles-CKRlCpv6.css", "https://velicoach.test"), false);
  assert.equal(firstParty("https://cdn.other.com/assets/x.js", "https://velicoach.test"), false);
  assert.equal(firstParty("https://velicoach.test/explainers/a.js", "https://velicoach.test"), false);
});
