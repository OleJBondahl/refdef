"""F17 gate: no tracked text file holds a word whose digest is in `APPLICATION_HASHES`."""

from pathlib import Path

import family


def check_standalone(root: Path = family.ROOT) -> None:
    """Fail naming the file and the digest, never the word."""
    found = []
    for path in family.tracked(root):
        text = family.read_text_or_none(path)
        if text is None:
            continue
        digests = {family.digest(word) for word in set(family.WORD.findall(text))}
        found += [
            f"{path.relative_to(root)}: {d}" for d in sorted(digests & family.APPLICATION_HASHES)
        ]
    assert not found, "application name digests found: " + "; ".join(found)


def test_standalone():
    assert len(family.APPLICATION_HASHES) >= 1
    check_standalone()
