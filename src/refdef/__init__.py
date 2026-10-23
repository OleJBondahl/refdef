"""Reference designations as strict, typed, immutable values."""

from refdef._check import check
from refdef._parse import parse
from refdef._render import render
from refdef.designation import Designation
from refdef.issues import Issue, IssueCode, Parsed
from refdef.level import Aspect, Level
from refdef.numbering import allocate, lowest_free, number_group
from refdef.order import natural_key, sort_key
from refdef.scheme import STANDARD, ClassEntry, Scheme
from refdef.terminal import Signal, Terminal

__all__ = [
    "STANDARD",
    "Aspect",
    "ClassEntry",
    "Designation",
    "Issue",
    "IssueCode",
    "Level",
    "Parsed",
    "Scheme",
    "Signal",
    "Terminal",
    "allocate",
    "check",
    "lowest_free",
    "natural_key",
    "number_group",
    "parse",
    "render",
    "sort_key",
]
