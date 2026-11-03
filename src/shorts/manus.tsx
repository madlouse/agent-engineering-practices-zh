import { Box, cinnabar, card, ink, line, muted, reveal, Stage, wash } from "@/shorts/kit";

function Plain({ p }: { p: number }) {
  const oldWay = 1 - reveal(p, 0.35, 0.25);
  const live = reveal(p, 0.4);
  return (
    <Stage index={1} kicker="用大白话" caption="人已经默认和 agent 并肩干活。" note="一个人同时推进十到二十个请求，在原文里已经是常态。">
      <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
        <div style={{ opacity: oldWay, textDecoration: oldWay < 0.4 ? "line-through" : "none" }}>
          <Box label="旧办法" sub="先读消息，再自己写代码" w={760} />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 18, opacity: live }}>
          <Box label="原话" sub="贴进会话" w={220} hot />
          <Arrow live={reveal(p, 0.55)} />
          <Box label="agent" sub="找代码，提出修改" w={280} />
          <Arrow live={reveal(p, 0.7)} />
          <Box label="人" sub="指挥、检查、负责" w={240} hot />
        </div>
      </div>
    </Stage>
  );
}

function Arrow({ live }: { live: number }) {
  return <div style={{ width: 72 * live, height: 4, background: cinnabar }} />;
}

function Wrong({ p }: { p: number }) {
  const pile = Math.round(reveal(p, 0.05, 0.4) * 8);
  const monday = reveal(p, 0.55);
  return (
    <Stage index={2} kicker="容易听错" caption="没有终点，循环只会堆决策。" note="那个周末，agent 为每条反馈开了项目。周一，两百多个项目等着人决定。">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28 }}>
        <div>
          <p style={{ margin: "0 0 12px", fontSize: 30, color: muted }}>周末 · 自主</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {Array.from({ length: pile }, (_, i) => (
              <div key={i} style={{ width: 72, height: 48, border: `2px solid ${line}`, background: card }} />
            ))}
          </div>
        </div>
        <div style={{ opacity: monday }}>
          <p style={{ margin: "0 0 12px", fontSize: 30, color: muted }}>周一 · 人</p>
          <Box label="有测试" sub="bug 可以自己跑完" w={340} hot />
          <div style={{ height: 16 }} />
          <Box label="没测试" sub="产品决定停在人这里" w={340} />
        </div>
      </div>
    </Stage>
  );
}

function Mono({ p }: { p: number }) {
  const books = reveal(p, 0);
  const page = reveal(p, 0.35);
  const stamp = reveal(p, 0.62);
  return (
    <Stage index={3} kicker="一个比喻" caption="Mono 是手册，不是合并仓库。" note="讲解图。agent 按需取一页。合并仍要人点头。">
      <div style={{ display: "flex", gap: 18, opacity: books }}>
        {["仓库 A", "仓库 B", "仓库 C"].map((name) => (
          <Box key={name} label={name} sub="仍然分开" w={220} />
        ))}
      </div>
      <div style={{ marginTop: 36, display: "flex", alignItems: "center", gap: 24 }}>
        <div style={{ opacity: page }}>
          <Box label="手册里的一页" sub="做什么，为何如此" w={420} hot />
        </div>
        <div style={{ opacity: stamp, border: `3px solid ${cinnabar}`, color: cinnabar, padding: "22px 18px", fontSize: 32, fontWeight: 650 }}>
          合并
          <div style={{ fontSize: 26, fontWeight: 450, marginTop: 6 }}>在人手里</div>
        </div>
      </div>
    </Stage>
  );
}

function Originals({ p }: { p: number }) {
  const rows = [
    { t: "Mono 如何运作，以及它如何演进", d: "同事用 Manus 做的视频" },
    { t: "语音输入的产品需求", d: "另一段原视频" },
    { t: "工程师、产品、设计，同一个会话", d: "示意图。作者写明不是真实调价" },
  ];
  return (
    <Stage index={4} kicker="不能译的原件" caption="两段视频，一张图，画面不另译。" note="这些原件嵌在正文里。">
      <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        {rows.map((row, i) => (
          <div key={row.t} style={{ opacity: reveal(p, i * 0.18), border: `2px solid ${ink}`, background: wash, padding: "26px 22px" }}>
            <p style={{ margin: 0, fontSize: 36, fontWeight: 650 }}>{row.t}</p>
            <p style={{ margin: "8px 0 0", fontSize: 28, color: muted }}>{row.d}</p>
          </div>
        ))}
      </div>
    </Stage>
  );
}

function Line({ p }: { p: number }) {
  return (
    <Stage index={5} kicker="一句话" caption="人更集中在判断和责任上。" note="这也是他们仍在招聘的原因。">
      <p style={{ margin: 0, fontFamily: '"Noto Serif SC", serif', fontSize: 88, fontWeight: 650, lineHeight: 1.25, opacity: reveal(p, 0.05, 0.4) }}>
        工程变快之后
      </p>
      <p style={{ margin: "24px 0 0", fontFamily: '"Noto Serif SC", serif', fontSize: 88, fontWeight: 650, lineHeight: 1.25, color: cinnabar, opacity: reveal(p, 0.4, 0.4) }}>
        决定做什么，成了瓶颈
      </p>
    </Stage>
  );
}

export const manusScenes = [Plain, Wrong, Mono, Originals, Line];
