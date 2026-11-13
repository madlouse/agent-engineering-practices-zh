// 偏好写两处：上级域的 cookie（子域之间共享）和本机存储（兜底）。读的时候 cookie 优先。
const PARENT = ".fam.example";
export function savePref(key: "fam-theme" | "fam-lang", value: string) {
  document.cookie = `${key}=${encodeURIComponent(value)}; Domain=${PARENT}; Path=/; SameSite=Lax; Max-Age=31536000`;
  try { localStorage.setItem(key, value); } catch {}
}
export function readPref(key: "fam-theme" | "fam-lang"): string | null {
  const m = document.cookie.match(new RegExp(`(?:^|; )${key}=([^;]*)`));
  if (m) return decodeURIComponent(m[1]);
  try { return localStorage.getItem(key); } catch { return null; }
}
