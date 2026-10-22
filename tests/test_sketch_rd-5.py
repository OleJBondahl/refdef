"""Sketch cases S41 and S42 on the real library."""

from refdef.plc import parse_address


def test_s41_plc_as_bit():
    """R11: `%Q7.5` prints as it is and `as_bit` gives `%QX7.5`."""
    address = parse_address("%Q7.5").value
    assert address is not None
    assert str(address) == "%Q7.5"
    assert str(address.as_bit()) == "%QX7.5"


def test_s42_plc_incomplete():
    """R11: `%I*` is read and prints `%I*`."""
    assert str(parse_address("%I*").value) == "%I*"
