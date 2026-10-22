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
