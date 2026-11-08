from base import Bot

class Paroli(Bot):
    strat = "reverse_martingale"

    def __init__(self, seed=None, base_bet=...):
        super().__init__(seed, base_bet, multiplier=2.0)

    def bet(self, history: dict, balance: int, rng=0) -> int:
        win_last_round = bool(history) and history[-1]["win"]
        if win_last_round:
            amount = self.base_bet * self.multiplier
        else:
            amount = self.BET_UNIT

        return self.to_valid_bet(amount, balance)