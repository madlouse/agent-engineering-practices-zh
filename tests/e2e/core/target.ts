import { existsSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright";
import { E2E } from "../env.ts";

export type Need = "site" | "browser";

const now = new Date().toISOString();
export const RUN_ID = process.env.E2E_RUN_ID || (process.env.NODE_TEST_CONTEXT ? `${now.slice(0, 10)}-runner-${process.ppid}` : now.replace(/[:.]/g, "-"));
export const ARTIFACTS_ROOT = process.env.E2E_ARTIFACTS || join(tmpdir(), "velicoach-e2e");
export const ARTIFACTS = join(ARTIFACTS_ROOT, RUN_ID);

export function browserMissing(): string | false {
  try {
    return existsSync(chromium.executablePath()) ? false : "没有安装 Playwright 的 Chromium（npx playwright install chromium）";
  } catch (e) {
    return `找不到 Playwright 的 Chromium：${(e as Error).message}`;
  }
}

const MISSING: Record<Need, () => string | false> = {
  site: () => (E2E.base ? false : "未设置 E2E_BASE_URL"),
  browser: browserMissing,
};

export function skipReason(needs: readonly Need[]): string | false {
  for (const n of needs) {
    const why = MISSING[n]();
    if (why) return why;
  }
  return false;
}

export function artifactDir(...parts: string[]): string {
  const dir = join(ARTIFACTS, ...parts);
  mkdirSync(dir, { recursive: true });
  return dir;
}

export function latestRun(root = ARTIFACTS_ROOT): string | null {
  if (!existsSync(root)) return null;
  const runs = readdirSync(root)
    .map((d) => join(root, d, "coverage"))
    .filter((dir) => existsSync(dir))
    .sort((a, b) => statSync(a).mtimeMs - statSync(b).mtimeMs);
  return runs.length ? join(runs[runs.length - 1], "..") : null;
}
