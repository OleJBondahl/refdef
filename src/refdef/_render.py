"""The strict printer and its three explicit options."""

from collections.abc import Collection, Mapping

from refdef.designation import Designation
from refdef.level import Aspect, Level


def _check(d: object, pad: object, dotted: object, bare: object) -> None:
    if not isinstance(d, Designation):
        msg = "render takes a Designation"
        raise TypeError(msg)
    if pad is not None and not (
        isinstance(pad, Mapping)
        and all(isinstance(k, str) and type(v) is int and v >= 0 for k, v in pad.items())
    ):
        msg = "pad must be a mapping of str to non-negative int, or None"
        raise TypeError(msg)
    if not isinstance(dotted, Collection) or not all(isinstance(a, Aspect) for a in dotted):
        msg = "dotted must be a collection of Aspect"
        raise TypeError(msg)
    if not isinstance(bare, bool):
        msg = "bare must be a bool"
        raise TypeError(msg)


def _is_sub(level: Level, previous: Level | None) -> bool:
    """A number-only level right after a level of the same aspect."""
    return (
        previous is not None
        and previous.aspect is level.aspect
        and level.code == ""
        and level.number is not None
    )


def _text(level: Level, pad: Mapping[str, int]) -> str:
    if level.code and level.code in pad:
        return level.code + str(level.number).zfill(pad[level.code])
    return level.text


def render(
    d: Designation,
    *,
    pad: Mapping[str, int] | None = None,
    dotted: Collection[Aspect] = (),
    bare: bool = False,
) -> str:
    """Print a designation; `pad`, `dotted` and `bare` are the explicit dialects, none is `str(d)`.

    `pad={"W": 4}` gives `-W0001`; `dotted=(P,)` gives `-W25.1`; `bare=True` omits the first sign.
    """
    _check(d, pad, dotted, bare)
    widths = pad or {}
    out = [f"<{d.top}>"] if d.top else []
    previous = None
    for index, level in enumerate(d.levels):
        sign = level.aspect.value
        if _is_sub(level, previous) and level.aspect in dotted:
            sign = "."
        out.append(("" if bare and index == 0 else sign) + _text(level, widths))
        previous = level
    return "".join(out)
