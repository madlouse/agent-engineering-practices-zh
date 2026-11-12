import type { ReactNode } from "react";
import { AbsoluteFill } from "remotion";

// 这些短片是固定 1080×1920 的视频画面（Remotion 合成），数值是视频像素，不是页面里的间距和字号，
// 设计 token 的阶梯用不上。所以每一处写死的数值都标了 lint-tokens-ignore；颜色仍然只引用 token。
// 接入主站时这些短片整体换新（docs/uiue/design-system.md「进代码」），到时一并去掉标记。
export const ink = "var(--vc-text)";
export const paper = "var(--vc-paper)";
export const card = "var(--vc-paper-surface)";
export const line = "var(--vc-paper-line)";
export const muted = "var(--vc-text-2)";
export const faint = "var(--vc-text-3)";
export const cinnabar = "var(--vc-cinnabar-deep)";
export const wash = "color-mix(in srgb, var(--vc-cinnabar-deep) 12%, var(--vc-paper))";

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
      <div style={{ /* lint-tokens-ignore */ display: "flex", height: "100%", flexDirection: "column", padding: "68px 64px 72px" }}>
        <p style={{ /* lint-tokens-ignore */ margin: 0, fontSize: 34, fontWeight: 650, letterSpacing: "0.12em", color: cinnabar }}>
          {String(index).padStart(2, "0")} / 05 · {kicker}
        </p>
        <div style={{ /* lint-tokens-ignore */ display: "flex", flex: 1, flexDirection: "column", justifyContent: "center" }}>{children}</div>
        <p
          style={{
            margin: 0,
            fontFamily: '"Noto Serif SC", "Source Serif 4", serif',
            fontSize: 68, // lint-tokens-ignore
            fontWeight: 650,
            lineHeight: 1.22, // lint-tokens-ignore
          }}
        >
          {caption}
        </p>
        {note ? <p style={{ /* lint-tokens-ignore */ margin: "18px 0 0", fontSize: 30, lineHeight: 1.45, color: muted }}>{note}</p> : null}
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
        padding: "22px 20px", // lint-tokens-ignore
        opacity: live,
        transform: `translateY(${(1 - live) * 16}px)`,
      }}
    >
      <p style={{ /* lint-tokens-ignore */ margin: 0, fontSize: 36, fontWeight: 650, lineHeight: 1.25 }}>{label}</p>
      {sub ? <p style={{ /* lint-tokens-ignore */ margin: "8px 0 0", fontSize: 26, lineHeight: 1.35, color: muted }}>{sub}</p> : null}
    </div>
  );
}
