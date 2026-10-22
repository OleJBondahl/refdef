# refdef: agent guide

refdef is a library of reference designations: strict, typed, immutable Python values for the tags
that name things in a plant, with no runtime dependency. A sibling library follows the same family rules.
Docs: <https://olejbondahl.github.io/refdef/>. Surface: `python -m refdef api`.

## Read first

Read `DESIGN.md`, then `RULES.md`. They bind: a change follows RULES.md, and code that disagrees
with them is wrong. Family rules F1-F17 are shared with the sibling library; R1-R12 are ours.

## Gate

`just ci` runs locally (no hosted gate beyond one CI job): ruff, ty, vulture, pytest with a 95 %
coverage floor, the tests on Python 3.14, the two guards, and the strict site build. Its last
stdout line is `site built: .site`. Each shared test guards one family rule:

- `test_deps` (F1): no runtime dependency, stdlib and the package only.
- `test_pure` (F2), `test_check` and `test_malformed` (F3): frozen values, no I/O, issues as values.
- `test_vocab` (F4): a closed vocabulary is never a bare `str`.
- `test_boundary` (F5, F6, F13): no boundary names, no application default, no sibling import.
- `test_wording` (F7 and the em-dash rule): no standard cited by number, clause or year.
- `test_surface` (F8, F15): the snapshot equals `python -m refdef api`; no operators on surface classes.
- `test_docs` (F9) and `test_site`: every name has a docstring and a runnable guide block.
- `test_lean` (F10): no nested def, 300 code lines, short docstrings, every noqa with a reason.
- `test_release_guard` (F11) and `test_design_guard` (F12): the guard scripts can fail.
- `test_licence` (F14), `test_agents` (F16), `test_standalone` (F17), `test_family_rules`, `test_pyproject_pins`.

## Process

- F12: a commit that touches a review path (`DESIGN.md`, `RULES.md`, `docs/api-snapshot.txt`,
  `src/refdef/tables/`, `tests/corpus/`) carries a trailer `Design-review: <ID>`. The maintainer approves the
  contract; the design reviewer approves surface and table changes.
- F13: a missing need is a reviewed extension of the surface, never a workaround or a private import.
- F17: name no application anywhere, in a tracked or an untracked file, or in a commit message.
- One source of truth for the surface: `docs/api-snapshot.txt`, regenerated with `just api-write`,
  never edited by hand. A new surface name adds its door to `[tool.family].doors` and `_api.DOORS`
  together, a docstring, a runnable guide block, a CHANGELOG line and its `docs/llms.txt` lines.
- The identical test set listed in `scripts/family_files.txt` is copied byte for byte between the
  sibling repositories; `scripts/family_compare.py` checks it. Edit it in both or in neither.

## Style

- `uv` only; no bare `python` or `pip`. Dependencies are exact pins (`name==X.Y.Z`).
- No em-dashes in any text file.
- Lean limits (F10): 15 statements, 12 branches, complexity 8, no nested `def`, 300 code lines per
  module, docstrings of one summary line plus at most two of why, `# noqa: CODE - reason`.
- Stage named paths with git; never `git add -A`.
