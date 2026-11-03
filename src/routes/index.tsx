import { createFileRoute, Link } from "@tanstack/react-router";
import { Masthead } from "@/components/masthead";
import { posts } from "@/content";
import { SECTION_LABEL, type Section } from "@/content/types";

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  const featured = posts[0];
  const rest = posts.slice(1);
  const groups: Section[] = ["engineering", "life"];

  return (
    <div className="min-h-screen bg-paper text-ink">
      <Masthead />
      <main className="mx-auto max-w-6xl px-5 pb-24">
        <section className="grid gap-10 border-b border-line py-12 lg:grid-cols-12">
          <p className="text-sm text-cinnabar lg:col-span-3">开篇</p>
          <div className="lg:col-span-9">
            <p className="text-sm text-muted">
              {featured.sourceName} · {featured.date} · {featured.minutes} 分钟
              {featured.official ? " · 官方中文" : " · 中文整理"}
            </p>
            <h2 className="mt-3 font-serif text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
              <Link to="/posts/$slug" params={{ slug: featured.slug }} className="hover:text-cinnabar">
                {featured.title}
              </Link>
            </h2>
            <p className="mt-4 max-w-2xl text-lg leading-relaxed text-muted">{featured.dek}</p>
            <Link
              to="/posts/$slug"
              params={{ slug: featured.slug }}
              className="mt-6 inline-flex min-h-11 items-center text-sm font-medium text-ink underline decoration-cinnabar decoration-2 underline-offset-4"
            >
              阅读全文
            </Link>
          </div>
        </section>

        {groups.map((section) => {
          const items = rest.filter((post) => post.section === section);
          if (items.length === 0 && featured.section !== section) return null;
          const list = posts.filter((post) => post.section === section && post.slug !== featured.slug);
          return (
            <section key={section} id={section} className="scroll-mt-20 border-b border-line py-12">
              <div className="grid gap-8 lg:grid-cols-12">
                <h2 className="font-serif text-2xl font-semibold lg:col-span-3">{SECTION_LABEL[section]}</h2>
                <ol className="lg:col-span-9">
                  {list.map((post, index) => (
                    <li key={post.slug} className="border-t border-line first:border-t-0">
                      <Link
                        to="/posts/$slug"
                        params={{ slug: post.slug }}
                        className="group -mx-3 grid gap-3 rounded-md px-3 py-6 motion-safe:transition-colors hover:bg-wash sm:grid-cols-12 sm:items-baseline"
                      >
                        <span className="font-mono text-sm text-faint sm:col-span-1">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <span className="sm:col-span-7">
                          <span className="font-serif text-2xl font-semibold leading-snug group-hover:text-cinnabar">
                            {post.title}
                          </span>
                          <span className="mt-2 block text-base leading-7 text-muted">{post.dek}</span>
                        </span>
                        <span className="text-sm text-faint sm:col-span-4 sm:text-right">
                          {post.sourceName}
                          <span className="mt-1 block">
                            {post.minutes} 分钟
                            {post.blocksEn ? " · 中英" : ""}
                            {post.official ? " · 官方中文" : ""}
                          </span>
                        </span>
                      </Link>
                    </li>
                  ))}
                </ol>
              </div>
            </section>
          );
        })}

        <section id="method" className="scroll-mt-20 grid gap-8 py-14 lg:grid-cols-12">
          <h2 className="font-serif text-2xl font-semibold lg:col-span-3">体例</h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:col-span-9">
            {[
              ["栏目", "工程实践，以及 Agent 与生活。新文章只进已有栏目，不另起视觉。"],
              ["来源", "每篇保留作者、日期、原文链接和版权方。官方中文优先，不改写。"],
              ["译文", "无官方中文时按克制的中文技术写作：直角引号、中英留白、同一术语不换词。"],
              ["阅读", "文章页有目录、进度、代码块和上下篇。有英文稿的篇目可以切换。"],
            ].map(([title, body]) => (
              <div key={title} className="border-t border-line pt-4">
                <h3 className="font-medium text-ink">{title}</h3>
                <p className="mt-2 text-sm leading-7 text-muted">{body}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
      <footer className="border-t border-line">
        <p className="mx-auto max-w-6xl px-5 py-8 text-sm leading-7 text-faint">
          内容版权归原作者及公司。本站只作学习分享。如需撤下，以原文链接为准联系处理。
        </p>
      </footer>
    </div>
  );
}
