"""Family gate wrappers."""

import dataclasses

import family
import pytest

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
