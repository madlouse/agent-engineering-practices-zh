import type { ReactNode } from "react";
import { AbsoluteFill } from "remotion";

export const ink = "var(--color-ink)";
export const paper = "var(--color-paper)";
export const card = "var(--color-card)";
export const line = "var(--color-line)";
export const muted = "var(--color-muted)";
export const faint = "var(--color-faint)";
export const cinnabar = "var(--color-cinnabar)";
export const wash = "var(--color-wash)";

export function clamp01(n: number) {
  return Math.min(1, Math.max(0, n));
}

export function ease(t: number) {
  const x = clamp01(t);
  return x * x * (3 - 2 * x);
}

export function reveal(p: number, delay: number, span = 0.22) {
  if (delay <= 0) return 1;
  return ease(clamp01((p - delay) / span));
}

export function Stage({
  index,
  kicker,
  caption,
  note,
  children,
}: {
  index: number;
  kicker: string;
  caption: string;
  note?: string;
  children: ReactNode;
}) {
  return (
    <AbsoluteFill
      style={{
        background: paper,
        color: ink,
        fontFamily: '"Noto Sans SC", "IBM Plex Sans", sans-serif',
      }}
    >
      <div style={{ display: "flex", height: "100%", flexDirection: "column", padding: "68px 64px 72px" }}>
        <p style={{ margin: 0, fontSize: 34, fontWeight: 650, letterSpacing: "0.12em", color: cinnabar }}>
          {String(index).padStart(2, "0")} / 05 · {kicker}
        </p>
        <div style={{ display: "flex", flex: 1, flexDirection: "column", justifyContent: "center" }}>{children}</div>
        <p
          style={{
            margin: 0,
            fontFamily: '"Noto Serif SC", "Source Serif 4", serif',
            fontSize: 68,
            fontWeight: 650,
            lineHeight: 1.22,
          }}
        >
          {caption}
        </p>
        {note ? <p style={{ margin: "18px 0 0", fontSize: 30, lineHeight: 1.45, color: muted }}>{note}</p> : null}
      </div>
    </AbsoluteFill>
  );
}

export function Box({
  label,
  sub,
  live = 1,
  hot = false,
  w = 280,
}: {
  label: string;
  sub?: string;
  live?: number;
  hot?: boolean;
  w?: number;
}) {
  return (
    <div
      style={{
        width: "100%",
        maxWidth: w,
        boxSizing: "border-box",
        border: `2px solid ${hot ? cinnabar : line}`,
        background: hot ? wash : card,
        padding: "22px 20px",
        opacity: live,
        transform: `translateY(${(1 - live) * 16}px)`,
      }}
    >
      <p style={{ margin: 0, fontSize: 36, fontWeight: 650, lineHeight: 1.25 }}>{label}</p>
      {sub ? <p style={{ margin: "8px 0 0", fontSize: 26, lineHeight: 1.35, color: muted }}>{sub}</p> : null}
    </div>
  );
}
