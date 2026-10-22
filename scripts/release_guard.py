"""Fail when the public API changed since the last tag with no changelog line or version bump.

Usage (from the repository root):
    uv run python scripts/release_guard.py
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

SNAPSHOT = "docs/api-snapshot.txt"
CHANGELOG = Path("docs/CHANGELOG.md")
NAME = re.compile(r"(?:class\s+)?([A-Za-z_]\w*)")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    argv = ["git", *args]
    return subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603 - fixed git argv


def names(snapshot: str) -> set[str]:
    """The names of a snapshot: the leading identifier of each entry's head line."""
    found = set()
    for line in snapshot.splitlines():
        if not line.strip() or line[0].isspace() or line.startswith("## "):
            continue
        match = NAME.match(line)
        if match:
            found.add(match.group(1))
    return found


def unreleased(changelog: str) -> list[str]:
    """The content lines under `## Unreleased`, before the next `## ` heading."""
    lines, inside = [], False
    for line in changelog.splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Unreleased"
        elif inside and line.strip() and not line.startswith("#"):
            lines.append(line)
    return lines


def version(pyproject: str) -> tuple[int, ...]:
    """The `[project].version` of a pyproject text as a tuple of integers."""
    text = tomllib.loads(pyproject)["project"]["version"]
    return tuple(int(part) for part in re.findall(r"\d+", text))


def breaking_allowed(old: tuple[int, ...], new: tuple[int, ...]) -> bool:
    """Whether `new` is a high enough release to remove names: a higher major, or minor at 0.x."""
    return new[0] > old[0] or (old[0] == 0 and new[:2] > old[:2])


def check(tag: str) -> str | None:
    """The failure message for the API change since `tag`, or None."""
    old = _git("show", f"{tag}:{SNAPSHOT}").stdout
    new = Path(SNAPSHOT).read_text(encoding="utf-8")
    if old == new:
        return None
    if not unreleased(CHANGELOG.read_text(encoding="utf-8")):
        return f"{SNAPSHOT} changed since {tag}: add a line under '## Unreleased' in {CHANGELOG}"
    gone = sorted(names(old) - names(new))
    old_version = version(_git("show", f"{tag}:pyproject.toml").stdout)
    new_version = version(Path("pyproject.toml").read_text(encoding="utf-8"))
    if gone and not breaking_allowed(old_version, new_version):
        return f"names removed since {tag} ({', '.join(gone)}): raise the major (minor while 0.x)"
    return None


def main() -> int:
    """Run the guard in the current directory; return the exit code."""
    described = _git("describe", "--tags", "--abbrev=0", "--match", "v*")
    if described.returncode != 0:
        sys.stdout.write("release_guard: no release tag yet, nothing to compare\n")
        return 0
    tag = described.stdout.strip()
    message = check(tag)
    if message:
        sys.stdout.write(f"release_guard: {message}\n")
        return 1
    sys.stdout.write(f"release_guard: ok (since {tag})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
