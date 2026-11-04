// Finds quality words with no definition, and filler words, in places that decide pass or fail:
// checklist items, list items under an acceptance heading, and acceptance columns of tables.
// Words, rule ids, dimensions and allowed phrases live in docs/standards/quality-terms.md.

export function parseBlock(markdown, name) {
  const block = markdown.match(new RegExp("```" + name + "\\n([\\s\\S]*?)```"));
  if (!block) throw new Error(`docs/standards/quality-terms.md has no \`\`\`${name} block`);
  return block[1]
    .split("\n")
    .map((t) => t.trim())
    .filter(Boolean);
}

export function parseRuleIds(markdown) {
  return new Set([...markdown.matchAll(/^\| ([A-Z]\d+) /gm)].map((m) => m[1]));
}

// Reads the dimension table: the words a dimension covers and the letter of its rules (「U1–U12」 → U).
export function parseDimensions(markdown) {
  const map = new Map();
  for (const line of markdown.split("\n")) {
    const c = cells(line);
    const letter = c.at(-1)?.trim().match(/^([A-Z])\d+–\1?\d+$/)?.[1];
    if (!letter || c.length < 3) continue;
    for (const word of c.at(-2).split("、")) map.set(word.trim(), letter);
  }
  return map;
}

const ACCEPTANCE = /验收|出口|退出条件|判定|怎么判|到位|通过标准|完成的?标准|交付物|怎么查|门槛|acceptance|criteria|definition of done/i;
const RULE_REF = /quality-terms(?:\.md)?`?\s*(?:#|§)?\s*([A-Z]\d+)/g;
const COMBO_REF = /quality-terms(?:\.md)?`?\s*§\s*2\.2/;

// Splits a table row on unescaped pipes, so "中文 \| EN" stays one cell.
function cells(line) {
  return line.trim().replace(/^\|/, "").replace(/(?<!\\)\|$/, "").split(/(?<!\\)\|/);
}
// Quoted filler words are being named, not used: 「待定」, “TBD”, `适当`.
const unquote = (text) => text.replace(/「[^」]*」|“[^”]*”|"[^"]*"|`[^`]*`/g, "");
const uncode = (text) => text.replace(/`[^`]*`/g, "");

export function findViolations(text, { vague, filler, allowed = [], ruleIds = new Set(), dimensions = new Map() }) {
  const out = [];
  const lines = text.split("\n");
  let header = null;
  let acceptanceLevel = 0; // heading level of the acceptance section we are inside, 0 = none
  lines.forEach((line, i) => {
    const heading = line.match(/^(#{1,6})\s/);
    if (heading) {
      const level = heading[1].length;
      if (acceptanceLevel && level > acceptanceLevel) return;
      acceptanceLevel = ACCEPTANCE.test(line) ? level : 0;
      return;
    }
    const isRow = /^\s*\|/.test(line);
    if (!isRow) header = null;
    else if (/^\s*\|\s*:?-{3,}/.test(line)) {
      header = cells(lines[i - 1] ?? "").map((h) => ACCEPTANCE.test(h));
      return;
    }
    let checked = [];
    if (/^\s*[-*]\s+\[[ xX]\]/.test(line)) checked = [line];
    else if (isRow && header) checked = cells(line).filter((_, c) => header[c]);
    else if (acceptanceLevel && /^\s*(?:[-*]|\d+\.)\s/.test(line)) checked = [line];
    for (const raw of checked) {
      let named = unquote(raw);
      for (const a of allowed) named = named.split(a).join("");
      for (const word of filler) if (named.includes(word)) out.push({ line: i + 1, word, kind: "filler" });

      const refs = [...raw.matchAll(RULE_REF)].map((m) => m[1]);
      for (const id of refs) if (!ruleIds.has(id)) out.push({ line: i + 1, word: id, kind: "bad-ref" });
      const letters = new Set(refs.filter((id) => ruleIds.has(id)).map((id) => id[0]));
      const used = uncode(raw);
      for (const word of vague) {
        if (!used.includes(word)) continue;
        const letter = dimensions.get(word);
        const defined = letter ? letters.has(letter) : COMBO_REF.test(raw);
        if (!defined) out.push({ line: i + 1, word, kind: letter ? "vague" : "combo" });
      }
    }
  });
  return out;
}
