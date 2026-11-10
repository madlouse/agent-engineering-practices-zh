import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { ROLE_OF, requiredReviewKinds, reviewVerdict } from "./review-markers.mjs";

// scripts/review-markers.mjs：vc-review 结论标记只认对应评审角色、经 Claude 应用写的、没编辑过的评论（复用 Veli 安全评审 F3、S4）
const SCRIPTS = dirname(fileURLToPath(import.meta.url));
const ROOT = join(SCRIPTS, "..");
const SHA = "a".repeat(40);
const OTHER = "b".repeat(40);
const T1 = "2026-11-09T01:00:00Z";
const T2 = "2026-11-09T02:00:00Z";
const marker = (kind, verdict, sha = SHA) => `<!-- vc-review kind=${kind} verdict=${verdict} sha=${sha} -->`;
const by = (role, body, created_at = T1, slug = "claude") => ({
  body: `<!-- vc-bot role=${role} -->\n结论：……\n${body}`,
  performed_via_github_app: slug === null ? null : { slug },
  created_at,
  updated_at: created_at,
});
const review = (kind, verdict, at, sha) => by(ROLE_OF[kind], marker(kind, verdict, sha), at);

test("评审标记：三种结论各自由对应角色给出才算", () => {
  for (const kind of ["general", "general-b", "content", "security"]) {
    assert.equal(reviewVerdict([review(kind, "pass")], SHA, kind), "pass", kind);
    assert.equal(reviewVerdict([review(kind, "rework")], SHA, kind), "rework", kind);
    assert.equal(reviewVerdict([], SHA, kind), null, kind);
    assert.equal(reviewVerdict([review(kind, "pass", T1, OTHER)], SHA, kind), null, `${kind}：别的提交上的结论不算`);
  }
});

test("评审标记：种类和角色要对上，一种评审的 pass 顶替不了另一种", () => {
  assert.equal(reviewVerdict([by("评审", marker("content", "pass"))], SHA, "content"), null, "站点评审写的 content 结论不算");
  assert.equal(reviewVerdict([by("内容评审", marker("general", "pass"))], SHA, "general"), null, "内容评审写的 general 结论不算");
  assert.equal(reviewVerdict([by("评审", marker("security", "pass"))], SHA, "security"), null);
  assert.equal(reviewVerdict([review("general", "pass")], SHA, "security"), null);
  assert.equal(reviewVerdict([review("general", "pass")], SHA, "content"), null);
});

test("评审标记：做事的角色、主会话写的 pass 不算；角色行不在第一行、没有角色行也不算", () => {
  assert.equal(reviewVerdict([by("implementer", marker("general", "pass"))], SHA, "general"), null);
  assert.equal(reviewVerdict([by("主会话", marker("general", "pass"))], SHA, "general"), null);
  const second = { ...review("general", "pass"), body: `随便写点\n<!-- vc-bot role=评审 -->\n${marker("general", "pass")}` };
  assert.equal(reviewVerdict([second], SHA, "general"), null);
  const bare = { body: marker("general", "pass"), performed_via_github_app: { slug: "claude" }, created_at: T1, updated_at: T1 };
  assert.equal(reviewVerdict([bare], SHA, "general"), null);
});

test("评审标记：不是经 Claude 应用写的不算", () => {
  assert.equal(reviewVerdict([by("评审", marker("general", "pass"), T1, null)], SHA, "general"), null);
  assert.equal(reviewVerdict([by("评审", marker("general", "pass"), T1, "other-app")], SHA, "general"), null);
});

test("评审标记：标记要单独一行；一条评论里有多个标记（含写坏的）整条作废", () => {
  assert.equal(reviewVerdict([by("评审", `结论：${marker("general", "pass")}`)], SHA, "general"), null);
  assert.equal(reviewVerdict([by("评审", `  ${marker("general", "pass")}  `)], SHA, "general"), "pass");
  const two = by("评审", `${marker("general", "rework")}\n${marker("general", "pass")}`);
  assert.equal(reviewVerdict([two], SHA, "general"), null);
  const broken = by("评审", `${marker("general", "pass")}\n<!-- vc-review kind=general verdict=pass -->`);
  assert.equal(reviewVerdict([broken], SHA, "general"), null);
});

test("评审标记：同一 sha 上有一条有效 rework 就是 rework，后来的 pass 盖不过", () => {
  assert.equal(reviewVerdict([review("content", "rework", T1), review("content", "pass", T2)], SHA, "content"), "rework");
  assert.equal(reviewVerdict([review("general", "pass", T1), review("general", "pass", T2)], SHA, "general"), "pass");
  assert.equal(reviewVerdict([review("general", "pass", T1), review("general", "rework", T2, OTHER)], SHA, "general"), "pass", "别的 sha 上的 rework 不影响");
});

test("评审标记：带标记的评论编辑过就按 rework 算，并锁住所有种类", () => {
  const edited = (c) => ({ ...c, updated_at: "2026-11-09T09:00:00Z" });
  assert.equal(reviewVerdict([edited(review("general", "pass"))], SHA, "general"), "rework");
  const tampered = edited(by("评审", marker("general", "rework", OTHER), T2));
  assert.equal(reviewVerdict([review("content", "pass"), tampered], SHA, "content"), "rework");
  const note = edited({ ...review("general", "pass"), body: "<!-- vc-bot role=主会话 -->\n交接说明" });
  assert.equal(reviewVerdict([review("general", "pass"), note], SHA, "general"), "pass", "没有标记名的评论编辑过不影响");
});

test("评审种类：content/ 要内容评审；b 类要两份站点评审；其余一份", () => {
  assert.equal(requiredReviewKinds("content/21-agent-loop", "ticket"), "content");
  for (const ref of ["feat/12-home", "fix/3-nav", "contents/1-x"]) assert.equal(requiredReviewKinds(ref, "ticket"), "general", ref);
  assert.equal(requiredReviewKinds("chore/pipeline-prep", "a"), "general");
  assert.equal(requiredReviewKinds("obs/2026-11-09-x", "b"), "general general-b");
  assert.throws(() => requiredReviewKinds("chore/x", "c"), /类别只能是/);
  assert.throws(() => requiredReviewKinds("chore/x", ""), /类别只能是/);
});

test("b 类：只有一份评审过不了；general-b 只认评审B 写的，两份不能由同一角色顶替", () => {
  const onlyOne = [review("general", "pass")];
  const kinds = requiredReviewKinds("chore/x", "b").split(" ");
  assert.deepEqual(kinds.map((k) => reviewVerdict(onlyOne, SHA, k)), ["pass", null], "只有 kind=general 时 general-b 没有结论");
  assert.equal(reviewVerdict([by("评审", marker("general-b", "pass"))], SHA, "general-b"), null, "评审写的 general-b 不算");
  assert.equal(reviewVerdict([by("评审B", marker("general", "pass"))], SHA, "general"), null, "评审B 写的 general 不算");
  const both = [review("general", "pass"), review("general-b", "pass")];
  assert.deepEqual(kinds.map((k) => reviewVerdict(both, SHA, k)), ["pass", "pass"]);
  assert.equal(reviewVerdict([review("general", "pass"), review("general-b", "rework")], SHA, "general-b"), "rework");
});

test("评审角色名和 .claude/agents/ 里各评审写的评论首行一致", () => {
  const agents = { general: "reviewer.md", "general-b": "reviewer-b.md", content: "content-reviewer.md", security: "security-reviewer.md" };
  for (const [kind, file] of Object.entries(agents)) {
    const md = readFileSync(join(ROOT, ".claude/agents", file), "utf8");
    assert.ok(md.includes(`<!-- vc-bot role=${ROLE_OF[kind]} -->`), `${file} 的评论首行要是 role=${ROLE_OF[kind]}`);
    assert.ok(md.includes(`kind=${kind} verdict=pass|rework`), `${file} 要写 kind=${kind} 的结论标记`);
  }
});

// 从合并脚本里抽出 markers() 的 node -e，不另抄一份：脚本改了，这里跟着测
const CALL = /--input-type=module -e '([^']+)' "\$lib_dir\/review-markers\.mjs"/.exec(readFileSync(join(SCRIPTS, "merge-ticket-pr.sh"), "utf8"))?.[1] ?? "";

test("合并脚本调判定库的方式能跑通", () => {
  const dir = mkdtempSync(join(tmpdir(), "vc-markers-"));
  try {
    assert.ok(CALL.includes("pathToFileURL"), "合并脚本里找不到 markers() 的调用");
    const lib = join(SCRIPTS, "review-markers.mjs");
    const file = join(dir, "c.json");
    const run = (...a) => spawnSync("node", ["--input-type=module", "-e", CALL, lib, ...a], { encoding: "utf8" });
    writeFileSync(file, JSON.stringify([review("content", "pass", T1)]));
    assert.equal(run("reviewVerdictFromFile", file, SHA, "content").stdout.trim(), "pass");
    assert.equal(run("reviewVerdictFromFile", file, SHA, "general").stdout.trim(), "none");
    assert.equal(run("requiredReviewKinds", "content/7-x", "ticket").stdout.trim(), "content");
    assert.equal(run("requiredReviewKinds", "chore/x", "b").stdout.trim(), "general general-b");
    assert.notEqual(run("reviewVerdictFromFile", file, SHA, "bogus").status, 0, "种类不对就拒绝");
    assert.notEqual(run("reviewVerdictFromFile", file, "abc", "general").status, 0, "sha 格式不对就拒绝");
    writeFileSync(file, JSON.stringify([{ ...review("general", "pass"), id: 42, updated_at: T2 }]));
    assert.equal(run("reviewVerdictFromFile", file, SHA, "general").stdout.trim(), "locked:42");
    // 平台在标记后面追加页脚，标记单独一行照样认
    writeFileSync(file, JSON.stringify([{ ...review("general", "pass"), body: `${review("general", "pass").body}\n\n---\n_Generated by [Claude Code](https://claude.ai/code)_` }]));
    assert.equal(run("reviewVerdictFromFile", file, SHA, "general").stdout.trim(), "pass");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("合并脚本逐个核对 requiredReviewKinds 给的每一种评审，类别取自 merge-gates 的输出", () => {
  const sh = readFileSync(join(SCRIPTS, "merge-ticket-pr.sh"), "utf8");
  assert.match(sh, /kinds=\$\(markers requiredReviewKinds "\$head" "\$category"\)/);
  assert.match(sh, /for kind in \$kinds; do/);
  assert.match(sh, /--pr-base "\$base" --target "\$TARGET"/);
  assert.ok(sh.indexOf("merge-gates.mjs\" \"$tgt\"") < sh.indexOf("for kind in $kinds"), "先定类别，再核对评审");
});
