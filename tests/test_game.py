import pytest

from game import (Color, RED_NUMBERS, spin, color_of, validate_bet, calculate_payout, play_round)

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
    