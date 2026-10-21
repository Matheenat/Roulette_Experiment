import random
from enum import Enum

START_BALANCE = 1000
BET_TYPES =  ("red", "black", "green")

# European based wheel so only 1 green pocket being green
RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

class Color(str, Enum):
    RED = "red"
    BLACK = "black"
    GREEN = "green"

def spin() -> int:
    return random.randint(0, 36)

def map_color(pocket) -> None:
    if pocket == 0:
        return Color.GREEN
    return Color.RED if pocket in RED_NUMBERS else Color.BLACK

def validate_bet(bet, balance) -> str:
    if bet <= 0:
        return "Bet must be more than 0."
    if bet > balance:
        return "Bet must be within your balance."
    return None

def calculate_payout(bet,)