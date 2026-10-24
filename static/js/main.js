/* ------------------------------------------------------------------
   Everything that decides an outcome happens on the server.
   The browser only draws the screens and the wheel and sends clicks.

   To add a screen: add templates/screens/<name>.html, add
   static/js/screens/<name>.js (export init and/or render), then list
   it in `screens` below.
------------------------------------------------------------------- */
import { api } from "./api.js";
import { store } from "./store.js";
import { showStage } from "./nav.js";
import * as consent from "./screens/consent.js";
import * as pre from "./screens/pre.js";
import * as game from "./screens/game.js";
import * as post from "./screens/post.js";
import * as reveal from "./screens/reveal.js";

const screens = [consent, pre, game, post, reveal];

// Put a state object from the server on screen (also used after a refresh).
function applyState(data) {
  store.balance = data.balance;
  store.rounds = data.rounds;
  store.currentBet = 0;
  store.chosenColor = null;
  store.gameOver = false;
  store.shownAt = performance.now();
  screens.forEach((screen) => screen.render?.(data));
  showStage(data.stage);
}

async function init() {
  screens.forEach((screen) => screen.init?.());
  document.addEventListener("server-state", (e) => applyState(e.detail));
  const { data } = await api("/api/state");
  applyState(data);
}

init();
