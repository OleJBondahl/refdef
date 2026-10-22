"""R2: `Level(Aspect.PRODUCT, 'K', 1.0)` is a malformed call and raises TypeError."""

from refdef import Aspect, Level


def build() -> object:
    """Build the malformed value."""
    return Level(Aspect.PRODUCT, "K", 1.0)  # ty: ignore[invalid-argument-type] - a malformed call on purpose
