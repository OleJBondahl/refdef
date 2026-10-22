"""R2: `Signal('-K1', 'X')` is a malformed call and raises TypeError."""

from refdef import Signal


def build() -> object:
    """Build the malformed value."""
    return Signal("-K1", "X")  # ty: ignore[invalid-argument-type] - a malformed call on purpose
