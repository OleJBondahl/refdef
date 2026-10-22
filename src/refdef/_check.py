"""The scheme rules: the one place that reads a scheme (R5)."""

from collections.abc import Iterable

from refdef.designation import Designation
from refdef.issues import Issue, IssueCode
from refdef.level import Level
from refdef.scheme import Scheme


def _level_issues(level: Level, scheme: Scheme) -> list[Issue]:
    """Aspect rule for every level; letter and class rules for coded levels only."""
    subject = level.aspect.value + level.text
    found = []
    if level.aspect not in scheme.aspects:
        found.append(
            Issue(
                IssueCode.ASPECT_OFF, subject, f"aspect {level.aspect.value} is off in the scheme"
            )
        )
    if not level.code:
        return found
    rule = scheme.letters
    if not rule.min_count <= len(level.code) <= rule.max_count:
        found.append(
            Issue(IssueCode.LETTER_COUNT, subject, f"{level.code} has an odd letter count")
        )
    if rule.never & set(level.code):
        found.append(Issue(IssueCode.NEVER_LETTER, subject, f"{level.code} uses a barred letter"))
    if scheme.classes.get(level.code) is None:
        found.append(Issue(IssueCode.UNKNOWN_CLASS, subject, f"{level.code} is not a known class"))
    return found


def check(designations: Iterable[Designation], scheme: Scheme) -> tuple[Issue, ...]:
    """Issues of the designations against `scheme`, in order; duplicates first for each one.

    Terminals and signals are not checked: pass their `of`.
    """
    if not isinstance(scheme, Scheme):
        msg = "scheme must be a Scheme"
        raise TypeError(msg)
    found: list[Issue] = []
    seen: set[str] = set()
    for design in designations:
        if not isinstance(design, Designation):
            msg = "designations must hold Designation"
            raise TypeError(msg)
        text = str(design)
        if text in seen:
            found.append(Issue(IssueCode.DUPLICATE, text, "designation used twice"))
        seen.add(text)
        for level in design.levels:
            found += _level_issues(level, scheme)
    return tuple(found)
