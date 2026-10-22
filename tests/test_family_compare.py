"""`scripts/family_compare.py` names each family file that differs or is missing elsewhere."""

import shutil
import subprocess
import sys
from pathlib import Path

import family

SCRIPT = family.ROOT / "scripts" / "family_compare.py"
FILES = ["a.txt", "sub/b.txt"]


def _tree(root: Path, extra: str = "") -> Path:
    for name in FILES:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(f"{name}\n{extra if name == 'a.txt' else ''}", encoding="utf-8")
    return root


def _pair(tmp_path: Path) -> tuple[Path, Path]:
    here = _tree(tmp_path / "here")
    (here / "scripts").mkdir()
    shutil.copy2(SCRIPT, here / "scripts" / SCRIPT.name)
    (here / "scripts" / "family_files.txt").write_text("# list\n\na.txt\nsub/b.txt\n")
    return here, _tree(tmp_path / "other")


def run(here: Path, other: Path) -> tuple[int, str]:
    done = subprocess.run(  # noqa: S603 - runs a copy of the repository's own script
        [sys.executable, str(here / "scripts" / SCRIPT.name), str(other)],
        capture_output=True,
        text=True,
        check=False,
    )
    return done.returncode, done.stdout


def test_identical_trees_report_the_count(tmp_path):
    here, other = _pair(tmp_path)
    assert run(here, other) == (0, "family: identical (2 files)\n")


def test_one_byte_of_difference_names_the_file(tmp_path):
    here, other = _pair(tmp_path)
    (other / "sub" / "b.txt").write_text("sub/b.txt\nx", encoding="utf-8")
    assert run(here, other) == (1, "family: DIFFERENT sub/b.txt\n")


def test_a_missing_file_fails(tmp_path):
    here, other = _pair(tmp_path)
    (other / "a.txt").unlink()
    assert run(here, other) == (1, "family: DIFFERENT a.txt\n")


def test_the_list_names_itself():
    listing = family.ROOT / "scripts" / "family_files.txt"
    assert "scripts/family_files.txt" in listing.read_text(encoding="utf-8").split()
