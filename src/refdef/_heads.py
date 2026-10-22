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


def head(levels: tuple[Level, ...], aspect: Aspect) -> tuple[Level, ...]:
    """The levels of `aspect`, in order."""
    return tuple(level for level in levels if level.aspect is aspect)


def _aspects(levels: tuple[Level, ...]) -> tuple[Aspect, ...]:
    """The aspects present in `levels`, in order of first appearance."""
    return tuple(dict.fromkeys(level.aspect for level in levels))


def _shared(mine: tuple[Level, ...], other: tuple[Level, ...]) -> int:
    """The length of the common prefix of two level tuples."""
    count = 0
    for left, right in zip(mine, other, strict=False):
        if left != right:
            break
        count += 1
    return count


def within(levels: tuple[Level, ...], root: tuple[Level, ...]) -> bool:
    """True when the root head is a prefix of ours per shared aspect; a root sharing none fails."""
    shared = [a for a in _aspects(root) if a in _aspects(levels)]
    if root and not shared:
        return False
    return all(_shared(head(levels, a), head(root, a)) == len(head(root, a)) for a in shared)


def drop_heads(levels: tuple[Level, ...], root: tuple[Level, ...]) -> tuple[Level, ...]:
    """The levels without, per aspect, as many leading ones as the root's head holds."""
    left = {a: len(head(root, a)) for a in _aspects(root)}
    kept = []
    for level in levels:
        if left.get(level.aspect, 0) > 0:
            left[level.aspect] -= 1
        else:
            kept.append(level)
    return tuple(kept)


def common(first: tuple[Level, ...], *others: tuple[Level, ...]) -> tuple[Level, ...]:
    """Per aspect of `first`, the shortest head all share with it, in the order of `first`."""
    keep = {
        a: min([len(head(first, a)), *(_shared(head(first, a), head(o, a)) for o in others)])
        for a in _aspects(first)
    }
    kept = []
    for level in first:
        if keep[level.aspect] > 0:
            keep[level.aspect] -= 1
            kept.append(level)
    return tuple(kept)
