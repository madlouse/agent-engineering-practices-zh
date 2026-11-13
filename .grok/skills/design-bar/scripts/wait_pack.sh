#!/bin/sh
# 用法：wait_pack.sh 分支 提交 基准秒数 [远端]
# 等 CI 把「canvas pack for <提交>」推到证据分支。证据分支每次强推，所以用 ls-remote 和 + 引用规格取，不会因为不是快进而一直取不到。
# 每看到分支上换了新提交打一行（含「进行中：某步做完」）；拿到最终包退出 0；超过基准秒数的两倍还没拿到退出 2，这时去看最新包的 timings.tsv。
branch="$1"; sha="$2"; base="$3"; remote="${4:-origin}"
t0=$(date +%s); last=""
while :; do
  head=$(git ls-remote "$remote" "refs/heads/$branch" | cut -f1)
  if [ -n "$head" ] && [ "$head" != "$last" ]; then
    git fetch -q "$remote" "+refs/heads/$branch:refs/remotes/$remote/$branch" || echo "取不到 $branch"
    msg=$(git log -1 --format=%s "$head" 2>/dev/null)
    echo "$(date -u +%H:%M:%S) $msg"
    last="$head"
    got="${msg#canvas pack for }"
    case "$got" in *" · "*|"$msg") ;; *) case "$sha" in "$got"*) exit 0;; esac; case "$got" in "$sha"*) exit 0;; esac;; esac
  fi
  if [ $(( $(date +%s) - t0 )) -ge $(( base * 2 )) ]; then
    echo "超过 $(( base * 2 )) 秒还没拿到 $sha 的证据包：当卡住处理，看最新包的 timings.tsv"
    exit 2
  fi
  sleep 20
done
