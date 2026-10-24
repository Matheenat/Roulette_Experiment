import { $ } from "../dom.js";
import { showStage } from "../nav.js";

export function init() {
  $("consent-check").addEventListener("change", (e) => {
    $("consent-next").disabled = !e.target.checked;
  });
  $("consent-next").addEventListener("click", () => showStage("pre"));
}
