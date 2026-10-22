"""R2: `Level('-', 'K', 1)` is a malformed call and raises TypeError."""

from refdef import Level


def build() -> object:
    """Build the malformed value."""
    return Level("-", "K", 1)  # ty: ignore[invalid-argument-type] - a malformed call on purpose
