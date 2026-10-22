"""F16 gate: `AGENTS.md` and `docs/llms.txt` carry the agent entry points; their links resolve."""

import re
import runpy
from pathlib import Path

import family
import pytest

ROOT = family.ROOT
URL = family.site_url()
LIB = family.lib_name()
SITE = runpy.run_path(str(ROOT / "scripts" / "build_site.py"))

COMMON: list[tuple[str, ...]] = [(URL,), (f"python -m {LIB} api",)]
REQUIRED: dict[str, list[tuple[str, ...]]] = {
    "AGENTS.md": [
        *COMMON,
        ("docs/guide",),
        ("DESIGN.md",),
        ("RULES.md",),
        ("A change follows RULES.md",),
    ],
    "docs/llms.txt": [
        *COMMON,
        ("docs/guide", URL + "guide/"),
        ("DESIGN.md", URL + "design/"),
        ("RULES.md", URL + "rules/"),
        ("a change follows RULES.md",),
    ],
}


def lacking(text: str, required: list[tuple[str, ...]]) -> list[str]:
    """The requirements of which no alternative occurs in `text`."""
    return [" | ".join(r) for r in required if not any(alt in text for alt in r)]


def links(text: str, url: str) -> list[str]:
    """Each link starting with `url`, cut at whitespace, `)`, `>` or a quote."""
    found = re.findall(re.escape(url) + r"""[^\s)>"']*""", text)
    return [f.rstrip(".,;)") for f in found]


def resolves(site: Path, url: str, link: str) -> bool:
    """Whether the link names a file of the built site."""
    path = link.removeprefix(url).split("#")[0].split("?")[0]
    if path == "" or path.endswith("/"):
        return (site / path / "index.html").is_file()
    return any(
        c.is_file() for c in (site / path, site / path / "index.html", site / f"{path}.html")
    )


def dead_links(root: Path, site: Path) -> list[str]:
    """The links of the entry-point files that resolve to no file of `site`."""
    url = family.site_url(root)
    texts = [(root / name).read_text(encoding="utf-8") for name in REQUIRED]
    return [link for text in texts for link in links(text, url) if not resolves(site, url, link)]


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    """The real repository's site, built once into a temporary folder."""
    out = SITE["stage"](ROOT, tmp_path_factory.mktemp("agents"))
    SITE["build"](out)
    return out / ".site"


@pytest.mark.parametrize("name", list(REQUIRED))
def test_the_entry_point_has_its_parts(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    assert not lacking(text, REQUIRED[name]), f"F16: {name} lacks {lacking(text, REQUIRED[name])}"


def test_every_site_link_resolves(site):
    assert not dead_links(ROOT, site)


def test_a_missing_part_is_found():
    assert lacking("A change follows RULES.md", [("A change follows RULES.md",)]) == []
    assert lacking("nothing", [("RULES.md", URL + "rules/")]) == [f"RULES.md | {URL}rules/"]


def test_links_are_cut_and_stripped():
    text = f"[a]({URL}api/). <{URL}guide/> '{URL}x.html;' {URL}"
    assert links(text, URL) == [URL + "api/", URL + "guide/", URL + "x.html", URL]


def test_a_dead_link_is_found(tmp_path):
    (tmp_path / "api").mkdir()
    (tmp_path / "api" / "index.html").write_text("x")
    (tmp_path / "index.html").write_text("x")
    (tmp_path / "llms.txt").write_text("x")
    assert resolves(tmp_path, URL, URL)
    assert resolves(tmp_path, URL, URL + "api/")
    assert resolves(tmp_path, URL, URL + "api")
    assert resolves(tmp_path, URL, URL + "llms.txt")
    assert not resolves(tmp_path, URL, URL + "gone/")
    assert not resolves(tmp_path, URL, URL + "gone")


def test_dead_links_are_listed_per_file(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "pyproject.toml").write_text((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    (tmp_path / "AGENTS.md").write_text(f"{URL}api/ and {URL}gone/\n")
    (tmp_path / "docs" / "llms.txt").write_text(f"Site: {URL}\n")
    site = tmp_path / "site"
    (site / "api").mkdir(parents=True)
    (site / "api" / "index.html").write_text("x")
    (site / "index.html").write_text("x")
    assert dead_links(tmp_path, site) == [URL + "gone/"]
