# Build

A designation is a tuple of levels, built by the constructor and `child`, never by an operator.

```python
from refdef import Aspect, Designation, Level
F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION
u1 = Designation().child(P, "U", 1)
k1 = u1.child(P, "U", 2).child(P, "K", 3)
print(k1)                                                  # -U1-U2-K3
print(Designation((Level(L, label="ER"),) + k1.levels))    # +ER-U1-U2-K3
print(Level(P, "K", 3).text)                               # K3
print(k1.parent())                                         # -U1-U2
print(Designation((Level(L, label="ER"),) + k1.levels).only(P))   # -U1-U2-K3
```

A level is upper-case letters with a number, a number alone, or a label. A label is never shaped
like a code, so `K1` and `7` cannot be labels (`K0` can). A malformed call raises `TypeError`.

```python
from refdef import Aspect, Level
try:
    Level(Aspect.PRODUCT, label="K1")
except TypeError:
    print("refused")                                       # refused
```

## Findings

A reader or a checker reports an `Issue` with an `IssueCode`, and a reader returns its value in `Parsed`.

```python
from refdef import Designation, Issue, IssueCode, Parsed
issue = Issue(IssueCode.EMPTY, "", "the text is empty")
parsed = Parsed(Designation(), (issue,))
print(parsed.issues[0].code.value)                         # empty
```
