"""R2: `Terminal(Designation(), ['1'])` is a malformed call and raises TypeError."""

from refdef import Designation, Terminal


def build() -> object:
    """Build the malformed value."""
    return Terminal(Designation(), ["1"])  # ty: ignore[invalid-argument-type] - a malformed call on purpose
