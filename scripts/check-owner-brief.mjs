// 等产品负责人合并的 PR 的「决策简报」检查（docs/standards/pipeline.md §5.2）。只读，不改任何东西。
// 用法：node scripts/check-owner-brief.mjs <PR 正文文件> [--question]
//   不带 --question：简报合格退出码 0；不合格逐条打印缺什么、退出码 1。
//   带 --question：先查整份简报，合格才打印「要你判断什么」那一句（日报「等你合并」用）；不合格打印「简报不合格：…」、退出码 1。
// 脚本守住「不是空壳」的下限（每项有内容、问题点名了要定的事）；简报是否属实靠评审。
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const BRIEF_TITLE = "决策简报";
// 七项，顺序就是简报里的顺序
export const ITEMS = ["要你判断什么", "背景和事实", "为什么要你", "选项和后果", "我的建议和理由", "风险和怎么撤回", "怎么回"];
// §5.1 要人的几种情形；「为什么要你」必须肯定地落在其中一条
export const REASONS = /产品意图|钱|付费|费用|法律|难以?撤回|权限设置|观察者|内容定稿|上线合并|紧急修复/g;
// 语气词和不表态的口头话：去掉以后再看还剩什么
const PARTICLES = /是否|要不要|可不可以|能不能|好不好|行不行|对不对|可以|能否|觉得|怎么样|怎样|整体上|整体|需要|现在|拍板|没问题|吗|呢|吧|么|嘛|呀|啊|哦|就/g;
// 不点名决策对象的泛词：合并的动作、目的地（分支名、到、进）、对象（这个 PR）、泛指（上面说的那件事）
const GENERIC = /请|麻烦|帮忙|产品负责人|你|您|我|审阅|审核|评审|确认|核对|过目|看一下|看看|看下|批准|同意|接受|通过|不合并|合并|决定|判断|一下|这个|这次|这样|那样|本次|本|此|该|上面|下面|说的|那件事|这件事|东西|方案|改动|修改|变更|集成分支|分支|把|进|入|到|并|按|#\d+|feature\/v\d+|\bpr\b|\b(?:site|main|pull|request|please|review|approve|merge|merged|lgtm|ok|okay|is|this|it|to|should|we|can|you|now|take|look|at|a|the)\b/gi;
// 各项自己的套话：去掉以后才算内容
const FILLER = {
  "我的建议和理由": /建议|选项?|没有问题|如上所述|如上|所述|理由/g,
  "风险和怎么撤回": /风险|撤回|很低|低|很小|小|没有|无|可|回退|回滚|恢复|revert/gi,
  "选项和后果": /会|被|不|怎样|怎么样|选了|影响/g,
};
const PUNCT = /[\s。，、！？?!.,：:；;「」“”"'`*（）()[\]【】\-—_/#…]/g;
// 每项去掉语气词、泛词、套话后至少这么多字
export const MIN = { "要你判断什么": 10, "背景和事实": 10, "为什么要你": 6, "我的建议和理由": 6, "风险和怎么撤回": 4, "选项和后果": 4 };
export const MAX_LINES = 30; // 一屏：行数
export const MAX_LINE = 200; // 一屏：单行长度
const len = (s) => [...s.replace(PUNCT, "")].length;
const substance = (s, key) => len(s.replace(PARTICLES, "").replace(GENERIC, "").replace(REASONS, "").replace(FILLER[key] ?? /$^/, ""));
// 没填：整项包在括号里（模板的占位）或只写了「见下」这类话
const placeholder = (s) => /^[（(][\s\S]*[）)][。.]?$/.test(s.trim()) || /^(?:见下面?|见上面?|同上|如上|略|无|待补|tbd|todo|n\/a)[。.]?$/i.test(s.trim());

const HEADING = /^#{1,6}\s+/;
const itemOf = (line) => {
  // 认「### 要你判断什么」「**要你判断什么**：…」「- 要你判断什么：…」三种写法
  const t = line.replace(HEADING, "").replace(/^[-*]\s+/, "").replace(/\*\*/g, "").trim();
  for (const key of ITEMS) {
    if (t === key || t.startsWith(key + "：") || t.startsWith(key + ":")) return { key, rest: t.slice(key.length).replace(/^[：:]\s*/, "") };
  }
  return null;
};

/** 简报：{ lines, items: { 项: 内容 } }。第一行是类别，之后第一个非空行必须是简报标题，否则 null。raw 为 false 时先去掉 HTML 注释。 */
export function parseBrief(body, { raw = false } = {}) {
  const src = body ?? "";
  const lines = (raw ? src : src.replace(/<!--[\s\S]*?-->/g, "")).split(/\r?\n/);
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
  if (!substance(q, "要你判断什么")) return `「要你判断什么」是空话（「${q}」）：点名要决定的那件事，写成是 / 否或二选一的问题`;
  if (substance(q, "要你判断什么") < MIN["要你判断什么"]) return `「要你判断什么」没点名要决定的事（「${q}」，去掉语气词、合并和分支这类泛词后不到 ${MIN["要你判断什么"]} 个字）`;
  if (!/[？?]\s*$/.test(q.trim())) return `「要你判断什么」要写成问句，以问号结尾（「${q}」）`;
  return null;
}

/** 「为什么要你」去掉带否定的分句（「不涉及钱」「与法律无关」）后，还肯定地命中 §5.1 的一条吗。 */
const affirmsReason = (why) =>
  why.split(/[，。；：,;:\n]/).filter((c) => !/[不没无非未别]/.test(c)).some((c) => new RegExp(REASONS.source).test(c));

/** 缺什么（空数组 = 合格）。脚本只守「不是空壳」的下限，是否属实靠评审（pipeline.md §5.2）。 */
export function checkOwnerBrief(body) {
  const brief = parseBrief(body);
  if (!brief) return [`PR 说明最上面（第一行「类别：…」之后）没有「${BRIEF_TITLE}」标题`];
  const problems = [];
  const items = Object.fromEntries(Object.entries(brief.items).filter(([, v]) => !placeholder(v)));
  for (const key of ITEMS) if (!items[key]) problems.push(`缺「${key}」，或者它是空的、还是模板的占位`);

  const q = items["要你判断什么"];
  const ask = q && askProblem(q);
  if (ask) problems.push(ask);
  const fact = items["背景和事实"];
  if (fact && substance(fact, "背景和事实") < MIN["背景和事实"]) problems.push(`「背景和事实」要一句完整的陈述（改了什么、依据什么事实），至少 ${MIN["背景和事实"]} 个字`);
  const why = items["为什么要你"];
  if (why && !affirmsReason(why)) {
    problems.push("「为什么要你」没有肯定地落在 §5.1 的任何一条（产品意图、钱、法律、难撤回、权限设置、观察者放宽、内容定稿、上线合并、紧急修复）；「不涉及钱」「与法律无关」这类否定不算");
  } else if (why && substance(why, "为什么要你") < MIN["为什么要你"]) {
    problems.push(`「为什么要你」除了落在哪一条，还要一句具体理由（至少 ${MIN["为什么要你"]} 个字）`);
  }
  const opts = items["选项和后果"];
  if (opts) {
    const lines = opts.split("\n").filter((l) => /^\s*(?:[-*]|\d+[.、)]|[①②③④⑤]|[A-D][.、)])\s*\S/.test(l));
    if (lines.length < 2) problems.push("「选项和后果」至少列两个选项（一行一个）");
    if (!/不合并/.test(opts)) problems.push("「选项和后果」要写「不合并」会怎样");
    const results = [];
    for (const l of lines) {
      const after = /[：:](.*)$/.exec(l)?.[1] ?? "";
      results.push(after.replace(PUNCT, ""));
      if (placeholder(after) || substance(after, "选项和后果") < MIN["选项和后果"]) {
        problems.push(`选项「${l.trim()}」要写成「选项：后果」，后果去掉合并、不合并这类词后至少 ${MIN["选项和后果"]} 个字`);
      }
    }
    if (new Set(results).size < results.length) problems.push("「选项和后果」里有两个选项的后果一样");
  }
  for (const key of ["我的建议和理由", "风险和怎么撤回"]) {
    if (items[key] && substance(items[key], key) < MIN[key]) problems.push(`「${key}」去掉套话后至少 ${MIN[key]} 个字`);
  }
  const risk = items["风险和怎么撤回"];
  if (risk && !/撤回|回退|回滚|revert|恢复/i.test(risk)) problems.push("「风险和怎么撤回」没写怎么撤回");
  const reply = items["怎么回"];
  if (reply && !/合并\s*#\d+|选项\s*[「"']?\s*[0-9①-⑤]|编号\s*[「"']?\s*[0-9①-⑤]|[「"']\s*[0-9①-⑤]\s*[」"']/.test(reply)) {
    problems.push("「怎么回」要写真实的回复：「合并 #PR 号」（不是模板的 #N）或选项编号");
  }

  const raw = parseBrief(body, { raw: true });
  if (raw && raw.lines.some((l) => l.includes("<!--"))) problems.push("简报里有 HTML 注释：产品负责人看不到的内容不放进简报");
  if (brief.lines.some((l) => /^\s*(?:```|~~~)/.test(l) || /^(?: {4}|\t)\S/.test(l) || /<\/?(?:pre|code)\b/i.test(l))) {
    problems.push("简报里有代码块（``` / ~~~ / 缩进 / <pre>）：判断不该要读代码，代码放到简报下面");
  }
  const used = brief.lines.filter((l) => l.trim()).length;
  if (used > MAX_LINES) problems.push(`简报 ${used} 行，超过一屏（${MAX_LINES} 行）：细节放到分隔线 --- 下面`);
  if (brief.lines.some((l) => [...l].length > MAX_LINE)) problems.push(`简报里有一行超过 ${MAX_LINE} 字：拆短，细节放到分隔线 --- 下面`);
  return problems;
}

/** 合格的简报里「要你判断什么」那一句；不合格返回 null。 */
export function briefQuestion(body) {
  if (checkOwnerBrief(body).length) return null;
  return parseBrief(body).items["要你判断什么"].trim();
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
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
