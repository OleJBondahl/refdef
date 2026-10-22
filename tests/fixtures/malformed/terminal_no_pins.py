"""R2: `Terminal(Designation(), ())` is a malformed call and raises TypeError."""

from refdef import Designation, Terminal


def build() -> object:
    """Build the malformed value."""
    return Terminal(Designation(), ())
