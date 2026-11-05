# 按钮与液态玻璃：从 Polaris 和苹果 HIG 借来的做法

> 什么时候读：做或改按钮、浮动控件、弹层、加载和出错状态时。数值和类名以设计系统 README「玻璃材质」「液态玻璃」「状态」为准，本页只讲为什么这样做、从哪里借的。2026-11-05 整理。

## 借了什么

| 做法 | 我们怎么用 | 出处 |
|---|---|---|
| 按钮分层：主按钮每个区域最多 1 个；次按钮、文字链接拉开层次；按钮用于操作、链接用于跳转 | 主按钮实色（`btn-action` 等），次按钮描边（`btn-quiet`），快捷入口文字链接（`quick`） | Polaris Button；HIG「每个视图醒目的按钮 1–2 个」 |
| 实色按钮的边缘光：顶边细高光、底边暗线、贴身短影，多层 `inset` 叠出来 | `shadow-bevel`；深色下高光更亮、影子更深 | Polaris shadow tokens（bevel）；Campsite 的光感边框 |
| 按下：变暗、内容下移 1px、阴影从凸起改成内凹，不缩放 | `.btn:active` 内容下移 1px，`shadow-bevel-press` | Polaris Button 源码（`translate3d(0,1px,0)`） |
| 加载中：按钮宽度不变，禁用，防止重复提交 | 文字换成进行时（「正在订阅」）并 `aria-disabled`；按最长文字定宽 | Polaris Button（loading）；HIG「Checkout → Checking out…」 |
| 焦点：outline，不用阴影，免得和边缘光打架 | 2px `vc-focus`，偏 2px | Polaris |
| 动效：时长按阶梯，交互用一种缓动，消失比出现快，只让一个元素动 | `duration-press` 100、`fast` 150、`base` 240、`exit` 160；`ease-out` 出现、`ease-in` 消失 | Polaris motion tokens（50ms 一档；Toast 进 400 出 200） |
| 层级的影子：卡片、弹出层、对话框各一档 | `shadow-card`、`shadow-pop`、`shadow-modal` | Polaris shadow 100 / 300 / 600 |
| 深度只给能点的、重要的东西 | 静态内容不加影子，卡片只有很淡的一档 | Polaris depth |
| 加载用骨架，不用转圈；骨架行数和真实内容一致 | 设计系统「状态」：灰块不闪 | Polaris Skeleton |
| 错误信息：说清哪里错、怎么改，放在出错位置旁边，不写「无效」，不过度道歉 | 订阅失败：「邮箱不完整，看看 @ 后面少了什么。」 | Polaris error messages |
| Liquid Glass 只用于浮在内容上的控件层；主按钮用有色面，不给多个控件都上色 | 液态玻璃只给压在动效、视频上的浮动控件；主按钮实色 | HIG Materials、Buttons |

## 没借的

- Polaris 的品牌色、按钮渐变的具体颜色：只借方法，外观按我们的纸墨两色。
- Polaris 按钮不写过渡：我们给 100–150ms 的颜色过渡，按下更跟手。
- Toast 报错：Polaris 自己也弃用了；我们的结果都在原位显示。
- 液态玻璃的折射做主效果：`backdrop-filter: url()` 只有 Chromium 画得出来，Safari 认得写法却什么都不画，`@supports` 也测不出。只在 Chromium 上作增强，按浏览器内核判断。

## 液态玻璃的四个判断

1. **背后会变吗？** 动效、视频、滚动时压过的正文：可以用。平涂底色：用实色面，否则只是一块灰（V5）。
2. **是不是主操作？** 是：实色，不用玻璃。
3. **字够清楚吗？** 按最差的背景算，正文 4.5:1；Safari 读不到「降低透明度」，玻璃底色本身就要够。
4. **一屏几块？** 不超过 3–4 块；不给模糊半径做动画（性能）。

## 来源

- Polaris 源码（Shopify/polaris，提交 3f7954a，2026-09-10）：`polaris-tokens/src/themes/base/{motion,shadow,color}.ts`、`dark.ts`；`polaris-react/src/components/Button`
- https://polaris.shopify.com/design/depth/shadow-tokens
- https://polaris.shopify.com/design/motion
- https://polaris.shopify.com/components/actions/button
- https://polaris.shopify.com/content/error-messages
- https://developer.apple.com/design/human-interface-guidelines/materials
- https://developer.apple.com/design/human-interface-guidelines/buttons
- https://web.dev/articles/backdrop-filter
- https://dev.to/devyatov/liquid-glass-on-the-web-6-ways-to-build-it-with-css-and-svg-3m07
