"""Stage the docs site and build it with Zensical, strict: a broken link fails the build.

Usage:
    uv run python scripts/build_site.py

Pages are staged into `.site-src/pages/` and built into `.site/`; both are gitignored and
rebuilt each run.
"""

import os
import posixpath
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s#]+)(#[^)\s]*)?\)")
FIXED = {
    "README.md": "index.md",
    "docs/index.md": "docs.md",
    "docs/CHANGELOG.md": "changelog.md",
    "DESIGN.md": "design.md",
    "RULES.md": "rules.md",
}


def _project(root: Path) -> dict[str, object]:
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def library(root: Path = ROOT) -> str:
    """The library name, read from `pyproject.toml`."""
    return str(_project(root)["name"])


def repo_url(root: Path = ROOT) -> str:
    """The repository URL, read from `pyproject.toml`."""
    urls: dict[str, str] = _project(root)["urls"]  # ty: ignore[invalid-assignment] - toml value
    return urls["Repository"]


def pages(root: Path = ROOT) -> dict[str, str]:
    """Map each repository path that becomes a site page to its page under `.site-src/pages/`."""
    found = dict(FIXED)
    for path in sorted((root / "docs" / "guide").glob("*.md")):
        found[f"docs/guide/{path.name}"] = f"guide/{path.name}"
    return found


def relink(
    text: str,
    source: str,
    mapping: dict[str, str] | None = None,
    repo: str | None = None,
    root: Path = ROOT,
) -> str:
    """Point each relative link outside fenced code at a site page or, if the file exists, GitHub.

    A target that is no file of the repository stays as written, so the strict build fails it.
    """
    mapping = pages() if mapping is None else mapping
    repo = repo_url() if repo is None else repo
    folder = posixpath.dirname(source)
    page_dir = posixpath.dirname(mapping.get(source, source))

    def fix(match: re.Match[str]) -> str:
        path, frag = match.group(1), match.group(2) or ""
        if "://" in path or path.startswith("mailto:"):
            return match.group(0)
        target = posixpath.normpath(posixpath.join(folder, path))
        if target in mapping:
            return f"]({posixpath.relpath(mapping[target], page_dir or '.')}{frag})"
        if not (root / target).exists():
            return match.group(0)
        return f"]({repo}/blob/main/{target}{frag})"

    out, fenced = [], False
    for line in text.splitlines(keepends=True):
        edge = line.lstrip().startswith("```")
        fenced ^= edge
        out.append(line if fenced or edge else LINK.sub(fix, line))
    return "".join(out)


def api_markdown(root: Path = ROOT) -> str:
    """The API page: the output of `python -m <library> api`, in a text fence."""
    name = library(root)
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    argv = [sys.executable, "-m", name, "api"]
    done = subprocess.run(  # noqa: S603 - runs this repository's own library
        argv,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    head = (
        f"# API reference\n\nEvery name `{name}` exports, as printed by `python -m {name} api`.\n\n"
    )
    return f"{head}```text\n{done.stdout}```\n"


def stage(root: Path, out: Path) -> Path:
    """Rebuild the pages, `llms.txt` and `mkdocs.yml` under `out`; return `out`."""
    site_src = out / ".site-src" / "pages"
    shutil.rmtree(site_src.parent, ignore_errors=True)
    site_src.mkdir(parents=True)
    mapping, repo = pages(root), repo_url(root)
    for source, page in mapping.items():
        text = (root / source).read_text(encoding="utf-8")
        (site_src / page).parent.mkdir(parents=True, exist_ok=True)
        (site_src / page).write_text(relink(text, source, mapping, repo, root), encoding="utf-8")
    (site_src / "api.md").write_text(api_markdown(root), encoding="utf-8")
    shutil.copy2(root / "docs" / "llms.txt", site_src.parent / "llms.txt")
    if out.resolve() != root.resolve():
        shutil.copy2(root / "mkdocs.yml", out / "mkdocs.yml")
    return out


def build(project: Path) -> None:
    """Run Zensical strict from `project`, the folder that holds the config."""
    subprocess.run(
        [sys.executable, "-m", "zensical", "build", "--strict", "-f", "mkdocs.yml"],
        cwd=project,
        check=True,
    )
    shutil.copy2(project / ".site-src" / "llms.txt", project / ".site" / "llms.txt")


def main() -> None:
    """Stage the repository's site and build it into `.site/`."""
    shutil.rmtree(ROOT / ".site", ignore_errors=True)
    build(stage(ROOT, ROOT))
    sys.stdout.write("site built: .site\n")


if __name__ == "__main__":
    main()
