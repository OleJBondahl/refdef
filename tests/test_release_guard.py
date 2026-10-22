"""F11 gate: `scripts/release_guard.py` fails an API change with no changelog line or bump."""

import re
import subprocess
import sys
from pathlib import Path

import family
import pytest

GUARD = family.ROOT / "scripts" / "release_guard.py"
OLD = "## door\nfoo(a)\nclass Bar(b)\n    doc\n"
NEW = "## door\nfoo(a, c)\nclass Bar(b)\n    doc\n"
GONE = "## door\nfoo(a)\n"
LOG = "# Changelog\n\n## Unreleased\n{}\n## 0.1.0\n\n- first\n"


def _git(repo: Path, *args: str) -> None:
    argv = ["git", *args]
    subprocess.run(argv, cwd=repo, check=True, capture_output=True)  # noqa: S603 - test git


def _project(version: str) -> str:
    return f'[project]\nname = "x"\nversion = "{version}"\n'


def _write(repo: Path, snapshot: str, line: str = "", version: str = "0.1.0") -> None:
    (repo / "pyproject.toml").write_text(_project(version), encoding="utf-8")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "api-snapshot.txt").write_text(snapshot, encoding="utf-8")
    (repo / "docs" / "CHANGELOG.md").write_text(LOG.format(line), encoding="utf-8")


@pytest.fixture
def repo(tmp_path):
    """A temporary git repository holding the three files, committed, not yet tagged."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.name", "T")
    _git(tmp_path, "config", "user.email", "t@example.org")
    _write(tmp_path, OLD)
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def _tag(repo: Path) -> None:
    _git(repo, "tag", "v0.1.0")


def run(repo: Path) -> tuple[int, str]:
    done = subprocess.run(  # noqa: S603 - runs the repository's own script
        [sys.executable, str(GUARD)], cwd=repo, capture_output=True, text=True, check=False
    )
    return done.returncode, done.stdout


def test_no_tag_passes(repo):
    assert run(repo)[0] == 0


def test_tagged_and_unchanged_passes(repo):
    _tag(repo)
    assert run(repo) == (0, "release_guard: ok (since v0.1.0)\n")


def test_a_changed_snapshot_with_an_empty_unreleased_fails(repo):
    _tag(repo)
    _write(repo, NEW)
    code, out = run(repo)
    assert code == 1
    assert "Unreleased" in out


def test_a_changed_snapshot_with_a_changelog_line_passes(repo):
    _tag(repo)
    _write(repo, NEW, line="\n- foo takes c\n")
    assert run(repo)[0] == 0


def test_a_removed_name_with_the_same_version_fails(repo):
    _tag(repo)
    _write(repo, GONE, line="\n- Bar removed\n")
    code, out = run(repo)
    assert code == 1
    assert "Bar" in out


def test_a_removed_name_with_a_bumped_version_passes(repo):
    _tag(repo)
    _write(repo, GONE, line="\n- Bar removed\n", version="0.2.0")
    assert run(repo)[0] == 0


def test_release_recipe_opens_a_fresh_unreleased(tmp_path):
    recipe = (family.ROOT / "justfile").read_text(encoding="utf-8").splitlines()
    step = next(line.strip() for line in recipe if "CHANGELOG.md" in line and "sed" in line)
    log = tmp_path / "docs" / "CHANGELOG.md"
    log.parent.mkdir()
    log.write_text("# Changelog\n\n## Unreleased\n\n- new\n\n## 0.1.0 (d)\n", encoding="utf-8")
    script = step.replace("{{V}}", "0.2.0")
    subprocess.run(["bash", "-c", script], cwd=tmp_path, check=True)  # noqa: S603, S607 - the recipe's own sed line
    lines = log.read_text(encoding="utf-8").splitlines()
    assert lines[:3] == ["# Changelog", "", "## Unreleased"]
    assert lines[3] == ""
    assert re.fullmatch(r"## 0\.2\.0 \(\d{4}-\d\d-\d\d\)", lines[4])
    assert "- new" in lines[5:]
