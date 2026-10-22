"""F12 gate: `scripts/design_guard.py` fails a review-path commit with no Design-review trailer."""

import subprocess
import sys
from pathlib import Path

import family
import pytest

GUARD = family.ROOT / "scripts" / "design_guard.py"
CONFIG = '[tool.family]\nreview_paths = ["RULES.md", "src/x/tables/"]\n'
ZEROS = "0" * 40


def _git(repo: Path, *args: str) -> str:
    argv = ["git", *args]
    done = subprocess.run(argv, cwd=repo, check=True, capture_output=True, text=True)  # noqa: S603 - test git
    return done.stdout.strip()


def commit(repo: Path, path: str, message: str = "change") -> str:
    """Write `path`, commit it with `message`; return the commit sha."""
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(message + _git(repo, "rev-list", "--all", "--count"), encoding="utf-8")
    _git(repo, "add", path)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    """A repository whose first commit holds only `pyproject.toml` with the review paths."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.name", "T")
    _git(tmp_path, "config", "user.email", "t@example.org")
    (tmp_path / "pyproject.toml").write_text(CONFIG, encoding="utf-8")
    _git(tmp_path, "add", "pyproject.toml")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def run(repo: Path, *base: str) -> tuple[int, str]:
    done = subprocess.run(  # noqa: S603 - runs the repository's own script
        [sys.executable, str(GUARD), *base], cwd=repo, capture_output=True, text=True, check=False
    )
    return done.returncode, done.stdout


def test_a_commit_off_the_review_paths_passes(repo):
    commit(repo, "src/x/other.py")
    assert run(repo) == (0, "design_guard: ok\n")


def test_a_review_path_without_a_trailer_fails(repo):
    sha = commit(repo, "RULES.md")
    code, out = run(repo)
    assert code == 1
    assert sha[:9] in out


def test_a_trailer_in_the_last_paragraph_passes(repo):
    commit(repo, "RULES.md", "edit rules\n\nwhy\n\nDesign-review: D-1")
    assert run(repo) == (0, "design_guard: ok\n")


def test_a_file_under_a_directory_entry_fails(repo):
    commit(repo, "src/x/tables/a.py")
    assert run(repo)[0] == 1


def test_base_limits_the_commits_examined(repo):
    bad = commit(repo, "RULES.md")
    commit(repo, "src/x/other.py")
    assert run(repo)[0] == 1
    assert run(repo, bad) == (0, "design_guard: ok\n")


def test_an_all_zero_base_examines_every_commit(repo):
    commit(repo, "RULES.md")
    commit(repo, "src/x/other.py")
    assert run(repo, ZEROS)[0] == 1


def test_the_real_repository_passes():
    assert run(family.ROOT) == (0, "design_guard: ok\n")
