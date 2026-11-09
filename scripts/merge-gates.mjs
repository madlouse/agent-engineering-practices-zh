// 合并脚本的「改动范围」检查（scripts/merge-ticket-pr.sh 从集成分支取本文件的版本来跑，PR 改不了它）。只读 git，不改任何东西。
// 用法：node scripts/merge-gates.mjs <base-ref> <head-sha> <head 分支名> [PR 标题和正文的文件]
// 分支名决定是不是票（TICKET_BRANCH）和票号；票的 PR 查得最严。
// 输出：通过时无输出、退出码 0；不通过时打印原因、退出码 1。
// 复用 Veli scripts/merge-gates.mjs，按主站改（docs/standards/pipeline.md §5、§8 第 0 阶段、§9）。
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

// 定义门槛的文件：票的 PR（feat/、fix/、content/）不能动，改名、删除也算。要改就由主会话开 chore/ PR，打 owner:merge
export const GATE_FILES = [
  /^scripts\/merge-ticket-pr\.sh$/,
  /^scripts\/merge-gates(\.test)?\.mjs$/,
  /^scripts\/review-markers(\.test)?\.mjs$/,
  /^scripts\/(check-terms|check-vague|vague-terms)\.mjs$/,
  /^eslint\.config\.mjs$/,
  /^\.github\/workflows\//,
  /^\.claude\/agents\//,
  /^\.claude\/settings[^/]*\.json$/,
  /^docs\/standards\/(pipeline|observer|quality-terms)\.md$/,
  /^docs\/delivery\/loops\//,
  /^docs\/GLOSSARY\.md$/,
];
// 状态 issue #13（总开关、运行锁、日报）不能被 PR 关掉
export const PROTECTED_ISSUES = new Set(["13"]);
// 票的分支：content/ 和 feat/、fix/ 一样算票
export const TICKET_BRANCH = /^(?:feat|fix|content)\/(\d+)-/;

// 不是票的分支只认这两种前缀；其余一律拒绝（出错时拒绝，不放行）
export const OTHER_BRANCH = /^(?:chore|obs)\/[^/]/;

/** 分支名 → { kind: 'ticket' | 'other' | 'invalid', ticket: 票号或 '' } */
export function classifyBranch(ref) {
  const m = TICKET_BRANCH.exec(ref);
  if (m) return { kind: "ticket", ticket: m[1] };
  if (OTHER_BRANCH.test(ref)) return { kind: "other", ticket: "" };
  return { kind: "invalid", ticket: "" };
}

export function checkGates({ base, head, kind, ticket = "", text = "", git }) {
  const show = (ref, path) => {
    try { return git("show", `${ref}:${path}`); } catch { return null; }
  };
  const problems = [];
  // 和 PR 的分叉点比：base 在 PR 开分支后改过的文件，不算 PR 改的
  const fork = git("merge-base", base, head).trim();
  const isTicket = kind === "ticket";

  if (isTicket) {
    const changed = git("diff", "--no-renames", "--name-only", `${fork}..${head}`).split("\n").filter(Boolean);
    for (const f of changed) if (GATE_FILES.some((r) => r.test(f))) problems.push(`改了定义门槛的文件 ${f}`);
    // package.json：已有的检查命令不能改、不能删；新增命令可以
    const bs = JSON.parse(show(fork, "package.json") ?? "{}").scripts ?? {};
    const hs = JSON.parse(show(head, "package.json") ?? "{}").scripts ?? {};
    for (const k of Object.keys(bs)) if (hs[k] !== bs[k]) problems.push(`package.json 的 scripts.${k} 被改或被删`);
  }

  // 关闭关键字（GitHub 的九个词，可带冒号、可带 owner/repo；否定句里写了也会生效）：查 PR 标题、正文和提交说明
  const all = text + "\n" + git("log", "--format=%B", `${fork}..${head}`);
  const CLOSE = /\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b:?\s+(?:[\w.-]+\/[\w.-]+)?#(\d+)/gi;
  for (const m of all.matchAll(CLOSE)) {
    const n = m[1];
    if (PROTECTED_ISSUES.has(n)) problems.push(`会关掉 #${n}（「${m[0]}」）：状态 issue 不能被 PR 关掉`);
    else if (isTicket && ticket && n !== ticket) problems.push(`票 #${ticket} 的 PR 会关掉别的 issue #${n}（「${m[0]}」）`);
  }

  // 票的 PR 不能削弱测试：删测试文件、新增 .only / .skip / .todo、新增关掉 lint 的写法
  if (isTicket) {
    const status = git("diff", "--no-renames", "--name-status", `${fork}..${head}`).split("\n").filter(Boolean);
    for (const line of status) {
      const [st, path] = line.split("\t");
      if (st === "D" && /\.test\.(?:mjs|ts|tsx)$/.test(path)) problems.push(`删了测试文件 ${path}`);
    }
    const added = git("diff", "-U0", `${fork}..${head}`, "--", ".", ":(exclude)docs")
      .split("\n")
      .filter((l) => l.startsWith("+") && !l.startsWith("+++"));
    const SKIP = [
      /\b(?:test|it|describe|suite|t|context|ctx)\.(?:only|skip|todo)\s*\(/,
      /\b(?:only|skip|todo)\s*:\s*(?:true|['"`])/, // 环境门控 { skip: needSite } 不算
    ];
    for (const l of added) {
      const code = l.slice(1).trim();
      if (SKIP.some((r) => r.test(code))) problems.push(`新增了跳过或只跑部分测试的写法：${code.slice(0, 80)}`);
      if (/eslint-disable|\/\*\s*eslint\s/.test(code)) problems.push(`新增了关掉 lint 的写法：${code.slice(0, 80)}`);
    }
  }
  return problems;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [base, head, ref, bodyFile = ""] = process.argv.slice(2);
  if (!base || !head || !ref) {
    console.log("用法：node scripts/merge-gates.mjs <base-ref> <head-sha> <head 分支名> [正文文件]");
    process.exit(2);
  }
  const { kind, ticket } = classifyBranch(ref);
  if (kind === "invalid") {
    console.log(`- 分支名不合规：${ref}。票用 feat/、fix/、content/ 加「<票号>-」开头，其余只能是 chore/ 或 obs/（docs/standards/pipeline.md §5）`);
    process.exit(1);
  }
  const git = (...a) => execFileSync("git", a, { encoding: "utf8", maxBuffer: 64 << 20 });
  const text = bodyFile ? readFileSync(bodyFile, "utf8") : "";
  const problems = checkGates({ base, head, kind, ticket, text, git });
  if (problems.length) {
    console.log(problems.map((p) => `- ${p}`).join("\n"));
    if (kind === "ticket") console.log("这类改动单独开 chore/ PR，由主会话做、打 owner:merge（docs/standards/pipeline.md §5）。");
    process.exit(1);
  }
}
