import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

const ERAS = ["起源", "机器学习", "深度学习", "大语言模型", "智能体"];

scenario("S06 看清首页：AI 发展史按五个时代分组", {}, async (user) => {
  await user.open("/mind");
  for (const era of ERAS) {
    assert.ok((await user.countOf(era)) > 0, `看清首页没有时代分组：${era}`);
  }
});

scenario("S06 看清首页：里程碑默认收起，点一下原地展开，地址不变", {}, async (user) => {
  await user.open("/mind");
  await user.markPage();
  const before = await user.path();
  assert.ok(await user.expandFirst(), "点了里程碑却没有展开");
  assert.equal(await user.path(), before, "展开里程碑不该改变地址");
  assert.ok(await user.isSamePage(), "展开里程碑不该重新加载页面");
});

scenario("S06 看清首页：顶部的学习路径入口，1 步到学习路径", {}, async (user) => {
  await user.open("/mind");
  await user.tap(/学习路径/);
  await user.waitForPath(/^\/mind\/learn\/?$/);
});

scenario("S06 看清首页：分段控件原地切到人机协作，地址跟着变，不整页重载", {}, async (user) => {
  await user.open("/mind");
  await user.markPage();
  await user.tap(/人机协作/);
  await user.waitForPath(/^\/mind\/collaboration\/?$/);
  assert.ok(await user.isSamePage(), "切换内容线不该整页重载");
});
