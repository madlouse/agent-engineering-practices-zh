import { cinnabar, card, ink, line, muted, reveal, Stage, wash } from "@/shorts/kit";

function Plain({ p }: { p: number }) {
  return (
    <Stage index={1} kicker="用大白话" caption="先成为会过那种生活的人。" note="协议大约要一整天。问题自己答，不要交给 AI。">
      <div style={{ /* lint-tokens-ignore */ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        <Path title="多数人" steps={["先改行动", "指望变成另一种人", "旧生活把它拉回来"]} live={reveal(p, 0)} strike />
        <Path title="他反过来" steps={["先过那种生活", "行动是那个人的动作", "结果从这里来"]} live={reveal(p, 0.35)} />
      </div>
    </Stage>
  );
}

function Path({ title, steps, live, strike = false }: { title: string; steps: string[]; live: number; strike?: boolean }) {
  return (
    <div style={{ /* lint-tokens-ignore */ opacity: live, border: `2px solid ${strike ? line : cinnabar}`, background: strike ? card : wash, padding: 22 }}>
      <p style={{ /* lint-tokens-ignore */ margin: 0, fontSize: 30, color: strike ? muted : cinnabar }}>{title}</p>
      {steps.map((step, i) => (
        <p key={step} style={{ /* lint-tokens-ignore */ margin: "16px 0 0", fontSize: 32, lineHeight: 1.35, textDecoration: strike ? "line-through" : "none", opacity: reveal(live, i * 0.2) }}>
          {step}
        </p>
      ))}
    </div>
  );
}

function Lens({ p }: { p: number }) {
  return (
    <Stage index={2} kicker="容易听错" caption="目标是透镜，不是终点线。" note="没到该转折的那一章，协议不会魔法生效。">
      <div style={{ /* lint-tokens-ignore */ display: "flex", flexDirection: "column", gap: 28 }}>
        <div style={{ /* lint-tokens-ignore */ opacity: reveal(p, 0), fontSize: 36, color: muted, textDecoration: "line-through" }}>写下一组目标，人就会换掉</div>
        <svg viewBox="0 0 760 280" style={{ /* lint-tokens-ignore */ width: "100%", height: 280, opacity: reveal(p, 0.25) }}>
          <ellipse cx="250" cy="140" rx={90 + reveal(p, 0.3) * 20} ry="110" fill="none" stroke={cinnabar} strokeWidth="8" />
          <text x="190" y="148" fontSize="32" fill={ink}>
            透镜
          </text>
          <line x1="430" y1="140" x2={430 + reveal(p, 0.45) * 220} y2="140" stroke={ink} strokeWidth="4" />
          <polygon points="650,140 620,124 620,156" fill={ink} opacity={reveal(p, 0.7)} />
          <text x="500" y="110" fontSize="32" fill={muted}>
            不是终点
          </text>
        </svg>
      </div>
    </Stage>
  );
}

function Rings({ p }: { p: number }) {
  const labels = ["约束 · 规则", "每天 · 杠杆", "一个月 · 头目战", "一年 · 当前任务", "愿景 · 怎样算赢", "反愿景 · 输了会怎样"];
  return (
    <Stage index={3} kicker="一个比喻" caption="六层，收成一局游戏。" note="讲解图。规则不是来扫兴的，是让创造发生。">
      <div style={{ /* lint-tokens-ignore */ display: "flex", flexDirection: "column", gap: 12 }}>
        {labels.map((label, i) => {
          const live = reveal(p, i * 0.1);
          const inset = (5 - i) * 28;
          return (
            <div key={label} style={{ /* lint-tokens-ignore */ marginLeft: inset, marginRight: inset, opacity: live, border: `2px solid ${i === 0 ? cinnabar : ink}`, background: i === 0 ? wash : card, padding: "12px 16px", fontSize: 32 }}>
              {label}
            </div>
          );
        })}
      </div>
    </Stage>
  );
}

function Originals({ p }: { p: number }) {
  return (
    <Stage index={4} kicker="不能译的原件" caption="帖子没有配图。句子不改写。" note="订阅信的招募段没有收进正文。">
      <p style={{ /* lint-tokens-ignore */ margin: 0, fontFamily: '"Source Serif 4", serif', fontSize: 72, lineHeight: 1.2, opacity: reveal(p, 0) }}>
        Trust only movement.
      </p>
      <p style={{ /* lint-tokens-ignore */ margin: "18px 0 0", fontSize: 32, color: muted, opacity: reveal(p, 0.25) }}>— Alfred Adler</p>
      <p style={{ /* lint-tokens-ignore */ margin: "48px 0 0", fontSize: 34, lineHeight: 1.45, opacity: reveal(p, 0.45) }}>
        Impulsive · Self-Protective · Conformist · … · Unitive
      </p>
    </Stage>
  );
}

function Line({ p }: { p: number }) {
  return (
    <Stage index={5} kicker="一句话" caption="你玩得越久，这股约束越像你自己。">
      <p style={{ /* lint-tokens-ignore */ margin: 0, fontFamily: '"Noto Serif SC", serif', fontSize: 80, fontWeight: 650, lineHeight: 1.28, opacity: reveal(p, 0.05, 0.4) }}>
        先看清你在保护的生活
      </p>
      <p style={{ /* lint-tokens-ignore */ margin: "20px 0 0", fontFamily: '"Noto Serif SC", serif', fontSize: 80, fontWeight: 650, lineHeight: 1.28, color: cinnabar, opacity: reveal(p, 0.4, 0.35) }}>
        再给一个小的愿景
      </p>
    </Stage>
  );
}

export const danScenes = [Plain, Lens, Rings, Originals, Line];
