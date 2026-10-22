"""R2: `Signal(None, 'X ')` is a malformed call and raises TypeError."""

from refdef import Signal


def build() -> object:
    """Build the malformed value."""
    return Signal(None, "X ")
