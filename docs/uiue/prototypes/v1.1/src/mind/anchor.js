/* 从别的页带锚点进来（/mind#<里程碑>、/mind/learn#<步骤>），或页内换了锚点：那一条原地展开并标出，滚到它（联审 C-08）。Mind 和 Learn 两块画板共用这一份 */
function revealHashTarget() {
  const id = decodeURIComponent((location.hash || '').slice(1));
  const t = id && document.getElementById(id);
  if (t && t.matches('.vc-ms, .vc-step')) { const d = t.querySelector('details'); if (d) d.open = true; t.classList.add('is-target'); t.scrollIntoView({ block: 'start' }); }
}
