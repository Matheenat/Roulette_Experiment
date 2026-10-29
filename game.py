import random
from enum import Enum
from config import START_BALANCE

# Const
RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

class Color(str, Enum):
    RED = "red"
    BLACK = "black"
    GREEN = "green"

def spin() -> int:
    return random.randint(0, 36)

def color_of(pocket: int) -> Color:
    if not 0 <= pocket <= 36:
        raise ValueError("Pocket must be between 0 and 36")
    if pocket == 0:
        return Color.GREEN
    return Color.RED if pocket in RED_NUMBERS else Color.BLACK

def validate_bet(bet: int, balance: int) -> str | None:
    if bet <= 0:
        return "Bet must be more than 0."
    if bet > balance:
        return "Bet must be within your balance."
    return None

def calculate_payout(bet_type: Color, bet: int, pocket: int) -> int:
    if color_of(pocket) != bet_type:
        return -bet
    if bet_type == Color.GREEN:
        return bet * 35
    return bet

def play_round(bet_type: Color, bet: int, balance: int, pocket: int | None = None) -> dict:
    bet_type = Color(bet_type)
    error = validate_bet(bet, balance)
    if error:
        raise ValueError(error)
    if pocket is None:
        pocket = spin()

    payout = calculate_payout(bet_type, bet, pocket)

    return {
        "balance_before" : balance,
        "bet_amount" : bet,
        "bet_type" : bet_type.value,
        "pocket" : pocket,
        "result_color" : color_of(pocket).value,
        "win": 1 if payout > 0 else 0,
        "payout" : payout,
        "balance_after" : balance + payout,
    }

if __name__ == "__main__":
    print(play_round(Color.GREEN, 10, 1000, pocket=0)["payout"])