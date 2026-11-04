// Finds quality words with no definition, and filler words, in places that decide pass or fail:
// checklist items, list items under an acceptance heading, and acceptance columns of tables.
// Words, rule ids and allowed phrases live in docs/standards/quality-terms.md.

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

const ACCEPTANCE = /验收|出口|退出条件|判定|怎么判|到位|通过标准|完成的?标准|交付物|怎么查|门槛|acceptance|criteria|definition of done/i;
const RULE_REF = /quality-terms(?:\.md)?\s*(?:#|§)?\s*([A-Z]\d+)/g;

// Splits a table row on unescaped pipes, so "中文 \| EN" stays one cell.
const cells = (line) => line.trim().replace(/^\|/, "").replace(/(?<!\\)\|$/, "").split(/(?<!\\)\|/);
// Quoted words are being named, not used: 「待定」, “simple”, `适当`.
const unquote = (text) => text.replace(/「[^」]*」|“[^”]*”|"[^"]*"|`[^`]*`/g, "");

export function findViolations(text, { vague, filler, allowed = [], ruleIds = new Set() }) {
  const out = [];
  const lines = text.split("\n");
  let header = null;
  let underAcceptanceHeading = false;
  lines.forEach((line, i) => {
    if (/^#{1,6}\s/.test(line)) underAcceptanceHeading = ACCEPTANCE.test(line);
    const isRow = /^\s*\|/.test(line);
    if (!isRow) header = null;
    else if (/^\s*\|\s*:?-{3,}/.test(line)) {
      header = cells(lines[i - 1] ?? "").map((h) => ACCEPTANCE.test(h));
      return;
    }
    let checked = [];
    if (/^\s*[-*]\s+\[[ xX]\]/.test(line)) checked = [line];
    else if (isRow && header) checked = cells(line).filter((_, c) => header[c]);
    else if (underAcceptanceHeading && /^\s*(?:[-*]|\d+\.)\s/.test(line)) checked = [line];
    for (const raw of checked) {
      let part = unquote(raw);
      for (const a of allowed) part = part.split(a).join("");
      for (const word of filler) if (part.includes(word)) out.push({ line: i + 1, word, kind: "filler" });
      const refs = [...part.matchAll(RULE_REF)].map((m) => m[1]);
      for (const id of refs) if (!ruleIds.has(id)) out.push({ line: i + 1, word: id, kind: "bad-ref" });
      if (refs.some((id) => ruleIds.has(id))) continue;
      for (const word of vague) if (part.includes(word)) out.push({ line: i + 1, word, kind: "vague" });
    }
  });
  return out;
}
