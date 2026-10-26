"""R5, R10 and the shipped table: shape of the 184 entries, lookup by `code[:depth]`, `extend`."""

import re
from pathlib import Path

import family
import pytest
from test_wording import check_wording

from refdef import STANDARD, Aspect, ClassEntry, Designation, check, parse, render
from refdef.scheme import ClassTable

ENTRIES = STANDARD.classes.entries
MAINS = [e for e in ENTRIES if len(e.code) == 1]
PAIRS = [e for e in ENTRIES if len(e.code) == 2]


def test_table_counts():
    """R10: 18 main letters and 166 two-letter codes, nothing else."""
    assert len(MAINS) == 18
    assert len(PAIRS) == 166
    assert len(ENTRIES) == len(MAINS) + len(PAIRS)


def test_class_a_parses_checks_and_renders():
    """R10: class A (assemblies and controllers) is in the table; `-A4` parses and checks clean."""
    value = parse("-A4", bare=Aspect.PRODUCT).value
    assert isinstance(value, Designation)
    assert check([value], STANDARD) == ()
    assert render(value) == "-A4"


def test_table_codes_are_unique_capitals():
    """R10: codes are unique and made of capital letters A-Z only."""
    codes = [e.code for e in ENTRIES]
    assert len(set(codes)) == len(codes)
    assert all(re.fullmatch(r"[A-Z]{1,2}", c) for c in codes)


def test_table_every_pair_has_its_main_letter():
    """R10: the first letter of every two-letter code is a listed main letter."""
    mains = {e.code for e in MAINS}
    assert {e.code[0] for e in PAIRS} <= mains


def test_table_titles_one_to_five_words_without_digits_and_unique():
    """R10 and M15: 1-5 words, no digit, and no title is used twice."""
    titles = [e.title for e in ENTRIES]
    assert all(1 <= len(t.split()) <= 5 for t in titles)
    assert not any(ch.isdigit() for t in titles for ch in t)
    assert len(set(titles)) == len(titles)


def test_table_is_depth_two_and_sorted():
    """M15: depth 2 and entries sorted by code, the generator's order."""
    assert STANDARD.classes.depth == 2
    codes = [e.code for e in ENTRIES]
    assert codes == sorted(codes)


def test_get_finds_by_first_two_letters():
    """R5: `get("KEB")` finds `KE`; a one-letter code finds its main letter."""
    table = STANDARD.classes
    assert table.get("KEB") == table.index["KE"]
    assert table.get("K") == table.index["K"]
    assert table.get("KE") == table.index["KE"]


def test_get_has_no_shorter_prefix_fallback():
    """R5: `KX` is unknown although `K` exists; `get` never falls back to the main letter."""
    assert "K" in STANDARD.classes.index
    assert STANDARD.classes.get("KX") is None
    assert STANDARD.classes.get("KXY") is None
    assert STANDARD.classes.get("J") is None


def test_get_uses_the_tables_depth():
    """R5: a depth-1 table looks a code up by its first letter only."""
    table = ClassTable("t", "1", 1, (ClassEntry("K", "relay"),))
    assert table.get("KE") == ClassEntry("K", "relay")
    assert table.get("KEB") == ClassEntry("K", "relay")


def test_extend_later_wins_and_first_position_is_kept():
    """R5: an entry overlaid by code replaces the old one in its place; new codes go last."""
    scheme = STANDARD.extend(ClassEntry("B", "Own title"), ClassEntry("J", "board connector"))
    entries = scheme.classes.entries
    assert entries[1] == ClassEntry("B", "Own title")
    assert entries[-1] == ClassEntry("J", "board connector")
    assert len(entries) == len(ENTRIES) + 1
    assert [e.code for e in entries[:-1]] == [e.code for e in ENTRIES]


def test_extend_returns_a_new_scheme_and_leaves_standard_alone():
    """R5: `extend` never changes the scheme it is called on; aspects are added, not replaced."""
    scheme = STANDARD.extend(aspects=(Aspect.TYPE,))
    assert Aspect.TYPE in scheme.aspects
    assert Aspect.TYPE not in STANDARD.aspects
    assert scheme.aspects >= STANDARD.aspects
    assert STANDARD.classes.get("J") is None


def test_standard_aspects_are_function_product_location():
    """R5: only `=`, `-` and `+` are on in the shipped scheme."""
    assert STANDARD.aspects == {Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION}


def test_f7_patterns_run_over_the_table(tmp_path: Path):
    """F7: the wording scan reads `tables/`; a cited standard in the table fails it."""
    folder = tmp_path / "src" / "refdef" / "tables"
    folder.mkdir(parents=True)
    text = (family.ROOT / "src" / "refdef" / "tables" / "standard.py").read_text(encoding="utf-8")
    (folder / "standard.py").write_text(text, encoding="utf-8")
    check_wording(tmp_path)
    (folder / "standard.py").write_text(text + "# see IEC 81346\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="standard wording"):
        check_wording(tmp_path)
