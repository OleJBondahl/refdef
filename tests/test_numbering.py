"""R8: allocate against a brute-force search, number_group against the fold, no store."""

import random
from itertools import count

import pytest

from refdef import Aspect, Level, allocate, lowest_free, number_group

P = Aspect.PRODUCT


def _rng(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - seeded test data, not security


def _levels(rng: random.Random, aspect: Aspect, code: str, top: int) -> set[Level]:
    return {Level(aspect, code, n) for n in range(1, top) if rng.random() < 0.6}


def test_allocate_equals_brute_force_over_500_random_inputs():
    """R8: allocate is the first n from `first` with the level in neither collection."""
    rng = _rng(8)
    for _ in range(500):
        code = rng.choice(["K", "W", "KE"])
        taken = _levels(rng, P, code, 12) | _levels(rng, Aspect.LOCATION, code, 6)
        reserved = _levels(rng, P, code, 12)
        first = rng.randint(1, 6)
        expected = next(n for n in count(first) if Level(P, code, n) not in taken | reserved)
        before = set(taken)
        assert allocate(P, code, taken, reserved, first=first) == expected
        assert taken == before


def test_number_group_equals_the_fold_over_500_random_inputs():
    """R8: number_group is allocate in sequence, each result added to taken; taken is unchanged."""
    rng = _rng(9)
    for _ in range(500):
        codes = [rng.choice(["K", "F", "W"]) for _ in range(rng.randint(0, 6))]
        taken = _levels(rng, P, rng.choice(["K", "F"]), 8)
        reserved = _levels(rng, P, "W", 5)
        before = set(taken)
        used = set(taken)
        folded = []
        for code in codes:
            level = Level(P, code, allocate(P, code, used, reserved))
            used.add(level)
            folded.append(level)
        assert number_group(P, codes, taken, reserved) == tuple(folded)
        assert taken == before


def test_allocate_ignores_other_aspects_and_codes():
    """R8: only a level equal in aspect, code and number counts as taken."""
    taken = {Level(Aspect.LOCATION, "K", 1), Level(P, "F", 1)}
    assert allocate(P, "K", taken) == 1


def test_allocate_counts_a_reserved_level_as_used():
    """R8: a reserved level leaves a gap."""
    assert allocate(P, "K", set(), reserved={Level(P, "K", 1)}) == 2


@pytest.mark.parametrize("first", [0, -1, True, 1.0, "1"])
def test_allocate_refuses_a_first_below_one_or_not_an_int(first):
    """R8: `first` is an int of at least 1, else TypeError."""
    with pytest.raises(TypeError):
        allocate(P, "K", (), first=first)


def test_lowest_free_equals_brute_force_over_500_random_inputs():
    """R8: lowest_free is the first n from `first` in neither collection; inputs are unchanged."""
    rng = _rng(10)
    for _ in range(500):
        taken = {n for n in range(1, 12) if rng.random() < 0.6}
        reserved = {n for n in range(1, 12) if rng.random() < 0.4}
        first = rng.randint(1, 6)
        expected = next(n for n in count(first) if n not in taken | reserved)
        before = (set(taken), set(reserved))
        assert lowest_free(taken, reserved, first=first) == expected
        assert (taken, reserved) == before


def test_lowest_free_equals_allocate_over_one_class():
    """R8: over one aspect and code, lowest_free of the numbers is allocate of the levels."""
    rng = _rng(11)
    for _ in range(500):
        taken = _levels(rng, P, "K", 12)
        reserved = _levels(rng, P, "K", 12)
        first = rng.randint(1, 6)
        numbers = ({lv.number for lv in s if lv.number is not None} for s in (taken, reserved))
        got = lowest_free(*numbers, first=first)
        assert got == allocate(P, "K", taken, reserved, first=first)


def test_lowest_free_skips_a_reserved_number_like_a_taken_one():
    """R8: a reserved number leaves a gap."""
    assert lowest_free({1, 2}, {3}) == 4
    assert lowest_free(set(), {1}) == 2


def test_lowest_free_of_nothing_is_first():
    """R8: empty input gives `first`."""
    assert lowest_free(()) == 1
    assert lowest_free((), first=10) == 10


@pytest.mark.parametrize("first", [0, -1, True, 1.0, "1"])
def test_lowest_free_refuses_a_first_below_one_or_not_an_int(first):
    """R8: `first` is an int of at least 1, else TypeError."""
    with pytest.raises(TypeError):
        lowest_free((), first=first)
