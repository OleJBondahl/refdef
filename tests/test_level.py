"""R2 (half) and R3 gates for Level: every value that constructs prints its text."""

import pytest

from refdef import Aspect, Designation, Level
from refdef.level import coded_split

SIGNS = {a: a.value for a in Aspect}


def test_coded_split_hits_and_misses():
    """R2: `coded_split` reads a code shape worth 1..999_999_999 and nothing else."""
    assert coded_split("K1") == ("K", "1")
    assert coded_split("k01") == ("k", "01")
    assert coded_split("7") == ("", "7")
    assert coded_split("KE12") == ("KE", "12")
    assert coded_split("K999999999") == ("K", "999999999")
    for body in ("K0", "0", "00", "K1234567890", "ER", "", "K1A", "1" * 5000, "Å1", "K\u0661"):
        assert coded_split(body) is None, body


def _every_value():
    for aspect in Aspect:
        yield Level(aspect, "K", 1)
        yield Level(aspect, "AB", 999_999_999)
        yield Level(aspect, number=3)
        yield Level(aspect, label="ER")
    for label in ("K0", "0", "K1234567890", "Room 1", "Skjåp", "A1B2", "PE_BAR", "00"):
        yield Level(Aspect.LOCATION, label=label)


@pytest.mark.parametrize("level", list(_every_value()))
def test_every_constructible_level_prints(level):
    """R2: a level that constructs prints its sign and text; the text is coded-free for labels."""
    text = str(Designation((level,)))
    assert text == level.aspect.value + level.text
    assert text.startswith(SIGNS[level.aspect])
    if level.label:
        assert coded_split(level.text) is None
    else:
        assert coded_split(level.text) == (level.code, str(level.number))


def test_level_text_is_label_or_code_and_number():
    """R2: `text` is the label, else letters then number without padding."""
    assert Level(Aspect.PRODUCT, "K", 12).text == "K12"
    assert Level(Aspect.PRODUCT, number=4).text == "4"
    assert Level(Aspect.PRODUCT, label="ER").text == "ER"


def test_a_malformed_level_names_its_field():
    """R2: the TypeError message names the offending field."""
    with pytest.raises(TypeError, match="label"):
        Level(Aspect.PRODUCT, label="K1")
    with pytest.raises(TypeError, match="number"):
        Level(Aspect.PRODUCT, "K", 0)


def test_non_str_code_or_label_is_refused():
    """R2: a code or label of a wrong Python type raises TypeError."""
    with pytest.raises(TypeError, match="str"):
        Level(Aspect.PRODUCT, code=1, number=1)  # ty: ignore[invalid-argument-type] - a malformed call on purpose
    with pytest.raises(TypeError, match="str"):
        Level(Aspect.PRODUCT, label=1)  # ty: ignore[invalid-argument-type] - a malformed call on purpose
