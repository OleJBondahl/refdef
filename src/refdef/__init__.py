"""Reference designations as strict, typed, immutable values."""

from refdef._parse import parse
from refdef._render import render
from refdef.designation import Designation
from refdef.issues import Issue, IssueCode, Parsed
from refdef.level import Aspect, Level
from refdef.numbering import allocate, number_group
from refdef.order import natural_key, sort_key
from refdef.terminal import Signal, Terminal

__all__ = [
    "Aspect",
    "Designation",
    "Issue",
    "IssueCode",
    "Level",
    "Parsed",
    "Signal",
    "Terminal",
    "allocate",
    "natural_key",
    "number_group",
    "parse",
    "render",
    "sort_key",
]
