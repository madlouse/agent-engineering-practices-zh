import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { docsOnly, decide, splitPaths } from "./preview-skip.mjs";

test("只改文档算文档", () => {
  assert.equal(docsOnly(["docs/prd/velicoach.md", "docs/uiue/prototypes/v1.1/boards/Main.dc.html", ".grok/skills/velicoach-layout/SKILL.md", "README.md", "AGENTS.project.md"]), true);
});
test("碰到站点、脚本、配置就不算", () => {
  for (const f of ["src/routes/index.tsx", "scripts/check-terms.mjs", "package.json", "vercel.json", "public/favicon.svg", "server/api.ts", "migrations/site/001.sql", "docs.md/x.ts", ".grok/app-env.json", ".claude/settings.json"]) {
    assert.equal(docsOnly(["docs/a.md", f]), false, f);
  }
});
test("子目录里的 md 不算根目录的说明", () => assert.equal(docsOnly(["src/content/post.md"]), false));
test("没有改动不算", () => {
  assert.equal(docsOnly([]), false);
  assert.equal(docsOnly(["", "  "]), false);
});
test("集成和生产分支总是构建", () => {
  assert.equal(decide({ branch: "feature/v1", previousSha: "abc1234", files: ["docs/a.md"] }).skip, false);
  assert.equal(decide({ branch: "site", previousSha: "abc1234", files: ["docs/a.md"] }).skip, false);
});
test("没有上次部署或找不到那个提交时构建", () => {
  assert.equal(decide({ branch: "chore/x", previousSha: "", files: [] }).skip, false);
  assert.equal(decide({ branch: "chore/x", previousSha: "abc1234", files: null }).skip, false);
});
test("PR 分支只改文档时跳过，改了代码就构建", () => {
  assert.equal(decide({ branch: "chore/x", previousSha: "abc1234", files: ["docs/a.md"] }).skip, true);
  assert.equal(decide({ branch: "feat/22-tokens", previousSha: "abc1234", files: ["docs/a.md", "src/x.ts"] }).skip, false);
});
test("eslint 会查的脚本要构建，画板目录 eslint 不查", () => {
  assert.equal(docsOnly([".grok/skills/design-bar/scripts/liquid-glass.js"]), false);
  assert.equal(docsOnly(["docs/tools/x.mjs"]), false);
  assert.equal(docsOnly(["docs/uiue/prototypes/v1.1/src/pages/article.js"]), true);
});
test("中文文件名和改名都按原路径判", (t) => {
  const dir = mkdtempSync(join(tmpdir(), "preview-skip-"));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const git = (...a) => execFileSync("git", ["-C", dir, ...a], { encoding: "utf8" });
  git("init", "-q");
  git("config", "user.email", "t@t");
  git("config", "user.name", "t");
  mkdirSync(join(dir, "src"));
  mkdirSync(join(dir, "docs"));
  writeFileSync(join(dir, "src", "a.ts"), "export const a = 1;\n".repeat(20));
  writeFileSync(join(dir, "docs", "说明.md"), "一\n");
  git("add", "-A");
  git("commit", "-qm", "base");
  writeFileSync(join(dir, "docs", "说明.md"), "二\n");
  git("commit", "-qam", "doc");
  assert.equal(docsOnly(splitPaths(git("diff", "-z", "--no-renames", "--name-only", "HEAD~1", "HEAD"))), true);
  git("mv", "src/a.ts", "docs/a.ts.md");
  git("commit", "-qm", "move");
  assert.deepEqual(splitPaths(git("diff", "-z", "--no-renames", "--name-only", "HEAD~1", "HEAD")).filter(Boolean).sort(), ["docs/a.ts.md", "src/a.ts"]);
  assert.equal(docsOnly(splitPaths(git("diff", "-z", "--no-renames", "--name-only", "HEAD~1", "HEAD"))), false);
});
