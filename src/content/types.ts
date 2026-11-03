export type Block =
  | { t: "p"; x: string }
  | { t: "h2"; id: string; x: string }
  | { t: "h3"; id: string; x: string }
  | { t: "ul"; items: string[] }
  | { t: "ol"; items: string[] }
  | { t: "q"; x: string; by?: string }
  | { t: "code"; x: string; label?: string }
  | { t: "note"; x: string }
  | { t: "video"; src: string; caption: string }
  | { t: "figure"; src: string; caption: string; alt?: string };

export type Section = "engineering" | "life";

export type Post = {
  slug: string;
  title: string;
  titleEn?: string;
  dek: string;
  dekEn?: string;
  author: string;
  date: string;
  minutes: number;
  source: string;
  sourceName: string;
  copyright: string;
  official: boolean;
  section: Section;
  blocks: Block[];
  blocksEn?: Block[];
};

export const SECTION_LABEL: Record<Section, string> = {
  engineering: "工程",
  life: "生活",
};
