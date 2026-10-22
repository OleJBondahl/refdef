"""Family text gate: the `## Family rules` body of RULES.md is exactly the agreed F1 to F17 text."""

import hashlib
import re
from pathlib import Path

import family

FAMILY_SHA256 = "ed5e17d8a572770db0e78d403cbb380667fc92a699452d2808aa62ec2b9f2bfd"
HEADING = "## Family rules"
BULLET = re.compile(r"^- \*\*F(\d+)\.\*\*")


def family_body(root: Path = family.ROOT) -> str:
    """The body of the family section: outer blanks stripped, joined with LF plus one final LF."""
    lines = (root / "RULES.md").read_bytes().decode("utf-8").splitlines()
    assert HEADING in lines, "RULES.md has no family section"
    rest = lines[lines.index(HEADING) + 1 :]
    section = []
    for line in rest:
        if line.startswith("## "):
            break
        section.append(line)
    return "\n".join(section).strip("\n") + "\n"


def check_family_rules(root: Path = family.ROOT) -> None:
    """Fail unless the bullets are F1 to F17 in order and the body hash is FAMILY_SHA256."""
    body = family_body(root)
    numbers = [int(m.group(1)) for line in body.splitlines() if (m := BULLET.match(line))]
    assert numbers == list(range(1, 18)), f"family bullets: {numbers}"
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == FAMILY_SHA256


def test_family_rules():
    check_family_rules()
