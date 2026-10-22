# Terminals and signals

A `Terminal` is a designation and its pins; a `Signal` is a name on a designation, or alone. Pins
and names are opaque text: refdef never reads inside them.

```python
from refdef import Aspect, Designation, Signal, Terminal
P = Aspect.PRODUCT
k1 = Designation().child(P, "K", 1)
x1 = Designation().child(P, "X", 1)
print(Terminal(k1, ("13",)))                    # -K1:13
print(Terminal(x1, ("L1", "1")))                # -X1:L1:1
print(Terminal(x1, ("OUT1-",)))                 # -X1:OUT1-
print(Terminal(k1, ("A A 9",)))                 # -K1:A A 9
print(Signal(k1, "SYSTEM_CAN_L"))               # -K1;SYSTEM_CAN_L
print(Signal(None, "ALARM"))                    # ;ALARM
```

A terminal has at least one pin, and a signal on an empty designation is refused.

```python
from refdef import Designation, Signal
try:
    Signal(Designation(), "ALARM")
except TypeError:
    print("use None")                           # use None
```
