#!/bin/bash
# 给每块页面画板截一组标准图（改动前后比较用）。用法：shots.sh <画板目录> <canvas.css 的绝对路径> <输出目录>（输出目录放在仓库外面，截图不进仓库）
# 每块：1440 浅色、1440 深色、820、390、390 英文；另加几种状态（看清的人机协作、单条开发日志、页面状态各页、订阅关）。
export PYTHONDONTWRITEBYTECODE=1
P=$1; CSS=$2; OUT=$3
U=$(cd "$(dirname "$0")/.." && pwd)
R=$(cd "$U/../../../.." && pwd)/.grok/skills/design-bar/scripts/render_dc.py
mkdir -p "$OUT/tmp"
shot() {  # 画板名 输出名 宽x高 其余参数
  local b=$1 name=$2 size=$3; shift 3
  local tmp="$OUT/tmp/$b.$$.$RANDOM.dc.html"
  sed -e "s#/_blob/2d0ccacf7377c5a050e285f270f25ffd#file://$CSS#" -e "s#/_blob/26c007f478ecf5fa646eda60cbc23992#file://$U/canvas.js#" "$P/$b.dc.html" > "$tmp"
  python3 $R "$tmp" "$OUT/$name.png" --size $size --full --still "$@" >/dev/null 2>"$OUT/tmp/$name.err" || echo "失败 $name: $(tail -1 "$OUT/tmp/$name.err")"
  rm -f "$tmp"
}
std() {  # 画板名 [额外 props 的 JSON 片段，开头带逗号]
  local b=$1 x=$2 tag=$3
  shot $b "$b$tag-1440-light" 1440x900 --props "{\"theme\":\"浅色\"$x}" &
  shot $b "$b$tag-1440-dark" 1440x900 --props "{\"theme\":\"深色\"$x}" &
  shot $b "$b$tag-820" 820x1180 --props "{\"theme\":\"浅色\"$x}" &
  shot $b "$b$tag-390" 390x844 --props "{\"theme\":\"浅色\"$x}" &
  shot $b "$b$tag-390-en" 390x844 --props "{\"theme\":\"浅色\",\"lang\":\"English\"$x}" &
  wait
}
for b in Main Mind Learn Article About States Build Project Body Controls; do std $b; done
std Mind ',"line":"人机协作（/mind/collaboration）"' -collab
std Article ',"kind":"开发日志"' -log
std Main ',"subscribeGate":"关"' -rss
# 「开始训练」展开：真实的组合是悬停站稳一侧（倾斜 62:38）加展开，只展开这一个浮层；订阅条展开另出一张
shot Main Main-open-1440 1440x900 --props '{"theme":"浅色","start":"展开"}' --state '{"lean":"body"}' &
shot Main Main-open-en-1440 1440x900 --props '{"theme":"浅色","start":"展开","lang":"English"}' --state '{"lean":"body"}' &
shot Main Main-sub-error-1440 1440x900 --props '{"theme":"浅色","subscribe":"格式不对"}' &
shot Main Main-focus-orb-1440 1440x900 --props '{"theme":"浅色","focus":"接缝上的圆"}' &
shot Main Main-390x664 390x664 --props '{"theme":"浅色"}' &
shot Mind Mind-expand-1440 1440x900 --props '{"theme":"浅色","expand":"展开一条"}' &
shot Mind Mind-expand-390 390x844 --props '{"theme":"浅色","expand":"展开一条"}' &
shot Mind Mind-load加载失败-1440 1440x900 --props '{"theme":"浅色","load":"加载失败"}' &
shot Mind Mind-network离线-390 390x844 --props '{"theme":"浅色","network":"离线"}' &
shot Main Main-en-1440 1440x900 --props '{"theme":"浅色","lang":"English"}' &
shot Mind Mind-en-1440-dark 1440x900 --props '{"theme":"深色","lang":"English"}' &
shot Article Article-en-1440 1440x900 --props '{"theme":"浅色","lang":"English"}' &
shot Article Article-sticky-1440 1440x900 --props '{"theme":"浅色","nav":"吸顶"}' &
shot Body Body-open-1440 1440x900 --props '{"theme":"浅色","startMenu":"展开"}' &
wait
for pg in 加载中 "加载超过 10 秒" 内容加载失败 视频无法播放 文章暂无英文版 订阅失败 网络断开; do
  n=$(echo "$pg" | tr -d ' ')
  shot States "States-$n-1440" 1440x900 --props "{\"theme\":\"浅色\",\"page\":\"$pg\"}" &
  shot States "States-$n-390" 390x844 --props "{\"theme\":\"浅色\",\"page\":\"$pg\"}" &
done
for a in '"media":"视频无法播放"' '"load":"加载中"' '"load":"加载失败"' '"english":"暂无英文版"'; do
  n=$(echo "$a" | tr -d '":' ); shot Article "Article-$n-1440" 1440x900 --props "{\"theme\":\"浅色\",$a}" &
done
shot Project Project-empty-1440 1440x900 --props '{"theme":"浅色","devlog":"还没有日志"}' &
wait
rmdir "$OUT/tmp" 2>/dev/null; ls "$OUT" | grep -c png
