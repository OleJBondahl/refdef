"""The natural order of designations: numbers by value, text as text."""

import re
from collections.abc import Sequence
from typing import Any, NamedTuple

from refdef.designation import Designation
from refdef.level import Aspect

_RUNS = re.compile(r"[0-9]+|[^0-9]+")


class NaturalKey(NamedTuple):
    """The key `natural_key` returns: one key per digit or text run, then the raw text.

    It is a plain tuple, so keys compare and sort as before; `runs` and `text` name its two parts.
    """

    runs: tuple[tuple[int, int, str] | tuple[int, str], ...]
    text: str


def _run_key(run: str, *, case_sensitive: bool) -> tuple[int, int, str] | tuple[int, str]:
    if run.isascii() and run.isdigit():
        significant = run.lstrip("0")
        # (length, digits) orders like int(run) and never hits the int-from-text digit limit
        return (0, len(significant), significant)
    return (1, run if case_sensitive else run.lower())


def natural_key(text: str, *, case_sensitive: bool = True) -> NaturalKey:
    """A sort key: digit runs by value, text runs as text, numbers first, then the raw text."""
    if not isinstance(text, str):
        msg = "text must be str"
        raise TypeError(msg)
    runs = tuple(_run_key(run, case_sensitive=case_sensitive) for run in _RUNS.findall(text))
    return NaturalKey(runs, text)


def sort_key(
    d: Designation, *, aspects: Sequence[Aspect], case_sensitive: bool = True
) -> tuple[Any, ...]:
    """A sort key: per level the rank of its aspect in `aspects` and its natural key.

    Aspects not listed rank after the listed ones, in enum order. The top is not in the key.
    """
    if not isinstance(aspects, Sequence) or not all(isinstance(a, Aspect) for a in aspects):
        msg = "aspects must be a sequence of Aspect"
        raise TypeError(msg)
    order = [*aspects, *(a for a in Aspect if a not in aspects)]
    return tuple(
        (order.index(level.aspect), natural_key(level.text, case_sensitive=case_sensitive))
        for level in d.levels
    )
