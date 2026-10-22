"""R4: `parse` reports lower_case for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-k1", bare=Aspect.PRODUCT).issues
