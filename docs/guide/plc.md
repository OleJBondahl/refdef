# PLC addresses

`refdef.plc` holds the direct address form common to PLC programming languages: a memory area, an
optional size and a dotted path, with `*` for an incomplete address. `as_bit` is the one
normalisation: a size-less dotted address gets the bit size.

```python
from refdef.plc import parse_address
address = parse_address("%Q7.5").value
print(address)                                  # %Q7.5
print(address.as_bit())                         # %QX7.5
print(parse_address("%QW4").value.as_bit())     # %QW4
print(parse_address("%I*").value)               # %I*
```

An `Address` is also built from its parts; the path is a tuple of ints.

```python
from refdef.plc import Address, Memory, Size
print(Address(Memory.MARKER, Size.WORD, (12,)))  # %MW12
```

Text that is not an address gives no value and a `NOT_ADDRESS` issue. Outer whitespace and leading
zeros are repaired, each with an issue that names the repaired text: the whole text for the
whitespace, and one issue per path element for the zeros.

```python
from refdef.plc import parse_address
result = parse_address("%Z9")
print(result.value)                             # None
print(result.issues[0].code.name)               # NOT_ADDRESS
result = parse_address(" %IX00.2.010 ")
print(result.value)                             # %IX0.2.10
print([(i.code.name, i.subject) for i in result.issues])  # [('WHITESPACE', ' %IX00.2.010 '), ('LEADING_ZERO', '00'), ('LEADING_ZERO', '010')]
```

A channel tag such as `-KE1:DI03` is a `Terminal`. A `ChannelTag` pairs it with an optional
address and prints as the terminal alone.

```python
from refdef import Aspect, parse
from refdef.plc import ChannelTag, Memory, Size, parse_address
terminal = parse("-KE1:DI03", bare=Aspect.PRODUCT).value
tag = ChannelTag(terminal, parse_address("%IX0.2").value)
print(tag)                                      # -KE1:DI03
print(tag.address)                              # %IX0.2
print(tag.address.memory is Memory.INPUT)       # True
print(tag.address.size is Size.BIT)             # True
```
