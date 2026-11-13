import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

scenario("S08 切换语言：在看清首页点 EN，1 步到英文版，再点中文回来", {}, async (user) => {
  await user.open("/mind");
  await user.tap("EN");
  await user.waitForPath(/^\/en\/mind\/?$/);
  assert.match(await user.lang(), /^en/, "英文页的语言属性不是英文");
  await user.tap("中文");
  await user.waitForPath(/^\/mind\/?$/);
  assert.match(await user.lang(), /^zh/, "中文页的语言属性不是中文");
});

scenario("S08 切换语言：选择被记住，下次打开首页沿用", {}, async (user) => {
  await user.open("/");
  await user.tap("EN");
  await user.waitForPath(/^\/en\/?$/);
  assert.equal(await user.stored("vc-lang"), "en", "没有记住语言选择");
  await user.open("/");
  await user.waitForPath(/^\/en\/?$/);
});

scenario("S08 切换语言：第一次访问首页时按浏览器语言选版本", { locale: "en-US" }, async (user) => {
  await user.open("/");
  await user.waitForPath(/^\/en\/?$/);
  assert.match(await user.lang(), /^en/, "浏览器语言是英文，页面却不是英文");
});

scenario("S08 切换语言：首页声明互指的 hreflang 和 x-default", {}, async (user) => {
  await user.open("/");
  const tags = await user.hreflangs();
  assert.ok(tags.some((t) => /^zh/.test(t)), `没有声明中文版：${tags.join("、")}`);
  assert.ok(tags.some((t) => /^en/.test(t)), `没有声明英文版：${tags.join("、")}`);
  assert.ok(tags.includes("x-default"), `首页没有声明 x-default：${tags.join("、")}`);
});
