// 等产品负责人合并的 PR 的「决策简报」检查（docs/standards/pipeline.md §5.1「要你合并时给什么」）。只读，不改任何东西。
// 用法：node scripts/check-owner-brief.mjs <PR 正文文件> [--question]
//   不带 --question：简报齐全退出码 0；不齐全逐条打印缺什么、退出码 1。
//   带 --question：只打印「要你判断什么」那一句（日报「等你合并」一栏用），没有就退出码 1。
// 合并脚本对 owner:merge 和判成 owner 类的 PR 拒绝时顺带跑它；reviewer、reviewer-b 核对简报属实；digest-writer 用 --question。
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

export const BRIEF_TITLE = "决策简报";
// 五项加「怎么回」，顺序就是简报里的顺序
export const ITEMS = ["要你判断什么", "为什么要你", "选项和后果", "我的建议和理由", "风险和怎么撤回", "怎么回"];
// §5.1 要人的几种情形；「为什么要你」必须落在其中一条
export const REASONS = /产品意图|钱|付费|费用|法律|难以?撤回|权限设置|观察者|内容定稿/;
// 只说「请审阅」这类话，等于没提问题
const EMPTY_ASK = /^(?:请|麻烦)?(?:你|您)?(?:帮忙)?(?:审阅|审核|评审|确认|核对|过目|看一下|看看|看下|批准|同意|合并|决定|判断|review|approve|lgtm)(?:一下)?(?:这个|本|此)?(?:pr|改动|修改|变更)?(?:吧|即可|就行)?$/i;
export const MAX_LINES = 30; // 一屏：超过的细节放到简报下面

const HEADING = /^#{1,6}\s+/;
const itemOf = (line) => {
  // 认「### 要你判断什么」「**要你判断什么**：…」「- 要你判断什么：…」三种写法
  const t = line.replace(HEADING, "").replace(/^[-*]\s+/, "").replace(/\*\*/g, "").trim();
  for (const key of ITEMS) {
    if (t === key || t.startsWith(key + "：") || t.startsWith(key + ":")) return { key, rest: t.slice(key.length).replace(/^[：:]\s*/, "") };
  }
  return null;
};

/** 简报：{ start, lines, items: { 项: 内容 } }；正文第一行是类别，之后第一个非空行必须是简报标题，否则 null。 */
export function parseBrief(body) {
  const lines = (body ?? "").split(/\r?\n/);
  let i = 1; // 第一行是「类别：…」
  while (i < lines.length && !lines[i].trim()) i++;
  if (i >= lines.length || lines[i].replace(HEADING, "").replace(/\*\*/g, "").trim() !== BRIEF_TITLE) return null;
  const start = i;
  const items = {};
  let cur = null;
  for (i = start + 1; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*(?:---+|\*\*\*+)\s*$/.test(line)) break; // 分隔线以下是细节
    const it = itemOf(line);
    if (it) { cur = it.key; items[cur] = it.rest ? [it.rest] : []; continue; }
    if (HEADING.test(line)) break; // 别的标题：简报结束
    if (cur) items[cur].push(line);
  }
  const text = Object.fromEntries(Object.entries(items).map(([k, v]) => [k, v.join("\n").trim()]));
  return { start, end: i, lines: lines.slice(start, i), items: text };
}

/** 「要你判断什么」那一句；没有简报或没写返回 null。 */
export function briefQuestion(body) {
  const q = parseBrief(body)?.items["要你判断什么"];
  return q ? q.split("\n")[0].trim() : null;
}

/** 缺什么（空数组 = 齐全）。 */
export function checkOwnerBrief(body) {
  const brief = parseBrief(body);
  if (!brief) return [`PR 说明最上面（第一行「类别：…」之后）没有「${BRIEF_TITLE}」标题`];
  const problems = [];
  const { items } = brief;
  for (const key of ITEMS) if (!items[key]) problems.push(`缺「${key}」，或者它是空的`);

  const q = items["要你判断什么"];
  if (q) {
    const bare = q.replace(/[\s。，、！？?!.,：:「」“”"'`*]/g, "");
    if (q.split("\n").filter((l) => l.trim()).length > 1) problems.push("「要你判断什么」要一句话");
    if (!bare || EMPTY_ASK.test(bare)) problems.push(`「要你判断什么」是空话（「${q}」）：写成一个是 / 否或二选一的问题`);
    else if (!/[？?]\s*$/.test(q.trim())) problems.push(`「要你判断什么」要写成问句，以问号结尾（「${q}」）`);
  }
  const why = items["为什么要你"];
  if (why && !REASONS.test(why)) problems.push("「为什么要你」没落在 §5.1 的任何一条（产品意图、钱、法律、难撤回、权限设置、观察者放宽、内容定稿）");
  const opts = items["选项和后果"];
  if (opts) {
    const n = opts.split("\n").filter((l) => /^\s*(?:[-*]|\d+[.、)]|[①②③④⑤]|[A-D][.、)])\s*\S/.test(l)).length;
    if (n < 2) problems.push("「选项和后果」至少列两个选项（一行一个）");
    if (!/不合并/.test(opts)) problems.push("「选项和后果」要写「不合并」会怎样");
  }
  const risk = items["风险和怎么撤回"];
  if (risk && !/撤回|回退|回滚|revert|恢复/i.test(risk)) problems.push("「风险和怎么撤回」没写怎么撤回");
  const reply = items["怎么回"];
  if (reply && !/合并\s*#|选项|编号/.test(reply)) problems.push("「怎么回」要写回什么：「合并 #N」或选项编号");

  if (brief.lines.some((l) => /^\s*```/.test(l))) problems.push("简报里有代码块：判断不该要读代码，代码放到简报下面");
  const used = brief.lines.filter((l) => l.trim()).length;
  if (used > MAX_LINES) problems.push(`简报 ${used} 行，超过一屏（${MAX_LINES} 行）：细节放到分隔线 --- 下面`);
  return problems;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const question = args.includes("--question");
  const file = args.find((a) => a !== "--question");
  if (!file) {
    console.log("用法：node scripts/check-owner-brief.mjs <PR 正文文件> [--question]");
    process.exit(2);
  }
  const body = readFileSync(file, "utf8");
  if (question) {
    const q = briefQuestion(body);
    if (!q) process.exit(1);
    console.log(q);
    process.exit(0);
  }
  const problems = checkOwnerBrief(body);
  if (problems.length) {
    console.log(`决策简报不齐全（docs/standards/pipeline.md §5.1「要你合并时给什么」）：\n${problems.map((p) => `- ${p}`).join("\n")}`);
    process.exit(1);
  }
  console.log("决策简报齐全");
}
