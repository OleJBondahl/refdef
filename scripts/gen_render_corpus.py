"""Generate tests/corpus/render.txt from tests/corpus/strings.txt.

Each output line holds four renders of the parsed string joined by TAB: plain, padded (W to 4
digits), dotted and bare, each with the printed pin or name suffix. render.txt is generated once and
reviewed by eye; the golden test in tests/test_render.py compares against it.
"""

from pathlib import Path

from refdef import Aspect, Designation, parse, render

CORPUS = Path(__file__).resolve().parent.parent / "tests" / "corpus"


def columns(line: str) -> str:
    """Return the four render columns of one canonical string, joined by TAB."""
    value = parse(line, bare=Aspect.PRODUCT).value
    if isinstance(value, Designation):
        d, suffix = value, ""
    else:
        d = value.of or Designation()
        suffix = str(value)[len(str(d)) :]
    return "\t".join(
        (
            render(d) + suffix,
            render(d, pad={"W": 4}) + suffix,
            render(d, dotted=(Aspect.PRODUCT,)) + suffix,
            render(d, bare=True) + suffix,
        )
    )


def main() -> None:
    """Write render.txt with one line per line of strings.txt, in the same order."""
    strings = (CORPUS / "strings.txt").read_text(encoding="utf-8").removesuffix("\n").split("\n")
    body = "".join(columns(line) + "\n" for line in strings)
    (CORPUS / "render.txt").write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
