"""F16 content: `docs/llms.txt` names every door name and carries every refdef rule line."""

import importlib
import re
from pathlib import Path

import family

ROOT = family.ROOT
RULE = re.compile(r"^- \*\*(R\d+)\. [^*]*\*\* (.+)$", re.M)


def missing_names(llms: str, names: list[tuple[str, str]]) -> list[str]:
    """The `door.name` entries with no line that opens `name:`."""
    lines = [line.split(":", 1)[0] for line in llms.splitlines()]
    return [f"{door}.{name}" for door, name in names if name not in lines]


def missing_rules(llms: str, rules: str) -> list[str]:
    """The ids of the rules whose `Rn. text` line is not in `llms`."""
    lines = set(llms.splitlines())
    cut = [(rid, body.split(" GATE:")[0]) for rid, body in RULE.findall(rules)]
    return [rid for rid, body in cut if f"{rid}. {body}" not in lines]


def _names() -> list[tuple[str, str]]:
    doors = family.family_config(ROOT)["doors"]
    return [(d, n) for d in doors for n in importlib.import_module(d).__all__]


def _read(name: str) -> str:
    return (Path(ROOT) / name).read_text(encoding="utf-8")


def test_llms_names_every_door_name():
    assert not missing_names(_read("docs/llms.txt"), _names())


def test_llms_carries_every_rule_line():
    assert not missing_rules(_read("docs/llms.txt"), _read("RULES.md"))


def test_a_missing_name_and_a_changed_rule_are_found():
    assert missing_names("parse: x\nSize: y\n", [("m", "parse"), ("m", "Memory")]) == ["m.Memory"]
    rules = "- **R1. Title.** Body one. GATE: x\n- **R2. Other.** Body two.\n"
    assert missing_rules("R1. Body one.\nR2. Body 2.\n", rules) == ["R2"]
    assert len(RULE.findall(_read("RULES.md"))) == 12
