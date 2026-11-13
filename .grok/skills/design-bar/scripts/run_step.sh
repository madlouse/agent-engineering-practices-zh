#!/bin/sh
# 用法：run_step.sh 名称 上限秒数 卡住秒数 日志 命令…
# 跑一个可能很久的步骤：超过上限秒数停掉（退出码 124），日志超过卡住秒数没有新输出也停掉（退出码 125），
# 两种都在日志末尾写一句原因；用时追加到 $TIMINGS（不给就不记）。被调的脚本要每做完一块打一行进度，卡住检测才分得清慢和卡。
name="$1"; limit="$2"; stall="$3"; log="$4"; shift 4
t0=$(date +%s)
"$@" > "$log" 2>&1 &
pid=$!
code=""
while kill -0 "$pid" 2>/dev/null; do
  sleep 5
  now=$(date +%s)
  idle=$(( now - $(stat -c %Y "$log" 2>/dev/null || echo "$now") ))
  if [ $(( now - t0 )) -ge "$limit" ]; then code=124; why="超时：${limit} 秒内没跑完，被停掉"
  elif [ "$idle" -ge "$stall" ]; then code=125; why="卡住：${stall} 秒没有新输出，被停掉（最后一行在上面）"
  else continue; fi
  kill "$pid" 2>/dev/null; sleep 10; kill -9 "$pid" 2>/dev/null
  break
done
if [ -z "$code" ]; then wait "$pid"; code=$?; else wait "$pid" 2>/dev/null; echo "$why" >> "$log"; fi
dt=$(( $(date +%s) - t0 ))
[ -n "${TIMINGS:-}" ] && printf '%s\t%s\t%ss\t上限 %ss，卡住 %ss\n' "$name" "$code" "$dt" "$limit" "$stall" >> "$TIMINGS"
exit "$code"
