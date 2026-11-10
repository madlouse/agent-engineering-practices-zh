import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// 脚本判断「是不是被直接运行」时，入口路径要先 realpath 再和 import.meta.url 比：
// macOS 上 /tmp、/var 是符号链接，直接比较会让命令什么都不做、退出码 0（lessons.md 2026-11-10）
const SCRIPTS = dirname(fileURLToPath(import.meta.url));

test("入口判断都先 realpath", () => {
  const bad = readdirSync(SCRIPTS)
    .filter((f) => f.endsWith(".mjs") && !f.endsWith(".test.mjs"))
    .filter((f) => {
      const src = readFileSync(join(SCRIPTS, f), "utf8");
      return src.split("\n").some((l) => /process\.argv\[1\]/.test(l) && /import\.meta\.url/.test(l) && !/realpathSync/.test(l));
    });
  assert.deepEqual(bad, []);
});
