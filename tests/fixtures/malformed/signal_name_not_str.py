"""R2: `Signal(None, 3)` is a malformed call and raises TypeError."""

from refdef import Signal


def build() -> object:
    """Build the malformed value."""
    return Signal(None, 3)  # ty: ignore[invalid-argument-type] - a malformed call on purpose
