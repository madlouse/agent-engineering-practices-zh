// Compares docs/delivery/gate-3b-split.md (§1 counts, §3 ticket tables, §4 dependency diagram) with GitHub:
// titles, labels and native dependencies of every open issue. Dependencies are fetched page by page:
// the endpoint returns 30 per page by default, and a truncated list is how #66 once lost four blockers.
//
// Usage: node scripts/check-ticket-table.mjs [--write] [owner/repo]
//   without --write: lists every difference and exits 1 if there is any
//   with --write:    rewrites the generated parts of the doc from GitHub, then checks again
// Needs the gh CLI; read-only on GitHub. Not part of `npm test` (it needs the network).
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import { isOwnerIssue } from "./cross-repo-refs.mjs";
import { REPO, compare, paginate, regenerate } from "./ticket-table.mjs";

const DOC = "docs/delivery/gate-3b-split.md";
const PER_PAGE = 100;
const MAX_PAGES = 20;
const GH_TIMEOUT_MS = 30_000;
const WRITABLE_REPO = `madlouse/${REPO}`;
const args = process.argv.slice(2);
const write = args.includes("--write");
const repo = args.find((a) => !a.startsWith("--")) ?? WRITABLE_REPO;
if (write && repo !== WRITABLE_REPO) {
  console.error(`--write 只对 ${WRITABLE_REPO} 用：别的仓库的数据不能写进本仓库的文档。`);
  process.exit(2);
}

function gh(path, page) {
  const sep = path.includes("?") ? "&" : "?";
  const out = execFileSync("gh", ["api", `${path}${sep}per_page=${PER_PAGE}&page=${page}`], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024, timeout: GH_TIMEOUT_MS });
  return JSON.parse(out);
}

// Only issues opened by the repository owner: the repo is public, and a stranger's issue must not reach the doc or fail the check.
const open = (await paginate((page) => gh(`repos/${repo}/issues?state=open`, page), PER_PAGE, MAX_PAGES)).filter(isOwnerIssue);
const issues = new Map();
for (const issue of open) {
  const blockers = await paginate((page) => gh(`repos/${repo}/issues/${issue.number}/dependencies/blocked_by`, page), PER_PAGE, MAX_PAGES);
  issues.set(issue.number, {
    title: issue.title,
    labels: issue.labels.map((l) => l.name),
    blockedBy: blockers.map((b) => ({ repo: b.repository_url.split("/").pop(), number: b.number, state: b.state })),
  });
}

let doc = readFileSync(DOC, "utf8");
if (write) {
  doc = regenerate(doc, issues);
  writeFileSync(DOC, doc);
}
const problems = compare(doc, issues);
for (const p of problems) console.log(p);
if (problems.length) {
  console.error(`\n${DOC} 和 GitHub 有 ${problems.length} 处不一致。${write ? "重新生成以后还剩这些，要手工改。" : "跑 `npm run check:ticket-table -- --write` 重新生成 §3、§4 和 §1 的数字。"}`);
  process.exit(1);
}
console.log(`票表检查通过：${issues.size} 张仓库所有者开的、开着的票，§3 的表、§4 的图、§1 的数字和 GitHub 一致，原生依赖没有环。`);
