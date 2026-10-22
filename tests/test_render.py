"""R3 gates: strict `str`, and each `render` option changes only its documented characters."""

import importlib.util
from pathlib import Path

import pytest

from refdef import Aspect, Designation, Level, Signal, Terminal, render

F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION


def _k1() -> Designation:
    return Designation().child(P, "U", 1).child(P, "U", 2).child(P, "K", 3)


VALUES = [
    Designation(),
    _k1(),
    Designation((Level(L, label="ER"), *_k1().levels)),
    Designation().child(P, "W", 25).child(P, number=1),
    Designation().child(P, "W", 1),
    Designation((Level(F, "U", 1), Level(F, "P", 1), Level(L, label="ER"), Level(L, number=3))),
    Designation((Level(L, number=3), Level(L, number=3))),
    Designation((Level(Aspect.ASSIGNMENT, "F", 1), Level(Aspect.SITE, "S", 1), Level(P, "K", 1))),
    Designation(_k1().levels, top="Plant A"),
    Designation(top="Plant A"),
    Designation((Level(P, label="Room 1"), Level(P, "W", 12345))),
]


@pytest.mark.parametrize("value", VALUES)
def test_str_is_render_with_no_option(value):
    """R3: `str(v) == render(v)` and the explicit defaults change nothing."""
    assert str(value) == render(value)
    assert render(value, pad=None, dotted=(), bare=False) == str(value)


def test_str_never_pads_dots_or_drops_a_sign():
    """R3: strict print keeps every sign and writes numbers without padding."""
    assert str(_k1()) == "-U1-U2-K3"
    assert str(Designation().child(P, "W", 25).child(P, number=1)) == "-W25-1"
    assert str(Designation((Level(L, number=3), Level(L, number=3)))) == "+3+3"
    assert str(Designation(_k1().levels, top="T")) == "<T>-U1-U2-K3"


def test_worked_examples():
    """R3: the guide's examples print as documented."""
    assert render(Designation().child(P, "W", 25).child(P, number=1), dotted=(P,)) == "-W25.1"
    assert render(Designation().child(P, "W", 1), pad={"W": 4}) == "-W0001"
    assert render(_k1(), bare=True) == "U1-U2-K3"


@pytest.mark.parametrize("value", VALUES)
def test_pad_changes_only_digits_of_listed_codes(value):
    """R3: `pad` adds only zeros inside the number of a coded level with a listed code."""
    padded = render(value, pad={"W": 4})
    assert len(padded) >= len(str(value))
    assert padded.replace("0", "") == str(value).replace("0", "")
    if all(lv.code != "W" for lv in value.levels):
        assert padded == str(value)


def test_pad_details():
    """R3: a wider number prints in full, an unlisted code and a number-only level are kept."""
    w = Designation().child(P, "W", 123456).child(P, "K", 7).child(P, number=2)
    assert render(w, pad={"W": 4, "K": 2}) == "-W123456-K07-2"
    assert render(w, pad={}) == str(w)
    assert render(w, pad={"": 3}) == str(w)


@pytest.mark.parametrize("value", VALUES)
def test_dotted_changes_only_signs_of_number_only_followers(value):
    """R3: `dotted` swaps a sign for `.` on a number-only level after the same aspect."""
    out = render(value, dotted=tuple(Aspect))
    expected = value.top and f"<{value.top}>"
    prev = None
    for level in value.levels:
        sub = prev is not None and prev.aspect is level.aspect and not level.code and level.number
        expected += ("." if sub else level.aspect.value) + level.text
        prev = level
    assert out == expected
    assert render(value, dotted=()) == str(value)


def test_dotted_only_for_listed_aspects():
    """R3: an aspect that is not listed keeps its sign."""
    v = Designation((Level(L, number=3), Level(L, number=3), Level(P, "W", 1), Level(P, number=1)))
    assert render(v, dotted=(P,)) == "+3+3-W1.1"
    assert render(v, dotted=(L,)) == "+3.3-W1-1"


@pytest.mark.parametrize("value", VALUES)
def test_bare_omits_only_the_first_sign(value):
    """R3: `bare` drops the first level's sign and nothing else."""
    out = render(value, bare=True)
    if not value.levels:
        assert out == str(value)
        return
    first = value.levels[0]
    prefix = f"<{value.top}>" if value.top else ""
    assert str(value) == prefix + first.aspect.value + out[len(prefix) :]


def test_options_are_required_by_name_and_checked():
    """R3 and F3: options are keyword-only and a malformed call raises TypeError."""
    with pytest.raises(TypeError):
        render(Designation(), {"W": 4})  # ty: ignore[too-many-positional-arguments] - keyword-only
    for bad in (
        lambda: render("-K1"),  # ty: ignore[invalid-argument-type] - a malformed call on purpose
        lambda: render(Designation(), pad={"W": "4"}),  # ty: ignore[invalid-argument-type] - a malformed call on purpose
        lambda: render(Designation(), pad={"W": True}),
        lambda: render(Designation(), pad=[("W", 4)]),  # ty: ignore[invalid-argument-type] - a malformed call on purpose
        lambda: render(Designation(), dotted=("-",)),  # ty: ignore[invalid-argument-type] - a malformed call on purpose
        lambda: render(Designation(), bare=1),  # ty: ignore[invalid-argument-type] - a malformed call on purpose
    ):
        with pytest.raises(TypeError):
            bad()


def test_terminal_and_signal_print_through_str_only():
    """R3: terminals and signals have `__str__` only, built on the strict designation."""
    assert str(Terminal(_k1(), ("13",))) == "-U1-U2-K3:13"
    assert str(Terminal(Designation().child(P, "X", 1), ("L1", "1"))) == "-X1:L1:1"
    assert str(Signal(Designation().child(P, "K", 1), "SYSTEM_CAN_L")) == "-K1;SYSTEM_CAN_L"
    assert str(Signal(None, "N")) == ";N"
    assert str(Signal(Designation(top="T"), "a:b;c&d")) == "<T>;a:b;c&d"


_CORPUS = Path(__file__).resolve().parent / "corpus"
_SPEC = importlib.util.spec_from_file_location(
    "gen_render_corpus", Path(__file__).resolve().parent.parent / "scripts" / "gen_render_corpus.py"
)
_GEN = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_GEN)


def _lines(name: str) -> list[str]:
    """The lines of a corpus file, dropping only its final newline."""
    return (_CORPUS / name).read_text(encoding="utf-8").removesuffix("\n").split("\n")


def test_golden_render_corpus():
    """R3: each line of render.txt is `columns()` of the same line of strings.txt."""
    strings = _lines("strings.txt")
    golden = _lines("render.txt")
    assert len(golden) == len(strings)
    for text, expected in zip(strings, golden, strict=True):
        assert _GEN.columns(text) == expected, f"render differs for string {text!r}"


def test_golden_lines_are_four_columns_led_by_strict_print():
    """R3: every render.txt line has four TAB-separated columns and column 1 is the input string."""
    for text, golden in zip(_lines("strings.txt"), _lines("render.txt"), strict=True):
        fields = golden.split("\t")
        assert len(fields) == 4, f"string {text!r}"
        assert fields[0] == text, f"strict print differs for string {text!r}"
