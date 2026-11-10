// vc-review 结论标记的判定。合并脚本从集成分支取本文件的版本来调 reviewVerdictFromFile，PR 改不了它。
// 复用 Veli scripts/lib/review-markers.ts（安全评审 F3、S4）：只数同时满足三条的评论——
// 1. 第一行是这个种类对应的评审角色行（ROLE_OF）；
// 2. 经 Claude 应用写的（performed_via_github_app.slug === 'claude'）；
// 3. 没编辑过（updated_at === created_at）。
// 一条评论里有多个标记、或标记的 kind 和角色对不上，整条作废。
// 同一个 sha 上只要有一条有效的 rework，就按 rework 算，后来的 pass 盖不过：评审要翻案，推新提交或由产品负责人合并。
// 经 Claude 应用写、含标记名、又编辑过的评论锁住整个 PR（不分 sha、不分种类），推新提交也解不开；要解开就删掉那条评论。
import { readFileSync } from "node:fs";

// 角色名和 .claude/agents/ 里各评审写的首行一致（docs/standards/pipeline.md §3、§5）
// general-b：不是票的 b 类 PR 的第二份评审，由不同模型的 reviewer-b 写（pipeline.md §5.1）
export const ROLE_OF = { general: "评审", "general-b": "评审B", content: "内容评审", security: "安全评审" };
export const KINDS = Object.keys(ROLE_OF);

const MARKER = /^<!-- vc-review kind=(general-b|general|content|security) verdict=(pass|rework) sha=([0-9a-f]{40}) -->$/;
// 数「像标记的东西」用宽松的写法：写坏的第二个标记也算多个，整条作废
const LOOSE = /vc-review/g;

const fromClaude = (c) => c.performed_via_github_app?.slug === "claude";
const edited = (c) => c.updated_at !== c.created_at;

function parse(c) {
  if (!fromClaude(c)) return null;
  if (Number.isNaN(Date.parse(c.created_at ?? ""))) return null;
  const body = c.body ?? "";
  const lines = body.split(/\r?\n/).map((l) => l.trim());
  const role = /^<!-- vc-bot role=(\S+) -->$/.exec(lines[0])?.[1];
  if ((body.match(LOOSE) ?? []).length !== 1) return null;
  const m = MARKER.exec(lines.find((l) => l.includes("vc-review")) ?? "");
  if (!m) return null;
  const kind = m[1];
  if (ROLE_OF[kind] !== role) return null;
  return { kind, verdict: m[2], sha: m[3] };
}

/** 锁住整个 PR 的评论：经 Claude 应用写、含标记名、又编辑过的。 */
export function lockingComments(comments) {
  return comments.filter((c) => fromClaude(c) && edited(c) && (c.body ?? "").includes("vc-review"));
}

/** 头提交 sha 上该种类评审的结论：pass / rework；没有有效结论返回 null。 */
export function reviewVerdict(comments, sha, kind) {
  if (lockingComments(comments).length > 0) return "rework";
  const mine = comments.map(parse).filter((p) => p && p.kind === kind && p.sha === sha);
  if (mine.length === 0) return null;
  return mine.some((p) => p.verdict === "rework") ? "rework" : "pass";
}

/** 合并脚本的入口：返回 pass / rework / none，被编辑过的评论锁住时返回 locked:<评论 id>；参数不对就抛错。 */
export function reviewVerdictFromFile(file, sha, kind) {
  if (!/^[0-9a-f]{40}$/.test(sha)) throw new Error(`sha 格式不对：${sha}`);
  if (!KINDS.includes(kind)) throw new Error(`评审种类只能是 ${KINDS.join(" / ")}：${kind}`);
  const comments = JSON.parse(readFileSync(file, "utf8"));
  if (!Array.isArray(comments)) throw new Error("评论 JSON 不是数组");
  const locked = lockingComments(comments);
  if (locked.length > 0) return `locked:${locked.map((c) => String(c.id ?? "?")).join(",")}`;
  return reviewVerdict(comments, sha, kind) ?? "none";
}

/**
 * 要哪几种评审（空格分隔，合并脚本逐个核对）：content/ 分支要 content；不是票的 b 类要 general 和 general-b；其余要 general。
 * category 是 merge-gates.mjs 的 prCategory 结果：ticket / a / b。
 */
export function requiredReviewKinds(headRef, category) {
  if (!["ticket", "a", "b"].includes(category)) throw new Error(`类别只能是 ticket / a / b：${category}`);
  if (/^content\//.test(headRef)) return "content";
  return category === "b" ? "general general-b" : "general";
}
