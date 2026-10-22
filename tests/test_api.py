"""`_api.render` and `python -m <lib> api`: every kind of surface name, and the usage error."""

import runpy
import sys
import textwrap

import family
import pytest

DOOR = '''
"""A stand-in door."""
import dataclasses
import enum

__all__ = ["Colour", "Box", "build", "LIMIT"]


class Colour(enum.Enum):
    """Two colours."""

    RED = 1


@dataclasses.dataclass(frozen=True)
class Box:
    """A box.

    With a second paragraph.
    """

    width: int = 1


def build(box: Box, *, deep: bool = False) -> int:
    """Build one."""
    return box.width


LIMIT = 3
'''


def test_render_prints_each_kind_of_name(tmp_path, monkeypatch):
    (tmp_path / "standin_door.py").write_text(textwrap.dedent(DOOR), encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    api = __import__(f"{family.lib_name()}._api", fromlist=["render"])
    text = api.render(("standin_door",))
    assert text.startswith("## standin_door\nclass Box(width: 'int' = 1) -> 'None'")
    assert "class Colour\n    Two colours." in text
    assert "build(box: 'Box', *, deep: 'bool' = False) -> 'int'" in text
    assert text.index("class Colour") < text.index("LIMIT: int\n") < text.index("build(")
    assert "    With a second paragraph." in text
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_main_prints_the_snapshot(capsys):
    main = __import__(f"{family.lib_name()}.__main__", fromlist=["main"]).main
    assert main(["api"]) == 0
    expected = (family.ROOT / "docs" / "api-snapshot.txt").read_text(encoding="utf-8")
    assert capsys.readouterr().out == expected


def test_main_rejects_anything_else(capsys):
    main = __import__(f"{family.lib_name()}.__main__", fromlist=["main"]).main
    assert main([]) == 2
    assert main(["api", "extra"]) == 2
    assert "usage" in capsys.readouterr().err


def test_the_module_runs_as_a_script(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "nope"])
    monkeypatch.delitem(sys.modules, f"{family.lib_name()}.__main__", raising=False)
    with pytest.raises(SystemExit) as stop:
        runpy.run_module(family.lib_name(), run_name="__main__")
    assert stop.value.code == 2
