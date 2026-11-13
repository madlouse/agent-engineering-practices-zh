#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const WHY = /^(?:why|为什么)\s*[:：]\s*\S/i;
export const DIRECTIVES =
  /^(?:eslint-|@ts-|prettier-ignore|biome-ignore|deno-lint-ignore|c8 |v8 |istanbul |<reference|@vitest-|@vite-|@jsx|webpack|[#@]__PURE__|shellcheck |noqa|type: ?ignore|pragma|!)/;

const C_LIKE = /\.(?:[cm]?[jt]sx?|css|scss)$/;
const SQL = /\.sql$/;
const TRIPLE_QUOTED = /\.(?:py|toml)$/;
const HASH = /\.(?:sh|bash|ya?ml)$/;

const stripStrings = (line) => line.replace(/(["'`])(?:\\.|(?!\1).)*\1/g, '""');

function cLikeComments(lines) {
  let inBlock = false;
  let previous = null;
  return lines.map((l) => {
    if (previous !== null && l.line !== previous + 1) inBlock = false;
    previous = l.line;
    const code = stripStrings(l.text);
    if (inBlock) {
      if (code.includes("*/")) inBlock = false;
      return { text: code.replace(/\*\/.*$/, "").replace(/^\s*\*?\s?/, ""), multi: true };
    }
    const m = /(?:^|[^:\\])(\/\/|\/\*)(.*)$/.exec(code);
    if (!m) return null;
    if (m[1] === "//") return { text: m[2].replace(/^\/?\s*/, ""), multi: false };
    const closed = m[2].includes("*/");
    inBlock = !closed;
    return { text: m[2].replace(/\*\/.*$/, "").replace(/^\*?\s*/, ""), multi: !closed };
  });
}

function tripleQuotedComments(lines) {
  let open = null;
  let previous = null;
  return lines.map((l) => {
    if (previous !== null && l.line !== previous + 1) open = null;
    previous = l.line;
    let code = l.text;
    if (open) {
      const end = code.indexOf(open);
      if (end < 0) return null;
      code = code.slice(end + 3);
      open = null;
    }
    code = code.replace(/("""|''')[\s\S]*?\1/g, '""');
    const unclosed = /"""|'''/.exec(code);
    const m = /#(.*)$/.exec(stripStrings(unclosed ? code.slice(0, unclosed.index) : code));
    if (m) return { text: (m[1] + (unclosed ? code.slice(unclosed.index) : "")).trim(), multi: false };
    if (unclosed) open = unclosed[0];
    return null;
  });
}

export function commentsOf(path, lines) {
  if (C_LIKE.test(path)) return cLikeComments(lines);
  if (TRIPLE_QUOTED.test(path)) return tripleQuotedComments(lines);
  const pattern = SQL.test(path) ? /--(.*)$/ : HASH.test(path) ? /(?:^|(?<!\\)\s)#(.*)$/ : null;
  return lines.map((l) => {
    const m = pattern && pattern.exec(stripStrings(l.text));
    return m ? { text: m[1].trim(), multi: false } : null;
  });
}

export function judge({ config, added }) {
  const toRes = (list) => (list ?? []).map((s) => new RegExp(s));
  const paths = toRes(config.paths);
  const exclude = toRes(config.exclude);
  const allow = toRes(config.allow);
  const problems = [];
  for (const { path, lines } of added) {
    if (!paths.some((r) => r.test(path)) || exclude.some((r) => r.test(path))) continue;
    const comments = commentsOf(path, lines);
    comments.forEach((c, i) => {
      if (!c) return;
      const text = c.text.trim();
      if (!text || DIRECTIVES.test(text) || allow.some((r) => r.test(text))) return;
      const where = `${path}:${lines[i].line}`;
      if (!WHY.test(text)) {
        problems.push(`${where} 新增了注释：${text.slice(0, 60)}`);
        return;
      }
      const touching = [i - 1, i + 1].some((j) => comments[j] && Math.abs(lines[j].line - lines[i].line) === 1);
      if (c.multi || touching) problems.push(`${where} why 注释只能写一行`);
    });
  }
  return problems;
}

export function addedLines(diff) {
  const out = [];
  let file = null;
  let line = 0;
  for (const raw of diff.split("\n")) {
    if (raw.startsWith("+++ ")) {
      file = raw.startsWith("+++ b/") ? { path: raw.slice(6), lines: [] } : null;
      if (file) out.push(file);
      continue;
    }
    const hunk = /^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/.exec(raw);
    if (hunk) {
      line = Number(hunk[1]);
      continue;
    }
    if (!file) continue;
    if (raw.startsWith("+")) file.lines.push({ line: line++, text: raw.slice(1) });
    else if (!raw.startsWith("-") && !raw.startsWith("\\")) line++;
  }
  return out;
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [base, head] = process.argv.slice(2);
  if (!base || !head) {
    console.log("用法：node scripts/check-comments.mjs <base-ref> <head-ref>。配置取自 base 上 .velicoach-checks.json 的 comments（paths、exclude、allow，都是正则）；规则见 velicoach-mono/standards/engineering.md「结构和代码」。");
    process.exit(2);
  }
  const git = (...a) => execFileSync("git", a, { encoding: "utf8", maxBuffer: 64 << 20, stdio: ["ignore", "pipe", "ignore"] });
  let config;
  try {
    config = JSON.parse(git("show", `${base}:.velicoach-checks.json`)).comments;
  } catch {
    config = undefined;
  }
  if (!config) {
    console.log(`注释：${base} 上还没有 .velicoach-checks.json 的 comments 配置，跳过`);
    process.exit(0);
  }
  const diff = git("-c", "core.quotepath=off", "diff", "--no-renames", "--unified=0", `${base}...${head}`);
  const problems = judge({ config, added: addedLines(diff) });
  if (problems.length === 0) {
    console.log("注释：新增的代码里没有注释，或只有一行 why 注释");
    process.exit(0);
  }
  console.log(
    [
      "注释：代码里不写注释，代码本身就是唯一事实。把意图写进命名、类型和测试，需求和设计写进 PRD 和技术方案；如果注释在解释为什么没按正确的做法写，去改代码本身，不要把它改写成 why。只有从代码读不出来的外部原因（第三方库的 bug、平台的硬限制）可以留一行「// why: …」。",
      ...problems.map((p) => `- ${p}`),
    ].join("\n"),
  );
  process.exit(1);
}
