"""R10: the class table is versioned; its entries must match the hash stored beside the version."""

import hashlib

from refdef import STANDARD
from refdef.tables import standard


def entries_digest(entries: tuple[tuple[str, str], ...]) -> str:
    """SHA-256 of `code TAB title NEWLINE` for each entry, as UTF-8 (M15)."""
    return hashlib.sha256("".join(f"{c}\t{t}\n" for c, t in entries).encode("utf-8")).hexdigest()


def test_r10_stored_hash_matches_the_entries():
    """R10: editing an entry without regenerating (and bumping the version) breaks this."""
    assert entries_digest(standard.ENTRIES) == standard.ENTRIES_SHA256


def test_r10_hash_moves_with_any_entry():
    """R10: the digest differs for a changed title, a dropped entry and a changed code."""
    base = standard.ENTRIES
    first = base[0]
    changed = ((first[0], first[1] + "s"), *base[1:])
    assert entries_digest(changed) != entries_digest(base)
    assert entries_digest(base[1:]) != entries_digest(base)
    assert entries_digest((("Z", first[1]), *base[1:])) != entries_digest(base)


def test_r10_version_line_is_the_tables_own():
    """R10: the scheme's table holds the generated version, name, depth and entries."""
    table = STANDARD.classes
    assert (table.name, table.version, table.depth) == (
        standard.NAME,
        standard.VERSION,
        standard.DEPTH,
    )
    assert table.version == "1"
    assert tuple((e.code, e.title) for e in table.entries) == standard.ENTRIES
