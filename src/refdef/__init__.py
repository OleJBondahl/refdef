"""Reference designations as strict, typed, immutable values."""

from refdef._parse import parse
from refdef._render import render
from refdef.designation import Designation
from refdef.issues import Issue, IssueCode, Parsed
from refdef.level import Aspect, Level
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
    "parse",
    "render",
]
