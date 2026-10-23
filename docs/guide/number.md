# Number

`allocate` returns the lowest free number of a class, given what is taken and what is reserved.
`number_group` numbers several levels in order, each after the earlier ones. Neither stores
anything: you pass what is taken, and `taken` is never changed.

```python
from refdef import Aspect, Level, allocate, number_group
P = Aspect.PRODUCT
taken = {Level(P, "K", 1), Level(P, "K", 2)}
print(allocate(P, "K", taken))                                                   # 3
print(allocate(P, "K", set(), reserved={Level(P, "K", 1)}))                      # 2
print(allocate(P, "K", taken, first=10))                                         # 10
group = number_group(P, ["K", "K", "F"], taken={Level(P, "K", 2)})
print([level.text for level in group])                                           # ['K1', 'K3', 'F1']
```

`first` is at least 1. A reserved level is skipped like a taken one.

`lowest_free` is the same rule over plain positive integers, such as terminals on a rail, cores of
a cable or screw positions.

```python
from refdef import lowest_free
print(lowest_free({1, 2}, reserved={3}))                                         # 4
print(lowest_free({1, 2}, first=10))                                             # 10
```

A reserved number is skipped like a taken one; the caller keeps the reserved set.
