"""One step of a reference designation: its aspect, class letters, number or label."""

import re
from dataclasses import dataclass
from enum import Enum

MAX_NUMBER = 999_999_999
_NOT_IN_LABEL = frozenset("=-+%#:;&<>.")
_CODED = re.compile(r"([A-Za-z]*)([0-9]+)")
_LETTERS = re.compile(r"[A-Z]*")


class Aspect(Enum):
    """The tree a level belongs to; the value is its sign.

    The first three are on in the shipped scheme; declaration order is the rank tie-break.
    """

    FUNCTION = "="
    PRODUCT = "-"
    LOCATION = "+"
    TYPE = "%"
    OTHER = "#"
    ASSIGNMENT = "=="
    SITE = "++"


def coded_split(body: str) -> tuple[str, str] | None:
    """Split `body` into letters and digits when it is shaped like a code, else None.

    The digits must be worth 1 to 999_999_999; `K0` and `K1234567890` are not codes.
    """
    hit = _CODED.fullmatch(body)
    if hit is None:
        return None
    letters, digits = hit.groups()
    if len(digits.lstrip("0")) > len(str(MAX_NUMBER)) or not 1 <= int(digits) <= MAX_NUMBER:
        return None
    return letters, digits


def _check_types(aspect: object, code: object, label: object) -> None:
    if not isinstance(aspect, Aspect):
        msg = "aspect must be an Aspect"
        raise TypeError(msg)
    if not isinstance(code, str) or not isinstance(label, str):
        msg = "code and label must be str"
        raise TypeError(msg)


def _check_number(number: object) -> None:
    if number is None:
        return
    if not isinstance(number, int) or isinstance(number, bool):
        msg = "number must be an int or None"
        raise TypeError(msg)
    if not 1 <= number <= MAX_NUMBER:
        msg = f"number must be 1..{MAX_NUMBER}"
        raise TypeError(msg)


def _check_label(label: str) -> None:
    if label != label.strip():
        msg = "label must not have outer whitespace"
        raise TypeError(msg)
    if _NOT_IN_LABEL & set(label):
        msg = "label must not hold any of = - + % # : ; & < > ."
        raise TypeError(msg)
    if coded_split(label) is not None:
        msg = "label must not be shaped like a code (letters and a number)"
        raise TypeError(msg)


@dataclass(frozen=True)
class Level:
    """One step in a tree: letters and a number (`-K2`), a number alone (`+3`) or a label (`+ER`).

    Letters are upper case and need a number; a label is never code-shaped. Else TypeError.
    """

    aspect: Aspect
    code: str = ""
    number: int | None = None
    label: str = ""

    def __post_init__(self) -> None:
        """Validate the shape; every violation raises TypeError naming the field."""
        _check_types(self.aspect, self.code, self.label)
        _check_number(self.number)
        coded = bool(self.code) or self.number is not None
        if coded == bool(self.label):
            msg = "a level is letters and a number, a number alone, or a label"
            raise TypeError(msg)
        if coded:
            self._check_coded()
        else:
            _check_label(self.label)

    def _check_coded(self) -> None:
        if _LETTERS.fullmatch(self.code) is None:
            msg = "code must be upper-case ASCII letters A-Z only"
            raise TypeError(msg)
        if self.number is None:
            msg = "code letters need a number"
            raise TypeError(msg)

    @property
    def text(self) -> str:
        """The level without its sign: the label, or the letters and the number."""
        return self.label or f"{self.code}{self.number}"
