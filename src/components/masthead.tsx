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
            <h1 className="mt-0 max-w-3xl font-serif text-5xl font-semibold leading-tight tracking-tight text-balance text-ink sm:text-6xl">
              别人怎么和 agent 一起工作
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
              这里读公开的文章。有官方中文，就用官方中文。没有的，译成中文，并放上原文链接。
            </p>
          </div>
        </div>
      )}
    </>
  );
}