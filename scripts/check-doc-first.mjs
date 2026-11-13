#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const EXEMPT = ["重构", "依赖", "修复", "测试", "构建"];

export function fieldOf(body, name) {
  const line = body.split("\n").find((l) => new RegExp(`^\\s*(?:[-*]\\s*)?(?:\\*\\*)?${name}(?:\\*\\*)?\\s*[：:]`).test(l));
  return line ? line.replace(new RegExp(`^.*?${name}(?:\\*\\*)?\\s*[：:]`), "").trim() : null;
}

export function judge({ config, changed, body }) {
  const toRes = (list) => (list ?? []).map((s) => new RegExp(s));
  const code = toRes(config.code);
  const docs = toRes(config.docs);
  const refs = toRes(config.refs);
  const codeFiles = changed.filter((f) => code.some((r) => r.test(f)));
  if (codeFiles.length === 0) return { ok: true, why: "没改产品代码" };
  const docFiles = changed.filter((f) => docs.some((r) => r.test(f)));
  if (docFiles.length) return { ok: true, why: `同一个 PR 里改了需求或技术方案：${docFiles.slice(0, 3).join("、")}` };
  const need = fieldOf(body, "需求");
  if (need && refs.some((r) => r.test(need))) return { ok: true, why: `正文引用了需求：${need.slice(0, 80)}` };
  const exempt = fieldOf(body, "免文档");
  if (exempt) {
    const kind = EXEMPT.find((k) => exempt.startsWith(k));
    if (kind && exempt.length > kind.length + 1) return { ok: true, why: `免文档（${kind}）：${exempt.slice(0, 80)}` };
  }
  const sample = codeFiles.slice(0, 3).join("、") + (codeFiles.length > 3 ? " 等" : "");
  return {
    ok: false,
    why: [
      `改了产品代码（${sample}），但没有对应的需求或技术方案。先改 PRD，再改技术方案，再改代码。三种补法选一种：`,
      "1. 在同一个 PR 里改需求或技术方案文档；",
      "2. 需求已经写在文档里：PR 正文加一行「需求：<文档路径或需求编号>」；",
      `3. 不改行为的改动：PR 正文加一行「免文档：<${EXEMPT.join("、")}之一>，<一句理由>」，只修复和文档不符的行为才算修复。`,
      "根因是需求或设计没写下来：补上文档再改代码，不要为了过检查写一个对不上的引用或免文档。",
    ].join("\n"),
  };
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [base, head, bodyFile = ""] = process.argv.slice(2);
  if (!base || !head) {
    console.log("用法：node scripts/check-doc-first.mjs <base-ref> <head-ref> [PR 正文文件]。配置取自 base 上 .velicoach-checks.json 的 docFirst（code、docs、refs，都是正则）；规则见 velicoach-mono/standards/engineering.md「文档先行」。");
    process.exit(2);
  }
  const git = (...a) => execFileSync("git", a, { encoding: "utf8", maxBuffer: 64 << 20, stdio: ["ignore", "pipe", "ignore"] });
  let config;
  try {
    config = JSON.parse(git("show", `${base}:.velicoach-checks.json`)).docFirst;
  } catch {
    config = undefined;
  }
  if (!config) {
    console.log(`文档先行：${base} 上还没有 .velicoach-checks.json 的 docFirst 配置，跳过`);
    process.exit(0);
  }
  const changed = git("-c", "core.quotepath=off", "diff", "--no-renames", "--name-only", `${base}...${head}`).split("\n").filter(Boolean);
  const body = bodyFile ? readFileSync(bodyFile, "utf8") : "";
  const result = judge({ config, changed, body });
  console.log(`文档先行：${result.why}`);
  process.exit(result.ok ? 0 : 1);
}
