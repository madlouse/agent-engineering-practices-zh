import { Box, cinnabar, card, ink, line, muted, reveal, Stage, wash } from "@/shorts/kit";

function Plain({ p }: { p: number }) {
  const doors = reveal(p, 0.25, 0.4);
  return (
    <Stage index={1} kicker="用大白话" caption="把会话藏起来。" note="一个人通常只能盯住三到五个会话。对外仍像只有一个 agent。">
      <div style={{ display: "flex", gap: 28 }}>
        <div style={{ opacity: reveal(p, 0) }}>
          <Box label="你看见的" sub="三到五个会话" w={320} hot />
        </div>
        <div style={{ flex: 1, opacity: doors }}>
          <Box label="Router" sub="前台。沟通，不把活干完" w={520} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 16 }}>
            {["Worker", "Worker", "Worker", "Worker"].map((name, i) => (
              <div key={i} style={{ border: `2px solid ${line}`, background: card, padding: "18px 14px", fontSize: 30, opacity: reveal(p, 0.4 + i * 0.08) }}>
                {name}
                <div style={{ color: muted, fontSize: 24, marginTop: 4 }}>门关着</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Stage>
  );
}

function Gap({ p }: { p: number }) {
  return (
    <Stage index={2} kicker="容易听错" caption="仓库不是文章的全部。" note="公开代码经过改写。Watchdog、存算分离，有些只是方向。">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 80px 1fr", alignItems: "center" }}>
        <div style={{ opacity: reveal(p, 0) }}>
          <Box label="仓库里的原型" sub="研究代码，不是产品" w={360} />
        </div>
        <div style={{ height: 4, background: cinnabar, opacity: reveal(p, 0.3) }} />
        <div style={{ opacity: reveal(p, 0.4) }}>
          <Box label="设计文里的全部" sub="有些还没做进原型" w={360} hot />
        </div>
      </div>
    </Stage>
  );
}

function Rooms({ p }: { p: number }) {
  const direct = reveal(p, 0.45);
  return (
    <Stage index={3} kicker="一个比喻" caption="后续消息可以直接送到房间。" note="讲解图，不是官方架构图。本页不另画一张替代图。">
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ opacity: reveal(p, 0) }}>
          <Box label="前台 Router" sub="听需求，决定交给谁" w={640} />
        </div>
        <div style={{ marginLeft: 80, width: 4, height: 40, background: ink, opacity: reveal(p, 0.2) }} />
        <div style={{ opacity: reveal(p, 0.28) }}>
          <Box label="工作室 Worker" sub="一件事，一个房间" w={640} hot />
        </div>
        <div style={{ opacity: direct, border: `2px solid ${cinnabar}`, background: wash, padding: "20px 18px", fontSize: 34 }}>
          同一话题的下一条 → 直达这个房间，不必回前台排队
        </div>
      </div>
    </Stage>
  );
}

function Names({ p }: { p: number }) {
  const left = 20.4 * reveal(p, 0.35, 0.4);
  const right = 12.4 * reveal(p, 0.35, 0.4);
  const names = ["Router", "Worker", "Session", "Trigger", "Watchdog"];
  return (
    <Stage index={4} kicker="不能译的原件" caption="名字保持原文。数字不是本站复测。" note="p50 约 12.4 分钟，对照约 20.4。p95 约 15.7，对照约 29.5。公开转述。">
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {names.map((name, i) => (
          <div key={name} style={{ opacity: reveal(p, i * 0.08), border: `2px solid ${ink}`, padding: "14px 16px", fontSize: 32, background: card }}>
            {name}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 36 }}>
        <Meter label="对照" value={left} max={32} />
        <div style={{ height: 14 }} />
        <Meter label="两层结构" value={right} max={32} hot />
      </div>
    </Stage>
  );
}

function Meter({ label, value, max, hot = false }: { label: string; value: number; max: number; hot?: boolean }) {
  return (
    <div>
      <div style={{ height: 36, background: card, border: `2px solid ${line}` }}>
        <div style={{ width: `${(value / max) * 100}%`, height: "100%", background: hot ? cinnabar : ink }} />
      </div>
      <p style={{ margin: "8px 0 0", fontSize: 28, color: muted }}>{label}</p>
    </div>
  );
}

function Line({ p }: { p: number }) {
  return (
    <Stage index={5} kicker="一句话" caption="人退到决策和验收。" note="连续和并发靠两层结构，主动靠事件。">
      <p style={{ margin: 0, fontFamily: '"Noto Serif SC", serif', fontSize: 86, fontWeight: 650, lineHeight: 1.25, opacity: reveal(p, 0.05, 0.45) }}>
        人不再被会话数量卡住
      </p>
    </Stage>
  );
}

export const deepseekScenes = [Plain, Gap, Rooms, Names, Line];
