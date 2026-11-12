// 外观（自动、浅色、深色）的读取、应用和保存。选择只存在本机 localStorage 的 vc-theme 键，不发给服务端。
// data-theme 只在选了浅色或深色时写；自动、没存过、读不到、取值以外的值都不写，交给 tokens.css 里的系统偏好（读不到系统偏好时是浅色）。

export const THEME_KEY = "vc-theme";

/**
 * 读保存的外观并应用到 <html>；给了 next 就先保存再应用。返回这一页用的选择（auto、light、dark）。
 * 自成一体（不引用外面的变量）：THEME_BOOT_SCRIPT 把它原样放进 <head>，第一次绘制之前执行。
 * localStorage 抛异常（隐私模式）时不抛，按自动处理；这一页的选择照样生效，只是没存下来。
 */
export function syncTheme(doc, getStorage, next) {
  const key = "vc-theme";
  const valid = (v) => v === "auto" || v === "light" || v === "dark";
  let choice = "auto";
  try {
    const storage = getStorage();
    if (valid(next)) storage.setItem(key, next);
    const saved = storage.getItem(key);
    if (valid(saved)) choice = saved;
  } catch {
    // 隐私模式等读写不了：按自动处理
  }
  if (valid(next)) choice = next;
  if (choice === "auto") doc.documentElement.removeAttribute("data-theme");
  else doc.documentElement.setAttribute("data-theme", choice);
  return choice;
}

export const THEME_BOOT_SCRIPT = `(${syncTheme})(document,function(){return localStorage})`;
