"""Helpers on tuples of levels; no Designation import, so no import cycle."""

from refdef.level import Aspect, Level


def only(levels: tuple[Level, ...], aspects: tuple[Aspect, ...]) -> tuple[Level, ...]:
    """The levels whose aspect is listed, in order."""
    return tuple(level for level in levels if level.aspect in aspects)


def without_last(levels: tuple[Level, ...], aspect: Aspect | None) -> tuple[Level, ...]:
    """The levels without the last one of `aspect` (of any aspect if None); unchanged if none."""
    for index in range(len(levels) - 1, -1, -1):
        if aspect is None or levels[index].aspect is aspect:
            return levels[:index] + levels[index + 1 :]
    return levels
