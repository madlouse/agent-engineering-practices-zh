#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const WHY = /^(?:why|为什么)\s*[:：]\s*\S/i;

const list = (item) => String.raw`${item}(?:\s*,\s*${item})*`;
const full = (...forms) => new RegExp(`^(?:${forms.join("|")})$`);
const NOQA = String.raw`noqa(?::\s*${list(String.raw`[A-Z]+\d+`)})?`;

export const DIRECTIVES = {
  c: full(
    String.raw`eslint-(?:disable|enable)(?:-next-line|-line)?(?:\s+${list(String.raw`[\w@/-]+`)})?(?:\s+--\s+\S.*)?`,
    String.raw`eslint-env\s+${list(String.raw`[\w-]+`)}`,
    String.raw`eslint\s+${list(String.raw`[\w@/-]+:\s*(?:off|warn|error|[0-2]|\[.*\])`)}`,
    String.raw`globals?\s+${list(String.raw`[\w$]+(?::\s*(?:readonly|writable|off))?`)}`,
    String.raw`@ts-(?:expect-error|ignore)(?:\s+\S.*)?`,
    String.raw`@ts-(?:check|nocheck)`,
    String.raw`prettier-ignore`,
    String.raw`biome-ignore(?:-all|-start|-end)?\s+[\w/]+(?:\([\w/-]+\))?:\s*\S.*`,
    String.raw`deno-lint-ignore(?:-file)?(?:\s+[\w-]+)*`,
    String.raw`(?:c8|v8)\s+ignore\s+(?:next|if|else|file|start|stop)(?:\s+\d+)?`,
    String.raw`istanbul\s+ignore\s+(?:next|if|else|file)`,
    String.raw`<reference\s+(?:path|types|lib|no-default-lib)=""\s*/>`,
    String.raw`@vitest-environment\s+[\w-]+`,
    String.raw`@vite-ignore`,
    String.raw`@jsx(?:Runtime|ImportSource|Frag)?\s+[\w.@/-]+`,
    list(String.raw`webpack\w+:\s*\S+`),
    String.raw`[#@]__(?:PURE|NO_SIDE_EFFECTS)__`,
  ),
  hash: full(
    NOQA,
    String.raw`type:\s*ignore(?:\[${list(String.raw`[\w-]+`)}\])?`,
    String.raw`type:\s*[\w.\[\](),|*\s>-]+`,
    String.raw`pylint:\s*(?:disable|enable|disable-next)=${list(String.raw`[\w-]+`)}`,
    String.raw`pylint:\s*skip-file`,
    String.raw`pyright:\s*(?:ignore(?:\[${list(String.raw`[\w-]+`)}\])?|basic|standard|strict|${list(String.raw`\w+=\w+`)})`,
    String.raw`mypy:\s*${list(String.raw`[\w-]+(?:\s*=\s*[\w.-]+)?`)}`,
    String.raw`fmt:\s*(?:skip|off|on)`,
    String.raw`isort:\s*(?:skip|skip_file|off|on|split)`,
    String.raw`nosec(?:\s+${list(String.raw`B\d+`)})?`,
    String.raw`pragma:\s*no\s+(?:cover|branch)`,
    String.raw`shellcheck(?:\s+(?:disable|enable|source|source-path|shell|external-sources)=\S+)+`,
    String.raw`yamllint\s+(?:disable|enable)(?:-line|-file)?(?:\s+rule:[\w-]+)*`,
    String.raw`-\*-\s*coding[:=]\s*[\w.-]+\s*-\*-`,
  ),
  sql: full(NOQA),
};
const NESTED = { c: /\s+\/\/\s*/, hash: /\s+#(?!\d)\s*/, sql: /\s+--\s*/ };

const C_LIKE = /\.(?:[cm]?[jt]sx?|css|scss)$/;
const SQL = /\.sql$/;
const TRIPLE_QUOTED = /\.(?:py|toml)$/;
const HASH = /\.(?:sh|bash|ya?ml)$/;
const TRIPLE_QUOTED_TOKEN = /"""|'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#(.*)$/g;

const stripStrings = (line) => line.replace(/(["'`])(?:\\.|(?!\1).)*\1/g, '""');
const shebang = (l) => l.line === 1 && l.text.startsWith("#!");

function cLikeComments(lines) {
  let inBlock = false;
  let previous = null;
  return lines.map((l) => {
    if (previous !== null && l.line !== previous + 1) inBlock = false;
    previous = l.line;
    const code = stripStrings(l.text);
    if (inBlock) {
      if (code.includes("*/")) inBlock = false;
      return { text: code.replace(/\*\/.*$/, "").replace(/^\s*\*?\s?/, ""), multi: true, kind: "c" };
    }
    const m = /(?:^|[^:\\])(\/\/|\/\*)(.*)$/.exec(code);
    if (!m) return null;
    if (m[1] === "//") return { text: m[2].replace(/^\/?\s*/, ""), multi: false, kind: "c" };
    const closed = m[2].includes("*/");
    inBlock = !closed;
    return { text: m[2].replace(/\*\/.*$/, "").replace(/^\*?\s*/, ""), multi: !closed, kind: "c" };
  });
}

function tripleQuotedComments(lines) {
  let open = null;
  let previous = null;
  return lines.map((l) => {
    if (previous !== null && l.line !== previous + 1) open = null;
    previous = l.line;
    if (shebang(l)) return null;
    TRIPLE_QUOTED_TOKEN.lastIndex = 0;
    if (open) {
      const end = l.text.indexOf(open);
      if (end < 0) return null;
      TRIPLE_QUOTED_TOKEN.lastIndex = end + 3;
      open = null;
    }
    for (let m; (m = TRIPLE_QUOTED_TOKEN.exec(l.text)); ) {
      if (m[1] !== undefined) return { text: m[1].trim(), multi: false, kind: "hash" };
      if (m[0] !== '"""' && m[0] !== "'''") continue;
      const end = l.text.indexOf(m[0], TRIPLE_QUOTED_TOKEN.lastIndex);
      if (end < 0) {
        open = m[0];
        return null;
      }
      TRIPLE_QUOTED_TOKEN.lastIndex = end + 3;
    }
    return null;
  });
}

export function commentsOf(path, lines) {
  if (C_LIKE.test(path)) return cLikeComments(lines);
  if (TRIPLE_QUOTED.test(path)) return tripleQuotedComments(lines);
  const [pattern, kind] = SQL.test(path) ? [/--(.*)$/, "sql"] : HASH.test(path) ? [/(?:^|(?<!\\)\s)#(.*)$/, "hash"] : [];
  return lines.map((l) => {
    const m = pattern && !shebang(l) && pattern.exec(stripStrings(l.text));
    return m ? { text: m[1].trim(), multi: false, kind } : null;
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
      const parts = c.text.trim().split(NESTED[c.kind]).filter(Boolean);
      const last = parts.length - 1;
      const why = last >= 0 && WHY.test(parts[last]);
      const allowed = (p, j) => DIRECTIVES[c.kind].test(p) || allow.some((r) => r.test(p)) || (j === last && why);
      const where = `${path}:${lines[i].line}`;
      if (!parts.every(allowed)) {
        problems.push(`${where} 新增了注释：${c.text.trim().slice(0, 60)}`);
        return;
      }
      if (!why) return;
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
