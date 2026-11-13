import js from "@eslint/js";
import prettier from "eslint-config-prettier";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import globals from "globals";
import tseslint from "typescript-eslint";

/** Flat ESLint config for the TanStack Start app-builder template. */
export default tseslint.config(
  {
    ignores: [
      "dist/**",
      ".output/**",
      ".vercel/**",
      ".nitro/**",
      "node_modules/**",
      "src/routeTree.gen.ts",
      // 画板的生成源：拼进画板的脚本片段，单个文件不是完整的模块，在画布里运行，不是站点代码（docs/uiue/prototypes/v1.1/README.md）
      "docs/uiue/prototypes/**",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: { ...globals.browser, ...globals.node },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
  // 沙箱预置的 src/lib 模块不改（AGENTS.md「What is already here」），里面有意吞掉异常的空 catch 放行；
  // 别的空块照样报错，我们自己的代码在 catch 里写明为什么可以忽略。
  {
    files: ["src/lib/**"],
    rules: { "no-empty": ["error", { allowEmptyCatch: true }] },
  },
  // Disable rules that conflict with Prettier formatting.
  prettier,
);
