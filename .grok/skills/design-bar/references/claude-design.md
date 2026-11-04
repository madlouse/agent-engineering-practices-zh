# 在 Claude Design 里建立和维护设计语言

Claude Design 现在在 Claude 里以两种产物类型出现：**Design System**（设计语言）和 **Design**（画布）。都通过 Artifact 工具使用。

## 找到或新建设计系统

1. `Artifact(action="list", scope="types")` 确认有 Design System 类型。
2. `Artifact(action="list", type="Design System")` 列出用户能打开的设计系统：
   - 有标为默认的：直接用，不用再问；
   - 有几个但都不是默认：列出名字请用户选；
   - 没有：新建。
3. 新建：用 Design System 类型的 `type_url`、一个 `title`（品牌名）发布，不带文件。返回的说明（类型自带的 SKILL.md）规定了文件结构，按它写，不要凭记忆。

要点（以类型说明为准）：内容放在 `project/` 下；`project/README.md` 是品牌手册，必须有；`project/tokens.json` 是 token；组件放在 `project/components/<名字>/`（`README.md` 规范 + `preview.html` 预览）；`components/Cover/preview.html` 是封面，最后写；索引 `project/design-system.json` 放在最后一次发布里。

## 设计系统 README 应该有的章节

1. 一句话定位与气质
2. 一句话原则（例如「打开就是此刻该做的那一个」）
3. 内容与语气：品牌名用法、该说和不该说的、数字格式
4. 视觉基础：层级（字号角色表）、颜色只表达什么、留白与分组、材质、动效与签名时刻、触控与可访问性
5. 关键页面的层级（例如首页从上到下放什么，为什么）
6. 具名反面模式
7. 给写代码的 agent：先读什么、只用 token、需要新 token 怎么办、交付前跑哪些检查、评审意见写回哪里
8. 尚未包含的内容（字体文件、组件代码包、还没画的界面）

## tokens.json 的要点

- 颜色是一个扁平列表，每个 token 按主题给值（第一个主题放浅色）；别名写成 `{other-token}`；不能用 `var()`、`color-mix()`、颜色名。
- 文字样式放在 `type.groups[].styles`；字体栈放在 `type.families`（不能含括号）。
- 其他族（spacing、radius、size、shadow、duration、easing 等）都是 `{"tokens": [{"name", "value", "usage"}]}` 列表。
- 每个 token 写 `usage`：用在哪里、不用在哪里。
- 名字和代码里的 CSS 变量一致（去掉 `--`），这样 `sync_tokens.py` 生成的文件可以直接替换代码里的 tokens.css。
- 材质这类需要 `color-mix()` 的派生值不进 tokens.json，写在 README 和代码的全局样式里，并且只引用 token。

## 发布前自查

- 渲染每个组件预览和封面，浅色、深色各看一遍；文字对比度两个主题都 ≥ 4.5:1。
- 预览里的样式只用 token。
- 没有渐变、emoji 卡片、左侧色条这类 AI 套路。

## 用 Design 画布出界面

- 比较方向、画关键界面、画交互状态时用 Design 类型，先列出设计系统，用标为默认的那个。
- 每个界面画出全部状态（空、加载、错误、完成等），这是实现和评审的对照。
- 画布链接写进 `<设计目录>/design-system.md` 或功能简报。

实际踩过的坑：

- **样式表**：画板里的 `.css` 要先作为资源上传到画布（`asset: true`），用返回的 `/_blob/<id>` 链接；本地核对时保留相对路径 `tokens.css`，发布前替换。
- **主题锁定**：画板会跟随看稿人的系统深浅色。浅色稿在根元素加 `data-theme="light"`，固定深色的区域（训练模式）加 `data-theme="dark"`；`sync_tokens.py` 生成的 tokens.css 支持在任意元素上切主题。
- **一个流程跨多个状态**：每张画板有自己的状态；需要共享状态的流程（做一组 → 组间休息 → 练完了）放在同一张画板里，用 `<sc-if>` 切换，再加一个 `data-props` 开关方便直接跳到某个状态。
- **中文换行**：数字和单位、「周二」这类词用 `white-space: nowrap` 包起来；`text-wrap: balance` 对中文不总是有效，长句按意群拆成几个不换行的片段。
- **网页是流式页面**：`expand: "fill"`、不写死宽度、`max-width` 容器；手机宽度下导航改成横向滚动的一行，摘要数字排到最前。

## 修改

- 先 `read` 设计系统的索引和要改的文件，在最新内容上改，只发布改过的文件；`tokens.json` 每次整份发送。
- 改了 token：重新运行 `sync_tokens.py` 同步到代码。
- 设计系统被标为 `"editing": "code"`（由代码同步而来）时，在代码里改，再用 Claude Code 的 `/design-sync` 同步，不要在页面上改。
