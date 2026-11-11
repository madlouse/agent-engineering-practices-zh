// Runs the cross-repo issue number check (scripts/cross-repo-refs.mjs) over the bodies of this repository's open issues.
// check:terms only reads files; issue bodies live on GitHub, so this is a separate, repeatable command.
// Only issues opened by the repository owner are checked (author_association is OWNER).
// Usage: node scripts/check-issue-refs.mjs [owner/repo]   (needs the gh CLI; read-only)
import { execFileSync } from "node:child_process";
import { findSharedPrefixRefsInIssues } from "./cross-repo-refs.mjs";

const repo = process.argv[2] ?? "madlouse/velicoach";
const raw = execFileSync("gh", ["api", "--paginate", `repos/${repo}/issues?state=open&per_page=100`, "--jq", ".[] | {number, body, author_association, pull_request}"], {
  encoding: "utf8",
  maxBuffer: 64 * 1024 * 1024,
});
const issues = raw
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line));

const { checked, hits } = findSharedPrefixRefsInIssues(issues);
for (const { number, line, ref } of hits) console.log(`#${number}:${line}: 「${ref}」`);
if (hits.length) {
  console.error(`\n${hits.length} 处跨仓库的票号共用了一个前缀：每个号都写全，跨仓库的号排在本仓库的号后面。`);
  process.exit(1);
}
console.log(`票正文的跨仓库票号检查通过：${checked} 张仓库所有者开的、开着的票。`);
