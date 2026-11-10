import { Link } from "@tanstack/react-router";
import { useLang, type Lang } from "@/lib/lang";

export function Masthead({ progress }: { compact?: boolean; progress?: number }) {
  const { lang, setLang } = useLang();
  return (
    <div className="sticky top-0 z-30 bg-paper">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5">
        <Link to="/" className="group flex min-h-11 items-center gap-3">
          <span className="size-2 shrink-0 rounded-full bg-cinnabar" />
          <span className="font-serif text-xl font-semibold tracking-tight text-ink">{lang === "en" ? "Mind" : "看清"}</span>
          <span className="hidden text-sm text-muted sm:inline">Velicoach</span>
        </Link>
        <div className="flex items-center gap-1 sm:gap-2">
          <nav className="flex items-center text-sm text-muted">
            <a
              href="/#record"
              className="inline-flex min-h-11 items-center px-2 underline-offset-4 hover:text-ink hover:underline hover:decoration-cinnabar motion-safe:transition-colors"
            >
              {lang === "en" ? "Record" : "记录"}
            </a>
          </nav>
          <div className="flex items-center" role="group" aria-label={lang === "en" ? "Language" : "语言"}>
            <LangButton current={lang} value="zh" onPick={setLang}>
              中文
            </LangButton>
            <LangButton current={lang} value="en" onPick={setLang}>
              English
            </LangButton>
          </div>
        </div>
      </div>
      {typeof progress === "number" ? (
        <div className="h-1 bg-line" aria-hidden>
          <div className="h-full bg-cinnabar" style={{ width: `${progress * 100}%` }} />
        </div>
      ) : (
        <div className="h-px bg-line" />
      )}
    </div>
  );
}

function LangButton({
  current,
  value,
  onPick,
  children,
}: {
  current: Lang;
  value: Lang;
  onPick: (lang: Lang) => void;
  children: string;
}) {
  const on = current === value;
  return (
    <button
      type="button"
      aria-pressed={on}
      onClick={() => onPick(value)}
      className={
        on
          ? "inline-flex min-h-11 items-center bg-ink px-3 text-sm text-paper"
          : "inline-flex min-h-11 items-center px-3 text-sm text-muted"
      }
    >
      {children}
    </button>
  );
}
