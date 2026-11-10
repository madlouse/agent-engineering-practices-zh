import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { briefQuestion, checkOwnerBrief, MAX_LINE, MAX_LINES } from "./check-owner-brief.mjs";

// scripts/check-owner-brief.mjs：等产品负责人合并的 PR 要有决策简报（pipeline.md §5.2）
const HERE = dirname(fileURLToPath(import.meta.url));
const SCRIPT = join(HERE, "check-owner-brief.mjs");
const TEMPLATE = readFileSync(join(HERE, "../.github/pull_request_template.md"), "utf8");

const GOOD = `类别：b

## 决策简报

**要你判断什么**：订阅邮件改成每两周一封，还是保持每周一封？
**背景和事实**：PRD 第 6 节定的是每周一封；上月 40 个退订里有 21 个选了「太频繁」。
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

// 评审B 在 #74 构造的反例（t1–t8），原样保留
const SKELETON_OPTS = "**选项和后果**：\n1. 合并：\n2. 不合并：\n";
const REVIEW_B = {
  t1: `类别：b\n\n## 决策简报\n\n**要你判断什么**：要不要合并这个 PR？\n**为什么要你**：产品意图\n${SKELETON_OPTS}**我的建议和理由**：合并\n**风险和怎么撤回**：撤回\n**怎么回**：回「合并 #N」或选项编号。\n`,
  t1q: `类别：b\n\n## 决策简报\n\n**要你判断什么**：好不好？\n**为什么要你**：产品意图\n${SKELETON_OPTS}**我的建议和理由**：合并\n**风险和怎么撤回**：撤回\n**怎么回**：回「合并 #N」或选项编号。\n`,
  t3b: `类别：票\n\n## 决策简报\n\n**要你判断什么**：要不要合并？\n**为什么要你**：（§5.1 哪一条：产品意图、钱、法律、难撤回、权限设置、观察者放宽、内容定稿）\n${SKELETON_OPTS}**我的建议和理由**：合并\n**风险和怎么撤回**：撤回\n**怎么回**：回「合并 #N」或选项编号。\n\n---\n\n## 做了什么\n`,
  t4: `类别：b\n\n## 决策简报\n\n**要你判断什么**：是否合并？\n**为什么要你**：产品意图\n${SKELETON_OPTS}**我的建议和理由**：\n~~~\ndiff --git a/x b/x\n+code\n~~~\n    indented code\n\n**风险和怎么撤回**：撤回\n**怎么回**：回「合并 #N」或选项编号。\n`,
  t5: `类别：b\n\n## 决策简报\n\n**要你判断什么**：是否合并？\n**为什么要你**：产品意图\n${SKELETON_OPTS}**我的建议和理由**：${"x".repeat(5000)}\n**风险和怎么撤回**：撤回\n**怎么回**：回「合并 #N」或选项编号。\n`,
  t6: `类别：b\n\n## 决策简报\n\n**要你判断什么**：是否合并？\n**为什么要你**：不涉及钱，也不难撤回\n${SKELETON_OPTS}**我的建议和理由**：合并\n**风险和怎么撤回**：撤回\n**怎么回**：回「合并 #N」或选项编号。\n`,
  t7: "类别：b\n\n## 决策简报\n\n### 要你判断什么\n是否合并？\n### 为什么要你\n权限设置\n### 选项和后果\n- 合并：x\n- 不合并：y\n### 我的建议和理由\n合并\n### 风险和怎么撤回\n回退\n### 怎么回\n合并 #1\n",
  t8: "## 决策简报\n\n**要你判断什么**：是否合并？\n",
};

const with_ = (from, to) => {
  assert.ok(GOOD.includes(from), from);
  return GOOD.replace(from, to);
};

test("合格的简报通过；「要你判断什么」能单独取出来（日报用）", () => {
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
  for (const ask of ["请审阅", "请确认。", "请审阅本 PR", "麻烦看一下", "Review", "请合并", "是否合并？", "要不要合并这个 PR？", "可以合并吗？", "你同意吗？", "确认吗？", "好不好？", "Please review?", "请审阅这个 PR 吗？"]) {
    const body = with_("订阅邮件改成每两周一封，还是保持每周一封？", ask);
    assert.ok(checkOwnerBrief(body).some((p) => p.includes("是空话")), ask);
  }
  // 点名了一点但太短：去掉语气词后不到 10 个字
  assert.ok(checkOwnerBrief(with_("订阅邮件改成每两周一封，还是保持每周一封？", "改成两周吗？")).some((p) => p.includes("没点名要决定的事")));
  const notQuestion = with_("订阅邮件改成每两周一封，还是保持每周一封？", "订阅邮件改成每两周一封");
  assert.ok(checkOwnerBrief(notQuestion).some((p) => p.includes("要写成问句")));
  const twoLines = with_("还是保持每周一封？", "还是保持每周一封？\n另外顺便看看排版？");
  assert.ok(checkOwnerBrief(twoLines).some((p) => p.includes("要一句话")));
  // 「请确认」开头、后面有实际问题的不算空话
  assert.deepEqual(checkOwnerBrief(with_("订阅邮件改成", "请确认：订阅邮件改成")), []);
});

test("「为什么要你」要落在 §5.1 的一条；选项至少两个且写不合并；风险写怎么撤回；怎么回写合并 #N 或编号", () => {
  assert.ok(checkOwnerBrief(with_("产品意图（PRD 第 6 节写的是每周）。", "改动比较大。")).some((p) => p.includes("没有肯定地落在 §5.1")));
  for (const neg of ["不涉及钱，也不难撤回", "没有产品意图的变化", "不是权限设置"]) {
    assert.ok(checkOwnerBrief(with_("产品意图（PRD 第 6 节写的是每周）。", neg)).some((p) => p.includes("没有肯定地落在 §5.1")), neg);
  }
  assert.deepEqual(checkOwnerBrief(with_("产品意图（PRD 第 6 节写的是每周）。", "不改就违背 PRD：产品意图。")), [], "否定之外还有肯定的那一条");
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周，节奏不变。", "2. 不合并：不变")).some((p) => p.includes("后果至少 6 个字")));
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周，节奏不变。", "2. 不合并")).some((p) => p.includes("选项：后果")));
  assert.ok(checkOwnerBrief(with_("选 1。上月退订原因里「太频繁」占一半。", "合并")).some((p) => p.includes("「我的建议和理由」至少")));
  assert.ok(checkOwnerBrief(with_("打开率可能下降；撤回就是 revert 这个合并，下一期恢复每周。", "撤回")).some((p) => p.includes("「风险和怎么撤回」至少")));
  assert.ok(checkOwnerBrief(GOOD.replace(/^\*\*背景和事实\*\*.*\n/m, "")).some((p) => p.includes("缺「背景和事实」")));
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周，节奏不变。\n", "")).some((p) => p.includes("至少列两个选项")));
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周", "2. 先放着：保持每周")).some((p) => p.includes("「不合并」会怎样")));
  assert.ok(checkOwnerBrief(with_("撤回就是 revert 这个合并，下一期恢复每周", "影响不大")).some((p) => p.includes("没写怎么撤回")));
  assert.ok(checkOwnerBrief(with_("回「合并 #88」或选项编号「1」「2」。", "回复即可。")).some((p) => p.includes("「怎么回」")));
});

test("不要读代码、一屏以内：简报里有代码块或超过一屏都报；分隔线下面的细节不算", () => {
  assert.ok(checkOwnerBrief(with_("**怎么回**", "```js\nx()\n```\n**怎么回**")).some((p) => p.includes("代码块")));
  const long = with_("**怎么回**", Array.from({ length: MAX_LINES }, (_, i) => `补充 ${i}`).join("\n") + "\n**怎么回**");
  assert.ok(checkOwnerBrief(long).some((p) => p.includes("超过一屏")));
  for (const code of ["~~~\nx()\n~~~\n", "    const x = 1;\n", "\tx();\n"]) {
    assert.ok(checkOwnerBrief(with_("**怎么回**", code + "**怎么回**")).some((p) => p.includes("代码块")), code);
  }
  assert.ok(checkOwnerBrief(with_("选 1。", "选 1。" + "很".repeat(MAX_LINE))).some((p) => p.includes(`超过 ${MAX_LINE} 字`)));
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
    assert.match(bad.stdout, /决策简报不合格/);
    assert.match(bad.stdout, /是空话/);
    const q = run(GOOD, "--question");
    assert.equal(q.status, 0);
    assert.equal(q.stdout.trim(), "订阅邮件改成每两周一封，还是保持每周一封？");
    const noBrief = run("类别：b\n", "--question");
    assert.equal(noBrief.status, 1);
    assert.match(noBrief.stdout, /^简报不合格：/);
    const weak = run(REVIEW_B.t1, "--question");
    assert.equal(weak.status, 1, "问题能取出来、但简报不合格的，日报不原样列");
    assert.match(weak.stdout, /^简报不合格：/);
    assert.equal(spawnSync("node", [SCRIPT], { encoding: "utf8" }).status, 2);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("评审B 的反例 t1–t8 都不能过", () => {
  for (const [name, body] of Object.entries(REVIEW_B)) assert.ok(checkOwnerBrief(body).length > 0, name);
  assert.ok(checkOwnerBrief(REVIEW_B.t4).some((p) => p.includes("代码块")), "t4：~~~ 和缩进代码");
  assert.ok(checkOwnerBrief(REVIEW_B.t5).some((p) => p.includes(`超过 ${MAX_LINE} 字`)), "t5：一行 5000 字");
  assert.ok(checkOwnerBrief(REVIEW_B.t6).some((p) => p.includes("没有肯定地落在")), "t6：否定不算");
  assert.ok(checkOwnerBrief(REVIEW_B.t7).some((p) => p.includes("是空话")), "t7：是否合并");
});

test("PR 模板：骨架原样不能过；按模板填完能过（注释不挡简报）", () => {
  assert.ok(checkOwnerBrief(TEMPLATE).length > 0);
  const filled = TEMPLATE
    .replace("类别：票", "类别：内容定稿")
    .replace(/(\*\*要你判断什么\*\*：).*/, "$1第 3 周文章用作者授权的中文全文，还是只发摘要？")
    .replace(/(\*\*背景和事实\*\*：).*/, "$1作者邮件同意转载中文全文，但没写能不能改标题。")
    .replace(/(\*\*为什么要你\*\*：).*/, "$1法律（授权范围）和内容定稿。")
    .replace("1. 合并：（选了会怎样）", "1. 合并：发全文中文版，标题照原文直译。")
    .replace("2. 不合并：（选了会怎样）", "2. 不合并：本周改发摘要，等作者回复标题的事。")
    .replace("**我的建议和理由**：", "**我的建议和理由**：选 1，授权邮件已贴在票上，标题不改。")
    .replace("**风险和怎么撤回**：", "**风险和怎么撤回**：作者事后反对时撤回：revert 这个合并，页面一小时内下线。");
  assert.deepEqual(checkOwnerBrief(filled), []);
  assert.equal(briefQuestion(filled), "第 3 周文章用作者授权的中文全文，还是只发摘要？");
});

test("HTML 注释夹在类别行和简报之间也认", () => {
  assert.deepEqual(checkOwnerBrief(GOOD.replace("类别：b\n", "类别：b\n<!--\n说明\n-->\n")), []);
});
