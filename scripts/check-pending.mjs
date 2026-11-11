// Lists every line in docs/ that carries a pending marker such as 〔<topic>：待定〕 (see pending-markers.mjs).
// It only reports and always exits 0: a marker is a legitimate state. Tickets that wait for a topic to be
// decided (e.g. #89 for "Resend 留存") require that this list no longer contains that topic.
// Review reports are records and quote markers; they are left out.
//
// Usage: node scripts/check-pending.mjs [topic]
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { findPending } from "./pending-markers.mjs";

const SKIP_DIRS = ["docs/uiue/reviews/", "docs/prd/reviews/", "docs/delivery/reviews/"];
const topic = process.argv[2];

const files = execFileSync("git", ["ls-files", "docs"], { encoding: "utf8" })
  .split("\n")
  .filter((f) => f.endsWith(".md") && !SKIP_DIRS.some((d) => f.startsWith(d)));

let count = 0;
for (const file of files) {
  for (const hit of findPending(readFileSync(file, "utf8"))) {
    if (topic && hit.topic !== topic) continue;
    console.log(`${file}:${hit.line}: ${hit.topic}`);
    count++;
  }
}
console.log(`带「待定」标记的行：${count} 处${topic ? `（只看「${topic}」）` : ""}，查了 ${files.length} 个文件。`);
