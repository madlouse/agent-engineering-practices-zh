#!/bin/bash
# 首页「叶与网」的四帧证据（capture_motion.py：执行画板自己的挂载代码，截到 WebGL 画出来的画面和兜底画面）。用法：motion_frames.sh <输出目录>（放在仓库外面）
#   1 悬停倾斜（62:38，指针停在站稳一侧）  2 系统减弱动态效果（静态线稿）  3 无 WebGL（静态线稿）  4 键盘焦点在接缝的圆上（画板属性 focus）
# 另加两张手机首屏（390×844 中文、英文）的动效帧：叶在纸色一半、网在墨色一半
export PYTHONDONTWRITEBYTECODE=1
OUT=$1; U=$(cd "$(dirname "$0")/.." && pwd)
C=$(cd "$U/../../../.." && pwd)/.grok/skills/design-bar/scripts/capture_motion.py
CSS=$(cd "$U/../../system" && pwd)/canvas.css
B="--blob 2d0ccacf7377c5a050e285f270f25ffd=$CSS --blob 26c007f478ecf5fa646eda60cbc23992=$U/canvas.js"
M=$U/boards/Main.dc.html
mkdir -p "$OUT"
python3 $C $M "$OUT/Main-motion-lean-body-1440.png" --size 1440x900 --props '{"theme":"浅色"}' --state '{"lean":"body"}' --hover 400,450 $B
python3 $C $M "$OUT/Main-motion-lean-mind-1440.png" --size 1440x900 --props '{"theme":"浅色"}' --state '{"lean":"mind"}' --hover 1100,450 $B
python3 $C $M "$OUT/Main-motion-reduced-1440.png" --size 1440x900 --props '{"theme":"浅色"}' --reduced-motion --expect '.vc-still-leaf' $B
python3 $C $M "$OUT/Main-motion-nowebgl-1440.png" --size 1440x900 --props '{"theme":"浅色"}' --no-webgl --expect '.vc-still-leaf' $B
python3 $C $M "$OUT/Main-motion-focus-orb-1440.png" --size 1440x900 --props '{"theme":"浅色","focus":"接缝上的圆"}' $B
python3 $C $M "$OUT/Main-motion-390.png" --size 390x844 --props '{"theme":"浅色"}' $B
python3 $C $M "$OUT/Main-motion-390-en.png" --size 390x844 --props '{"theme":"浅色","lang":"English"}' $B
ls "$OUT" | grep -c motion
