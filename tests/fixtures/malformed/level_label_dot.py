"""R2: `Level(Aspect.PRODUCT, label='A.B')` is a malformed call and raises TypeError."""

from refdef import Aspect, Level


def build() -> object:
    """Build the malformed value."""
    return Level(Aspect.PRODUCT, label="A.B")
