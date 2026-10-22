"""R5: `check` reports never_letter for a barred letter."""

from refdef import STANDARD, Aspect, Designation, Issue, check

VIA = "check"
P = Aspect.PRODUCT


def issues() -> tuple[Issue, ...]:
    """Issues of a barred letter."""
    return check([Designation().child(P, "KI", 1)], STANDARD)
