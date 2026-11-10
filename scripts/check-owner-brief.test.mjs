import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { briefQuestion, checkOwnerBrief, MAX_LINES } from "./check-owner-brief.mjs";

// scripts/check-owner-brief.mjs：等产品负责人合并的 PR 要有决策简报（pipeline.md §5.1「要你合并时给什么」）
const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "check-owner-brief.mjs");

const GOOD = `类别：b

## 决策简报

**要你判断什么**：订阅邮件改成每两周一封，还是保持每周一封？
**为什么要你**：产品意图（PRD 第 6 节写的是每周）。
**选项和后果**：
1. 合并：改成每两周，读者收到的邮件减半，内容车道周日少一次起草。
2. 不合并：保持每周，节奏不变。
**我的建议和理由**：选 1。上月退订原因里「太频繁」占一半。
**风险和怎么撤回**：打开率可能下降；撤回就是 revert 这个合并，下一期恢复每周。
**怎么回**：回「合并 #88」或选项编号「1」「2」。

---

## 细节

改了 docs/prd/velicoach.md 第 6 节。
`;

const with_ = (from, to) => {
  assert.ok(GOOD.includes(from), from);
  return GOOD.replace(from, to);
};

test("齐全的简报通过；「要你判断什么」能单独取出来（日报用）", () => {
  assert.deepEqual(checkOwnerBrief(GOOD), []);
  assert.equal(briefQuestion(GOOD), "订阅邮件改成每两周一封，还是保持每周一封？");
});

test("其他写法：标题式、列表式也认", () => {
  const headings = GOOD.replace(/\*\*(要你判断什么|为什么要你|选项和后果|我的建议和理由|风险和怎么撤回|怎么回)\*\*：/g, "### $1\n");
  assert.deepEqual(checkOwnerBrief(headings), []);
  const list = GOOD.replace(/\*\*(要你判断什么|为什么要你|我的建议和理由|风险和怎么撤回|怎么回)\*\*：/g, "- $1：");
  assert.deepEqual(checkOwnerBrief(list), []);
});

test("简报要在最上面：没有、或在别的段落后面都不算", () => {
  assert.match(checkOwnerBrief("类别：b\n\n## 改了什么\nx\n")[0], /最上面.*没有「决策简报」/);
  assert.match(checkOwnerBrief(with_("## 决策简报", "## 背景\n说明\n\n## 决策简报"))[0], /最上面/);
  assert.match(checkOwnerBrief("")[0], /最上面/);
  assert.equal(briefQuestion("类别：b\n"), null);
});

test("五项和「怎么回」缺一项就报那一项", () => {
  for (const key of ["为什么要你", "我的建议和理由", "怎么回"]) {
    const body = GOOD.split("\n").filter((l) => !l.startsWith(`**${key}**`)).join("\n");
    assert.ok(checkOwnerBrief(body).some((p) => p.includes(`缺「${key}」`)), key);
  }
  const noQ = with_("**要你判断什么**：订阅邮件改成每两周一封，还是保持每周一封？", "**要你判断什么**：");
  assert.ok(checkOwnerBrief(noQ).some((p) => p.includes("缺「要你判断什么」")));
});

test("「要你判断什么」不能是「请审阅 / 请确认」这类空话，要是一句问句", () => {
  for (const ask of ["请审阅", "请确认。", "请审阅本 PR", "麻烦看一下", "Review", "请合并"]) {
    const body = with_("订阅邮件改成每两周一封，还是保持每周一封？", ask);
    assert.ok(checkOwnerBrief(body).some((p) => p.includes("是空话")), ask);
  }
  const notQuestion = with_("订阅邮件改成每两周一封，还是保持每周一封？", "订阅邮件改成每两周一封");
  assert.ok(checkOwnerBrief(notQuestion).some((p) => p.includes("要写成问句")));
  const twoLines = with_("还是保持每周一封？", "还是保持每周一封？\n另外顺便看看排版？");
  assert.ok(checkOwnerBrief(twoLines).some((p) => p.includes("要一句话")));
  // 「请确认」开头、后面有实际问题的不算空话
  assert.deepEqual(checkOwnerBrief(with_("订阅邮件改成", "请确认：订阅邮件改成")), []);
});

test("「为什么要你」要落在 §5.1 的一条；选项至少两个且写不合并；风险写怎么撤回；怎么回写合并 #N 或编号", () => {
  assert.ok(checkOwnerBrief(with_("产品意图（PRD 第 6 节写的是每周）。", "改动比较大。")).some((p) => p.includes("没落在 §5.1")));
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周，节奏不变。\n", "")).some((p) => p.includes("至少列两个选项")));
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周", "2. 先放着：保持每周")).some((p) => p.includes("「不合并」会怎样")));
  assert.ok(checkOwnerBrief(with_("撤回就是 revert 这个合并，下一期恢复每周", "影响不大")).some((p) => p.includes("没写怎么撤回")));
  assert.ok(checkOwnerBrief(with_("回「合并 #88」或选项编号「1」「2」。", "回复即可。")).some((p) => p.includes("「怎么回」")));
});

test("不要读代码、一屏以内：简报里有代码块或超过一屏都报；分隔线下面的细节不算", () => {
  assert.ok(checkOwnerBrief(with_("**怎么回**", "```js\nx()\n```\n**怎么回**")).some((p) => p.includes("代码块")));
  const long = with_("**怎么回**", Array.from({ length: MAX_LINES }, (_, i) => `补充 ${i}`).join("\n") + "\n**怎么回**");
  assert.ok(checkOwnerBrief(long).some((p) => p.includes("超过一屏")));
  const below = GOOD + "```js\n" + Array.from({ length: 50 }, (_, i) => `l${i}`).join("\n") + "\n```\n";
  assert.deepEqual(checkOwnerBrief(below), []);
});

test("命令行：齐全退出 0，不齐全打印缺什么、退出 1；--question 打印那一句", () => {
  const dir = mkdtempSync(join(tmpdir(), "vc-brief-"));
  try {
    const run = (body, ...flags) => {
      writeFileSync(join(dir, "body"), body);
      return spawnSync("node", [SCRIPT, join(dir, "body"), ...flags], { encoding: "utf8" });
    };
    assert.equal(run(GOOD).status, 0);
    const bad = run("类别：b\n\n## 决策简报\n**要你判断什么**：请审阅\n");
    assert.equal(bad.status, 1);
    assert.match(bad.stdout, /决策简报不齐全/);
    assert.match(bad.stdout, /是空话/);
    const q = run(GOOD, "--question");
    assert.equal(q.status, 0);
    assert.equal(q.stdout.trim(), "订阅邮件改成每两周一封，还是保持每周一封？");
    assert.equal(run("类别：b\n", "--question").status, 1);
    assert.equal(spawnSync("node", [SCRIPT], { encoding: "utf8" }).status, 2);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
