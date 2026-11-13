import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

scenario("S10 浅色与深色：系统是深色、没有保存选择时，页面是深色", { colorScheme: "dark" }, async (user) => {
  await user.open("/");
  assert.ok(await user.isDark(), "系统是深色，页面却不是深色");
});

scenario("S10 浅色与深色：系统是浅色时，页面是浅色", { colorScheme: "light" }, async (user) => {
  await user.open("/");
  assert.ok(!(await user.isDark()), "系统是浅色，页面却是深色");
});

scenario("S10 浅色与深色：在页脚选浅色立即生效并被记住，选自动后恢复跟随系统", { colorScheme: "dark" }, async (user) => {
  await user.open("/");
  await user.tap("浅色");
  await user.waitForTheme(false);
  assert.equal(await user.stored("vc-theme"), "light", "没有记住外观选择");
  await user.reload();
  assert.ok(!(await user.isDark()), "重新加载后外观回到了深色");
  await user.tap("自动");
  await user.waitForTheme(true);
  assert.equal(await user.stored("vc-theme"), "auto", "选自动后没有记住");
});
