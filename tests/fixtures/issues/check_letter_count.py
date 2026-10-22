"""R5: `check` reports letter_count for a four-letter code."""

from refdef import STANDARD, Aspect, Designation, Issue, check

VIA = "check"
P = Aspect.PRODUCT


def issues() -> tuple[Issue, ...]:
    """Issues of a four-letter code."""
    return check([Designation().child(P, "KEBX", 1)], STANDARD)
