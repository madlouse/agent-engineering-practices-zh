#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { readFileSync, realpathSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const idsIn = (text, re) => new Set([...text.matchAll(new RegExp(re, "g"))].map((m) => m[1] ?? m[0]).filter(Boolean));

export const CASE_REF = /\b(?:test|it|describe|scenario)(?:\.(?!skip\b|todo\b|fixme\b)\w+)*\(\s*(["'`])((?:(?!\1)[^\\]|\\.)*)\1|\bprd["']?\s*[:=]\s*(\[[^\]]*\]|["'`][^"'`\n]*["'`])/g;

export const caseRefs = (text) => [...text.matchAll(CASE_REF)].map((m) => m[2] ?? m[3]).join("\n");

export function judge({ config, files }) {
  if (typeof config.id !== "string" || !config.id.trim()) return { ok: false, summary: "e2eTrace 没配 id", missing: [], problems: ["e2eTrace.id 要写一个匹配 PRD 编号的正则，比如 \\b(F\\d{2})\\b"] };
  const pick = (list) => files.filter((f) => (list ?? []).some((s) => new RegExp(s).test(f.path)));
  const prd = new Set();
  for (const f of pick(config.prd)) for (const id of idsIn(f.text, config.id)) prd.add(id);
  const cited = new Map();
  for (const f of pick(config.cases)) for (const id of idsIn(caseRefs(f.text), config.id)) cited.set(id, [...(cited.get(id) ?? []), f.path]);
  const exempt = config.exempt ?? {};
  const problems = [];
  for (const [id, where] of cited) if (!prd.has(id)) problems.push(`${where[0]} 引用的 ${id} 在 PRD 里不存在：改成现有的条目，或先改 PRD`);
  for (const [id, reason] of Object.entries(exempt)) {
    if (!prd.has(id)) problems.push(`exempt 里的 ${id} 在 PRD 里不存在，删掉这条豁免`);
    if (!String(reason).trim()) problems.push(`exempt 里的 ${id} 没写理由：写清为什么不能做成 E2E`);
  }
  const target = [...prd].filter((id) => !(id in exempt)).sort();
  const covered = target.filter((id) => cited.has(id));
  const missing = target.filter((id) => !cited.has(id));
  const ratio = target.length ? covered.length / target.length : 1;
  const min = config.minCoverage ?? 0;
  if (prd.size === 0) problems.push("PRD 里一个编号都没找到：检查 e2eTrace 的 prd 路径和 id 正则");
  if (ratio < min) problems.push(`PRD 覆盖 ${(ratio * 100).toFixed(0)}%，低于门槛 ${(min * 100).toFixed(0)}%：给缺的条目补案例；确实不能做成 E2E 的写进 exempt 并写理由`);
  const summary = `PRD 条目 ${target.length} 条（另有豁免 ${prd.size - target.length} 条），有案例的 ${covered.length} 条，${(ratio * 100).toFixed(0)}%`;
  return { ok: problems.length === 0, summary, missing, problems };
}

function listFiles(root) {
  const git = (...a) => execFileSync("git", ["-C", root, ...a], { encoding: "utf8", maxBuffer: 256 << 20, stdio: ["ignore", "pipe", "ignore"] });
  const paths = git("-c", "core.quotepath=off", "ls-files").split("\n").filter(Boolean);
  return { git, paths, read: (p) => readFileSync(join(root, p), "utf8") };
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [base] = process.argv.slice(2);
  const root = process.cwd();
  const { git, paths, read } = listFiles(root);
  let config;
  try {
    config = JSON.parse(base ? git("show", `${base}:.velicoach-checks.json`) : read(".velicoach-checks.json")).e2eTrace;
  } catch {
    config = undefined;
  }
  if (!config) {
    console.log(`E2E 覆盖 PRD：${base ?? "工作区"} 上还没有 .velicoach-checks.json 的 e2eTrace 配置，跳过`);
    process.exit(0);
  }
  const wanted = [...(config.prd ?? []), ...(config.cases ?? [])].map((s) => new RegExp(s));
  const files = paths.filter((p) => wanted.some((r) => r.test(p))).map((p) => ({ path: p, text: read(p) }));
  const result = judge({ config, files });
  console.log(`E2E 覆盖 PRD：${result.summary}`);
  if (result.missing.length) console.log(`还没有案例：${result.missing.join("、")}`);
  for (const p of result.problems) console.error(`problem: ${p}`);
  process.exit(result.ok ? 0 : 1);
}
