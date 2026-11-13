#!/bin/bash
# 用仓库里已合并的验证器；本站的色面门槛（相邻色面 ≥ 1.8:1 或有描边）在 docs/uiue/design-bar.json，验证器自动采用。对全部页面画板跑 verify_canvas.py：浅色、深色、伪语言，各加 390x844、320x568、820x1180；首页另加 1280x720、1440x790、390x664、984x1100。结论要 done。
# 用法：verify_all.sh <输出目录>             输出目录必填，放在仓库外面（截图不进仓库）；目录会先清空。
#       verify_all.sh --devices <输出目录>   改查手机、平板、折叠屏画板（同一份标记在画板自己的尺寸下、每个属性状态各查一遍）
# 退出码：0 结论 done；1 结论不是 done（验证器自己的退出码原样传出）；2 验证器没跑完、没生成报告（例如没装浏览器）。完整输出在 <输出目录>/verify.log。
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
U=$(cd "$(dirname "$0")/.." && pwd)
P=$U/boards
CSS=$(cd "$U/../../system" && pwd)/canvas.css
DEV=0; if [ "${1:-}" = "--devices" ]; then DEV=1; shift; fi
OUT=${1:?要给输出目录（放在仓库外面）}
V=$(cd "$U/../../../.." && pwd)/.grok/skills/design-bar/scripts/verify_canvas.py
PAGES="Main Mind Learn Article About States Build Project Body Controls"
args=()
for b in $PAGES; do for sz in 390x844 320x568 820x1180; do args+=(--size "$b.dc.html=$sz"); done; done
for sz in 1280x720 1440x790 390x664 984x1100; do args+=(--size "Main.dc.html=$sz"); done
files=(); for b in $PAGES; do files+=("$P/$b.dc.html"); done
if [ $DEV = 1 ]; then args=(); files=(); for b in Tablet Mobile Fold MindMobile LearnMobile ArticleMobile AboutMobile BuildMobile; do files+=("$P/$b.dc.html"); done; fi
rm -rf "$OUT"; mkdir -p "$OUT"
python3 $V "${files[@]}" --out "$OUT" --themes light,dark,pseudo \
  --blob 2d0ccacf7377c5a050e285f270f25ffd=$CSS --blob 26c007f478ecf5fa646eda60cbc23992=$U/canvas.js "${args[@]}" >"$OUT/verify.log" 2>&1
code=$?
tail -40 "$OUT/verify.log"
if [ ! -s "$OUT/verify-canvas.md" ]; then echo "验证器没生成报告（退出码 $code），完整输出在 $OUT/verify.log" >&2; exit 2; fi
exit $code
