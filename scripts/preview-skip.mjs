import { execFileSync } from "node:child_process";
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

const DOC_PATHS = [/^docs\//, /^\.grok\/(?:skills|references)\//, /^\.claude\/(?:skills|agents)\//, /^attachments\//, /^screenshots\//, /^[^/]+\.md$/];
const LINTED = /\.(?:[cm]?[jt]sx?)$/;
const LINT_IGNORED = [/^docs\/uiue\/prototypes\//];
const ALWAYS_BUILD = new Set(["site", "feature/v1"]);

const isDoc = (f) => DOC_PATHS.some((re) => re.test(f)) && (!LINTED.test(f) || LINT_IGNORED.some((re) => re.test(f)));

export function docsOnly(files) {
  const list = files.filter((f) => f.length > 0);
  return list.length > 0 && list.every(isDoc);
}

export function splitPaths(text) {
  return text.includes("\0") ? text.split("\0") : text.split("\n").map((f) => f.trim());
}

export function decide({ branch, previousSha, files }) {
  if (ALWAYS_BUILD.has(branch)) return { skip: false, why: `${branch} 是集成或生产分支，每个提交都要有预览部署` };
  if (!previousSha) return { skip: false, why: "这个分支还没有成功的部署，没有可比的提交" };
  if (files === null) return { skip: false, why: `克隆里找不到上次部署的提交 ${previousSha.slice(0, 7)}` };
  if (docsOnly(files)) return { skip: true, why: `从 ${previousSha.slice(0, 7)} 起只改了文档（${files.length} 个文件）` };
  return { skip: false, why: "改到了文档以外的文件" };
}

function changedSince(sha) {
  try {
    execFileSync("git", ["cat-file", "-e", `${sha}^{commit}`], { stdio: "ignore" });
    return splitPaths(execFileSync("git", ["diff", "-z", "--no-renames", "--name-only", sha, "HEAD"], { encoding: "utf8" })).filter(Boolean);
  } catch {
    return null;
  }
}

if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv.includes("--stdin")) {
    process.exit(docsOnly(splitPaths(readFileSync(0, "utf8"))) ? 0 : 1);
  }
  const branch = process.env.VERCEL_GIT_COMMIT_REF ?? "";
  const previousSha = process.env.VERCEL_GIT_PREVIOUS_SHA ?? "";
  const { skip, why } = decide({ branch, previousSha, files: previousSha ? changedSince(previousSha) : [] });
  console.log(`${skip ? "跳过预览部署" : "照常构建"}：${why}`);
  // why: Vercel 的 ignoreCommand 约定退出码 0 表示跳过构建，1 表示照常构建
  process.exit(skip ? 0 : 1);
}
