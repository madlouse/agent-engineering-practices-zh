import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, writeFileSync, renameSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { checkBase, classifyBranch, declaredCategory } from "./merge-gates.mjs";

// scripts/merge-gates.mjs：合并脚本替票的 PR 把的「改动范围」关（pipeline.md §5、§8 第 0 阶段）
const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "merge-gates.mjs");

function repo() {
  const dir = mkdtempSync(join(tmpdir(), "vc-gates-"));
  const git = (...a) => execFileSync("git", a, { cwd: dir, encoding: "utf8" }).trim();
  git("init", "-q", "-b", "base");
  git("config", "user.email", "t@example.invalid");
  git("config", "user.name", "t");
  const write = (path, body) => {
    mkdirSync(dirname(join(dir, path)), { recursive: true });
    writeFileSync(join(dir, path), body);
  };
  const commit = (msg) => { git("add", "-A"); git("commit", "-q", "-m", msg); return git("rev-parse", "HEAD"); };
  write("package.json", JSON.stringify({ scripts: { test: "node --test", "check:terms": "node scripts/check-terms.mjs" } }));
  write("src/a.ts", "export const a = 1;\n");
  write("src/content/post.ts", "export default {};\n");
  write("scripts/merge-ticket-pr.sh", "echo\n");
  write("docs/standards/pipeline.md", "# 流水线\n");
  write("scripts/a.test.mjs", "test('a', () => {});\n");
  write(".gitignore", ".pr-body\n");
  commit("base");
  // 和合并脚本一样：第三个参数是分支名，由脚本自己判断是不是票
  const run = (head, ref, body = "", flags = []) => {
    writeFileSync(join(dir, ".pr-body"), body);
    return spawnSync("node", [SCRIPT, "base", head, ref, join(dir, ".pr-body"), ...flags], { cwd: dir, encoding: "utf8" });
  };
  const branch = (name) => git("checkout", "-q", "-b", name, "base");
  return { dir, git, write, commit, run, branch, cleanup: () => rmSync(dir, { recursive: true, force: true }) };
}

test("分支分类：feat/、fix/、content/ 带票号算票，其余不算", () => {
  assert.deepEqual(classifyBranch("feat/12-home"), { kind: "ticket", ticket: "12" });
  assert.deepEqual(classifyBranch("fix/3-nav"), { kind: "ticket", ticket: "3" });
  assert.deepEqual(classifyBranch("content/21-agent-loop"), { kind: "ticket", ticket: "21" });
  for (const ref of ["chore/pipeline-prep", "obs/2026-11-09-x"]) {
    assert.deepEqual(classifyBranch(ref), { kind: "other", ticket: "" }, ref);
  }
  // 出错时拒绝：漏了票号、前缀写错的都不能当成 chore 放行
  for (const ref of ["feat/home", "content/x", "fix/nav", "feature/12-x", "test/12-x", "chore", "main", "chore/", "obs/", "Chore/x", "Feat/12-x"]) {
    assert.deepEqual(classifyBranch(ref), { kind: "invalid", ticket: "" }, ref);
  }
});

test("门槛文件：站点票和内容票改源码、内容放行；改门槛文件（含改名挪走）拒绝", () => {
  const r = repo();
  try {
    r.branch("feat/1-ok"); r.write("src/a.ts", "export const a = 2;\n");
    assert.equal(r.run(r.commit("src"), "feat/1-ok").status, 0);
    r.branch("content/2-ok"); r.write("src/content/post.ts", "export default { a: 1 };\n");
    assert.equal(r.run(r.commit("post"), "content/2-ok").status, 0);

    const gates = [
      "scripts/merge-ticket-pr.sh", "scripts/merge-gates.mjs", "scripts/review-markers.mjs", "scripts/merge-gates.test.mjs",
      "scripts/check-vague.mjs", "scripts/check-voice.mjs", "scripts/voice-terms.mjs", "docs/standards/pipeline.md", "docs/standards/quality-terms.md", "docs/GLOSSARY.md",
      ".github/workflows/site-db-migrate.yml", ".claude/agents/reviewer.md", ".claude/settings.json", "docs/delivery/loops/site-runner.md",
      "eslint.config.mjs",
    ];
    gates.forEach((f, i) => {
      for (const prefix of ["feat", "content"]) {
        const ref = `${prefix}/${10 + i}-gate`;
        r.branch(ref); r.write(f, `changed ${i}\n`);
        const res = r.run(r.commit(f), ref);
        assert.equal(res.status, 1, `${ref} 改 ${f} 要拒绝`);
        assert.ok(res.stdout.includes(`改了定义门槛的文件 ${f}`), res.stdout);
      }
    });

    r.branch("fix/5-move"); renameSync(join(r.dir, "docs/standards/pipeline.md"), join(r.dir, "docs/standards/other.md"));
    assert.equal(r.run(r.commit("move"), "fix/5-move").status, 1, "改名挪走也算动了门槛文件");

    r.branch("chore/pipeline"); r.write("scripts/merge-ticket-pr.sh", "echo 2\n");
    assert.equal(r.run(r.commit("chore"), "chore/pipeline").status, 0, "主会话的 chore/ PR 不受这条限制");
  } finally { r.cleanup(); }
});

test("package.json：票可以新增命令，不能改或删已有的", () => {
  const r = repo();
  try {
    r.branch("feat/1-add");
    r.write("package.json", JSON.stringify({ scripts: { test: "node --test", "check:terms": "node scripts/check-terms.mjs", "check:x": "y" } }));
    assert.equal(r.run(r.commit("add"), "feat/1-add").status, 0);
    r.branch("content/2-weaken");
    r.write("package.json", JSON.stringify({ scripts: { test: "true", "check:terms": "node scripts/check-terms.mjs" } }));
    const res = r.run(r.commit("weaken"), "content/2-weaken");
    assert.equal(res.status, 1);
    assert.match(res.stdout, /scripts\.test 被改或被删/);
  } finally { r.cleanup(); }
});

test("和分叉点比：base 在票开分支后改了门槛文件，不算票改的", () => {
  const r = repo();
  try {
    r.branch("feat/1-x"); r.write("src/a.ts", "export const a = 3;\n");
    const head = r.commit("ticket work");
    r.git("checkout", "-q", "base");
    r.write("docs/standards/pipeline.md", "# 流水线 v2\n");
    r.commit("base moved on");
    const res = r.run(head, "feat/1-x");
    assert.equal(res.status, 0, res.stdout);
  } finally { r.cleanup(); }
});

test("关闭关键字：不能关状态 issue #13；票的 PR 只能关自己那张票", () => {
  const r = repo();
  try {
    r.branch("content/12-x"); r.write("src/content/post.ts", "export default { b: 1 };\n");
    const head = r.commit("work");
    assert.equal(r.run(head, "content/12-x", "Closes #12").status, 0);
    for (const body of ["this does not close #13", "Fixes: #13", "Resolves madlouse/velicoach#13"]) {
      const res = r.run(head, "chore/x", body);
      assert.equal(res.status, 1, body);
      assert.match(res.stdout, /状态 issue 不能被 PR 关掉/);
    }
    const other = r.run(head, "content/12-x", "Closes #12, fixes #14");
    assert.equal(other.status, 1);
    assert.match(other.stdout, /会关掉别的 issue #14/);
    r.branch("feat/9-msg"); r.write("src/a.ts", "export const a = 5;\n");
    assert.equal(r.run(r.commit("closed #13 by accident"), "feat/9-msg").status, 1, "提交说明里的关闭关键字也查");
  } finally { r.cleanup(); }
});

test("票的 PR 不能削弱测试：删测试文件、新增 .only / .skip / eslint-disable；环境门控不误伤", () => {
  const r = repo();
  try {
    r.branch("feat/1-del"); r.git("rm", "-q", "scripts/a.test.mjs");
    const del = r.commit("del");
    assert.match(r.run(del, "feat/1-del").stdout, /删了测试文件 scripts\/a\.test\.mjs/);
    assert.equal(r.run(del, "chore/del").status, 0, "不是票的 PR 不受限");

    for (const [name, code] of [["only", "test.only('a', () => {});"], ["obj", "test('a', { skip: true }, () => {});"], ["todo", "test.todo('a');"]]) {
      const ref = `fix/2-${name}`;
      r.branch(ref); r.write("scripts/a.test.mjs", code + "\n");
      assert.match(r.run(r.commit(name), ref).stdout, /跳过或只跑部分测试/, code);
    }
    r.branch("content/3-dis"); r.write("src/a.ts", "// eslint-disable-next-line\nexport const a = 6;\n");
    assert.match(r.run(r.commit("dis"), "content/3-dis").stdout, /关掉 lint/);
    r.branch("feat/4-env"); r.write("scripts/a.test.mjs", "test('a', { skip: !process.env.E2E }, () => {});\n");
    assert.equal(r.run(r.commit("env"), "feat/4-env").status, 0);
  } finally { r.cleanup(); }
});

test("分支名不合规：改门槛文件、削弱测试的同一组改动，换个分支名也绕不过去", () => {
  const r = repo();
  try {
    r.branch("feat/landing"); r.write("scripts/merge-ticket-pr.sh", "#!/bin/sh\nexit 0\n");
    const head = r.commit("weaken gate");
    for (const ref of ["feat/landing", "feature/12-x", "test/12-x"]) {
      const res = r.run(head, ref);
      assert.equal(res.status, 1, ref);
      assert.match(res.stdout, /分支名不合规/, ref);
    }
    assert.equal(r.run(head, "feat/12-ok").status, 1, "按票处理时照样拦住改门槛文件");
  } finally { r.cleanup(); }
});

// pipeline.md §5.1「谁合并」：base、类别和 b 类的判定
const category = (res) => /^category=(\S+)$/m.exec(res.stdout)?.[1];

test("base：上线前只合并进 feature/v1，base 是 site 的拒绝；上线后只合并进 site", () => {
  assert.deepEqual(checkBase("feature/v1", "feature/v1"), []);
  assert.deepEqual(checkBase("site", "site"), []);
  assert.match(checkBase("site", "feature/v1")[0], /site 只接受产品负责人确认的上线合并/);
  assert.equal(checkBase("main", "feature/v1").length, 1);
  assert.equal(checkBase("feature/v1", "site").length, 1, "上线后 feature/v1 不再是目标");
  assert.equal(checkBase("x", "x").length, 1, "目标分支只能是 feature/v1 或 site");
  const r = repo();
  try {
    r.branch("feat/1-base"); r.write("src/a.ts", "export const a = 9;\n");
    const head = r.commit("w");
    const bad = r.run(head, "feat/1-base", "类别：票", ["--pr-base", "site", "--target", "feature/v1"]);
    assert.equal(bad.status, 1);
    assert.match(bad.stdout, /base 是 site/);
    const ok = r.run(head, "feat/1-base", "类别：票", ["--pr-base", "feature/v1", "--target", "feature/v1"]);
    assert.equal(ok.status, 0, ok.stdout);
    assert.equal(category(ok), "ticket");
    assert.equal(r.run(head, "feat/1-base", "", ["--pr-base", "feature/v1"]).status, 2, "--pr-base 和 --target 要成对");
  } finally { r.cleanup(); }
});

test("类别行：只认正文第一行；正文为空时不拿后面的标题当类别", () => {
  for (const [body, want] of [["类别：a\n说明", "a"], ["  类别: b  \n", "b"], ["类别：票", "票"], ["类别：内容定稿", "内容定稿"], ["类别：A", "a"]]) {
    assert.equal(declaredCategory(body), want, body);
  }
  for (const body of ["", "\n类别：a", "说明\n类别：a", "类别：c", "类别：a 类", "类别：a / b"]) assert.equal(declaredCategory(body), null, body);
});

test("不是票的 PR：写 a 且不碰门槛才算 a；没写、写 b、改门槛文件或已有命令一律按 b", () => {
  const r = repo();
  try {
    r.branch("chore/docs"); r.write("docs/notes.md", "x\n");
    const docs = r.commit("docs");
    assert.equal(category(r.run(docs, "chore/docs", "类别：a\n加一条检查")), "a");
    assert.equal(category(r.run(docs, "chore/docs", "加一条检查")), "b", "没写类别按 b");
    assert.equal(category(r.run(docs, "chore/docs", "类别：b")), "b");
    assert.equal(category(r.run(docs, "chore/docs", "类别：票")), "b", "类别和分支对不上按 b");
    assert.equal(category(r.run(docs, "chore/docs", "标题\n类别：a")), "b", "类别不在第一行按 b");

    r.branch("chore/gate"); r.write("docs/standards/pipeline.md", "# 流水线 v2\n");
    const gate = r.run(r.commit("gate"), "chore/gate", "类别：a");
    assert.equal(gate.status, 0, gate.stdout);
    assert.equal(category(gate), "b", "改了门槛文件、说明写 a，也按 b");
    assert.match(gate.stdout, /按 b 类处理：改了门槛文件 docs\/standards\/pipeline\.md/);

    r.branch("chore/pkg");
    r.write("package.json", JSON.stringify({ scripts: { test: "true", "check:terms": "node scripts/check-terms.mjs" } }));
    assert.equal(category(r.run(r.commit("pkg"), "chore/pkg", "类别：a")), "b", "改了已有检查命令按 b");
  } finally { r.cleanup(); }
});

test("票的 PR：类别写内容定稿的不合并（等产品负责人），写 a / b 的拒绝；没写按票", () => {
  const r = repo();
  try {
    r.branch("content/7-final"); r.write("src/content/post.ts", "export default { c: 1 };\n");
    const head = r.commit("final");
    const fin = r.run(head, "content/7-final", "类别：内容定稿");
    assert.equal(fin.status, 1);
    assert.match(fin.stdout, /等产品负责人本人合并/);
    assert.equal(r.run(head, "content/7-final", "类别：b").status, 1);
    assert.equal(category(r.run(head, "content/7-final", "类别：票")), "ticket");
    assert.equal(category(r.run(head, "content/7-final", "")), "ticket");
  } finally { r.cleanup(); }
});

test("权限设置只归产品负责人：任何 PR 改了 .claude/settings*.json 都不合并", () => {
  const r = repo();
  try {
    for (const [ref, body] of [["chore/perm", "类别：a"], ["chore/perm-b", "类别：b"], ["obs/2026-11-09-perm", "类别：b"], ["feat/3-perm", "类别：票"]]) {
      r.branch(ref); r.write(".claude/settings.json", `{"permissions":{"allow":["Bash(*)"]}}\n`);
      const res = r.run(r.commit(ref), ref, body);
      assert.equal(res.status, 1, ref);
      assert.match(res.stdout, /改了权限设置 \.claude\/settings\.json：等产品负责人合并/, ref);
      assert.equal(category(res), undefined, ref);
    }
    r.branch("chore/perm-local"); r.write(".claude/settings.local.json", "{}\n");
    assert.equal(r.run(r.commit("local"), "chore/perm-local", "类别：b").status, 1, "settings.local.json 也算");
  } finally { r.cleanup(); }
});

test("不是票的 PR 削弱检查或改红线，说明写 a 也按 b（评审B 的三条复现）", () => {
  const r = repo();
  try {
    r.write("scripts/check-auth-invariant.mjs", "process.exit(check())\n");
    r.write("scripts/brand-check.mjs", "check()\n");
    r.write("scripts/vague-terms.test.mjs", "test('v', () => {});\n");
    r.write("AGENTS.project.md", "8. 密钥只放在服务端\n");
    r.write("src/AGENTS.md", "# src\n");
    r.write("CLAUDE.md", "@AGENTS.project.md\n");
    r.write("eslint-suppressions.json", "{}\n");
    r.commit("more base");
    const cases = [
      ["清空检查脚本", () => r.write("scripts/check-auth-invariant.mjs", ""), /改或删了检查脚本 scripts\/check-auth-invariant\.mjs/],
      ["删检查脚本", () => r.git("rm", "-q", "scripts/brand-check.mjs"), /改或删了检查脚本 scripts\/brand-check\.mjs/],
      ["删测试文件", () => r.git("rm", "-q", "scripts/vague-terms.test.mjs"), /删了测试文件 scripts\/vague-terms\.test\.mjs/],
      ["加 skip", () => r.write("scripts/a.test.mjs", "test.skip('a', () => {});\n"), /跳过或只跑部分测试/],
      ["加 eslint-disable", () => r.write("src/a.ts", "/* eslint-disable */\nexport const a = 1;\n"), /关掉 lint/],
      ["删红线", () => r.write("AGENTS.project.md", "\n"), /改了门槛文件 AGENTS\.project\.md/],
      ["改子目录 AGENTS.md", () => r.write("src/AGENTS.md", "# x\n"), /改了门槛文件 src\/AGENTS\.md/],
      ["改 CLAUDE.md", () => r.write("CLAUDE.md", "\n"), /改了门槛文件 CLAUDE\.md/],
      ["改 lint 抑制", () => r.write("eslint-suppressions.json", '{"x":1}\n'), /改或删了检查脚本 eslint-suppressions\.json/],
    ];
    cases.forEach(([name, change, why], i) => {
      const ref = `chore/weaken-${i}`;
      r.git("checkout", "-q", "-b", ref, "base"); change();
      const res = r.run(r.commit(name), ref, "类别：a");
      assert.equal(res.status, 0, `${name}：${res.stdout}`);
      assert.equal(category(res), "b", name);
      assert.match(res.stdout, why, name);
    });
    r.git("checkout", "-q", "-b", "chore/new-check", "base"); r.write("scripts/check-new.mjs", "check()\n");
    assert.equal(category(r.run(r.commit("new"), "chore/new-check", "类别：a")), "a", "新增检查脚本是收紧，仍是 a");
    r.git("checkout", "-q", "-b", "feat/4-agents", "base"); r.write("src/AGENTS.md", "# y\n");
    assert.equal(r.run(r.commit("t"), "feat/4-agents", "类别：票").status, 1, "票的 PR 不能改 AGENTS*.md");
  } finally { r.cleanup(); }
});

test("正文为空时标题不算类别：按 b", () => {
  const r = repo();
  try {
    r.branch("chore/empty"); r.write("docs/notes.md", "y\n");
    // 合并脚本写的文件：正文（空）一行，再是标题
    assert.equal(category(r.run(r.commit("e"), "chore/empty", "\n类别：a\n")), "b");
  } finally { r.cleanup(); }
});

// 后续加固（PR #68 两份复审的应改项）
test("非 ASCII 文件名：门槛文件、删测试文件照样认出来（git 默认转义中文路径）", () => {
  const r = repo();
  try {
    r.write("scripts/中文.test.mjs", "test('z', () => {});\n");
    r.commit("zh base");
    for (const f of [".github/workflows/中文.yml", ".claude/agents/中文.md"]) {
      const ref = `fix/21-${f.includes("workflows") ? "wf" : "agent"}`;
      r.branch(ref); r.write(f, "x\n");
      const res = r.run(r.commit(f), ref, "类别：票");
      assert.equal(res.status, 1, `${ref}：${res.stdout}`);
      assert.ok(res.stdout.includes(`改了定义门槛的文件 ${f}`), res.stdout);
    }
    r.branch("chore/zh-wf"); r.write(".github/workflows/中文.yml", "x\n");
    const wf = r.run(r.commit("wf"), "chore/zh-wf", "类别：a");
    assert.equal(category(wf), "b", wf.stdout);
    assert.ok(wf.stdout.includes("改了门槛文件 .github/workflows/中文.yml"), wf.stdout);
    r.branch("chore/zh-del"); r.git("rm", "-q", "scripts/中文.test.mjs");
    const del = r.run(r.commit("del"), "chore/zh-del", "类别：a");
    assert.equal(category(del), "b", del.stdout);
    assert.ok(del.stdout.includes("删了测试文件 scripts/中文.test.mjs"), del.stdout);
  } finally { r.cleanup(); }
});

test("观察者（obs/）判成 b 的直接拒绝，等产品负责人；判成 a 的照常", () => {
  const r = repo();
  try {
    r.branch("obs/2026-11-09-gate"); r.write("docs/standards/pipeline.md", "# 流水线 v3\n");
    const gate = r.commit("gate");
    for (const body of ["类别：a", "类别：b", ""]) {
      const res = r.run(gate, "obs/2026-11-09-gate", body);
      assert.equal(res.status, 1, body);
      assert.match(res.stdout, /观察者提的 b 类（.*改了门槛文件 docs\/standards\/pipeline\.md.*）：等产品负责人合并/, body);
      assert.equal(category(res), undefined, body);
    }
    assert.equal(category(r.run(gate, "chore/gate", "类别：a")), "b", "同一组改动主会话提，按 b 合并");
    r.branch("obs/2026-11-09-docs"); r.write("docs/quality/notes.md", "x\n");
    const docs = r.commit("docs");
    const a = r.run(docs, "obs/2026-11-09-docs", "类别：a");
    assert.equal(a.status, 0, a.stdout);
    assert.equal(category(a), "a");
    assert.equal(r.run(docs, "obs/2026-11-09-docs", "加一条").status, 1, "没写类别按 b，观察者的拒绝");
  } finally { r.cleanup(); }
});

test("改已有测试的断言、新增 skipIf / @ts-nocheck / @ts-ignore：不是票的 PR 写 a 也按 b", () => {
  const r = repo();
  try {
    r.write("scripts/v.test.mjs", "test('v', () => {\n  assert.equal(f(1), 2);\n  expect(g()).toBe(3);\n});\n");
    r.write("src/b.ts", "export const b = 1;\n");
    r.commit("tests base");
    const cases = [
      ["assert 换成空语句", () => r.write("scripts/v.test.mjs", "test('v', () => {\n  ;\n  expect(g()).toBe(3);\n});\n"), /改了已有测试 scripts\/v\.test\.mjs，删掉 1 行断言：assert\.equal/],
      ["删 expect", () => r.write("scripts/v.test.mjs", "test('v', () => {\n  assert.equal(f(1), 2);\n});\n"), /删掉 1 行断言：expect/],
      ["skipIf", () => r.write("scripts/a.test.mjs", "test.skipIf(true)('a', () => {});\n"), /跳过或只跑部分测试/],
      ["describe.skipIf", () => r.write("scripts/a.test.mjs", "describe.skipIf(ci)('a', () => {});\n"), /跳过或只跑部分测试/],
      ["@ts-nocheck", () => r.write("src/b.ts", "// @ts-nocheck\nexport const b = 1;\n"), /关掉类型检查/],
      ["@ts-ignore", () => r.write("src/b.ts", "// @ts-ignore\nexport const b: number = '1';\n"), /关掉类型检查/],
    ];
    cases.forEach(([name, change, why], i) => {
      const ref = `chore/assert-${i}`;
      r.git("checkout", "-q", "-b", ref, "base"); change();
      const res = r.run(r.commit(name), ref, "类别：a");
      assert.equal(res.status, 0, `${name}：${res.stdout}`);
      assert.equal(category(res), "b", name);
      assert.match(res.stdout, why, name);
    });
    r.git("checkout", "-q", "-b", "chore/add-case", "base");
    r.write("scripts/v.test.mjs", "test('v', () => {\n  assert.equal(f(1), 2);\n  expect(g()).toBe(3);\n});\ntest('w', () => { assert.ok(h()); });\n");
    assert.equal(category(r.run(r.commit("add"), "chore/add-case", "类别：a")), "a", "只新增用例仍是 a");
    r.git("checkout", "-q", "-b", "feat/6-ts", "base"); r.write("src/b.ts", "// @ts-ignore\nexport const b = 1;\n");
    assert.match(r.run(r.commit("t"), "feat/6-ts", "类别：票").stdout, /关掉类型检查/, "票的 PR 也不能关类型检查");
  } finally { r.cleanup(); }
});

test("改 docs/standards/observer.md 的 PR 等产品负责人（§4 只能由产品负责人改）", () => {
  const r = repo();
  try {
    r.write("docs/standards/observer.md", "# 观察者\n## 4. 权限\n");
    r.commit("observer base");
    for (const [ref, body] of [["chore/obs-perm", "类别：a"], ["chore/obs-perm-b", "类别：b"], ["obs/2026-11-09-perm", "类别：a"]]) {
      r.git("checkout", "-q", "-b", ref, "base"); r.write("docs/standards/observer.md", "# 观察者\n## 4. 权限：都能做\n");
      const res = r.run(r.commit(ref), ref, body);
      assert.equal(res.status, 1, ref);
      assert.match(res.stdout, /改了 docs\/standards\/observer\.md：§4（观察者的权限）只能由产品负责人改/, ref);
      assert.equal(category(res), undefined, ref);
    }
  } finally { r.cleanup(); }
});
