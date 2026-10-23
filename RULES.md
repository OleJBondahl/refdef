# refdef: rules

These rules bind every implementation and every later change of refdef. The family rules F1-F17 are shared with elecdef and carried verbatim; the refdef rules R1-R12 add what is refdef's own and repeat no family rule. Each rule is one sentence and its GATE: the mechanical check that fails a breach, or "review" only where no mechanism can work, with the reason. A change to this file, to `DESIGN.md`, to `docs/api-snapshot.txt`, to `src/refdef/tables/` or to `tests/corpus/` needs a `Design-review:` trailer (F12, R3).

## refdef rules

- **R1. One value per string.** For every designation, terminal or signal value `v`, `parse(str(v), bare=a).value == v` for any aspect `a`, and for every string `s` that parses without an issue, `str(parse(s, bare=a).value) == s`. GATE: `tests/test_roundtrip.py`, a property test whose stdlib generator draws levels, labels, tops, pins and signal names from the full alphabets R2 allows (pins and names including `; & < > + - .` and inner spaces), plus `tests/corpus/strings.txt` of strings seen in real projects.
- **R2. The shapes that construct.** A `Level` has upper-case letters with a number, a number alone, or a stripped non-empty label without `= - + % # : ; & < > .`; a number is an `int` from 1 to 999_999_999; a label is never shaped like a code (ASCII letters, then digits worth 1 to 999_999_999, such as `K1`, `k01` or `7`), because `-K1` must read back as a coded level (`K0` and `K1234567890` are labels); a `Designation.top` is empty or stripped, non-empty and without `> : ; &`; a `Terminal` has at least one pin, each stripped, non-empty and without `:`; a `Signal.name` is stripped and non-empty, and a `Signal.of` is `None` or a designation with at least one level or a top (an empty `Signal.of` is refused, because `;N` must read back to the same value); any other shape is malformed and raises `TypeError` at construction (F3). GATE: `tests/test_malformed.py` holds one fixture per clause (the labels `K1`, `k01` and `7`, the numbers 0 and 1_000_000_000, and an empty `Signal.of` among them) and asserts `TypeError`; `tests/test_level.py` asserts every value that constructs prints and parses back to itself (R1).
- **R3. Strict render.** `str()` prints every level with its sign and never pads, dots or drops a sign; every dialect (`pad`, `dotted`, `bare`) is an explicit `render` option, and a change to any printed form moves the golden. GATE: `tests/test_render.py` asserts `str(v) == render(v)` over the round-trip corpus, compares `render` of `tests/corpus/strings.txt` under each option to `tests/corpus/render.txt` line by line, and asserts each option changes only the documented characters; `scripts/design_guard.py` watches `tests/corpus/` (F12).
- **R4. Lenient parse with issues.** `parse` and `parse_address` return a value and an issue tuple for any string, every lenient repair (case, leading zero, dot, missing sign, free label, unsupported suffix) is matched by an issue with its code, and no default letter or number is ever substituted; a digit run that is zero or longer than nine digits (the bound of R2) reads as a label with an issue. GATE: `tests/test_parse.py` feeds a fuzz corpus (random text, every sign alone, empty, whitespace) and asserts no exception, and asserts one issue per repair against a table of input, value and codes.
- **R5. Shape in parse, scheme in check.** `parse` takes no scheme, every rule that needs one (aspect on, letter count, never-letters (`Scheme.extend(never=)` takes any iterable of single A-Z letters and refuses a bare `str`), unknown class by `code[:depth]`, duplicate) lives in `check`, and no function reads a scheme or table other than through its argument. GATE: `tests/test_parse.py` asserts `parse`'s signature has no `scheme` parameter; `tests/test_check.py` has one case per check-family `IssueCode`, asserts `parse` never emits them, and an AST test in it fails the name `STANDARD` or an import from `refdef.tables` anywhere under `src/refdef` outside `scheme.py` and `__init__.py`.
- **R6. An issue is a code, a subject and a message.** `Issue` has exactly these three fields, no severity, and `IssueCode` is a closed enum of exactly 21 codes that every emitted issue uses: the parse family (16) `EMPTY`, `NO_SIGN`, `EMPTY_LEVEL`, `EMPTY_TOP`, `WHITESPACE`, `LOWER_CASE`, `LEADING_ZERO`, `ZERO_NUMBER`, `NUMBER_TOO_LARGE`, `FREE_LABEL`, `BAD_LABEL`, `DOT_LEVEL`, `EMPTY_PIN`, `EMPTY_NAME`, `UNSUPPORTED_SUFFIX`, `NOT_ADDRESS` (the last only from `parse_address`), and the check family (5) `ASPECT_OFF`, `LETTER_COUNT`, `NEVER_LETTER`, `UNKNOWN_CLASS`, `DUPLICATE`; the values are the lower-case names. GATE: `tests/test_check.py` asserts the field names of `Issue`, that the `IssueCode` names equal these 21, and that every issue any test produces has a code in `IssueCode`.
- **R7. Per-aspect tree arithmetic.** `within`, `relative_to` (on `Designation`, `Terminal` and `Signal`) and `common` follow the rule in `DESIGN.md` exactly, and every argument is within `common(*ds)`. GATE: `tests/test_tree.py` holds the unit-root, cable, mixed-order and top-node cases for all three types, and a property test asserting `a.within(common(a, b))`, `len(b.relative_to(common(a, b)).levels) == len(b.levels) - len(common(a, b).levels)` and `Terminal(d, p).relative_to(r).of == d.relative_to(r)` for random values.
- **R8. Numbering is pure.** `allocate` returns the lowest free number from `first` given `taken` and `reserved`, `lowest_free` does the same over plain ints, `number_group` equals `allocate` applied in sequence with each result added to `taken`, and refdef holds no numbering store. GATE: `tests/test_numbering.py` asserts `allocate` and `lowest_free` against a brute-force search, `lowest_free` against `allocate` over one class, and `number_group` against the sequential fold, for random inputs.
- **R9. One natural order.** `natural_key` orders digit runs by value and text runs as text, numbers before text, with the raw text as the last tie-break; `sort_key` is one `(aspect rank, natural_key(level.text))` pair per level, with the aspect order a required keyword and an unlisted aspect ranked after the listed ones in enum order. GATE: `tests/test_order.py` asserts the fixed cases (`-W2 < -W10`, `X01 < X1`, numbers before text), a property test that `sorted` by `sort_key` is a total order consistent with `natural_key` on single-level designations, and that `sort_key` has no default for `aspects`.
- **R10. The class table is versioned.** `ClassTable.version` is refdef's own line, bumps whenever the entry tuple changes, and the changelog names each moved code. GATE: `tests/test_table_version.py` hashes the entry tuple and compares it with the hash stored beside `version`, failing when the entries change and the version does not; the changelog line is review.
- **R11. One PLC grammar in the core.** `refdef.plc` holds only the direct-address form (`%` + memory area + optional size + dotted path, `*` for incomplete), with `as_bit` the one normalisation, and every vendor dialect is its own module behind its own type. GATE: `tests/test_plc.py` round-trips `tests/corpus/addresses.txt` through `parse_address` and `str`, asserts `as_bit` changes only a size-less dotted address, and `tests/test_boundary.py` fails a vendor name (`siemens`, `rockwell`, `omron`, `mitsubishi`, `beckhoff`) in `plc.py`.
- **R12. Pins and signal names are opaque.** refdef never reads inside a pin or a signal name: the only operations on them are the `:` split in `parse`, the `:` join in `render` and `natural_key`. GATE: an AST test in `tests/test_boundary.py` fails any attribute call, subscript or comparison on `pins`, a pin element or `Signal.name` under `src/refdef` outside those three sites; the F5 name list below catches a field that would hold their meaning.

## refdef's lists for the family gates

- F4 allowlist of `str` fields, by design: `Level.code` (class letters), `Level.label` (verbatim text), `Designation.top`, `Terminal.pins` (`tuple[str, ...]`, opaque by R12), `Signal.name` (opaque by R12), `ClassEntry.code`, `ClassEntry.title`, `ClassTable.name`, `ClassTable.version`, `Scheme.name`, `Issue.subject`, `Issue.message`. Every other closed set is an enum: `Aspect`, `IssueCode`, `plc.Memory`, `plc.Size`.
- F5 boundary names for refdef: F5's six (`rating`, `voltage`, `svg`, `x`, `y`, `page`) plus `marking`, `role`, `kind`, `potential`.
- F6 caller conventions refdef takes only as arguments: `bare` (which aspect a signless tag means, required), `aspects` (the sort order of aspects, required), `pad`, `dotted`, `first`, `case_sensitive`.
- F15 numeric types: none; no refdef surface class defines an arithmetic or bitwise dunder, and `Designation` is built by its constructor and `child()` only.

## Family rules

These rules bind elecdef and refdef alike, and symdef where it can (symdef has one runtime dependency, so F1 does not bind it). Both repositories carry this text verbatim in `RULES.md`,
and `tests/test_family_rules.py` in each compares it to the other's last release.

- **F1.** The library declares no runtime dependency and imports only the standard library and
  itself; libraries of the family never import each other.
  GATE: `tests/test_deps.py` asserts `dependencies = []` in `pyproject.toml` and walks every
  module's imports with `ast`, allowing only `sys.stdlib_module_names` and the package.
- **F2.** Every value is a frozen dataclass or an enum; the library performs no file, network,
  clock or random access.
  GATE: `tests/test_pure.py` fails a `@dataclass` without `frozen=True` and any import or name
  from `os`, `pathlib`, `io`, `socket`, `time`, `datetime`, `random`, `secrets`, `uuid` or a
  call to `open` under `src/`.
- **F3.** Validation returns issues as values and never raises for content; only a malformed
  call (a wrong type, a wrong kind of argument, or a shape the library's `RULES.md` names as
  malformed) raises `TypeError`.
  GATE: `tests/test_check.py` runs `check` over every malformed fixture in `tests/fixtures/`
  and asserts a non-empty issue tuple and no exception; `tests/test_malformed.py` asserts
  `TypeError` for each malformed-call fixture.
- **F4.** A closed vocabulary is an enum or a typed constant, never a string.
  GATE: `tests/test_vocab.py` fails any dataclass field annotated `str` that is not in the
  allowlist that the test names and `RULES.md` lists for that library.
- **F5.** A fact has one home across the family: `symdef` draws, `elecdef` says what a thing is,
  `refdef` says what it is called, a consumer connects and lays out.
  GATE: `tests/test_boundary.py` fails a field or function named for another home, from a list each
  library keeps in the test (for elecdef: `designation`, `tag`, `svg`, `x`, `y`, `page`; for refdef:
  `rating`, `voltage`, `svg`, `x`, `y`, `page`); the rest is review, because a
  duplicated meaning under a new name is invisible to a test.
- **F6.** A caller's convention (a padding, an ordering, a default, a project class) arrives as an
  argument or a value; no general function carries a caller's default. A fact the library itself
  defines (a block's default terminal markings, the shipped scheme's signs) is not a convention.
  GATE: the tests of every option-taking function pass the option explicitly, and
  `tests/test_boundary.py` fails a module-level default that names a consumer; what counts as a
  convention is review, because a test cannot tell a convention from a fact.
- **F7.** No paid standard is cited and no standard's wording is used; open sources are used
  only with the credit block in `README.md`.
  GATE: `tests/test_wording.py` fails a standards-body abbreviation followed by digits, an
  edition year beside a table or scheme name, or a clause reference (the pattern list lives in
  the test) anywhere under `src/`, `docs/`, `README.md` or
  `CHANGELOG.md` outside the README credit block, and asserts the credit block names every
  open source a `tables/` module header declares.
- **F8.** The public surface is the names in `__all__` of the top level and of each door, read
  by `python -m <library> api`, and it changes only with the snapshot.
  GATE: `tests/test_surface.py` compares `python -m <library> api` to `docs/api-snapshot.txt`
  byte for byte, and fails an import of a non-surface name in `docs/` and `tests/guide/`.
- **F9.** Every surface name has a docstring and a runnable example on the docs site.
  GATE: `tests/test_docs.py` asserts a non-empty docstring for every surface name, one fenced
  Python block naming it under `docs/guide/`, and runs every fenced block; the strict
  Zensical docs build runs in CI.
- **F10.** Code stays lean: a function has at most 15 statements, complexity 8 and 12 branches,
  no `def` inside a `def`; a module has at most 300 code lines; a docstring is one summary line
  plus at most two lines of why.
  GATE: ruff `PLR0915=15`, `C901=8`, `PLR0912=12` in `pyproject.toml`; `tests/test_lean.py` for
  nested defs, module lines and docstring shape; every `noqa` and `ty: ignore` names its reason
  on its line, checked by the same test.
- **F11.** Versions are semantic and every surface change carries a changelog line.
  GATE: `scripts/release_guard.py` in CI fails when `docs/api-snapshot.txt` differs from the
  last tag's copy and `CHANGELOG.md` has no line under the unreleased heading, and when a name
  disappeared without a major bump (minor before 1.0).
- **F12.** A pull request that edits `DESIGN.md` or `RULES.md`, or changes
  `docs/api-snapshot.txt`, or changes a shipped table under `src/<library>/tables/`, carries a
  `Design-review:` trailer naming an approved review. The maintainer approves a change to
  `DESIGN.md` or `RULES.md`; the design reviewer approves a surface or table change, and the
  maintainer sees it at the next review.
  GATE: `scripts/design_guard.py` in CI inspects every commit in the range touching those
  paths and fails one without the trailer; branch protection requires the job.
- **F13.** A consumer's missing need is met by a reviewed surface extension, never by a
  workaround in the consumer, a private import, a copy of the rule or a consumer-specific
  default in the library.
  GATE: `tests/test_boundary.py` fails an import or a name of another family library under `src/`, and
  `tests/test_standalone.py` (F17) fails an application's name; the consumer side is review, because the library cannot see the
  consumer's tree.
- **F14.** The library is MIT licensed, and the licence covers its code and its shipped tables.
  GATE: `tests/test_licence.py` asserts `LICENSE` holds the MIT text and `pyproject.toml`
  declares `license = "MIT"`, and fails a `tables/` module header that declares an open source
  whose licence is share-alike or non-commercial.
- **F15.** One public spelling per task: a second way to build, read or print the same value is
  not added, and no operator is overloaded to build a value; arithmetic belongs only to the
  numeric value types the library's `RULES.md` names.
  GATE: `tests/test_surface.py` fails an arithmetic or bitwise dunder (`__add__`, `__or__`,
  `__truediv__` and their kin) on a surface class that `RULES.md` does not name as numeric;
  a second spelling under a new name is review, because a test cannot see that two names do one
  task.
- **F16.** An agent finds everything from one place: `AGENTS.md` in the repository and `llms.txt`
  at the docs site root name the docs site, the surface command (`python -m <library> api`),
  the guide, `DESIGN.md` and `RULES.md`, and say that a change follows `RULES.md`.
  GATE: `tests/test_agents.py` asserts both files exist, name each of those five targets, and
  that every link in them resolves in the built site (the strict Zensical docs build).
- **F17.** The library stands alone: no file in the repository names an application that uses it.
  It is written for every electrical engineer, and its examples are general.
  GATE: `tests/test_standalone.py` lowercases every word in the tracked files and fails one whose
  SHA-256 is in the test's list of application-name hashes, so the test spells no name itself.
