# Sort

`natural_key` orders digit runs by value and text runs as text, numbers before text, and breaks a
tie on the raw text. `sort_key` gives a designation one key per level, ranked by the aspects you
list; `aspects` has no default. An aspect you leave out ranks after the listed ones.

```python
from refdef import Aspect, natural_key, parse, sort_key
F, P, L = Aspect.FUNCTION, Aspect.PRODUCT, Aspect.LOCATION
print(natural_key("W2") < natural_key("W10"))                                    # True
print(natural_key("X01") < natural_key("X1"))                                    # True
print(natural_key("b", case_sensitive=False) < natural_key("C", case_sensitive=False))  # True
tags = [parse(text, bare=P).value for text in ["-W10", "-W2", "-K1", "+ER-K1", "+3"]]
ordered = sorted(tags, key=lambda d: sort_key(d, aspects=(F, L, P)))
print(" ".join(str(d) for d in ordered))                                         # +3 +ER-K1 -K1 -W2 -W10
```
