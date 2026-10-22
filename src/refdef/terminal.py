"""A terminal (`-K1:13`) and a signal (`-K1;SYSTEM_CAN_L`) of a designation."""

from dataclasses import dataclass

from refdef.designation import Designation


def _stripped(text: object, banned: str) -> bool:
    """True when `text` is a non-empty str without outer whitespace and without `banned`."""
    if not isinstance(text, str) or not text or text != text.strip():
        return False
    return not any(char in text for char in banned)


@dataclass(frozen=True)
class Terminal:
    """A designation and the pins on it, printed `of:pin:pin`.

    At least one pin; each is stripped, non-empty and without `:`. Pins are opaque text.
    """

    of: Designation
    pins: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate the designation and the pins; every violation raises TypeError."""
        if not isinstance(self.of, Designation):
            msg = "of must be a Designation"
            raise TypeError(msg)
        if not isinstance(self.pins, tuple) or not self.pins:
            msg = "pins must be a non-empty tuple of str"
            raise TypeError(msg)
        if not all(_stripped(pin, ":") for pin in self.pins):
            msg = "each pin must be stripped, non-empty and without ':'"
            raise TypeError(msg)

    def __str__(self) -> str:
        """The strict printed form."""
        return ":".join((str(self.of), *self.pins))

    def relative_to(self, root: Designation) -> Terminal:
        """The terminal with its designation made relative to `root`; the pins are kept."""
        return Terminal(self.of.relative_to(root), self.pins)


@dataclass(frozen=True)
class Signal:
    """A signal name on a designation, printed `of;name`; `of` is None for a bare name.

    The name is stripped and non-empty and may hold `: ; &`. It is opaque text.
    """

    of: Designation | None
    name: str

    def __post_init__(self) -> None:
        """Validate the designation and the name; every violation raises TypeError."""
        if self.of is not None and (
            not isinstance(self.of, Designation) or not (self.of.levels or self.of.top)
        ):
            msg = "of must be None or a Designation with a level or a top"
            raise TypeError(msg)
        if not _stripped(self.name, ""):
            msg = "name must be a stripped, non-empty str"
            raise TypeError(msg)

    def __str__(self) -> str:
        """The strict printed form."""
        return (str(self.of) if self.of is not None else "") + ";" + self.name

    def relative_to(self, root: Designation) -> Signal:
        """The signal with its designation made relative to `root`; None if nothing is left."""
        if self.of is None:
            return self
        rest = self.of.relative_to(root)
        return Signal(rest if rest.levels or rest.top else None, self.name)
