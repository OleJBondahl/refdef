"""R2: `Designation([Level(Aspect.PRODUCT, 'K', 1)])` is a malformed call and raises TypeError."""

from refdef import Aspect, Designation, Level


def build() -> object:
    """Build the malformed value."""
    return Designation([Level(Aspect.PRODUCT, "K", 1)])  # ty: ignore[invalid-argument-type] - a malformed call on purpose
