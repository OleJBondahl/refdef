"""The lenient reader: text in, a value and the issues of every repair out."""

import re

from refdef.designation import Designation
from refdef.issues import Issue, IssueCode, Parsed
from refdef.level import Aspect, Level, coded_split
from refdef.terminal import Signal, Terminal

_SIGNS = re.compile(r"(==|\+\+|=|-|\+|%|#|\.)")
_DIGITS = re.compile(r"[A-Za-z]*([0-9]+)")
_BY_SIGN = {aspect.value: aspect for aspect in Aspect}


def _issue(issues: list[Issue], code: IssueCode, subject: str, message: str) -> None:
    issues.append(Issue(code, subject, message))


def _clean(text: str) -> str:
    """Outer whitespace off a piece of text; pins and names reach this as plain `str`."""
    return text.strip()


def _split_suffix(text: str) -> tuple[str, str, str]:
    """The text before the first of `: ; &`, that sign, and the rest (sign empty if none)."""
    cuts = [text.index(sign) for sign in ":;&" if sign in text]
    if not cuts:
        return text, "", ""
    cut = min(cuts)
    return text[:cut], text[cut], text[cut + 1 :]


def _take_top(head: str, issues: list[Issue]) -> tuple[str, str]:
    """The top node and the text after it; a head with no `<...>` at its start has no top."""
    if not (head.startswith("<") and ">" in head):
        return "", head
    end = head.index(">")
    raw, rest = head[1:end], head[end + 1 :]
    top = _clean(raw)
    if not top:
        _issue(issues, IssueCode.EMPTY_TOP, raw, "the top node is empty; dropped")
    elif top != raw:
        _issue(issues, IssueCode.WHITESPACE, raw, "outer whitespace of the top node removed")
    return top, rest


def _label(
    aspect: Aspect, body: str, why: tuple[IssueCode, str], issues: list[Issue]
) -> Level | None:
    """A label level for text that is not a code, with the issue `why`; None if Level refuses it."""
    try:
        level = Level(aspect, label=body)
    except TypeError:
        _issue(issues, IssueCode.BAD_LABEL, body, "the label holds a reserved character; dropped")
        return None
    _issue(issues, why[0], body, why[1])
    return level


def _not_code(aspect: Aspect, body: str, issues: list[Issue]) -> Level | None:
    """A level for a body that `coded_split` refused: a zero or oversize number, or free text."""
    shape = _DIGITS.fullmatch(body)
    why = (IssueCode.FREE_LABEL, "not letters and a number; kept as a label")
    if shape is not None and shape.group(1).strip("0"):
        why = (IssueCode.NUMBER_TOO_LARGE, "the number is over nine digits; kept as a label")
    elif shape is not None:
        why = (IssueCode.ZERO_NUMBER, "zero is not a number here; kept as a label")
    return _label(aspect, body, why, issues)


def _level(aspect: Aspect, raw: str, issues: list[Issue]) -> Level | None:
    """One body read as a level, with an issue per repair; None if nothing is left of it."""
    body = _clean(raw)
    if body != raw:
        _issue(issues, IssueCode.WHITESPACE, raw, "outer whitespace of the level removed")
    if not body:
        _issue(issues, IssueCode.EMPTY_LEVEL, raw, "a sign with nothing after it; dropped")
        return None
    split = coded_split(body)
    if split is None:
        return _not_code(aspect, body, issues)
    letters, digits = split
    if len(digits) > 1 and digits.startswith("0"):
        _issue(issues, IssueCode.LEADING_ZERO, body, "leading zero dropped")
    if letters != letters.upper():
        _issue(issues, IssueCode.LOWER_CASE, body, "letters raised to upper case")
    return Level(aspect, letters.upper(), int(digits))


def _signed(
    sign: str, body: str, levels: list[Level], aspect: Aspect, issues: list[Issue]
) -> Aspect:
    """Read one signed body onto `levels`; a dot takes the aspect of the previous level (M6)."""
    if sign == ".":
        _issue(issues, IssueCode.DOT_LEVEL, body, "a dot read as a level of the same aspect")
        aspect = levels[-1].aspect if levels else aspect
    else:
        aspect = _BY_SIGN[sign]
    level = _level(aspect, body, issues)
    if level is not None:
        levels.append(level)
    return aspect


def _levels(head: str, bare: Aspect, issues: list[Issue]) -> tuple[Level, ...]:
    """Split the head on signs and read each body; a dot repeats the aspect before it."""
    parts = _SIGNS.split(head)
    levels: list[Level] = []
    aspect = bare
    if _clean(parts[0]):
        _issue(issues, IssueCode.NO_SIGN, parts[0], f"no sign; read as {bare.name.lower()}")
        first = _level(aspect, parts[0], issues)
        if first is not None:
            levels.append(first)
    elif parts[0]:
        _issue(issues, IssueCode.WHITESPACE, parts[0], "whitespace before the first sign removed")
    for sign, body in zip(parts[1::2], parts[2::2], strict=True):
        aspect = _signed(sign, body, levels, aspect, issues)
    return tuple(levels)


def _pins(rest: str, issues: list[Issue]) -> tuple[str, ...]:
    """The pins of a terminal: split on `:`, strip each, drop the empty ones."""
    pins = []
    for raw in rest.split(":"):
        pin = _clean(raw)
        if pin != raw:
            _issue(issues, IssueCode.WHITESPACE, raw, "outer whitespace of the pin removed")
        if pin:
            pins.append(pin)
        else:
            _issue(issues, IssueCode.EMPTY_PIN, raw, "an empty pin; dropped")
    return tuple(pins)


def _signal(design: Designation, rest: str, issues: list[Issue]) -> Designation | Signal:
    """A signal named by the rest; a bare designation if the name is empty."""
    name = _clean(rest)
    if name != rest:
        _issue(issues, IssueCode.WHITESPACE, rest, "outer whitespace of the name removed")
    if not name:
        _issue(issues, IssueCode.EMPTY_NAME, rest, "an empty signal name; dropped")
        return design
    return Signal(design if design.levels or design.top else None, name)


def _finish(
    design: Designation, sign: str, rest: str, issues: list[Issue]
) -> Designation | Terminal | Signal:
    """Attach the suffix: pins make a terminal, a name a signal, `&` is dropped with an issue."""
    if sign == ":":
        pins = _pins(rest, issues)
        return Terminal(design, pins) if pins else design
    if sign == ";":
        return _signal(design, rest, issues)
    if sign == "&":
        _issue(issues, IssueCode.UNSUPPORTED_SUFFIX, sign + rest, "the document suffix is dropped")
    return design


def parse(text: str, *, bare: Aspect) -> Parsed[Designation | Terminal | Signal]:
    """Read text as a designation, terminal or signal, with an issue for each repair.

    `bare` is the aspect of text before the first sign. Never raises for content.
    """
    if not isinstance(text, str) or not isinstance(bare, Aspect):
        msg = "parse takes a str and a bare Aspect"
        raise TypeError(msg)
    text = _clean(text)
    issues: list[Issue] = []
    if not text:
        _issue(issues, IssueCode.EMPTY, text, "nothing to read")
        return Parsed(Designation(), tuple(issues))
    head, sign, rest = _split_suffix(text)
    top, head = _take_top(head, issues)
    design = Designation(_levels(head, bare, issues), top)
    return Parsed(_finish(design, sign, rest, issues), tuple(issues))
