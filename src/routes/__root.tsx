import { createRootRoute, HeadContent, Outlet, Scripts } from "@tanstack/react-router";
import { AuthProvider } from "@/lib/auth/provider";
import { LangProvider } from "@/lib/lang";
import { PreviewHostBridge } from "@/components/preview-host-bridge";
import { THEME_BOOT_SCRIPT } from "@/lib/theme-init.mjs";
import tokens from "../../docs/uiue/system/tokens.json";
import appCss from "../styles.css?url";

const paperColor = tokens.color.tokens.find((t) => t.name === "vc-paper")!.value as { light: string; dark: string };

const APP_NAME = "看清 · Velicoach";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: APP_NAME },
      {
        name: "description",
        content: "人和 agent，一起走向还没到来的 AGI。按时间阅读这条路上的文章。",
      },
    ],
    links: [
      { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
      { rel: "stylesheet", href: appCss },
      { rel: "manifest", href: "/__grok/manifest.webmanifest" },
      { rel: "apple-touch-icon", href: "/__grok/icon-180.png" },
    ],
    scripts: [{ children: THEME_BOOT_SCRIPT }],
  }),
  component: () => (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        <meta name="theme-color" media="(prefers-color-scheme: light)" content={paperColor.light} />
        <meta name="theme-color" media="(prefers-color-scheme: dark)" content={paperColor.dark} />
        <HeadContent />
      </head>
      <body>
        <PreviewHostBridge />
        <AuthProvider>
          <LangProvider>
            <Outlet />
          </LangProvider>
        </AuthProvider>
        <Scripts />
      </body>
    </html>
  ),
});
