import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { readRun, summarize } from "./coverage.ts";
import { latestRun } from "./target.ts";

const runDir = process.argv[2] || latestRun();
if (!runDir) {
  console.log("还没有覆盖率数据：先跑 npm run test:e2e（需要浏览器和 E2E_BASE_URL）");
  process.exit(0);
}
const s = summarize(readRun(runDir));
const pct = (r: number) => `${(r * 100).toFixed(1)}%`;
const lines = [
  `E2E 运行时覆盖率（浏览器端，第一方脚本按字节）：${pct(s.ratio)}`,
  `运行 ${runDir}，案例 ${s.runs} 条，脚本 ${s.scripts} 个，${s.covered} / ${s.total} 字节`,
  "",
  "| 脚本 | 字节 | 走到 | 覆盖 |",
  "|---|---|---|---|",
  ...s.byScript.slice(0, 15).map((x) => `| ${x.url} | ${x.total} | ${x.covered} | ${pct(x.total ? x.covered / x.total : 0)} |`),
];
writeFileSync(join(runDir, "coverage", "summary.json"), JSON.stringify(s, null, 2));
writeFileSync(join(runDir, "coverage", "summary.md"), lines.join("\n") + "\n");
console.log(lines.join("\n"));
