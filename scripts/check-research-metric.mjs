import { readFileSync, readdirSync, statSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const EXT = /\.(html|tsx|ts|jsx|js|json|md)$/;
const PASS = new Set(["高", "中", "high", "moderate"]);
const KNOWN = new Set(["高", "中", "低", "很低", "high", "moderate", "low", "very-low"]);
const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]);

export function scanTags(text) {
  const tags = [];
  const re = /<(\/?)([A-Za-z][\w:-]*)((?:"[^"]*"|'[^']*'|[^'">])*?)(\/?)>/g;
  let m;
  while ((m = re.exec(text))) {
    const attrs = new Map();
    for (const a of m[3].matchAll(/([A-Za-z_:][\w:.-]*)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+)))?/g)) {
      attrs.set(a[1], a[2] ?? a[3] ?? a[4] ?? "");
    }
    const line = text.slice(0, m.index).split("\n").length;
    tags.push({ close: m[1] === "/", name: m[2].toLowerCase(), attrs, self: m[4] === "/" || VOID.has(m[2].toLowerCase()), line });
  }
  return tags;
}

export function findProblems(text) {
  const problems = [];
  const stack = [];
  for (const tag of scanTags(text)) {
    if (tag.close) {
      for (let i = stack.length - 1; i >= 0; i--) {
        if (stack[i].name === tag.name) {
          stack.length = i;
          break;
        }
      }
      continue;
    }
    if (tag.attrs.has("data-research-metric")) {
      const card = tag.attrs.has("data-research-card") ? tag : [...stack].reverse().find((t) => t.attrs.has("data-research-card")) ?? tag;
      const value = card.attrs.get("data-credibility");
      if (value === undefined) problems.push({ line: tag.line, why: "研究卡放了大数字，但没有标 data-credibility" });
      else if (!KNOWN.has(value)) problems.push({ line: tag.line, why: `data-credibility 的值「${value}」不合法，只能是 高、中、低、很低、high、moderate、low、very-low` });
      else if (!PASS.has(value)) problems.push({ line: tag.line, why: `可信度是「${value}」，不放大字：数写进方法一行（quality-terms T8）` });
    }
    if (!tag.self) stack.push(tag);
  }
  return problems;
}

function collect(path, out) {
  const st = statSync(path);
  if (st.isDirectory()) {
    for (const name of readdirSync(path)) {
      if (name === "node_modules" || name.startsWith(".")) continue;
      collect(join(path, name), out);
    }
  } else if (EXT.test(path)) out.push(path);
  return out;
}

export function run(args) {
  const roots = args.length ? args : ["src"];
  const files = roots.flatMap((r) => collect(r, []));
  const lines = [];
  for (const file of files) {
    for (const p of findProblems(readFileSync(file, "utf8"))) lines.push(`${file}:${p.line}: ${p.why}`);
  }
  return { files: files.length, lines };
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { files, lines } = run(process.argv.slice(2));
  if (lines.length) {
    for (const l of lines) console.log(l);
    console.error(`\n${lines.length} 处问题。大数字只用于可信度为高或中的研究卡（docs/standards/quality-terms.md T8）。`);
    process.exit(1);
  }
  console.log(`研究卡大数字检查通过：${files} 个文件。`);
}
