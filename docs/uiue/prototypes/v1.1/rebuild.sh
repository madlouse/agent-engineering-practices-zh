#!/bin/bash
# 一条龙：从源片段重新生成共享样式表、shell.md 和全部画板，再做类名审计。改了任何一处源，跑这一个脚本。
#   bash docs/uiue/prototypes/v1.1/rebuild.sh                       生成 + 审计
#   bash docs/uiue/prototypes/v1.1/rebuild.sh --verify <输出目录>   再跑 verify_canvas.py（页面画板和设备画板各一遍，报告在 <输出目录>/pages 和 <输出目录>/devices；输出目录放在仓库外面）
# 从哪个目录跑都可以，路径都相对本脚本算。
#
# 源在哪里（成品 boards/*.dc.html 不直接改；Main.dc.html 例外，它是手写的，本身就是源）：
#   共享样式表   src/shell/tools/canvas.head.css（手写的类）+ canvas.glass.css（液态玻璃模板）+ ../../system/tokens.json → ../../system/canvas.css
#   外壳         src/shell/test/ShellTest.dc.html → shell.md（各页面的生成脚本从 shell.md 里取外壳片段）
#   首页         boards/Main.dc.html（手写；外壳的脚本段由 tools/sync_shell.py 换成 shell.md 的那一份，标记段只核对）
#   看清、学习路径   src/mind/（Mind|Learn.body.html、.js、build.py）
#   文章、状态、关于 src/pages/（parts/、build.py）
#   动手、项目、站稳 src/build/（parts.py、build.py、project.py、body.py）
#   控件样张     src/shell/tools/gen_controls.py（样张的标记在 controls_samples.json，由 extract_samples.py 从页面画板取）
#   手机、平板、折叠屏画板  gen_device_boards.py（从页面画板生成同一份标记）
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
U=$(cd "$(dirname "$0")" && pwd)
SYS=$(cd "$U/../../system" && pwd)
P=$U/boards
T=$U/src/shell/tools

echo '── 1. 共享样式表'
python3 "$T/build_css.py" "$SYS/canvas.css" "$SYS/tokens.json"
python3 "$T/gen_canvas_vars.py" "$SYS/tokens.json" "$SYS/canvas.css" --check

echo '── 2. 外壳：shell.md、首页的外壳'
python3 "$T/gen_shell_md.py" "$U/src/shell/test/ShellTest.dc.html" "$U/shell.md"
python3 "$U/tools/sync_shell.py" "$U/shell.md" "$P/Main.dc.html"

echo '── 3. 页面画板'
python3 "$T/gen_controls.py" "$P/Controls.dc.html"
(cd "$U/src/mind" && python3 build.py)
(cd "$U/src/pages" && python3 build.py)
(cd "$U/src/build" && python3 build.py && python3 project.py && python3 body.py >/dev/null)

echo '── 4. 手机、平板、折叠屏画板'
python3 "$U/gen_device_boards.py" "$P"

echo '── 5. 类名审计（重复定义、没用到、没定义）'
python3 "$U/tools/audit_classes.py" "$SYS/canvas.css" "$P" --strict

if [ "${1:-}" = "--verify" ]; then
  OUT=${2:?--verify 后面要给输出目录（放在仓库外面）}
  echo '── 6. verify_canvas.py'
  bash "$U/tools/verify_all.sh" "$OUT/pages"
  bash "$U/tools/verify_all.sh" --devices "$OUT/devices"
fi
echo '完成'
