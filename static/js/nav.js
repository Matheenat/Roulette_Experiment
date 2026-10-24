// Moving between screens. Screens never import each other or main.js;
// they call these two functions instead.

export function showStage(stage) {
  document.querySelectorAll("section[data-stage]").forEach((section) => {
    section.hidden = section.dataset.stage !== stage;
  });
  window.scrollTo(0, 0);
}

// "The server sent a new state": main.js listens and redraws every screen.
export function publishState(data) {
  document.dispatchEvent(new CustomEvent("server-state", { detail: data }));
}
