"""Family gate wrappers."""

import ast
import dataclasses
import random

import family
import fuzz
import issue_hook
import pytest

from refdef import STANDARD, Aspect, ClassEntry, Designation, Level, Signal, Terminal, check, parse
from refdef.issues import Issue, IssueCode, Parsed


def test_f3_issues_fixtures():
    family.gate_f3_check()


def test_r6_issue_fields():
    """R6: Issue has exactly the fields code, subject and message."""
    names = [f.name for f in dataclasses.fields(Issue)]
    assert names == ["code", "subject", "message"]


def test_r6_issue_code_members():
    """R6: IssueCode declares the 21 codes in order, parse family first."""
    names = [member.name for member in IssueCode]
    assert names == [
        "EMPTY",
        "NO_SIGN",
        "EMPTY_LEVEL",
        "EMPTY_TOP",
        "WHITESPACE",
        "LOWER_CASE",
        "LEADING_ZERO",
        "ZERO_NUMBER",
        "NUMBER_TOO_LARGE",
        "FREE_LABEL",
        "BAD_LABEL",
        "DOT_LEVEL",
        "EMPTY_PIN",
        "EMPTY_NAME",
        "UNSUPPORTED_SUFFIX",
        "NOT_ADDRESS",
        "ASPECT_OFF",
        "LETTER_COUNT",
        "NEVER_LETTER",
        "UNKNOWN_CLASS",
        "DUPLICATE",
    ]


def test_r6_issue_code_values_are_lower_case_names():
    """R6: every IssueCode value is the lower-case form of its name."""
    for member in IssueCode:
        assert member.value == member.name.lower()


def test_r6_issue_and_parsed_are_frozen():
    """R6: Issue and Parsed reject field assignment."""
    issue = Issue(IssueCode.EMPTY, "", "text is empty")
    parsed = Parsed(1, ())
    with pytest.raises(dataclasses.FrozenInstanceError):
        issue.message = "changed"  # ty: ignore[invalid-assignment] - assigning to a frozen field on purpose
    with pytest.raises(dataclasses.FrozenInstanceError):
        parsed.value = 2  # ty: ignore[invalid-assignment] - assigning to a frozen field on purpose


def test_r6_parsed_shape():
    """R6: Parsed holds value and issues, and value is kept as given."""
    assert Parsed(1, ()).value == 1
    assert [f.name for f in dataclasses.fields(Parsed)] == ["value", "issues"]


P, F, L = Aspect.PRODUCT, Aspect.FUNCTION, Aspect.LOCATION
CHECK_FAMILY = ("aspect_off", "letter_count", "never_letter", "unknown_class", "duplicate")


def _codes(*texts: str) -> list[str]:
    values = [parse(text, bare=P).value for text in texts]
    return [
        issue.code.value
        for issue in check([v for v in values if isinstance(v, Designation)], STANDARD)
    ]


@pytest.mark.parametrize(
    ("texts", "expected"),
    [
        (("%T1",), ["aspect_off"]),
        (("-KEBX1",), ["letter_count"]),
        (("-K1", "-K1"), ["duplicate"]),
        (("-KX1",), ["unknown_class"]),
        (("-KI1",), ["never_letter", "unknown_class"]),
    ],
)
def test_r5_one_case_per_check_code(texts, expected):
    """R5: each check-family code is reported for its own case."""
    assert _codes(*texts) == expected


def test_r5_every_check_code_has_a_case():
    """R5: the cases above cover the five check-family codes of IssueCode."""
    covered = {
        c for t in (("%T1",), ("-KEBX1",), ("-K1", "-K1"), ("-KX1",), ("-KI1",)) for c in _codes(*t)
    }
    assert set(CHECK_FAMILY) <= covered
    assert [m.value for m in IssueCode][-5:] == list(CHECK_FAMILY)


def test_r5_letter_count_below_the_minimum():
    """R5: a scheme whose rule needs two letters flags a one-letter code."""
    rule = dataclasses.replace(STANDARD.letters, min_count=2)
    scheme = dataclasses.replace(STANDARD, letters=rule)
    result = check([Designation().child(P, "K", 1)], scheme)
    assert [i.code for i in result] == [IssueCode.LETTER_COUNT]


def test_r5_issue_order_duplicate_before_level_issues():
    """R5: per designation, DUPLICATE comes before that designation's level issues."""
    assert _codes("-KX1", "-KX1") == ["unknown_class", "duplicate", "unknown_class"]


def test_r5_labels_and_number_only_levels_get_only_the_aspect_rule():
    """R5: a label or number-only level gets no letter or class issue; an off aspect shows."""
    labelled = Designation(
        (Level(L, label="ER"), Level(P, number=3), Level(Aspect.TYPE, label="X"))
    )
    result = check([labelled], STANDARD)
    assert [i.code for i in result] == [IssueCode.ASPECT_OFF]
    assert result[0].subject == "%X"


def test_r5_check_reads_the_scheme_it_is_given():
    """R5: `extend` turns an aspect on and adds a class; nothing else decides."""
    j = STANDARD.extend(ClassEntry("J", "board connector"), aspects=(Aspect.TYPE,))
    assert check([Designation().child(P, "J", 1).child(Aspect.TYPE, "J", 2)], j) == ()
    assert _codes("-J1") == ["unknown_class"]


def test_r5_check_type_errors():
    """R5: a non-Scheme scheme or a non-Designation item is a TypeError, not an issue."""
    with pytest.raises(TypeError):
        check([Designation()], "standard")  # ty: ignore[invalid-argument-type] - wrong type on purpose
    with pytest.raises(TypeError):
        check([Terminal(Designation().child(P, "K", 1), ("1",))], STANDARD)  # ty: ignore[invalid-argument-type] - wrong type on purpose
    with pytest.raises(TypeError):
        check(["-K1"], STANDARD)  # ty: ignore[invalid-argument-type] - wrong type on purpose


def test_r5_parse_never_emits_a_check_code():
    """R5: no parse of the corpus or of hostile text carries a check-family code or NOT_ADDRESS."""
    lines = (
        (family.ROOT / "tests" / "corpus" / "strings.txt").read_text(encoding="utf-8").splitlines()
    )
    texts = [*lines, *fuzz.hostile_texts(random.Random(1))]  # noqa: S311 - seeded test data
    banned = {*CHECK_FAMILY, "not_address"}
    emitted = {i.code.value for text in texts for a in Aspect for i in parse(text, bare=a).issues}
    assert not emitted & banned
    assert emitted  # the corpus does produce parse issues, so the test can see them


def test_f3_check_over_parse_values_with_issues():
    """F3: check over designations parse returned with issues gives issues and does not raise."""
    values = []
    for text in ["=CS-CV01", "-kx01", "+ER-Room 1", "%t1", "-k1-k1", "=", "-K1:1", "-K1;sig"]:
        value = parse(text, bare=P).value
        values.append(value.of if isinstance(value, Terminal | Signal) else value)
    designs = [v for v in values if isinstance(v, Designation)]
    assert isinstance(check(designs, STANDARD), tuple)
    assert check(designs, STANDARD)


def _table_sites(tree: ast.Module) -> list[str]:
    """Names `STANDARD` and imports of the tables package in one tree."""
    found = [t for _, t in family.identifiers(tree) if t == "STANDARD"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if "tables" in a.name.split(".")]
        elif isinstance(node, ast.ImportFrom):
            if "tables" in (node.module or "").split("."):
                found.append(node.module or "")
            found += [a.name for a in node.names if a.name == "tables"]
    return found


def test_r5_no_standard_or_tables_outside_scheme_and_init():
    """R5: `STANDARD` and `refdef.tables` appear in src/refdef only in scheme.py, __init__.py."""
    bad = [
        f"{path.name}: {site}"
        for path, tree in family.src_trees()
        if path.name not in {"scheme.py", "__init__.py"}
        for site in _table_sites(tree)
    ]
    assert not bad, bad
    assert any(_table_sites(tree) for path, tree in family.src_trees() if path.name == "scheme.py")


@pytest.mark.parametrize(
    "source",
    [
        "x = STANDARD",
        "from refdef.scheme import STANDARD",
        "import refdef.tables.standard",
        "from refdef.tables import standard",
        "from refdef import tables",
        "from . import tables",
        "y = refdef.STANDARD.classes",
    ],
)
def test_r5_the_ast_scan_sees_each_form(source):
    """R5: the scan finds a bare name, an attribute, an alias and each import form of the table."""
    assert _table_sites(ast.parse(source))


def test_r6_hook_rejects_a_code_outside_issuecode(monkeypatch):
    """R6: the conftest hook fails an issue built with a code that is not an IssueCode."""
    seen = issue_hook.install(monkeypatch)
    Issue("empty", "", "")  # ty: ignore[invalid-argument-type] - the wrong code on purpose
    with pytest.raises(AssertionError, match="outside IssueCode"):
        issue_hook.assert_codes(seen)
    seen.clear()
    issue_hook.assert_codes(seen)
    Issue(IssueCode.EMPTY, "", "")
    assert seen == [IssueCode.EMPTY]
    issue_hook.assert_codes(seen)
