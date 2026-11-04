# design-bar

Claude Design 的配套技能。设计在 Claude Design 里做；本技能补上 Claude Design 不做的四件事，让设计从需求到代码保持一致、不退化。

| 谁 | 负责什么 |
|---|---|
| Claude Design · Design System | 设计语言的唯一来源：品牌手册、多主题 token、组件规范与预览 |
| Claude Design · Design | 方向稿、界面、交互状态 |
| design-bar | 开工前确认关键信息与标杆；把设计系统同步进代码仓库；对画板和实现代码做只读验证；检查需求覆盖和过时口径；把评审意见沉淀回设计系统 |

## 为什么需要它

- **说不清需求时，直接出图会用品类默认值填空。** design-bar 先读完项目资料，用「我的理解」表和对比题让用户只做纠正和选择；受众、核心任务、气质确认之前不出完整设计。
- **画布不会检查代码。** 写代码的 agent 读不到私有画布，代码会悄悄长成另一套设计语言。design-bar 把设计系统的 token 生成为代码里的 tokens.css，把规则写进 `AGENTS.md`，并用脚本检查实现。
- **评审意见会被遗忘。** 同一类意见出现两次以上，就写回设计系统或检查阈值。
- **需求一直在加，设计跟不上。** `coverage.py` 列出还没画的功能，`stale_terms.py` 按词汇表找出还在用旧说法的地方，`verify_canvas.py` 把每块画板的每个状态在浅色、深色下验一遍，只给 done 或 needs_work。

做稿和打磨的手艺吸收了 [unslop](https://heydamir.design/unslop)（Damir Sokolovsky，CC BY 4.0）的方向五行与九遍打磨，以及 [baoyu-design](https://github.com/JimLiu/baoyu-design)（JimLiu）的假设先行、只读验证者、写法规范和中日韩排版，见 `references/craft.md`。

做法参考了 Vercel 公开的 [design.md](https://vercel.com/design.md) 实践：判断写成规则，数值交给样式表，能机械判断的交给检查脚本。

## 流程

```
0 接入项目 → 1 确认关键信息 → 2 标杆卡 → 3 在 Claude Design 建立设计系统
→ 4 同步进仓库 → 5 实现、检查、评审 → 6 沉淀回设计系统
```

已有设计系统时，新功能和打磨从第 5 步开始，先写一份功能简报。

## 安装

**个人全局（Claude Code）**

```bash
cp -r design-bar ~/.claude/skills/
```

**接入某个项目（推荐）**

```bash
python design-bar/scripts/init_project.py /path/to/project \
  --design-dir docs/design --tokens-path src/app/tokens.css
```

- 创建设计目录模板；已有同名目录和 README 时只追加，不覆盖；
- 把技能复制到项目的 `.claude/skills/design-bar/`（项目已有 `.agents/skills` 或 `skills/` 时沿用）；
- 在 `AGENTS.md` 写入设计规则，`CLAUDE.md` 通过 `@AGENTS.md` 引入；Claude Code、Codex 等 agent 都能读到。

可重复运行。更新项目里的技能副本加 `--update-skill`。

**claude.ai**：把 `design-bar` 文件夹打包成 `.skill` 文件上传。

## 项目里的设计目录

```
docs/design/            （或 design/）
├── README.md           目录说明与维护规则
├── design-system.md    设计系统链接、代码 token 路径、同步时间、画布链接
├── brief.md            已确认的产品与用户信息
├── bar-sheet.md        标杆卡
├── decisions.md        设计决策日志
├── features/           每个功能一份设计简报
└── reviews/            每轮评审的报告与截图
```

## 脚本

需要 Python 3；渲染检查还需要 Playwright：`pip install playwright && python -m playwright install chromium`

```bash
# 设计系统的 tokens.json → 代码里的 tokens.css（--check 只比较，不写入）
python scripts/sync_tokens.py tokens.json --out src/app/tokens.css --source <设计系统链接>

# 渲染截图 + 机械检查：溢出、字号、对比度、触控尺寸、焦点、reduced-motion、h1 等
python scripts/check_page.py <页面路径或 URL> --out docs/design/reviews/2026-10-30-首页 --dark

# 源码里写死的颜色和数值、Tailwind 任意值、静态内联样式、!important、未定义的 token
python scripts/lint_tokens.py src --tokens src/app/tokens.css
```

`lint_tokens.py` 和 `sync_tokens.py --check` 发现问题时退出码为 1，可以接入提交前检查。

## 文件

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 主流程 |
| `references/claude-design.md` | 怎么用 Design System 与 Design 类型 |
| `references/intake.md` | 确认问题库 |
| `references/taste-lexicon.md` | 形容词 → 设计参数 |
| `references/anti-patterns.md` | 具名反面模式 |
| `references/rubric.md` | 评分维度与底线 |
| `references/app.md` | App 交互的额外流程 |
| `scripts/` | 接入、同步、检查脚本 |
| `assets/` | 项目设计目录模板与 AGENTS.md 规则块 |

## 实测记录

第一次实测在 [thin-muscle-coach](https://github.com/madlouse/thin-muscle-coach)（私有）上进行：发现代码与设计文档是两套设计语言，基线评审抓出小字、触控尺寸、缺少 h1、45 处静态内联样式等问题；确认方向后建立了 Veli 设计系统，并按它重做首页。测试中修正了技能自身的三个问题：`file://` 下 reduced-motion 误报、内联样式误报、token 文件位置固定。
