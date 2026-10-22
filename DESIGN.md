# refdef: design

refdef is a small Python library for reference designations: the tags that name the things in a plant, a machine or a cabinet (`=M1+ER-K2`, `-X1:3`, `-KE1:DI03`). It is compatible with IEC practice. This file is the current truth of the design; `RULES.md` holds the rules every change must keep, and the two change only through the process in the last section.

## Purpose

A designation names an occurrence of a thing by its place in one or more trees: what it does (function, `=`), what it is (product, `-`) and where it sits (location, `+`). Every electrical engineer who scripts, generates or checks drawings, lists and PLC configurations in Python meets these tags, and every tool passes them around as strings and then re-splits, re-sorts and re-checks them in slightly different ways. refdef gives the tag one structured value, one strict way to print it, one lenient way to read it, and the operations a tool needs on top: relative paths, common prefixes, free-number allocation, natural sort, a class-code table and a check that reports issues. It has no runtime dependency, does no I/O and holds no global state.

## The family

Three libraries share the work, and each fact has one home:

- `symdef` draws: symbols, frames, markers, their geometry and styles.
- `elecdef` says what a thing is: kinds of devices, their properties, terminal markings and internal links.
- `refdef` says what a thing is called: designations, their structure, printing, reading, numbering and order.

symdef draws a thing, elecdef says what it is, refdef says what it is called; an application connects and lays out. The three are basic building blocks for electrical work in Python, written for every electrical engineer who works there, and each stands alone. A fact never has two homes; what a terminal number means is an `elecdef` fact, how it prints after the colon is a `refdef` fact. None of the three imports another, and none names an application that uses it.

## The core model

**Aspect.** An enum whose value is the sign: `FUNCTION "="`, `PRODUCT "-"`, `LOCATION "+"`, `TYPE "%"`, `OTHER "#"`, `ASSIGNMENT "=="`, `SITE "++"`. The first three are on in the shipped scheme; the other four parse always and are off until a project turns them on.

**Level.** One step in a tree: an aspect with class letters and a number (`-K2`), a number alone (`+3`), or a verbatim label (`+ER`, `-PE_BAR`). A string has exactly one value: letters need a number, so letters alone are a label; a number is an `int` from 1 to 999,999,999 with no padding and no meaning; a label is stripped, non-empty, holds no sign or separator character (`= - + % # : ; & < > .`) and is never shaped like a code (ASCII letters then digits worth 1 to 999,999,999, so `K1` and `7` are refused as labels while `K0` is one), so what it prints reads back to itself. Code letters are upper case. Whether the letters form a known class is not a construction rule, so a designation from any era can be built.

**Designation.** A frozen tuple of levels and an optional top node (printed `<...>`). The empty designation is the root. Level order is kept as given; nothing re-sorts aspects. The builder is the constructor taking levels and `child(aspect, code, number, label)`, and nothing else: two designations are joined through their levels, `Designation(tag.levels + d.levels)`, and no operator builds a value. It is viewed with `only(*aspects)`, `parent(aspect)` and `last`. A top node, when given, is stripped, non-empty and holds none of `> : ; &`.

**Scheme.** A frozen value passed to every check: the aspects that are on, a `LetterRule` (letter count, letters that never appear) and a `ClassTable`. `STANDARD` is the shipped scheme. `scheme.extend(*entries, aspects=...)` returns a new scheme with project classes overlaid and further aspects on; a project that uses `J` for its board connectors adds `ClassEntry("J", "board connector")` this way.

**Parse and render.** `str(d)` prints strictly: every level with its sign, no padding, no separators. `render(d, pad=, dotted=, bare=)` adds the dialects a caller may want: `pad={"W": 4}` prints `-W0001`; `dotted=(Aspect.PRODUCT,)` prints a number-only sub-level as `-W25.1`; `bare=True` drops the first sign. `parse(text, bare=)` reads leniently and returns `Parsed(value, issues)`: lower-case code letters are raised, leading zeros dropped, a dot read as a sub-level, text before the first sign taken as the aspect the caller names in `bare` (a required keyword: which aspect a signless tag means is the caller's convention), anything that is not letters and a number kept verbatim as a label, each with a named issue. Nothing is coerced to a default letter or number, and nothing raises for content. `parse` knows shape only; `check(designations, scheme)` holds every scheme rule: an aspect that is off, a letter count, a letter that never appears, an unknown class, a duplicate. An `Issue` is a code from a closed enum of 21 (16 from `parse` and `parse_address`, 5 from `check`, listed in R6), a subject and a message; the caller decides what is fatal. A digit run of zero or over nine digits reads as a label with an issue.

**Tree arithmetic.** Every operation works per aspect. `d.within(root)` holds when, for each aspect both share, the root's levels are a head of `d`'s; an aspect missing from either side constrains nothing; a root with a top node matches only that top. `d.relative_to(root)` drops the matched heads and keeps the rest in order, so `=U1=P1+ER+C1-K1` relative to the unit root `=U1+ER` is `=P1+C1-K1`, and a cable `=U1-W1` with no location prints `-W1` inside that unit. `Designation.common(*ds)` is the longest shared head per aspect, ordered as the first argument; it is within every argument. Units as atoms is this: a unit's own document prints each tag relative to the unit's root.

**Numbering.** `allocate(aspect, code, taken, reserved, first=1)` returns the lowest free number: the first `n` from `first` whose level is in neither collection. Gaps refill unless the caller lists them as reserved. `number_group(aspect, codes, taken, reserved)` numbers a sequence of codes in one go and feeds each result back into `taken`. refdef owns no store of retired numbers; what forms a sibling group and what stays reserved are the caller's facts.

**Sorting.** `natural_key(text, case_sensitive=True)` orders digit runs by value and text runs as text, numbers first, with the raw text as the last tie-break (`X01` before `X1`). `sort_key(d, aspects=, case_sensitive=True)` is one pair per level, aspect rank then the natural key of the level text; `aspects` is a required keyword, since the order of aspects is the caller's convention, and an unlisted aspect ranks after the listed ones.

**Terminals and signals.** `Terminal(of, pins)` prints `-K1:13`, `-X1:L1:1`, `-A2:J7:3`, `-X1:OUT1-`; a pin is stripped, non-empty text without `:` (so `+`, `-`, `;`, `<` and inner spaces are allowed, and every pin reads back), kept verbatim, and its meaning is an `elecdef` fact. `Signal(of, name)` prints `;NAME` or `-K1;NAME`; the name is stripped, non-empty, free text, and `of` is `None` or a designation with a level or a top (an empty designation is refused). Both have `relative_to`. refdef never reads inside a pin or a name. Wires and cables need no type of their own: `-W25`, `=FIRE-W25`, a core as a sub-level.

**PLC.** `refdef.plc` holds the direct-address form common to PLC programming languages: `Address(memory, size, path)` for `%IX0.0`, `%QW4`, `%M10.3` and the incomplete `%I*`, with `as_bit()` normalising `%Q7.5` to `%QX7.5`, and `parse_address(text)`. A channel tag such as `-KE1:DI03` is a `Terminal`; `ChannelTag(terminal, address)` pairs it with an optional address (named so it does not collide with `elecdef`'s channel). Vendor address dialects are separate modules, added when an application needs one.

## The class table

`refdef.tables.standard` is a generated Python module holding `ClassTable(name="standard", version="1", depth=2, entries=(...))`: the single letters that name the main classes and the two-letter codes beneath them, as electrical practice uses them, each with a short title in our own words. A title names the typical device of the class (owner 2026-10-22); a device's own facts are `elecdef`'s knowledge. `depth=2` means `check` tests a code by its first two letters, so a three-letter code passes when its two-letter parent exists. The code index is built once per table.

The table has its own version line, independent of the library version. A moved, added or removed code bumps `version`, ships as a new entry tuple under the same `STANDARD` name, and is named in the changelog. A project pins the library version and gets the table that version carries; a second table, for another code set or a translation keyed by code, is a further module and a further scheme constant.

## The public surface

`refdef.__all__`: `Aspect`, `Level`, `Designation`, `Terminal`, `Signal`, `Scheme`, `ClassEntry`, `STANDARD`, `parse`, `Parsed`, `render`, `check`, `Issue`, `IssueCode`, `allocate`, `number_group`, `natural_key`, `sort_key`. `refdef.plc.__all__`: `Memory`, `Size`, `Address`, `ChannelTag`, `parse_address`. `ClassTable` and `LetterRule` are reached through `Scheme`. An application imports these names and nothing below them. Every surface name has a docstring of one summary line and at most two lines of why, an entry in the generated API reference and a runnable example in the guide (family rule F9). No surface class overloads an operator; one spelling builds, one reads, one prints (F15). `python -m refdef api` prints the two `__all__` tuples with every surface signature; `docs/api-snapshot.txt` holds that output byte for byte, and a change to it is a reviewed design change (family rules F8 and F12).

## Docs and agents

The docs site is GitHub Pages, built with Zensical from `docs/`, with the API reference generated from the docstrings. It ships with the first public release and has four parts: a guide (build, print, read, check, number, sort) in which every surface name has a runnable example, the API reference, `DESIGN.md` and `RULES.md` rendered as they are, and a changelog that names every moved class code.

Two files are written for agents (family rule F16). `llms.txt` at the docs site root lists, in plain text, what refdef is, the URL of each docs page, the surface names with one line each, and the rules in one line each. `AGENTS.md` in the repository root names the docs site, the surface command (`python -m refdef api`) and snapshot (`docs/api-snapshot.txt`), the guide, `DESIGN.md` and `RULES.md`; it says which files change only with a design review (`DESIGN.md`, `RULES.md`, `docs/api-snapshot.txt`, `src/refdef/tables/`, `tests/corpus/`) and that a need the surface does not meet is a reviewed design change and never a workaround. The docs build is a gate: a surface name without an example, or an example that does not run, fails it (F9).

## Out of scope

refdef does not hold: the meaning of a pin or terminal number, a device's recommended class code, a drawing of anything, a store of retired numbers or a numbering file, document designations and their kind codes, signal-name rules, wire-number rules, vendor PLC dialects, the three-letter class level, other code sets, translations. Each is either another library's fact or a later, reviewed addition.

## How it changes

`DESIGN.md` and `RULES.md` are the contract. A pull request that edits either, changes `docs/api-snapshot.txt`, changes `src/refdef/tables/` or moves a golden under `tests/corpus/` carries a `Design-review:` trailer naming an approved review; `scripts/design_guard.py` fails the merge otherwise (family rule F12, refdef rule R3). An application whose need the surface does not meet opens a design review rather than a workaround on either side; a change that breaks a rule in `RULES.md` is not merged. Versions follow family rule F11; a changed printed form of an unchanged value moves the render golden (R3) and carries its changelog line, and a table change bumps the table's own version (R10).

Who approves is family rule F12: the maintainer approves the contract, and the design reviewer approves surface and table changes.

## Licence

refdef is MIT licensed, code and shipped class table alike (family rule F14). Open sources used are credited in one block in `README.md` (F7); no share-alike or non-commercial source is used.
