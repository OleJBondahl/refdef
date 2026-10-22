"""R5: `check` reports duplicate for a designation used twice."""

from refdef import STANDARD, Aspect, Designation, Issue, check

VIA = "check"
P = Aspect.PRODUCT


def issues() -> tuple[Issue, ...]:
    """Issues of a designation used twice."""
    return check([Designation().child(P, "K", 1)] * 2, STANDARD)
