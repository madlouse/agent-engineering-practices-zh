// 路径产品只写本机存储：同级产品先读 cookie，这里的改动会被旧 cookie 盖回去。
export function savePref(key: "fam-theme" | "fam-lang", value: string) {
  try { localStorage.setItem(key, value); } catch {}
}
export function readPref(key: "fam-theme" | "fam-lang"): string | null {
  try { return localStorage.getItem(key); } catch { return null; }
}
