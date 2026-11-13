import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

scenario("S07 学习路径：从看清首页 1 步到学习路径，页面有四级步骤", {}, async (user) => {
  await user.open("/mind");
  await user.tap(/学习路径/);
  await user.waitForPath(/^\/mind\/learn\/?$/);
  for (const level of [/基础/, /智能体/, /模型/, /前沿/]) {
    assert.ok((await user.countOf(level)) > 0, `学习路径页没有这一级：${String(level)}`);
  }
});

scenario("S07 学习路径：步骤默认收起，点一下原地展开", {}, async (user) => {
  await user.open("/mind/learn");
  assert.ok(await user.expandFirst(), "点了学习路径步骤却没有展开");
});

scenario("S07 学习路径：顶部有回看清首页的链接，导航高亮看清", {}, async (user) => {
  await user.open("/mind/learn");
  assert.ok((await user.linksTo("/mind")) > 0, "学习路径页顶部没有回 /mind 的链接");
  assert.match((await user.currentNav()) ?? "", /看清/, "导航没有高亮看清");
});
