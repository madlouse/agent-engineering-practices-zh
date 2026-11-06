# 体验标杆研究：Vercel、Shopify、Anthropic、OpenAI

> 查询日期 2026-11-06。只用一手来源（官方博客、官方文档、官方开源仓库）。引用原文每处不超过 15 个字（英文按词计），其余是转述。拿不到的页面在 §0 写明。

## 0. 结论

**四家共同的三件事**

1. **规则要能判对错，判不了的交给人。** Vercel 的 design.md 把「机械的」放进样式表和自动检查，把「判断」留在文字里，再用评测循环把反复出现的意见变成检查；Claude Code 文档把指令分成模型自己决定的和框架必须执行的两类，「永远不能」的规则要放进 hook，不放在说明里。我们的 `quality-terms.md` 走的就是这条路，研究支持它。
2. **人和 Agent 协作，确认要按风险分级，不按步数。** 用户对 Claude Code 的确认请求 93% 都点了同意，于是出现「确认疲劳」；四家的解法一致：低风险自动做，不可撤回的（提交、付款、发消息、改线上数据）才停下来确认，用户随时能打断、接管，Agent 遇到偏好和意图问题主动问。
3. **在别人的地盘上，像宿主比像自己更重要。** OpenAI 禁止应用在 ChatGPT 里用自定义字体、渐变和花纹；Shopify 要求应用和后台「长得一样、用起来一样」，把「熟悉」列为体验价值；Vercel 把通用规则和「只代表 Vercel 品牌的偏好」分成两章。品牌表达只在自己的页面上做，而且要证明它让任务更快、更好懂。

**最需要挑战的一条我们的原则**：液态玻璃（`velicoach-layout` §8、`liquid-glass.md` §0–§1）。四家都把装饰放在最后：Polaris 要用「好用」而不是「装饰」让人惊喜，Vercel 的动效先过「必要性检查」，OpenAI 明令去掉破坏极简的效果。我们的玻璃写了透镜、色散、位移图、背景采样和一整套检查，花的力气和它给读者带来的好处不成比例。建议改成：**实色是默认，玻璃要先证明它让人看到了背后正在变化的东西**，透镜和色散整套去掉，或者只在首页「叶与网」上留一处（见 §6.3）。

**拿不到或已改版的一手来源**

| 页面 | 情况 | 用什么替代 |
|---|---|---|
| vercel.com/design/guidelines | 抓取被拦截 | 同一份内容的开源仓库 [vercel-labs/web-interface-guidelines](https://github.com/vercel-labs/web-interface-guidelines)（`README.md`、`AGENTS.md`，提交 434b7f9，2026-10-05） |
| vercel.com/design.md（design.md 正文） | 没有拿到 | 只用 Vercel 博客对它的说明 |
| vercel.com/geist/introduction | 抓取被拦截 | [vercel.com/design/introduction](https://vercel.com/design/introduction)（同一份 Geist 首页） |
| polaris.shopify.com 全站 | 302 跳到 shopify.dev，跳转后的页面没拿到 | Polaris 官方仓库 [Shopify/polaris](https://github.com/Shopify/polaris) 里的站点源文件（`polaris.shopify.com/content/`，提交 3f7954a，2026-09-10） |
| help.openai.com 的 ChatGPT agent 帮助页 | 站点返回错误 | OpenAI 的发布文章和系统卡片 |
| Apps SDK 的「conversational, intelligent, simple, responsive, accessible」五条 | **现在的官方页面里没有这五个词**：design-guidelines 和 ui-guidelines 两个地址都已改成「插件 UI 指南」，ux-principles 改成了「用例规划」 | 只用现在的版本；这五条不能当作已核实的出处引用 |

---

## 1. Vercel

### 1.1 结论

Vercel 的价值不在某一条规则，而在**做法**：把一百多条细节写成可以机器检查的清单（Web Interface Guidelines），把品牌偏好和通用规则分开，给 Agent 一份 design.md 加一份它不用读的样式表，再用固定场景的评测去改规则。它的规则粒度最细、最能直接抄进 lint，但信息密度和语气是开发者工具的，搬到大众产品要挑。

### 1.2 design.md 是什么、怎么写、为什么对 Agent 有用

出处：John Phamous，[How our agents build on brand pages with design.md](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md)，2026-08-31。

- **是什么**：一份公开文件，任何编码 Agent 读了就能做出「像 Vercel」的报告、提案、简报页。它针对的是 Agent 读不到 Vercel 代码仓库的场合。
- **由三部分组成**：
  1. **design.md（判断）**：怎么框定读者要完成的事、怎么组织证据、怎么选构图、怎么写文案、怎么用标识；还**点名列出生成式设计的常见反模式**，因为模型认得出有名字的模式。
  2. **公开样式表（机械）**：一套有边界、有文档的类名和 token（页头、表格、数字条、图表）。Agent 只写类名，**不读 CSS**，所以不占上下文。
  3. **评测循环**：人判断主观质量，代码抓机械错误（例如表格没用满可用宽度）；同一条意见出现多次，就同时写进 design.md 和一条确定性检查。
- **怎么写（原文的六步）**：选一种反复要做、有真实读者的产出并写评分标准 → 先存一份没有新设计上下文的基线 → 把最近十次修改意见写成可观察的规则 → 能重复的机械部分交给样式表和 token，判断留在文字里 → 和基线做盲测 A/B → 每条修正放到「能执行它的最窄的地方」，人工循环见效后再加工具。
- **为什么有用**：直接把产品技能改写成公开提示词失败了，因为模型对主观描述的理解各不相同，也缺组件和实例。改用这套做法后，同一个续约提案，基线是「一个通用的 SaaS 仪表盘」，用了 design.md 的版本先给建议、把商业证据归组、把同类数字放在同一刻度上——**改变的是结构和层级，不只是样式**。
- **数据和它自己承认的限度**：三个场景各生成两次，确定性检查在 6 页里找到 39 个已知问题，不用 design.md 时 91 个，少约 57%。但 6 页样本太小；**每一页都至少有一个阻止上线的问题**；检查只能抓已经写进去的错误，说明不了整体质量；只在一个模型上出现的问题不写进规则，等它在多个模型上重复再写。

### 1.3 核心思想

| # | 一句话原则 | 解决什么问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| V-1 | 判断写成文字，机械交给样式表和检查 | 模型对同一段主观描述理解不同，产出不稳定 | Agent 只引用类名；每条反复出现的意见都有一条对应的自动检查 | [design.md 博客](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md) |
| V-2 | 给反模式起名字 | 模型认不出「模板味」这种笼统的说法 | 规范里有一张带名字的反模式清单 | 同上 |
| V-3 | 用固定场景评测规则，不靠感觉 | 改了规则不知道是变好还是变坏 | 有基线、固定场景、盲测对比；修正后同类意见的次数应下降 | 同上 |
| V-4 | 界面的好来自上百个小决定 | 大原则落不到实现 | 清单按交互、动效、布局、内容、表单、性能、设计分节，每条一句、多数带数值 | [WIG README](https://github.com/vercel-labs/web-interface-guidelines/blob/main/README.md) |
| V-5 | 用户的状态不该丢 | 刷新、分享、后退之后找不到刚才的位置 | 筛选、标签页、展开的面板都写进 URL；后退恢复滚动位置 | 同上「Interactions」 |
| V-6 | 每个屏幕都有下一步 | 空状态、错误状态是死胡同 | 空、稀疏、密集、错误四种状态都有设计；错误文案给出路 | 同上「Content」「Copywriting」 |
| V-7 | 动效先过必要性检查 | 为了动而动，拖慢、让人晕 | 只为说清因果或刻意的惊喜而动；可打断；只动 `transform`、`opacity` | 同上「Animations」 |
| V-8 | 通用规则和品牌偏好分开 | 把一家的口味当成普遍规律 | 文案的 Title Case、用 `&` 代替 and 等单列在「Vercel-specific」，原文说它们「不是通用准则」 | 同上「Vercel-specific」 |

Geist 首页（[vercel.com/design/introduction](https://vercel.com/design/introduction)）**没有写成条的设计原则**，只描述了范围：高对比、无障碍的颜色系统；网格是「Vercel 美学的核心」；图标为开发者工具定制；文档页加 `.md` 就能给 Agent 读。所以 Geist 的「原则」只能从 WIG 和 design.md 里看。

### 1.4 能直接用的规则（都能判对错）

出处均为 [WIG `AGENTS.md`](https://github.com/vercel-labs/web-interface-guidelines/blob/main/AGENTS.md)，除非另注。

| 编号 | 规则 | 怎么判 | 为什么 |
|---|---|---|---|
| VR1 | 加载中的按钮显示指示器，**保留原来的文字** | 点提交后截图，文字不变、宽度不变 | 用户知道自己点的是什么，版面不跳 |
| VR2 | 转圈或骨架屏先延迟约 150–300ms 再出现，出现后至少显示约 300–500ms | 在快速网络下录屏，不闪 | 响应很快时一闪而过比没有更糟 |
| VR3 | 提交按钮在请求开始前一直可点，不预先禁用；请求中禁用并带幂等键 | 空表单点提交会看到校验提示 | 预先禁用让人猜不出缺什么；幂等键防重复提交 |
| VR4 | 不拦截输入、不禁止粘贴；先接收再校验 | 在数字框里输字母，能输进去并看到提示 | 拦按键没有解释，用户以为键盘坏了 |
| VR5 | 错误放在字段旁边；提交时焦点移到第一个错误 | 提交错表单，焦点落在第一个错的字段 | 用户不用找错在哪 |
| VR6 | `autocomplete`、正确的 `type` 和 `inputmode`；邮箱、验证码关闭拼写检查 | 读 HTML 属性 | 自动填充、合适的键盘，少打字 |
| VR7 | 手机上输入框字号 ≥ 16px；不禁用缩放 | 读计算样式；`viewport` 里没有 `user-scalable=no` | iOS Safari 小于 16px 会自动放大页面 |
| VR8 | 可点区域 ≥ 24px，手机 ≥ 44px；看起来能点的地方都能点，复选框的文字和框是同一个点击区 | `check_page.py` 量点击区 | 减少点不中和「死区」 |
| VR9 | 焦点圈看得见、不被吸顶条遮住 | Tab 走一遍，焦点从不在吸顶条下面 | 键盘用户看不到焦点就迷路 |
| VR10 | 导航用 `<a>`，不用 `<div onClick>` 或按钮代替 | 读 DOM；能 Cmd/中键新标签打开 | 保住浏览器的标准行为 |
| VR11 | 状态写进 URL：筛选、标签页、分页、展开的面板 | 刷新、分享后状态还在 | 分享和后退都靠它 |
| VR12 | 后退恢复滚动位置 | 进文章再后退，回到原来的位置 | 长列表里来回不丢位置 |
| VR13 | 破坏性操作要确认，或者给有安全窗口的撤销 | 删除后能撤销，或有确认 | 二选一，不是两样都要 |
| VR14 | 乐观更新：大概率成功就先改界面，失败回滚或给撤销 | 断网点操作，界面先变、失败后复原并提示 | 把感知等待降到零 |
| VR15 | 吐司和行内校验用 `aria-live="polite"` | 读 DOM | 读屏用户听得到结果 |
| VR16 | 尊重 `prefers-reduced-motion`；不用 `transition: all`；只动 `transform`、`opacity` | `lint` 搜 `transition: all`；系统减弱动态后录屏 | 避免误动布局属性造成卡顿 |
| VR17 | 自动播放且超过 5 秒的动效有暂停、停止或隐藏；除了静音的非必要循环，不自动播放 | 找暂停入口 | WCAG 2.2.2 |
| VR18 | 骨架屏和最终内容的形状完全一致 | 骨架和加载完的截图叠在一起比 | 防止版面移动 |
| VR19 | 比较数字用等宽数字 `tabular-nums` | 读计算样式 | 列对齐，一眼能比 |
| VR20 | 不只靠颜色表达状态；只有图标的按钮有 `aria-label` | 灰度截图仍能读懂；读 DOM | 色盲和读屏用户 |
| VR21 | 版式能扛住短、普通、很长三种内容；flex 子元素加 `min-w-0` | 用超长标题、空字符串各渲染一次 | 用户内容和翻译后的文字会变长 |
| VR22 | 日期、数字、货币按用户的语言格式化；语言按 `Accept-Language` 判断，不按 IP | 换浏览器语言再看 | 位置不等于语言 |
| VR23 | 品牌名、产品名、代码加 `translate="no"` | 读 DOM | 浏览器自动翻译不把专名翻坏 |
| VR24 | 单位和数字之间用不换行空格（`10&nbsp;MB`、`⌘&nbsp;K`） | 读源码 | 不在行尾被拆开 |
| VR25 | 写操作（POST/PATCH/DELETE）< 500ms；超过 50 项的列表虚拟化；图片写明尺寸 | 端到端计时；CLS | 性能预算写成数字 |
| VR26 | 悬停、按下、焦点的对比度比静止时更高 | 取色比较 | 状态变化看得出 |
| VR27 | 嵌套圆角：子 ≤ 父，同心 | 读 token | 曲线对齐 |
| VR28 | 深色主题在 `<html>` 上写 `color-scheme: dark`；`theme-color` 和页面底色一致 | 读 HTML | 滚动条和浏览器框不刺眼 |
| VR29（文案，Vercel 自己的偏好里也通用的部分） | 错误文案说清怎么修：不写「API 密钥无效」，写「已过期，去设置里生成新的」；按钮写具体结果（不写「继续」，写「保存 API 密钥」） | 逐条读 | 让用户知道下一步 |

### 1.5 批判

- **信息密度和语气是开发者工具的。** 「Title Case」「用 `&` 代替 and」「数字一律用阿拉伯数字」是 Vercel 自己承认的品牌偏好；中文页没有大小写问题，`&` 在中文里更不该用。
- **两条规则在大众产品上要改。** 「桌面单个主输入框自动聚焦」适合控制台，不适合内容站首页（会抢走读屏用户的阅读起点）；「对比度优先用 APCA 而不是 WCAG 2」和法规、审计脚本冲突，我们的 A1 继续用 WCAG 2 的数值，APCA 只作参考。
- **内部有张力。** 「确认或撤销」二选一是对的，但它和「乐观更新」放在一起时没说清：对外发出去的东西（邮件、订阅）撤销不了，乐观更新只能用于能回滚的本地状态。
- **design.md 的证据很弱，而且它自己说了。** 6 页、一个模型、每页仍有阻止上线的问题。可借的是做法（基线、固定场景、盲测、意见变检查），不是那个 57%。
- **样式表「不让 Agent 读 CSS」是双刃剑。** 省上下文，但 Agent 不知道某个类在窄屏下长什么样，只能靠检查兜底；我们的 token 也要配可渲染的检查，不能只给名字。

---

## 2. Shopify

### 2.1 结论

Shopify 的核心是**为一个具体的人（商家）减负，而且承认他的处境不完美**：六条体验价值里，「Considerate（体贴）」排第一，「Efficient」里写明「用摩擦突出重要决定」，「Trustworthy」里写明「安全的操作零摩擦，有风险的给清楚的说明和更多控制」。内容规范最可借：7 年级阅读水平、一个东西只用一个叫法、按钮以强动词开头、按情境调语气（日常任务少说话，庆祝很少用）。Sidekick 的公开做法只有一条但很硬：**不经批准不改线上店铺**，改动先进草稿，商家自己发布。Polaris 的「Pro」高密度是后台专用，搬到大众产品就错。

> 「Merchants first」：在 Polaris 体验价值页的关键词里有「merchant first」，**正文里没有这条原则**。正文的六条是 Considerate、Empowering、Crafted、Efficient、Trustworthy、Familiar。下面按正文写，不把「Merchants first」当成正式原则引用。

### 2.2 核心思想

出处：Polaris 仓库 [`foundations/experience-values.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/foundations/experience-values.mdx)（原页面 polaris.shopify.com/foundations/experience-values，现已跳转）。

| # | 一句话原则 | 解决什么问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| S-1 | 体贴：不假设用户处境完美 | 设计只在理想条件下成立 | 每种屏幕、平台、语言、国家都能用；为不同需求给不同路径 | experience-values「Considerate」 |
| S-2 | 赋能：帮用户完成，但不替他做决定 | 自动化剥夺控制感 | 最重要的任务最顺，其他任务不被挡住；复杂度藏起来，但需要时拿得到 | 同上「Empowering」 |
| S-3 | 精致：用好用让人惊喜，不用装饰 | 用视觉花样掩盖难用 | 原文：「not with extra decoration or flair」；细节和小处体现用心 | 同上「Crafted」 |
| S-4 | 高效：重视生产力胜过单纯的快和简单 | 为了少一步牺牲正确 | 拆步骤、去掉重复；**用摩擦突出重要决定**，然后让人回去干活；批量和自动化 | 同上「Efficient」 |
| S-5 | 可信：坦白能做什么、不能做什么 | 小错误和不一致侵蚀信任 | 修小错；安全操作零摩擦，有风险的给说明和控制；出错容易恢复 | 同上「Trustworthy」 |
| S-6 | 熟悉：同样的原则、同样的行为 | 每个模块一套交互 | 沿用通行模式；新版本无缝演进 | 同上「Familiar」；[应用设计指南](https://shopify.dev/apps/design-guidelines)要求应用和后台外观、行为一致 |
| S-7 | 动效有目的、跟着操作、要利落 | 动效变成装饰或娱乐 | 只动一个元素就够说明上下文；动效大小和操作大小相称；先快后慢 | [`design/motion/index.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/design/motion/index.mdx)、[`creating-motion.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/design/motion/creating-motion.mdx) |
| S-8 | 字是设计的一部分，每个字都要称重 | 文字太多显得廉价又难用 | 能用图标就不用字（「+」而不是「+ 添加」）；像叠叠乐一样删到快塌为止 | [`content/fundamentals.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/content/fundamentals.mdx) |

### 2.3 能直接用的规则

| 编号 | 规则 | 怎么判 | 为什么 | 出处 |
|---|---|---|---|---|
| SR1 | 界面文字按美国 7 年级阅读水平写；用标题、列表、短句 | 英文用 Hemingway 一类工具测；中文按我们 C1、C2 | 读者最广时理解最快 | [shopify.dev 内容指南](https://shopify.dev/docs/apps/design/content.md)、fundamentals |
| SR2 | 一个东西、一个动作只用一个叫法（不要一处「上传图片」一处「添加照片」） | 术语表 + 全文搜同义词 | 同义词让人以为是两件事 | 同上 |
| SR3 | 按钮以表示动作的强动词开头，写成「动词 + 对象」（「添加顾客」「删除商品」） | 逐个读 | 一看就知道点了会怎样 | 同上；[`patterns/common-actions`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/patterns/common-actions/variants/best-practices.mdx) |
| SR4 | 不在标题栏下重复页面标题；同一页不用两种方式呈现同一内容 | 看截图 | 重复是噪音 | [shopify.dev 内容指南](https://shopify.dev/docs/apps/design/content.md) |
| SR5 | 错误提示说清哪里错、怎么修；具体到数字、日期甚至用户自己的数据；不说「无效」；不是我们的错就不道歉、不提「我们」 | 逐个触发错误 | 用户要的是出路，不是歉意 | [`content/error-messages.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/content/error-messages.mdx) |
| SR6 | 多个错误时写「保存前要改 2 处：填标题、加重量」，不写「本页有 2 个错误」 | 逐个读 | 把错误改写成待办 | 同上 |
| SR7 | 错误放在要改的地方旁边；红色只给马上要处理、否则会伤害业务的，黄色给日常流程里的警告 | 看截图 | 严重程度一眼可辨 | 同上 |
| SR8 | 日常任务的完成用不打扰的确认（例如吐司）；**不把简单步骤叫「成功」**；庆祝很少用，只给真正重要的里程碑，不抢用户的功劳 | 数页面里的庆祝和「成功」 | 过度庆祝显得假、打扰 | [voice-and-tone](https://shopify.dev/docs/apps/design/content/voice-and-tone.md) |
| SR9 | 不写「每个」「所有」「大多数」这类泛化成功的词；不承诺结果 | 搜词 | 夸大损害信任 | 同上 |
| SR10 | 新功能公告能关掉、能推迟 | 每个公告找关闭入口 | 不强迫 | 同上 |
| SR11 | 严重问题写清对业务的影响；没有修复办法就直接说，并说正在做什么；安抚要有数据或背景支撑 | 读严重错误文案 | 坦白比含糊更让人信 | 同上 |
| SR12 | 交互反馈克制而清楚，同一种交互全后台同一种反馈 | 对照控件状态表 | 不一致会破坏模式 | [`design/interaction-states.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/design/interaction-states.mdx) |
| SR13 | 一次转场只动一个元素；不让页面上所有变化的元素同时动 | 录屏数同时在动的元素 | 全部一起动让人迷失 | [`creating-motion.mdx`](https://github.com/Shopify/polaris/blob/main/polaris.shopify.com/content/design/motion/creating-motion.mdx) |
| SR14 | 先移动端设计 | 先出手机稿 | 大部分商店流量在手机 | [应用设计指南](https://shopify.dev/apps/design-guidelines) |
| SR15（Sidekick） | **Agent 不经批准不改线上数据**：生成的内容带「应用」按钮；改动先成为草稿卡片，用户点「开始检查」后自己发布 | 每个写操作都有一个用户点的发布动作 | 可撤回性由「先草稿」保证 | [Sidekick 功能](https://help.shopify.com/en/manual/shopify-admin/productivity-tools/sidekick/features)、[Sidekick Pulse](https://help.shopify.com/manual/ai-powered-tools/sidekick/pulse) |
| SR16（Sidekick） | 主动建议一次最多 5 条，每条能用 × 关掉，关掉的理由可选填，用来调整之后的建议 | 数卡片；找关闭 | 主动但不压人 | [Sidekick Pulse](https://help.shopify.com/manual/ai-powered-tools/sidekick/pulse) |
| SR17（Sidekick 工程） | 指令随工具结果「即时」给，不全塞进系统提示；工具保持少（0–20 个边界清楚，50 个以上就会出现多种做法） | 数工具、数常驻指令 | 「千条指令之死」；指令越多越不可靠 | Andrew McNamara，[Building production-ready agentic systems](https://shopify.engineering/building-production-ready-agentic-systems)，2025-08-26 |

### 2.4 批判

- **高密度只适合后台。** Polaris 的「Pro 设计语言」明说后台默认高密度、为每天重复的任务服务；内容站和第一次来的读者要的是低密度和留白。这条不能借。
- **「图标代替文字」和我们的 C10 有冲突。** Polaris 说常用动作（添加、编辑、删除、复制）可以只用图标、不带文字，前提是商家每天用、已经认得。大众产品的访客多半第一次来，我们继续只允许通行图标（搜索、关闭、播放、暂停、菜单）单独出现。
- **「不加标点」不适用中文。** fundamentals 说短文字不加句号（两句以上除外）；这条对英文按钮和标签可以借，中文的标点规则以 Fenng 指南和 `velicoach-content` 为准。
- **内部的张力：高效 vs 摩擦。** 「去掉重复任务」和「用摩擦突出重要决定」都对，但 Polaris 没给判断标准，哪些算「重要决定」要产品自己定。这正好是我们 Veli 的自主等级（A/S/B/C/D）在做的事。
- **Sidekick 的公开设计原则很少。** 官方只公开了工程文章和帮助页，没有面向设计的原则页；工程文章里关于评测（真实对话抽样、至少 3 位专家标注、评委和人的一致度从 0.02 提到 0.61）的部分比 UI 部分更有用。

---

## 3. Anthropic / Claude

### 3.1 结论

Anthropic 公开讲的设计取舍集中在**人怎么监督 Agent**，结论很清楚：**先简单，再透明；监督从「每一步批准」移到「看计划、可随时打断、高风险才确认」**。证据是它自己的数据：用户对确认请求 93% 都点同意（确认疲劳）；有经验的用户更常全自动，但打断也更多（5% → 9% 的轮次）——好的监督是「看着、必要时插手」，不是「每步点同意」。宪法里和体验直接相关的是：诚实到「外交式的诚实，而不是不诚实的外交」、不讨好、不追求过度的参与和依赖、尊重用户自己做决定，同时**不把「不帮忙」当成安全**——多余的警告、免责和说教都是体验缺陷。

### 3.2 核心思想

| # | 一句话原则 | 解决什么问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| A-1 | 先用最简单的方案，确实需要才加复杂度 | 一上来就做多 Agent、大框架 | 能用固定流程就不用 Agent；Agent 有停止条件（例如最大轮数） | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)，2024-12-19 |
| A-2 | 把 Agent 的计划步骤明明白白给人看 | 人看不见 Agent 在干什么就无法纠偏 | 实时待办清单；计划模式先给全盘计划，人改完再执行 | 同上；[安全可信 Agent 的框架](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)，2025-08-04；[Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents)，2026-04-09 |
| A-3 | 人在关键处保留控制，但不是每一步 | 确认疲劳：93% 的确认请求都被点了同意 | 默认只读；按动作设「总是允许 / 要批准 / 禁止」；随时能停；常用操作能永久授权 | [How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)，2026-03-25；框架文章 |
| A-4 | 按风险自动放行，挡住的换安全做法，屡次被挡才找人 | 全自动危险，全手动没人看 | 分类器先审每个工具调用；连续 3 次或累计 20 次被拒才交给人；分类器漏判 17% 的「过度积极」动作，所以高风险基础设施仍要人审 | auto mode 工程文章；[Auto mode 产品博客](https://claude.com/blog/auto-mode) |
| A-5 | 遇到只有用户能回答的偏好和意图问题，停下来问 | Agent 自作主张做错方向 | 复杂任务上 Claude 主动停下的次数是简单任务的两倍多；最常见的理由是「请你在几种做法中选一个」（35%） | [Measuring agent autonomy](https://www.anthropic.com/research/measuring-agent-autonomy)，2026-02-18；Trustworthy agents |
| A-6 | 不可撤回的动作前确认 | 提示注入和误操作 | 提交表单、购买、发消息、改数据前停下请求确认；原文称这是对提示注入「最有效的单一缓解」；每步留截图便于事后查 | [电脑和浏览器使用的最佳实践](https://claude.com/resources/articles/best-practices-for-computer-and-browser-use-with-claude)，2026-05-13 |
| A-7 | 必须每次都发生的规则交给程序执行，不写在说明里 | 模型会认为某条指南「这次不适用」 | 「永远不能」放进 hook、拒绝规则、托管设置；说明文件保持短；给 Agent 一个能返回通过或失败的检查，并要求它拿出证据（命令和输出、截图） | [Claude Code 最佳实践](https://code.claude.com/docs/en/best-practices) |
| A-8 | 诚实、不讨好、尊重自主，但不过度谨慎 | 讨好、空洞的保守回答、说教 | 校准的信心；主动说出有用的信息；不制造过度依赖；能提出顾虑但尊重用户的决定；不加不必要的警告和免责；只在真的有歧义时提问 | [Claude 的宪法](https://www.anthropic.com/constitution) |

**产品上公开讲过的取舍**

- **Artifacts**：把产出放在对话旁边的独立窗口里，让人能查看和修改，从「对话」变成「一起工作的环境」（[Claude 3.5 Sonnet 发布](https://www.anthropic.com/news/claude-3-5-sonnet)，2024-06-21）。取舍：对话保持短，产出可以长、可编辑；代价是两块区域要同步。
- **Claude Code**：默认只读、改动要问；后来改成默认 auto mode，由分类器审风险动作，因为逐条批准挡住了长时间无人看守的运行（auto mode 两篇）。「永远不能」的规则放 hook，不放 CLAUDE.md（最佳实践）。
- **Computer use**：不可撤回的动作前确认；每步截图存档；截图贵（每张约 1000–1800 个 token），所以只留最近几张；不要用会让 Agent「看不到真实状态」就连做多步的批量工具（浏览器最佳实践）。
- **Claude Design**：对话出第一版，然后**行内评论、直接改字、用调节旋钮现场调间距颜色和版式**；入门时读代码库和设计文件建一份设计系统，之后每个项目自动用；完成后打包交给 Claude Code（[Claude Design 发布](https://www.anthropic.com/news/claude-design-anthropic-labs)，2026-04-17）。做它的设计师 Nate Parrott 的说法：不给方向，Claude 会落到「它偏爱的几种审美」；多出几版再挑，大多数不好也没关系；最后的微调用手改，比用嘴描述更准（[Nate Parrott 访谈](https://claude.com/resources/articles/how-the-product-designer-who-built-claude-design-uses-it-to-explore-ideas-before-building-them)，2026-07-24）。

### 3.3 能直接用的规则

| 编号 | 规则 | 怎么判 | 为什么 | 出处 |
|---|---|---|---|---|
| AR1 | 每个 Agent 动作标出风险等级；只有不可撤回或影响他人的动作要用户确认，其余自动执行并可撤销 | 列出所有动作和等级，数确认弹窗只出现在不可撤回的动作上 | 93% 的确认被点同意，说明逐条确认没人看 | auto mode 工程文章；浏览器最佳实践 |
| AR2 | 多步任务开工前给出计划，用户能改、能批准；执行中任何时刻能打断，打断后从原状态继续 | 走一遍：计划可编辑；执行中点停止后进度不丢 | 监督从步骤移到策略 | Trustworthy agents；框架文章 |
| AR3 | 执行中显示实时进度清单，当前步骤高亮 | 看截图 | 透明 | 框架文章 |
| AR4 | Agent 主动提问只在「偏好或意图」上，一次给出几个选项让人选，而不是开放式提问 | 抽查 Agent 的提问，至少给出 2 个可点的选项 | 最常见的有效提问就是「选一个做法」 | Measuring agent autonomy |
| AR5 | 被安全规则挡住时，Agent 换一条安全的路，不绕过；屡次被挡才交给人，并说清被挡的原因 | 构造被挡场景看行为 | 避免「为了完成任务而绕过检查」 | auto mode 工程文章 |
| AR6 | Agent 说「完成了」时附证据（运行的检查和输出、截图），不只说「测试都过了」 | 看完成消息里有没有证据 | 自我报告不可信 | Claude Code 最佳实践 |
| AR7 | 「必须每次都做」的规则用程序执行；如果一条说明加了「重要」还被忽略，就把它改成 hook 或检查；反过来只是偏好的就删掉 hook | 数常驻说明和强制规则 | 说明是给模型权衡的，规则是给程序执行的 | 同上 |
| AR8 | 回答长度匹配请求：没有填充、重复和多余的免责；需要完整时不截短 | 抽查回答 | 宪法把过度谨慎列为有代价的失败 | 宪法 |
| AR9 | 不用讨好和制造依赖的手法：不夸大赞美、不刻意延长对话、不制造「离不开」 | 抽查文案和推送 | 原文对比了「为参与度优化的媒体」，要像「关心我们的可信朋友」那样吸引人 | 宪法 |
| AR10 | 用户坚持自己的做法时，Agent 说一次顾虑，然后照做（在安全范围内） | 抽查 | 尊重用户在自己事情上的决定权 | 宪法 |

### 3.4 批判

- **多数是开发者场景的结论。** 93%、5% → 9% 都来自 Claude Code 用户（程序员）。大众用户对「风险分级」的直觉更弱，更需要每次确认时说清「这一步会发生什么、能不能撤回」，不能直接照搬开发者的放行比例。
- **「透明」和「少打扰」互相拉扯，它自己也承认。** 框架文章说透明的细节多了少了都有问题；Trustworthy agents 说并行的子 Agent 让流程更难看清，还在找办法。没有现成的数值可借。
- **auto mode 是用一个模型监督另一个模型。** 漏判率 17% 是它自己公开的；把「分类器放行」当成「已经安全」是错的，涉及钱、健康和对外发送的动作仍要人确认。
- **宪法讲的是模型的行为，不是界面规则。** 「不讨好」「尊重自主」要翻译成界面上可查的东西（例如不预勾选、不倒计时、关掉一步完成），否则无法验收。我们的 T9 已经在做这件事。
- **Claude Design 的「设计系统自动套用」只在给了权限、设置好之后才成立**，而且发布文章里没描述设计稿交给 Claude Code 之前的审查步骤——这一步我们要自己补（关口三 a 的验证）。

---

## 4. OpenAI

### 4.1 结论

OpenAI 的两套东西分别回答了两个问题。**Apps SDK 的 UI 指南**回答「在别人的对话里放界面」：界面只在「可视交互确实让流程更好」时才出现，内联卡片最多两个操作、不嵌套滚动、不深层导航，颜色字体图标一律用宿主的，「做完你那部分就把控制还给对话」。**Operator / ChatGPT agent** 回答「Agent 替人操作」：随时打断和接管，敏感输入（登录、付款）交给人自己输入且不截屏，有实际后果的动作前明确请求许可，敏感网站上开「监看模式」，用户离开就暂停。两套都偏保守，代价是品牌和表达空间很小。

### 4.2 核心思想

| # | 一句话原则 | 解决什么问题 | 可观察的特征 | 出处 |
|---|---|---|---|---|
| O-1 | 扩展对话，不打断对话 | 应用把用户拖出对话、变成另一个 App | 每个应用先以内联方式出现，且出现在模型回答之前；全屏时宿主的输入框仍浮在上面 | [UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines) |
| O-2 | 只有可视交互让流程更好时才给界面 | 能用一句话说清的也做成卡片 | 每种显示方式有明确的「什么时候用」 | 同上 |
| O-3 | 像宿主，不像自己 | 各家品牌风格把平台弄乱 | 系统颜色、字体、图标、网格、圆角；品牌色只用在主按钮上；不放自己的标识（宿主会加） | 同上「Visual design」 |
| O-4 | 能力，而不是把产品搬进来 | 把整个网站塞进对话 | 只做几件最拿手的事；每个应用至少在「知道、做到、展示」三者之一上有增益 | Corey Ching，[What makes a great ChatGPT app](https://developers.openai.com/blog/what-makes-a-great-chatgpt-app)，2025-11-24 |
| O-5 | 第一轮就有用 | 长长的引导流程 | 意图模糊时最多问一两个问题就给出具体结果；意图明确时不让用户重复；陌生品牌一句话说清自己 | 同上 |
| O-6 | 不暗示做得到其实做不到的事 | 名字和描述许诺过多 | 每个用户期待要么支持，要么有明确的不支持理由；说得出自己不能做什么并给下一步 | [UX principles（用例规划）](https://developers.openai.com/apps-sdk/concepts/ux-principles) |
| O-7 | 用户随时能打断、接管，敏感输入由人来 | Agent 处理密码、付款的风险 | 接管模式下输入不被收集或截屏；登录、付款、验证码时主动请人接管；卡住时把控制交回 | [Introducing Operator](https://openai.com/index/introducing-operator/)，2025-01-23 |
| O-8 | 有实际后果的动作前请求许可；敏感网站上要人看着 | 误购、误发、提示注入 | 购买、发邮件前停下；监看模式下用户离开对话就暂停；任务完成时在手机上通知 | [Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/)，2025-07-17；[系统卡片：监看模式](https://deploymentsafety.openai.com/chatgpt-agent/watch-mode) |

### 4.3 能直接用的规则

| 编号 | 规则 | 怎么判 | 为什么 | 出处 |
|---|---|---|---|---|
| OR1 | 内联卡片最多 2 个操作：1 个主操作、1 个可选的次操作；操作要么发起一轮对话，要么调一个工具 | 数按钮 | 卡片是决定点，不是控制台 | UI guidelines |
| OR2 | 卡片里不深层导航、不分多视图、不放标签页、不嵌套滚动；高度随内容长，最多到手机屏高 | 看截图；滚动测试 | 嵌套滚动在手机上互相抢手势 | 同上 |
| OR3 | 轮播 3–8 项，每项有图，元数据尽量 2 行以内（最多 3 行），每项最多 1 个操作 | 数 | 可比较、可扫读 | 同上 |
| OR4 | 全屏只给「一张卡片放不下」的任务（地图、画布、详细列表），全屏里宿主输入框照常能用 | 每个全屏场景写出理由 | 不让全屏变成逃离对话的出口 | 同上 |
| OR5 | 画中画随对话输入更新；会话结束自动关掉；不堆控件和静态内容 | 走一遍 | 平行任务不压过主线 | 同上 |
| OR6 | 不用自定义字体（全屏也不行）、不用自定义渐变和花纹；字号变化少，优先正文和小正文两档；粗体、斜体、高亮只用在内容里，不用在界面结构上 | 读样式 | 宿主的「极简外观」 | 同上 |
| OR7 | 不在卡片里复制宿主已有的功能（例如再放一个输入框） | 看截图 | 两个输入框让人不知道往哪打字 | 同上 |
| OR8 | 内容顺序：标题 → 说明 → 操作 | 看截图 | 先懂再做 | 同上 |
| OR9 | 文字对比度达 WCAG AA；每张图有替代文字；文字放大不坏版 | 自动检查 | 同上 | 同上 |
| OR10 | 卡片之后模型的跟进只提示编辑、下一步或相关动作，**不重复卡片里已有的内容** | 抽查回答 | 重复是噪音 | [design-guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines) |
| OR11 | 只收必要的字段；需要账号权限时用一句话说明为什么 | 数字段；读说明 | 少要、说清 | What makes a great ChatGPT app |
| OR12 | 做完你那部分就把控制还给对话，不做隧道式长流程 | 数一个任务里离不开应用的步数 | 用户的主线在对话里 | 同上 |
| OR13 | 让用户用一句话表达筛选，而不是给一排筛选侧栏（例如「欧洲、晴天、200 美元以下」） | 看有没有自然语言入口 | 语言比控件快 | [15 lessons](https://developers.openai.com/blog/15-lessons-building-chatgpt-apps)（Alpic 的 Nikolay Rodionov 写在 OpenAI 开发者博客上，2026-02-04，算准一手） |
| OR14 | Agent：接管时用户的输入不收集、不截屏；登录、付款、验证码主动请人接管 | 走一遍 | 敏感信息不进 Agent | Introducing Operator |
| OR15 | Agent：购买、发消息、改权限前明确请求许可；系统卡片公布的关键确认召回率是 99.9%–100% | 构造这几类任务，数没确认就执行的次数，应为 0 | 不可撤回 | 系统卡片：监看模式 |
| OR16 | Agent：能暂停、要进度摘要、停止并拿到部分结果；被打断后从上次状态继续 | 走一遍 | 停下不等于白干 | Introducing ChatGPT agent |

### 4.4 批判

- **「像宿主」只在别人的平台上成立。** 不准用自定义字体、渐变、标识，是因为应用活在 ChatGPT 里。我们的主站是自己的地盘，可以有品牌；但规则背后的道理——**品牌表达不能干扰任务**——对我们同样成立。
- **「最多两个操作」和「一个区域一个主操作」同源**，都是「一个决定点只问一件事」；但 OpenAI 的「两个」包括次操作，我们的 U3 只数主操作，两者不矛盾。
- **文档改版快，原则会消失。** 你提到的「conversational, intelligent, simple, responsive, accessible」五条，在现在的官方页面里找不到了；当前版本只剩「扩展对话」「只在有帮助时给界面」「可预测」「像原生」「无障碍」。引用时要写查询日期，旧版本不能当一手出处。
- **监看模式是用打扰换安全。** 用户一离开就暂停，对长任务不友好；OpenAI 自己说会根据其他缓解手段「重新考虑」。它适合高风险、短时的步骤，不适合当默认。
- **Agent 的确认靠模型自己判断「这算不算有后果」**，召回率 91% 不是 100%；关键类别靠专门训练才到 100%。对我们来说，「哪些动作必须确认」要由代码按清单决定，不能交给模型判断——这和 Veli 的「数字和安全只由代码决定」一致。

---

## 5. 跨四家：互相矛盾的规则和各自的适用范围

### 5.1 互相矛盾

| 矛盾 | 一方 | 另一方 | 怎么取舍 |
|---|---|---|---|
| 信息密度 | Polaris：后台默认高密度 | OpenAI：卡片元数据 2 行以内、字号两档 | 按任务定：每天重复的工具用高密度，第一次来的读者用低密度。我们是后者 |
| 只用图标 | Polaris：常用动作只用图标 | Vercel：图标要有文字（至少给读屏）；OpenAI 未规定 | 熟练用户的工具可以只用图标；大众产品只放通行图标，其余带字（保留 C10） |
| 确认还是撤销 | Vercel：确认或撤销二选一；Polaris：重要决定加摩擦 | Anthropic：逐条确认造成确认疲劳 | 能撤销就撤销；撤销不了（对外发送、付款、删除他人可见的内容）才确认，而且确认要说清后果 |
| 透明还是少打扰 | Anthropic：展示计划步骤；OpenAI：实时旁白 | Anthropic 自己：信息多了少了都不好 | 默认一行当前步骤 + 可展开的清单；不把全部日志摆出来 |
| 自动聚焦 | Vercel：桌面单个主输入时自动聚焦 | 无障碍：抢走阅读起点 | 只在「来这页就是为了输入」的页面（搜索页、登录弹层）自动聚焦 |
| 对比度算法 | Vercel：优先 APCA | WCAG 2（法规、工具） | 验收用 WCAG 2；APCA 只作参考 |
| 品牌表达 | Vercel、Anthropic 的 Claude Design：品牌一致自动化 | OpenAI：平台上不准有品牌字体和渐变 | 取决于在谁的地盘上 |

### 5.2 只适合它自己的场景

- **Vercel**：Title Case、`&`、阿拉伯数字计数、`YOUR_API_TOKEN_HERE` 占位符——开发者工具的品牌偏好，它自己标了「不是通用准则」。
- **Shopify**：Pro 高密度、只用图标的常用动作、红黄两色的错误严重度——为每天用后台的商家设计。
- **Anthropic**：auto mode 的放行比例、子 Agent、hook——开发者和代码仓库的场景。
- **OpenAI**：内联卡片、画中画、宿主输入框——只在对话宿主里成立。

### 5.3 提炼：能用到任何产品的 12 条

网页 GUI 和人与 Agent 协作的界面都适用；每条都能判对错。

| # | 规则 | 怎么判 | 依据 |
|---|---|---|---|
| G1 | 一个决定点只问一件事：一个区域 1 个主操作，最多再加 1 个次操作 | 数按钮 | OR1；我们的 U3 |
| G2 | 按钮写成「动词 + 对象」，写出点了得到什么；同一个动作全产品一个叫法 | 逐个读；术语表 | SR2、SR3、VR29 |
| G3 | 错误提示 = 发生了什么 + 怎么修 + 一个修的入口；不写「无效」，不给错误码 | 逐个触发 | SR5、VR29、VR5 |
| G4 | 每个屏幕有下一步：空、稀疏、密集、错误四种状态都有设计 | 逐个触发 | V-6 |
| G5 | 状态不丢：刷新、分享、后退后，筛选、展开、滚动位置、输入了一半的内容都还在 | 刷新、后退测试 | VR11、VR12 |
| G6 | 加载反馈：0.1 秒内有按下反馈；转圈延迟约 150–300ms 出现、出现后至少约 300–500ms；按钮文字和宽度不变 | 录屏 | VR1、VR2；Nielsen |
| G7 | 能撤销就不确认；不可撤回的才确认，确认框写清后果 | 列出所有动作，标「可撤销 / 需确认」 | VR13、AR1、S-5 |
| G8 | Agent 的多步任务：先给可改的计划，执行中显示当前步骤，随时能停、停了不丢进度，完成时附证据 | 走一遍 | AR2、AR3、AR6、OR16 |
| G9 | Agent 主动提问只问偏好和意图，给可点的选项 | 抽查 | AR4、O-5 |
| G10 | 敏感输入（密码、付款）由人自己输入，Agent 不看、不存 | 走一遍 | OR14 |
| G11 | 动效先过必要性检查：只为说清因果或一处刻意的惊喜而动，一次只动一个元素，可打断，尊重减弱动态 | 录屏数同时动的元素 | V-7、SR13、VR16 |
| G12 | 规则分两类：判断写成文字，机械的写成检查；同一条意见第二次出现就写成检查 | 每条意见有去处（检查或规则） | V-1、AR7 |

---

## 6. 对照我们现有的原则

只写结论和理由。「支持」= 研究里有一手来源和它一致；「挑战」= 研究给出了改它的理由；「未涉及」= 四家没有相关内容，保持不动。

### 6.1 `docs/standards/quality-terms.md` §4

**好用（U）**

| 规则 | 结论 | 理由 |
|---|---|---|
| U1 核心旅程两步内 | **部分挑战** | 少步数和 Polaris「高效」一致；但 Polaris 也说「用摩擦突出重要决定」，Anthropic 的数据说明该停的地方要停。步数预算要允许「不可撤回的动作多一步确认」，否则规则会逼着删掉必要的确认。建议在 U1 加一句：确认不可撤回动作的那一步不计入预算 |
| U2 首屏回答三件事 | 支持 | Polaris「聚焦下一件要做的事」、OpenAI「第一轮就有用」 |
| U3 一个区域 1 个主操作 | 支持 | OpenAI 卡片 1 主 1 次；Polaris 用按钮层级表达重要性 |
| U4 主导航 ≤ 6 项 | 未涉及 | 四家没有给数 |
| U5 标签说出去处或结果 | 支持 | Vercel「不写『继续』，写『保存 API 密钥』」；Polaris 动词 + 对象 |
| U6 能退出；能撤回的用撤销 | 支持，**补一条** | Vercel「确认或撤销」二选一与此一致。补：撤不回的（订阅提交后的邮件、对外发送）确认框写清后果 |
| U7 一站 | 支持 | OpenAI「做完就把控制还给对话」、不搞隧道式流程，是同一个道理在宿主场景的版本 |
| U8 一秒 | 支持，**补数** | Vercel 给了更细的数：写操作 < 500ms、转圈延迟 150–300ms 出现并至少显示 300–500ms（防闪）。现在的 U8 只管慢，不管「快到闪一下」 |
| U9 三种状态、0.1/1/10 秒 | 支持 | Vercel「交互时对比度更高」、Polaris「克制但清楚」 |
| U10 渐进披露、展开不挤动版面、同一操作同一控件 | 支持 | Polaris「熟悉」「复杂度藏起来但拿得到」；Vercel 骨架屏不移位 |
| U11 键盘能做完全部操作 | 支持 | Vercel「键盘到处可用」「焦点不被吸顶条挡住」 |
| U12 出错有出路、六种页面状态 | 支持 | Vercel「没有死胡同」「四种状态都设计」 |
| U13 换姿态不打断 | 支持 | Vercel「状态写进 URL、后退恢复滚动」是同一类；可补「状态写进 URL」 |

**好懂（C）**

| 规则 | 结论 | 理由 |
|---|---|---|
| C1 句长 | 支持 | Polaris 7 年级阅读水平、短句 |
| C2 段长 | 支持 | 同上 |
| C3 用术语表的叫法 | 支持 | Polaris「一个东西一个叫法」、Vercel「名词保持一致」 |
| C4 按钮动词 + 对象，≤ 8 字 | 支持 | Polaris common-actions；Vercel |
| C5 错误提示说清怎么办，不给错误码 | 支持 | Polaris 错误规范几乎逐字一致；可补 Polaris 的「多个错误写成待办」 |
| C6 不造词、不用空话 | 支持 | Polaris「不夸大」「不写『每个』『所有』」 |
| C7 中英两版，英文重写 | 支持 | Vercel 语言按 `Accept-Language` 不按 IP；可补 `translate="no"` 保护专名 |
| C8 每张图讲清一个意思 | 未涉及 | |
| C9 文章结构 | 未涉及 | |
| C10 不用读就会用 | 支持，**与 Polaris 有分歧** | Polaris 允许常用动作只用图标；那是给每天用的商家。我们的访客多半第一次来，保留「只有通行图标能单独出现」 |

**好看（V）**

| 规则 | 结论 | 理由 |
|---|---|---|
| V1 字体三种 | 未涉及（OpenAI 的「不用自定义字体」只在宿主内成立） | |
| V2 强调色只给主操作、链接、当前所在 | 支持 | OpenAI「品牌色只用在主按钮」 |
| V3 每区域只放标题、一句说明、操作 | 支持 | OpenAI「标题 → 说明 → 操作」 |
| V4 同层级同一种排法 | 支持 | Polaris「熟悉」、Vercel「刻意对齐」 |
| V5 玻璃 | **挑战** | 见 §6.3 |
| V6 只引用 token、对齐栅格 | 支持 | Vercel「每个元素都刻意对齐」；design.md 用样式表约束机械部分 |
| V7 动效有含义、每屏最多一个主动效 | 支持 | Vercel 必要性检查、Polaris 有目的且一次只动一个元素 |
| V8 元信息克制 | 未涉及 | |
| V9 排版细节 | 支持 | Vercel 避免孤字、用 `…`、不换行空格；可补「数字和单位之间用不换行空格」「比较数字用等宽数字」 |
| V10 没有模板味、换名测试 | 支持 | design.md 给反模式起名字，正是这条的做法；Nate Parrott：不给方向就落到「它偏爱的审美」 |

**可信（T）**

| 规则 | 结论 | 理由 |
|---|---|---|
| T1–T5 出处、来源、日期、纠错、授权 | 未涉及（与 Polaris「坦白能做什么不能做什么」方向一致） | |
| T6 「我们的判断」写清代价 | 支持 | 宪法「校准」「主动说出有用信息」 |
| T7 讲原因、代价、适用范围 | 未涉及 | |
| T8 健康内容 | 未涉及 | |
| T9 不操纵 | 支持 | 宪法不讨好、不制造依赖；Polaris 公告能关能推迟、不承诺结果 |
| T10 对外只放正式版 | 支持 | OpenAI「不暗示做得到其实做不到的事」 |

**舒适（A）**

| 规则 | 结论 | 理由 |
|---|---|---|
| A1 对比度 4.5:1 / 3:1 | 支持 | Vercel 建议 APCA，我们不跟（法规和工具） |
| A2 可点区域 ≥ 44px | 支持 | 比 Vercel（桌面 24px、手机 44px）更严，没有问题 |
| A3 320px 不横滚、放大 200% | 支持 | OpenAI「文字放大不坏版」 |
| A4 动效能停、减弱动态 | 支持 | Vercel 与此逐条一致 |
| A5 不打扰、不首访弹窗 | 支持 | Polaris 公告能关能推迟 |
| A6 读起来不累 | 未涉及 | |
| A7 媒体有替代 | 支持 | Vercel、OpenAI 都要求 |
| A8 折痕 | 未涉及 | |

### 6.2 `velicoach-layout` §3、§7

| 条目 | 结论 | 理由 |
|---|---|---|
| §3 一站、一键、一秒 | 支持，补两处 | 同 U1、U8：确认步不计入预算；补「转圈延迟出现、最短显示」 |
| §3 首屏就是操作台、按钮直达结果 | 支持 | OpenAI「第一轮就有用」、Polaris「聚焦下一件事」 |
| §3 原地展开：悬停 80ms 展开、离开 300ms 收起 | **部分挑战** | Vercel 讲「宽容的交互」（预测锥）和「同组第一个提示要延迟」。80ms 很可能让鼠标路过就误开；没有一手来源支持这个数。建议标成「自定」，并用真实鼠标轨迹测一次误开率再定 |
| §3 展开不挤动版面 | 支持 | Vercel 骨架屏不移位、防 CLS |
| §3 撤销代替确认、记住选择、认出回来的人 | 支持 | Vercel、Polaris；补「撤不回的才确认」 |
| §3 分清登录前后、位置预留不跳 | 支持 | Vercel 防 CLS、骨架和最终内容一致 |
| §3 在对的时刻提示 | 支持 | Polaris「激励行动时说清下一步和为什么」 |
| §3 不用操纵手段 | 支持 | 宪法；Polaris |
| §7 胶囊导航、同一时刻只吸一条 | 支持，补一条 | 补 Vercel「吸顶条不遮住焦点元素」（加 `scroll-margin-top` / `scroll-padding-top`） |
| §7 语言切换用语言名、是链接、带 `hreflang` | 支持 | Vercel「链接就用链接」「按语言设置不按位置」；补品牌名 `translate="no"` |
| §7 书脊 | 未涉及 | |
| §7 按钮：一个区域一个主按钮、加载中宽度不变、按下下移 1px | 支持 | Vercel「加载按钮保留原文字」、OpenAI 1 主 1 次 |
| §7 卡片整张可点、标题是链接文字 | 支持 | Vercel「看起来能点就能点」「没有死区」 |
| §7 订阅框原地展开、两步、原地显示结果 | 支持，补表单规则 | 补 Vercel：`type="email"`、`autocomplete="email"`、关拼写检查、回车提交、提交前不禁用按钮、错误放在框旁边并聚焦、去掉首尾空格 |

### 6.3 玻璃：`velicoach-layout` §8 与 `liquid-glass.md` 开头（§0–§2）

**结论：挑战。保留「玻璃只给背后会变的那一层」这个限制，但把默认翻过来，并砍掉透镜和色散。**

支持的部分：

- §0「平涂底色上的表面不动」「不叠玻璃」「声明要成立」：和 Polaris「精致来自好用，不来自装饰」、Vercel「必要性检查」一致，是对的方向。
- §8「玻璃上的文字按最差的背景算对比度」「降低透明度、强制颜色、不支持背景滤镜时换实色」：和 A1、Vercel「交互时对比度更高」一致。
- §1「悬停、按下改玻璃自己的 token，不叠灰层」：和 Polaris「同一种交互同一种反馈」一致。

挑战的部分：

1. **装饰的投入和收益不成比例。** 四家里没有一家把材质当体验的来源：Polaris 原文说惊喜要来自「有多强、多有效」而不是装饰；Vercel 只允许为说清因果或一处刻意的惊喜而动；OpenAI 直接要求去掉破坏「极简外观」的效果。我们的玻璃有边缘透镜、位移图、色散、背景采样脚本，外加「声明成立」「背后亮度变化 ≥ 0.04」「通栏另算」一整套检查。这些规则几乎都在防玻璃自己带来的问题，而不是在帮读者完成任务。
2. **性能风险没进规则。** Vercel 要求在 iOS 低电量模式和 macOS Safari 上测；`backdrop-filter` 加 SVG 位移滤镜在这两处最贵，而我们的 U8 要求 INP ≤ 200ms。现在的玻璃规范里没有性能预算。
3. **读者的任务是读和点，不是看背后。** 主站是内容站：导航压在正文上时，读者要的是「导航清楚、正文不打扰」，20px 模糊的吸顶条和实色吸顶条在这件事上差别很小。

建议（交给关口三 a 决定）：

- **实色是默认**；一个表面要用玻璃，先回答「读者透过它看到的东西有没有用」，答不出就用实色。吸顶导航可以留轻度模糊（这是浏览器原生能力，成本低），但不加透镜和内光。
- **透镜、色散、位移图整套去掉**，或者只在首页「叶与网」上留一处作为品牌签名，并写明性能预算（例如在中端安卓机上滚动帧率不低于 55fps、INP ≤ 200ms，自定，待实测）。
- 去掉之后，`verify_canvas.py` 里只为透镜服务的检查一起删（「先做减法」）。

---

## 7. 出处总表

| 公司 | 来源 | 日期 |
|---|---|---|
| Vercel | [How our agents build on brand pages with design.md](https://vercel.com/blog/how-our-agents-build-on-brand-pages-with-design-md) | 2026-08-31 |
| Vercel | [vercel-labs/web-interface-guidelines](https://github.com/vercel-labs/web-interface-guidelines)（README.md、AGENTS.md，提交 434b7f9） | 2026-10-05 |
| Vercel | [Geist 首页](https://vercel.com/design/introduction) | 查询日 |
| Shopify | [Shopify/polaris](https://github.com/Shopify/polaris)（提交 3f7954a）：`foundations/experience-values.mdx`、`content/fundamentals.mdx`、`content/error-messages.mdx`、`design/motion/*`、`design/interaction-states.mdx`、`design/pro-design-language.mdx`、`design/layout/density.mdx`、`patterns/common-actions` | 2026-09-10 |
| Shopify | [应用设计指南](https://shopify.dev/apps/design-guidelines)、[内容指南](https://shopify.dev/docs/apps/design/content.md)、[语气](https://shopify.dev/docs/apps/design/content/voice-and-tone.md) | 查询日 |
| Shopify | [Sidekick 功能](https://help.shopify.com/en/manual/shopify-admin/productivity-tools/sidekick/features)、[Sidekick Pulse](https://help.shopify.com/manual/ai-powered-tools/sidekick/pulse) | 查询日 |
| Shopify | [Building production-ready agentic systems](https://shopify.engineering/building-production-ready-agentic-systems) | 2025-08-26 |
| Anthropic | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 2024-12-19 |
| Anthropic | [Our framework for developing safe and trustworthy agents](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents) | 2025-08-04 |
| Anthropic | [Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy) | 2026-02-18 |
| Anthropic | [How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode) | 2026-03-25 |
| Anthropic | [Auto mode for Claude Code](https://claude.com/blog/auto-mode) | 2026-03-24（2026-07-10 更新） |
| Anthropic | [Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents) | 2026-04-09 |
| Anthropic | [Introducing Claude Design](https://www.anthropic.com/news/claude-design-anthropic-labs) | 2026-04-17 |
| Anthropic | [Best practices for computer and browser use](https://claude.com/resources/articles/best-practices-for-computer-and-browser-use-with-claude) | 2026-05-13 |
| Anthropic | [Nate Parrott 谈 Claude Design](https://claude.com/resources/articles/how-the-product-designer-who-built-claude-design-uses-it-to-explore-ideas-before-building-them) | 2026-07-24 |
| Anthropic | [Claude Code 最佳实践](https://code.claude.com/docs/en/best-practices) | 查询日 |
| Anthropic | [Introducing Claude 3.5 Sonnet（Artifacts）](https://www.anthropic.com/news/claude-3-5-sonnet) | 2024-06-21 |
| Anthropic | [Claude 的宪法](https://www.anthropic.com/constitution) | 查询日 |
| OpenAI | [Apps SDK UI guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)、[design-guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines)、[UX principles](https://developers.openai.com/apps-sdk/concepts/ux-principles) | 查询日（已改版为插件指南） |
| OpenAI | [What makes a great ChatGPT app](https://developers.openai.com/blog/what-makes-a-great-chatgpt-app) | 2025-11-24 |
| OpenAI | [15 lessons learned building ChatGPT Apps](https://developers.openai.com/blog/15-lessons-building-chatgpt-apps)（作者来自 Alpic，发在 OpenAI 开发者博客） | 2026-02-04 |
| OpenAI | [Introducing Operator](https://openai.com/index/introducing-operator/) | 2025-01-23（2025-07-17 更新） |
| OpenAI | [Introducing ChatGPT agent](https://openai.com/index/introducing-chatgpt-agent/) | 2025-07-17 |
| OpenAI | [ChatGPT agent 系统卡片：监看模式](https://deploymentsafety.openai.com/chatgpt-agent/watch-mode) | 查询日 |
