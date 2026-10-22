"""R2 and F3 gates for the Designation, Terminal and Signal methods of RD-1."""

import pytest

from refdef import Aspect, Designation, Level, Signal, Terminal

F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION


def _d() -> Designation:
    return Designation((Level(F, "U", 1), Level(P, "K", 2), Level(L, label="ER"), Level(P, "F", 3)))


def test_child_adds_one_level_and_keeps_the_top():
    """R2: `child` appends a validated level and keeps the top."""
    d = Designation(top="T").child(P, "K", 1)
    assert d.levels == (Level(P, "K", 1),)
    assert d.top == "T"


def test_only_keeps_listed_aspects_in_order_and_the_top():
    """R2: `only` filters by aspect, keeps order and top."""
    d = Designation(_d().levels, top="T")
    assert str(d.only(P)) == "<T>-K2-F3"
    assert str(d.only(L, F)) == "<T>=U1+ER"
    assert d.only() == Designation(top="T")


def test_parent_removes_the_last_level_of_an_aspect():
    """R2: `parent` drops the last level of the aspect, any aspect if None, else returns self."""
    assert str(_d().parent()) == "=U1-K2+ER"
    assert str(_d().parent(P)) == "=U1-K2+ER"
    assert str(_d().parent(F)) == "-K2+ER-F3"
    assert _d().parent(Aspect.SITE) == _d()
    assert Designation().parent() == Designation()


def test_last_is_the_last_level_or_none():
    """R2: `last` is the last level, or None for the root."""
    assert _d().last == Level(P, "F", 3)
    assert Designation().last is None


def test_wrong_kind_of_argument_raises_type_error():
    """F3: a wrong kind of argument to `only` or `parent` raises TypeError."""
    with pytest.raises(TypeError):
        _d().only("-")  # ty: ignore[invalid-argument-type] - a malformed call on purpose
    with pytest.raises(TypeError):
        _d().parent("-")  # ty: ignore[invalid-argument-type] - a malformed call on purpose


def test_a_designation_and_terminal_are_frozen_and_hashable():
    """F2: values are frozen and equal by value."""
    assert hash(_d()) == hash(_d())
    assert Terminal(_d(), ("1",)) == Terminal(_d(), ("1",))
    assert Signal(None, "N") == Signal(None, "N")
