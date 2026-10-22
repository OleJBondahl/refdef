"""The scheme a check reads: aspects that are on, a letter rule and a class table."""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cached_property

from refdef.level import Aspect
from refdef.tables import standard as _standard


@dataclass(frozen=True)
class LetterRule:
    """How many letters a code has and which letters never appear."""

    min_count: int = 1
    max_count: int = 3
    never: frozenset[str] = frozenset("IO")


@dataclass(frozen=True)
class ClassEntry:
    """One class code with its title, the typical device of the class."""

    code: str
    title: str


@dataclass(frozen=True)
class ClassTable:
    """Versioned class entries; `depth` is how many leading letters of a code are looked up."""

    name: str
    version: str
    depth: int
    entries: tuple[ClassEntry, ...]

    @cached_property
    def index(self) -> dict[str, ClassEntry]:
        """The entries by code, built once."""
        return {entry.code: entry for entry in self.entries}

    def get(self, code: str) -> ClassEntry | None:
        """The entry for the first `depth` letters of `code`, or None; no shorter fallback."""
        return self.index.get(code[: self.depth])


@dataclass(frozen=True)
class Scheme:
    """What `check` tests against: aspects on, a letter rule and a class table.

    `STANDARD` is the shipped scheme: `= - +` on, 1-3 letters without I and O, a versioned table.
    """

    name: str
    aspects: frozenset[Aspect]
    letters: LetterRule
    classes: ClassTable

    def extend(self, *entries: ClassEntry, aspects: Iterable[Aspect] = ()) -> Scheme:
        """A new scheme with `entries` overlaid by code (later wins) and `aspects` turned on."""
        merged = {entry.code: entry for entry in (*self.classes.entries, *entries)}
        table = replace(self.classes, entries=tuple(merged.values()))
        return replace(self, aspects=self.aspects | frozenset(aspects), classes=table)


_TABLE = ClassTable(
    _standard.NAME,
    _standard.VERSION,
    _standard.DEPTH,
    tuple(ClassEntry(code, title) for code, title in _standard.ENTRIES),
)
STANDARD = Scheme(
    "standard",
    frozenset({Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION}),
    LetterRule(),
    _TABLE,
)
