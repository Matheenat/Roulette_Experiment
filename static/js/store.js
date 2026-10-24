// Shared state that more than one screen needs.
export const store = {
  balance: 0,
  rounds: [],
  currentBet: 0,
  chosenColor: null,
  spinning: false,
  gameOver: false,               // true after going bust, until the player clicks Next
  shownAt: performance.now(),    // when the player last saw a result
};
