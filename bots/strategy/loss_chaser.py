from base import Bot

class LossChaser(Bot):
    strat = "loss_chaser"

    def __init__(self, seed=None, base_bet=...):
        super().__init__(seed, base_bet)

    def bet(self, history: dict, balance: int, rng=0) -> int:
        amount = self.base_bet * 2
        return self.to_valid_bet(amount, balance)