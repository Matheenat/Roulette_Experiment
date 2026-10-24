import pytest
import random
from config import START_BALANCE

from game import (
    Color,
    RED_NUMBERS,
    spin,
    color_of,
    validate_bet,
    calculate_payout,
    play_round,
    )

def test_is_zero_green():
    assert color_of(0) == Color.GREEN

def test_is_red():
    assert color_of(1) == Color.RED
    assert color_of(3) == Color.RED
    assert color_of(19) == Color.RED
    assert color_of(21) == Color.RED

def test_is_black():
    assert color_of(2) == Color.BLACK
    assert color_of(35) == Color.BLACK

def test_valid_pocket():
    with pytest.raises(ValueError):
        color_of(37)
    with pytest.raises(ValueError):
        color_of(-1)

def color_count():
    colors = [color_of(p) for p in range(37)]
    assert colors.count(Color.RED) == 18
    assert colors.count(Color.BLACK) == 18
    assert colors.count(Color.GREEN) == 1

def test_red_numbers_set_is_valid():
    assert len(RED_NUMBERS) == 18
    assert 0 not in RED_NUMBERS
    assert all(1 <= n <= 36 for n in RED_NUMBERS)

def test_pocket_boundaries_are_valid():
    assert color_of(0) == Color.GREEN
    assert color_of(36) == Color.RED

def test_win_payouts():
    assert calculate_payout(Color.RED, 20, 3) == 20
    assert calculate_payout(Color.BLACK, 20, 2) == 20
    assert calculate_payout(Color.GREEN, 10, 0) == 350

def test_loss_costs_exactly_the_bet():
    assert calculate_payout(Color.RED, 20, 2) == -20
    assert calculate_payout(Color.GREEN, 10, 5) == -10

def test_zero_loses_red_and_black_bets():
    assert calculate_payout(Color.RED, 20, 0) == -20
    assert calculate_payout(Color.BLACK, 20, 0) == -20

def test_payout_is_always_loss_or_a_valid_win():
    for pocket in range(37):
        for bet_type in Color:
            for bet in (1, 10, 500):
                payout = calculate_payout(bet_type, bet, pocket)
                win_amount = 35 * bet if bet_type == Color.GREEN else bet
                assert payout in (-bet, win_amount)
                assert payout >= -bet  

@pytest.mark.parametrize("bet_type", list(Color))
def test_house_edge_is_minus_one_unit_per_37_spins(bet_type):
    total = sum(calculate_payout(bet_type, 1, p) for p in range(37))
    assert total == -1

def test_balance_after_equals_before_plus_payout():
    for pocket in range(37):
        r = play_round(Color.RED, 10, 1000, pocket=pocket)
        assert r["balance_after"] == r["balance_before"] + r["payout"]

def test_win_flag_matches_payout():
    for pocket in range(37):
        r = play_round(Color.BLACK, 10, 1000, pocket=pocket)
        assert r["win"] == (1 if r["payout"] > 0 else 0)

def test_all_in_loss_ends_at_zero_not_negative():
    r = play_round(Color.RED, 1000, 1000, pocket=2)
    assert r["balance_after"] == 0

def test_balance_never_negative_over_many_random_rounds():
    balance = START_BALANCE
    for _ in range(5000):
        if balance == 0:
            break
        bet = random.randint(1, balance)
        r = play_round(random.choice(list(Color)), bet, balance)
        assert r["balance_after"] >= 0
        balance = r["balance_after"]

def test_invalid_bets_are_rejected():
    assert validate_bet(0, 1000) is not None
    assert validate_bet(-5, 1000) is not None
    assert validate_bet(1001, 1000) is not None

def test_valid_bets_are_accepted():
    assert validate_bet(1, 1000) is None
    assert validate_bet(1000, 1000) is None

def test_play_round_rejects_bad_inputs():
    with pytest.raises(ValueError):
        play_round(Color.RED, 2000, 1000, pocket=3)   
    with pytest.raises(ValueError):
        play_round("Red", 10, 1000, pocket=3)       
    with pytest.raises(ValueError):
        play_round(Color.RED, 10, 1000, pocket=40)    

def test_play_round_accepts_plain_string_color():
    assert play_round("black", 10, 1000, pocket=2)["win"] == 1

def test_spin_stays_in_range():
    assert all(0 <= spin() <= 36 for _ in range(5000))