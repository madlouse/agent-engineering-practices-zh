import assert from "node:assert/strict";
import { test } from "node:test";
import { findPending } from "./pending-markers.mjs";

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
