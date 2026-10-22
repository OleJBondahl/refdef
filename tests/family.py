"""Shared helpers and gates of the family rules F1-F17; the identical set carries it verbatim.

The library name comes from `pyproject.toml`, never from this text. Each `gate_f<n>(root)` raises
`AssertionError` when its rule is breached; the F part of a test file is a thin wrapper over it.
"""

import ast
import hashlib
import importlib
import importlib.util
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent

# Digests of every name the application has had, with its plurals (SHA-256 of the lowercased word).
APPLICATION_HASHES = frozenset(
    {
        "01aa28fcf8c8ead78b7c2a4369b8015848e9d9dfeeff133289ffdb2cc819b254",
        "d51efe19f97fe25d099b3a56085aae219f9154b6b2278b70dcb3b00e40c20bdf",
        "24e96e9171edb34725e95db860f8d8659b7333b3d363411a65783443bdcb6861",
        "f88fd5d38492f15bb99bd49224d5e443047cec09086521e4aa25c4dfd3ff9df1",
        "b53ebc9d2b1124dd0af080ac6e1ab3135035040b987ec40e6445f774c3fafaee",
        "c237b623df962e71e9a27140a1e954a94bd33c348296420ba9830e021aee1166",
    }
)

WORD = re.compile(r"[A-Za-z0-9]+")


def pyproject(root: Path = ROOT) -> dict:
    """The parsed `pyproject.toml` of `root`."""
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))


def lib_name(root: Path = ROOT) -> str:
    """The library name, read from `[project].name`."""
    return pyproject(root)["project"]["name"]


def family_config(root: Path = ROOT) -> dict:
    """The `[tool.family]` table of `root`."""
    return pyproject(root)["tool"]["family"]


def site_url(root: Path = ROOT) -> str:
    """The docs site URL, derived from the repository URL in `[project.urls]`."""
    repo = pyproject(root)["project"]["urls"]["Repository"]
    owner, name = repo.removeprefix("https://github.com/").split("/")
    return f"https://{owner.lower()}.github.io/{name}/"


def src_files(root: Path = ROOT) -> list[Path]:
    """Every `.py` file of the package under `src/<lib>/`, sorted."""
    return sorted((root / "src" / lib_name(root)).rglob("*.py"))


def parse(path: Path) -> ast.Module:
    """The syntax tree of one source file."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def tracked(root: Path = ROOT) -> list[Path]:
    """Every file of `git ls-files` in `root` that exists, as absolute paths."""
    out = subprocess.run(
        ["git", "ls-files", "-z"],  # noqa: S607 - git on PATH is the contract
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [root / name for name in out.split("\0") if name and (root / name).is_file()]


def digest(word: str) -> str:
    """SHA-256 hex of the lowercased word."""
    return hashlib.sha256(word.lower().encode("utf-8")).hexdigest()


def read_text_or_none(path: Path) -> str | None:
    """The file's UTF-8 text, or None for a binary file."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


FAMILY_NAMES = ("elecdef", "refdef")
FORBIDDEN_MODULES = (
    "os",
    "pathlib",
    "io",
    "socket",
    "time",
    "datetime",
    "random",
    "secrets",
    "uuid",
)
STR_TYPES = ("str", "tuple[str, ...]")
_BINARY = (
    *("add", "sub", "mul", "matmul", "truediv", "floordiv", "mod"),
    *("pow", "and", "or", "xor", "lshift", "rshift"),
)
ARITHMETIC = frozenset(
    f"__{prefix}{name}__"
    for name in (*_BINARY, "neg", "pos", "invert")
    for prefix in ("", "r", "i")
)
FENCE = re.compile(r"^```python[^\n]*\n(.*?)^```", re.DOTALL | re.MULTILINE)
_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
_NAME_FIELDS = {
    ast.Name: ("id",),
    ast.Attribute: ("attr",),
    ast.arg: ("arg",),
    ast.alias: ("name", "asname"),
    ast.ImportFrom: ("module",),
}
_DEF_FIELDS = {
    ast.FunctionDef: ("name",),
    ast.AsyncFunctionDef: ("name",),
    ast.ClassDef: ("name",),
}


def src_trees(root: Path = ROOT) -> list[tuple[Path, ast.Module]]:
    """Every source file of the package with its syntax tree."""
    return [(path, parse(path)) for path in src_files(root)]


def where(root: Path, path: Path, lineno: int) -> str:
    """`relative/path.py:line`, the form an offender is reported in."""
    return f"{path.relative_to(root)}:{lineno}"


def identifiers(tree: ast.Module, *, defs: bool = False) -> list[tuple[int, str]]:
    """Every (line, identifier) of names, attributes, parameters, imports; `defs` adds def names."""
    found = []
    for node in ast.walk(tree):
        fields = _NAME_FIELDS.get(type(node)) or (_DEF_FIELDS.get(type(node)) if defs else None)
        found += [(getattr(node, "lineno", 0), t) for f in fields or () if (t := getattr(node, f))]
    return found


def dataclass_decorator(cls: ast.ClassDef) -> ast.expr | None:
    """The `@dataclass` decorator of a class (bare or called), or None."""
    for dec in cls.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if (isinstance(target, ast.Name) and target.id == "dataclass") or (
            isinstance(target, ast.Attribute) and target.attr == "dataclass"
        ):
            return dec
    return None


def is_frozen(dec: ast.expr) -> bool:
    """True when the decorator is a call carrying `frozen=True`."""
    return isinstance(dec, ast.Call) and any(
        kw.arg == "frozen" and isinstance(kw.value, ast.Constant) and kw.value.value is True
        for kw in dec.keywords
    )


def dataclasses_of(tree: ast.Module) -> list[ast.ClassDef]:
    """Every class of the tree that carries a `@dataclass` decorator."""
    return [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and dataclass_decorator(n)]


def fields_of(cls: ast.ClassDef) -> list[ast.AnnAssign]:
    """The annotated fields (`name: type`) in a class body."""
    return [s for s in cls.body if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]


def _imported_roots(tree: ast.Module) -> list[str]:
    roots = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots += [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            roots.append((node.module or "").split(".")[0])
    return roots


def gate_f1(root: Path = ROOT) -> None:
    """F1: no runtime dependency; src imports only the standard library and the package."""
    deps = pyproject(root)["project"].get("dependencies")
    assert deps == [], f"F1: [project].dependencies must be [], got {deps!r}"
    allowed = sys.stdlib_module_names | {lib_name(root)}
    bad = [
        f"{path.relative_to(root)}: import {name}"
        for path, tree in src_trees(root)
        for name in _imported_roots(tree)
        if name not in allowed
    ]
    assert not bad, "F1: imports outside the standard library:\n" + "\n".join(bad)


def gate_f2(root: Path = ROOT) -> None:
    """F2: frozen dataclasses only; no file, network, clock or random access in src."""
    bad = []
    for path, tree in src_trees(root):
        for cls in dataclasses_of(tree):
            dec = dataclass_decorator(cls)
            if dec is None or not is_frozen(dec):
                bad.append(f"{where(root, path, cls.lineno)}: dataclass {cls.name} is not frozen")
        for lineno, text in identifiers(tree):
            if any(part in (*FORBIDDEN_MODULES, "open") for part in text.split(".")):
                bad.append(f"{where(root, path, lineno)}: forbidden name {text}")
    assert not bad, "F2: impure or unfrozen code:\n" + "\n".join(bad)


def _load_fixture(path: Path) -> ModuleType:
    name = f"fixture_{path.parent.name}_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _fixtures(root: Path, kind: str) -> list[Path]:
    folder = root / "tests" / "fixtures" / kind
    return sorted(p for p in folder.glob("*.py") if not p.name.startswith("_"))


def _issues_problem(module: ModuleType) -> str | None:
    via = getattr(module, "VIA", None)
    if not isinstance(via, str) or not via:
        return "VIA must be a non-empty str"
    result = module.issues()
    if not isinstance(result, tuple) or not result:
        return f"issues() must return a non-empty tuple, got {result!r}"
    return None


def gate_f3_check(root: Path = ROOT) -> None:
    """F3 (check half): every issues fixture returns a non-empty issue tuple and does not raise."""
    bad = []
    for path in _fixtures(root, "issues"):
        problem = _issues_problem(_load_fixture(path))
        if problem:
            bad.append(f"{path.relative_to(root)}: {problem}")
    assert not bad, "F3: issues fixtures:\n" + "\n".join(bad)


def _build_problem(module: ModuleType) -> str | None:
    try:
        module.build()
    except TypeError:
        return None
    except Exception as exc:  # noqa: BLE001 - any other exception type is the finding
        return f"build() raised {type(exc).__name__}, not TypeError"
    return "build() returned without raising"


def gate_f3_malformed(root: Path = ROOT) -> None:
    """F3 (malformed half): every malformed fixture's `build()` raises TypeError."""
    bad = []
    for path in _fixtures(root, "malformed"):
        problem = _build_problem(_load_fixture(path))
        if problem:
            bad.append(f"{path.relative_to(root)}: {problem}")
    assert not bad, "F3: malformed fixtures:\n" + "\n".join(bad)


def _members(node: ast.expr) -> list[ast.expr]:
    """The union members of an annotation, with `None` and `Optional[...]` stripped."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        node = ast.parse(node.value, mode="eval").body
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _members(node.left) + _members(node.right)
    if isinstance(node, ast.Subscript) and ast.unparse(node.value).split(".")[-1] == "Optional":
        return _members(node.slice)
    if isinstance(node, ast.Constant) and node.value is None:
        return []
    return [node]


def gate_f4(root: Path = ROOT) -> None:
    """F4: a dataclass field typed `str` or `tuple[str, ...]` has a name in the allowlist."""
    allowed = set(family_config(root)["str_allowlist"])
    bad = []
    for path, tree in src_trees(root):
        for cls in dataclasses_of(tree):
            for field in fields_of(cls):
                name = ast.unparse(field.target)
                texts = [ast.unparse(m) for m in _members(field.annotation)]
                if name not in allowed and any(t in STR_TYPES for t in texts):
                    bad.append(f"{where(root, path, field.lineno)}: {cls.name}.{name}")
    assert not bad, "F4: str fields outside the allowlist:\n" + "\n".join(bad)


def _declared(tree: ast.Module) -> list[tuple[int, str]]:
    found = [(n.lineno, n.name) for n in ast.walk(tree) if isinstance(n, _DEFS)]
    found += [(n.lineno, n.arg) for n in ast.walk(tree) if isinstance(n, ast.arg)]
    for cls in dataclasses_of(tree):
        found += [(f.lineno, ast.unparse(f.target)) for f in fields_of(cls)]
    return found


def gate_f5(root: Path = ROOT) -> None:
    """F5: no field, parameter, function or class is named for another home."""
    names = {n.lower() for n in family_config(root)["boundary_names"]}
    bad = [
        f"{where(root, path, lineno)}: {text}"
        for path, tree in src_trees(root)
        for lineno, text in _declared(tree)
        if text.lower() in names
    ]
    assert not bad, "F5: names that belong to another home:\n" + "\n".join(bad)


def _module_assigns(tree: ast.Module) -> list[tuple[int, list[str]]]:
    """Per module-level assignment: its line and the target name plus every string in its value."""
    found = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign):
            targets, value = [node.target], node.value
        else:
            continue
        texts = [t.id for t in targets if isinstance(t, ast.Name)]
        if value is not None:
            texts += [
                n.value
                for n in ast.walk(value)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)
            ]
        found.append((node.lineno, texts))
    return found


def gate_f6_hash(root: Path = ROOT) -> None:
    """F6 (hash half): no module-level assignment names or holds a word of the application."""
    bad = [
        f"{where(root, path, lineno)}: word with digest {digest(word)[:12]}"
        for path, tree in src_trees(root)
        for lineno, texts in _module_assigns(tree)
        for text in texts
        for word in WORD.findall(text)
        if digest(word) in APPLICATION_HASHES
    ]
    assert not bad, "F6: module-level defaults naming a consumer:\n" + "\n".join(bad)


def gate_f13(root: Path = ROOT) -> None:
    """F13: src never imports or names the other library of the family."""
    others = [n for n in FAMILY_NAMES if n != lib_name(root)]
    bad = [
        f"{where(root, path, lineno)}: {text}"
        for path, tree in src_trees(root)
        for lineno, text in identifiers(tree, defs=True)
        for other in others
        if other in text.lower()
    ]
    assert not bad, "F13: names of the other library:\n" + "\n".join(bad)


def door_names(door: str) -> list[str]:
    """The `__all__` of an imported door."""
    return list(importlib.import_module(door).__all__)


def _snippets(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        return FENCE.findall(text)
    return [text] if path.suffix == ".py" else []


def _bad_module(name: str, lib: str, doors: list[str]) -> bool:
    parts = name.split(".")
    if parts[0] != lib:
        return False
    return any(p.startswith("_") for p in parts) or (len(parts) > 1 and name not in doors)


def _bad_imports(node: ast.AST, lib: str, doors: list[str]) -> list[str]:
    if isinstance(node, ast.Import):
        return [a.name for a in node.names if _bad_module(a.name, lib, doors)]
    if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
        return []
    if _bad_module(node.module, lib, doors):
        return [node.module]
    if node.module.split(".")[0] != lib:
        return []
    exported = set(door_names(node.module)) if node.module in doors else set()
    return [
        f"{node.module}.{a.name}"
        for a in node.names
        if a.name not in exported and f"{node.module}.{a.name}" not in doors
    ]


def _snippet_problems(source: str, lib: str, doors: list[str]) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [bad for node in ast.walk(tree) for bad in _bad_imports(node, lib, doors)]


def _api_problem(root: Path) -> str | None:
    lib = lib_name(root)
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    run = subprocess.run(  # noqa: S603 - fixed argv, no untrusted input
        [sys.executable, "-m", lib, "api"], cwd=root, env=env, capture_output=True, check=False
    )
    if run.returncode != 0:
        return f"`python -m {lib} api` exited {run.returncode}: {run.stderr.decode()[-300:]}"
    if run.stdout != (root / "docs" / "api-snapshot.txt").read_bytes():
        return "`api` output differs from docs/api-snapshot.txt"
    return None


def gate_f8(root: Path = ROOT) -> None:
    """F8: api output equals the snapshot; docs and guide tests import only the public surface."""
    problem = _api_problem(root)
    assert problem is None, f"F8: {problem}"
    lib, doors = lib_name(root), family_config(root)["doors"]
    files = [*(root / "docs").rglob("*.md"), *(root / "tests" / "guide").rglob("*")]
    bad = [
        f"{path.relative_to(root)}: {name}"
        for path in files
        if path.is_file()
        for source in _snippets(path)
        for name in _snippet_problems(source, lib, doors)
    ]
    assert not bad, "F8: private or unexported imports in docs:\n" + "\n".join(bad)


def gate_f15(root: Path = ROOT) -> None:
    """F15: no surface class outside `numeric_classes` defines an arithmetic dunder."""
    config = family_config(root)
    bad = []
    for door in config["doors"]:
        module = importlib.import_module(door)
        for name in door_names(door):
            obj = getattr(module, name)
            if not isinstance(obj, type) or name in config["numeric_classes"]:
                continue
            for klass in obj.__mro__:
                own = ARITHMETIC & vars(klass).keys() if klass.__module__ != "builtins" else set()
                bad += [f"{door}.{name} ({klass.__qualname__}): {op}" for op in sorted(own)]
    assert not bad, "F15: arithmetic on a non-numeric class:\n" + "\n".join(bad)


def gate_doors(root: Path = ROOT) -> None:
    """`_api.DOORS` equals `[tool.family].doors`."""
    api = importlib.import_module(f"{lib_name(root)}._api")
    doors = tuple(family_config(root)["doors"])
    assert tuple(api.DOORS) == doors, f"DOORS {tuple(api.DOORS)} != [tool.family].doors {doors}"
