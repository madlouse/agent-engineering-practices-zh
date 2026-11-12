#!/usr/bin/env node
// 回退字体放在主站自己的服务器上：把 @fontsource 包里的 @font-face 改成设计系统字体栈用的族名，写成 src/fonts.css。
// 字体文件随构建由主站自己的域名提供，不从 Google 取。中文按 unicode-range 分片，访客只下载页面用到的那几片。
// 用法：node scripts/gen-fonts.mjs（写文件）；--check 只比较，不一致退出码为 1。
import { readFileSync, realpathSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const FONTS_CSS = fileURLToPath(new URL("../src/fonts.css", import.meta.url));
const pkgDir = (name) => fileURLToPath(new URL(`../node_modules/${name}/`, import.meta.url));

// 字体栈（tokens.json 的 type.families）里列的、需要自托管的四款，OFL-1.1。变量字体一个文件覆盖 100–900 字重；
// 等宽只要 400（设计系统的等宽字号字重只用 400）。拉丁文只带 latin 和 latin-ext，站点只有中英两版。
const FONTS = [
  { family: "Inter Tight", pkg: "@fontsource-variable/inter-tight", css: "wght.css", keep: /-(latin|latin-ext)-wght-normal \*\/$/ },
  { family: "Noto Sans SC", pkg: "@fontsource-variable/noto-sans-sc", css: "wght.css", keep: /wght-normal \*\/$/ },
  { family: "Noto Serif SC", pkg: "@fontsource-variable/noto-serif-sc", css: "wght.css", keep: /wght-normal \*\/$/ },
  { family: "IBM Plex Mono", pkg: "@fontsource/ibm-plex-mono", css: "400.css", keep: /-(latin|latin-ext)-400-normal \*\/$/ },
];

export function buildFontsCss() {
  const out = [
    "/* 回退字体：由 scripts/gen-fonts.mjs 从 node_modules 里的 @fontsource 包生成，不要手改（npm run gen:fonts）。",
    " * 字体文件由主站自己提供，不请求 fonts.googleapis.com、fonts.gstatic.com；中文按 unicode-range 分片加载。",
    " * 四款字体的许可都是 SIL Open Font License 1.1（见各包的 LICENSE）。 */",
  ];
  for (const f of FONTS) {
    const dir = pkgDir(f.pkg);
    const src = readFileSync(`${dir}${f.css}`, "utf8");
    for (const block of src.split(/\n(?=\/\* )/)) {
      const head = block.split("\n")[0];
      if (!f.keep.test(head)) continue;
      const get = (re) => block.match(re)[1];
      const file = get(/url\(\.\/files\/([^)]+\.woff2)\)/);
      const weight = get(/font-weight: ([^;]+);/);
      const range = get(/unicode-range: ([^;]+);/);
      out.push(
        "",
        `/* ${head.slice(3, -3).trim()} */`,
        "@font-face {",
        `  font-family: "${f.family}";`,
        "  font-style: normal;",
        "  font-display: swap;",
        `  font-weight: ${weight};`,
        `  src: url("../node_modules/${f.pkg}/files/${file}") format("woff2");`,
        `  unicode-range: ${range};`,
        "}",
      );
    }
  }
  return out.join("\n") + "\n";
}

function main() {
  const css = buildFontsCss();
  if (process.argv.includes("--check")) {
    let current = "";
    try {
      current = readFileSync(FONTS_CSS, "utf8");
    } catch {
      // 文件不存在，按不一致处理
    }
    if (current !== css) {
      console.error("src/fonts.css 和依赖里的字体不一致：运行 npm run gen:fonts");
      process.exit(1);
    }
    return;
  }
  writeFileSync(FONTS_CSS, css);
}

if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) main();
