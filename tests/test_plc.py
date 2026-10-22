"""R11: the direct-address form round-trips, `as_bit` is the one normalisation."""

import itertools
from pathlib import Path
from typing import Any, cast

import pytest

from refdef import Aspect, Designation, IssueCode, Terminal, parse
from refdef.plc import Address, ChannelTag, Memory, Size, parse_address

CORPUS = Path(__file__).parent / "corpus" / "addresses.txt"
ACCEPTED, REJECTED = CORPUS.read_text(encoding="utf-8").split("# rejected\n")
ACCEPTED_LINES = ACCEPTED.split()
REJECTED_LINES = REJECTED.splitlines()
PATHS = [p for n in range(4) for p in itertools.product((0, 7, 12), repeat=n)]


def test_r11_corpus_is_big_enough():
    """R11: the corpus holds 30+ accepted lines and a rejected section."""
    assert len(ACCEPTED_LINES) >= 30
    assert len(REJECTED_LINES) >= 10


@pytest.mark.parametrize("line", ACCEPTED_LINES)
def test_r11_accepted_line_round_trips(line: str):
    """R11: each accepted line parses without an issue and prints back to itself."""
    result = parse_address(line)
    assert result.issues == ()
    assert str(result.value) == line


@pytest.mark.parametrize("line", REJECTED_LINES)
def test_r11_rejected_line_is_not_an_address(line: str):
    """R11, R4: each rejected line gives no value and one NOT_ADDRESS issue naming the text."""
    result = parse_address(line)
    assert result.value is None
    assert [(i.code, i.subject) for i in result.issues] == [(IssueCode.NOT_ADDRESS, line)]


def test_r4_outer_whitespace_is_repaired_with_an_issue():
    """R4, M13: outer whitespace is dropped and reported as `parse` reports it."""
    result = parse_address("  %QW4\n")
    assert [(i.code, i.subject) for i in result.issues] == [(IssueCode.WHITESPACE, "  %QW4\n")]
    assert str(result.value) == "%QW4"


def test_r4_leading_zeros_are_repaired_per_element():
    """R4, M13: each path element with leading zeros is repaired and named in its own issue."""
    one = parse_address("%I007")
    assert str(one.value) == "%I7"
    assert [(i.code, i.subject) for i in one.issues] == [(IssueCode.LEADING_ZERO, "007")]
    many = parse_address("%IX00.2.010")
    assert str(many.value) == "%IX0.2.10"
    assert [(i.code, i.subject) for i in many.issues] == [
        (IssueCode.LEADING_ZERO, "00"),
        (IssueCode.LEADING_ZERO, "010"),
    ]


def test_r4_nine_digit_limit_counts_after_the_zeros_are_stripped():
    """R4: `%I0000000001` is index 1; ten significant digits are still refused."""
    assert str(parse_address("%I0000000001").value) == "%I1"
    assert parse_address("%I1234567890").value is None


def test_r11_parse_address_refuses_a_non_str():
    """R11, F3: a wrong type is a malformed call."""
    with pytest.raises(TypeError):
        parse_address(cast("Any", 4))


def test_r11_as_bit_changes_only_a_sizeless_dotted_address():
    """R11: over Memory x Size x paths, `as_bit` adds BIT exactly when size is NONE and len > 1."""
    for memory, size, path in itertools.product(Memory, Size, PATHS):
        address = Address(memory, size, path)
        bit = address.as_bit()
        if size is Size.NONE and len(path) > 1:
            assert bit == Address(memory, Size.BIT, path)
        else:
            assert bit is address


def test_r11_as_bit_is_idempotent_and_prints_the_bit():
    """R11: `%Q7.5` becomes `%QX7.5`; a second call changes nothing."""
    address = parse_address("%Q7.5").value
    assert address is not None
    assert str(address) == "%Q7.5"
    assert str(address.as_bit()) == "%QX7.5"
    assert address.as_bit().as_bit() == address.as_bit()


def test_r11_incomplete_address_has_an_empty_path():
    """R11: `%I*` is an empty path, and it prints with the star."""
    address = parse_address("%I*").value
    assert address == Address(Memory.INPUT, Size.NONE, ())


@pytest.mark.parametrize(
    "args",
    [
        ("I", Size.NONE, ()),
        (Memory.INPUT, "", ()),
        (Memory.INPUT, Size.NONE, [0]),
        (Memory.INPUT, Size.NONE, (-1,)),
        (Memory.INPUT, Size.NONE, (True,)),
        (Memory.INPUT, Size.NONE, ("1",)),
        (Memory.INPUT, Size.NONE, (1_000_000_000,)),
    ],
)
def test_r11_malformed_address_raises(args: tuple[object, ...]):
    """R11, F3: a wrong type, a negative index or one above nine digits raises TypeError."""
    with pytest.raises(TypeError):
        Address(*cast("Any", args))


def test_r11_channel_tag_prints_the_terminal_only():
    """R11: `ChannelTag(parse("-KE1:DI03", bare=P).value, address)` prints `-KE1:DI03`."""
    terminal = parse("-KE1:DI03", bare=Aspect.PRODUCT).value
    address = parse_address("%IX0.2").value
    tag = ChannelTag(cast("Terminal", terminal), address)
    assert str(tag) == "-KE1:DI03"
    assert tag.address == address
    assert ChannelTag(cast("Terminal", terminal)).address is None


@pytest.mark.parametrize("args", [(Designation(),), ("-K1:1",), (None,)])
def test_r11_channel_tag_refuses_a_non_terminal(args: tuple[object, ...]):
    """R11, F3: the terminal must be a Terminal."""
    with pytest.raises(TypeError):
        ChannelTag(*cast("Any", args))


def test_r11_channel_tag_refuses_a_text_address():
    """R11, F3: the address must be None or an Address."""
    terminal = Terminal(Designation().child(Aspect.PRODUCT, "K", 1), ("1",))
    with pytest.raises(TypeError):
        ChannelTag(terminal, cast("Any", "%I0.0"))
