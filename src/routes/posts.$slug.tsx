import { useEffect, useState } from "react";
import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArticleBody, headingsOf } from "@/components/article-body";
import { FeynmanFilm } from "@/components/feynman-film";
import { Masthead } from "@/components/masthead";
import { getPost, neighbors } from "@/content";
import { getExplainer } from "@/content/explainers";
import { SECTION_LABEL } from "@/content/types";

export const Route = createFileRoute("/posts/$slug")({
  loader: ({ params }) => {
    const post = getPost(params.slug);
    if (!post) throw notFound();
    return { post };
  },
  notFoundComponent: Missing,
  component: ArticlePage,
});

function Missing() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center px-5">
      <p className="text-sm text-cinnabar">未收录</p>
      <h1 className="mt-3 font-serif text-4xl font-semibold text-balance">这篇还不在目录里。</h1>
      <Link to="/" className="mt-6 inline-flex min-h-11 items-center text-sm underline decoration-cinnabar underline-offset-4">
        返回目录
      </Link>
    </main>
  );
}

function ArticlePage() {
  const { post } = Route.useLoaderData();
  const { prev, next } = neighbors(post.slug);
  const [lang, setLang] = useState<"zh" | "en">("zh");
  const [progress, setProgress] = useState(0);
  const [active, setActive] = useState("");
  const blocks = lang === "en" && post.blocksEn ? post.blocksEn : post.blocks;
  const headings = headingsOf(blocks);
  const headingKey = headings.map((heading) => `${heading.t}:${heading.id}`).join("|");
  const film = getExplainer(post.slug);

  useEffect(() => {
    const onScroll = () => {
      const scrolled = window.scrollY;
      const height = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(height > 0 ? Math.min(1, scrolled / height) : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [lang, post.slug]);

  useEffect(() => {
    const nodes = headingKey
      .split("|")
      .filter(Boolean)
      .map((item) => document.getElementById(item.split(":")[1] ?? ""))
      .filter((node): node is HTMLElement => Boolean(node));
    if (nodes.length === 0) return;
    const seen = new Map<string, number>();
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          seen.set(entry.target.id, entry.isIntersecting ? entry.boundingClientRect.top : Number.POSITIVE_INFINITY);
        }
        const nextId = [...seen.entries()]
          .filter(([, top]) => top < window.innerHeight * 0.45)
          .sort((a, b) => b[1] - a[1])[0]?.[0];
        if (nextId) setActive(nextId);
      },
      { rootMargin: "0px 0px -50% 0px", threshold: [0, 1] },
    );
    for (const node of nodes) observer.observe(node);
    return () => observer.disconnect();
  }, [headingKey]);

  return (
    <div className="min-h-screen bg-paper text-ink">
      <Masthead compact progress={progress} />
      <article data-lang={lang} className="mx-auto grid max-w-6xl gap-y-10 px-5 py-10 lg:grid-cols-12 lg:gap-x-8 lg:py-14">
        <div className="lg:col-span-7">
          <p className="text-sm text-cinnabar">
            {SECTION_LABEL[post.section]}
            {post.official ? " · 官方中文" : " · 中文整理"}
          </p>
          <h1
            className={
              lang === "en"
                ? "mt-4 max-w-3xl font-serif text-4xl font-semibold leading-tight tracking-tight text-balance text-ink sm:text-5xl"
                : "mt-4 max-w-xl font-serif text-4xl font-semibold leading-tight tracking-tight text-balance text-ink sm:text-5xl"
            }
          >
            {lang === "en" && post.titleEn ? post.titleEn : post.title}
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-muted">
            {lang === "en" && post.dekEn ? post.dekEn : post.dek}
          </p>
          <div className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm text-faint tabular-nums">
            <span>{post.author}</span>
            <span aria-hidden>·</span>
            <span>{post.date}</span>
            <span aria-hidden>·</span>
            <span>{post.minutes} 分钟</span>
          </div>
          {post.blocksEn ? (
            <div className="mt-4 inline-flex rounded-full border border-line p-1">
              <button
                type="button"
                onClick={() => setLang("zh")}
                className={
                  lang === "zh"
                    ? "min-h-11 rounded-full bg-ink px-4 text-sm text-paper"
                    : "min-h-11 rounded-full px-4 text-sm text-muted"
                }
              >
                中文
              </button>
              <button
                type="button"
                onClick={() => setLang("en")}
                className={
                  lang === "en"
                    ? "min-h-11 rounded-full bg-ink px-4 text-sm text-paper"
                    : "min-h-11 rounded-full px-4 text-sm text-muted"
                }
              >
                English
              </button>
            </div>
          ) : null}
          {film ? (
            <div className="mt-10">
              <FeynmanFilm film={film} lang={lang} />
            </div>
          ) : null}
          <details className="mt-8 border border-line bg-card lg:hidden">
            <summary className="px-4 py-3 text-sm font-medium text-ink">目录 · {headings.filter((heading) => heading.t === "h2").length} 节</summary>
            <div className="border-t border-line px-2 py-2">
              <Toc headings={headings} active={active} onPick={setActive} />
            </div>
          </details>
          <div className="mt-10">
            <ArticleBody blocks={blocks} />
          </div>
          <aside className="mt-14 max-w-2xl border border-line bg-card px-5 py-4 text-sm leading-7 text-muted">
            <p className="text-xs font-medium tracking-wide text-cinnabar">来源与版权</p>
            <p className="mt-2">
              来源：{" "}
              <a href={post.source} className="text-ink underline decoration-cinnabar underline-offset-4">
                {post.sourceName}
              </a>
            </p>
            <p className="mt-1">版权：{post.copyright}。本页仅供学习分享，不替代原文。</p>
          </aside>
          <nav className="mt-10 grid max-w-2xl gap-4 border-t border-line pt-8 sm:grid-cols-2">
            {prev ? (
              <Link to="/posts/$slug" params={{ slug: prev.slug }} className="group min-h-11">
                <span className="text-sm text-faint">上一篇</span>
                <span className="mt-1 block font-serif text-xl text-balance group-hover:text-cinnabar motion-safe:transition-colors">
                  {prev.title}
                </span>
              </Link>
            ) : (
              <span />
            )}
            {next ? (
              <Link to="/posts/$slug" params={{ slug: next.slug }} className="group min-h-11 sm:text-right">
                <span className="text-sm text-faint">下一篇</span>
                <span className="mt-1 block font-serif text-xl text-balance group-hover:text-cinnabar motion-safe:transition-colors">
                  {next.title}
                </span>
              </Link>
            ) : null}
          </nav>
        </div>
        <aside className="max-lg:hidden lg:col-span-4 lg:col-start-9">
          <div className="sticky top-24">
            <p className="text-xs font-medium tracking-wide text-cinnabar">目录</p>
            <Toc headings={headings} active={active} onPick={setActive} />
          </div>
        </aside>
      </article>
    </div>
  );
}

function Toc({
  headings,
  active,
  onPick,
}: {
  headings: ReturnType<typeof headingsOf>;
  active: string;
  onPick: (id: string) => void;
}) {
  return (
    <ol className="toc-rail mt-3 border-l border-line">
      {headings.map((heading) => {
        const on = heading.id === active;
        return (
          <li key={heading.id}>
            <a
              href={`#${heading.id}`}
              title={heading.x}
              onClick={() => onPick(heading.id)}
              className={
                heading.t === "h3"
                  ? `line-clamp-2 border-l-2 py-1 pr-3 pl-6 text-sm leading-6 ${on ? "-ml-px border-cinnabar text-ink" : "border-transparent text-faint hover:text-ink"}`
                  : `line-clamp-2 border-l-2 py-1.5 pr-3 pl-4 text-sm leading-6 ${on ? "-ml-px border-cinnabar text-ink" : "border-transparent text-muted hover:text-ink"}`
              }
            >
              {heading.x}
            </a>
          </li>
        );
      })}
    </ol>
  );
}