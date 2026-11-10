#!/usr/bin/env python3
"""把 design-bar 接入一个项目。

做三件事，全部可重复运行（已存在的文件不会被覆盖）：
  1. 在项目里创建 design/ 目录模板（设计系统链接、简报、标杆卡、决策、功能简报、评审）；
  2. 把本技能复制到项目的 skills 目录，方便各种 agent 发现和使用；
  3. 在 AGENTS.md 和 CLAUDE.md 里写入设计工作规则（用标记包裹，重复运行时原地更新）。

用法：
  python init_project.py <项目根目录> [--skills-dir .claude/skills] [--design-dir design]
                         [--tokens-path src/styles/tokens.css] [--update-skill] [--dry-run]

skills 目录的默认选择顺序：已存在的 .claude/skills → .agents/skills → skills/（其中已有技能时）→ 新建 .claude/skills
"""
import argparse
import pathlib
import re
import shutil
import sys

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "project-template" / "design"
BLOCK = SKILL_ROOT / "assets" / "agents-block.md"
START, END = "<!-- design-bar:start -->", "<!-- design-bar:end -->"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def pick_skills_dir(root: pathlib.Path) -> pathlib.Path:
    for cand in (".claude/skills", ".agents/skills"):
        if (root / cand).is_dir():
            return root / cand
    plain = root / "skills"
    if plain.is_dir() and any((p / "SKILL.md").exists() for p in plain.iterdir() if p.is_dir()):
        return plain
    return root / ".claude" / "skills"


def upsert_block(path: pathlib.Path, block: str, create_header: str, dry: bool, log):
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if START in text and END in text:
            new = re.sub(re.escape(START) + r".*?" + re.escape(END), block.strip(), text, flags=re.S)
            action = "更新"
        else:
            new = text.rstrip() + "\n\n" + block.strip() + "\n"
            action = "追加"
    else:
        new = create_header + block.strip() + "\n"
        action = "创建"
    if path.exists() and new == path.read_text(encoding="utf-8"):
        log(f"未变化  {path.name}")
        return
    if not dry:
        path.write_text(new, encoding="utf-8")
    log(f"{action}  {path.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--skills-dir")
    ap.add_argument("--design-dir", default="design")
    ap.add_argument("--tokens-path", help="tokens.css 的位置（相对项目根目录）。放在代码能直接引用的地方；默认 <design-dir>/tokens.css")
    ap.add_argument("--update-skill", action="store_true", help="覆盖项目里已有的 design-bar 副本")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = pathlib.Path(a.project).resolve()
    if not root.is_dir():
        sys.exit(f"项目目录不存在：{root}")
    dry = a.dry_run
    lines = []
    log = lines.append

    # 1. design/ 目录模板
    design = root / a.design_dir
    for src in sorted(TEMPLATE.rglob("*")):
        rel = src.relative_to(TEMPLATE)
        dst = design / rel
        if src.is_dir():
            if not dry:
                dst.mkdir(parents=True, exist_ok=True)
            continue
        if dst.exists():
            existing = dst.read_text(encoding="utf-8") if rel.as_posix() == "README.md" else ""
            if rel.as_posix() == "README.md" and START in existing:
                # 项目自己的 README：在标记块里追加或更新本技能的目录说明
                body = src.read_text(encoding="utf-8").split("\n", 2)[2]  # 去掉模板标题
                readme_block = f"{START}\n## design-bar 工作目录\n\n{body.strip()}\n{END}\n"
                upsert_block(dst, readme_block, "", dry, lambda m: log(m.replace("README.md", f"{a.design_dir}/README.md")))
            else:
                log(f"已存在  {a.design_dir}/{rel}")
            continue
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        log(f"创建    {a.design_dir}/{rel}")

    # 2. 技能副本
    skills_dir = (root / a.skills_dir) if a.skills_dir else pick_skills_dir(root)
    target = skills_dir / "design-bar"
    rel_skill = target.relative_to(root).as_posix()
    if target.resolve() == SKILL_ROOT:
        log(f"技能已在项目内  {rel_skill}")
    elif target.exists() and not a.update_skill:
        log(f"已存在  {rel_skill}（如需更新，加 --update-skill）")
    else:
        existed = target.exists()
        if not dry:
            if existed:
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(SKILL_ROOT, target, ignore=IGNORE)
        log(f"{'更新' if existed else '复制'}  技能 → {rel_skill}")

    # 3. AGENTS.md 与 CLAUDE.md
    block = (BLOCK.read_text(encoding="utf-8")
             .replace("{{SKILL_PATH}}", rel_skill).replace("{{DESIGN_DIR}}", a.design_dir.strip("/"))
             .replace("{{TOKENS_PATH}}", a.tokens_path or f"{a.design_dir.strip('/')}/tokens.css"))
    upsert_block(root / "AGENTS.md", block, "# AGENTS.md\n\n", dry, log)
    claude = root / "CLAUDE.md"
    if claude.exists() and re.search(r"^@AGENTS\.md\s*$", claude.read_text(encoding="utf-8"), flags=re.M):
        log("未变化  CLAUDE.md（已通过 @AGENTS.md 引入）")
    elif claude.exists():
        upsert_block(claude, block, "", dry, log)
    else:
        if not dry:
            claude.write_text("@AGENTS.md\n", encoding="utf-8")
        log("创建    CLAUDE.md（内容为 @AGENTS.md，Claude Code 会据此读取 AGENTS.md）")

    print(("[演练，未写入任何文件]\n" if dry else "") + "\n".join(lines))
    print(f"\n完成。下一步：让 agent 读取 {rel_skill}/SKILL.md，从第 1 步（确认关键信息）开始；设计语言在 Claude Design 的设计系统里建立。")


if __name__ == "__main__":
    main()
