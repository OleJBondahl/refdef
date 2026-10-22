"""R11, R12: no vendor word in `plc.py`; pins and signal names are never read inside."""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "refdef"
VENDORS = ("siemens", "rockwell", "omron", "mitsubishi", "beckhoff")
NAMES = {"pins", "pin"}  # local names holding the pins or a pin
ATTRS = {"pins", "name"}  # attributes holding the pins or a Signal.name
# R12 sites by (file, operation), one entry each; M14: parse (split, the strip helper), terminal
# (join, the validating helper) and natural_key. Operations: call:ATTR, arg:FUNC (a private helper
# handed the value), subscript, compare. `_parse.py` call:lower is `bare.name.lower()`, an Aspect.
SITES = frozenset(
    {
        ("_parse.py", "call:append"),
        ("_parse.py", "call:lower"),
        ("_parse.py", "compare"),
        ("terminal.py", "arg:_stripped"),
    }
)


def test_r11_no_vendor_word_in_plc():
    """R11: the five vendor words are absent from `plc.py`, in any case."""
    text = (SRC / "plc.py").read_text(encoding="utf-8").lower()
    assert [word for word in VENDORS if word in text] == []


def test_r11_vendor_check_finds_a_word():
    """R11: the word check can fail; a text holding a vendor word in capitals is reported."""
    assert [w for w in VENDORS if w in "# Siemens dialect".lower()] == ["siemens"]


def _opaque(node: ast.AST, tainted: set[str]) -> bool:
    """True for a pin, the pins or a signal name: a listed name or attribute, or an element."""
    if isinstance(node, ast.Name):
        return node.id in NAMES or node.id in tainted
    if isinstance(node, ast.Attribute):
        return node.attr in ATTRS
    return isinstance(node, ast.Subscript) and _opaque(node.value, tainted)


def _loop_names(tree: ast.AST, tainted: set[str]) -> None:
    """Add the targets of every `for` and comprehension that walks an opaque value."""
    for node in ast.walk(tree):
        if isinstance(node, ast.For | ast.comprehension) and _opaque(node.iter, tainted):
            tainted.update(n.id for n in ast.walk(node.target) if isinstance(n, ast.Name))


def _private_helper(call: ast.Call, tainted: set[str]) -> str:
    """The name of a private helper (`_name`) handed an opaque value, else an empty string."""
    func = call.func
    if isinstance(func, ast.Name) and func.id.startswith("_"):
        return func.id if any(_opaque(arg, tainted) for arg in call.args) else ""
    return ""


def operations(tree: ast.AST) -> set[str]:
    """The operations of one module that read inside an opaque value."""
    tainted: set[str] = set()
    _loop_names(tree, tainted)
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and _opaque(node.func.value, tainted):
                found.add(f"call:{node.func.attr}")
            helper = _private_helper(node, tainted)
            if helper:
                found.add(f"arg:{helper}")
        elif isinstance(node, ast.Subscript) and _opaque(node.value, tainted):
            found.add("subscript")
        elif isinstance(node, ast.Compare) and any(
            _opaque(n, tainted) for n in (node.left, *node.comparators)
        ):
            found.add("compare")
    return found


def found_sites(root: Path) -> set[tuple[str, str]]:
    """Every (file, operation) under `root` that reads inside an opaque value."""
    return {
        (path.name, op)
        for path in sorted(root.rglob("*.py"))
        for op in operations(ast.parse(path.read_text(encoding="utf-8")))
    }


def test_r12_pins_and_names_are_read_only_at_the_listed_sites():
    """R12: no call, subscript or comparison on a pin or a signal name outside SITES."""
    assert found_sites(SRC) - SITES == set()


def test_r12_every_listed_site_is_still_used():
    """R12: a stale entry in SITES is reported, so the list cannot grow past the code."""
    assert SITES - found_sites(SRC) == set()


def test_r12_walker_finds_each_kind_of_read(tmp_path: Path):
    """R12: the walker can fail; each read of a pin in a scratch module is found."""
    source = (
        "def f(t, signal):\n"
        "    t.pins[0].upper()\n"
        "    t.pins[0][1:]\n"
        "    for pin in t.pins:\n"
        "        _look(pin)\n"
        "        pin == 'a'\n"
        "    signal.name.strip()\n"
    )
    (tmp_path / "x.py").write_text(source, encoding="utf-8")
    ops = {op for _, op in found_sites(tmp_path)}
    assert ops == {"call:upper", "call:strip", "subscript", "arg:_look", "compare"}


def test_r12_walker_ignores_other_names():
    """R12: a call on a name that is not a pin or a signal name is not reported."""
    assert (
        operations(ast.parse("def f(text):\n    text.upper()\n    text[0]\n    text == 'a'"))
        == set()
    )
