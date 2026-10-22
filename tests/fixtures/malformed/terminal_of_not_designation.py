"""R2: `Terminal('-K1', ('1',))` is a malformed call and raises TypeError."""

from refdef import Terminal


def build() -> object:
    """Build the malformed value."""
    return Terminal("-K1", ("1",))  # ty: ignore[invalid-argument-type] - a malformed call on purpose
