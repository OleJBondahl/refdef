# Class table

`STANDARD` is the shipped scheme: function, product and location on, one to three letters without
`I` and `O`, and a versioned table of class codes with a short title each. The table has its own
version, independent of the library version, and the changelog names each moved code.

```python
from refdef import STANDARD
print(STANDARD.classes.version, STANDARD.classes.depth)   # 1 2
print(STANDARD.classes.get("KEB").code)   # KE
print(STANDARD.classes.get("KX"))   # None
```

`get` looks up the first `depth` letters of a code and never falls back to a shorter prefix, so
`KX` is unknown although `K` is a class.

A project adds its own classes, or turns on more aspects, with `extend`. It returns a new scheme
and leaves `STANDARD` alone; an entry with a known code replaces the old one.

```python
from refdef import Aspect, ClassEntry, Scheme, check, parse
j = STANDARD.extend(ClassEntry("J", "board connector"))
print(isinstance(j, Scheme), j.name)   # True standard
P = Aspect.PRODUCT
print(check([parse("-J1", bare=P).value], j))   # ()
print([i.code.value for i in check([parse("-J1", bare=P).value], STANDARD)])   # ['unknown_class']
```

`never` bars further letters on top of the scheme's own: the new set is the union, so `I` and `O`
stay barred and `extend` never lifts a letter.

```python
strict = STANDARD.extend(never=frozenset("A"))
print([i.code.value for i in check([parse("-A1", bare=P).value], strict)])   # ['never_letter', 'unknown_class']
```
