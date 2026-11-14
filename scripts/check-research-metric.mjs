import { readFileSync, readdirSync, statSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const EXT = /\.(html|tsx|ts|jsx|js|json|md)$/;
const PASS = new Set(["高", "中", "high", "moderate"]);
const KNOWN = new Set(["高", "中", "低", "很低", "high", "moderate", "low", "very-low"]);
const VOID = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"]);

function skipQuoted(text, i) {
  const q = text[i];
  for (i++; i < text.length; i++) {
    if (text[i] === "\\") i++;
    else if (text[i] === q) return i + 1;
  }
  return i;
}

function skipBraces(text, i) {
  let depth = 0;
  while (i < text.length) {
    const c = text[i];
    if (c === '"' || c === "'" || c === "`") i = skipQuoted(text, i);
    else {
      if (c === "{") depth++;
      else if (c === "}" && --depth === 0) return i + 1;
      i++;
    }
  }
  return i;
}

function parseAttrs(src) {
  const attrs = new Map();
  let i = 0;
  while (i < src.length) {
    if (src[i] === "{") {
      i = skipBraces(src, i);
      continue;
    }
    const name = /^[A-Za-z_:][\w:.-]*/.exec(src.slice(i));
    if (!name) {
      i++;
      continue;
    }
    i += name[0].length;
    const eq = /^\s*=\s*/.exec(src.slice(i));
    let value = "";
    if (eq) {
      i += eq[0].length;
      const c = src[i];
      if (c === '"' || c === "'") {
        const end = skipQuoted(src, i);
        value = src.slice(i + 1, end - 1);
        i = end;
      } else if (c === "{") {
        const end = skipBraces(src, i);
        const lit = /^\{\s*(?:"([^"]*)"|'([^']*)'|`([^`$]*)`)\s*\}$/.exec(src.slice(i, end));
        value = lit ? lit[1] ?? lit[2] ?? lit[3] : src.slice(i, end);
        i = end;
      } else {
        const bare = /^[^\s"'>]+/.exec(src.slice(i));
        value = bare ? bare[0] : "";
        i += value.length;
      }
    }
    attrs.set(name[0], value);
  }
  return attrs;
}

export function scanTags(text) {
  const tags = [];
  const open = /<(\/?)([A-Za-z][\w:-]*)/g;
  let m;
  while ((m = open.exec(text))) {
    let i = open.lastIndex;
    while (i < text.length && text[i] !== ">") {
      const c = text[i];
      if (c === '"' || c === "'") i = skipQuoted(text, i);
      else if (c === "{") i = skipBraces(text, i);
      else i++;
    }
    let body = text.slice(open.lastIndex, i);
    const self = body.trimEnd().endsWith("/");
    if (self) body = body.trimEnd().slice(0, -1);
    const name = m[2].toLowerCase();
    const line = text.slice(0, m.index).split("\n").length;
    tags.push({ close: m[1] === "/", name, attrs: parseAttrs(body), self: self || VOID.has(name), line });
    open.lastIndex = i + 1;
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
