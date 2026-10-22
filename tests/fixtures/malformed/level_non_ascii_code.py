"""R2: `Level(Aspect.PRODUCT, 'Å', 1)` is a malformed call and raises TypeError."""

from refdef import Aspect, Level


def build() -> object:
    """Build the malformed value."""
    return Level(Aspect.PRODUCT, "Å", 1)
