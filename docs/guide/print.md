# Print

`str(d)` is the strict form: every sign, no padding. `render` adds three explicit options.

```python
from refdef import Aspect, Designation, render
P = Aspect.PRODUCT
k1 = Designation().child(P, "U", 1).child(P, "U", 2).child(P, "K", 3)
print(k1)                                                                        # -U1-U2-K3
print(render(Designation().child(P, "W", 25).child(P, number=1), dotted=(P,)))   # -W25.1
print(render(Designation().child(P, "W", 1), pad={"W": 4}))                      # -W0001
print(render(k1, bare=True))                                                     # U1-U2-K3
```

`pad` pads the number of coded levels by their letters, `dotted` prints a number-only level after
a level of its aspect with a dot, and `bare` leaves out the first sign.
