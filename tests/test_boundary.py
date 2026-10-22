"""Family gate wrappers."""

import family


def test_f5_boundary_names():
    family.gate_f5()


def test_f6_no_consumer_default():
    family.gate_f6_hash()


def test_f13_other_library():
    family.gate_f13()
