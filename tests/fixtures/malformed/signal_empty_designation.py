"""R2: `Signal(Designation(), 'X')` is a malformed call and raises TypeError."""

from refdef import Designation, Signal


def build() -> object:
    """Build the malformed value."""
    return Signal(Designation(), "X")
