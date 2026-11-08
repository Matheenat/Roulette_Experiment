from base import Bot
from game import Color
from config import BET_CHIPS

class LossChaser(Bot):
    name = "loss_chaser"
    def __init__(self, base_bet=min(BET_CHIPS), chase_prob=1.0, multiplier=2.0,
                 seed=None, max_rounds=100):
        super().__init__(seed, max_rounds)
        self.base_bet = base_bet
        self.multiplier = multiplier
        self.chase_prob = chase_prob

    def params(self):
        return {**super().params(),
                 "base_bet": self.base_bet, 
                 "multiplier": self.multiplier,
                 "chase_prob": self.chase_prob,
                 }

    def next_bet(self, history, balance):
        bet_type = self.rng.choice([Color.RED, Color.BLACK])
        
        lost_last_round = bool(history) and not history[-1]["win"] 
        if lost_last_round and self.rng.random() < self.chase_prob:
            amount = history[-1]["bet_amount"] * self.multiplier
        else:
            amount = self.base_bet
            
        return bet_type, self.to_valid_bet(amount, balance)

    def decision_seconds(self, history):
        if history and not history[-1]["win"]:
            return self.rng.lognormvariate(0.2, 0.4)
        return self.rng.lognormvariate(1.1, 0.4)