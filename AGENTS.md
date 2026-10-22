# Agent guide

- Docs site: https://olejbondahl.github.io/refdef/
- Surface: `python -m refdef api`, snapshot in `docs/api-snapshot.txt`
- Guide: `docs/guide/`
- Design: `DESIGN.md`
- Rules: `RULES.md`
- A change follows RULES.md.
- Design-review paths: `DESIGN.md`, `RULES.md`, `docs/api-snapshot.txt`, `src/refdef/tables/`, `tests/corpus/`.
  A commit touching them needs a `Design-review: <ID>` trailer.
- A need the surface does not meet is a reviewed design change, never a workaround.
- Use `uv` only, with exact pins.
