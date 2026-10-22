"""F14 gate: MIT licence file, MIT in pyproject, no restrictive licence on a shipped table."""

import re
from pathlib import Path

import family

HEADER = re.compile(r"^# Licence: (.+?)\s*$", re.MULTILINE)
RESTRICTIVE = re.compile(
    r"(?<![A-Za-z])(?:SA|NC)(?![A-Za-z])|share-?alike|non-?commercial|GPL|ODbL", re.IGNORECASE
)


def check_licence(root: Path = family.ROOT) -> None:
    """Fail unless LICENSE and pyproject say MIT and no table header names a restrictive licence."""
    text = (root / "LICENSE").read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert "Permission is hereby granted, free of charge" in text
    assert family.pyproject(root)["project"]["license"] == "MIT"
    tables = sorted((root / "src" / family.lib_name(root) / "tables").glob("*.py"))
    for path in tables:
        for value in HEADER.findall(path.read_text(encoding="utf-8")):
            assert not RESTRICTIVE.search(value), f"{path.name}: licence {value!r}"


def test_licence():
    check_licence()
