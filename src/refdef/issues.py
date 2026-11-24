"""Issues found while reading or checking reference designations."""

from dataclasses import dataclass
from enum import Enum


class IssueCode(Enum):
    """The 22 issue codes: the first 16 come from the readers, the last 6 from check.

    `RESERVED_LETTER` is advisory: a caller may treat it as a warning; it never refuses one.
    """

    EMPTY = "empty"
    NO_SIGN = "no_sign"
    EMPTY_LEVEL = "empty_level"
    EMPTY_TOP = "empty_top"
    WHITESPACE = "whitespace"
    LOWER_CASE = "lower_case"
    LEADING_ZERO = "leading_zero"
    ZERO_NUMBER = "zero_number"
    NUMBER_TOO_LARGE = "number_too_large"
    FREE_LABEL = "free_label"
    BAD_LABEL = "bad_label"
    DOT_LEVEL = "dot_level"
    EMPTY_PIN = "empty_pin"
    EMPTY_NAME = "empty_name"
    UNSUPPORTED_SUFFIX = "unsupported_suffix"
    NOT_ADDRESS = "not_address"
    ASPECT_OFF = "aspect_off"
    LETTER_COUNT = "letter_count"
    NEVER_LETTER = "never_letter"
    UNKNOWN_CLASS = "unknown_class"
    DUPLICATE = "duplicate"
    RESERVED_LETTER = "reserved_letter"


@dataclass(frozen=True)
class Issue:
    """One finding about a string or a designation: a code, the offending text, a short sentence."""

    code: IssueCode
    subject: str
    message: str


@dataclass(frozen=True)
class Parsed[T]:
    """A value read from text together with the issues the reader found."""

    value: T
    issues: tuple[Issue, ...]
