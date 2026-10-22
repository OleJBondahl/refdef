"""R5: `check` reports aspect_off for a type-aspect level."""

from refdef import STANDARD, Aspect, Designation, Issue, check

VIA = "check"
P = Aspect.PRODUCT


def issues() -> tuple[Issue, ...]:
    """Issues of a type-aspect level."""
    return check([Designation().child(Aspect.TYPE, "T", 1)], STANDARD)
