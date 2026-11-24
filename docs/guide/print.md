# Print

`str(d)` is the strict form: every sign, no padding. `render` adds four explicit options.

```python
from refdef import Aspect, Designation, render
P = Aspect.PRODUCT
k1 = Designation().child(P, "U", 1).child(P, "U", 2).child(P, "K", 3)
print(k1)                                                                        # -U1-U2-K3
print(render(Designation().child(P, "W", 25).child(P, number=1), dotted=(P,)))   # -W25.1
print(render(Designation().child(P, "W", 1), pad={"W": 4}))                      # -W0001
print(render(k1, bare=True))                                                     # U1-U2-K3
print(render(k1, sign="_"))                                                       # U1_U2_K3
```

`pad` pads the number of coded levels by their letters, `dotted` prints a number-only level after
a level of its aspect with a dot, `bare` leaves out the first sign, and `sign` prints the string you give in place of every sign and
leaves out the first, so a tag can be a file-name fragment without reading the printed text again.
It must be non-empty, with no whitespace and no path separator; a dotted level keeps its dot.
