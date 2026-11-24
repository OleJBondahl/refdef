# Changelog

This file holds one section per release of refdef, newest first.
Every change to the public surface gets a line under Unreleased until the release is cut.

## Unreleased

- `NaturalKey`: the type `natural_key` returns (a tuple of the run keys and the raw text) instead of `tuple[Any, ...]`; keys compare and sort exactly as before.
- `Scheme.sign_characters()`: the signs of the aspects that are on, joined in aspect order (`=-+` for `STANDARD`).
- `render(..., sign=)`: a given string replaces every sign between levels and drops the leading one, so `=A1+C1-K1` prints `A1-C1-K1` with `sign="-"`. It must be non-empty, without whitespace or a path separator.
- `LetterRule.reserved` and `Scheme.extend(reserved=)`: letters a code should not start with. `check` reports one as the new advisory `IssueCode.RESERVED_LETTER`, which never refuses a designation; `STANDARD` reserves none.

## 0.3.1 (2026-10-26)

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
