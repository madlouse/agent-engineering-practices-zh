# 质量词：把形容词和动词变成可检查的规则

> 建立：2026-11-04 · 产品负责人：「所有的点，包括需求点、原因和逻辑，都要做系统性的、批判性对抗的评审，用金字塔原理，确保不重不漏。不清晰的标准也必须有清晰的规则。比如『体验友好』：不是网上找找就行，要看有没有对标的产品，再基于对标产品的特征来定义。你说体验友好，就必须有几个特性、几条规则能把它评审清楚、定义清楚，不管是名词还是动词。」
> 以谁为准：质量词的意思以本页为准；本页和 PRD 冲突时以 PRD 为准，并回来改本页。
> 依据：三组对标研究（2026-11-04 查询，出处写在每条规则后面）；`design-bar` 的 `references/rubric.md`。查不到的写「未查到」，自己定的数写「自定」和理由，观察者两周后按数据复核。

## 1. 结论

**「体验友好」由好用、好懂、好看、可信、舒适五个维度组成，每个维度有对标产品和可检查的规则（§2、§4）。一个质量词只有在能判对错时才能用：它要有对标产品、从对标上观察到的特征、由特征推出的规则、检查方法和门槛。** 验收里出现没定义的质量词，或者「适当」「尽量」这类判不了对错的虚词，检查不通过（`npm run check:vague`）。

## 2. 总树：「体验友好」由五个维度组成

按用户心里的五个问题来分，一个问题对应一个维度，互不重叠：

| 维度 | 用户的问题 | 收进来的词 | 条目 |
|---|---|---|---|
| 好用 | 我能不能快、顺地做成想做的事？ | 好用、易用、易上手、简单、一眼、直观、顺手、流畅 | §4.1，规则 U1–U9 |
| 好懂 | 我看不看得懂？ | 易懂、易理解、通俗、白话、清楚、清晰 | §4.2，规则 C1–C6 |
| 好看 | 它看起来是不是用心做的、有自己的样子？ | 好看、美观、高级感、有品味、品味、极简、克制、精致、质感、赏心悦目、干净、苹果设计语言 | §4.3，规则 V1–V9；看清另加 K1–K7 |
| 可信 | 我信不信它说的？ | 专业、可信、有深度、有分量、值得读 | §4.4，规则 T1–T8 |
| 舒适 | 用着累不累、会不会被打扰？ | 舒服、舒适、不打扰、轻松 | §4.5，规则 A1–A7 |

- **体验友好**：五个维度的规则全部通过。
- **专业又通俗易懂**：可信（T）和好懂（C）同时通过。
- **拿奖级**：五个维度全部通过，再按 Awwwards 的权重评分：设计 40%、可用性 30%、创意 20%、内容 10%（[Awwwards 评审说明](https://www.awwwards.com/about-evaluation/)）。两份独立设计评审各打 1–10 分，加权平均都 ≥ 7.0，单项都 ≥ 6.5。6.5 是 Awwwards 荣誉提名的分数线（[FAQ](https://awwwards.com/faqs)）；7.0 是自定，留出余量。Awwwards 没有公布每日最佳的分数线（未查到）。

## 3. 怎么定义一个词

1. **先问用户因为它能做成什么**：每个质量词都回到 PRD 的目标，说不出对用户的作用，这个词就不该出现。
2. **选对标**，四条都满足：做的是同一类任务或面向同一类读者；有公认的证据（获奖、被同行引用、行业规范）；页面公开、能直接观察；至少两个来源，互相补充，避免照抄一家。
3. **观察对标**：只记能观察到的特征（数得出、量得出、截得到图），每条附网址和查询日期。查不到的写「未查到」。
4. **推规则**：几个对标共有的特征才变成规则；每条规则能用工具、计数或截图判定，写清门槛。
5. **对抗**：找反例，即满足了全部规则、用户仍然觉得不好的情况。找到就说明规则不完整，补一条。
6. **不重不漏**：一个词只归一个维度；同义词并进同一个条目；同一条规则只写在一个地方。

## 4. 五个维度的对标和规则

每条规则写：规则、怎么查、出处。「对标」一栏写选它的理由和观察到的特征。

### 4.1 好用（U）

**对标**：Linear 和 Raycast 的命令面板（按 ⌘K 输入动作名直接执行）；Stripe Link、Apple Pay、Google One Tap（认出老用户，一次点击完成）；NN/g 的十条可用性启发式。选它们，是因为它们都把「少一步」做成了产品的核心，有官方说明可查。

| 规则 | 怎么查 | 出处 |
|---|---|---|
| U1 核心场景两步内完成，不常用的不超过三步；悬停不算一步 | 按 PRD 步数预算逐条走一遍，记点按次数 | PRD 第 4 节；[NN/g：三次点击规则没有数据支持，真正起作用的是信息气味和速度](https://www.nngroup.com/articles/3-click-rule/) |
| U2 首屏回答三件事：这是给谁的、能做什么、下一步点哪里 | 关口四：5 个没看过的人看首屏 5 秒，至少 4 人答得出；之前由设计评审按截图回答 | [NN/g：用户在前 10 秒最容易离开](https://www.nngroup.com/articles/how-long-do-users-stay-on-web-pages/) |
| U3 一个区域只有 1 个主操作；整个首屏的主操作不超过 2 个 | 数截图上的实色主按钮 | 对标首屏：apple.com、stripe.com、vercel.com 各 2 个，linear.app 1 个；设计系统「一个区域只有一个主按钮」 |
| U4 主导航不超过 6 项 | 数导航 | linear.app、stripe.com、anthropic.com 各 6 项，vercel.com 4 项（apple.com 的 11 项是零售站，不算） |
| U5 导航标签和按钮文字说出去处或结果，不用「了解更多」「点击这里」 | 逐个读 | NN/g 信息气味；[Mailchimp](https://styleguide.mailchimp.com/web-elements/) |
| U6 每个弹层、展开和流程都有明显的退出：关闭按钮、Esc、点外面；能撤回的操作用「撤销」，不用「确定吗」 | 逐个试 | [NN/g 启发式第 3 条](https://www.nngroup.com/articles/ten-usability-heuristics/) |
| U7 看内容不要求登录；要登录时一次点击完成（One Tap、通行密钥） | 未登录走一遍关键路径 | [Google One Tap](https://developers.google.com/identity/siwg/features)；[Apple Pay 先买后注册](https://developer.apple.com/design/human-interface-guidelines/apple-pay) |
| U8 快：手机 75 分位 LCP ≤ 2.5 秒、INP ≤ 200 毫秒、CLS ≤ 0.1；操作 0.1 秒内有反馈，超过 1 秒显示状态，超过 10 秒显示进度 | 上线前用 Lighthouse 量实验室值；上线后看真实数据 | [Core Web Vitals](https://web.dev/articles/vitals)；[Nielsen 响应时间](https://www.nngroup.com/articles/response-times-3-important-limits/) |
| U9 同一种操作在全站用同一种控件、放在同一个位置 | 列出全站的控件清单逐个对照 | NN/g 启发式第 4 条 |

### 4.2 好懂（C）

**对标**：GOV.UK 的写作规范（政府服务，读者最广，规则带数值）；Microsoft、Apple 的界面文字规范；Fenng 的《中文技术文档写作风格指南》（[Fenng/Tech-Doc-Style-Chinese](https://github.com/Fenng/Tech-Doc-Style-Chinese)，带检查脚本）。中文没有查到带数值的公认白话规范，中文的数是自定。

| 规则 | 怎么查 | 出处 |
|---|---|---|
| C1 英文一句不超过 25 词；中文一句不超过 40 字（自定：按 GOV.UK 的 25 词折算，并和设计系统「导语每行不超过 32 字」相容） | 内容评审逐句看；超出的拆开 | [GOV.UK 句长](https://insidegovuk.blog.gov.uk/2014/08/04/sentence-length-why-25-words-is-our-limit/)：平均 14 词时理解 90% 以上，43 词时不到 10% |
| C2 一段只讲一件事；英文一段不超过 5 句，中文一段不超过 4 句（自定） | 逐段看 | [GOV.UK 清楚的语言](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/)；Fenng「一段一个主要信息点」 |
| C3 用术语表的叫法；术语和缩写第一次出现时给一句白话解释 | `npm run check:terms`；内容评审 | GOV.UK；Microsoft；`docs/GLOSSARY.md` |
| C4 按钮写成「动词 + 对象」，中文不超过 6 个字，英文不超过 4 个词（自定） | 逐个数 | [GOV.UK 按钮](https://design-system.service.gov.uk/components/button/)；Microsoft「几个短词」 |
| C5 错误提示说清哪里错了、怎么办；不怪用户，不给错误码 | 逐个触发错误状态 | NN/g 启发式第 9 条；[Microsoft](https://learn.microsoft.com/windows/uwp/design/style/writing-style)；Apple「写清是哪个字段、该填什么」 |
| C6 不造词；我们自己写的文字不用「赋能、抓手、闭环、打通」这类空词（译文照原文，原文这么写的保留） | `content-reviewer` 逐篇看；不进 `check:terms`，因为译文里有合法的用法 | Fenng 指南；`AGENTS.project.md` |

### 4.3 好看（V）

**对标**：apple.com、linear.app、stripe.com、vercel.com、anthropic.com（工程背景的产品站，公认的克制和品味）；Apple Human Interface Guidelines（苹果设计语言的唯一原文）。WebFetch 拿不到样式，对标站的版心宽度、玻璃、动效、主色数量**未查到**，关口三 a 用浏览器实测后补进来。

| 规则 | 怎么查 | 出处 |
|---|---|---|
| V1 正文最多 2 个字族（无衬线；看清另用衬线），等宽字体只用于代码和元信息；不用 Ultralight、Thin、Light 三档字重 | `check_page.py` 的字体统计；读 token | Linear（Inter 系）、Stripe（Söhne）、Anthropic（Styrene + Tiempos）；HIG「Minimize the number of typefaces」 |
| V2 每站 1 个强调色，只给主操作和状态；浅色、深色两套都有；不只靠颜色表达信息 | 读 token；截图对照 | Linear 的颜色系统只用 3 个变量；[HIG 颜色](https://developer.apple.com/design/human-interface-guidelines/color) |
| V3 首屏文字只有标题和一句说明：中文不超过 40 字，英文不超过 35 词 | 数截图上的字 | 五个对标站首屏都在约 35 词以内 |
| V4 一页的分区用同一种模块格式重复，一页 5–6 个分区 | 数分区 | apple.com 9 个推广模块同一格式；linear.app 6 个，stripe.com、vercel.com 各 5 个 |
| V5 玻璃只用在浮在内容上的导航和控件，正文内容层不用；玻璃上的文字对比度 ≥ 4.5:1，浅色深色各查；系统减少透明度时换成实色 | `verify_canvas.py`、`check_page.py` 的对比度；逐个找用了玻璃的元素 | [HIG 材质](https://developer.apple.com/design/human-interface-guidelines/materials)：「Don't use Liquid Glass in the content layer」「Use Liquid Glass effects sparingly」 |
| V6 先放主要内容，次要的原地展开（渐进披露）；按重要性从上往下排 | 设计评审看截图 | [HIG 布局](https://developer.apple.com/design/human-interface-guidelines/layout) |
| V7 样式只引用 token，用留白分组、对齐到间距阶梯 | `lint_tokens.py` 0；`verify_canvas.py` 写死的颜色 0 | 设计系统；`design-bar` rubric「版式与留白」 |
| V8 没有模板味：`anti-patterns.md` 和 unslop 的信号 0；把产品名换掉，这一屏就不成立 | `verify_canvas.py` 的模板味提示；设计评审做换名测试 | `design-bar` `references/anti-patterns.md`、`craft.md` §1 |
| V9 每屏最多一个主动效，并且有含义（表达三站之间的关系），不做装饰性的循环 | 设计评审对照设计系统「动效」一节 | [Apple Design Awards](https://developer.apple.com/design/awards/)「high-quality animations with a distinctive and cohesive theme」；设计系统「每屏一个主动效」 |

**看清另加的规则（K，工程品味）**：对标是酷壳（[coolshell.org 镜像](https://coolshell.org/articles/)，陈皓本人的站被禁止抓取）、[martinfowler.com](https://martinfowler.com/articles/microservices.html)、[simonwillison.net](https://simonwillison.net/)、[distill.pub](https://distill.pub/2020/circuits/zoom-in/)。选它们，是因为它们都是工程师写给工程师的长期阅读站，同行引用多，页面可以直接观察。

| 规则 | 怎么查 | 出处 |
|---|---|---|
| K1 文章元信息只放标题、所属的线、原文日期、适用于、最后核对日期、阅读时长；不放阅读数、点赞数 | 看文章页 | 酷壳、Fowler、Willison、Distill 都只有标题、作者、日期和少量标签 |
| K2 超过 2000 字的文章有目录 | 数字数 | 酷壳（5 项目录）、Fowler、Distill |
| K3 每张图都回答正文里的一个问题，不放装饰图 | 逐张问「它回答哪个问题」 | 酷壳一篇 12 段代码只配 1 张图 |
| K4 补充说明放侧注（桌面）或文末脚注（手机、平板），不打断主线 | 看文章页 | Fowler 的 sidebar；Distill 的旁注 |
| K5 分清文章类型（长文、链接、引言）；长文标阅读时长 | 看列表和文章页 | Willison 按类型分、长文标字数 |
| K6 文末有所在系列、上下篇或延伸阅读 | 看文末 | 酷壳的系列导航；Fowler 的 Further Reading |
| K7 按「问题 → 方案 → 总结」讲，开头不先讲是什么；结尾有能照做的做法 | 内容评审 | 陈皓：「千万不要一上来就说 What」「一定要有 Best Practice 或方法论总结」（[coolshell.org/articles/21589.html](https://coolshell.org/articles/21589.html)） |

### 4.4 可信（T）

**对标**：Our World in Data（数据出处和更新的标杆）、Distill、Martin Fowler、Simon Willison、酷壳。选它们，是因为它们公开出处、日期和改正记录，读者能自己核对。

| 规则 | 怎么查 | 出处 |
|---|---|---|
| T1 每个数字、研究和引用都写明作者并链到原文；出处表里有原句摘录和查询日期 | `content-reviewer` 逐条打开核对 | Willison「总写出原作者的名字」；Distill；Fowler |
| T2 图和数据写明来源，并说明怎么处理过 | 看图注 | [OWID](https://ourworldindata.org/grapher/exponential-growth-of-computation-in-the-training-of-notable-ai-systems)：「with major processing by Our World in Data」 |
| T3 有原文日期和最后核对日期；改过的有更新记录 | 看文章页 | 酷壳的发布和修改日期；Fowler 的 Significant Revisions；OWID 的 Last updated |
| T4 有公开的纠错入口，改正后记进更新记录 | 看文章页 | Distill 的 Updates and Corrections；陈皓主张文章「能被修改」 |
| T5 写明版权、能不能转载、怎么引用 | 看文末 | Distill 的 Reuse 和 Citation；OWID 的 How to cite |
| T6 「我们的判断」写清值不值得读、适合谁、代价；没读完的不推荐 | 内容评审 | Willison「没读过的不推荐」 |
| T7 讲到原因、代价和适用范围，并留一个能动手验证的练习（这就是「有深度」「有分量」） | 内容评审 | 陈皓「要了解技术就一定需要了解整个计算机的技术历史发展和进化路线」；设计系统「看清的气质」 |
| T8 健康内容写明研究类型和样本量，页上写「威利不是医生」 | 内容评审 | PRD 第 6 节 |

### 4.5 舒适（A）

**对标**：WCAG 2.2、Apple HIG 无障碍、Butterick《Practical Typography》、Google 关于侵入式弹窗的规则。选它们，是因为它们是行业规范，带数值。

| 规则 | 怎么查 | 出处 |
|---|---|---|
| A1 文字对比度 ≥ 4.5:1，控件和图形 ≥ 3:1，浅色深色都测 | `check_page.py`、`verify_canvas.py` | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) 1.4.3、1.4.11 |
| A2 可点区域 ≥ 44px | 同上 | 设计系统 `control-height`；Apple 44pt；WCAG 2.5.8 的 AA 是 24px，我们取更严的 |
| A3 320px 宽不横向滚动；文字放大到 200% 不丢内容；按 WCAG 1.4.12 加大行距和字距后页面不坏 | `check_page.py` 加 320 宽；手工放大 | WCAG 1.4.10、1.4.4、1.4.12 |
| A4 焦点看得见、不被挡住；只用键盘能做完全部操作 | 手工 Tab 走一遍 | WCAG 2.4.7、2.4.11 |
| A5 系统减弱动态效果时只留一帧；自动播放超过 5 秒的动效能暂停，或滚出视野就停；有声媒体不自动播放 | 打开系统设置看；找暂停入口 | WCAG 2.2.2、1.4.2；[web.dev](https://web.dev/articles/prefers-reduced-motion)；HIG：位移改成淡入淡出 |
| A6 首次访问不弹遮挡内容的弹窗；订阅只在页内原地展开 | 清空浏览器数据后打开 | [Google 侵入式弹窗](https://developers.google.com/search/docs/appearance/avoid-intrusive-interstitials) |
| A7 读起来不累：正文 ≥ 16px；中文每行不超过 40 字，行高 1.6–1.8；英文每行 45–75 个字符，行高为字号的 1.2–1.45 倍；段落之间用段距，不同时用首行缩进 | 量版心和字号 | [Butterick](https://practicaltypography.com/summary-of-key-rules.html)；Bringhurst 45–75 字符（转引）；W3C clreq 讨论中文每行不超过 48 字、书籍多为 17–40 字（未进正式版）；`design-bar` rubric 中文行高 1.6–1.8 |

### 4.6 用这些规则对照现有设计，已经发现的冲突

这一节是对抗评审的第一批结果，交给关口三 a（#14）处理：

1. **英文正文太宽、行距太大**：正文版心 640px、16px 时，英文每行约 80–90 个字符，超过 A7 的 75；英文行高 1.7 超过 1.45 倍。中文 640px ÷ 16px = 40 字，正好在上限。英文版要单独定字号、版心或行高。
2. **首页「叶与网」一直在动**：不悬停时 10 秒一次呼吸，持续超过 5 秒，A5 要求能暂停或滚出视野就停。现在滚出视野会停，还缺一个暂停的方式。
3. **语言切换的点按高度 38px**，小于 A2 的 44px（手机、平板画板）。
4. **站稳、动手两块画板写死了 145 处颜色**，违反 V7。

## 5. 动词：每个动作写清产出和完成的标准

| 动词 | 产出 | 什么时候算做完 |
|---|---|---|
| 打磨 | 按 `design-bar` 第 5 步一轮一轮改：只读检查 → 独立评审 → 修前 3 项 | 停止条件：标杆原则都 ≥ 4 分且检查全过；或一轮没有提升；或已经 3 轮 |
| 优化、提升 | 写明哪个指标、从多少到多少、怎么量 | 量到了目标值；没写指标的「优化」不能进票 |
| 完善、补齐 | 列出缺的条目清单 | 清单逐条有着落：补上了，或写明为什么不补 |
| 梳理、汇总 | 一份文档或一张表，结构是金字塔：结论、分组、依据 | 每条依据追到原话、PRD 或出处；分组不重不漏 |
| 评审 | 一条结论评论：通过或要改，阻塞项带位置和改法 | 实际跑过检查；每条发现有可信度分，低于 80 不报 |
| 对抗评审 | 由没看过制作过程的新 Agent 做；按金字塔自上而下：结论能不能被下层支撑，同层是否不重不漏，每条理由能不能追到来源，有没有反例 | 发现逐条有去向；两个不同模型的评审互相看不到（设计）或换模型（代码） |
| 举一反三 | 找出这条意见背后的原则，列出所有同类位置 | 同类位置都改了；原则写回技能、设计系统、规范或术语表；`trace.md` 记一笔 |
| 沉淀 | 规则写进对应文档，能机械检查的写成检查 | 同一类意见第二次出现时，已经有对应的规则或检查 |
| 校准 | 按 `velicoach-content` 的校准清单逐项核对已上线内容 | 每项有结论：仍然成立、已更新、已下线 |
| 核对 | 打开出处，找到原句 | 原句摘录和链接写在出处表里 |
| 对齐 | 写明和谁对齐、以哪份文档为准、改了哪一方 | 两份文档不再冲突；改动记在 `trace.md` 或 `decisions.md` |

## 6. 不能出现在验收里的虚词

这些词判不了对错，验收里出现就不通过。换成具体的数、动作或产出。

```filler-terms
适当
合适
合理
尽量
视情况
酌情
待定
TBD
等等
相关的
基本可以
比较好
```

## 7. 要有定义才能用的质量词

下面的词出现在验收里，必须链到本页对应的条目（写上 `quality-terms.md#条目`），或者直接写成条目里的规则。

```vague-terms
体验友好
友好
好用
易用
易上手
简单
简洁
一眼
直观
顺手
流畅
易懂
易理解
通俗
白话
清楚
清晰
好看
美观
高级感
有品味
品味
极简
克制
精致
质感
赏心悦目
干净
苹果设计语言
拿奖
专业
可信
有深度
有分量
值得读
舒服
舒适
不打扰
轻松
```
