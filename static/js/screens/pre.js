import { $ } from "../dom.js";
import { api } from "../api.js";
import { publishState } from "../nav.js";

async function startGame() {
  const choice = document.querySelector('input[name="odds_before"]:checked');
  const { ok, data } = await api("/api/start", {
    consent: true,
    odds_before: choice.value,
  });
  if (!ok) return alert(data.error || "Something went wrong.");
  publishState(data);
}

export function init() {
  document.querySelectorAll('input[name="odds_before"]').forEach((input) =>
    input.addEventListener("change", () => { $("start-btn").disabled = false; }));
  $("start-btn").addEventListener("click", startGame);
}
