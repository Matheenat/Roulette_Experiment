from base import Bot

class LossChaser(Bot):
    strat = "loss_chaser"

    def __init__(self, seed=None, base_bet=...):
        super().__init__(seed, base_bet, multiplier=2.0)

    def bet(self, history: dict, balance: int, rng=0) -> int:
        lose_last_round = bool(history) and not history[-1]["win"]
        if lose_last_round:
            amount = self.base_bet * self.multiplier
        else:
            amount = self.BET_UNIT

        return self.to_valid_bet(amount, balance)