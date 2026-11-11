import { test } from "node:test";
import assert from "node:assert/strict";
import { blockerRefs, compare, counts, diagramTitle, expectedEdges, findCycle, loadIssues, paginate, parseArgs, parseCounts, parseMermaidEdges, parseTables, regenerate, tableTitle } from "./ticket-table.mjs";

const local = (number, state = "open") => ({ repo: "velicoach", number, state });
const veli = (number, state = "open") => ({ repo: "thin-muscle-coach", number, state });

function issuesOf(list) {
  return new Map(list.map(([number, title, labels, blockedBy]) => [number, { title, labels, blockedBy }]));
}

const ISSUES = () =>
  issuesOf([
    [21, "页脚", ["lane:site", "ready-for-human"], []],
    [22, "主题：浅色和深色", ["lane:site", "ready-for-agent"], [local(15)]],
    [66, "上线", ["lane:site", "ready-for-human", "risk:high"], [local(22), local(5), veli(72), local(29, "closed")]],
    [5, "内容 · 里程碑", ["lane:content"], [local(22)]],
    [15, "流水线开跑前", ["ready-for-human"], []],
    [17, "规格 M1", ["lane:site", "spec"], []],
    [3, "内容总票", ["lane:content"], []],
  ]);

const DOC = `# 拆分

## 1. 结论

**站点车道 4 份规格、3 张开着的票：标签：1 张 \`ready-for-agent\`，2 张 \`ready-for-human\`，0 张暂时没有就绪标签；1 张 \`risk:high\`。内容车道 1 张。**

## 3. 里程碑 → 规格 → 票

### M1 · 规格 #17

| 票 | 标题 | 功能号 | 被谁卡住 | 车道 | 标签 | 11-11 |
|---|---|---|---|---|---|---|
| #21 | 页脚 | F21 | — | 站点 | \`lane:site\` \`ready-for-human\` | 没动 |
| #22 | 主题：浅色和深色 | F24 | #15 | 站点 | \`lane:site\` \`ready-for-agent\` | 改了 |

### M4 · 规格 #20

| 票 | 标题 | 功能号 | 被谁卡住 | 车道 | 标签 | 11-11 |
|---|---|---|---|---|---|---|
| #66 | 上线 | F09 | #22、#5、thin-muscle-coach#72 | 站点 | \`lane:site\` \`ready-for-human\` \`risk:high\` | 等人 |

### 内容车道（总票 #3）

| 票 | 标题 | 功能号 | 被谁卡住 | 车道 | 标签 | 11-11 |
|---|---|---|---|---|---|---|
| #5 | 内容 · 里程碑 | F13 | #22 | 内容 | \`lane:content\` | 改了 |

## 4. 依赖图

\`\`\`mermaid
flowchart LR
  subgraph M1
    T21["#21 页脚"]
    T22["#22 主题：浅色和深色"]
  end
  C15 --> T22
  T22 --> T66
  C5 --> T66
  V72 --> T66
  T22 --> C5
  C15(["#15"])
  class T21 human
\`\`\`

## 5. 别的
`;

test("paginate keeps asking until a short page: 34 blockers arrive as 30 + 4", async () => {
  const all = Array.from({ length: 34 }, (_, i) => i + 1);
  const pages = [];
  const got = await paginate(async (page) => {
    pages.push(page);
    return all.slice((page - 1) * 30, page * 30);
  }, 30);
  assert.deepEqual(got, all);
  assert.deepEqual(pages, [1, 2]);
});

test("paginate asks once more when the last page is exactly full", async () => {
  const pages = [];
  const got = await paginate(async (page) => {
    pages.push(page);
    return page === 1 ? Array(30).fill(0) : [];
  }, 30);
  assert.equal(got.length, 30);
  assert.deepEqual(pages, [1, 2]);
});

test("blockers: open ones only, this repo first, other repos with their prefix", () => {
  assert.deepEqual(blockerRefs([veli(72), local(22), local(29, "closed"), local(5)]), ["#22", "#5", "thin-muscle-coach#72"]);
});

test("the sample doc matches the sample issues; specs, the umbrella issue and issues without a lane label are not expected in the table", () => {
  assert.deepEqual(compare(DOC, ISSUES()), []);
});

test("parseTables reads group, title, blockers and labels; a title may contain an escaped pipe", () => {
  const rows = parseTables(DOC.replace("| 页脚 |", "| 页脚 \\| 法务 |"));
  assert.equal(rows.length, 4);
  assert.deepEqual(
    rows.map((r) => r.group),
    ["M1", "M1", "M4", "内容车道"],
  );
  assert.equal(rows[0].title, "页脚 | 法务");
  assert.deepEqual(rows[2].blockers, ["#22", "#5", "thin-muscle-coach#72"]);
  assert.deepEqual(rows[2].labels, ["lane:site", "ready-for-human", "risk:high"]);
});

test("a blocker added on GitHub after the table was written is reported in the table and in the diagram", () => {
  const issues = ISSUES();
  issues.get(66).blockedBy.push(local(21));
  const problems = compare(DOC, issues);
  assert.ok(problems.some((p) => p.includes("#66") && p.includes("少了 #21")));
  assert.ok(problems.some((p) => p.includes("少了一条边：T21 --> T66")));
});

test("title, label, closed-ticket, missing-ticket and count differences are each reported", () => {
  const issues = ISSUES();
  issues.get(22).title = "主题";
  issues.get(22).labels = ["lane:site"];
  issues.delete(21);
  issues.set(99, { title: "新票", labels: ["lane:site"], blockedBy: [] });
  const problems = compare(DOC, issues).join("\n");
  assert.match(problems, /#22：标题不一样/);
  assert.match(problems, /#22：标签不一样/);
  assert.match(problems, /#21：GitHub 上不是开着的票/);
  assert.match(problems, /#99「新票」开着，§3 的表里没有它/);
  assert.match(problems, /§1 的数字不对/);
});

test("an edge the diagram has but GitHub does not is reported", () => {
  const doc = DOC.replace("  T22 --> C5\n", "  T22 --> C5\n  T21 --> C5\n");
  assert.ok(compare(doc, ISSUES()).some((p) => p.includes("多了一条边：T21 --> C5")));
});

test("expectedEdges and counts", () => {
  const rows = parseTables(DOC);
  const edges = expectedEdges(rows, ISSUES()).map(([a, b]) => `${a}>${b}`);
  assert.deepEqual(edges.sort(), ["C15>T22", "C5>T66", "T22>C5", "T22>T66", "V72>T66"].sort());
  assert.deepEqual(counts(rows, ISSUES()), { site: 3, readyForAgent: 1, readyForHuman: 2, noReadyLabel: 0, riskHigh: 1, content: 1 });
  assert.deepEqual(parseCounts(DOC), { site: 3, readyForAgent: 1, readyForHuman: 2, noReadyLabel: 0, riskHigh: 1, content: 1 });
  assert.equal(parseMermaidEdges(DOC).length, 5);
});

test("findCycle finds a loop among open issues and ignores closed blockers", () => {
  const issues = ISSUES();
  assert.equal(findCycle(issues), null);
  issues.get(22).blockedBy.push(local(5));
  assert.deepEqual(findCycle(issues).slice(-3), [22, 5, 22]);
  issues.get(22).blockedBy.pop();
  issues.get(22).blockedBy.push(local(5, "closed"));
  assert.equal(findCycle(issues), null);
});

test("regenerate rewrites title, blockers, labels, the diagram and the counts, and keeps the hand-written columns", () => {
  const issues = ISSUES();
  issues.get(66).blockedBy.push(local(21));
  issues.get(22).title = "主题";
  issues.get(22).labels = ["lane:site"];
  const out = regenerate(DOC, issues);
  assert.deepEqual(compare(out, issues), []);
  assert.match(out, /\| #22 \| 主题 \| F24 \| #15 \| 站点 \| `lane:site` \| 改了 \|/);
  assert.match(out, /0 张 `ready-for-agent`/);
  assert.match(out, /1 张暂时没有就绪标签/);
  assert.equal(regenerate(out, issues), out, "running it twice changes nothing");
});

test("regenerate refuses to guess when the table lists a closed ticket", () => {
  const issues = ISSUES();
  issues.delete(21);
  assert.throws(() => regenerate(DOC, issues), /#21/);
});

test("a blocker the table lists but GitHub does not have is reported", () => {
  const issues = ISSUES();
  issues.get(22).blockedBy = [];
  const problems = compare(DOC, issues);
  assert.ok(problems.some((p) => p.includes("#22") && p.includes("多了 #15")));
});

test("a blocker that has been closed on GitHub counts as extra in the table", () => {
  const issues = ISSUES();
  issues.get(22).blockedBy = [local(15, "closed")];
  assert.ok(compare(DOC, issues).some((p) => p.includes("#22") && p.includes("多了 #15")));
});

test("the same ticket in the table twice is reported", () => {
  const row = "| #21 | 页脚 | F21 | — | 站点 | `lane:site` `ready-for-human` | 没动 |\n";
  const doc = DOC.replace(row, row + row);
  assert.ok(compare(doc, ISSUES()).some((p) => p.includes("#21") && p.includes("出现了两次")));
});

test("compare reports a dependency cycle", () => {
  const issues = ISSUES();
  issues.get(22).blockedBy.push(local(5));
  assert.ok(compare(DOC, issues).some((p) => p.startsWith("原生依赖有环") && p.includes("#22") && p.includes("#5")));
});

test("paginate stops with an error after maxPages full pages", async () => {
  await assert.rejects(
    paginate(async () => Array(30).fill(0), 30, 3),
    /翻了 3 页/,
  );
});

test("titles are neutralised before they are written into the table and the diagram", () => {
  assert.equal(tableTitle("文章页 /mind/<slug> 和 `code` [x](http://e.com) a\\b"), "文章页 /mind/&lt;slug> 和 code &#91;x](http:&#47;&#47;e.com) ab");
  assert.equal(diagramTitle('a"]<b>`c`[d]\\e'), "abcde");
  const issues = ISSUES();
  issues.get(21).title = "页脚 <script> [x](y) `z`";
  const out = regenerate(DOC, issues);
  assert.match(out, /\| #21 \| 页脚 &lt;script> &#91;x\]\(y\) z \|/);
  assert.match(out, /T21\["#21 页脚 script x\(y\) z"\]/);
  assert.deepEqual(compare(out, issues), [], "the doc with the neutralised title matches GitHub");
});

test("titles: bare links, www., mentions and bidirectional controls are neutralised too", () => {
  assert.equal(tableTitle("见 https://evil.example/x 和 WWW.evil.example，找 @someone"), "见 https:&#47;&#47;evil.example/x 和 WWW&#46;evil.example，找 &#64;someone");
  assert.equal(tableTitle("a\u202Eb\u2066c\u200Fd"), "abcd");
  assert.equal(diagramTitle("a\u202Eb\u2069c"), "abc");
});

test("parseArgs: --write only for this repository, unknown flags and malformed repos are refused", () => {
  assert.deepEqual(parseArgs([]), { write: false, repo: "madlouse/velicoach" });
  assert.deepEqual(parseArgs(["--write"]), { write: true, repo: "madlouse/velicoach" });
  assert.deepEqual(parseArgs(["someone/else"]), { write: false, repo: "someone/else" });
  assert.match(parseArgs(["--write", "someone/else"]).error, /--write 只对 madlouse\/velicoach 用/);
  assert.match(parseArgs(["--write", "Madlouse/velicoach"]).error, /--write 只对/);
  assert.match(parseArgs(["--force"]).error, /不认识的参数/);
  assert.match(parseArgs(["not-a-repo"]).error, /owner\/repo/);
});

test("loadIssues keeps owner-opened issues only, skips pull requests, and fetches every page of blockers", async () => {
  const blockers = Array.from({ length: 34 }, (_, i) => ({ number: i + 100, state: "open", repository_url: "https://api.github.com/repos/madlouse/velicoach" }));
  blockers[32] = { number: 185, state: "open", repository_url: "https://api.github.com/repos/madlouse/thin-muscle-coach" };
  blockers[33] = { number: 29, state: "closed", repository_url: "https://api.github.com/repos/madlouse/velicoach" };
  const calls = [];
  const fetchPage = async (path, page) => {
    calls.push(`${path}#${page}`);
    if (path.endsWith("issues?state=open"))
      return page === 1
        ? [
            { number: 66, title: "上线", labels: [{ name: "lane:site" }], author_association: "OWNER" },
            { number: 70, title: "陌生人的票", labels: [{ name: "lane:site" }], author_association: "NONE" },
            { number: 71, title: "一个 PR", labels: [], author_association: "OWNER", pull_request: {} },
          ]
        : [];
    if (path.includes("/66/")) return blockers.slice((page - 1) * 30, page * 30);
    throw new Error(`unexpected ${path}`);
  };
  const { issues, nonOwnerOpen } = await loadIssues("madlouse/velicoach", fetchPage, 30);
  assert.deepEqual([...issues.keys()], [66]);
  assert.equal(issues.get(66).title, "上线");
  assert.equal(issues.get(66).blockedBy.length, 34);
  assert.deepEqual(issues.get(66).blockedBy[0], { repo: "velicoach", number: 100, state: "open" });
  assert.deepEqual(issues.get(66).blockedBy[32], { repo: "thin-muscle-coach", number: 185, state: "open" });
  assert.deepEqual(issues.get(66).blockedBy[33], { repo: "velicoach", number: 29, state: "closed" });
  assert.deepEqual(issues.get(66).labels, ["lane:site"]);
  assert.deepEqual([...nonOwnerOpen], [70]);
  assert.ok(!calls.some((c) => c.includes("/70/") || c.includes("/71/")), "no blocker requests for issues that are not kept");
});

test("a row for an open issue that the owner did not open gets its own message", () => {
  const issues = ISSUES();
  issues.delete(21);
  const problems = compare(DOC, issues, { nonOwnerOpen: new Set([21]) });
  assert.ok(problems.some((p) => p.includes("#21") && p.includes("不是仓库所有者开的")));
  assert.ok(!problems.some((p) => p.includes("#21") && p.includes("已关闭或不存在")));
});
