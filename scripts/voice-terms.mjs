// Finds spoken-language markers and registered transcription errors in formal text, and checks that
// owner input from timeline.md No. 84 on is traced with its 「举一反三」.
// Lists live in docs/GLOSSARY.md (「口语和转写错误」): ```spoken-markers, ```transcription-errors, ```allowed-phrases.

export function parseFence(markdown, name) {
  const block = markdown.match(new RegExp("```" + name + "\\n([\\s\\S]*?)```"));
  if (!block) throw new Error(`docs/GLOSSARY.md has no \`\`\`${name} block`);
  return block[1]
    .split("\n")
    .map((t) => t.trim())
    .filter(Boolean);
}

const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
// Characters that end a standalone interjection: start or end of line, spaces and punctuation.
const EDGE = "\\s，。！？、；：,.!?;:…—「」“”\"'（）()";

// 「[啊]」 in the list means standalone only (「啊，」 at a pause, not 「真好啊」); ASCII words match whole words only.
function compile(entry) {
  const standalone = /^\[.+\]$/.test(entry);
  const word = standalone ? entry.slice(1, -1) : entry;
  const ascii = /^[\x20-\x7e]+$/.test(word);
  let source = escape(word);
  if (standalone) source = `(?<=^|[${EDGE}])${source}(?=[，。！？、,.!?…])`;
  else if (ascii) source = `(?<![A-Za-z])${source}(?![A-Za-z])`;
  return { word, re: new RegExp(source, ascii ? "i" : "") };
}

const QUOTES = [["「", "」"], ["“", "”"], ["`", "`"], ['"', '"']];
const FENCE = /^\s{0,3}(`{3,}|~{3,})/;

/**
 * Returns [{ line, word, kind }], kind: "spoken", "transcription" or "fence" (a code fence that never closes).
 * A spoken marker quoted on its own (「嗯」, “对吧”, `um`) is being named, not used; transcription errors count
 * inside quotes too (naming a wrong spelling goes through allowed phrases, e.g. 「（不是阀值）」).
 * Fences close by CommonMark rules (same character, at least as long). With skipFences (the glossary only,
 * where the lists live) fenced lines are not scanned; everywhere else they are.
 */
export function findVoiceHits(text, { spoken, transcription, allowed = [] }, { markdown = true, skipFences = false } = {}) {
  const terms = [...spoken.map((e) => ({ ...compile(e), kind: "spoken" })), ...transcription.map((e) => ({ ...compile(e), kind: "transcription" }))];
  const hits = [];
  let open = null;
  let openLine = 0;
  text.split("\n").forEach((raw, i) => {
    if (markdown) {
      const f = raw.match(FENCE);
      if (f && !open) {
        open = f[1];
        openLine = i + 1;
        return;
      }
      if (f && open && f[1][0] === open[0] && f[1].length >= open.length && raw.trim() === f[1]) {
        open = null;
        return;
      }
      if (open && skipFences) return;
    }
    let line = raw;
    for (const a of allowed) line = line.split(a).join("");
    for (const { word, kind } of terms) {
      if (kind !== "spoken") continue;
      for (const [o, c] of QUOTES) line = line.split(o + word + c).join("");
    }
    for (const { word, kind, re } of terms) if (re.test(line)) hits.push({ line: i + 1, word, kind });
  });
  if (open) hits.push({ line: openLine, word: open, kind: "fence" });
  return hits;
}

const cells = (line) => line.trim().replace(/^\|/, "").replace(/(?<!\\)\|$/, "").split(/(?<!\\)\|/).map((s) => s.trim());
const EMPTY = new Set(["无", "-", "—", "同上", "见上", "略", "n/a"]);
const MIN_SIBLINGS = 10;

/**
 * Owner input from `from` on (timeline.md 「## N」) must have a trace.md row whose last column 「举一反三」 says
 * which class of problem it is, where the siblings are and what changed: at least 10 characters once punctuation and
 * spaces are removed; 「无」「-」「同上」 count as empty. Returns [{ n, why }].
 */
export function traceGaps(timeline, trace, from = 84) {
  const rows = new Map();
  for (const line of trace.split("\n")) {
    const c = cells(line);
    if (/^\d+$/.test(c[0] ?? "")) rows.set(Number(c[0]), c);
  }
  const wanted = new Set([...timeline.matchAll(/^## (\d+)\s*$/gm)].map((m) => Number(m[1])).filter((n) => n >= from));
  for (const n of rows.keys()) if (n >= from) wanted.add(n);
  const gaps = [];
  // 除第一行的总标题外，timeline.md 的每个标题都只能写成「## N」（和上面取编号的写法一致）：
  // 换级别、多空格、缩进、编号后加字、全角数字都会绕过取编号，一律报错
  const lines = timeline.split("\n");
  const first = lines.findIndex((l) => l.trim() !== "");
  lines.forEach((line, i) => {
    if (i === first || !/^[ \t]{0,3}#{1,6}([ \t]|$|\d)/.test(line) || /^## \d+\s*$/.test(line)) return;
    const n = Number((line.match(/\d+/) ?? [NaN])[0]);
    gaps.push({ n, why: `timeline.md 第 ${i + 1} 行的标题要写成「## 编号」，现在是「${line.trim()}」` });
  });
  for (const n of [...wanted].sort((a, b) => a - b)) {
    const c = rows.get(n);
    if (!c) {
      gaps.push({ n, why: "timeline.md 有这一条，trace.md 没有这一行" });
      continue;
    }
    const cell = (c[6] ?? "").trim();
    const bare = cell.replace(/[\s\p{P}\p{S}]/gu, "");
    if (EMPTY.has(cell.toLowerCase()) || bare.length < MIN_SIBLINGS) gaps.push({ n, why: `「举一反三」一栏是空的或不到 ${MIN_SIBLINGS} 个字` });
  }
  return gaps;
}
