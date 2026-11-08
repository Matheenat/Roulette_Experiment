import random
from config import BET_CHIPS
from abc import ABC, abstractmethod
from game import Color

class Bot(ABC):
    strat = None
    BET_UNIT = min(BET_CHIPS)

    def __init__(self, seed=None, base_bet=BET_UNIT, multiplier=1.0) -> None:
        self.seed = seed if seed is not None else random.randrange(2**32)
        self.base_bet = base_bet
        self.multiplier = multiplier

    def params(self):
        return {"base_bet": self.base_bet,
                "seed": self.seed,
                }

    @abstractmethod
    def bet(self, history: dict, balance: int, rng: float | int = 0):
        pass

    @staticmethod
    def to_valid_bet(amount: int, balance: int) -> int:
        amount = max(Bot.BET_UNIT, round(amount / Bot.BET_UNIT) *  Bot.BET_UNIT)
        return min(amount, balance)

    '''
    Flat TODO
    Martingale 
    Reverse Martingale (Paroli) TODO
    Fibonacci TODO
    D'Alembert TODO
    Labouchere TODO
    Oscar's Grind TODO
    Random TODO
    '''