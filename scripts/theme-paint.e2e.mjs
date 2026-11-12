#!/usr/bin/env node
// 票 #22 的页面验收：首帧主题、加载后不再变、系统切换、读不到偏好、localStorage 异常、没有 Google 字体请求。
// 需要一个正在跑的站（本地 dev 或预览）：node scripts/theme-paint.e2e.mjs <基础地址> [输出目录]
// 不进 npm test（要起服务和浏览器）。首帧的做法：把所有外部脚本卡住，等 first-contentful-paint 出来就截图，
// 这时候只有 HTML、样式和 <head> 里的内联脚本起了作用；再放行脚本，等加载完成，再截一次。
import { chromium } from "playwright";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const base = (process.argv[2] ?? "http://127.0.0.1:8080").replace(/\/$/, "");
const out = process.argv[3] ?? "theme-paint-out";
mkdirSync(out, { recursive: true });

const tokens = JSON.parse(readFileSync(fileURLToPath(new URL("../docs/uiue/system/tokens.json", import.meta.url)), "utf8"));
const paper = tokens.color.tokens.find((t) => t.name === "vc-paper").value;
const rgb = (hex) => `rgb(${[1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(", ")})`;
const BG = { light: rgb(paper.light), dark: rgb(paper.dark) };
const PAGES = ["/", "/posts/dan-koe-one-day"];

const results = [];
const check = (name, ok, detail = "") => {
  results.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? `  ${detail}` : ""}`);
};

const SPY = `
  window.__themeLog = [];
  new MutationObserver((ms) => { for (const m of ms) window.__themeLog.push({ t: performance.now(), attr: m.attributeName, value: document.documentElement.getAttribute(m.attributeName) }); })
    .observe(document.documentElement, { attributes: true });
  window.__fcp = null;
  new PerformanceObserver((l) => { for (const e of l.getEntries()) if (e.name === 'first-contentful-paint') window.__fcp = e.startTime; }).observe({ type: 'paint', buffered: true });
`;

const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined });

async function firstPaint({ page, system, stored, shot }) {
  const ctx = await browser.newContext({ colorScheme: system, viewport: { width: 1180, height: 800 } });
  if (stored !== undefined) await ctx.addInitScript(`try{localStorage.setItem("vc-theme", ${JSON.stringify(stored)})}catch(e){}`);
  await ctx.addInitScript(SPY);
  let release;
  const gate = new Promise((r) => (release = r));
  await ctx.route("**/*", async (route) => {
    if (route.request().resourceType() === "script") await gate;
    await route.continue();
  });
  const p = await ctx.newPage();
  const requests = [];
  p.on("request", (r) => requests.push(r.url()));
  await p.goto(base + page, { waitUntil: "commit" });
  await p.waitForFunction(() => location.protocol.startsWith("http") && document.body && window.__fcp !== null, null, { timeout: 15000 });
  const read = () =>
    p.evaluate(() => ({
      bg: getComputedStyle(document.body).backgroundColor,
      attr: document.documentElement.getAttribute("data-theme"),
      html: document.documentElement.outerHTML,
      fcp: window.__fcp,
    }));
  const first = await read();
  const clip = { x: 0, y: 0, width: 4, height: 4 };
  const firstPixels = await p.screenshot({ clip });
  await p.screenshot({ path: `${out}/${shot}-first.png` });
  release();
  await p.waitForLoadState("load");
  await p.waitForLoadState("networkidle").catch(() => {});
  await p.waitForTimeout(800);
  const after = await read();
  const afterPixels = await p.screenshot({ clip });
  await p.screenshot({ path: `${out}/${shot}-loaded.png` });
  const log = await p.evaluate(() => ({ log: window.__themeLog, fcp: window.__fcp }));
  const lateChanges = log.log.filter((m) => m.t > log.fcp);
  await ctx.close();
  return { first, after, same: firstPixels.equals(afterPixels), lateChanges, requests };
}

const expectDark = (system, stored) => (stored === "light" ? "light" : stored === "dark" ? "dark" : system === "dark" ? "dark" : "light");

for (const page of PAGES) {
  const tag = page === "/" ? "home" : "article";
  const cases = [
    { system: "dark", stored: undefined, label: "系统深色·没存过（自动）" },
    { system: "dark", stored: "auto", label: "系统深色·存的 auto" },
    { system: "dark", stored: "light", label: "系统深色·存的 light" },
    { system: "light", stored: "dark", label: "系统浅色·存的 dark" },
    { system: "no-preference", stored: undefined, label: "读不到系统偏好·没存过" },
  ];
  for (const c of cases) {
    const want = c.system === "no-preference" && c.stored === undefined ? "light" : expectDark(c.system, c.stored);
    const r = await firstPaint({ page, system: c.system, stored: c.stored, shot: `${tag}-${c.system}-${c.stored ?? "none"}` });
    check(`${page} ${c.label}：首帧是${want === "dark" ? "深色" : "浅色"}`, r.first.bg === BG[want], `首帧 ${r.first.bg}，期望 ${BG[want]}`);
    check(`${page} ${c.label}：加载后主题不变、首帧和加载后同一像素`, r.after.bg === r.first.bg && r.after.attr === r.first.attr && r.same, `data-theme ${r.first.attr} → ${r.after.attr}`);
    check(`${page} ${c.label}：首次绘制之后 <html> 属性没有再变`, r.lateChanges.length === 0, JSON.stringify(r.lateChanges));
  }
}

// 反例：取值以外的值按自动处理，值不进 DOM
for (const bad of ["Dark", "blue", "", "<b>x</b>"]) {
  const r = await firstPaint({ page: "/", system: "dark", stored: bad, shot: `bad-${bad.length}` });
  const leaked = bad !== "" && r.after.html.includes(bad);
  check(`取值 ${JSON.stringify(bad)}：按自动（系统深色→深色），data-theme 为空，值没进 DOM`, r.first.bg === BG.dark && r.after.attr === null && !leaked, `data-theme=${r.after.attr}`);
}

// 反例：localStorage 一访问就抛异常（隐私模式）
{
  const ctx = await browser.newContext({ colorScheme: "dark" });
  await ctx.addInitScript(`Object.defineProperty(window, "localStorage", { get() { throw new DOMException("denied", "SecurityError"); } });`);
  const p = await ctx.newPage();
  const errors = [];
  p.on("pageerror", (e) => errors.push(String(e)));
  await p.goto(base + "/", { waitUntil: "load" });
  await p.waitForTimeout(800);
  const bg = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  const attr = await p.evaluate(() => document.documentElement.getAttribute("data-theme"));
  const hasText = await p.evaluate(() => document.body.innerText.length > 20);
  check("localStorage 抛异常：页面照常绘制，按自动处理（系统深色→深色）", bg === BG.dark && attr === null && hasText && !errors.some((e) => /SecurityError|denied/.test(e)), `bg=${bg} data-theme=${attr} pageerror=${errors.length}`);
  await ctx.close();
}

// 页面开着、自动：系统切换，不刷新就跟着变
{
  const ctx = await browser.newContext({ colorScheme: "light" });
  const p = await ctx.newPage();
  await p.goto(base + "/", { waitUntil: "load" });
  await p.evaluate(() => (window.__marker = 1));
  const bg1 = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await p.emulateMedia({ colorScheme: "dark" });
  await p.waitForTimeout(300);
  const bg2 = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await p.emulateMedia({ colorScheme: "light" });
  await p.waitForTimeout(300);
  const bg3 = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  const marker = await p.evaluate(() => window.__marker);
  check("自动：系统浅→深→浅，页面不刷新就跟着变", bg1 === BG.light && bg2 === BG.dark && bg3 === BG.light && marker === 1, `${bg1} → ${bg2} → ${bg3}`);
  await ctx.close();
}

// 网络：没有发往 Google 字体的请求；外观的选择不发给服务端
{
  const ctx = await browser.newContext({ colorScheme: "dark" });
  await ctx.addInitScript(`localStorage.setItem("vc-theme", "light")`);
  const p = await ctx.newPage();
  const seen = [];
  p.on("request", (r) => seen.push({ url: r.url(), body: r.postData() ?? "", headers: JSON.stringify(r.headers()) }));
  for (const page of PAGES) {
    await p.goto(base + page, { waitUntil: "load" });
    await p.waitForLoadState("networkidle").catch(() => {});
  }
  const google = seen.filter((r) => /fonts\.googleapis\.com|fonts\.gstatic\.com/.test(r.url));
  check(`没有发往 fonts.googleapis.com、fonts.gstatic.com 的请求（共 ${seen.length} 个请求）`, google.length === 0, google.map((g) => g.url).join(" "));
  const leaked = seen.filter((r) => /vc-theme/.test(r.url + r.body + r.headers));
  check("外观的选择不发给服务端：没有请求的地址、正文、头里带 vc-theme", leaked.length === 0, leaked.map((l) => l.url).join(" "));
  const cookies = await ctx.cookies();
  check("外观的选择不写 Cookie", !cookies.some((c) => /vc-theme/.test(c.name + c.value)));
  const keys = await p.evaluate(() => Object.keys(localStorage));
  check("localStorage 里的外观只有 vc-theme 这一个键", keys.filter((k) => /theme/i.test(k)).join() === "vc-theme", `键：${keys.join()}`);
  await ctx.close();
}

await browser.close();
writeFileSync(`${out}/results.json`, JSON.stringify(results, null, 2));
const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} 通过`);
process.exit(failed.length ? 1 : 0);
