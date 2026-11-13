import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

scenario("S03 进入一站：点导航里的看清，1 步到看清首页", {}, async (user) => {
  await user.open("/");
  await user.tap(/^看清/, "navigation");
  await user.waitForPath(/^\/mind\/?$/);
  assert.match(await user.screenText(), /AI 发展史/, "看清首页没有显示 AI 发展史");
});

scenario("S03 进入一站：点首屏「动手」入口，1 步直达开发日志列表", {}, async (user) => {
  await user.open("/");
  await user.tap(/动手/, "main");
  await user.waitForPath(/^\/build\/?#devlog$/);
});

scenario("S03 进入一站：站稳入口的目标是 Veli 的 /body", {}, async (user) => {
  await user.open("/");
  const href = await user.hrefOf(/站稳/, "main");
  assert.match(href ?? "", /^\/body\/?$/, `站稳入口的链接目标不对：${href}`);
});
