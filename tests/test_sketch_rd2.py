"""Sketch cases S01, S02, S18, S23-S25, S28-S33, S34-S40 on the real library, one function each."""

from typing import Any, cast

import pytest

from refdef import Aspect, Designation, Level, Signal, Terminal, parse, render

P, L = Aspect.PRODUCT, Aspect.LOCATION


def test_s01_letters_only_label_parses_as_label():
    """R2: `+ER` parses to a location level with the label ER, equal to the built designation."""
    assert parse("+ER", bare=P).value == Designation().child(L, label="ER")


def test_s02_letters_only_code_refused():
    """R2: a Level with letters-only code `ER` is refused with TypeError."""
    with pytest.raises(TypeError):
        Level(L, code="ER")


def test_s18_two_levels_with_free_label_and_leading_zero():
    """R4: `=CS-CV01` gives two levels, issues free_label and leading_zero, prints `=CS-CV1`."""
    result = parse("=CS-CV01", bare=P)
    assert len(cast("Any", result.value).levels) == 2
    assert [issue.code.value for issue in result.issues] == ["free_label", "leading_zero"]
    assert str(result.value) == "=CS-CV1"


def test_s23_channel_text_is_terminal_with_pin():
    """R2: `-KE1:DI03` parses to a Terminal whose pins are `("DI03",)`."""
    value = parse("-KE1:DI03", bare=P).value
    assert isinstance(value, Terminal)
    assert value.pins == ("DI03",)


def test_s24_label_case_kept():
    """R2: `-Psu_main` keeps the label case, so the first level's label is `Psu_main`."""
    assert cast("Any", parse("-Psu_main", bare=P).value).levels[0].label == "Psu_main"


def test_s25_lower_case_code_upper_cased_with_issue():
    """R4: `-k1` gives the code K and the single issue lower_case."""
    result = parse("-k1", bare=P)
    assert cast("Any", result.value).levels[0].code == "K"
    assert [issue.code.value for issue in result.issues] == ["lower_case"]


def test_s28_empty_text_gives_empty_issue_and_empty_designation():
    """R4: `parse("")` returns the empty designation with the single issue empty."""
    result = parse("", bare=P)
    assert [issue.code.value for issue in result.issues] == ["empty"]
    assert result.value == Designation()


def test_s29_pins_keep_any_text_but_colon():
    """R2: a pin may hold a trailing `-` or inner spaces: `OUT1-` and `A A 9` are whole pins."""
    assert cast("Any", parse("-X1:OUT1-", bare=P).value).pins == ("OUT1-",)
    assert cast("Any", parse("-K1:A A 9", bare=P).value).pins == ("A A 9",)


def test_s30_pad_option_zero_fills_number():
    """R3: `render(..., pad={"W": 4})` zero-fills the number of `-W1` to `-W0001`."""
    assert render(cast("Designation", parse("-W1", bare=P).value), pad={"W": 4}) == "-W0001"


def test_s31_top_node_prints_with_angle_brackets():
    """R3: the top node `<MCC 5>` is printed in front of the levels, `<MCC 5>+3+3`."""
    assert str(parse("<MCC 5>+3+3", bare=P).value) == "<MCC 5>+3+3"


def test_s32_text_without_sign_gets_minus_and_no_sign_issue():
    """R4: `K1` gives the single issue no_sign and prints with the sign, `-K1`."""
    result = parse("K1", bare=P)
    assert [issue.code.value for issue in result.issues] == ["no_sign"]
    assert str(result.value) == "-K1"


def test_s33_signal_text_is_signal():
    """R2: `-K1;SYSTEM_CAN_L` parses to a Signal that prints back unchanged."""
    value = parse("-K1;SYSTEM_CAN_L", bare=P).value
    assert isinstance(value, Signal)
    assert str(value) == "-K1;SYSTEM_CAN_L"


def test_s34_round_trip_tree_with_three_levels():
    """R1: `=A1+C1-K1` parses and prints back to itself."""
    assert str(parse("=A1+C1-K1", bare=P).value) == "=A1+C1-K1"


def test_s35_round_trip_label_level_between_codes():
    """R1: `=N-T1+L11` parses and prints back to itself."""
    assert str(parse("=N-T1+L11", bare=P).value) == "=N-T1+L11"


def test_s36_round_trip_label_with_underscore():
    """R1: `-PE_BAR` parses and prints back to itself."""
    assert str(parse("-PE_BAR", bare=P).value) == "-PE_BAR"


def test_s37_round_trip_three_product_levels():
    """R1: `+ER-U1-U2-K1` parses and prints back to itself."""
    assert str(parse("+ER-U1-U2-K1", bare=P).value) == "+ER-U1-U2-K1"


def test_s38_round_trip_terminal_with_pin_colon_digits():
    """R1: `-X1:L1:1` parses and prints back to itself."""
    assert str(parse("-X1:L1:1", bare=P).value) == "-X1:L1:1"


def test_s39_round_trip_top_node_with_number_levels():
    """R1: `<MCC 5>+3+3` parses and prints back to itself."""
    assert str(parse("<MCC 5>+3+3", bare=P).value) == "<MCC 5>+3+3"


def test_s40_round_trip_function_level_then_product_levels():
    """R1: `==F1++S1-K1` parses and prints back to itself."""
    assert str(parse("==F1++S1-K1", bare=P).value) == "==F1++S1-K1"
