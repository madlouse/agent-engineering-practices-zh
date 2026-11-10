// 等产品负责人合并的 PR 的「决策简报」检查（docs/standards/pipeline.md §5.2）。只读，不改任何东西。
// 用法：node scripts/check-owner-brief.mjs <PR 正文文件> [--question]
//   不带 --question：简报合格退出码 0；不合格逐条打印缺什么、退出码 1。
//   带 --question：先查整份简报，合格才打印「要你判断什么」那一句（日报「等你合并」用）；不合格打印「简报不合格：…」、退出码 1。
// 脚本守住「不是空壳」的下限（每项有内容、问题点名了要定的事）；简报是否属实靠评审。
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

export const BRIEF_TITLE = "决策简报";
// 七项，顺序就是简报里的顺序
export const ITEMS = ["要你判断什么", "背景和事实", "为什么要你", "选项和后果", "我的建议和理由", "风险和怎么撤回", "怎么回"];
// §5.1 要人的几种情形；「为什么要你」必须肯定地落在其中一条
export const REASONS = /产品意图|钱|付费|费用|法律|难以?撤回|权限设置|观察者|内容定稿|上线合并|紧急修复/;
// 语气词：去掉以后再看问题还剩什么
const PARTICLES = /是否|要不要|可不可以|能不能|好不好|行不行|对不对|可以|能否|吗|呢|吧|么|嘛/g;
// 不点名决策对象的泛词：问题只剩这些就是空话
const GENERIC = /请|麻烦|帮忙|你|您|审阅|审核|评审|确认|核对|过目|看一下|看看|看下|批准|同意|通过|合并|决定|判断|一下|这个|本次|本|此|该|pr|改动|修改|变更|please|review|approve|merge|lgtm|ok/gi;
const PUNCT = /[\s。，、！？?!.,：:；;「」“”"'`*（）()\[\]【】\-—_/#]/g;
export const MIN_QUESTION = 10; // 去掉语气词后，问题至少这么多字
export const MIN_TEXT = 6; // 选项的后果、建议、风险和撤回至少这么多字
export const MAX_LINES = 30; // 一屏：行数
export const MAX_LINE = 200; // 一屏：单行长度
const len = (s) => [...s.replace(PUNCT, "")].length;

const HEADING = /^#{1,6}\s+/;
const itemOf = (line) => {
  // 认「### 要你判断什么」「**要你判断什么**：…」「- 要你判断什么：…」三种写法
  const t = line.replace(HEADING, "").replace(/^[-*]\s+/, "").replace(/\*\*/g, "").trim();
  for (const key of ITEMS) {
    if (t === key || t.startsWith(key + "：") || t.startsWith(key + ":")) return { key, rest: t.slice(key.length).replace(/^[：:]\s*/, "") };
  }
  return null;
};

/** 简报：{ lines, items: { 项: 内容 } }。先去掉 HTML 注释；第一行是类别，之后第一个非空行必须是简报标题，否则 null。 */
export function parseBrief(body) {
  const lines = (body ?? "").replace(/<!--[\s\S]*?-->/g, "").split(/\r?\n/);
  let i = 1; // 第一行是「类别：…」
  while (i < lines.length && !lines[i].trim()) i++;
  if (i >= lines.length || lines[i].replace(HEADING, "").replace(/\*\*/g, "").trim() !== BRIEF_TITLE) return null;
  const start = i;
  const items = {};
  let cur = null;
  let fence = null;
  for (i = start + 1; i < lines.length; i++) {
    const line = lines[i];
    const f = /^\s*(```|~~~)/.exec(line);
    if (f) fence = fence === f[1] ? null : fence ?? f[1];
    if (!fence && /^\s*(?:---+|\*\*\*+)\s*$/.test(line)) break; // 分隔线以下是细节
    const it = fence ? null : itemOf(line);
    if (it) { cur = it.key; items[cur] = it.rest ? [it.rest] : []; continue; }
    if (!fence && HEADING.test(line)) break; // 别的标题：简报结束
    if (cur) items[cur].push(line);
  }
  const text = Object.fromEntries(Object.entries(items).map(([k, v]) => [k, v.join("\n").trim()]));
  return { lines: lines.slice(start, i), items: text };
}

/** 问题有没有点名要决定的事：返回问题描述，没问题返回 null。 */
function askProblem(q) {
  if (q.split("\n").filter((l) => l.trim()).length > 1) return "「要你判断什么」要一句话";
  const noParticles = q.replace(PARTICLES, "");
  if (!len(noParticles.replace(GENERIC, ""))) return `「要你判断什么」是空话（「${q}」）：点名要决定的那件事，写成是 / 否或二选一的问题`;
  if (len(noParticles) < MIN_QUESTION) return `「要你判断什么」没点名要决定的事（「${q}」，去掉语气词后不到 ${MIN_QUESTION} 个字）`;
  if (!/[？?]\s*$/.test(q.trim())) return `「要你判断什么」要写成问句，以问号结尾（「${q}」）`;
  return null;
}

/** 缺什么（空数组 = 合格）。 */
export function checkOwnerBrief(body) {
  const brief = parseBrief(body);
  if (!brief) return [`PR 说明最上面（第一行「类别：…」之后）没有「${BRIEF_TITLE}」标题`];
  const problems = [];
  const { items } = brief;
  for (const key of ITEMS) if (!items[key]) problems.push(`缺「${key}」，或者它是空的`);

  const q = items["要你判断什么"];
  const ask = q && askProblem(q);
  if (ask) problems.push(ask);
  const why = items["为什么要你"];
  // 「不涉及钱」这类否定不算：去掉否定词到句末的部分再找
  if (why && !REASONS.test(why.replace(/(?:不涉及|不涉|不是|不算|没有|没|无|不|非|未)[^，。；：,;:\n]*/g, ""))) {
    problems.push("「为什么要你」没有肯定地落在 §5.1 的任何一条（产品意图、钱、法律、难撤回、权限设置、观察者放宽、内容定稿、上线合并、紧急修复）");
  }
  const opts = items["选项和后果"];
  if (opts) {
    const lines = opts.split("\n").filter((l) => /^\s*(?:[-*]|\d+[.、)]|[①②③④⑤]|[A-D][.、)])\s*\S/.test(l));
    if (lines.length < 2) problems.push("「选项和后果」至少列两个选项（一行一个）");
    if (!/不合并/.test(opts)) problems.push("「选项和后果」要写「不合并」会怎样");
    for (const l of lines) {
      const after = /[：:](.*)$/.exec(l)?.[1] ?? "";
      if (len(after) < MIN_TEXT) problems.push(`选项「${l.trim()}」要写成「选项：后果」，后果至少 ${MIN_TEXT} 个字`);
    }
  }
  for (const key of ["我的建议和理由", "风险和怎么撤回"]) {
    if (items[key] && len(items[key]) < MIN_TEXT) problems.push(`「${key}」至少 ${MIN_TEXT} 个字`);
  }
  const risk = items["风险和怎么撤回"];
  if (risk && !/撤回|回退|回滚|revert|恢复/i.test(risk)) problems.push("「风险和怎么撤回」没写怎么撤回");
  const reply = items["怎么回"];
  if (reply && !/合并\s*#|选项|编号/.test(reply)) problems.push("「怎么回」要写回什么：「合并 #N」或选项编号");

  if (brief.lines.some((l) => /^\s*(?:```|~~~)/.test(l) || /^(?: {4}|\t)\S/.test(l))) problems.push("简报里有代码块（``` / ~~~ / 缩进）：判断不该要读代码，代码放到简报下面");
  const used = brief.lines.filter((l) => l.trim()).length;
  if (used > MAX_LINES) problems.push(`简报 ${used} 行，超过一屏（${MAX_LINES} 行）：细节放到分隔线 --- 下面`);
  const long = brief.lines.find((l) => [...l].length > MAX_LINE);
  if (long) problems.push(`简报里有一行超过 ${MAX_LINE} 字：拆短，细节放到分隔线 --- 下面`);
  return problems;
}

/** 合格的简报里「要你判断什么」那一句；不合格返回 null。 */
export function briefQuestion(body) {
  if (checkOwnerBrief(body).length) return null;
  return parseBrief(body).items["要你判断什么"].trim();
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
  const problems = checkOwnerBrief(body);
  if (question) {
    if (problems.length) {
      console.log(`简报不合格：${problems[0]}`);
      process.exit(1);
    }
    console.log(briefQuestion(body));
    process.exit(0);
  }
  if (problems.length) {
    console.log(`决策简报不合格（docs/standards/pipeline.md §5.2）：\n${problems.map((p) => `- ${p}`).join("\n")}`);
    process.exit(1);
  }
  console.log("决策简报合格");
}
