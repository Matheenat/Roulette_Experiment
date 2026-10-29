import random

from config import BET_CHIPS, START_BALANCE
from game import play_round

BET_UNIT = min(BET_CHIPS)

class Bot:
    name = "placeholder"
    def __init__(self, seed=None, max_rounds = 100):
        self.seed = seed if seed is not None else random.randrange(2**32)
        self.rng = random.Random(self.seed)
        self.max_rounds = max_rounds

    def params(self) -> dict[str, int]:
        return {"max_rounds" : self.max_rounds}

    def next_bet(self, history, current_balance):
        raise NotImplementedError("Missing next_bot impl (bot Class)")

    def decision_seconds(self, history) -> float:
        return self.rng.lognormvariate(1.0, 0.5)

    @staticmethod
    def to_valid_bet(amount, balance):
        amount = max(BET_UNIT, round(amount / BET_UNIT) * 10)
        return min(amount, balance)

    def play_session(self): 
        session_id = f"{self.name}-{self.seed}"
        balance = START_BALANCE
        rounds = []
        ended_by = "max_rounds"

        while len(rounds) < self.max_rounds:
            choice = self.next_bet(rounds, balance)
            if choice is None:
                ended_by = "stopped"
                break
            bet_type, bet = choice

            result = play_round(bet_type, bet, balance, pocket=self.rng.randint(0, 36))
            result["session_id"] = session_id
            result["round_no"] = len(rounds) + 1
            result["decision_seconds"] = round(self.decision_seconds(rounds), 2)
            rounds.append(result)
            balance = result["balance_after"]

            if balance == 0:
                ended_by = "bust"
                break

        session = {
            "session_id": session_id,
            "strategy": self.name,
            "seed": self.seed,
            "start_balance": START_BALANCE,
            "rounds": len(rounds),
            "final_balance": balance,
            "ended_by": ended_by,
        }
        return session, rounds