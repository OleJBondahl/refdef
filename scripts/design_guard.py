"""Fail when a commit touches a design-review path without a `Design-review:` trailer.

Usage (from the repository root):
    uv run python scripts/design_guard.py [BASE]
"""

import subprocess
import sys
import tomllib
from pathlib import Path

ZEROS = "0" * 40


def _git(*args: str, stdin: str | None = None) -> str:
    argv = ["git", *args]
    done = subprocess.run(argv, input=stdin, capture_output=True, text=True, check=False)  # noqa: S603 - fixed git argv
    return done.stdout


def commits(base: str | None) -> list[str]:
    """The non-merge commits of BASE..HEAD, or all reachable ones; none without commits."""
    if _git("rev-parse", "--verify", "-q", "HEAD^{commit}").strip() == "":
        return []
    usable = (
        base and base != ZEROS and _git("rev-parse", "--verify", "-q", f"{base}^{{commit}}").strip()
    )
    span = f"{base}..HEAD" if usable else "HEAD"
    return _git("rev-list", "--no-merges", span).split()


def touches(paths: list[str], review: list[str]) -> bool:
    """Whether a path equals a review entry or sits under a directory entry (ending `/`)."""
    return any(p == r or (r.endswith("/") and p.startswith(r)) for p in paths for r in review)


def reviewed(sha: str) -> bool:
    """Whether the commit message carries a `Design-review:` trailer with a token."""
    message = _git("show", "-s", "--format=%B", sha)
    for line in _git("interpret-trailers", "--parse", stdin=message).splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() == "design-review" and value.strip():
            return True
    return False


def offenders(base: str | None, review: list[str]) -> list[str]:
    """The short shas of commits that touch a review path with no trailer."""
    bad = []
    for sha in commits(base):
        paths = _git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", sha).split("\n")
        if touches(paths, review) and not reviewed(sha):
            bad.append(sha[:9])
    return bad


def main(argv: list[str]) -> int:
    """Run the guard in the current directory; return the exit code."""
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    review = config["tool"]["family"]["review_paths"]
    bad = offenders(argv[0] if argv else None, review)
    if bad:
        sys.stdout.write(
            f"design_guard: commits without a Design-review trailer: {' '.join(bad)}\n"
        )
        return 1
    sys.stdout.write("design_guard: ok\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
