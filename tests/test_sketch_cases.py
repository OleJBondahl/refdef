"""Sketch cases ported to the real library, one function per case, the ID in the name."""

import pytest

from refdef import Aspect, Designation, Level, render

P, L = Aspect.PRODUCT, Aspect.LOCATION


def test_s17_label_with_sign_refused():
    """R2: a label holding a sign character is refused with TypeError."""
    for label in ("A-B", "A+B", "A=B", "A%B", "A#B"):
        with pytest.raises(TypeError):
            Level(L, label=label)


def test_s26_dotted_on_product():
    """R3: `dotted` prints a number-only product level after a product level with a dot."""
    d = Designation().child(P, "W", 25).child(P, number=1)
    assert render(d, dotted=(P,)) == "-W25.1"
    assert str(d) == "-W25-1"


def test_s27_grid_plus_3_plus_3():
    """R3: two number-only location levels print `+3+3` and keep their signs."""
    d = Designation().child(L, number=3).child(L, number=3)
    assert str(d) == "+3+3"
    assert render(d, dotted=()) == "+3+3"
