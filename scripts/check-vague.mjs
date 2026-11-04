// Fails when a checklist item or an acceptance column uses a quality word without its definition
// (docs/standards/quality-terms.md) or uses a filler word that cannot be judged.
// Usage: node scripts/check-vague.mjs [file ...]   (no files: the repo's docs, agents and site skills)
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { parseBlock, findViolations } from "./vague-terms.mjs";

const defs = readFileSync("docs/standards/quality-terms.md", "utf8");
const terms = { vague: parseBlock(defs, "vague-terms"), filler: parseBlock(defs, "filler-terms") };

// Verbatim user input and logs keep the original wording on purpose.
const skip = new Set([
  "docs/standards/quality-terms.md",
  "docs/requirements/timeline.md",
  "docs/requirements/summary.md",
  "docs/requirements/trace.md",
  "docs/uiue/decisions.md",
  "docs/delivery/lessons.md",
]);

const files = process.argv.slice(2).length
  ? process.argv.slice(2)
  : execFileSync("git", ["ls-files", "docs", ".claude/agents", ".grok/skills/velicoach-content", ".grok/skills/velicoach-layout", ".grok/skills/agent-team-setup", "AGENTS.project.md"], { encoding: "utf8" })
      .split("\n")
      .filter((f) => f.endsWith(".md") && !skip.has(f));

let hits = 0;
for (const file of files) {
  for (const v of findViolations(readFileSync(file, "utf8"), terms)) {
    const why = v.kind === "filler" ? "判不了对错的虚词，换成具体的数、动作或产出" : "质量词没有定义，链到 docs/standards/quality-terms.md 或换成那里的规则";
    console.log(`${file}:${v.line}: 「${v.word}」 ${why}`);
    hits++;
  }
}
if (hits) {
  console.error(`\n${hits} 处验收里的词判不了对错。规则见 docs/standards/quality-terms.md。`);
  process.exit(1);
}
console.log(`质量词检查通过：${files.length} 个文件，${terms.vague.length} 个质量词，${terms.filler.length} 个虚词。`);
