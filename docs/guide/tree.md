# Tree arithmetic

Every operation works per aspect. `within` holds when, for each aspect both share, the root's levels
are a head of the designation's. `relative_to` drops those heads and keeps the rest in order.

```python
from refdef import Aspect, Designation, parse
P = Aspect.PRODUCT
def d(text):
    return parse(text, bare=P).value
root = d("=U1+ER")
print(d("=U1=P1+ER+C1-K1").relative_to(root))   # =P1+C1-K1
print(d("=U1-W1").relative_to(root))            # -W1
print(d("=U1-W1").within(root))                 # True
print(d("-K1").within(root))                    # False
```

`Designation.common` is the longest head per aspect that all its arguments share, ordered as the
first argument.

```python
from refdef import Aspect, Designation, Terminal, Signal, parse
P = Aspect.PRODUCT
def d(text):
    return parse(text, bare=P).value
print(Designation.common(d("=A1+C1-K1"), d("=A1+C1-K2"), d("=A1+C2-F1")))   # =A1
print(Designation.common(d("=A1+C1-K1"), d("-K1")))                          # -K1
print(Designation.common() == Designation())                                 # True
```

A `Terminal` and a `Signal` are made relative through their designation; pins and names are kept.

```python
from refdef import Aspect, Signal, Terminal, parse
P = Aspect.PRODUCT
def d(text):
    return parse(text, bare=P).value
root = d("=U1+ER")
print(Terminal(d("=U1=P1+ER-X1"), ("L1", "1")).relative_to(root))   # =P1-X1:L1:1
print(Signal(d("=U1+ER"), "ALARM").relative_to(root))               # ;ALARM
```

## A unit's documents

One cell as the unit `-U1` sees it, as the unit `-U2` inside it sees it, and as a whole plant lists
it. There is no `+` operator: levels are joined by building a new `Designation` from them.

```python
from refdef import Aspect, ClassEntry, Designation, Level, STANDARD, Terminal
from refdef import allocate, check, render, sort_key
from refdef.plc import ChannelTag, parse_address
F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION
def join(*ds):
    return Designation(tuple(level for d in ds for level in d.levels))
scheme = STANDARD.extend(ClassEntry("J", "board connector"))
u1 = Designation().child(P, "U", 1)
u2 = u1.child(P, "U", 2)
k1 = u2.child(P, "K", allocate(P, "K", set(), reserved={Level(P, "K", 1)}))
er = Designation().child(L, label="ER")
fn = Designation().child(F, "M", 1)
x1 = u1.child(P, "X", 1)
ke1 = u1.child(P, "KE", 1)
tag = ChannelTag(Terminal(ke1, ("DI03",)), parse_address("%IX0.2").value)
print(join(fn, er, k1))                                         # =M1+ER-U1-U2-K2
print(join(fn, er, k1).only(L, P))                              # +ER-U1-U2-K2
print(k1.relative_to(u1))                                       # -U2-K2
print(k1.relative_to(u2))                                       # -K2
print(render(k1.relative_to(u1), bare=True))                    # U2-K2
print(Terminal(x1, ("L1", "1")).relative_to(u1))                # -X1:L1:1
print(Terminal(k1, ("13",)))                                    # -U1-U2-K2:13
print(f"{tag.terminal.relative_to(u1)}  {tag.address}")        # -KE1:DI03  %IX0.2
print(Designation.common(join(er, k1), join(er, x1)).only(L))   # +ER
print(check([k1, x1, ke1], scheme))                             # ()
print(" ".join(str(d) for d in sorted([x1, k1, ke1, u2], key=lambda d: sort_key(d, aspects=(F, L, P)))))  # -U1-KE1 -U1-U2 -U1-U2-K2 -U1-X1
```
