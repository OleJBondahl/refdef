"""R2: `Designation(top=' T')` is a malformed call and raises TypeError."""

from refdef import Designation


def build() -> object:
    """Build the malformed value."""
    return Designation(top=" T")
