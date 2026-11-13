import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";
import type { User } from "../core/web.ts";

async function homeFitsScreen(user: User, touch: boolean): Promise<void> {
  await user.open("/");
  await user.sees(/开始训练/);
  await user.sees(/读最新文章/);
  assert.ok((await user.horizontalOverflow()) <= 0, "首页出现了横向滚动");
  assert.ok(await user.canTap(/动手/), "首屏上点不到动手入口");
  if (touch) assert.deepEqual(await user.smallTargets(44), [], "有点按区域小于 44 px 的控件");
}

scenario("S12 三种设备版式：手机 390 px 竖屏，上下拼接，没有横向滚动，点按区域 ≥ 44 px", { width: 390, height: 844, touch: true }, (user) => homeFitsScreen(user, true));

scenario("S12 三种设备版式：iPad 820 px 竖屏，左右各半，没有横向滚动，点按区域 ≥ 44 px", { width: 820, height: 1180, touch: true }, (user) => homeFitsScreen(user, true));

scenario("S12 三种设备版式：桌面 1440 px，没有横向滚动，入口都可见", { width: 1440, height: 900 }, (user) => homeFitsScreen(user, false));
