// Runs the cross-repo issue number check (scripts/cross-repo-refs.mjs) over the bodies of this repository's open issues.
// check:terms only reads files; issue bodies live on GitHub, so this is a separate, repeatable command.
// Usage: node scripts/check-issue-refs.mjs [owner/repo]   (needs the gh CLI; read-only)
import { execFileSync } from "node:child_process";
import { findSharedPrefixRefs } from "./cross-repo-refs.mjs";

const repo = process.argv[2] ?? "madlouse/velicoach";
const raw = execFileSync("gh", ["api", "--paginate", `repos/${repo}/issues?state=open&per_page=100`, "--jq", ".[] | select(.pull_request | not) | {number, body}"], {
  encoding: "utf8",
  maxBuffer: 64 * 1024 * 1024,
});
const issues = raw
  .split("\n")
  .filter(Boolean)
  .map((line) => JSON.parse(line));

let hits = 0;
for (const { number, body } of issues) {
  (body ?? "").split("\n").forEach((line, i) => {
    for (const ref of findSharedPrefixRefs(line)) {
      console.log(`#${number}:${i + 1}: 「${ref}」`);
      hits++;
    }
  });
}
if (hits) {
  console.error(`\n${hits} 处跨仓库的票号共用了一个前缀：每个号都写全，跨仓库的号排在本仓库的号后面。`);
  process.exit(1);
}
console.log(`票正文的跨仓库票号检查通过：${issues.length} 张开着的票。`);
