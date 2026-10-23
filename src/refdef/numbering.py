"""Numbering: the lowest free number for a class, and a group of them in order."""

from collections.abc import Collection, Sequence

from refdef.level import Aspect, Level


def _check_first(first: int) -> None:
    if not isinstance(first, int) or isinstance(first, bool) or first < 1:
        msg = "first must be an int of at least 1"
        raise TypeError(msg)


def allocate(
    aspect: Aspect,
    code: str,
    taken: Collection[Level],
    reserved: Collection[Level] = (),
    *,
    first: int = 1,
) -> int:
    """The smallest number from `first` for which `Level(aspect, code, n)` is in neither collection.

    `first` below 1 is a TypeError. Nothing is stored: the caller passes what is taken.
    """
    _check_first(first)
    number = first
    while Level(aspect, code, number) in taken or Level(aspect, code, number) in reserved:
        number += 1
    return number


def lowest_free(taken: Collection[int], reserved: Collection[int] = (), *, first: int = 1) -> int:
    """The smallest number from `first` that is in neither `taken` nor `reserved`.

    `reserved` is never handed out; the caller stores it. `first` below 1 is a TypeError.
    """
    _check_first(first)
    number = first
    while number in taken or number in reserved:
        number += 1
    return number


def number_group(
    aspect: Aspect,
    codes: Sequence[str],
    taken: Collection[Level] = (),
    reserved: Collection[Level] = (),
) -> tuple[Level, ...]:
    """One level per code, each numbered after the earlier ones; `taken` is not changed."""
    used = set(taken)
    out: list[Level] = []
    for code in codes:
        level = Level(aspect, code, allocate(aspect, code, used, reserved))
        used.add(level)
        out.append(level)
    return tuple(out)
