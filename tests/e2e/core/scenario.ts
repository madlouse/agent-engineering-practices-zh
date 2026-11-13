import { test } from "node:test";
import { join } from "node:path";
import { chromium } from "playwright";
import { E2E } from "../env.ts";
import { startCoverage, stopCoverage } from "./coverage.ts";
import { artifactDir, skipReason } from "./target.ts";
import { userOn, type User } from "./web.ts";

export interface ScenarioOptions {
  width?: number;
  height?: number;
  locale?: string;
  colorScheme?: "light" | "dark";
  touch?: boolean;
}

const slug = (title: string) => title.replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "").slice(0, 80);

export function scenario(title: string, options: ScenarioOptions, body: (user: User) => Promise<void>): void {
  test(title, { skip: skipReason(["site", "browser"]) }, async () => {
    const origin = new URL(E2E.base).origin;
    const browser = await chromium.launch();
    const context = await browser.newContext({
      viewport: { width: options.width ?? 1280, height: options.height ?? 800 },
      locale: options.locale ?? "zh-CN",
      timezoneId: "Asia/Shanghai",
      colorScheme: options.colorScheme ?? "light",
      hasTouch: options.touch ?? false,
      isMobile: options.touch ?? false,
      extraHTTPHeaders: E2E.bypass ? { "x-vercel-protection-bypass": E2E.bypass, "x-vercel-set-bypass-cookie": "true" } : {},
    });
    // 为什么：第三方字体和统计在隔离环境里可能不可达，会拖住页面加载，案例只验主站自己的行为
    await context.route((url) => url.origin !== origin, (route) => route.abort());
    const page = await context.newPage();
    await startCoverage(page);
    const name = slug(title);
    try {
      await body(userOn(page));
    } catch (e) {
      await page.screenshot({ path: join(artifactDir("evidence"), `${name}.png`), fullPage: true }).catch(() => undefined);
      throw e;
    } finally {
      await stopCoverage(page, origin, name).catch(() => undefined);
      await browser.close();
    }
  });
}
