import { createFileRoute, Link } from "@tanstack/react-router";
import { Masthead } from "@/components/masthead";
import { posts } from "@/content";
import { SECTION_LABEL } from "@/content/types";
import { useLang } from "@/lib/lang";

type Row = {
  date: string;
  title: string;
  titleEn?: string;
  author: string;
  line: string;
  lineEn?: string;
  to?: string;
  href?: string;
  mark: string;
  markEn: string;
};

const MARK_EN = { engineering: "Engineering", life: "Life" } as const;

const earlier: Row[] = [
  {
    date: "2019-03-13",
    title: "苦涩的教训",
    titleEn: "The Bitter Lesson",
    author: "理查德·萨顿",
    line: "七十年的人工智能研究里，走得远的是能随着计算一起变大的通用方法，不是把人以为自己怎么思考写进系统。搜索和学习，是这样两条路。",
    lineEn:
      "Across seventy years of AI research, the methods that last are the general ones that grow with computation, not the ones that encode how we think we think. Search and learning are those two roads.",
    href: "https://www.incompleteideas.net/IncIdeas/BitterLesson.html",
    mark: "教训",
    markEn: "Lesson",
  },
  {
    date: "2025-07-18",
    title: "上下文工程：建造 Manus 的教训",
    titleEn: "Context Engineering: Lessons from Building Manus",
    author: "季逸超",
    line: "与其训练一个钉在海底的模型，不如让产品成为会随潮水升起的船。上下文要为缓存设计。工具宁可用遮罩，也不要随时拆掉。",
    lineEn:
      "Rather than train a model nailed to the seabed, let the product be a boat that rises with the tide. Design context for the cache. Mask tools instead of ripping them out.",
    href: "https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus",
    mark: "教训",
    markEn: "Lesson",
  },
];

export const Route = createFileRoute("/")({ component: Home });

function Home() {
  const { lang } = useLang();
  const en = lang === "en";
  const rows: Row[] = [
    ...earlier,
    ...posts.map((post) => ({
      date: post.date,
      title: post.title,
      titleEn: post.titleEn,
      author: post.author,
      line: post.dek,
      lineEn: post.dekEn,
      to: post.slug,
      mark: SECTION_LABEL[post.section],
      markEn: MARK_EN[post.section],
    })),
  ].sort((a, b) => a.date.localeCompare(b.date));

  const years = [...new Set(rows.map((row) => row.date.slice(0, 4)))];

  return (
    <div className="min-h-screen bg-paper text-ink">
      <Masthead compact />
      <main className="mx-auto max-w-6xl px-5 pb-24">
        <section className="grid items-end gap-10 border-b border-line py-12 lg:grid-cols-12 lg:py-16">
          <div className="lg:col-span-6">
            <h1 className="font-serif text-5xl font-semibold leading-tight tracking-tight text-balance sm:text-6xl">
              {en ? (
                <>
                  People and agents,
                  <br />
                  walking toward an AGI that has not arrived
                </>
              ) : (
                <>
                  人和智能体，
                  <br />
                  一起走向还没到来的 AGI
                </>
              )}
            </h1>
            <p className="mt-6 max-w-md text-lg leading-relaxed text-muted">
              {en
                ? "The digital years are already long. AGI is still ahead. For now we work together, and we also get through the day. The writing below is kept in time."
                : "数字化已经走了很久。AGI 还在前面。眼下要一起工作，也要一起把一天过完。下面按时间记着这条路上的文章。"}
            </p>
          </div>
          <figure className="lg:col-span-6">
            <img
              src="/chronicle/desk.jpg"
              alt="一张长桌从眼前的笔记本伸向窗边，远处放着一台合上的电脑"
              className="aspect-3/2 w-full object-cover"
            />
            <figcaption className="mt-3 text-sm leading-6 text-muted">
              {en
                ? "A notebook is close. A closed computer is farther down the same desk, toward the light in the window."
                : "近处是人的笔记，远处是还没打开的电脑。同一张桌子，从今天伸向窗边还亮着的地方。"}
            </figcaption>
          </figure>
        </section>

        <section id="record" className="scroll-mt-20 py-12">
          {years.map((year) => (
            <div key={year} className="grid gap-2 border-t border-line py-8 lg:grid-cols-12">
              <h2 className="font-serif text-3xl font-semibold text-cinnabar lg:col-span-2">{year}</h2>
              <ol className="lg:col-span-10">
                {rows
                  .filter((row) => row.date.startsWith(year))
                  .map((row) => (
                    <li key={row.title} className="border-b border-line py-7 last:border-b-0">
                      <p className="text-sm text-faint">
                        {row.date} · {row.author} · {en ? row.markEn : row.mark}
                      </p>
                      <h3 className="mt-2 font-serif text-3xl font-semibold leading-snug tracking-tight">
                        {row.to ? (
                          <Link to="/posts/$slug" params={{ slug: row.to }} className="hover:text-cinnabar">
                            {en && row.titleEn ? row.titleEn : row.title}
                          </Link>
                        ) : (
                          <a
                            href={row.href}
                            className="hover:text-cinnabar"
                            rel="noreferrer"
                            target="_blank"
                          >
                            {en && row.titleEn ? row.titleEn : row.title}
                          </a>
                        )}
                      </h3>
                      <p className="mt-3 max-w-2xl text-base leading-7 text-muted">{en && row.lineEn ? row.lineEn : row.line}</p>
                      {row.to ? (
                        <Link
                          to="/posts/$slug"
                          params={{ slug: row.to }}
                          className="mt-4 inline-flex min-h-11 items-center text-sm underline decoration-cinnabar underline-offset-4"
                        >
                          {en ? "Read" : "阅读"}
                        </Link>
                      ) : (
                        <a
                          href={row.href}
                          className="mt-4 inline-flex min-h-11 items-center text-sm underline decoration-cinnabar underline-offset-4"
                          rel="noreferrer"
                          target="_blank"
                        >
                          {en ? "Source" : "原文"}
                        </a>
                      )}
                    </li>
                  ))}
              </ol>
            </div>
          ))}
          <p className="border-t border-line pt-8 font-serif text-2xl leading-snug text-ink">
            {en ? "What comes after this has not been written." : "再往后，是还没写成的日子。"}
          </p>
        </section>
      </main>
      <footer className="border-t border-line">
        <p className="mx-auto max-w-6xl px-5 py-8 text-sm leading-7 text-faint">
          {en ? "Copyright stays with the authors." : "版权归原作者。"}
        </p>
      </footer>
    </div>
  );
}
