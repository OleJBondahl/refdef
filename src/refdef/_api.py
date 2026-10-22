"""The surface printer: `render` lists every door's `__all__` with signatures and docstrings."""

import annotationlib
import dataclasses
import enum
import importlib
import inspect

DOORS: tuple[str, ...] = ("refdef", "refdef.plc")


def _signature(obj: object) -> str:
    """The signature as source text, so 3.14 and 3.15 print the same bytes."""
    return str(inspect.signature(obj, annotation_format=annotationlib.Format.STRING))  # ty: ignore[invalid-argument-type] - obj is callable here


def _head(name: str, obj: object) -> str:
    """The first line of a name's entry."""
    if isinstance(obj, type) and issubclass(obj, enum.Enum):
        return f"class {name}"
    if isinstance(obj, type) and dataclasses.is_dataclass(obj):
        return f"class {name}{_signature(obj)}"
    if callable(obj):
        return f"{name}{_signature(obj)}"
    return f"{name}: {type(obj).__name__}"


def _entry(name: str, obj: object) -> list[str]:
    """A name's head, its docstring indented four spaces, and a blank line."""
    doc = inspect.getdoc(obj if callable(obj) else type(obj)) or ""
    return [_head(name, obj), *(f"    {line}".rstrip() for line in doc.splitlines()), ""]


def render(doors: tuple[str, ...]) -> str:
    """Return the public surface of `doors` as text: deterministic, one final newline."""
    lines: list[str] = []
    for door in doors:
        module = importlib.import_module(door)
        lines.append(f"## {door}")
        for name in sorted(module.__all__):
            lines += _entry(name, getattr(module, name))
    return "\n".join(lines).rstrip("\n") + "\n"
