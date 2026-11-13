import type { Locator, Page } from "playwright";
import { E2E } from "../env.ts";

export type Text = string | RegExp;
export type Where = "navigation" | "main";

export interface User {
  readonly page: Page;
  readonly errors: string[];
  open(path: string): Promise<number>;
  reload(): Promise<void>;
  tap(name: Text, where?: Where): Promise<void>;
  sees(text: Text, timeoutMs?: number): Promise<void>;
  notSees(text: Text, timeoutMs?: number): Promise<void>;
  canTap(name: Text, where?: Where): Promise<boolean>;
  onFirstScreen(name: Text): Promise<boolean>;
  countOf(text: Text): Promise<number>;
  path(): Promise<string>;
  waitForPath(expected: RegExp, timeoutMs?: number): Promise<void>;
  screenText(): Promise<string>;
  lang(): Promise<string>;
  navLinks(): Promise<{ name: string; href: string | null }[]>;
  currentNav(): Promise<string | null>;
  linksTo(path: string): Promise<number>;
  expandFirst(): Promise<boolean>;
  hrefOf(name: Text, where?: Where): Promise<string | null>;
  hreflangs(): Promise<string[]>;
  stored(key: string): Promise<string | null>;
  isDark(): Promise<boolean>;
  waitForTheme(dark: boolean, timeoutMs?: number): Promise<void>;
  horizontalOverflow(): Promise<number>;
  smallTargets(minPx: number): Promise<string[]>;
  markPage(): Promise<void>;
  isSamePage(): Promise<boolean>;
}

const exact = (t: Text) => (typeof t === "string" ? { name: t, exact: true } : { name: t });

function control(page: Page, name: Text, where?: Where): Locator {
  const root = where ? page.getByRole(where).first() : page;
  const roles = ["link", "button", "tab", "radio", "checkbox", "switch"] as const;
  return roles.map((role) => root.getByRole(role, exact(name))).reduce((all, one) => all.or(one));
}

function darkBackground(): boolean {
  const rgb = getComputedStyle(document.body).backgroundColor.match(/[\d.]+/g)?.map(Number) ?? [255, 255, 255];
  const [r, g, b] = rgb;
  return 0.2126 * r + 0.7152 * g + 0.0722 * b < 128;
}

export function userOn(page: Page): User {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  const visible = (t: Text) => page.getByText(t).filter({ visible: true }).first();
  return {
    page,
    errors,
    async open(path) {
      const response = await page.goto(`${E2E.base}${path}`, { waitUntil: "load" });
      return response?.status() ?? 0;
    },
    async reload() {
      await page.reload({ waitUntil: "load" });
    },
    async tap(name, where) {
      await control(page, name, where).filter({ visible: true }).first().click();
    },
    async sees(text, timeoutMs = 10_000) {
      await visible(text).waitFor({ state: "visible", timeout: timeoutMs });
    },
    async notSees(text, timeoutMs = 2_000) {
      await page.getByText(text).filter({ visible: true }).first().waitFor({ state: "detached", timeout: timeoutMs }).catch(async () => {
        if (await visible(text).isVisible()) throw new Error(`不该出现却出现了：${String(text)}`);
      });
    },
    async canTap(name, where) {
      const c = control(page, name, where).filter({ visible: true }).first();
      return (await c.count()) > 0 && (await c.isEnabled());
    },
    async onFirstScreen(name) {
      const c = control(page, name).filter({ visible: true }).first();
      if ((await c.count()) === 0 || !(await c.isEnabled())) return false;
      return c.evaluate((el) => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && r.top < window.innerHeight && r.bottom > 0 && r.left < window.innerWidth && r.right > 0;
      });
    },
    async countOf(text) {
      return page.getByText(text).filter({ visible: true }).count();
    },
    async path() {
      const u = new URL(page.url());
      return u.pathname + u.hash;
    },
    async waitForPath(expected, timeoutMs = 10_000) {
      await page.waitForURL((u) => expected.test(u.pathname + u.hash), { timeout: timeoutMs });
    },
    async screenText() {
      return page.locator("body").innerText();
    },
    async lang() {
      return (await page.locator("html").getAttribute("lang")) ?? "";
    },
    async navLinks() {
      const nav = page.getByRole("navigation").first();
      const items = nav.getByRole("link").or(nav.getByRole("button")).or(nav.getByRole("radio")).or(nav.getByRole("tab"));
      return items.evaluateAll((els) =>
        els
          .map((el) => ({ name: (el.getAttribute("aria-label") || el.textContent || "").trim(), href: el.getAttribute("href") }))
          .filter((x) => x.name),
      );
    },
    async currentNav() {
      const current = page.getByRole("navigation").first().locator('[aria-current="page"]').first();
      if ((await current.count()) === 0) return null;
      return ((await current.getAttribute("aria-label")) || (await current.textContent()) || "").trim();
    },
    async linksTo(path) {
      return page.locator(`a[href="${path}"]`).filter({ visible: true }).count();
    },
    async expandFirst() {
      const folded = await page.locator('main [aria-expanded="false"]').filter({ visible: true }).first().elementHandle();
      if (!folded) return false;
      await folded.click();
      return page
        .waitForFunction((el) => el.getAttribute("aria-expanded") === "true", folded, { timeout: 2_000 })
        .then(() => true, () => false);
    },
    async hrefOf(name, where) {
      const root = where ? page.getByRole(where).first() : page;
      return root.getByRole("link", exact(name)).filter({ visible: true }).first().getAttribute("href");
    },
    async hreflangs() {
      return page.locator('link[rel="alternate"][hreflang]').evaluateAll((els) => els.map((el) => el.getAttribute("hreflang") ?? ""));
    },
    async stored(key) {
      return page.evaluate((k) => {
        try {
          return localStorage.getItem(k);
        } catch {
          return null;
        }
      }, key);
    },
    async isDark() {
      return page.evaluate(darkBackground);
    },
    async waitForTheme(dark, timeoutMs = 3_000) {
      const deadline = Date.now() + timeoutMs;
      while ((await page.evaluate(darkBackground)) !== dark) {
        if (Date.now() > deadline) throw new Error(`页面没有在 ${timeoutMs} 毫秒内变成${dark ? "深色" : "浅色"}`);
        await page.waitForTimeout(100);
      }
    },
    async horizontalOverflow() {
      return page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    },
    async smallTargets(minPx) {
      return page.evaluate((min) => {
        const selector = "a[href], button, input, select, textarea, [role=button], [role=link], [role=radio], [role=tab]";
        return [...document.querySelectorAll(selector)]
          .filter((el) => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && (r.width < min || r.height < min);
          })
          .map((el) => (el.getAttribute("aria-label") || el.textContent || el.tagName).trim().slice(0, 30));
      }, minPx);
    },
    async markPage() {
      await page.evaluate(() => {
        (window as unknown as { __e2eMark?: boolean }).__e2eMark = true;
      });
    },
    async isSamePage() {
      return page.evaluate(() => (window as unknown as { __e2eMark?: boolean }).__e2eMark === true);
    },
  };
}
