"""R7: seeded properties of `common`, `relative_to` and `Terminal.relative_to` over small random trees."""

import random

from refdef import Aspect, Designation, Terminal

F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION


def _random(rng: random.Random) -> Designation:
    """A small designation over three aspects, two letters and two numbers, so overlaps occur."""
    levels = tuple(
        Designation().child(rng.choice((F, P, L)), rng.choice("AB"), rng.choice((1, 2))).levels[0]
        for _ in range(rng.randint(0, 4))
    )
    return Designation(levels, rng.choice(("", "", "T")))


def test_pair_properties():
    """R7: every argument is within `common`; the remainder is shorter by the common's length; Terminal follows `of`."""
    rng = random.Random(7)
    for _ in range(500):
        a, b = _random(rng), _random(rng)
        c = Designation.common(a, b)
        assert a.within(c)
        assert len(b.relative_to(c).levels) == len(b.levels) - len(c.levels)
        assert Terminal(a, ("1",)).relative_to(b).of == a.relative_to(b)


def test_common_of_three_has_every_argument_within():
    """R7: for three arguments each is within `common(*ds)`."""
    rng = random.Random(11)
    for _ in range(500):
        ds = [_random(rng) for _ in range(3)]
        c = Designation.common(*ds)
        assert all(each.within(c) for each in ds)
