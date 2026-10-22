"""F9 gate: every door name has a docstring and a guide example, and every guide block runs."""

import importlib
import inspect
import re
from pathlib import Path

import family
import pytest

FENCE = re.compile(r"^```python[^\n]*\n(.*?)^```", re.S | re.M)


def door_names(root: Path = family.ROOT) -> list[tuple[str, str]]:
    """Each `(door, name)` of every door named in `[tool.family]`."""
    doors = family.family_config(root)["doors"]
    return [(door, name) for door in doors for name in importlib.import_module(door).__all__]


def guide_blocks(root: Path = family.ROOT) -> dict[Path, list[str]]:
    """The python blocks of each guide page, in order."""
    pages = sorted((root / "docs" / "guide").glob("*.md"))
    return {p: FENCE.findall(p.read_text(encoding="utf-8")) for p in pages}


def undocumented(names: list[tuple[str, str]]) -> list[str]:
    """The names whose object (or, for a constant, its type) has no docstring."""
    bad = []
    for door, name in names:
        obj = getattr(importlib.import_module(door), name)
        constant = not (inspect.isclass(obj) or callable(obj))
        doc = inspect.getdoc(obj) or (inspect.getdoc(type(obj)) if constant else None)
        if not doc:
            bad.append(f"{door}.{name}")
    return bad


def unshown(names: list[tuple[str, str]], root: Path = family.ROOT) -> list[str]:
    """The names that no guide python block mentions as a word."""
    code = "\n".join(b for blocks in guide_blocks(root).values() for b in blocks)
    return [f"{d}.{n}" for d, n in names if not re.search(rf"\b{re.escape(n)}\b", code)]


def run_pages(root: Path = family.ROOT) -> None:
    """Run every block with `exec`, one namespace per page, in order."""
    for page, blocks in guide_blocks(root).items():
        namespace: dict[str, object] = {"__name__": "__guide__"}
        for number, block in enumerate(blocks, 1):
            try:
                exec(compile(block, f"{page.name}:{number}", "exec"), namespace)  # noqa: S102 - the gate runs the docs
            except Exception as error:
                message = f"{page.name} block {number}: {error!r}"
                raise AssertionError(message) from error


def check_docs(root: Path = family.ROOT) -> None:
    """Fail naming each undocumented name, each name with no example, the first failing block."""
    names = door_names(root)
    assert not undocumented(names), f"F9: no docstring: {undocumented(names)}"
    assert not unshown(names, root), f"F9: no guide example: {unshown(names, root)}"
    run_pages(root)


def _guide(root: Path, text: str) -> Path:
    page = root / "docs" / "guide"
    page.mkdir(parents=True)
    (page / "a.md").write_text(text, encoding="utf-8")
    return root


def test_docs():
    check_docs()


def test_an_undocumented_name_is_found(tmp_path, monkeypatch):
    source = (
        'LIMIT = 3\n\n\ndef bare(): ...\n\n\nclass Bare: ...\n\n\ndef good():\n    """Doc."""\n'
    )
    (tmp_path / "gatedoor.py").write_text(source + '__all__ = ["LIMIT", "bare", "Bare", "good"]\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    names = [("gatedoor", n) for n in ("LIMIT", "bare", "Bare", "good")]
    assert undocumented(names) == ["gatedoor.bare", "gatedoor.Bare"]


def test_a_name_without_an_example_is_found(tmp_path):
    root = _guide(tmp_path, "```python\nx = 1\n```\n\n```text\nfoo\n```\n")
    assert unshown([("m", "foo"), ("m", "x")], root) == ["m.foo"]


def test_a_word_match_is_whole_word(tmp_path):
    root = _guide(tmp_path, "```python\nfoobar = 1\n```\n")
    assert unshown([("m", "foo")], root) == ["m.foo"]


def test_a_failing_block_fails_the_gate(tmp_path):
    root = _guide(tmp_path, "```python\nraise ValueError('boom')\n```\n")
    with pytest.raises(AssertionError, match=r"a\.md block 1"):
        run_pages(root)


def test_blocks_of_a_page_share_a_namespace_in_order(tmp_path):
    root = _guide(tmp_path, "```python\nx = 1\n```\n\n```python\nassert x == 1\n```\n")
    run_pages(root)
    assert [len(b) for b in guide_blocks(root).values()] == [2]
