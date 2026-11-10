// 评审贴结论评论前自查草稿：node scripts/check-review-draft.mjs <草稿文件> <种类> <PR 头 sha>
// 判定在 review-markers.mjs 的 draftProblems（和合并时同一套）。命令行单独放一个文件：合并脚本用 node -e 导入 review-markers.mjs，
// 那里不能有顶层入口代码。退出码：0 能贴，1 不能贴，2 用法不对。
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { draftProblems } from "./review-markers.mjs";

// 入口比较前先 realpath：macOS 上 /tmp、/var 是符号链接，直接比较会让命令什么都不做、退出码 0
if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [file, kind, sha] = process.argv.slice(2);
  if (!file || !kind || !sha) {
    console.error("用法：node scripts/check-review-draft.mjs <草稿文件> <种类> <PR 头 sha>");
    process.exit(2);
  }
  const problems = draftProblems(readFileSync(file, "utf8"), kind, sha);
  for (const p of problems) console.error(`草稿不能贴：${p}`);
  if (problems.length === 0) console.log("草稿可以贴");
  process.exit(problems.length === 0 ? 0 : 1);
}
