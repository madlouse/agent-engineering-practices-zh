import { E2E, site } from "../env.ts";
import { ARTIFACTS_ROOT, browserMissing } from "./target.ts";

interface Check {
  name: string;
  ok: boolean;
  detail: string;
  required: boolean;
}

async function run(): Promise<Check[]> {
  const out: Check[] = [];
  const add = (name: string, ok: boolean, detail: string, required = true) => out.push({ name, ok, detail, required });
  const browser = browserMissing();
  add("浏览器", !browser, browser || "Playwright Chromium 已安装");
  if (!E2E.base) {
    add("被测站点", false, "未设置 E2E_BASE_URL");
    return out;
  }
  try {
    const home = await site("/");
    add("被测站点", home.status === 200, `${E2E.base}/ → ${home.status}`);
    const type = home.headers.get("content-type") ?? "";
    add("首页是网页", type.includes("text/html"), `content-type：${type || "空"}`);
  } catch (e) {
    add("被测站点", false, `${E2E.base} 连不上：${(e as Error).message}`);
  }
  add("证据和覆盖率目录", true, ARTIFACTS_ROOT, false);
  return out;
}

const checks = await run();
for (const c of checks) console.log(`${c.ok ? "✓" : c.required ? "✗" : "·"} ${c.name}：${c.detail}`);
const blocking = checks.filter((c) => c.required && !c.ok);
console.log(blocking.length ? `\n环境没准备好（${blocking.map((c) => c.name).join("、")}）：这时案例失败算环境问题，不算产品问题。` : "\n环境可以跑。");
process.exit(blocking.length ? 1 : 0);
