import { Link } from "@tanstack/react-router";

export function Masthead({
  compact = false,
  progress,
}: {
  compact?: boolean;
  progress?: number;
}) {
  return (
    <>
      <div className="sticky top-0 z-30 bg-paper">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-5">
          <Link to="/" className="group flex min-h-11 items-center gap-3">
            <span className="size-2 shrink-0 rounded-full bg-cinnabar" />
            <span className="font-serif text-xl font-semibold tracking-tight text-ink">同席</span>
            <span className="hidden text-sm text-faint sm:inline">人和 agent</span>
          </Link>
          <nav className="flex items-center gap-1 text-sm text-muted sm:gap-2">
            <a
              href="/#engineering"
              className="inline-flex min-h-11 items-center px-2 underline-offset-4 hover:text-ink hover:underline hover:decoration-cinnabar motion-safe:transition-colors"
            >
              工程
            </a>
            <a
              href="/#life"
              className="inline-flex min-h-11 items-center px-2 underline-offset-4 hover:text-ink hover:underline hover:decoration-cinnabar motion-safe:transition-colors"
            >
              生活
            </a>
            <a
              href="/#method"
              className="inline-flex min-h-11 items-center px-2 underline-offset-4 hover:text-ink hover:underline hover:decoration-cinnabar motion-safe:transition-colors"
            >
              体例
            </a>
          </nav>
        </div>
        {typeof progress === "number" ? (
          <div className="h-1 bg-line" aria-hidden>
            <div className="h-full bg-cinnabar" style={{ width: `${progress * 100}%` }} />
          </div>
        ) : (
          <div className="h-px bg-line" />
        )}
      </div>
      {compact ? null : (
        <div className="border-b border-line">
          <div className="mx-auto max-w-6xl px-5 pt-12 pb-16 sm:pt-16 sm:pb-20">
            <p className="text-sm font-medium tracking-wide text-cinnabar">第 01 期 · 2026</p>
            <h1 className="mt-4 max-w-3xl font-serif text-5xl font-semibold leading-tight tracking-tight text-balance text-ink sm:text-6xl">
              先有框架，
              <br />
              再把文章放进去。
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
              公开的 Agent 工程实践，按同一套阅读结构收录。官方中文优先。没有官方中文时，按克制、准确的中文技术写作整理，并注明来源与版权。
            </p>
          </div>
        </div>
      )}
    </>
  );
}