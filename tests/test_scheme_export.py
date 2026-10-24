"""LetterRule and ClassTable are public names: a caller builds a Scheme from them."""

import refdef
from refdef import Aspect, ClassEntry, ClassTable, LetterRule, Scheme


def test_letter_rule_and_class_table_are_exported():
    assert "LetterRule" in refdef.__all__
    assert "ClassTable" in refdef.__all__


def test_a_scheme_built_from_exported_names_looks_up_its_entry():
    table = ClassTable(name="t", version="1", depth=1, entries=(ClassEntry("A", "x"),))
    scheme = Scheme("custom", frozenset({Aspect.PRODUCT}), LetterRule(1, 2, frozenset("I")), table)
    assert scheme.classes.get("A") == ClassEntry("A", "x")
    assert scheme.letters.never == frozenset("I")
