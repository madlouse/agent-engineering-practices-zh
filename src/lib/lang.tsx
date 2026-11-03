import { createContext, useContext, useState, type ReactNode } from "react";

export type Lang = "zh" | "en";

const LangContext = createContext<{ lang: Lang; setLang: (lang: Lang) => void } | null>(null);

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("zh");
  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

export function useLang() {
  const value = useContext(LangContext);
  if (!value) throw new Error("useLang needs LangProvider");
  return value;
}
