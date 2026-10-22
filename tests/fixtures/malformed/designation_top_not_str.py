"""R2: `Designation(top=1)` is a malformed call and raises TypeError."""

from refdef import Designation


def build() -> object:
    """Build the malformed value."""
    return Designation(top=1)  # ty: ignore[invalid-argument-type] - a malformed call on purpose
