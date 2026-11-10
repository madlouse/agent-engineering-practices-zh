// Finds spoken-language markers and registered transcription errors in formal text.
// Lists live in docs/GLOSSARY.md (「口语和转写错误」): ```spoken-markers, ```voice-allowed, ```transcription-errors.

export function parseFence(markdown, name) {
  const block = markdown.match(new RegExp("```" + name + "\\n([\\s\\S]*?)```"));
  if (!block) throw new Error(`docs/GLOSSARY.md has no \`\`\`${name} block`);
  return block[1]
    .split("\n")
    .map((t) => t.trim())
    .filter(Boolean);
}

const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
// ASCII words match whole words only, so 「um」 does not hit 「umbrella」; Chinese has no word breaks.
const pattern = (term) => (/^[\x20-\x7e]+$/.test(term) ? new RegExp(`(?<![A-Za-z])${escape(term)}(?![A-Za-z])`, "i") : new RegExp(escape(term)));

/**
 * Returns [{ line, word, kind }] where kind is "spoken" or "transcription".
 * A marker quoted on its own (「嗯」, “对吧”, `um`) is being named, not used. Allowed phrases (「也就是说」) are removed first.
 * In markdown, fenced code blocks are skipped: the lists themselves live in fences.
 */
export function findVoiceHits(text, { spoken, transcription, allowed = [] }, { markdown = true } = {}) {
  const terms = [...spoken.map((w) => [w, "spoken"]), ...transcription.map((w) => [w, "transcription"])].map(([w, kind]) => ({ w, kind, re: pattern(w) }));
  const hits = [];
  let fenced = false;
  text.split("\n").forEach((raw, i) => {
    if (markdown && /^\s*```/.test(raw)) {
      fenced = !fenced;
      return;
    }
    if (fenced) return;
    let line = raw;
    for (const a of allowed) line = line.split(a).join("");
    for (const { w } of terms) for (const [open, close] of [["「", "」"], ["“", "”"], ["`", "`"], ['"', '"']]) line = line.split(open + w + close).join("");
    for (const { w, kind, re } of terms) if (re.test(line)) hits.push({ line: i + 1, word: w, kind });
  });
  return hits;
}

/**
 * trace.md rows numbered `from` and later must fill the last column 「举一反三」 (docs/requirements/README.md).
 * Returns the row numbers that leave it empty or missing.
 */
export function traceRowsMissingSiblings(markdown, from = 84) {
  const missing = [];
  for (const line of markdown.split("\n")) {
    const c = line.trim().replace(/^\|/, "").replace(/(?<!\\)\|$/, "").split(/(?<!\\)\|/).map((s) => s.trim());
    const n = Number(c[0]);
    if (!/^\d+$/.test(c[0] ?? "") || n < from) continue;
    if (c.length < 7 || !c[6]) missing.push(n);
  }
  return missing;
}
