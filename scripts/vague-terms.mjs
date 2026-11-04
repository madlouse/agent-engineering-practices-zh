// Finds quality words with no definition in places that decide pass or fail: checklist items and
// acceptance columns of tables. Words and their definitions live in docs/standards/quality-terms.md.

export function parseBlock(markdown, name) {
  const block = markdown.match(new RegExp("```" + name + "\\n([\\s\\S]*?)```"));
  if (!block) throw new Error(`docs/standards/quality-terms.md has no \`\`\`${name} block`);
  return block[1]
    .split("\n")
    .map((t) => t.trim())
    .filter(Boolean);
}

const ACCEPTANCE_HEADER = /验收|出口|退出条件|判定|怎么判|到位|通过标准|完成的标准/;
const DEFINITION_LINK = "quality-terms";

const cells = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|");

export function findViolations(text, { vague, filler }) {
  const out = [];
  const lines = text.split("\n");
  let header = null;
  lines.forEach((line, i) => {
    const isRow = /^\s*\|/.test(line);
    const isRule = /^\s*\|\s*:?-{3,}/.test(line);
    if (!isRow) header = null;
    else if (isRule) {
      header = cells(lines[i - 1] ?? "").map((h) => ACCEPTANCE_HEADER.test(h));
      return;
    }
    let checked = [];
    if (/^\s*[-*]\s+\[[ xX]\]/.test(line)) checked = [line];
    else if (isRow && header) checked = cells(line).filter((_, c) => header[c]);
    for (const part of checked) {
      for (const word of filler) if (part.includes(word)) out.push({ line: i + 1, word, kind: "filler" });
      if (part.includes(DEFINITION_LINK)) continue;
      for (const word of vague) if (part.includes(word)) out.push({ line: i + 1, word, kind: "vague" });
    }
  });
  return out;
}
