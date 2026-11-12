import { useEffect, useRef, useState } from "react";
import type { PlayerRef } from "@remotion/player";
import type { Explainer } from "@/content/explainers";
import { SHORT_FPS, SHORT_FRAMES } from "@/shorts/timing";

type PlayerComponent = typeof import("@remotion/player").Player;
type ShortComponent = typeof import("@/shorts/explainer-short").ExplainerShort;

type Cue = {
  duration: number;
  beats: number[];
  voice: string;
};

export function FeynmanFilm({ film, lang }: { film: Explainer; lang: "zh" | "en" }) {
  const playerRef = useRef<PlayerRef>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [zoom, setZoom] = useState<1 | 2 | 3>(1);
  const [reduced, setReduced] = useState(false);
  const [mods, setMods] = useState<{ Player: PlayerComponent; Short: ShortComponent } | null>(null);
  const [loadError, setLoadError] = useState("");
  const [cue, setCue] = useState<Cue | null>(null);
  const [voiceBlocked, setVoiceBlocked] = useState(false);
  const [voiceLang, setVoiceLang] = useState<"zh" | "en">(lang);

  useEffect(() => {
    setVoiceLang(lang);
  }, [lang]);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReduced(media.matches);
    apply();
    media.addEventListener("change", apply);
    return () => media.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    let live = true;
    Promise.all([import("@remotion/player"), import("@/shorts/explainer-short")]).then(([player, short]) => {
      if (!live) return;
      setMods({ Player: player.Player, Short: short.ExplainerShort });
    }).catch((error: unknown) => {
      if (!live) return;
      setLoadError(error instanceof Error ? error.message : String(error));
    });
    return () => {
      live = false;
    };
  }, []);

  useEffect(() => {
    let live = true;
    setCue(null);
    setVoiceBlocked(false);
    fetch(`/explainers/${film.slug}.${voiceLang}.json`)
      .then((response) => (response.ok ? response.json() : null))
      .then((data: Cue | null) => {
        if (!live || !data || typeof data.duration !== "number" || !Array.isArray(data.beats)) return;
        setCue(data);
      })
      .catch(() => {
        if (live) setCue(null);
      });
    return () => {
      live = false;
    };
  }, [film.slug, voiceLang]);

  useEffect(() => {
    const player = playerRef.current;
    const audio = audioRef.current;
    if (!player || !audio || !cue) return;

    const place = () => {
      const next = player.getCurrentFrame() / SHORT_FPS;
      if (Number.isFinite(next)) audio.currentTime = next;
    };
    const onPlay = () => {
      place();
      void audio.play().catch(() => setVoiceBlocked(true));
    };
    const onPause = () => audio.pause();
    const onSeeked = () => {
      place();
      if (player.isPlaying()) void audio.play().catch(() => setVoiceBlocked(true));
    };
    const onEnded = () => audio.pause();
    const onMute = (event: { detail: { isMuted: boolean } }) => {
      audio.muted = event.detail.isMuted;
    };
    const onVolume = (event: { detail: { volume: number } }) => {
      audio.volume = event.detail.volume;
    };

    player.addEventListener("play", onPlay);
    player.addEventListener("pause", onPause);
    player.addEventListener("seeked", onSeeked);
    player.addEventListener("ended", onEnded);
    player.addEventListener("mutechange", onMute);
    player.addEventListener("volumechange", onVolume);
    return () => {
      player.removeEventListener("play", onPlay);
      player.removeEventListener("pause", onPause);
      player.removeEventListener("seeked", onSeeked);
      player.removeEventListener("ended", onEnded);
      player.removeEventListener("mutechange", onMute);
      player.removeEventListener("volumechange", onVolume);
      audio.pause();
    };
  }, [mods, cue, voiceLang]);

  const followPicture = () => {
    const audio = audioRef.current;
    const player = playerRef.current;
    if (!audio || !player) return;
    audio.currentTime = player.getCurrentFrame() / SHORT_FPS;
    if (player.isPlaying()) {
      void audio.play().then(() => setVoiceBlocked(false)).catch(() => setVoiceBlocked(true));
    } else {
      audio.pause();
    }
  };

  const unlockVoice = () => {
    const player = playerRef.current;
    if (player && !player.isPlaying()) player.play();
    followPicture();
  };

  const durationInFrames = cue ? Math.max(1, Math.round(cue.duration * SHORT_FPS)) : SHORT_FRAMES;
  const beats = cue?.beats?.length === film.scenes.length ? cue.beats : film.scenes.map((scene) => scene.at);
  const zoomClass = zoom === 1 ? "short-fit" : zoom === 2 ? "short-lg" : "short-xl";

  return (
    <section aria-label="三分钟讲解" className="max-w-2xl">
      <p className="text-xs font-medium tracking-wide text-cinnabar">三分钟讲解</p>
      <p className="mt-2 text-sm leading-6 text-muted">先看短片，再读文章。</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <ZoomButton current={zoom} value={1} onPick={setZoom}>
          正常
        </ZoomButton>
        <ZoomButton current={zoom} value={2} onPick={setZoom}>
          放大
        </ZoomButton>
        <ZoomButton current={zoom} value={3} onPick={setZoom}>
          更大
        </ZoomButton>
        <VoiceButton current={voiceLang} value="zh" onPick={setVoiceLang}>
          中文
        </VoiceButton>
        <VoiceButton current={voiceLang} value="en" onPick={setVoiceLang}>
          English
        </VoiceButton>
        {voiceBlocked ? (
          <button type="button" onClick={unlockVoice} className="inline-flex min-h-11 items-center border border-cinnabar bg-card px-4 text-sm text-cinnabar">
            打开声音
          </button>
        ) : null}
      </div>
      {cue ? (
        <audio
          ref={audioRef}
          key={`${film.slug}-${voiceLang}`}
          src={`/explainers/${film.slug}.${voiceLang}.mp3`}
          preload="auto"
        />
      ) : null}
      <div className="short-scroll mt-3 border border-line bg-paper" onClick={followPicture}>
        <div className={zoomClass}>
          {mods ? (
            <mods.Player
              ref={playerRef}
              key={`${film.slug}-${voiceLang}-${durationInFrames}`}
              component={mods.Short}
              inputProps={{
                slug: film.slug,
                beats,
                reduced,
              }}
              durationInFrames={durationInFrames}
              compositionWidth={1080}
              compositionHeight={1920}
              fps={SHORT_FPS}
              controls
              clickToPlay
              allowFullscreen
              doubleClickToFullscreen
              spaceKeyToPlayOrPause
              alwaysShowControls
              acknowledgeRemotionLicense
              style={{ /* lint-tokens-ignore：Remotion Player 只从 style.width 读宽度，class 不起作用 */ width: "100%" }}
            />
          ) : (
            <div className="short-poster">
              <p className="text-xs font-medium tracking-wide text-cinnabar">01 / 05</p>
              <p className="mt-6 font-serif text-3xl font-semibold leading-snug text-balance">{film.scenes[0]?.title}</p>
              <p className="mt-8 text-sm text-muted">{loadError || "加载中"}</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function ZoomButton({
  current,
  value,
  onPick,
  children,
}: {
  current: 1 | 2 | 3;
  value: 1 | 2 | 3;
  onPick: (value: 1 | 2 | 3) => void;
  children: string;
}) {
  const on = current === value;
  return (
    <button
      type="button"
      aria-pressed={on}
      onClick={() => onPick(value)}
      className={
        on
          ? "inline-flex min-h-11 items-center border border-ink bg-ink px-4 text-sm text-paper"
          : "inline-flex min-h-11 items-center border border-line bg-card px-4 text-sm text-ink"
      }
    >
      {children}
    </button>
  );
}

function VoiceButton({
  current,
  value,
  onPick,
  children,
}: {
  current: "zh" | "en";
  value: "zh" | "en";
  onPick: (value: "zh" | "en") => void;
  children: string;
}) {
  const on = current === value;
  return (
    <button
      type="button"
      aria-pressed={on}
      onClick={() => onPick(value)}
      className={
        on
          ? "inline-flex min-h-11 items-center border border-ink bg-ink px-4 text-sm text-paper"
          : "inline-flex min-h-11 items-center border border-line bg-card px-4 text-sm text-ink"
      }
    >
      {children}
    </button>
  );
}
