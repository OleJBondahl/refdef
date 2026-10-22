"""Family gate wrappers."""

import shutil
from pathlib import Path

import family
import pytest


def test_f8_snapshot_and_docs():
    family.gate_f8()


def _f8_copy(tmp_path: Path) -> Path:
    """A tmp copy of what gate_f8 reads, with an empty tests/guide."""
    for name in ("src", "docs"):
        shutil.copytree(
            family.ROOT / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__")
        )
    shutil.copy(family.ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    (tmp_path / "tests" / "guide" / "__pycache__").mkdir(parents=True)
    return tmp_path


def test_f8_skips_bytecode_but_still_fails_a_private_import(tmp_path):
    root = _f8_copy(tmp_path)
    (root / "tests" / "guide" / "__pycache__" / "x.pyc").write_bytes(b"\xff\xfe\x80\x00")
    family.gate_f8(root)
    lib = family.lib_name(root)
    (root / "tests" / "guide" / "test_g.py").write_text(
        f"from {lib}._private import x\n", encoding="utf-8"
    )
    with pytest.raises(AssertionError, match="private or unexported"):
        family.gate_f8(root)


def test_f15_no_arithmetic():
    family.gate_f15()


def test_doors_match_config():
    family.gate_doors()
