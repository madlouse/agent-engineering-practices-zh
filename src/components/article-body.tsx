import type { Block } from "@/content/types";

export function ArticleBody({ blocks }: { blocks: Block[] }) {
  const leadAt = blocks.findIndex((block) => block.t === "p");

  return (
    <div className="max-w-2xl space-y-6">
      {blocks.map((block, index) => {
        if (block.t === "h2") {
          return (
            <h2
              id={block.id}
              key={block.id}
              className="scroll-mt-28 pt-10 font-serif text-3xl font-semibold leading-snug tracking-tight text-balance text-ink"
            >
              {block.x}
            </h2>
          );
        }
        if (block.t === "h3") {
          return (
            <h3
              id={block.id}
              key={block.id}
              className="scroll-mt-28 pt-4 font-serif text-2xl font-semibold leading-snug text-balance text-ink"
            >
              {block.x}
            </h3>
          );
        }
        if (block.t === "p") {
          return (
            <p
              key={index}
              className={
                index === leadAt
                  ? "text-xl leading-9 text-ink"
                  : "text-lg leading-8 text-ink"
              }
            >
              {block.x}
            </p>
          );
        }
        if (block.t === "ul" || block.t === "ol") {
          const List = block.t === "ul" ? "ul" : "ol";
          return (
            <List
              key={index}
              className={
                block.t === "ul"
                  ? "list-disc space-y-3 pl-5 text-lg leading-8 text-ink marker:text-cinnabar"
                  : "list-decimal space-y-4 pl-6 text-lg leading-8 text-ink marker:font-mono marker:text-sm marker:text-cinnabar"
              }
            >
              {block.items.map((item) => (
                <li key={item} className="pl-1">
                  {item}
                </li>
              ))}
            </List>
          );
        }
        if (block.t === "q") {
          return (
            <blockquote key={index} className="border-l-2 border-cinnabar bg-wash px-6 py-5">
              <p className="font-serif text-2xl leading-snug text-balance text-ink">{block.x}</p>
              {block.by ? <p className="mt-3 text-sm text-muted">{block.by}</p> : null}
            </blockquote>
          );
        }
        if (block.t === "code") {
          return <CodeFigure key={index} label={block.label} source={block.x} />;
        }
        if (block.t === "video") {
          return (
            <figure key={index} className="border border-line bg-card">
              <video controls playsInline preload="metadata" className="w-full bg-ink" src={block.src}>
                <a href={block.src} className="text-paper underline">
                  打开原视频
                </a>
              </video>
              <figcaption className="border-t border-line px-4 py-3 text-sm leading-6 text-muted">
                <span className="text-cinnabar">原文视频，不译。</span> {block.caption}
              </figcaption>
            </figure>
          );
        }
        if (block.t === "figure") {
          return (
            <figure key={index} className="border border-line bg-card">
              <img src={block.src} alt={block.alt ?? block.caption} className="w-full" />
              <figcaption className="border-t border-line px-4 py-3 text-sm leading-6 text-muted">
                <span className="text-cinnabar">原图，不译。</span> {block.caption}
              </figcaption>
            </figure>
          );
        }
        return (
          <div key={index} className="border border-line bg-card px-5 py-4">
            <p className="text-xs font-medium tracking-wide text-cinnabar">注</p>
            <p className="mt-2 text-sm leading-7 text-muted">{block.x}</p>
          </div>
        );
      })}
    </div>
  );
}

function flowOf(source: string) {
  const lines = source
    .split("\n")
    .map((line) => line.trimEnd())
    .filter((line) => line.trim().length > 0);
  const steps = lines.filter((line) => /^\s*→\s*/.test(line));
  if (steps.length < 2 || steps.length < lines.length - 1) return null;
  const root = lines.find((line) => !/^\s*→\s*/.test(line))?.trim();
  return { root, steps: steps.map((line) => line.replace(/^\s*→\s*/, "")) };
}

function CodeFigure({ label, source }: { label?: string; source: string }) {
  const flow = flowOf(source);
  return (
    <figure className="max-w-full border border-line bg-card text-ink">
      <figcaption className="border-b border-line px-4 py-2 text-xs font-medium tracking-wide text-cinnabar">
        {label ?? "代码"}
      </figcaption>
      {flow ? (
        <div className="px-4 py-4">
          {flow.root ? <p className="text-base leading-7">{flow.root}</p> : null}
          <ol className={flow.root ? "mt-3 border-l border-cinnabar" : "border-l border-cinnabar"}>
            {flow.steps.map((step, index) => (
              <li key={step} className="flex gap-3 py-1.5 pl-4 text-base leading-7">
                <span className="w-6 shrink-0 pt-0.5 font-mono text-xs text-cinnabar tabular-nums">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      ) : (
        <pre className="code-scroll max-w-full overflow-x-auto px-4 py-4 text-sm leading-7">{source}</pre>
      )}
    </figure>
  );
}

export function headingsOf(blocks: Block[]) {
  return blocks.filter(
    (block): block is Extract<Block, { t: "h2" | "h3" }> => block.t === "h2" || block.t === "h3",
  );
}