"""F10 gate (AST half): no nested def, no async def, short modules and docstrings, reasoned noqa."""

import ast
import io
import re
import tokenize
from pathlib import Path

import family

MAX_CODE_LINES = 300
MAX_DOC_LINES = 3
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)
MARK = re.compile(r"#\s*(?:noqa|ty:\s*ignore)")
SHAPES = (
    re.compile(r"# noqa: [A-Z]+\d+(?:, [A-Z]+\d+)* - \S"),
    re.compile(r"# ty: ignore\[[a-z0-9-]+(?:, ?[a-z0-9-]+)*\] - \S"),
)
DOCUMENTED = (ast.Module, ast.ClassDef, *DEFS)


def problems_in_tree(tree: ast.Module) -> list[str]:
    """Nested defs, async defs and docstring shape problems of one module."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            found.append(f"async def {node.name}")
        if isinstance(node, DEFS):
            inner = [n for n in ast.walk(node) if isinstance(n, DEFS) and n is not node]
            found += [f"def {n.name} nested in {node.name}" for n in inner]
        if isinstance(node, DOCUMENTED):
            found += doc_problems(node)
    return found


def doc_problems(
    node: ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    """Docstring over three lines, or longer than one line without a blank second line."""
    doc = ast.get_docstring(node)
    if doc is None:
        return []
    lines = doc.splitlines()
    name = getattr(node, "name", "module")
    if len(lines) > MAX_DOC_LINES:
        return [f"docstring of {name} has {len(lines)} lines"]
    if len(lines) > 1 and lines[1].strip():
        return [f"docstring of {name} lacks a blank line after its summary"]
    return []


def code_lines(text: str) -> int:
    """Non-blank, non-comment lines."""
    return sum(
        1 for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")
    )


def comment_problems(text: str) -> list[str]:
    """Each `noqa` or `ty: ignore` comment that lacks the `CODE - reason` shape."""
    found = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        mark = MARK.search(tok.string) if tok.type == tokenize.COMMENT else None
        if mark and not any(s.match(tok.string, mark.start()) for s in SHAPES):
            found.append(f"line {tok.start[0]}: {tok.string.strip()!r}")
    return found


def file_problems(path: Path, *, structure: bool) -> list[str]:
    """Every F10 problem of one file; scripts get the comment check only."""
    text = path.read_text(encoding="utf-8")
    found = comment_problems(text)
    if structure:
        found += problems_in_tree(ast.parse(text))
        if code_lines(text) > MAX_CODE_LINES:
            found.append(f"{code_lines(text)} code lines")
    return [f"{path.name}: {item}" for item in found]


def check_lean(root: Path = family.ROOT) -> None:
    """Fail on any F10 problem under `src/<lib>` or any bad comment in `scripts/` and `tests/`."""
    found = []
    for path in sorted((root / "src" / family.lib_name(root)).rglob("*.py")):
        found += file_problems(path, structure=True)
    for folder in ("scripts", "tests"):
        for path in sorted((root / folder).rglob("*.py")):
            found += file_problems(path, structure=False)
    assert not found, "; ".join(found)


def test_lean():
    check_lean()


def test_bare_markers_are_found():
    bare = "x = 1  # noqa\ny = 2  # ty: ignore\nz = 3  # noqa: E501\n"
    assert len(comment_problems(bare)) == 3
    assert comment_problems("x = 1  # noqa: E501 - reason\n") == []
