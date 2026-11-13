import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

scenario("S01 第一次来：首屏同时有站稳、看清、动手三个入口和两个主操作", {}, async (user) => {
  await user.open("/");
  await user.sees(/开始训练/);
  await user.sees(/读最新文章/);
  for (const entry of [/开始训练/, /为什么是肌肉/, /读最新文章/, /动手/]) {
    assert.ok(await user.onFirstScreen(entry), `首屏上点不到：${String(entry)}`);
  }
  assert.ok(await user.onFirstScreen(/看清/), "首屏上点不到看清的入口");
  assert.ok(await user.onFirstScreen(/站稳/), "首屏上点不到站稳的入口");
});

scenario("S01 第一次来：所有人看到同一个首屏，没有登录入口，页面没有脚本错误", {}, async (user) => {
  await user.open("/");
  await user.sees(/开始训练/);
  assert.equal(await user.countOf(/登录|Sign in|Log in/), 0, "v1 主站不该有登录入口");
  assert.deepEqual(user.errors, [], "页面出现了未捕获的脚本错误");
});
