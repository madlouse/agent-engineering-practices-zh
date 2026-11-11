// Fails when docs, skills or site copy use a term listed under 「不再用的说法」 in docs/GLOSSARY.md.
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { parseFence } from "./voice-terms.mjs";
import { findSharedPrefixRefs } from "./cross-repo-refs.mjs";

const glossary = readFileSync("docs/GLOSSARY.md", "utf8");
// Transcription errors and allowed phrases are lists shared with check-voice (GLOSSARY 「口语和转写错误」).
const terms = [...parseFence(glossary, "stale-terms"), ...parseFence(glossary, "transcription-errors")];
const allowed = parseFence(glossary, "allowed-phrases");

// History files keep old wording on purpose: verbatim user input, the decision log and the glossary itself.
const skip = [
  "docs/GLOSSARY.md",
  "docs/requirements/timeline.md",
  "docs/requirements/summary.md",
  "docs/requirements/trace.md",
  "docs/uiue/decisions.md",
  "docs/issues/README.md",
];
// Review reports and research notes quote the wording they found; they are records, not live copy.
const skipDirs = ["docs/uiue/reviews/", "docs/prd/reviews/", "docs/delivery/reviews/", "docs/uiue/research/"];

const files = execFileSync("git", ["ls-files", "docs", "src", "AGENTS.project.md", "README.md", ".grok/skills/velicoach-content", ".grok/skills/velicoach-layout", ".grok/skills/article-pipeline", ".grok/skills/article-fidelity", ".grok/skills/article-zh-style", ".grok/skills/article-feynman", ".grok/skills/article-visual", "public/favicon.svg"], { encoding: "utf8" })
  .split("\n")
  .filter((f) => /\.(md|ts|tsx|json|svg)$/.test(f) && !skip.includes(f) && !skipDirs.some((d) => f.startsWith(d)));

// Cross-repo issue numbers are checked in every tracked doc, including the decision logs the stale-term check skips:
// those are live documents that cite issues. Only verbatim user input and review reports are left out
// (review reports quote what they found and use rubric ids like 「A#17、#27」).
const refSkip = ["docs/requirements/timeline.md"];
const refFiles = execFileSync("git", ["ls-files", "docs", "AGENTS.project.md", "README.md", ".claude/agents", ".grok/skills/velicoach-content", ".grok/skills/velicoach-layout", ".grok/skills/agent-team-setup", ".grok/skills/article-pipeline"], { encoding: "utf8" })
  .split("\n")
  .filter((f) => f.endsWith(".md") && !refSkip.includes(f) && !skipDirs.some((d) => f.startsWith(d)));

let hits = 0;
let refHits = 0;
for (const file of refFiles) {
  readFileSync(file, "utf8")
    .split("\n")
    .forEach((line, i) => {
      for (const ref of findSharedPrefixRefs(line)) {
        console.log(`${file}:${i + 1}: 「${ref}」 跨仓库的票号共用了一个前缀：每个号都写全，跨仓库的号排在本仓库的号后面`);
        refHits++;
      }
    });
}
for (const file of files) {
  const lines = readFileSync(file, "utf8").split("\n");
  lines.forEach((line, i) => {
    let text = line;
    for (const a of allowed) text = text.split(a).join("");
    for (const term of terms) {
      if (text.includes(term)) {
        console.log(`${file}:${i + 1}: 「${term}」 ${line.trim().slice(0, 80)}`);
        hits++;
      }
    }
  });
}
if (hits) {
  console.error(`\n${hits} 处用了不再用的说法，改法见 docs/GLOSSARY.md「不再用的说法」。`);
  process.exit(1);
}
if (refHits) {
  console.error(`\n${refHits} 处跨仓库的票号没写全：写成「thin-muscle-coach#185、thin-muscle-coach#101」，一个前缀不跨顿号共用。`);
  process.exit(1);
}
console.log(`术语检查通过：${files.length} 个文件，${terms.length} 个旧说法；跨仓库票号查了 ${refFiles.length} 个文件。`);
