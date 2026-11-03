import type { ReactElement } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { claudeScenes } from "@/shorts/claude";
import { danScenes } from "@/shorts/dankoe";
import { deepseekScenes } from "@/shorts/deepseek";
import { ease } from "@/shorts/kit";
import { manusScenes } from "@/shorts/manus";
import { shopifyScenes } from "@/shorts/shopify";
import { SHORT_FPS } from "@/shorts/timing";

const films: Record<string, Array<(props: { p: number }) => ReactElement>> = {
  "shopify-harness": shopifyScenes,
  "manus-rebuilding": manusScenes,
  "claude-code-review": claudeScenes,
  "deepseek-superagent": deepseekScenes,
  "dan-koe-one-day": danScenes,
};

export function ExplainerShort({
  slug,
  beats,
  reduced,
}: {
  slug: string;
  beats: number[];
  reduced: boolean;
}) {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const scenes = films[slug] ?? films["shopify-harness"];
  const marks = beats.length === scenes.length ? beats : scenes.map((_, i) => i / scenes.length);
  let index = 0;
  for (let i = 0; i < marks.length; i++) {
    if (frame >= marks[i] * durationInFrames) index = i;
  }
  const start = marks[index] * durationInFrames;
  const end = index === marks.length - 1 ? durationInFrames : marks[index + 1] * durationInFrames;
  const motionFrames = Math.min(end - start, 12 * SHORT_FPS);
  const raw = reduced ? 1 : Math.min(1, Math.max(0, (frame - start) / Math.max(1, motionFrames)));
  const View = scenes[index];
  return <View p={ease(raw)} />;
}
