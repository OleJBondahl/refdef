"""R4: `parse` reports zero_number for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-K0", bare=Aspect.PRODUCT).issues
