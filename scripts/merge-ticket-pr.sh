#!/usr/bin/env bash
# 合并一个 PR 进主站的集成分支（docs/standards/pipeline.md §5.1「谁合并」、§8 第 0 阶段）。流水线里唯一的合并入口：云端会话只放行本脚本。
# 复用 Veli scripts/merge-ticket-pr.sh，按主站改：
# - 目标分支：GitHub 上有 feature/v1 时只合并进 feature/v1（上线前）；feature/v1 删掉以后只合并进 site（上线后）。
#   上线前 feature/v1 → site 那一次由产品负责人确认，本脚本不做。
# - 只合并：base 是目标分支（base 是 site 的上线前一律拒绝）、开着、不是草稿、带 agent:pass、不带 agent:hold / agent:rework / owner:merge 的 PR；
# - 类别（merge-gates.mjs 的 prCategory）：票；不是票的 a 类；b 类（PR 说明写 b、没写类别、改了门槛文件、检查脚本或已有命令、削弱了测试）；
#   改了权限设置（.claude/settings*.json）或 docs/standards/observer.md 的、观察者 obs/ 分支的 b 类，一律不合并，等产品负责人。
# - 评审结论针对当前头提交：content/ 分支要 kind=content；b 类要 kind=general 和 kind=general-b 两份；其余要 kind=general；
#   risk:high 另要 kind=security 和 security:pass；改依赖、锁文件、.npmrc、生命周期脚本、migrations/site/、site:migrate 的（merge-gates.mjs 输出 risk=high）同样要。
# - 带 owner:merge 或判成 owner 类的，拒绝时顺带跑决策简报检查（check-owner-brief.mjs，取目标分支上的版本），缺简报就提示先补。
#   结论只认对应评审角色经 Claude 应用写的、没编辑过的 vc-review 标记（scripts/review-markers.mjs）。头提交一变，旧结论自动失效。
# - 票的 PR（feat/、fix/、content/）不能改门槛文件（scripts/merge-gates.mjs）；判定库、门槛和检查命令一律取目标分支上的版本。
# - 合并前在「PR + 最新目标分支」上重跑 §7 的检查：npm test、check:terms、check:vague、check:voice；装了 tsc、eslint 时也跑类型检查和 lint，
#   没装时以已确认 READY 的预览构建为准（构建命令里有 tsc --noEmit && eslint .）。
# 威胁模型同 Veli：本地门槛只防 Agent 出错、走捷径；不防有人篡改本地环境，那部分交给 GitHub 规则集。
set -euo pipefail
cd "$(dirname "$0")/.."
body_file=""; brief_file=""; lib_dir=""; comments_file=""; work=""; ROOT="$PWD"
trap 'cd "$ROOT"; if [ -n "$work" ]; then git worktree remove --force "$work" >/dev/null 2>&1 || rm -rf "$work"; fi; git worktree prune >/dev/null 2>&1; rm -rf "$lib_dir"; rm -f "$body_file" "$brief_file" "$comments_file" "$comments_file.n"' EXIT
REPO="repos/madlouse/velicoach"
PR="${1:?用法：bash scripts/merge-ticket-pr.sh <PR 号>}"
[[ "$PR" =~ ^[0-9]+$ ]] || { echo "PR 号要是数字"; exit 1; }
fail() { echo "不合并 #$PR：$1"; exit 1; }

# 目标分支：feature/v1 在就是它，GitHub 明确回 404 才算上线后改用 site；别的错误就停
if out=$(gh api "$REPO/git/ref/heads/feature/v1" --jq .object.sha 2>&1); then TARGET=feature/v1; remote_sha=$out
elif [[ "$out" == *"HTTP 404"* ]]; then TARGET=site; remote_sha=$(gh api "$REPO/git/ref/heads/site" --jq .object.sha) || fail "读不到 site"
else fail "读不到 feature/v1 的状态：$out"; fi

info=$(gh api "$REPO/pulls/$PR")
field() { node -e "const p=JSON.parse(process.argv[1]);console.log($1)" "$info"; }
base=$(field 'p.base.ref'); state=$(field 'p.state'); draft=$(field 'p.draft'); sha=$(field 'p.head.sha'); head=$(field 'p.head.ref')
labels=$(field 'p.labels.map(l=>l.name).join(",")')
has() { [[ ",$labels," == *",$1,"* ]]; }

# 分支名只允许 A-Z a-z 0-9 . _ / -，不能以 - 开头（最后删分支的 DELETE 和 git 参数都靠它，Veli 安全评审）
[[ "$head" =~ ^[A-Za-z0-9._/][A-Za-z0-9._/-]*$ ]] || fail "分支名 $head 不合规：只允许字母、数字和 . _ / -，不能以 - 开头"
git fetch -q origin -- "$TARGET" "$head" || fail "取不到 origin/$TARGET 或分支 $head"
# 信任根只用一个 sha：后面一律用 $tgt，再和 GitHub 上的核对一次
tgt=$(git rev-parse --verify -q "refs/remotes/origin/$TARGET^{commit}") || fail "本地没有 origin/$TARGET"
[ "$tgt" = "$remote_sha" ] || fail "本地取到的 $TARGET（${tgt:0:7}）和 GitHub 上的不一致"
# 本地被改过的门槛脚本不能拿来合并
gate_paths=(scripts/merge-ticket-pr.sh scripts/merge-gates.mjs scripts/review-markers.mjs)
git diff --quiet "$tgt" -- "${gate_paths[@]}" || fail "本地门槛脚本和 $TARGET 不一致，先切回最新的 $TARGET 再合并"
# 判定库和门槛取目标分支上的版本（PR 改不了它们）；取不到就停，不退回本地文件
lib_dir=$(mktemp -d)
for f in review-markers.mjs merge-gates.mjs; do
  git show "$tgt:scripts/$f" > "$lib_dir/$f" || fail "$TARGET 上没有 scripts/$f"
done
# 正文放前面，第一行是「类别：…」；正文为空时第一行是空行，不拿标题当类别
body_file=$(mktemp); { field 'p.body||""'; field 'p.title||""'; } > "$body_file"
# 等产品负责人的 PR：核对决策简报（pipeline.md §5.2），只读正文、不拼标题。只提示，不改变拒绝
brief_file=$(mktemp); field 'p.body||""' > "$brief_file"
owner_brief() {
  if ! git show "$tgt:scripts/check-owner-brief.mjs" > "$lib_dir/check-owner-brief.mjs" 2>/dev/null; then
    echo "（$TARGET 上还没有 scripts/check-owner-brief.mjs，没核对决策简报）"; return 0
  fi
  if node "$lib_dir/check-owner-brief.mjs" "$brief_file"; then
    echo "下一步：把 PR 说明里的决策简报原样贴给产品负责人（对话或 #13），不要只说「等你合并」。"
  else
    echo "下一步：先补决策简报，再请产品负责人合并。"
  fi
}
[ "$state" = "open" ] || fail "状态是 $state"
[ "$draft" = "false" ] || fail "还是草稿"
has owner:merge && { owner_brief; fail "带着 owner:merge：等产品负责人本人合并（pipeline.md §5.1）"; }
has agent:pass || fail "没有 agent:pass（冷评审没通过）"
has agent:hold && fail "带着 agent:hold"
has agent:rework && fail "同时带着 agent:rework：以最新一次评审为准，先由评审换好标签"

# 读全部评论：云端代理拒绝 --paginate 的第 2 页，自己按 page= 翻页，读失败就拒绝
comments_file=$(mktemp); echo '[]' > "$comments_file"
page=1
while :; do
  chunk=$(gh api "$REPO/issues/$PR/comments?per_page=100&page=$page") || fail "读不到 PR 评论（第 $page 页）"
  printf '%s' "$chunk" | node -e 'const fs=require("fs");const f=process.argv[1];let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{const a=JSON.parse(fs.readFileSync(f,"utf8"));const b=JSON.parse(d);fs.writeFileSync(f,JSON.stringify(a.concat(b)));process.stdout.write(String(b.length))})' "$comments_file" > "$comments_file.n"
  [ "$(cat "$comments_file.n")" -lt 100 ] && break
  page=$((page + 1))
done
# 改动范围、base 和类别
gates_out=$(node "$lib_dir/merge-gates.mjs" "$tgt" "$sha" "$head" "$body_file" --pr-base "$base" --target "$TARGET") || {
  printf '%s\n' "$gates_out" | grep -v '^owner=yes$'
  printf '%s\n' "$gates_out" | grep -qx 'owner=yes' && owner_brief
  fail "改动范围、base 或类别不合规（见上）"
}
category=$(printf '%s\n' "$gates_out" | sed -n 's/^category=//p' | tail -1)
[[ "$category" =~ ^(ticket|a|b)$ ]] || fail "读不懂类别：$gates_out"
printf '%s\n' "$gates_out" | grep -v -e '^category=' -e '^risk=high$' || true
# 要安全评审：带 risk:high 标签，或改了依赖、锁文件、订阅库迁移、site:migrate（两者同效）
risk_high=false
has risk:high && risk_high=true
printf '%s\n' "$gates_out" | grep -qx 'risk=high' && risk_high=true
if $risk_high; then
  has security:pass || fail "要独立安全评审（risk:high 或改了依赖、迁移，见上），还没有 security:pass。下一步：派一个 security-reviewer 子 Agent，并给 PR 打 risk:high"
  has security:rework && fail "带着 security:rework"
fi
markers() { node --input-type=module -e 'const [lib,fn,...a]=process.argv.slice(1);const {pathToFileURL}=await import("node:url");const m=await import(pathToFileURL(lib).href);console.log(m[fn](...a))' "$lib_dir/review-markers.mjs" "$@"; }
kinds=$(markers requiredReviewKinds "$head" "$category") || fail "读不懂评审种类"
for kind in $kinds; do
  verdict=$(markers reviewVerdictFromFile "$comments_file" "$sha" "$kind") || fail "读不懂评审结论标记"
  [[ "$verdict" != locked:* ]] || fail "评论 ${verdict#locked:} 带结论标记又被编辑过：这条会锁住整个 PR，要解开就删掉那条评论（DELETE $REPO/issues/comments/<id>），再重新评审"
  [ "$verdict" = "pass" ] || fail "类别 $category：没有针对头提交 ${sha:0:7} 的 kind=$kind 评审通过记录（要 $kinds 各一份；只认对应评审角色经 Claude 应用写的、没编辑过的 vc-review 标记，同一提交上有 rework 就是 rework；现在是 $verdict）。下一步：派新的 $([ "$kind" = general-b ] && echo reviewer-b || echo 评审) 评这个头提交"
done
if $risk_high; then
  v_security=$(markers reviewVerdictFromFile "$comments_file" "$sha" security) || fail "读不懂安全评审结论标记"
  [ "$v_security" = "pass" ] || fail "risk:high：没有针对头提交 ${sha:0:7} 的 kind=security 通过记录（现在是 $v_security）。下一步：派一个 security-reviewer 子 Agent 评这个头提交"
fi
# 预览部署：由调用方用 Vercel 连接器确认 PR 头提交的预览部署 READY 后，用 PREVIEW_READY_SHA=<该提交> 声明
[ "${PREVIEW_READY_SHA:-}" = "$sha" ] || fail "没有确认 PR 头 ${sha:0:7} 的 Vercel 预览部署 READY（先查，再用 PREVIEW_READY_SHA=$sha 调用）"

echo "▶ 在 PR #$PR（$head@${sha:0:7}，类别 $category）+ 最新 $TARGET 上重跑检查"
# 检查命令取自目标分支的 package.json，不用 PR 自己的版本
base_script() { git show "$tgt:package.json" | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{const v=JSON.parse(d).scripts[process.argv[1]];if(!v)process.exit(1);console.log(v)})' "$1"; }
checks=()
for s in test check:terms check:vague check:voice; do
  cmd=$(base_script "$s") || fail "$TARGET 的 package.json 里没有 $s"
  checks+=("$cmd")
done
work=$(mktemp -d)
git worktree add -q --detach "$work" "$sha"
# 每一步单独判断退出码：子 shell 放在 `|| fail` 左边时 set -e 不生效
cd "$work"
git merge -q --no-edit "$tgt" || fail "和 $TARGET 有冲突，先在分支上解决；推上去后头提交变了，要重新评审"
[ -d "$ROOT/node_modules" ] || fail "仓库根目录没有 node_modules：先 npm install --no-audit --no-fund，不能在缺依赖时跑门槛"
ln -s "$ROOT/node_modules" node_modules
export PATH="$PWD/node_modules/.bin:$PATH"
for c in "${checks[@]}"; do bash -c "$c" || fail "检查没过：$c（命令取自 $TARGET）"; done
if [ -x node_modules/.bin/tsc ] && [ -x node_modules/.bin/eslint ]; then
  tsc --noEmit || fail "类型检查没过"
  eslint . || fail "lint 没过"
else
  echo "（本地没装 tsc、eslint：类型检查和 lint 以已确认 READY 的预览构建为准）"
fi
cd "$ROOT"

echo "▶ 合并"
gh api -X PUT "$REPO/pulls/$PR/merge" -f merge_method=merge -f sha="$sha" --jq '.message'
gh api -X DELETE "$REPO/git/refs/heads/$head" >/dev/null 2>&1 && echo "✓ 已删分支 $head" || echo "（删分支 $head 没成功，留给清理）"
echo "✓ #$PR 已合并进 $TARGET。接下来：确认合并提交的预览部署 READY；票是否已关；写交接评论（<!-- vc-handoff -->）。"
