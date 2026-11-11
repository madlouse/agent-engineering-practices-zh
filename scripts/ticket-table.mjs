// Pure helpers behind `npm run check:ticket-table`: compare docs/delivery/gate-3b-split.md (§1 counts, §3 tables,
// §4 Mermaid edges) with what GitHub says, and regenerate the generated parts. No network and no file access here,
// so everything is unit-testable; scripts/check-ticket-table.mjs does the fetching and the file I/O.
//
// What comes from GitHub: title, labels, open blockers (native dependencies). What stays hand-written in the doc:
// the 功能号 column, the last (备注) column, and which table a ticket sits in.

import { isOwnerIssue } from "./cross-repo-refs.mjs";

export const REPO = "velicoach";
export const WRITABLE_REPO = `madlouse/${REPO}`;
export const PER_PAGE = 100;
export const MAX_PAGES = 20;
// Open issues that carry a lane label but are not tickets in the table: the content umbrella issue (#3)
// and the gate 3a review issue (#14).
export const NOT_IN_TABLE = new Set([3, 14]);
const SITE_GROUPS = ["M1", "M2", "M3", "M4", "不属于里程碑"];
const CONTENT_GROUP = "内容车道";

/**
 * Fetches every page. `fetchPage(page)` returns an array; a page shorter than `perPage` is the last one.
 * Stops with an error after `maxPages` full pages instead of looping forever on a misbehaving endpoint.
 */
export async function paginate(fetchPage, perPage = 100, maxPages = 20) {
  const all = [];
  for (let page = 1; page <= maxPages; page++) {
    const items = await fetchPage(page);
    all.push(...items);
    if (items.length < perPage) return all;
  }
  throw new Error(`翻了 ${maxPages} 页还没到头，停下（每页 ${perPage} 条）`);
}

/**
 * A title as it is written into a table cell. Titles come from GitHub and end up in a Markdown file that people and
 * agents read: backticks and backslashes are dropped, 「<」 and 「[」 are written as entities so the cell cannot open
 * an HTML tag or a link. The comparison uses the same function, so the doc and GitHub still match.
 */
export function tableTitle(title) {
  return stripBidi(title)
    .replace(/[`\\]/g, "")
    .replaceAll("<", "&lt;")
    .replaceAll("[", "&#91;")
    .replaceAll("://", ":&#47;&#47;")
    .replace(/www\./gi, (m) => `${m.slice(0, 3)}&#46;`)
    .replaceAll("@", "&#64;");
}

// Unicode bidirectional controls can make text display in a different order than it is stored.
function stripBidi(text) {
  return text.replace(/[\u202A-\u202E\u2066-\u2069\u200E\u200F]/g, "");
}

/** A title as it is written into a Mermaid node label: the characters that could end the label or start markup are dropped. */
export function diagramTitle(title) {
  return stripBidi(title)
    .replace(/[<>"`\\[\]]/g, "")
    .slice(0, 16);
}

/** One blocker as written in the table: 「#12」 for this repo, 「thin-muscle-coach#185」 for another one. */
export function blockerRef({ repo, number }) {
  return repo === REPO ? `#${number}` : `${repo}#${number}`;
}

/** Open blockers only, this repo's first, other repos' after (the order check:terms asks for). */
export function blockerRefs(blockedBy) {
  const open = blockedBy.filter((b) => b.state === "open");
  return [...open.filter((b) => b.repo === REPO), ...open.filter((b) => b.repo !== REPO)].map(blockerRef);
}

const escapeCell = (text) => text.replaceAll("|", "\\|");
const unescapeCell = (text) => text.replaceAll("\\|", "|");

function splitRow(line) {
  const cells = [];
  let cell = "";
  const inner = line.trim().replace(/^\|/, "").replace(/\|$/, "");
  for (let i = 0; i < inner.length; i++) {
    if (inner[i] === "\\" && inner[i + 1] === "|") {
      cell += "\\|";
      i++;
    } else if (inner[i] === "|") {
      cells.push(cell.trim());
      cell = "";
    } else cell += inner[i];
  }
  cells.push(cell.trim());
  return cells;
}

function groupOf(heading) {
  const m = heading.match(/^### (M\d)\b/);
  if (m) return m[1];
  if (heading.startsWith("### 不属于里程碑")) return "不属于里程碑";
  if (heading.startsWith("### 内容车道")) return CONTENT_GROUP;
  return null;
}

/** Parses §3: every table row that starts with 「| #N |」, with the group (sub-heading) it sits under. */
export function parseTables(doc) {
  const lines = doc.split("\n");
  const start = lines.findIndex((l) => l.startsWith("## 3."));
  const end = lines.findIndex((l) => l.startsWith("## 4."));
  if (start < 0 || end < 0) throw new Error("找不到 §3 或 §4 的标题");
  const rows = [];
  let group = null;
  for (let i = start; i < end; i++) {
    if (lines[i].startsWith("### ")) group = groupOf(lines[i]);
    if (!/^\| #\d+ \|/.test(lines[i])) continue;
    const cells = splitRow(lines[i]);
    if (cells.length !== 7) throw new Error(`第 ${i + 1} 行不是 7 列`);
    rows.push({
      line: i,
      group,
      number: Number(cells[0].slice(1)),
      title: unescapeCell(cells[1]),
      feature: cells[2],
      blockers: cells[3] === "—" ? [] : cells[3].split("、").map((s) => s.trim()),
      lane: cells[4],
      labels: [...cells[5].matchAll(/`([^`]+)`/g)].map((m) => m[1]),
      note: cells[6],
    });
  }
  return rows;
}

function formatRow(row, issue) {
  const blockers = blockerRefs(issue.blockedBy);
  const labels = issue.labels.map((l) => `\`${l}\``).join(" ");
  return `| #${row.number} | ${escapeCell(tableTitle(issue.title))} | ${row.feature} | ${blockers.join("、") || "—"} | ${row.lane} | ${labels} | ${row.note} |`;
}

/** The Mermaid block of §4, generated from the rows (for the grouping) and the issues (titles, labels, blockers). */
export function buildMermaid(rows, issues) {
  const site = new Set(rows.filter((r) => r.group !== CONTENT_GROUP).map((r) => r.number));
  const lines = ["```mermaid", "flowchart LR"];
  for (const group of SITE_GROUPS) {
    lines.push(`  subgraph ${group}`);
    for (const r of rows.filter((row) => row.group === group)) lines.push(`    T${r.number}["#${r.number} ${diagramTitle(issues.get(r.number).title)}"]`);
    lines.push("  end");
  }
  const outside = new Map();
  for (const [from, to] of expectedEdges(rows, issues)) {
    lines.push(`  ${from} --> ${to}`);
    for (const id of [from, to]) {
      if (id.startsWith("C")) outside.set(id, `#${id.slice(1)}`);
      if (id.startsWith("V")) outside.set(id, `thin-muscle-coach#${id.slice(1)}`);
    }
  }
  for (const id of [...outside.keys()].sort()) lines.push(`  ${id}(["${outside.get(id)}"])`);
  for (const r of rows) if (site.has(r.number) && issues.get(r.number).labels.includes("ready-for-human")) lines.push(`  class T${r.number} human`);
  lines.push("  classDef human stroke-dasharray: 4 3", "```");
  return lines.join("\n");
}

/** Edges the diagram must have: one per open blocker of every ticket in the tables. T = site ticket, C = other issue of this repo, V = other repo. */
export function expectedEdges(rows, issues) {
  const site = new Set(rows.filter((r) => r.group !== CONTENT_GROUP).map((r) => r.number));
  const node = (number) => (site.has(number) ? `T${number}` : `C${number}`);
  const edges = [];
  for (const r of rows) {
    for (const b of issues.get(r.number).blockedBy) {
      if (b.state !== "open") continue;
      edges.push([b.repo === REPO ? node(b.number) : `V${b.number}`, node(r.number)]);
    }
  }
  return edges;
}

export function parseMermaidEdges(doc) {
  const block = doc.match(/```mermaid\n([\s\S]*?)\n```/);
  if (!block) throw new Error("找不到 §4 的 Mermaid 图");
  return [...block[1].matchAll(/^\s*(\w+) --> (\w+)\s*$/gm)].map((m) => [m[1], m[2]]);
}

/** Counts stated in §1, computed from the rows and the issues. */
export function counts(rows, issues) {
  const site = rows.filter((r) => r.group !== CONTENT_GROUP).map((r) => issues.get(r.number));
  const has = (label) => site.filter((i) => i.labels.includes(label)).length;
  return {
    site: site.length,
    readyForAgent: has("ready-for-agent"),
    readyForHuman: has("ready-for-human"),
    noReadyLabel: site.filter((i) => !i.labels.includes("ready-for-agent") && !i.labels.includes("ready-for-human")).length,
    riskHigh: has("risk:high"),
    content: rows.filter((r) => r.group === CONTENT_GROUP).length,
  };
}

const COUNT_PATTERNS = {
  site: /、(\d+) 张开着的票/,
  readyForAgent: /(\d+) 张 `ready-for-agent`/,
  readyForHuman: /(\d+) 张 `ready-for-human`/,
  noReadyLabel: /(\d+) 张暂时没有就绪标签/,
  riskHigh: /(\d+) 张 `risk:high`/,
  content: /内容车道 (\d+) 张/,
};

function countsLine(doc) {
  const lines = doc.split("\n");
  const start = lines.findIndex((l) => l.startsWith("## 1."));
  const index = lines.findIndex((l, i) => i > start && l.startsWith("**站点车道"));
  if (start < 0 || index < 0) throw new Error("找不到 §1 里写数字的那一段（以「**站点车道」开头）");
  return { lines, index };
}

export function parseCounts(doc) {
  const { lines, index } = countsLine(doc);
  const out = {};
  for (const [key, re] of Object.entries(COUNT_PATTERNS)) {
    const m = lines[index].match(re);
    if (!m) throw new Error(`§1 里找不到「${re.source}」这个数字`);
    out[key] = Number(m[1]);
  }
  return out;
}

/** A cycle among open issues of this repo, as a list of numbers, or null. */
export function findCycle(issues) {
  const state = new Map();
  const walk = (number, path) => {
    state.set(number, 1);
    for (const b of issues.get(number)?.blockedBy ?? []) {
      if (b.repo !== REPO || b.state !== "open" || !issues.has(b.number)) continue;
      if (state.get(b.number) === 1) return [...path, number, b.number];
      if (!state.has(b.number)) {
        const found = walk(b.number, [...path, number]);
        if (found) return found;
      }
    }
    state.set(number, 2);
    return null;
  };
  for (const number of issues.keys()) {
    if (state.has(number)) continue;
    const found = walk(number, []);
    if (found) return found;
  }
  return null;
}

const sameSet = (a, b) => a.length === b.length && a.every((x) => b.includes(x));

/**
 * Every difference between the doc and GitHub, as readable lines. `issues` maps number -> { title, labels, blockedBy }
 * for every open issue of the repo; blockedBy items are { repo, number, state }.
 */
export function compare(doc, issues, { nonOwnerOpen = new Set() } = {}) {
  const problems = [];
  const rows = parseTables(doc);
  const seen = new Set();
  for (const row of rows) {
    const at = `§3 第 ${row.line + 1} 行 #${row.number}`;
    if (seen.has(row.number)) problems.push(`${at}：这张票在表里出现了两次`);
    seen.add(row.number);
    const issue = issues.get(row.number);
    if (!issue) {
      problems.push(
        nonOwnerOpen.has(row.number)
          ? `${at}：这张票开着，但不是仓库所有者开的，脚本不处理这样的票；表里不该列它`
          : `${at}：GitHub 上不是开着的票（已关闭或不存在），表里还列着`,
      );
      continue;
    }
    if (row.title !== tableTitle(issue.title)) problems.push(`${at}：标题不一样。表里「${row.title}」，GitHub「${tableTitle(issue.title)}」`);
    if (!sameSet(row.labels, issue.labels)) problems.push(`${at}：标签不一样。表里 ${row.labels.join("、") || "无"}，GitHub ${issue.labels.join("、") || "无"}`);
    const want = blockerRefs(issue.blockedBy);
    const missing = want.filter((x) => !row.blockers.includes(x));
    const extra = row.blockers.filter((x) => !want.includes(x));
    if (missing.length) problems.push(`${at}：「被谁卡住」少了 ${missing.join("、")}`);
    if (extra.length) problems.push(`${at}：「被谁卡住」多了 ${extra.join("、")}（GitHub 上没有这条依赖，或者那张票已经关了）`);
  }
  for (const [number, issue] of issues) {
    const isTicket = issue.labels.some((l) => l.startsWith("lane:")) && !issue.labels.includes("spec") && !NOT_IN_TABLE.has(number);
    if (isTicket && !seen.has(number)) problems.push(`#${number}「${issue.title}」开着，§3 的表里没有它：先手写一行（功能号、车道和最后一列要人填），再重新生成`);
  }
  const known = rows.filter((r) => issues.has(r.number));
  const key = ([a, b]) => `${a} --> ${b}`;
  const want = new Set(expectedEdges(known, issues).map(key));
  const have = new Set(parseMermaidEdges(doc).map(key));
  for (const e of want) if (!have.has(e)) problems.push(`§4 的图少了一条边：${e}`);
  for (const e of have) if (!want.has(e)) problems.push(`§4 的图多了一条边：${e}`);
  const stated = parseCounts(doc);
  const actual = counts(known, issues);
  for (const k of Object.keys(actual)) if (stated[k] !== actual[k]) problems.push(`§1 的数字不对（${COUNT_PATTERNS[k].source}）：写的是 ${stated[k]}，实际是 ${actual[k]}`);
  const cycle = findCycle(issues);
  if (cycle) problems.push(`原生依赖有环：${cycle.map((n) => `#${n}`).join(" → ")}`);
  return problems;
}

/** The doc with the generated parts rewritten: §3 rows (title, blockers, labels), the §4 diagram, the §1 counts. */
export function regenerate(doc, issues) {
  const rows = parseTables(doc);
  const missing = rows.filter((r) => !issues.has(r.number));
  if (missing.length) throw new Error(`表里有已经关闭的票：${missing.map((r) => `#${r.number}`).join("、")}。先把这些行删掉或挪走，再重新生成`);
  let lines = doc.split("\n");
  for (const row of rows) lines[row.line] = formatRow(row, issues.get(row.number));
  let out = lines.join("\n").replace(/```mermaid\n[\s\S]*?\n```/, () => buildMermaid(rows, issues));
  const actual = counts(rows, issues);
  const { lines: outLines, index } = countsLine(out);
  for (const [k, re] of Object.entries(COUNT_PATTERNS)) outLines[index] = outLines[index].replace(re, (whole, n) => whole.replace(n, String(actual[k])));
  return outLines.join("\n");
}

/**
 * Command-line arguments of check-ticket-table: `[--write] [owner/repo]`. `--write` is only allowed for this repository:
 * another repository's data must not be written into this repository's doc.
 */
export function parseArgs(argv) {
  const unknown = argv.filter((a) => a.startsWith("--") && a !== "--write");
  if (unknown.length) return { error: `不认识的参数：${unknown.join(" ")}` };
  const write = argv.includes("--write");
  const repo = argv.find((a) => !a.startsWith("--")) ?? WRITABLE_REPO;
  if (!/^[\w.-]+\/[\w.-]+$/.test(repo)) return { error: `仓库要写成 owner/repo：${repo}` };
  if (write && repo !== WRITABLE_REPO) return { error: `--write 只对 ${WRITABLE_REPO} 用：别的仓库的数据不能写进本仓库的文档。` };
  return { write, repo };
}

/**
 * Loads the open issues of `repo` with their blockers, page by page. `fetchPage(path, page)` returns one page of a REST list.
 * Only issues opened by the repository owner are kept: the repo is public, and a stranger's issue must not reach the doc
 * or fail the check. The numbers of the other open issues are returned so a row for one of them gets an accurate message.
 */
export async function loadIssues(repo, fetchPage, perPage = PER_PAGE, maxPages = MAX_PAGES) {
  const open = (await paginate((page) => fetchPage(`repos/${repo}/issues?state=open`, page), perPage, maxPages)).filter((i) => !i.pull_request);
  const issues = new Map();
  const nonOwnerOpen = new Set();
  for (const issue of open) {
    if (!isOwnerIssue(issue)) {
      nonOwnerOpen.add(issue.number);
      continue;
    }
    const blockers = await paginate((page) => fetchPage(`repos/${repo}/issues/${issue.number}/dependencies/blocked_by`, page), perPage, maxPages);
    issues.set(issue.number, {
      title: issue.title,
      labels: issue.labels.map((l) => l.name),
      blockedBy: blockers.map((b) => ({ repo: b.repository_url.split("/").pop(), number: b.number, state: b.state })),
    });
  }
  return { issues, nonOwnerOpen };
}
