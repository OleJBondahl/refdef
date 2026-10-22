"""R4: `parse` reports empty_pin for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-K1:", bare=Aspect.PRODUCT).issues
