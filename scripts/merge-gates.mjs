// 合并脚本的「改动范围」检查（scripts/merge-ticket-pr.sh 从集成分支取本文件的版本来跑，PR 改不了它）。只读 git，不改任何东西。
// 用法：node scripts/merge-gates.mjs <base-ref> <head-sha> <head 分支名> [PR 正文和标题的文件] [--pr-base <PR 的 base> --target <目标分支>]
// 分支名决定是不是票（TICKET_BRANCH）和票号；票的 PR 查得最严。不是票的 PR 按类别分 a、b；改了 OWNER_FILES 的、观察者（obs/）的 b 类一律不合并（prCategory）。
// 读路径一律用 -z（diffPaths），读内容的 diff 加 core.quotepath=false：git 默认把非 ASCII 文件名转义成带引号的形式，正则就匹配不上。
// 输出：通过时最后一行是 category=<ticket|a|b>、退出码 0；不通过时打印原因和按原因分开的下一步、退出码 1。
// 另有两行信号给合并脚本：risk=high（改依赖、锁文件、.npmrc、生命周期脚本、订阅库迁移或 site:migrate，和 risk:high 标签同效，riskHigh）；
// owner=yes（等产品负责人合并的类别，合并脚本顺带核对决策简报，scripts/check-owner-brief.mjs）。
// 复用 Veli scripts/merge-gates.mjs，按主站改（docs/standards/pipeline.md §5、§8 第 0 阶段、§9）。
import { execFileSync } from "node:child_process";
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

// 定义门槛的文件：票的 PR（feat/、fix/、content/）不能动，改名、删除也算。不是票的 PR 改了它们，一律按 b 类（要两份评审）
export const GATE_FILES = [
  /^scripts\/merge-ticket-pr\.sh$/,
  /^scripts\/merge-gates(\.test)?\.mjs$/,
  /^scripts\/review-markers(\.test)?\.mjs$/,
  /^scripts\/(check-terms|check-vague|vague-terms|check-owner-brief|check-voice|voice-terms)\.mjs$/,
  /^eslint\.config\.mjs$/,
  /^\.github\/workflows\//,
  /^\.claude\/agents\//,
  /^\.claude\/settings[^/]*\.json$/,
  /^docs\/standards\/(pipeline|observer|quality-terms)\.md$/,
  /^docs\/delivery\/loops\//,
  /^docs\/GLOSSARY\.md$/,
  /(?:^|\/)(?:AGENTS[^/]*|CLAUDE)\.md$/,
];
// 只归产品负责人的文件：任何 PR 改了，脚本都不合并（pipeline.md §5.1）
export const OWNER_FILES = [
  { re: /^\.claude\/settings[^/]*\.json$/, why: (p) => `改了权限设置 ${p}：等产品负责人合并（pipeline.md §5.1）` },
  // observer.md §4（观察者的权限）只能由产品负责人改（observer.md 开头）；脚本分不清改的是哪一节，整页都等产品负责人
  { re: /^docs\/standards\/observer\.md$/, why: (p) => `改了 ${p}：§4（观察者的权限）只能由产品负责人改，脚本分不清节，整页等产品负责人合并（pipeline.md §5.1）` },
];
// 执行检查的脚本：不是票的 PR 改或删它们，按 b 类（新增不算）
export const CHECK_FILES = [/^scripts\/(?:check-[^/]+|vague-terms|voice-terms|brand-check|[^/]+-verdict)\.mjs$/, /^eslint-suppressions\.json$/];
// 状态 issue #13（总开关、运行锁、日报）不能被 PR 关掉
export const PROTECTED_ISSUES = new Set(["13"]);
// 票的分支：content/ 和 feat/、fix/ 一样算票
export const TICKET_BRANCH = /^(?:feat|fix|content)\/(\d+)-/;

// 不是票的分支只认这两种前缀；其余一律拒绝（出错时拒绝，不放行）
export const OTHER_BRANCH = /^(?:chore|obs)\/[^/]/;
// 观察者的分支：它提的 b 类等产品负责人合并（pipeline.md §5.1、observer.md §4），不靠它自己打 owner:merge
export const OBSERVER_BRANCH = /^obs\//;
export const TEST_FILE = /\.test\.(?:[cm]?[jt]sx?)$/;

const QUOTE_OFF = ["-c", "core.quotepath=false"];
/** 改动的文件：[{ st, path }]，用 -z 读，非 ASCII 和带空白的文件名原样拿到。 */
export function diffPaths(git, range) {
  const parts = git(...QUOTE_OFF, "diff", "--no-renames", "--name-status", "-z", range).split("\0");
  const out = [];
  for (let i = 0; i + 1 < parts.length; i += 2) if (parts[i]) out.push({ st: parts[i], path: parts[i + 1] });
  return out;
}

// 上线前只合并进集成分支，上线后（feature/v1 删掉）只合并进生产分支；上线前进 site 的只有产品负责人确认的上线合并，脚本不做
export const INTEGRATION_BRANCH = "feature/v1";
export const PRODUCTION_BRANCH = "site";

/** PR 的 base 必须是目标分支（pipeline.md §5.1）。 */
export function checkBase(prBase, target) {
  if (![INTEGRATION_BRANCH, PRODUCTION_BRANCH].includes(target)) return [`目标分支只能是 ${INTEGRATION_BRANCH} 或 ${PRODUCTION_BRANCH}：${target}`];
  if (prBase === target) return [];
  if (prBase === PRODUCTION_BRANCH) return [`base 是 ${PRODUCTION_BRANCH}：上线前 ${PRODUCTION_BRANCH} 只接受产品负责人确认的上线合并，PR 改以 ${target} 为 base`];
  return [`base 是 ${prBase}，现在只合并进 ${target}`];
}

// PR 说明（正文）第一行写类别：「类别：票 / a / b / 内容定稿」（pipeline.md §5.1）
const CATEGORY_LINE = /^类别\s*[：:]\s*(票|a|b|内容定稿)\s*$/i;
/** 正文第一行里的类别；没写、写错或第一行是空行（正文为空时不拿标题顶替）返回 null。 */
export function declaredCategory(body) {
  const first = (body ?? "").split(/\r?\n/)[0].trim();
  const m = CATEGORY_LINE.exec(first);
  return m ? m[1].toLowerCase() : null;
}

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
    for (const { path: f } of diffPaths(git, `${fork}..${head}`)) if (GATE_FILES.some((r) => r.test(f))) problems.push(`改了定义门槛的文件 ${f}`);
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

  // 票的 PR 不能削弱测试（不是票的 PR 削弱了就按 b 类，见 prCategory）
  if (isTicket) problems.push(...weakenings({ fork, head, git }));
  return problems;
}

// tsconfig.json 的 include：只有这里的 @ts-expect-error 会被 tsc 核对
export const TSC_DIRS = /^(?:src|server)\//;
/** 削弱测试的改动：删测试文件、新增 .only / .skip / .todo / .skipIf、新增关掉 lint 或类型检查的写法。 */
export function weakenings({ fork, head, git }) {
  const problems = [];
  for (const { st, path } of diffPaths(git, `${fork}..${head}`)) {
    if (st === "D" && TEST_FILE.test(path)) problems.push(`删了测试文件 ${path}`);
  }
  const added = [];
  let file = "";
  for (const l of git(...QUOTE_OFF, "diff", "-U0", `${fork}..${head}`, "--", ".", ":(exclude)docs").split("\n")) {
    if (l.startsWith("+++ ")) file = l.slice(4).replace(/^b\//, "");
    else if (l.startsWith("+")) added.push({ file, line: l });
  }
  const SKIP = [
    /\b(?:test|it|describe|suite|t|context|ctx)\.(?:only|skip|todo|skipIf|runIf)\s*\(/,
    /\b(?:only|skip|todo)\s*:\s*(?:true|['"`])/, // 环境门控 { skip: needSite } 不算
  ];
  for (const { file: f, line: l } of added) {
    const code = l.slice(1).trim();
    if (SKIP.some((r) => r.test(code))) problems.push(`新增了跳过或只跑部分测试的写法：${code.slice(0, 80)}`);
    if (/eslint-disable|\/\*\s*eslint\s/.test(code)) problems.push(`新增了关掉 lint 的写法：${code.slice(0, 80)}`);
    if (/@ts-(?:nocheck|ignore)\b/.test(code)) problems.push(`新增了关掉类型检查的写法：${code.slice(0, 80)}`);
    // @ts-expect-error 只在 tsc 检查的目录放行：下一行没有类型错误时它自己报错，不会留下压错的空壳；压掉的真实错误靠评审核对
    else if (/@ts-expect-error\b/.test(code) && !TSC_DIRS.test(f)) problems.push(`新增了关掉类型检查的写法（${f} 不在 tsconfig 的 include 里，@ts-expect-error 等于 @ts-ignore）：${code.slice(0, 80)}`);
  }
  return problems;
}

/** 改已有测试文件时删掉的断言行（含 assert / expect）。只新增用例的不算。 */
export function removedAssertions({ fork, head, git }) {
  const problems = [];
  for (const { st, path } of diffPaths(git, `${fork}..${head}`)) {
    if (st !== "M" || !TEST_FILE.test(path)) continue;
    const removed = git(...QUOTE_OFF, "diff", "-U0", `${fork}..${head}`, "--", `:(literal)${path}`)
      .split("\n")
      .filter((l) => l.startsWith("-") && !l.startsWith("---") && /\b(?:assert|expect)\b/.test(l));
    if (removed.length) problems.push(`改了已有测试 ${path}，删掉 ${removed.length} 行断言：${removed[0].slice(1).trim().slice(0, 80)}`);
  }
  return problems;
}

// 提前结束：return 后面什么都没有，或只有一个字面量（测试回调的返回值被忽略，return 0 和 return; 一样）
const EARLY_RETURN = /\breturn\b\s*(?:(?:undefined|null|true|false|void\s+0|-?\d+(?:\.\d+)?|""|''|``)\s*)?(?:;|\}|$)/;
/** 改已有测试文件时新增的提前 return（return;、{ return }、return 0; 这类）：后面的断言就不跑了。新测试文件里的不算。 */
export function earlyReturns({ fork, head, git }) {
  const problems = [];
  for (const { st, path } of diffPaths(git, `${fork}..${head}`)) {
    if (st !== "M" || !TEST_FILE.test(path)) continue;
    const added = git(...QUOTE_OFF, "diff", "-U0", `${fork}..${head}`, "--", `:(literal)${path}`)
      .split("\n")
      // 去掉行尾注释时只认前面是空白或行首的 //，字符串里的 http:// 不算
      .filter((l) => l.startsWith("+") && !l.startsWith("+++") && EARLY_RETURN.test(l.slice(1).replace(/(^|\s)\/\/.*$/, "$1").trimEnd()));
    if (added.length) problems.push(`改了已有测试 ${path}，新增 ${added.length} 处提前 return：${added[0].slice(1).trim().slice(0, 80)}`);
  }
  return problems;
}

// 和 risk:high 标签同效的改动：依赖、锁文件、npm 配置和生命周期脚本、订阅库迁移、执行迁移的命令（pipeline.md §5.1）
export const DEP_FIELDS = ["dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "overrides"];
export const RISK_FILES = [/^package-lock\.json$/, /^npm-shrinkwrap\.json$/, /(?:^|\/)\.npmrc$/, /^migrations\/site\//];
// site:migrate 执行迁移；其余是 npm 生命周期脚本，npm install（每次预览和生产构建）会自动执行
export const RISK_SCRIPTS = ["site:migrate", "preinstall", "install", "postinstall", "prepublish", "preprepare", "prepare", "postprepare", "prepack", "postpack", "dependencies"];
/** 要安全评审的改动（返回原因）：改了 package.json 的依赖字段、site:migrate 或生命周期脚本，锁文件、.npmrc，migrations/site/ 下的文件。 */
export function riskHigh({ fork, head, git }) {
  const reasons = [];
  for (const { path } of diffPaths(git, `${fork}..${head}`)) if (RISK_FILES.some((r) => r.test(path))) reasons.push(`改了 ${path}`);
  const show = (ref) => { try { return JSON.parse(git("show", `${ref}:package.json`)); } catch { return {}; } };
  const b = show(fork);
  const h = show(head);
  const same = (x, y) => JSON.stringify(x ?? null) === JSON.stringify(y ?? null);
  for (const k of DEP_FIELDS) if (!same(b[k], h[k])) reasons.push(`改了 package.json 的 ${k}`);
  for (const k of RISK_SCRIPTS) if (!same(b.scripts?.[k], h.scripts?.[k])) reasons.push(`改了 package.json 的 scripts.${k}`);
  return reasons;
}

// 拒绝时的下一步，按原因分开（problems 是给人看的句子，这里按句子开头认原因）
const HINTS = [
  [/^改了定义门槛的文件|^package\.json 的 scripts\./, "门槛文件和已有命令的改动单独开 chore/ PR，按 b 类两份评审通过后合并（docs/standards/pipeline.md §5.1）。"],
  [/^删了测试文件|^新增了跳过|^新增了关掉/, "恢复测试，去掉跳过、关 lint、@ts-nocheck / @ts-ignore 的写法（src/、server/ 里可以用 @ts-expect-error）；确实要放宽的，单独开 chore/ PR 按 b 类评审。"],
  [/^会关掉|会关掉别的 issue/, "改掉 PR 标题、正文或提交说明里的关闭关键字：票的 PR 只关自己那张票，任何 PR 都不关 #13。"],
  [/^base 是|^目标分支只能是/, "把 PR 的 base 改成目标分支（上线前 feature/v1，上线后 site）。"],
  [/^票的分支写了类别/, "PR 说明第一行改成「类别：票」。"],
  [/等产品负责人/, "先补决策简报（docs/standards/pipeline.md §5.2，检查：node scripts/check-owner-brief.mjs <正文文件>），再把简报原样贴给产品负责人。"],
];
/** 每条原因对应的下一步，去重、按 HINTS 的顺序。 */
export function rejectionHints(problems) {
  return HINTS.filter(([re]) => problems.some((p) => re.test(p))).map(([, hint]) => hint);
}

/**
 * PR 的类别：票 → ticket；不是票的 → a 或 b；改了 OWNER_FILES 的、观察者（obs/）的 b 类、票写了内容定稿的 → owner（不合并，等产品负责人）。
 * 不是票的拿不准一律按 b：没写类别、写的不是 a、改了门槛文件（GATE_FILES）、改或删了检查脚本（CHECK_FILES）
 * 或 package.json 已有的命令、削弱了测试（weakenings）、删了已有测试的断言（removedAssertions）、已有测试里加了提前 return（earlyReturns）。
 * 返回 { category, reasons, problems }。
 */
export function prCategory({ base, head, kind, ref = "", body = "", git }) {
  const fork = git("merge-base", base, head).trim();
  const status = diffPaths(git, `${fork}..${head}`);
  const owner = status.flatMap(({ path }) => OWNER_FILES.filter(({ re }) => re.test(path)).map(({ why }) => why(path)));
  if (owner.length) return { category: "owner", reasons: [], problems: owner };
  const declared = declaredCategory(body);
  if (kind === "ticket") {
    if (declared === "内容定稿") return { category: "owner", reasons: [], problems: ["类别是内容定稿：等产品负责人本人合并，合并就是定稿（pipeline.md §5.1）"] };
    if (declared === "a" || declared === "b") return { category: "ticket", reasons: [], problems: [`票的分支写了类别 ${declared}：票的 PR 写「类别：票」`] };
    return { category: "ticket", reasons: [], problems: [] };
  }
  const reasons = [];
  if (declared === null) reasons.push("PR 说明第一行没写类别");
  else if (declared !== "a") reasons.push(`PR 说明的类别是 ${declared}`);
  for (const { st, path } of status) {
    if (GATE_FILES.some((r) => r.test(path))) reasons.push(`改了门槛文件 ${path}`);
    else if (st !== "A" && CHECK_FILES.some((r) => r.test(path))) reasons.push(`改或删了检查脚本 ${path}`);
  }
  const show = (ref) => { try { return git("show", `${ref}:package.json`); } catch { return null; } };
  const bs = JSON.parse(show(fork) ?? "{}").scripts ?? {};
  const hs = JSON.parse(show(head) ?? "{}").scripts ?? {};
  for (const k of Object.keys(bs)) if (hs[k] !== bs[k]) reasons.push(`package.json 的 scripts.${k} 被改或被删`);
  reasons.push(...weakenings({ fork, head, git }), ...removedAssertions({ fork, head, git }), ...earlyReturns({ fork, head, git }));
  if (reasons.length && OBSERVER_BRANCH.test(ref)) {
    return { category: "owner", reasons, problems: [`观察者提的 b 类（${reasons.join("；")}）：等产品负责人合并（pipeline.md §5.1）`] };
  }
  return { category: reasons.length ? "b" : "a", reasons, problems: [] };
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const flag = (name) => {
    const i = args.indexOf(name);
    if (i < 0) return null;
    const [, v] = args.splice(i, 2);
    return v ?? "";
  };
  const prBase = flag("--pr-base");
  const target = flag("--target");
  const [base, head, ref, bodyFile = ""] = args;
  if (!base || !head || !ref || (prBase === null) !== (target === null)) {
    console.log("用法：node scripts/merge-gates.mjs <base-ref> <head-sha> <head 分支名> [正文文件] [--pr-base <分支> --target <分支>]");
    process.exit(2);
  }
  const { kind, ticket } = classifyBranch(ref);
  if (kind === "invalid") {
    console.log(`- 分支名不合规：${ref}。票用 feat/、fix/、content/ 加「<票号>-」开头，其余只能是 chore/ 或 obs/（docs/standards/pipeline.md §5）`);
    process.exit(1);
  }
  const git = (...a) => execFileSync("git", a, { encoding: "utf8", maxBuffer: 64 << 20 });
  const text = bodyFile ? readFileSync(bodyFile, "utf8") : "";
  const cat = prCategory({ base, head, kind, ref, body: text, git });
  const problems = [
    ...(target === null ? [] : checkBase(prBase, target)),
    ...cat.problems,
    ...checkGates({ base, head, kind, ticket, text, git }),
  ];
  const fork = git("merge-base", base, head).trim();
  const risk = riskHigh({ fork, head, git });
  if (risk.length) console.log(`要安全评审（同 risk:high）：${risk.join("；")}\nrisk=high`);
  if (problems.length) {
    console.log(problems.map((p) => `- ${p}`).join("\n"));
    for (const hint of rejectionHints(problems)) console.log(`下一步：${hint}`);
    if (cat.category === "owner") console.log("owner=yes");
    process.exit(1);
  }
  if (cat.reasons.length) console.log(`按 b 类处理：${cat.reasons.join("；")}`);
  console.log(`category=${cat.category}`);
}
