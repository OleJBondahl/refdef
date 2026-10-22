"""R5: `check` reports unknown_class for an unknown class."""

from refdef import STANDARD, Aspect, Designation, Issue, check

VIA = "check"
P = Aspect.PRODUCT


def issues() -> tuple[Issue, ...]:
    """Issues of an unknown class."""
    return check([Designation().child(P, "KX", 1)], STANDARD)
