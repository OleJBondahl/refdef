"""M16 harness: run each guide block and compare each printed line with its comment."""

import ast
import contextlib
import io
import re
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FENCE = re.compile(r"^```python[^\n]*\n(.*?)^```", re.S | re.M)


def _comments(source: str) -> dict[int, str]:
    """Comment text by line number."""
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    return {t.start[0]: t.string[1:].strip() for t in tokens if t.type == tokenize.COMMENT}


def _is_print(node: ast.stmt) -> bool:
    call = node.value if isinstance(node, ast.Expr) else None
    return isinstance(call, ast.Call) and getattr(call.func, "id", "") == "print"


def mismatches(source: str, namespace: dict[str, object], name: str = "block") -> list[str]:
    """Run `source`; for each print statement with a trailing comment, compare the output."""
    comments = _comments(source)
    bad = []
    for node in ast.parse(source).body:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exec(compile(ast.Module([node], []), name, "exec"), namespace)  # noqa: S102 - the guide runs
        expected = comments.get(node.end_lineno or node.lineno)
        if _is_print(node) and expected is not None and out.getvalue().rstrip("\n") != expected:
            bad.append(f"{name}:{node.lineno}: printed {out.getvalue()!r}, comment {expected!r}")
    return bad


def page_mismatches(text: str, page: str = "page") -> list[str]:
    """Mismatches of every python block of one page; blocks share a namespace."""
    namespace: dict[str, object] = {"__name__": "__guide__"}
    bad = []
    for number, block in enumerate(FENCE.findall(text), 1):
        bad += mismatches(block, namespace, f"{page} block {number}")
    return bad


def test_every_guide_print_matches_its_comment():
    """M16: each printed line equals the comment after its print statement."""
    bad = []
    for page in sorted((ROOT / "docs" / "guide").glob("*.md")):
        bad += page_mismatches(page.read_text(encoding="utf-8"), page.name)
    assert not bad, "\n".join(bad)


def test_a_wrong_comment_is_found():
    """M16: the harness can fail; a comment that differs from the output is reported."""
    text = "```python\nprint(1 + 1)  # 3\nprint('a')  # a\n```\n"
    found = page_mismatches(text)
    assert len(found) == 1
    assert "comment '3'" in found[0]
