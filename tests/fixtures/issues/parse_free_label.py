"""R4: `parse` reports free_label for a hostile string."""

from refdef import Aspect, Issue, parse

VIA = "parse"


def issues() -> tuple[Issue, ...]:
    """Issues of the hostile string."""
    return parse("-Room 1", bare=Aspect.PRODUCT).issues
