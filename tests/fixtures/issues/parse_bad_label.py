"""R4: `parse` reports bad_label for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-a<b", bare=Aspect.PRODUCT).issues
