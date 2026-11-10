// Fails when formal text uses spoken-language markers or a registered transcription error, when a markdown code fence
// never closes, or when owner input from timeline.md No. 84 on has no trace.md row with its 「举一反三」
// (AGENTS.project.md 「不能越过的线」第 1 条). Lists live in docs/GLOSSARY.md 「口语和转写错误」;
// check-terms reads the same transcription and allowed lists.
// Usage: node scripts/check-voice.mjs [file ...]   (no files: the same scope as check-terms, plus agents and explainer narration)
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { parseFence, findVoiceHits, traceGaps } from "./voice-terms.mjs";

const glossary = readFileSync("docs/GLOSSARY.md", "utf8");
const lists = {
  spoken: parseFence(glossary, "spoken-markers"),
  allowed: parseFence(glossary, "allowed-phrases"),
  transcription: parseFence(glossary, "transcription-errors"),
};

// Verbatim user input stays as spoken; review reports and research notes quote what they found.
const skip = new Set(["docs/requirements/timeline.md"]);
const skipDirs = ["docs/uiue/reviews/", "docs/prd/reviews/", "docs/delivery/reviews/", "docs/uiue/research/", "docs/requirements/attachments/"];
// Records that name old wrong names on purpose: spoken markers are still checked there, transcription errors are not.
// Same list as check-terms skips.
const history = new Set(["docs/GLOSSARY.md", "docs/requirements/summary.md", "docs/requirements/trace.md", "docs/uiue/decisions.md", "docs/issues/README.md"]);
const scope = [
  "docs", "src", "AGENTS.project.md", "README.md", ".claude/agents", "public/explainers",
  ".grok/skills/velicoach-content", ".grok/skills/velicoach-layout", ".grok/skills/agent-team-setup",
  ".grok/skills/article-pipeline", ".grok/skills/article-fidelity", ".grok/skills/article-zh-style", ".grok/skills/article-feynman", ".grok/skills/article-visual",
];

const args = process.argv.slice(2);
const files = args.length
  ? args
  : execFileSync("git", ["-c", "core.quotepath=false", "ls-files", ...scope], { encoding: "utf8" })
      .split("\n")
      .filter((f) => /\.(md|ts|tsx|json)$/.test(f) && !skip.has(f) && !skipDirs.some((d) => f.startsWith(d)));

const why = {
  spoken: "口语标记：改成书面表达",
  transcription: "登记过的转写错误：按术语表改正（点名错字的说明写进 allowed-phrases）",
  fence: "代码围栏没有收尾：后面的内容都会被当成代码",
};
let hits = 0;
for (const file of files) {
  const use = history.has(file) ? { ...lists, transcription: [] } : lists;
  const options = { markdown: file.endsWith(".md"), skipFences: file === "docs/GLOSSARY.md" };
  for (const h of findVoiceHits(readFileSync(file, "utf8"), use, options)) {
    console.log(`${file}:${h.line}: 「${h.word}」 ${why[h.kind]}`);
    hits++;
  }
}
if (!args.length) {
  for (const { n, why: gap } of traceGaps(readFileSync("docs/requirements/timeline.md", "utf8"), readFileSync("docs/requirements/trace.md", "utf8"))) {
    console.log(`docs/requirements/trace.md: 第 ${n} 条：${gap}。写这条输入代表哪一类问题、同类位置在哪、各改了什么（docs/requirements/README.md）`);
    hits++;
  }
}
if (hits) {
  console.error(`\n${hits} 处问题。原话只进 docs/requirements/timeline.md；清单见 docs/GLOSSARY.md「口语和转写错误」。`);
  process.exit(1);
}
console.log(`口语检查通过：${files.length} 个文件，${lists.spoken.length} 个口语标记，${lists.transcription.length} 个转写错误。`);
