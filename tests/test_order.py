"""R9: the natural order, the sort key, and the required `aspects`."""

import inspect
import random
from typing import cast

import pytest

from refdef import Aspect, Designation, Level, natural_key, parse, sort_key

F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION


def test_digit_runs_compare_by_value():
    """R9: -W2 sorts before -W10."""
    assert natural_key("W2") < natural_key("W10")


def test_a_leading_zero_sorts_before_the_plain_number():
    """R9: equal values tie on the raw text, so X01 < X1."""
    assert natural_key("X01") < natural_key("X1")


def test_numbers_sort_before_text():
    """R9: a digit run ranks before a text run."""
    assert natural_key("1") < natural_key("A")
    assert natural_key("W1") < natural_key("WA")


def test_case_sensitivity_is_an_option():
    """R9: with case_sensitive False text runs compare lower-cased, ties on the raw text."""
    assert natural_key("B") < natural_key("a")
    assert natural_key("a") < natural_key("b")
    assert natural_key("a", case_sensitive=False) < natural_key("B", case_sensitive=False)
    assert natural_key("A", case_sensitive=False) < natural_key("a", case_sensitive=False)


def test_a_huge_digit_run_does_not_raise():
    """R9: a run longer than int's text limit still orders by value."""
    big = "9" * 5000
    assert natural_key("W" + big) > natural_key("W" + "9" * 4999)
    assert natural_key("W" + "0" * 5000 + "1") < natural_key("W2")


def test_non_ascii_digits_are_text():
    """R9: only ASCII digits are numbers."""
    assert natural_key("٣")[0] == ((1, "٣"),)


def test_natural_key_refuses_a_non_string():
    """R9: a malformed call raises TypeError."""
    with pytest.raises(TypeError):
        natural_key(1)  # ty: ignore[invalid-argument-type] - the malformed call


def test_sort_key_has_aspects_keyword_only_and_no_default():
    """R9: `aspects` is required and keyword-only."""
    parameter = inspect.signature(sort_key).parameters["aspects"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


def test_sort_key_ranks_by_the_listed_aspects_then_enum_order():
    """R9: a listed aspect ranks by its index, an unlisted one after, in enum order."""
    d = Designation((Level(L, label="ER"), Level(F, "M", 1), Level(P, "K", 1)))
    ranks = [pair[0] for pair in sort_key(d, aspects=(F, L, P))]
    assert ranks == [1, 0, 2]
    ranks = [pair[0] for pair in sort_key(d, aspects=(P,))]
    assert ranks == [2, 1, 0]


def test_sort_key_leaves_out_the_top():
    """R9: the top node is not part of the key."""
    assert sort_key(Designation(top="X"), aspects=(P,)) == ()


@pytest.mark.parametrize("aspects", ["abc", (P, "x"), 5])
def test_sort_key_refuses_bad_aspects(aspects):
    """R9: aspects must be a sequence of Aspect."""
    with pytest.raises(TypeError):
        sort_key(Designation(), aspects=aspects)


def test_mixed_designations_sort_in_the_documented_order():
    """R9: the mixed case of the sketch, aspects (F, L, P)."""
    texts = ["-W10", "-W2", "-K1", "+ER-K1", "+3", "-PE_BAR"]
    got = sorted(
        (cast("Designation", parse(t, bare=P).value) for t in texts),
        key=lambda d: sort_key(d, aspects=(F, L, P)),
    )
    assert [str(d) for d in got] == ["+3", "+ER-K1", "-K1", "-PE_BAR", "-W2", "-W10"]


_ALPHABET = ["A", "B", "a", "b", "0", "1", "2", "10", "01", "_"]


def _rng(seed: int) -> random.Random:
    return random.Random(seed)  # noqa: S311 - seeded test data, not security


def _random_text(rng: random.Random) -> str:
    return "".join(rng.choice(_ALPHABET) for _ in range(rng.randint(1, 4)))


def _labels(rng: random.Random) -> dict[str, tuple]:
    keys = {}
    for text in {_random_text(rng) for _ in range(300)}:
        try:
            keys[text] = sort_key(Designation((Level(P, label=text),)), aspects=(P,))
        except TypeError:
            continue  # a code-shaped text is no label
    return keys


def test_sort_key_is_a_total_order_consistent_with_natural_key():
    """R9: antisymmetry, transitivity and agreement with natural_key on single-level labels."""
    rng = _rng(7)
    key = _labels(rng)
    texts = sorted(key)
    for _ in range(500):
        a, b, c = (rng.choice(texts) for _ in range(3))
        assert not (key[a] < key[b] and key[b] < key[a])
        assert (key[a] == key[b]) == (a == b)
        if key[a] <= key[b] <= key[c]:
            assert key[a] <= key[c]
        assert (key[a] < key[b]) == (natural_key(a) < natural_key(b))
