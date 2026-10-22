# Read

`parse` reads text leniently: it returns the value it can make and an issue for each repair it made.
`bare` is the aspect of text before the first sign, and it has no default.

```python
from refdef import Aspect, parse
P = Aspect.PRODUCT
r = parse("=CS-CV01", bare=P)
print(r.value, [i.code.value for i in r.issues])   # =CS-CV1 ['free_label', 'leading_zero']
```

A missing sign takes the `bare` aspect, and a lower-case letter is raised to upper case.

```python
r = parse("K1", bare=P)
print(r.value, [i.code.value for i in r.issues])   # -K1 ['no_sign']
r = parse("-k1", bare=P)
print(r.value, [i.code.value for i in r.issues])   # -K1 ['lower_case']
```

A dot repeats the aspect of the level before it, and the printed form shows the sign.

```python
r = parse("-W25.1", bare=P)
print(r.value, [i.code.value for i in r.issues])   # -W25-1 ['dot_level']
```

A colon after the designation makes a `Terminal`, and a semicolon makes a `Signal`. A document
suffix is dropped with an issue.

```python
r = parse("-KE1:DI03", bare=P)
print(r.value, type(r.value).__name__)   # -KE1:DI03 Terminal
r = parse("-K1;SYSTEM_CAN_L", bare=P)
print(r.value, [i.code.value for i in r.issues])   # -K1;SYSTEM_CAN_L []
r = parse("-K1&2", bare=P)
print(r.value, [i.code.value for i in r.issues])   # -K1 ['unsupported_suffix']
```

Empty text gives an empty designation with an issue.

```python
r = parse("", bare=P)
print(repr(str(r.value)), [i.code.value for i in r.issues])   # '' ['empty']
```

`parse` never raises for content and takes no scheme: a check against a scheme is a later step.
