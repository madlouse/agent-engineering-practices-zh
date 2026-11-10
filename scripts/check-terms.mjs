// Fails when docs, skills or site copy use a term listed under 「不再用的说法」 in docs/GLOSSARY.md.
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const glossary = readFileSync("docs/GLOSSARY.md", "utf8");
const block = glossary.match(/```stale-terms\n([\s\S]*?)```/);
if (!block) {
  console.error("docs/GLOSSARY.md has no ```stale-terms block");
  process.exit(1);
}
const terms = block[1].split("\n").map((t) => t.trim()).filter(Boolean);

// History files keep old wording on purpose: verbatim user input, the decision log and the glossary itself.
const skip = [
  "docs/GLOSSARY.md",
  "docs/requirements/timeline.md",
  "docs/requirements/summary.md",
  "docs/requirements/trace.md",
  "docs/uiue/decisions.md",
  "docs/issues/README.md",
  "docs/uiue/identity.md",
];
// Allowed phrasings that name the past on purpose.
const allowed = ["原同席博客", "原来的同席博客", "搏击等对抗性运动", "学习路径步骤", "（不是阀值）"];

const files = execFileSync("git", ["ls-files", "docs", "src", "AGENTS.project.md", "README.md", ".grok/skills/velicoach-content", ".grok/skills/velicoach-layout"], { encoding: "utf8" })
  .split("\n")
  .filter((f) => /\.(md|ts|tsx|json)$/.test(f) && !skip.includes(f));

let hits = 0;
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
console.log(`术语检查通过：${files.length} 个文件，${terms.length} 个旧说法。`);
