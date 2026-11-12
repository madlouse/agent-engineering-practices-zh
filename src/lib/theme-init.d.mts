export const THEME_KEY: "vc-theme";
export type ThemeChoice = "auto" | "light" | "dark";
export function syncTheme(
  doc: { documentElement: { setAttribute(k: string, v: string): void; removeAttribute(k: string): void } },
  getStorage: () => { getItem(k: string): string | null; setItem(k: string, v: string): void },
  next?: string,
): ThemeChoice;
export const THEME_BOOT_SCRIPT: string;
