import assert from "node:assert/strict";
import { scenario } from "../core/scenario.ts";

const PAGES = ["/", "/mind", "/build", "/about"];

scenario("S04 导航与全局组件：每个页面的导航只有站标、三站和语言切换，没有登录和搜索", {}, async (user) => {
  for (const path of PAGES) {
    assert.equal(await user.open(path), 200, `${path} 打不开`);
    const names = (await user.navLinks()).map((x) => x.name);
    for (const station of ["站稳", "看清", "动手"]) {
      assert.ok(names.some((n) => n.includes(station)), `${path} 的导航里没有${station}：${names.join("、")}`);
    }
    assert.ok(names.some((n) => /EN/.test(n)), `${path} 的导航里没有语言切换：${names.join("、")}`);
    assert.ok(!names.some((n) => /登录|搜索|Sign in|Search/i.test(n)), `${path} 的导航里不该有登录或搜索：${names.join("、")}`);
  }
});

scenario("S04 导航与全局组件：站标回首页", {}, async (user) => {
  await user.open("/about");
  const logo = (await user.navLinks())[0];
  assert.equal(logo?.href, "/", "导航的第一项应当是回首页的站标");
});

scenario("S04 导航与全局组件：在看清首页上，导航里的看清是当前所在的站", {}, async (user) => {
  await user.open("/mind");
  assert.match((await user.currentNav()) ?? "", /看清/, "导航没有高亮看清");
});
