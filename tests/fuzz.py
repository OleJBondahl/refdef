"""A seeded generator of valid refdef values and of hostile texts (stdlib only)."""

import random
import string

from refdef import Aspect, Designation, Level, Signal, Terminal

_ASPECTS = tuple(Aspect)
_LABEL_CHARS = string.ascii_letters + string.digits + " _,/*!?()[]å Ø æ é ü ß 😀 日"
_TOP_CHARS = _LABEL_CHARS + "<=-+%#."
_PIN_CHARS = string.ascii_letters + string.digits + " ;&<>+-.=_/å😀"
_NAME_CHARS = _LABEL_CHARS + ":;&"
_TEXT_CHARS = string.ascii_letters + string.digits + " =-+%#<>:;&.åØ😀日\t"
_NUMBERS = (1, 2, 9, 10, 99, 100, 999_999_998, 999_999_999)
_FIXED_LABELS = ("K0", "K1234567890", "0", "00", "1234567890", "Skjåp", "ER", "a b", "7 up", "😀")


def _text(rng: random.Random, chars: str, low: int = 1, high: int = 8) -> str:
    return "".join(rng.choice(chars) for _ in range(rng.randint(low, high)))


def _stripped(rng: random.Random, chars: str, banned: str = "") -> str:
    """A non-empty text without outer whitespace and without any `banned` character."""
    while True:
        text = _text(rng, chars).strip()
        if text and not set(banned) & set(text):
            return text


def _number(rng: random.Random) -> int:
    if rng.random() < 0.5:
        return rng.choice(_NUMBERS)
    return rng.randint(1, 10 ** rng.randint(1, 9) - 1)


def _label(rng: random.Random, aspect: Aspect) -> Level:
    """A label level, built by rejection against the real constructor."""
    if rng.random() < 0.15:
        return Level(aspect, label=rng.choice(_FIXED_LABELS))
    while True:
        text = _text(rng, _LABEL_CHARS).strip()
        try:
            return Level(aspect, label=text)
        except TypeError:
            continue


def level(rng: random.Random) -> Level:
    """One level of any aspect: coded, number only or label."""
    aspect = rng.choice(_ASPECTS)
    kind = rng.random()
    if kind < 0.45:
        letters = "".join(rng.choice(string.ascii_uppercase) for _ in range(rng.randint(0, 3)))
        return Level(aspect, letters, _number(rng))
    if kind < 0.6:
        return Level(aspect, number=_number(rng))
    return _label(rng, aspect)


def designation(rng: random.Random) -> Designation:
    """A designation with 0 to 5 levels and a top about a third of the time."""
    top = _stripped(rng, _TOP_CHARS) if rng.random() < 0.3 else ""
    return Designation(tuple(level(rng) for _ in range(rng.randint(0, 5))), top)


def terminal(rng: random.Random) -> Terminal:
    """A terminal of a designation (possibly empty) with 1 to 3 pins."""
    pins = tuple(_stripped(rng, _PIN_CHARS) for _ in range(rng.randint(1, 3)))
    return Terminal(designation(rng), pins)


def signal(rng: random.Random) -> Signal:
    """A signal whose `of` is None or a designation with a level or a top."""
    name = _stripped(rng, _NAME_CHARS)
    if rng.random() < 0.3:
        return Signal(None, name)
    while True:
        of = designation(rng)
        if of.levels or of.top:
            return Signal(of, name)


def value(rng: random.Random) -> Designation | Terminal | Signal:
    """A designation, a terminal or a signal, each equally likely."""
    return rng.choice((designation, terminal, signal))(rng)


def hostile_texts(rng: random.Random) -> list[str]:
    """Texts that must not break the reader: random, single signs, brackets, long digit runs."""
    texts = [_text(rng, _TEXT_CHARS, 0, 40) for _ in range(200)]
    texts += ["=", "-", "+", "%", "#", "==", "++", "."]
    texts += ["<>", "<", ">", ":", ";", "&", "", " ", "   ", "\t", " \n "]
    run = "9" * 5000
    texts += [run, "K" + run, "-" + run, "-K" + run, "=" + "0" * 5000]
    return texts
