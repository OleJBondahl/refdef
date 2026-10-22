# Check

`check` tests designations against a `Scheme` and returns an issue for each finding. It reads the
scheme it is given and nothing else; `parse` never reports these codes. Terminals and signals are
not checked: pass their `of`.

```python
from refdef import Aspect, check, parse, STANDARD
P = Aspect.PRODUCT
print([i.code.value for i in check([parse("-KX1", bare=P).value], STANDARD)])   # ['unknown_class']
print([i.code.value for i in check([parse("-KEB1", bare=P).value], STANDARD)])  # []
```

A code is looked up by its first two letters, so `-KEB1` passes because `KE` is in the table.
The five codes are `aspect_off`, `letter_count`, `never_letter`, `unknown_class` and `duplicate`.

```python
two = [parse("-A1", bare=P).value, parse("-A1", bare=P).value]
print([i.code.value for i in check(two, STANDARD)])   # ['unknown_class', 'duplicate', 'unknown_class']
print([i.code.value for i in check([parse("%T1", bare=P).value], STANDARD)])   # ['aspect_off']
print([i.code.value for i in check([parse("-KI1", bare=P).value], STANDARD)])  # ['never_letter', 'unknown_class']
```

The aspects `%`, `#`, `==` and `++` parse always and are off until a scheme turns them on. A label
such as `+ER` is not a class tag, so it only meets the aspect rule.

```python
print(check([parse("+ER", bare=P).value], STANDARD))   # ()
```
