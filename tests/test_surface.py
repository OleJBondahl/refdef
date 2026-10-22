"""Family gate wrappers."""

import family


def test_f8_snapshot_and_docs():
    family.gate_f8()


def test_f15_no_arithmetic():
    family.gate_f15()


def test_doors_match_config():
    family.gate_doors()
