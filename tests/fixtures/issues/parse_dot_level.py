"""R4: `parse` reports dot_level for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-K1.2", bare=Aspect.PRODUCT).issues
