"""Reference designations as strict, typed, immutable values."""

from refdef._check import check
from refdef._parse import parse
from refdef._render import render
from refdef.designation import Designation
from refdef.issues import Issue, IssueCode, Parsed
from refdef.level import Aspect, Level
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
    "check",
    "parse",
    "render",
]
