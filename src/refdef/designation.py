"""The designation: a tuple of levels and an optional top node."""

from dataclasses import dataclass

from refdef import _heads
from refdef.level import Aspect, Level

_NOT_IN_TOP = frozenset(">:;&")


@dataclass(frozen=True)
class Designation:
    """A tuple of levels and an optional top node, built by the constructor and `child` only.

    Join two through their levels; the empty designation is the root.
    """

    levels: tuple[Level, ...] = ()
    top: str = ""

    def __post_init__(self) -> None:
        """Validate the levels and the top; every violation raises TypeError."""
        if not isinstance(self.levels, tuple) or not all(isinstance(v, Level) for v in self.levels):
            msg = "levels must be a tuple of Level"
            raise TypeError(msg)
        if not isinstance(self.top, str):
            msg = "top must be str"
            raise TypeError(msg)
        if self.top != self.top.strip() or _NOT_IN_TOP & set(self.top):
            msg = "top must be stripped and hold none of > : ; &"
            raise TypeError(msg)

    def __str__(self) -> str:
        """The strict printed form, the same as `render(self)`."""
        from refdef._render import render  # render imports this module, so import late

        return render(self)

    def child(
        self, aspect: Aspect, code: str = "", number: int | None = None, label: str = ""
    ) -> Designation:
        """This designation with one more level at the end."""
        return Designation((*self.levels, Level(aspect, code, number, label)), self.top)

    def only(self, *aspects: Aspect) -> Designation:
        """The levels of the listed aspects, in order; the top is kept."""
        if not all(isinstance(a, Aspect) for a in aspects):
            msg = "aspects must be Aspect"
            raise TypeError(msg)
        return Designation(_heads.only(self.levels, aspects), self.top)

    def parent(self, aspect: Aspect | None = None) -> Designation:
        """Without the last level of `aspect` (of any aspect if None); self if there is none."""
        if aspect is not None and not isinstance(aspect, Aspect):
            msg = "aspect must be an Aspect or None"
            raise TypeError(msg)
        return Designation(_heads.without_last(self.levels, aspect), self.top)

    @property
    def last(self) -> Level | None:
        """The last level, or None for a designation without levels."""
        return self.levels[-1] if self.levels else None
