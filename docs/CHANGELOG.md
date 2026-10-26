# Changelog

This file holds one section per release of refdef, newest first.
Every change to the public surface gets a line under Unreleased until the release is cut.

## Unreleased

- Class A (items with two or more purposes, such as assemblies and controllers) is in the standard table.
- Class table version 2: adds class A; the table source is `scripts/classes.csv`.

## 0.3.0 (2026-10-24)

- Export `LetterRule` and `ClassTable` from `refdef`.

## 0.2.0 (2026-10-23)

- Add `lowest_free(taken, reserved=(), *, first=1)`: the lowest free number over plain ints.
- `Scheme.extend` takes `never`: letters barred in addition to the scheme's own, as any iterable of A-Z letters (a bare `str` is a `TypeError`).

## 0.1.0 (2026-10-22)

- Add `Aspect`, `Level`, `Designation`, `Terminal`, `Signal`, `Issue`, `IssueCode`, `Parsed` and `render`.
- Add `parse`.
- Add `within`, `relative_to` and `common` on `Designation`, and `relative_to` on `Terminal` and `Signal`.
- Add `allocate`, `number_group`, `natural_key` and `sort_key`.
- Add the door `refdef.plc`: `Memory`, `Size`, `Address`, `ChannelTag` and `parse_address`.
- Add `Scheme`, `ClassEntry`, `STANDARD` and `check`.
- Add class table version 1: 17 main letters and 166 two-letter codes (first version, no moved code).
- First release: the package scaffold with the family rule gates, standard library only.
