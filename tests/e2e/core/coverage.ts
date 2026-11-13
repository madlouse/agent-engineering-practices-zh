import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import type { Page } from "playwright";
import { artifactDir } from "./target.ts";

export interface V8Range {
  startOffset: number;
  endOffset: number;
  count: number;
}
export interface V8Entry {
  url: string;
  source?: string;
  functions: { ranges: V8Range[] }[];
}
export interface ScriptCoverage {
  url: string;
  total: number;
  covered: [number, number][];
}

export function coveredRanges(entry: V8Entry, total: number): [number, number][] {
  const paint = new Uint8Array(total);
  const ranges = entry.functions.flatMap((f) => f.ranges).sort((a, b) => a.startOffset - b.startOffset || b.endOffset - a.endOffset);
  for (const r of ranges) paint.fill(r.count > 0 ? 1 : 0, Math.max(0, r.startOffset), Math.min(total, r.endOffset));
  const out: [number, number][] = [];
  for (let i = 0; i < total; i++) {
    if (!paint[i]) continue;
    const start = i;
    while (i < total && paint[i]) i++;
    out.push([start, i]);
  }
  return out;
}

export function union(a: [number, number][], b: [number, number][]): [number, number][] {
  const all = [...a, ...b].sort((x, y) => x[0] - y[0]);
  const out: [number, number][] = [];
  for (const [s, e] of all) {
    const last = out[out.length - 1];
    if (out.length && s <= last[1]) last[1] = Math.max(last[1], e);
    else out.push([s, e]);
  }
  return out;
}

export const bytes = (ranges: [number, number][]) => ranges.reduce((n, [s, e]) => n + e - s, 0);

export function firstParty(url: string, origin: string): boolean {
  return url.startsWith(origin) && /\/assets\/.+\.js$/.test(url.split("?")[0]);
}

export async function startCoverage(page: Page): Promise<void> {
  await page.coverage.startJSCoverage({ resetOnNavigation: false, reportAnonymousScripts: false });
}

export async function stopCoverage(page: Page, origin: string, name: string): Promise<void> {
  const entries = (await page.coverage.stopJSCoverage()) as V8Entry[];
  const scripts: ScriptCoverage[] = entries
    .filter((e) => firstParty(e.url, origin))
    .map((e) => {
      const total = e.source?.length ?? 0;
      return { url: e.url.slice(origin.length), total, covered: coveredRanges(e, total) };
    });
  writeFileSync(join(artifactDir("coverage"), `${name}.json`), JSON.stringify(scripts));
}

export interface CoverageSummary {
  scripts: number;
  total: number;
  covered: number;
  ratio: number;
  runs: number;
  byScript: { url: string; total: number; covered: number }[];
}

export function summarize(runFiles: ScriptCoverage[][]): CoverageSummary {
  const merged = new Map<string, ScriptCoverage>();
  for (const file of runFiles)
    for (const s of file) {
      const prev = merged.get(s.url);
      merged.set(s.url, prev ? { url: s.url, total: Math.max(prev.total, s.total), covered: union(prev.covered, s.covered) } : s);
    }
  const byScript = [...merged.values()].map((s) => ({ url: s.url, total: s.total, covered: bytes(s.covered) })).sort((a, b) => b.total - a.total);
  const total = byScript.reduce((n, s) => n + s.total, 0);
  const covered = byScript.reduce((n, s) => n + s.covered, 0);
  return { scripts: byScript.length, total, covered, ratio: total ? covered / total : 0, runs: runFiles.length, byScript };
}

export function readRun(runDir: string): ScriptCoverage[][] {
  const dir = join(runDir, "coverage");
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json") && f !== "summary.json")
    .map((f) => JSON.parse(readFileSync(join(dir, f), "utf8")) as ScriptCoverage[]);
}
