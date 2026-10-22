"""The direct address of a PLC program (`%IX0.0`, `%QW4`, `%I*`) and a channel tag that pairs it."""

import re
from dataclasses import dataclass, replace
from enum import Enum

from refdef.issues import Issue, IssueCode, Parsed
from refdef.terminal import Terminal

__all__ = ["Address", "ChannelTag", "Memory", "Size", "parse_address"]

_MAX = 999_999_999
_DIGITS = 9
_ADDRESS = re.compile(r"%([IQM])([XBWDL]?)(\*|[0-9]+(?:\.[0-9]+)*)")


class Memory(Enum):
    """The memory area of an address: input, output or marker; the value is the letter."""

    INPUT = "I"
    OUTPUT = "Q"
    MARKER = "M"


class Size(Enum):
    """The access size of an address: none, bit, byte, word, double word or long word."""

    NONE = ""
    BIT = "X"
    BYTE = "B"
    WORD = "W"
    DWORD = "D"
    LWORD = "L"


def _is_index(value: object) -> bool:
    """True for an int (not a bool) from 0 to 999_999_999."""
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= _MAX


@dataclass(frozen=True)
class Address:
    """A direct address printed `%` memory size path; an empty path is the incomplete `%I*`.

    A path index is an int from 0 to 999_999_999; any other shape raises TypeError.
    """

    memory: Memory
    size: Size
    path: tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate the fields; every violation raises TypeError."""
        if not isinstance(self.memory, Memory) or not isinstance(self.size, Size):
            msg = "memory must be a Memory and size a Size"
            raise TypeError(msg)
        if not isinstance(self.path, tuple) or not all(map(_is_index, self.path)):
            msg = "path must be a tuple of ints from 0 to 999_999_999"
            raise TypeError(msg)

    def __str__(self) -> str:
        """The strict printed form."""
        return f"%{self.memory.value}{self.size.value}" + (".".join(map(str, self.path)) or "*")

    def as_bit(self) -> Address:
        """The one normalisation: a size-less dotted address gets the bit size; others are kept."""
        if self.size is Size.NONE and len(self.path) > 1:
            return replace(self, size=Size.BIT)
        return self


def parse_address(text: str) -> Parsed[Address | None]:
    """Read a direct address; text that is not one gives `None` and a NOT_ADDRESS issue."""
    if not isinstance(text, str):
        msg = "text must be a str"
        raise TypeError(msg)
    match = _ADDRESS.fullmatch(text.strip())
    if match is None:
        return Parsed(None, (Issue(IssueCode.NOT_ADDRESS, text, "not a direct address"),))
    memory, size, rest = match.groups()
    parts = [] if rest == "*" else rest.split(".")
    if any(len(part) > _DIGITS for part in parts):
        return Parsed(None, (Issue(IssueCode.NOT_ADDRESS, text, "an index of over nine digits"),))
    path = tuple(map(int, parts))
    return Parsed(Address(Memory(memory), Size(size), path), ())


@dataclass(frozen=True)
class ChannelTag:
    """A terminal with an optional address, printed as the terminal alone (`-KE1:DI03`)."""

    terminal: Terminal
    address: Address | None = None

    def __post_init__(self) -> None:
        """Validate the fields; every violation raises TypeError."""
        if not isinstance(self.terminal, Terminal):
            msg = "terminal must be a Terminal"
            raise TypeError(msg)
        if self.address is not None and not isinstance(self.address, Address):
            msg = "address must be None or an Address"
            raise TypeError(msg)

    def __str__(self) -> str:
        """The terminal text only."""
        return str(self.terminal)
