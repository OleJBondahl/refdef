"""Sketch cases S03, S15, S16, S19-S22 on the real library and the real table, one function each."""

from refdef import STANDARD, Aspect, ClassEntry, Designation, IssueCode, check, parse

P, L = Aspect.PRODUCT, Aspect.LOCATION


def _codes(*texts: str) -> list[IssueCode]:
    designs = [d for d in (parse(t, bare=P).value for t in texts) if isinstance(d, Designation)]
    return [issue.code for issue in check(designs, STANDARD)]


def test_s03_check_skips_labels():
    """R5: `+ER` is a label, so check finds nothing in it."""
    assert check([Designation().child(L, label="ER")], STANDARD) == ()


def test_s15_kx_is_unknown():
    """R5: `-KX1` has no class `KX` in the table, so it is unknown."""
    assert _codes("-KX1") == [IssueCode.UNKNOWN_CLASS]


def test_s16_keb_passes_at_depth_two():
    """R5: `-KEB1` passes because its first two letters `KE` are in the table."""
    assert _codes("-KEB1") == []


def test_s19_duplicate_designation():
    """R5: `-A1 -A1` gives unknown_class, duplicate, unknown_class (A is no class)."""
    assert _codes("-A1", "-A1") == [
        IssueCode.UNKNOWN_CLASS,
        IssueCode.DUPLICATE,
        IssueCode.UNKNOWN_CLASS,
    ]


def test_s20_type_aspect_is_off():
    """R5: `%T1` is aspect_off in the shipped scheme and nothing else."""
    assert _codes("%T1") == [IssueCode.ASPECT_OFF]


def test_s21_barred_letter():
    """R5: `-KI1` uses the barred letter I."""
    assert IssueCode.NEVER_LETTER in _codes("-KI1")


def test_s22_extend_with_j():
    """R5: a scheme extended with `J` accepts `-J1` and stays hashable."""
    j = STANDARD.extend(ClassEntry("J", "board connector"))
    assert check([Designation().child(P, "J", 1)], j) == ()
    assert hash(j) is not None
