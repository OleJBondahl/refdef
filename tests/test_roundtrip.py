"""R1: what `str` prints, `parse` reads back to the same value."""

import random
from pathlib import Path

import fuzz
import pytest

from refdef import Aspect, Designation, Signal, Terminal, parse

_CORPUS = Path(__file__).parent / "corpus" / "strings.txt"


def _rng() -> random.Random:
    return random.Random(0)  # noqa: S311 - seeded test data, not security


@pytest.fixture(scope="module")
def values() -> list[Designation | Terminal | Signal]:
    """2000 seeded values, drawn once for the module."""
    rng = _rng()
    return [fuzz.value(rng) for _ in range(2000)]


def test_generator_reaches_every_kind(values):
    """R1: the draw holds every value kind, so the round trip cannot go vacuous."""
    designs = [v for v in values if isinstance(v, Designation)]
    signals = [v for v in values if isinstance(v, Signal)]
    inner = [v.of for v in values if isinstance(v, (Terminal, Signal)) and v.of is not None]
    levels = [lv for d in designs + inner for lv in d.levels]
    assert any(d.top for d in designs + inner)
    assert any(isinstance(v, Terminal) for v in values)
    assert any(s.of is None for s in signals)
    assert any(s.of is not None for s in signals)
    assert {lv.aspect for lv in levels} == set(Aspect)
    assert any(" " in lv.label for lv in levels)


def test_generator_reaches_every_level_and_text_shape(values):
    """R1: the draw holds every aspect, label shape, number boundary, pin and name sign."""
    inner = [v.of for v in values if isinstance(v, (Terminal, Signal)) and v.of is not None]
    levels = [
        lv for d in [v for v in values if isinstance(v, Designation)] + inner for lv in d.levels
    ]
    signals = [v for v in values if isinstance(v, Signal)]
    assert any(not lv.label.isascii() for lv in levels)
    assert any(lv.code and lv.number for lv in levels)
    assert any(not lv.code and lv.number for lv in levels)
    assert any(lv.number == 999_999_999 for lv in levels)
    assert any(lv.number == 1 for lv in levels)
    assert any(
        any(c in p for c in ";&<>+-.=") for v in values if isinstance(v, Terminal) for p in v.pins
    )
    assert any(any(c in s.name for c in ":;&") for s in signals)


def test_values_round_trip(values):
    """R1: parse(str(v)) equals v for every aspect, and an issue-free parse prints back."""
    for v in values:
        text = str(v)
        for aspect in Aspect:
            got = parse(text, bare=aspect)
            assert got.value == v, (text, aspect, got)
            if not got.issues:
                assert str(got.value) == text, (text, aspect)


def test_corpus_lines_round_trip():
    """R1: every corpus line prints back to itself for every aspect, with or without issues."""
    for line in _CORPUS.read_text(encoding="utf-8").splitlines():
        for aspect in Aspect:
            got = parse(line, bare=aspect)
            assert str(got.value) == line, (line, aspect, got)


def test_hostile_texts_print_back_when_issue_free():
    """R1: a stripped hostile text that parses with no issue prints back unchanged."""
    for text in fuzz.hostile_texts(_rng()):
        for aspect in Aspect:
            got = parse(text, bare=aspect)
            if text == text.strip() and not got.issues:
                assert str(got.value) == text, (text, aspect)
