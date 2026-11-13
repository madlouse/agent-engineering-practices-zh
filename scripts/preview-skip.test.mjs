import { test } from "node:test";
import assert from "node:assert/strict";
import { docsOnly, decide } from "./preview-skip.mjs";

test("只改文档算文档", () => {
  assert.equal(docsOnly(["docs/prd/velicoach.md", "docs/uiue/prototypes/v1.1/boards/Main.dc.html", ".grok/skills/velicoach-layout/SKILL.md", "README.md", "AGENTS.project.md"]), true);
});
test("碰到站点、脚本、配置就不算", () => {
  for (const f of ["src/routes/index.tsx", "scripts/check-terms.mjs", "package.json", "vercel.json", "public/favicon.svg", "server/api.ts", "migrations/site/001.sql", "docs.md/x.ts"]) {
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
