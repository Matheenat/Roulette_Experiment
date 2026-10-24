import { $ } from "../dom.js";
import { api } from "../api.js";
import { publishState } from "../nav.js";

async function finishGame() {
  const choice = document.querySelector('input[name="odds_after"]:checked');
  const { ok, data } = await api("/api/finish", { odds_after: choice.value });
  if (!ok) return alert(data.error || "Something went wrong.");
  publishState(data);
}

export function init() {
  document.querySelectorAll('input[name="odds_after"]').forEach((input) =>
    input.addEventListener("change", () => { $("finish-btn").disabled = false; }));
  $("finish-btn").addEventListener("click", finishGame);
}
