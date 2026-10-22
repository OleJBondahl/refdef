"""Sketch cases S04-S08 on the real library, one function each."""

from typing import cast

from refdef import Aspect, Designation, Level, allocate, natural_key, number_group, parse, sort_key

F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION


def test_s04_allocate_takes_the_first_free_number():
    """R8: with -K1 and -K2 taken, the next -K is 3."""
    assert allocate(P, "K", {Level(P, "K", 1), Level(P, "K", 2)}) == 3


def test_s05_reserved_leaves_a_gap():
    """R8: a reserved -K1 makes the first free -K number 2."""
    assert allocate(P, "K", set(), reserved={Level(P, "K", 1)}) == 2


def test_s06_number_group_numbers_in_sequence():
    """R8: K, K, F with -K2 taken gives K1, K3, F1."""
    group = number_group(P, ["K", "K", "F"], taken={Level(P, "K", 2)})
    assert [level.text for level in group] == ["K1", "K3", "F1"]


def test_s07_mixed_sort_order():
    """R9: numbers before text, locations before products, -W2 before -W10."""
    texts = ["-W10", "-W2", "-K1", "+ER-K1", "+3", "-PE_BAR"]
    parsed = [cast("Designation", parse(t, bare=P).value) for t in texts]
    ordered = sorted(parsed, key=lambda d: sort_key(d, aspects=(F, L, P)))
    assert [str(d) for d in ordered] == ["+3", "+ER-K1", "-K1", "-PE_BAR", "-W2", "-W10"]


def test_s08_a_leading_zero_sorts_first():
    """R9: X01 sorts before X1."""
    assert natural_key("X01") < natural_key("X1")
