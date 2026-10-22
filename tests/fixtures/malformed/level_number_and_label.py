"""R2: `Level(Aspect.PRODUCT, number=1, label='ER')` is a malformed call and raises TypeError."""

from refdef import Aspect, Level


def build() -> object:
    """Build the malformed value."""
    return Level(Aspect.PRODUCT, number=1, label="ER")
