// Fails when formal text uses spoken-language markers or a registered transcription error
// (AGENTS.project.md 「不能越过的线」第 1 条：用户原话只进 timeline.md，正式文档用书面表达和标准术语).
// Lists live in docs/GLOSSARY.md 「口语和转写错误」; check-terms reads the same transcription list.
// Usage: node scripts/check-voice.mjs [file ...]   (no files: every formal doc, skill and article)
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { parseFence, findVoiceHits, traceRowsMissingSiblings } from "./voice-terms.mjs";

const glossary = readFileSync("docs/GLOSSARY.md", "utf8");
const lists = {
  spoken: parseFence(glossary, "spoken-markers"),
  allowed: parseFence(glossary, "voice-allowed"),
  transcription: parseFence(glossary, "transcription-errors"),
};

// Verbatim user input stays as spoken; review reports and research notes quote what they found.
const skip = new Set(["docs/requirements/timeline.md"]);
// Records that name old wrong names on purpose (the glossary's own tables, the trace's history rows, the decision log):
// spoken markers are still checked there, transcription errors are not. Same list as check-terms skips.
const history = new Set(["docs/GLOSSARY.md", "docs/requirements/summary.md", "docs/requirements/trace.md", "docs/uiue/decisions.md", "docs/issues/README.md"]);
const skipDirs = ["docs/uiue/reviews/", "docs/prd/reviews/", "docs/delivery/reviews/", "docs/uiue/research/", "docs/requirements/attachments/"];
const scope = [
  "docs", "src/content", "AGENTS.project.md", "README.md", ".claude/agents",
  ".grok/skills/velicoach-content", ".grok/skills/velicoach-layout", ".grok/skills/agent-team-setup",
  ".grok/skills/article-pipeline", ".grok/skills/article-fidelity", ".grok/skills/article-zh-style", ".grok/skills/article-feynman", ".grok/skills/article-visual",
];

const files = process.argv.slice(2).length
  ? process.argv.slice(2)
  : execFileSync("git", ["-c", "core.quotepath=false", "ls-files", ...scope], { encoding: "utf8" })
      .split("\n")
      .filter((f) => /\.(md|ts|tsx)$/.test(f) && !skip.has(f) && !skipDirs.some((d) => f.startsWith(d)));

let hits = 0;
for (const file of files) {
  const use = history.has(file) ? { ...lists, transcription: [] } : lists;
  for (const h of findVoiceHits(readFileSync(file, "utf8"), use, { markdown: file.endsWith(".md") })) {
    const why = h.kind === "spoken" ? "口语标记：改成书面表达" : "登记过的转写错误：按术语表改正";
    console.log(`${file}:${h.line}: 「${h.word}」 ${why}`);
    hits++;
  }
}
if (!process.argv.slice(2).length) {
  for (const n of traceRowsMissingSiblings(readFileSync("docs/requirements/trace.md", "utf8"))) {
    console.log(`docs/requirements/trace.md: 第 ${n} 条「举一反三」一栏是空的：写这条输入代表哪一类问题、同类位置在哪、各改了什么`);
    hits++;
  }
}
if (hits) {
  console.error(`\n${hits} 处正式文字里有口语或转写错误。原话只进 docs/requirements/timeline.md；清单见 docs/GLOSSARY.md「口语和转写错误」。`);
  process.exit(1);
}
console.log(`口语检查通过：${files.length} 个文件，${lists.spoken.length} 个口语标记，${lists.transcription.length} 个转写错误。`);
