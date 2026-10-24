import { $, fmt } from "../dom.js";
import { api } from "../api.js";
import { store } from "../store.js";
import { publishState, showStage } from "../nav.js";
import { animateWheel, buildWheel } from "../wheel.js";

function showError(message) {
  const box = $("error-msg");
  box.textContent = message;
  box.hidden = !message;
}

function refreshControls() {
  const { balance, currentBet, chosenColor, spinning, gameOver } = store;

  document.querySelectorAll(".chip").forEach((button) => {
    button.disabled = spinning || currentBet + Number(button.dataset.amount) > balance;
  });
  $("all-in").disabled = spinning || currentBet === balance;
  $("clear-bet").disabled = spinning || currentBet === 0;
  $("betting-controls").hidden = gameOver;
  $("gameover").hidden = !gameOver;
  $("spin-btn").disabled = spinning || currentBet === 0 || !chosenColor;
  $("stop-btn").disabled = spinning || store.rounds.length === 0;

  document.querySelectorAll(".color-btn").forEach((button) => {
    button.disabled = spinning;
    button.setAttribute("aria-pressed", String(button.dataset.color === chosenColor));
  });

  $("balance").textContent = fmt(balance);
  $("current-bet").textContent = fmt(currentBet);
}

function fillBanner(round) {
  const el = $("banner");
  if (!round) {
    el.hidden = true;
    return;
  }
  const outcome = round.win
    ? `You won ${fmt(round.payout)}.`
    : `You lost ${fmt(Math.abs(round.payout))}.`;
  el.textContent =
    `The ball landed on ${round.pocket} (${round.result_color}). ` +
    `You bet ${fmt(round.bet_amount)} on ${round.bet_type}. ${outcome}`;
  el.className = `banner ${round.win ? "win" : "loss"}`;
  el.hidden = false;
}

function addHistoryRow(round) {
  const row = document.createElement("tr");
  const cells = [
    round.round_no, round.bet_type, fmt(round.bet_amount),
    `${round.pocket} ${round.result_color}`,
    fmt(round.payout), fmt(round.balance_after),
  ];
  for (const value of cells) {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.appendChild(cell);
  }
  $("history-body").appendChild(row);
}

function renderHistory() {
  $("history-body").replaceChildren();
  store.rounds.forEach(addHistoryRow);
}

async function spin() {
  if (store.spinning || store.currentBet === 0 || !store.chosenColor) return;
  store.spinning = true;               // set first, so a double click does nothing
  showError("");
  const decisionSeconds = (performance.now() - store.shownAt) / 1000;
  $("banner").hidden = true;
  refreshControls();

  const { ok, status, data } = await api("/api/spin", {
    bet: store.currentBet,
    bet_type: store.chosenColor,
    decision_seconds: decisionSeconds,
  }).catch(() => ({ ok: false, status: 0, data: { error: "Could not reach the server." } }));

  if (!ok) {
    store.spinning = false;
    if (status === 409) {              // our screen is out of date: reload it from the server
      const fresh = await api("/api/state");
      publishState(fresh.data);
    }
    showError(data.error || "Something went wrong.");
    refreshControls();
    return;
  }

  await animateWheel(data.round.pocket);

  // update the numbers only after the wheel has stopped
  store.balance = data.balance;
  store.rounds.push(data.round);
  addHistoryRow(data.round);
  store.currentBet = 0;
  store.chosenColor = null;
  store.spinning = false;
  store.gameOver = data.stage !== "game";   // went bust: stay on this screen until Next
  store.shownAt = performance.now();
  fillBanner(data.round);
  refreshControls();
}

async function stopPlaying() {
  const { ok, data } = await api("/api/stop", {});
  if (!ok) return showError(data.error || "Something went wrong.");
  publishState(data);
}

// called once, when the page loads
export function init() {
  buildWheel();

  document.querySelectorAll(".chip").forEach((button) =>
    button.addEventListener("click", () => {
      store.currentBet += Number(button.dataset.amount);
      refreshControls();
    }));
  $("all-in").addEventListener("click", () => {
    store.currentBet = store.balance;
    refreshControls();
  });
  $("clear-bet").addEventListener("click", () => {
    store.currentBet = 0;
    refreshControls();
  });
  document.querySelectorAll(".color-btn").forEach((button) =>
    button.addEventListener("click", () => {
      store.chosenColor = button.dataset.color;
      refreshControls();
    }));

  $("spin-btn").addEventListener("click", spin);
  $("stop-btn").addEventListener("click", stopPlaying);
  $("next-btn").addEventListener("click", () => showStage("post"));

  $("history-toggle").addEventListener("change", (e) => {
    $("history-wrap").hidden = !e.target.checked;
    if (e.target.checked) api("/api/history-view", {});   // count how often it is opened
  });
}

// called every time the server sends a state (page load, stop, refresh, resync)
export function render(data) {
  showError("");
  renderHistory();
  const last = store.rounds[store.rounds.length - 1];
  fillBanner(data.stage === "game" ? last : null);
  refreshControls();
}
