import { Box, cinnabar, card, ink, line, muted, reveal, Stage, wash } from "@/shorts/kit";

function Plain({ p }: { p: number }) {
  const fill = reveal(p, 0.05, 0.4);
  return (
    <Stage index={1} kicker="用大白话" caption="阅读交给机器，判断留在人这里。" note="原文：大约百分之九十的代码由 Claude 写。审查没有取消。">
      <p style={{ margin: "0 0 12px", fontSize: 30, color: muted }}>一份变更里，谁写的</p>
      <div style={{ display: "flex", height: 72, border: `2px solid ${ink}`, overflow: "hidden" }}>
        <div style={{ width: `${fill * 90}%`, background: ink }} />
        <div style={{ flex: 1, background: wash }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10, fontSize: 28, color: muted }}>
        <span>Claude 写 · 约 90%</span>
        <span>其余</span>
      </div>
      <div style={{ display: "flex", gap: 20, marginTop: 36 }}>
        <div style={{ opacity: reveal(p, 0.45) }}>
          <Box label="阅读" sub="大部分交给机器" w={360} />
        </div>
        <div style={{ opacity: reveal(p, 0.62) }}>
          <Box label="判断" sub="可能出什么错，哪一层抓" w={420} hot />
        </div>
      </div>
    </Stage>
  );
}

function Own({ p }: { p: number }) {
  return (
    <Stage index={2} kicker="容易听错" caption="你落地它，你就拥有它。" note="Agent 的批准不算人工批准。高风险仍然要人。">
      <p style={{ margin: 0, fontFamily: '"Source Serif 4", serif', fontSize: 64, lineHeight: 1.25, opacity: reveal(p, 0) }}>
        You land it, you own it.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginTop: 40 }}>
        <div style={{ opacity: reveal(p, 0.3), border: `2px solid ${line}`, background: card, padding: 24 }}>
          <p style={{ margin: 0, fontSize: 34, color: muted, textDecoration: "line-through" }}>机器审过 = 你审过</p>
        </div>
        <div style={{ opacity: reveal(p, 0.5), border: `2px solid ${cinnabar}`, background: wash, padding: 24 }}>
          <p style={{ margin: 0, fontSize: 34 }}>低风险可自动合并</p>
          <p style={{ margin: "10px 0 0", fontSize: 28, color: muted }}>高风险仍要人</p>
        </div>
      </div>
    </Stage>
  );
}

function Sieves({ p }: { p: number }) {
  const layers = ["提交前的验证", "安全审查", "其他检查", "回滚"];
  return (
    <Stage index={3} kicker="一个比喻" caption="一层一层的筛子，不是一道门。" note="讲解图。每一层都会漏，所以底下还有恢复。">
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {layers.map((layer, i) => {
          const live = reveal(p, i * 0.12);
          const last = i === layers.length - 1;
          return (
            <div key={layer} style={{ display: "flex", alignItems: "center", gap: 16, opacity: live }}>
              <div style={{ width: 22, height: 64, background: last ? cinnabar : ink }} />
              <div style={{ flex: 1, border: `2px solid ${last ? cinnabar : line}`, background: last ? wash : card, padding: "16px 18px", fontSize: 34 }}>
                {layer}
              </div>
              <div style={{ width: 18, height: 18, borderRadius: 99, background: ink, transform: `translateY(${live * i * 6}px)` }} />
            </div>
          );
        })}
      </div>
    </Stage>
  );
}

function Originals({ p }: { p: number }) {
  const figs = [
    ["图 A", "变更从作者机器到用户"],
    ["图 B", "六层检查，底下是回滚"],
    ["图 C", "用事故和回退做每日评估"],
    ["图 D", "改动前后的审查轮次"],
  ];
  return (
    <Stage index={4} kicker="不能译的原件" caption="四张示意图，英文留在图里。" note="学习那张图问的是：机器读了大部分代码，人怎么学会它。原图在正文。">
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {figs.map(([id, text], i) => (
          <div key={id} style={{ opacity: reveal(p, i * 0.12), border: `2px solid ${ink}`, padding: "22px 18px", background: wash }}>
            <p style={{ margin: 0, fontSize: 30, color: cinnabar }}>{id}</p>
            <p style={{ margin: "8px 0 0", fontSize: 32, lineHeight: 1.35 }}>{text}</p>
          </div>
        ))}
      </div>
    </Stage>
  );
}

function Line({ p }: { p: number }) {
  const grow = reveal(p, 0.15, 0.5);
  return (
    <Stage index={5} kicker="一句话" caption="回滚率不该跟着变多。" note="原文还写：合并的 pull request 增加一倍以上，需要回滚的比例下降超过百分之四十。这是原文的数。">
      <p style={{ margin: 0, fontFamily: '"Noto Serif SC", serif', fontSize: 84, fontWeight: 650, lineHeight: 1.25, opacity: reveal(p, 0) }}>
        写得更快
      </p>
      <div style={{ marginTop: 36, height: 28, border: `2px solid ${ink}` }}>
        <div style={{ width: `${grow * 100}%`, height: "100%", background: cinnabar }} />
      </div>
      <p style={{ margin: "14px 0 0", fontSize: 30, color: muted }}>速度可以上去。回滚不该一起上去。</p>
    </Stage>
  );
}

export const claudeScenes = [Plain, Own, Sieves, Originals, Line];
