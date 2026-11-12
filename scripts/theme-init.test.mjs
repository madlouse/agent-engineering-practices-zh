import test from "node:test";
import assert from "node:assert/strict";
import vm from "node:vm";
import { syncTheme, THEME_BOOT_SCRIPT, THEME_KEY } from "../src/lib/theme-init.mjs";

function fakeDoc() {
  const attrs = new Map();
  return {
    attrs,
    documentElement: {
      setAttribute: (k, v) => attrs.set(k, String(v)),
      removeAttribute: (k) => attrs.delete(k),
      getAttribute: (k) => (attrs.has(k) ? attrs.get(k) : null),
      get className() {
        return "";
      },
    },
  };
}
function fakeStorage(initial = {}) {
  const data = { ...initial };
  const writes = [];
  return {
    data,
    writes,
    getItem: (k) => (k in data ? data[k] : null),
    setItem: (k, v) => {
      writes.push(k);
      data[k] = String(v);
    },
  };
}
const throwing = () => {
  throw new DOMException("denied", "SecurityError");
};

test("键名是 vc-theme", () => assert.equal(THEME_KEY, "vc-theme"));

test("保存的是 light 或 dark：data-theme 就是它", () => {
  for (const v of ["light", "dark"]) {
    const d = fakeDoc();
    const s = fakeStorage({ "vc-theme": v });
    assert.equal(syncTheme(d, () => s), v);
    assert.equal(d.documentElement.getAttribute("data-theme"), v);
  }
});

test("保存的是 auto、没保存：不设 data-theme，交给系统偏好", () => {
  for (const init of [{ "vc-theme": "auto" }, {}]) {
    const d = fakeDoc();
    d.documentElement.setAttribute("data-theme", "dark");
    assert.equal(syncTheme(d, () => fakeStorage(init)), "auto");
    assert.equal(d.documentElement.getAttribute("data-theme"), null);
  }
});

test("反例：取值以外的值按自动处理，值不进任何 DOM 属性", () => {
  for (const bad of ["Dark", "blue", "", "  light", "<script>", "null", "auto "]) {
    const d = fakeDoc();
    assert.equal(syncTheme(d, () => fakeStorage({ "vc-theme": bad })), "auto");
    assert.deepEqual([...d.attrs.entries()], []);
  }
});

test("反例：读 localStorage 抛异常（隐私模式）时不抛，按自动处理", () => {
  const d = fakeDoc();
  assert.equal(syncTheme(d, throwing), "auto");
  assert.deepEqual([...d.attrs.entries()], []);
  const s = fakeStorage();
  s.getItem = throwing;
  assert.equal(syncTheme(d, () => s), "auto");
});

test("选择只写进 vc-theme 这一个键；无效的选择不写", () => {
  const d = fakeDoc();
  const s = fakeStorage();
  assert.equal(syncTheme(d, () => s, "dark"), "dark");
  assert.deepEqual(s.writes, ["vc-theme"]);
  assert.deepEqual(Object.keys(s.data), ["vc-theme"]);
  assert.equal(d.documentElement.getAttribute("data-theme"), "dark");
  assert.equal(syncTheme(d, () => s, "neon"), "dark");
  assert.deepEqual(s.writes, ["vc-theme"]);
});

test("写入失败（隐私模式）时这一页照样切换，不抛", () => {
  const d = fakeDoc();
  const s = fakeStorage();
  s.setItem = throwing;
  assert.equal(syncTheme(d, () => s, "light"), "light");
  assert.equal(d.documentElement.getAttribute("data-theme"), "light");
});

test("内联脚本（放在 <head> 里的那份）自成一体，在假页面上跑出同样的结果", () => {
  for (const [stored, attr] of [["dark", "dark"], ["light", "light"], ["auto", null], ["x", null], [undefined, null]]) {
    const d = fakeDoc();
    const s = fakeStorage(stored === undefined ? {} : { "vc-theme": stored });
    vm.runInNewContext(THEME_BOOT_SCRIPT, { document: d, localStorage: s });
    assert.equal(d.documentElement.getAttribute("data-theme"), attr, String(stored));
  }
});

test("内联脚本：访问 localStorage 这个属性本身就抛（隐私模式）时也不抛", () => {
  const d = fakeDoc();
  const sandbox = { document: d };
  Object.defineProperty(sandbox, "localStorage", {
    get() {
      throw new DOMException("denied", "SecurityError");
    },
  });
  assert.doesNotThrow(() => vm.runInNewContext(THEME_BOOT_SCRIPT, sandbox));
  assert.deepEqual([...d.attrs.entries()], []);
});
