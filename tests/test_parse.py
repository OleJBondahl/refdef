"""R4, R5: the lenient reader repairs with one issue per repair; `parse` takes no scheme."""

import inspect
import random
from typing import Any, cast

import fuzz
import pytest

from refdef import Aspect, Designation, Signal, Terminal, parse

P = Aspect.PRODUCT

# (text, bare, str(value), issue-code values in order)
TABLE = [
    ("-K1", P, "-K1", ()),
    ("==A1", P, "==A1", ()),
    ("++S1", P, "++S1", ()),
    ("<Plant A>-K1", P, "<Plant A>-K1", ()),
    ("", P, "", ("empty",)),
    ("   ", P, "", ("empty",)),
    ("  -K1  ", P, "-K1", ()),
    ("K1", P, "-K1", ("no_sign",)),
    ("K1", Aspect.LOCATION, "+K1", ("no_sign",)),
    ("-", P, "", ("empty_level",)),
    ("<>-K1", P, "-K1", ("empty_top",)),
    ("< Plant A >-K1", P, "<Plant A>-K1", ("whitespace",)),
    ("- K1", P, "-K1", ("whitespace",)),
    ("-k1", P, "-K1", ("lower_case",)),
    ("-K01", P, "-K1", ("leading_zero",)),
    ("-k01", P, "-K1", ("leading_zero", "lower_case")),
    ("-K0", P, "-K0", ("zero_number",)),
    ("-K1234567890", P, "-K1234567890", ("number_too_large",)),
    ("-Room 1", P, "-Room 1", ("free_label",)),
    ("-ER", P, "-ER", ("free_label",)),
    ("-a<b", P, "", ("bad_label",)),
    ("-K1.2", P, "-K1-2", ("dot_level",)),
    ("=P1-.5", P, "=P1=5", ("empty_level", "dot_level")),
    ("-K1:A:", P, "-K1:A", ("empty_pin",)),
    ("-K1: A ", P, "-K1:A", ("whitespace",)),
    ("-K1:", P, "-K1", ("empty_pin",)),
    ("-K1;", P, "-K1", ("empty_name",)),
    ("-K1; X ", P, "-K1;X", ("whitespace",)),
    ("-K1&D1", P, "-K1", ("unsupported_suffix",)),
    ("-K1:A:B", P, "-K1:A:B", ()),
    ("-K1;SIG", P, "-K1;SIG", ()),
    (";SIG", P, ";SIG", ()),
    ("<Plant>;SIG", P, "<Plant>;SIG", ()),
    ("-K1;a:b;c", P, "-K1;a:b;c", ()),
]


@pytest.mark.parametrize(("text", "bare", "shown", "codes"), TABLE)
def test_parse_table(text, bare, shown, codes):
    """R4: each input reads to its value and to one issue per repair, in order."""
    parsed = parse(text, bare=bare)
    assert str(parsed.value) == shown
    assert tuple(issue.code.value for issue in parsed.issues) == codes


def test_table_covers_every_parse_code():
    """R4: the table has a row for every parse-family code but NOT_ADDRESS."""
    seen = {code for *_, codes in TABLE for code in codes}
    assert seen >= {
        "empty",
        "no_sign",
        "empty_level",
        "empty_top",
        "whitespace",
        "lower_case",
        "leading_zero",
        "zero_number",
        "number_too_large",
        "free_label",
        "bad_label",
        "dot_level",
        "empty_pin",
        "empty_name",
        "unsupported_suffix",
    }
    assert "not_address" not in seen


def test_value_types():
    """R4: a suffix decides the type of the value; a dropped suffix leaves a Designation."""
    assert type(parse("-K1", bare=P).value) is Designation
    assert type(parse("-K1:A", bare=P).value) is Terminal
    assert type(parse("-K1;SIG", bare=P).value) is Signal
    assert type(parse(";SIG", bare=P).value) is Signal
    assert type(parse("-K1:", bare=P).value) is Designation
    assert type(parse("-K1;", bare=P).value) is Designation
    assert type(parse("-K1&D", bare=P).value) is Designation


def test_signal_of():
    """R4: a signal with no levels and no top has `of=None`; with a designation it keeps it."""
    assert cast("Any", parse(";SIG", bare=P).value).of is None
    assert cast("Any", parse("-K1;SIG", bare=P).value).of == parse("-K1", bare=P).value
    assert cast("Any", parse("<Plant>;SIG", bare=P).value).of == Designation(top="Plant")


def test_terminal_pins():
    """R4: pins are split on a colon and kept in order."""
    assert cast("Any", parse("-K1:A:B", bare=P).value).pins == ("A", "B")


def test_longest_sign():
    """R4: `==` and `++` win over `=` and `+`; they read as one level each."""
    assert len(cast("Any", parse("==A1", bare=P).value).levels) == 1
    assert len(cast("Any", parse("++S1", bare=P).value).levels) == 1
    assert cast("Any", parse("==A1", bare=P).value).levels[0].aspect is Aspect.ASSIGNMENT
    assert cast("Any", parse("++S1", bare=P).value).levels[0].aspect is Aspect.SITE


def test_signature():
    """R5: `parse` has no scheme; `text` is positional and `bare` is keyword-only, required."""
    params = inspect.signature(parse).parameters
    assert "scheme" not in params
    assert params["text"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert params["bare"].kind is inspect.Parameter.KEYWORD_ONLY
    assert params["bare"].default is inspect.Parameter.empty


@pytest.mark.parametrize("text", [None, 1, b"-K1", ["-K1"]])
def test_non_str_text_raises(text):
    """R4: only a non-`str` text raises TypeError."""
    with pytest.raises(TypeError):
        parse(text, bare=P)


@pytest.mark.parametrize("bare", [None, "-", "PRODUCT", 1])
def test_non_aspect_bare_raises(bare):
    """R4: only a non-`Aspect` bare raises TypeError."""
    with pytest.raises(TypeError):
        parse("-K1", bare=bare)


def test_bare_positional_raises():
    """R5: `bare` is keyword-only, so passing it positionally is a TypeError."""
    with pytest.raises(TypeError):
        parse("-K1", P)  # ty: ignore[too-many-positional-arguments, missing-argument] - passed positionally on purpose


@pytest.mark.parametrize("bare", list(Aspect))
def test_fuzz_corpus_never_raises(bare):
    """R4: random text, lone signs, `<>`, empty, whitespace and a 5000-digit run never raise."""
    for text in fuzz.hostile_texts(random.Random(0)):  # noqa: S311 - seeded test data, not security
        result = parse(text, bare=bare)
        assert isinstance(result.value, (Designation, Terminal, Signal))


def test_long_zero_run_is_a_zero_label():
    """R4: a run of 5000 zeros is above the int-string limit and reads as a zero label."""
    result = parse("-" + "0" * 5000, bare=P)
    assert [i.code.value for i in result.issues] == ["zero_number"]
