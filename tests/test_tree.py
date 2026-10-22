"""R7: per-aspect tree arithmetic (`within`, `relative_to`, `common`) on all three types."""

from typing import Any, cast

import pytest

from refdef import Aspect, Designation, Signal, Terminal, parse

F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION


def d(text: str) -> Designation:
    """The designation a string parses to."""
    value = parse(text, bare=P).value
    assert isinstance(value, Designation)
    return value


ROOT = d("=U1+ER")


def test_unit_root_designation():
    """R7: a unit root drops its heads per aspect; the product tree is untouched."""
    item = d("=U1=P1+ER+C1-K1")
    assert item.within(ROOT)
    assert str(item.relative_to(ROOT)) == "=P1+C1-K1"


def test_cable_designation():
    """R7: a cable with no location is within a root that has one and prints `-W1`."""
    cable = d("=U1-W1")
    assert cable.within(ROOT)
    assert str(cable.relative_to(ROOT)) == "-W1"


def test_mixed_order_designation():
    """R7: the order of the kept levels is the order of the original, not grouped by aspect."""
    item = d("-K1=U1-K2+ER=P1")
    assert str(item.relative_to(ROOT)) == "-K1-K2=P1"
    assert str(Designation.common(d("-K1+C1=A1"), d("=A1+C1-K1"))) == "-K1+C1=A1"
    assert str(Designation.common(d("=A1+C1-K1"), d("-K1+C1=A1"))) == "=A1+C1-K1"


def test_top_node_designation():
    """R7: a root with a top matches only that top and the top is dropped; else kept."""
    item = d("<S1>=U1-K1")
    assert item.within(d("<S1>=U1"))
    assert str(item.relative_to(d("<S1>=U1"))) == "-K1"
    assert not item.within(d("<S2>=U1"))
    assert item.relative_to(d("<S2>=U1")) is item
    assert str(item.relative_to(d("=U1"))) == "<S1>-K1"
    assert str(Designation.common(item, d("<S1>=U1-K2"))) == "<S1>=U1"
    assert str(Designation.common(item, d("=U1-K2"))) == "=U1"


def test_not_within_returns_self():
    """R7: a root that shares no aspect, or a longer head, leaves the designation unchanged."""
    k1 = d("-K1")
    assert not k1.within(ROOT)
    assert k1.relative_to(ROOT) is k1
    assert not d("=U1").within(d("=U1=P1"))
    assert d("-K1").within(Designation())
    assert d("-K1").relative_to(Designation()) == d("-K1")


def test_common_cases():
    """R7: the shortest shared head per aspect; none gives the root; a missing aspect gives 0."""
    assert str(Designation.common(d("=A1+C1-K1"), d("-K1"))) == "-K1"
    assert str(Designation.common(d("=A1+C1-K1"), d("=A1+C1-K2"), d("=A1+C2-F1"))) == "=A1"
    assert Designation.common() == Designation()
    assert Designation.common(d("=A1-K1")) == d("=A1-K1")
    assert Designation.common(d("=A1"), d("-K1")) == Designation()


def test_terminal_cases():
    """R7: a Terminal's `of` is made relative and its pins are kept as given."""
    pins = ("L1", "a b")
    unit = Terminal(d("=U1=P1+ER-X1"), pins)
    assert str(unit.relative_to(ROOT)) == "=P1-X1:L1:a b"
    cable = Terminal(d("=U1-W1"), ("1",))
    assert str(cable.relative_to(ROOT)) == "-W1:1"
    mixed = Terminal(d("-K1=U1-K2"), ("13",))
    assert str(mixed.relative_to(ROOT)) == "-K1-K2:13"
    topped = Terminal(d("<S1>=U1-K1"), ("A1",))
    assert str(topped.relative_to(d("<S1>=U1"))) == "-K1:A1"
    assert str(topped.relative_to(d("=U1"))) == "<S1>-K1:A1"
    assert Terminal(d("=U1"), ("1",)).relative_to(ROOT).pins == ("1",)


def test_signal_cases():
    """R7: a Signal's `of` is made relative; an empty result becomes None; the name is kept."""
    sig = Signal(d("=U1=P1+ER-K1"), "CAN_L")
    assert str(sig.relative_to(ROOT)) == "=P1-K1;CAN_L"
    assert str(Signal(d("=U1-W1"), "N").relative_to(ROOT)) == "-W1;N"
    assert str(Signal(d("-K1=U1-K2"), "N").relative_to(ROOT)) == "-K1-K2;N"
    assert str(Signal(d("<S1>=U1-K1"), "N").relative_to(d("<S1>=U1"))) == "-K1;N"
    assert Signal(d("=U1+ER"), "X").relative_to(ROOT) == Signal(None, "X")
    bare = Signal(None, "A;B")
    assert bare.relative_to(ROOT) is bare


@pytest.mark.parametrize(
    "call",
    [lambda: d("-K1").within(cast("Any", "-K1")), lambda: Designation.common(cast("Any", 1))],
)
def test_malformed_calls_raise_type_error(call):
    """R7: a non-Designation root or argument is a malformed call (F3)."""
    with pytest.raises(TypeError):
        call()
