"""Compare the shared family files of this repository with another checkout or remote.

Usage:
    uv run python scripts/family_compare.py OTHER_DIR_OR_URL
"""

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def listed(root: Path) -> list[str]:
    """The repo-relative paths in `scripts/family_files.txt`, without blanks and comments."""
    lines = (root / "scripts" / "family_files.txt").read_text(encoding="utf-8").splitlines()
    return [s for s in (line.strip() for line in lines) if s and not s.startswith("#")]


def digest(path: Path) -> str | None:
    """The SHA-256 of a file, or None when it is missing."""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def different(paths: list[str], here: Path, other: Path) -> list[str]:
    """The paths whose file is missing on either side or differs."""
    return [p for p in paths if digest(here / p) is None or digest(here / p) != digest(other / p)]


def compare(other: Path) -> int:
    """Print the verdict for `other` against this repository; return the exit code."""
    paths = listed(ROOT)
    bad = different(paths, ROOT, other)
    for path in bad:
        sys.stdout.write(f"family: DIFFERENT {path}\n")
    if not bad:
        sys.stdout.write(f"family: identical ({len(paths)} files)\n")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    """Clone a URL or git remote into a temporary folder, or use a directory as given."""
    target = argv[0]
    if "://" not in target and not target.endswith(".git"):
        return compare(Path(target))
    with tempfile.TemporaryDirectory() as tmp:
        argv = ["git", "clone", "--depth", "1", target, tmp]
        subprocess.run(argv, check=True, capture_output=True)  # noqa: S603 - fixed git argv
        return compare(Path(tmp))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
