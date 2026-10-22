"""`scripts/build_site.py` stages the pages and the API page, and builds them strict.

The module fixture stages a stand-in repository and builds it once; the tests share that build.
`test_the_real_repository_builds_strict` stages the real sources instead.
"""

import runpy
import shutil
import subprocess
from pathlib import Path

import family
import pytest

ROOT = family.ROOT
SITE = runpy.run_path(str(ROOT / "scripts" / "build_site.py"))
PAGES = ["index", "docs", "guide", "changelog", "design", "rules", "api"]


def _stand_in(root: Path) -> Path:
    """Small pages, the real pyproject, source, snapshot, llms.txt and site config."""
    (root / "docs" / "guide").mkdir(parents=True)
    (root / "README.md").write_text("# Home\n\n[guide](docs/guide/index.md) [x](AGENTS.md)\n")
    (root / "docs" / "index.md").write_text("# Docs\n\n[home](../README.md)\n")
    (root / "docs" / "guide" / "index.md").write_text("# Guide\n\n[docs](../index.md)\n")
    for name in ("DESIGN", "RULES"):
        (root / f"{name}.md").write_text(f"# {name}\n\n[home](README.md)\n")
    (root / "docs" / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n")
    (root / "AGENTS.md").write_text("# Agents\n")
    shutil.copytree(ROOT / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("pyproject.toml", "mkdocs.yml", "docs/llms.txt", "docs/api-snapshot.txt"):
        shutil.copy2(ROOT / name, root / name)
    return root


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    """Stage the stand-in once, build it strict once; return `(root, out)`."""
    base = tmp_path_factory.mktemp("site")
    root = _stand_in(base / "repo")
    out = SITE["stage"](root, base / "out")
    SITE["build"](out)
    return root, out


def test_the_pages_and_llms_txt_are_built(staged):
    _, out = staged
    built = {p: (out / ".site" / p / "index.html").is_file() for p in PAGES if p != "index"}
    assert all(built.values()), built
    assert (out / ".site" / "index.html").is_file()
    assert (out / ".site" / "llms.txt").read_bytes() == (ROOT / "docs" / "llms.txt").read_bytes()


def test_api_markdown_holds_the_snapshot_and_is_deterministic(staged):
    root, _ = staged
    text = SITE["api_markdown"](root)
    snapshot = (ROOT / "docs" / "api-snapshot.txt").read_text(encoding="utf-8")
    assert snapshot in text
    assert text == SITE["api_markdown"](root)
    assert f"python -m {family.lib_name()} api" in text


def test_links_point_at_site_pages_or_github(staged):
    _, out = staged
    index = (out / ".site-src" / "pages" / "index.md").read_text(encoding="utf-8")
    assert "](guide/index.md)" in index
    assert f"]({SITE['repo_url'](ROOT)}/blob/main/AGENTS.md)" in index
    assert "docs/guide" not in index.replace("](guide/index.md)", "")


def test_relink_leaves_fenced_code_and_absolute_links_alone():
    text = "[a](https://example.org/x.md)\n```\n[b](docs/index.md)\n```\n[c](docs/index.md)\n"
    mapping = {"README.md": "index.md", "docs/index.md": "docs.md"}
    out = SITE["relink"](text, "README.md", mapping, "https://r.example/repo")
    assert "[a](https://example.org/x.md)" in out
    assert "```\n[b](docs/index.md)\n```" in out
    assert "[c](docs.md)" in out


def test_a_broken_link_fails_the_strict_build(tmp_path_factory):
    base = tmp_path_factory.mktemp("broken")
    root = _stand_in(base / "repo")
    out = SITE["stage"](root, base / "out")
    with (out / ".site-src" / "pages" / "index.md").open("a", encoding="utf-8") as page:
        page.write("\n[gone](missing-page.md)\n")
    with pytest.raises(subprocess.CalledProcessError):
        SITE["build"](out)


def test_the_real_repository_builds_strict(tmp_path):
    out = SITE["stage"](ROOT, tmp_path)
    SITE["build"](out)
    assert (out / ".site" / "index.html").is_file()


def test_relink_keeps_a_link_to_no_file_so_the_build_can_fail_it():
    mapping = {"README.md": "index.md"}
    out = SITE["relink"]("[x](nope.md) [y](AGENTS.md)\n", "README.md", mapping, "https://r.x", ROOT)
    assert "[x](nope.md)" in out
    assert "[y](https://r.x/blob/main/AGENTS.md)" in out
