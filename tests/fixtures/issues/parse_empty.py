"""R4: `parse` reports empty for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("", bare=Aspect.PRODUCT).issues
