"""R6 hook helpers: record the code of every `Issue` built during a test."""

import functools
from typing import TYPE_CHECKING

from refdef.issues import Issue, IssueCode

if TYPE_CHECKING:
    import pytest

_ORIGINAL_INIT = Issue.__init__


def install(monkeypatch: pytest.MonkeyPatch) -> list[object]:
    """Patch `Issue.__init__` for the test; return the list its `code` arguments fill."""
    seen: list[object] = []

    @functools.wraps(_ORIGINAL_INIT)
    def record(self: Issue, code: object, subject: str, message: str) -> None:
        seen.append(code)
        _ORIGINAL_INIT(self, code, subject, message)  # ty: ignore[invalid-argument-type] - wrapped on purpose

    monkeypatch.setattr(Issue, "__init__", record)
    return seen


def assert_codes(seen: list[object]) -> None:
    """Fail when a recorded code is not an `IssueCode` member."""
    bad = [code for code in seen if not isinstance(code, IssueCode)]
    assert not bad, f"R6: issues built with a code outside IssueCode: {bad!r}"
