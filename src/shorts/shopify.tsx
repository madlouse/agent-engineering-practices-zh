import { Box, cinnabar, card, clamp01, faint, ink, line, muted, paper, reveal, Stage, wash } from "@/shorts/kit";

function Plain({ p }: { p: number }) {
  const cards = [
    { label: "可能的漏洞", keep: false },
    { label: "理论风险", keep: false },
    { label: "说得通的猜测", keep: false },
    { label: "能跑通的测试", keep: true },
  ];
  return (
    <Stage index={1} kicker="用大白话" caption="证明不了，就不算发现。" note="模型可以列出很多。留下的只有能证明被利用的那一条。">
      <div style={{ /* lint-tokens-ignore */ display: "flex", flexDirection: "column", gap: 18 }}>
        <Box label="模型" sub="只负责提出候选" live={reveal(p, 0)} hot />
        {cards.map((item, i) => {
          const live = reveal(p, 0.12 + i * 0.12);
          const drop = item.keep ? 0 : reveal(p, 0.62);
          return (
            <div key={item.label} style={{ /* lint-tokens-ignore */ display: "flex", alignItems: "center", gap: 22, opacity: live, minWidth: 0 }}>
              <div style={{ /* lint-tokens-ignore */ width: 18, height: 18, flex: "none", background: item.keep ? cinnabar : faint, transform: `scale(${0.4 + live * 0.6})` }} />
              <div style={{ /* lint-tokens-ignore */ minWidth: 0, flex: 1, transform: `translateY(${drop * 28}px)`, opacity: 1 - drop * 0.55 }}>
                <Box label={item.label} sub={item.keep ? "这一条才算发现" : "没有证明，丢掉"} w={640} hot={item.keep && drop === 0} />
              </div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
}

function Noise({ p }: { p: number }) {
  const candidate = 86 * reveal(p, 0.05, 0.45);
  const kept = 16 * reveal(p, 0.2, 0.45);
  const marks = ["降级", "误报", "纵深防御"];
  return (
    <Stage index={2} kicker="容易听错" caption="更强，不等于更少噪声。" note="约五个月的评估。三十多个候选，验证后没有留下一条可利用的发现。">
      <div style={{ /* lint-tokens-ignore */ display: "flex", alignItems: "flex-end", gap: 48, height: 640 }}>
        <Bar label="候选" h={candidate} hot={false} />
        <Bar label="被证明" h={kept} hot />
      </div>
      <div style={{ /* lint-tokens-ignore */ display: "flex", gap: 16, marginTop: 28 }}>
        {marks.map((mark, i) => (
          <div
            key={mark}
            style={{
              flex: 1,
              border: `2px solid ${line}`,
              background: card,
              padding: "16px 12px", // lint-tokens-ignore
              textAlign: "center",
              fontSize: 32, // lint-tokens-ignore
              opacity: reveal(p, 0.55 + i * 0.08),
            }}
          >
            {mark}
          </div>
        ))}
      </div>
    </Stage>
  );
}

function Bar({ label, h, hot }: { label: string; h: number; hot: boolean }) {
  return (
    <div style={{ /* lint-tokens-ignore */ display: "flex", flex: 1, flexDirection: "column", justifyContent: "flex-end", height: "100%" }}>
      <div style={{ /* lint-tokens-ignore */ height: `${h}%`, background: hot ? cinnabar : ink, minHeight: h > 0 ? 8 : 0 }} />
      <p style={{ /* lint-tokens-ignore */ margin: "16px 0 0", fontSize: 32, color: muted }}>{label}</p>
    </div>
  );
}

function Sieve({ p }: { p: number }) {
  const out = reveal(p, 0.15, 0.3);
  const inn = reveal(p, 0.48, 0.3);
  return (
    <Stage index={3} kicker="一个比喻" caption="模型会换。框留着。" note="讲解图，不是原文那三张手绘图。">
      <svg viewBox="0 0 760 760" style={{ /* lint-tokens-ignore */ width: "100%", height: 760 }}>
        <rect x="80" y="70" width="600" height="620" fill="none" stroke={cinnabar} strokeWidth="18" />
        <text x="100" y="54" fill={cinnabar} fontSize="32">
          Harness · 框
        </text>
        <g opacity={1 - out} transform={`translate(0 ${-out * 220})`}>
          <Mesh y={150} label="这一周的模型" />
        </g>
        <g opacity={inn} transform={`translate(0 ${(1 - inn) * 180})`}>
          <Mesh y={360} label="换上的模型" />
        </g>
      </svg>
    </Stage>
  );
}

function Mesh({ y, label }: { y: number; label: string }) {
  const lines = [0, 1, 2, 3, 4, 5];
  return (
    <g>
      {lines.map((i) => (
        <line key={i} x1="120" x2="640" y1={y + i * 28} y2={y + i * 28} stroke={ink} strokeWidth="3" />
      ))}
      <text x="140" y={y + 188} fill={ink} fontSize="34">
        {label}
      </text>
    </g>
  );
}

function Originals({ p }: { p: number }) {
  const rows = [
    { en: "DISPATCH", zh: "编排：语言、沙箱、代理" },
    { en: "PARALLEL → SEQUENTIAL", zh: "搜寻并行，验证串行" },
    { en: "shared scope / partition", zh: "整份范围，再切开" },
  ];
  return (
    <Stage index={4} kicker="不能译的原件" caption="图里的英文留在图里。" note="头图和三张手绘图在正文。这里只帮你记住每张图在说什么。">
      <div style={{ /* lint-tokens-ignore */ display: "flex", flexDirection: "column", gap: 22 }}>
        {rows.map((row, i) => {
          const live = reveal(p, i * 0.18);
          return (
            <div key={row.en} style={{ /* lint-tokens-ignore */ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 18, opacity: live }}>
              <div style={{ /* lint-tokens-ignore */ border: `2px solid ${ink}`, background: paper, padding: "28px 22px", fontSize: 34, fontWeight: 650 }}>{row.en}</div>
              <div style={{ /* lint-tokens-ignore */ border: `2px solid ${line}`, background: wash, padding: "28px 22px", fontSize: 32, lineHeight: 1.35 }}>{row.zh}</div>
            </div>
          );
        })}
      </div>
    </Stage>
  );
}

function Line({ p }: { p: number }) {
  const a = reveal(p, 0.05, 0.35);
  const b = reveal(p, 0.4, 0.35);
  return (
    <Stage index={5} kicker="一句话" caption="六周的账是原文的内部估算。" note="不是公开赏金记录，也不是本站复测。">
      <p style={{ /* lint-tokens-ignore */ margin: 0, fontFamily: '"Noto Serif SC", serif', fontSize: 92, fontWeight: 650, lineHeight: 1.2, opacity: a }}>
        留下的是证明
      </p>
      <p style={{ /* lint-tokens-ignore */ margin: "28px 0 0", fontFamily: '"Noto Serif SC", serif', fontSize: 92, fontWeight: 650, lineHeight: 1.2, color: cinnabar, opacity: b }}>
        不是当周的模型
      </p>
      <div style={{ /* lint-tokens-ignore */ marginTop: 48, height: 4, width: `${clamp01(p) * 100}%`, background: cinnabar }} />
    </Stage>
  );
}

export const shopifyScenes = [Plain, Noise, Sieve, Originals, Line];
