#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const GROUPS = { source: "产品源码", e2eCore: "E2E 能力模块", e2eCases: "E2E 案例" };

export function judge({ config, changed }) {
  const hit = {};
  for (const [group, list] of Object.entries(config ?? {})) {
    if (!(group in GROUPS)) continue;
    const res = list.map((s) => new RegExp(s));
    const files = changed.filter((f) => res.some((r) => r.test(f)));
    if (files.length) hit[group] = files;
  }
  const groups = Object.keys(hit);
  if (groups.length <= 1) return { ok: true, why: groups.length ? `只改了${GROUPS[groups[0]]}` : "没改源码和 E2E" };
  const detail = groups.map((g) => `${GROUPS[g]}：${hit[g].slice(0, 3).join("、")}${hit[g].length > 3 ? " 等" : ""}`).join("；");
  return {
    ok: false,
    why: [
      `同一个 PR 同时改了${groups.map((g) => GROUPS[g]).join("和")}（${detail}）。`,
      "E2E 只发现问题，修复由写代码的 Agent 做；为了让测试通过同时改源码和案例或 E2E 能力模块，测试就不再能证明什么。拆开提：",
      "1. E2E 失败说明产品有问题：只改源码，案例和能力模块不动；",
      "2. 案例本身和 PRD 对不上：先改 PRD 或在案例 PR 里引用 PRD 条目，单独提一个只改案例的 PR；",
      "3. 能力模块（环境、驱动、取证、覆盖率）有问题：单独提一个只改能力模块的 PR。",
      "规则见 velicoach-mono/verify/roles.md。",
    ].join("\n"),
  };
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [base, head] = process.argv.slice(2);
  if (!base || !head) {
    console.log("用法：node scripts/check-role-paths.mjs <base-ref> <head-ref>。路径分组取自 base 上 .velicoach-checks.json 的 roles（source、e2eCore、e2eCases，都是正则）；规则见 velicoach-mono/verify/roles.md。");
    process.exit(2);
  }
  const git = (...a) => execFileSync("git", a, { encoding: "utf8", maxBuffer: 64 << 20, stdio: ["ignore", "pipe", "ignore"] });
  let config;
  try {
    config = JSON.parse(git("show", `${base}:.velicoach-checks.json`)).roles;
  } catch {
    config = undefined;
  }
  if (!config) {
    console.log(`角色隔离：${base} 上还没有 .velicoach-checks.json 的 roles 配置，跳过`);
    process.exit(0);
  }
  const changed = git("-c", "core.quotepath=off", "diff", "--no-renames", "--name-only", `${base}...${head}`).split("\n").filter(Boolean);
  const result = judge({ config, changed });
  console.log(`角色隔离：${result.why}`);
  process.exit(result.ok ? 0 : 1);
}
