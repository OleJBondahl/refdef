"""R4: `parse` reports number_too_large for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-K1234567890", bare=Aspect.PRODUCT).issues
