"""Sketch cases S09-S14 on the real library, one function each."""

from refdef import Aspect, Designation, parse

P = Aspect.PRODUCT


def d(text: str) -> Designation:
    """The designation a string parses to."""
    value = parse(text, bare=P).value
    assert isinstance(value, Designation)
    return value


def test_s09_cable_within_root():
    """R7: the cable `=U1-W1` is within the root `=U1+ER`."""
    assert d("=U1-W1").within(d("=U1+ER"))


def test_s10_cable_relative():
    """R7: the cable relative to `=U1+ER` prints `-W1`."""
    assert str(d("=U1-W1").relative_to(d("=U1+ER"))) == "-W1"


def test_s11_item_relative():
    """R7: `=U1=P1+ER+C1-K1` relative to `=U1+ER` prints `=P1+C1-K1`."""
    assert str(d("=U1=P1+ER+C1-K1").relative_to(d("=U1+ER"))) == "=P1+C1-K1"


def test_s12_common_is_product_tail():
    """R7: `common(=A1+C1-K1, -K1)` is `-K1`, and `-K1` is within `=A1+C1-K1`."""
    assert str(Designation.common(d("=A1+C1-K1"), d("-K1"))) == "-K1"
    assert d("-K1").within(d("=A1+C1-K1"))


def test_s13_common_of_three():
    """R7: the common of `=A1+C1-K1`, `=A1+C1-K2` and `=A1+C2-F1` is `=A1`."""
    three = (d("=A1+C1-K1"), d("=A1+C1-K2"), d("=A1+C2-F1"))
    assert str(Designation.common(*three)) == "=A1"


def test_s14_common_of_none_is_root():
    """R7: `common()` is the empty designation."""
    assert Designation.common() == Designation()
