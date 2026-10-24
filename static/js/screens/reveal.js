import { $, fmt } from "../dom.js";

export function render(data) {
  if (data.stage !== "reveal" || !data.summary) return;
  const s = data.summary;
  $("r-before").textContent = s.odds_before;
  $("r-after").textContent = s.odds_after;
  $("r-correct").textContent = s.correct_option;
  $("r-rounds").textContent = fmt(s.rounds);
  const rate = s.rounds ? Math.round((s.wins / s.rounds) * 100) : 0;
  $("r-wins").textContent = `${fmt(s.wins)} (${rate}%)`;
  $("r-wagered").textContent = fmt(s.wagered);
  $("r-balance").textContent = fmt(s.final_balance);
  $("r-net").textContent = s.net.toLocaleString("en-US", { signDisplay: "always" });
  $("r-expected").textContent = fmt(s.expected_loss);
}
