"""R6 hook: every issue any test produces has a code in `IssueCode`."""

from collections.abc import Iterator

import issue_hook
import pytest


@pytest.fixture(autouse=True)
def _issue_codes_are_issue_codes(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Record each `Issue` built in the test and check its code after the test."""
    seen = issue_hook.install(monkeypatch)
    yield
    issue_hook.assert_codes(seen)
