"""R2: `Level(Aspect.PRODUCT, 'K1', 1)` is a malformed call and raises TypeError."""

from refdef import Aspect, Level


def build() -> object:
    """Build the malformed value."""
    return Level(Aspect.PRODUCT, "K1", 1)
