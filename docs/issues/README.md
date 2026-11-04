# 未完成项

内容打磨在 GitHub 上按模块跟进：总票 [#3](https://github.com/madlouse/velicoach/issues/3)，九个模块是它的子议题 #4–#12，标签 `lane:content`。画板 v1.0 是起始版本。下面的表是并入主站之前的收尾事项。

基线是本地提交 `7a7dffa`。一次只做一条。做完在这里改状态，再开下一条。

| 编号 | 事项 | 状态 |
| --- | --- | --- |
| 01 | 用户原话放进 [timeline.md](../requirements/timeline.md)，汇总在 [summary.md](../requirements/summary.md) | 完成。第 1 条仍只有残段 |
| 02 | 剩余范围写成 [PRD](../prd/remaining.md) | 完成 |
| 03 | 站名、主页、语言的 [界面说明](../uiue/identity.md) | 完成 |
| 04 | 按界面说明改站名。页眉、标题、分享卡一致 | 完成。分享卡图片由品牌资源另行替换 |
| 05 | 主页加上界面说明里的那张桌子图 | 完成。图在首页，图说写明近处是笔记、远处是电脑。标题按后来的原话，不是「坐在同一张桌子上」 |
| 06 | 页眉右上角全站中英切换 | 完成。刷新回到中文。没有英文稿时正文仍是中文，并写「这篇还没有英文。」 |
| 07 | DeepSeek 架构图：有稳定官方文件才嵌入 | 完成。官方仓库 `docs/007-architecture.md` 里是 Mermaid，不是可嵌入的图文件。页内缺口说明保留，不另画 |
| 08 | `with.velicoach.com` 的部署说明。不擅自改 DNS | 完成。见 [deploy.md](../deploy.md) |
| 09 | 旁白改为能落盘的开源声线，或确认站点声线能留下文件 | 完成。中文晓晓、美式英文 Andrew，各五条 mp3 在 `public/explainers/`。声线来自 edge-tts，不是开源模型，但文件已经留下 |
