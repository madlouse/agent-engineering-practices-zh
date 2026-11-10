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

test("七项缺一项就报那一项", () => {
  for (const key of ["背景和事实", "为什么要你", "我的建议和理由", "风险和怎么撤回", "怎么回"]) {
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
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周，节奏不变。", "2. 不合并：不变")).some((p) => p.includes("后果去掉合并")));
  assert.ok(checkOwnerBrief(with_("2. 不合并：保持每周，节奏不变。", "2. 不合并")).some((p) => p.includes("选项：后果")));
  assert.ok(checkOwnerBrief(with_("选 1。上月退订原因里「太频繁」占一半。", "合并")).some((p) => p.includes("「我的建议和理由」去掉套话后至少")));
  assert.ok(checkOwnerBrief(with_("打开率可能下降；撤回就是 revert 这个合并，下一期恢复每周。", "撤回")).some((p) => p.includes("「风险和怎么撤回」去掉套话后至少")));
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
    .replace(/(\*\*为什么要你\*\*：).*/, "$1法律：授权只写了转载，改标题算不算改编要你定。")
    .replace("1. 合并：（选了会怎样）", "1. 合并：发全文中文版，标题照原文直译。")
    .replace("2. 不合并：（选了会怎样）", "2. 不合并：本周改发摘要，等作者回复标题的事。")
    .replace("**我的建议和理由**：", "**我的建议和理由**：选 1，授权邮件已贴在票上，标题不改。")
    .replace("**风险和怎么撤回**：", "**风险和怎么撤回**：作者事后反对时撤回：revert 这个合并，页面一小时内下线。")
    .replace(/(\*\*怎么回\*\*：).*/, "$1回「合并 #90」或选项编号「1」「2」。");
  for (const key of ["背景和事实", "为什么要你", "怎么回"]) {
    const keep = TEMPLATE.match(new RegExp(`\\*\\*${key}\\*\\*：.*`))[0];
    const half = filled.replace(new RegExp(`\\*\\*${key}\\*\\*：.*`), keep);
    assert.ok(checkOwnerBrief(half).some((p) => p.includes(`缺「${key}」`)), `${key} 留模板占位不能过`);
  }
  assert.deepEqual(checkOwnerBrief(filled), []);
  assert.equal(briefQuestion(filled), "第 3 周文章用作者授权的中文全文，还是只发摘要？");
});

test("HTML 注释夹在类别行和简报之间也认", () => {
  assert.deepEqual(checkOwnerBrief(GOOD.replace("类别：b\n", "类别：b\n<!--\n说明\n-->\n")), []);
});

// 第二轮复审（#74）两份评审的样例：都是「看着填了、其实是空壳」，必须不过
const BP_BASE = {
  q: "要不要把首页改成三栏布局，并在本周上线？",
  bg: "首页现在是单栏，这个 PR 改成三栏，预览已通过三种版式检查。",
  why: "产品意图：版式取舍属于产品意图。",
  opts: ["1. 合并：首页变成三栏，本周上线。", "2. 不合并：首页保持单栏，下周再议。"],
  rec: "建议合并：三栏符合 PRD 第 4 节的两步原则。",
  risk: "风险是窄屏挤压；撤回方法是 revert 这个 PR。",
  reply: "回「合并 #74」或选项编号。",
};
const bp = (o = {}) => {
  const g = { ...BP_BASE, ...o };
  return ["类别：b", "", "## 决策简报", "", `**要你判断什么**：${g.q}`, `**背景和事实**：${g.bg}`, `**为什么要你**：${g.why}`, "**选项和后果**：", ...g.opts,
    `**我的建议和理由**：${g.rec}`, `**风险和怎么撤回**：${g.risk}`, `**怎么回**：${g.reply}`, ...(g.extra ?? []), "", "---", "细节"].join("\n");
};
const HOLLOW = `类别：票

## 决策简报

**要你判断什么**：是否把本 PR 合并进 feature/v1？
**背景和事实**：见下面
**为什么要你**：产品意图
**选项和后果**：
1. 合并：合并这个 PR
2. 不合并：不合并这个 PR
**我的建议和理由**：我建议合并吧
**风险和怎么撤回**：可以撤回，无风险
**怎么回**：回「合并 #N」或选项编号。

---
`;

test("正例：两份评审的基准简报、CRLF、回「合并 #1」都能过", () => {
  assert.deepEqual(checkOwnerBrief(bp()), []);
  assert.deepEqual(checkOwnerBrief(bp().replace(/\n/g, "\r\n")), []);
  assert.deepEqual(checkOwnerBrief(bp({ reply: "回合并 #1" })), []);
});

test("第二轮反例：整份空壳、模板占位、点了分支的空问题、后置否定、套话都不过", () => {
  assert.ok(checkOwnerBrief(HOLLOW).length >= 6, "hollow.md：七项里至少六项不合格");
  assert.equal(briefQuestion(HOLLOW), null);
  const asks = [
    "是否把本 PR 合并进 feature/v1？", "请产品负责人审阅并确认是否可以合并本 PR 到集成分支？", "你觉得这次整体上改得怎么样，需要现在就拍板吗？",
    "要不要合并 #74 的改动？", "合并合并合并合并合并合并合并合并合并合并合并？", "把标题改成新的并发布", "这个改动你看要不要合并进去好不好？",
    "请你确认一下这个PR是否可以合并吗？", "Should we merge this pull request now?", "Can you please take a look at it?", "你觉得这次的东西整体上怎么样呀？",
    "是否同意按上面说的那样去做呢？", "要不要合并上面背景里说的那件事？", "要不要合并这个改动？", "这个 PR 能合并吗？", "你看这样可以吗？", "同意这样改吗？",
    "合并进 feature/v1 吗？", "Merge?", "Is this OK to merge?", "LGTM?", "这个改动可以上线吗？", "可以合并到集成分支吗？", "这样改行吗？", "你觉得怎么样？",
    "这次的修改是否没问题？", "是否合并这个 PR 到 feature/v1？", "是否按建议合并？", "合并还是不合并？", "接受这个方案吗？", "现在合并可以吗？没问题吧？",
  ];
  for (const q of asks) assert.ok(checkOwnerBrief(bp({ q })).some((p) => p.includes("要你判断什么")), q);
  const whys = ["产品意图", "钱", "涉及钱", "与法律无关。", "跟钱没关系，但要你定。", "产品意图无关，例行合并", "这不是产品意图问题", "观察者要求的", "按流程要你合并",
    "这里和产品意图无关，只是例行合并。", "既不涉及钱也不难撤回，按规矩要你。", "不属于产品意图、钱、法律任何一条。", "（§5.1 哪一条）"];
  for (const why of whys) assert.ok(checkOwnerBrief(bp({ why })).some((p) => p.includes("为什么要你")), why);
  const facts = ["见下面", "见下", "同上", "x", "（改了什么、依据什么事实，一两句）", "改了一些东西"];
  for (const bg of facts) assert.ok(checkOwnerBrief(bp({ bg })).some((p) => p.includes("背景和事实")), bg);
  const optss = [
    ["1. 合并：会被合并。", "2. 不合并：不会合并。"], ["1. 合并：合并这个 PR", "2. 不合并：不合并这个 PR"], ["1. 合并：没有影响哦哦哦", "2. 不合并：没有影响哦哦哦"],
    ["1. 合并：（选了会怎样）", "2. 不合并：（选了会怎样）"], ["1. 合并：会怎样会怎样", "2. 不合并：不会怎样的"], ["合并：首页变成三栏本周上线", "不合并：首页保持单栏"],
    ["1. 合并：首页变成三栏，本周上线。", "2. 不合并：首页保持单栏，下周再议。", "3. 先放着："], ["1. 合并：标题换成新的。不合并：标题保持原样。", "2. 其他：好"],
  ];
  for (const opts of optss) assert.ok(checkOwnerBrief(bp({ opts })).some((p) => p.includes("选项")), opts.join(" / "));
  for (const rec of ["建议合并，没有问题。", "我建议合并吧", "建议如上所述。。。"]) assert.ok(checkOwnerBrief(bp({ rec })).some((p) => p.includes("建议")), rec);
  for (const risk of ["风险很低可以撤回", "可以撤回，无风险", "撤回撤回撤回", "无风险，可撤回。"]) assert.ok(checkOwnerBrief(bp({ risk })).some((p) => p.includes("风险和怎么撤回")), risk);
  for (const reply of ["回「合并 #N」或选项编号。", "选项"]) assert.ok(checkOwnerBrief(bp({ reply })).some((p) => p.includes("怎么回")), reply);
  const shapes = {
    tilde: { extra: ["~~~", "rm -rf", "~~~"] }, tilde4: { extra: ["````js", "x", "````"] }, indent: { extra: ["    code here"] }, tab: { extra: ["\tcode"] },
    pre: { extra: ["<pre>", "code", "</pre>"] }, inlineLong: { bg: "`" + "x".repeat(190) + "`" }, long: { bg: "长".repeat(250) }, cjk199: { bg: "长".repeat(199) },
    asciiWs: { bg: "a ".repeat(150) }, comment: { extra: ["<!--", "x".repeat(3000), "-->"] }, unclosed: { extra: ["```"] },
    details: { extra: ["<details><summary>x</summary>", "    code", "</details>"] }, dup: { extra: ["**要你判断什么**：是否合并？"] },
    commentItem: { q: "<!-- -->是否合并？" }, qInComment: { q: "<!-- 要不要把首页改成三栏布局并在本周上线 -->是否合并？" },
  };
  for (const [name, o] of Object.entries(shapes)) assert.ok(checkOwnerBrief(bp(o)).length > 0, name);
  assert.ok(checkOwnerBrief(["类别：b", "", "决策简报", "====", "", `**要你判断什么**：${BP_BASE.q}`].join("\n")).length > 0, "setext 标题");
  assert.ok(checkOwnerBrief(["", "## 决策简报"].join("\n")).length > 0, "没有类别行");
});
