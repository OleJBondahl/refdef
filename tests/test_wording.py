"""F7 wording gate and the docs hygiene rule: no standard cited, no em-dash in tracked docs."""

import re
from pathlib import Path

import family

BODY = r"\b(?:(?:IEC|ISO|IEEE|ANSI|NFPA|VDE|NEK|DIN|CSA)(?: |-)?|(?:EN|UL|BS|JIS)(?: |-))\d"
CLAUSE = r"\b(?i:clause|subclause|annex)\s+[A-Z0-9]"
YEAR = (
    r"\b(?i:edition|ed\.)\s*(?:19|20)\d\d\b"
    r"|\b(?:19|20)\d\d\s+(?i:edition)\b"
    r"|[A-Za-z0-9)]:(?:19|20)\d\d\b"
    r"|\b(?i:table|scheme)\s+[A-Za-z0-9.]{1,8}\s*[,(]\s*(?:19|20)\d\d\b(?!-)"
)
PATTERNS = tuple(re.compile(p) for p in (BODY, CLAUSE, YEAR))

CREDIT_START = "<!-- credit:start -->"
CREDIT_END = "<!-- credit:end -->"
HEADER = re.compile(r"^# Open source: (.+?)\s*$", re.MULTILINE)
EM_DASH = chr(0x2014)

HITS = (
    "IEC 61131",
    "EN 50005",
    "UL 508",
    "DIN 43880",
    "ISO-9001",
    "clause 4.2",
    "Annex B",
    "edition 2013",
    "61131-1:2013",
    "Table 5 (2013)",
)
MISSES = (
    "AC-3",
    "AC_3",
    "AC_3E",
    "gG",
    "gL",
    "aM",
    "M12",
    "IP67",
    "E12",
    "PL_D",
    "DIN_35",
    "VDE",
    "SIL_1",
    "RJ45",
    "C10A",
    "2000",
    "2026-10-22",
    "-BS1",
    "-UL1",
    "-EN1",
)


def credit_block(readme: str) -> str:
    """The text between the credit markers; the markers must each occur exactly once."""
    assert readme.count(CREDIT_START) == 1, "README needs exactly one credit start marker"
    assert readme.count(CREDIT_END) == 1, "README needs exactly one credit end marker"
    _head, rest = readme.split(CREDIT_START)
    block, _tail = rest.split(CREDIT_END)
    return block


def without_credit(readme: str) -> str:
    """The README text with the credit block cut out."""
    credit_block(readme)
    head, rest = readme.split(CREDIT_START)
    return head + rest.split(CREDIT_END)[1]


def scanned(root: Path) -> list[tuple[Path, str]]:
    """The (path, text) pairs F7 scans, with the README credit block removed."""
    paths = sorted((root / "src").rglob("*.py"))
    for suffix in ("*.md", "*.txt"):
        paths += sorted((root / "docs").rglob(suffix))
    paths.append(root / "README.md")
    pairs = [(path, path.read_text(encoding="utf-8")) for path in paths if path.is_file()]
    return [(p, without_credit(t) if p == root / "README.md" else t) for p, t in pairs]


def check_wording(root: Path = family.ROOT) -> None:
    """Fail when a scanned file cites a standard body, a clause or an edition year."""
    found = [
        f"{path.relative_to(root)}: {match.group(0)!r}"
        for path, text in scanned(root)
        for pattern in PATTERNS
        for match in pattern.finditer(text)
    ]
    assert not found, "standard wording: " + "; ".join(found)


def check_credits(root: Path = family.ROOT) -> None:
    """Fail unless the README credit block exists once and names every table source."""
    block = credit_block((root / "README.md").read_text(encoding="utf-8"))
    tables = sorted((root / "src" / family.lib_name(root) / "tables").glob("*.py"))
    for path in tables:
        for name in HEADER.findall(path.read_text(encoding="utf-8")):
            assert name in block, f"{path.name}: source {name!r} missing from the credit block"


def check_em_dash(root: Path = family.ROOT) -> None:
    """Fail when a tracked .md or .txt file holds an em-dash."""
    bad = [
        str(path.relative_to(root))
        for path in family.tracked(root)
        if path.suffix in {".md", ".txt"} and EM_DASH in path.read_text(encoding="utf-8")
    ]
    assert not bad, f"em-dash in: {bad}"


def test_standards_not_cited():
    check_wording()


def test_pattern_samples():
    for sample in HITS:
        assert any(p.search(sample) for p in PATTERNS), sample
    for sample in MISSES:
        assert not any(p.search(sample) for p in PATTERNS), sample


def test_credit_block():
    check_credits()


def test_no_em_dash():
    check_em_dash()
