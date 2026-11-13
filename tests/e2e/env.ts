export const E2E = {
  base: (process.env.E2E_BASE_URL || "").replace(/\/+$/, ""),
  bypass: process.env.E2E_BYPASS || "",
};

export const needSite = E2E.base ? false : "未设置 E2E_BASE_URL";

export interface Reply {
  status: number;
  headers: Headers;
  text: string;
}

export async function site(path: string, init: RequestInit = {}): Promise<Reply> {
  const headers = new Headers(init.headers);
  if (E2E.bypass) headers.set("x-vercel-protection-bypass", E2E.bypass);
  const r = await fetch(`${E2E.base}${path}`, { ...init, headers, redirect: "manual", signal: AbortSignal.timeout(20_000) });
  const text = await r.text();
  return { status: r.status, headers: r.headers, text: text.slice(0, 500) };
}
