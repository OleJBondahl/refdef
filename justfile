# refdef task runner
# Usage: just <target>

default:
    @just --list

# lint, format check and types
check:
    uv run ruff check src tests scripts
    uv run ruff format --check src tests scripts
    uv run ty check src tests scripts

# dead code sweep (confidence 60)
dead-code:
    uv run vulture src --min-confidence 60

# pytest with coverage; the 95 percent floor is baked into [tool.pytest.ini_options] addopts
cov:
    uv run pytest --cov-report=term-missing

# the tests on Python 3.14, the oldest supported version (requires-python), in a throwaway env
test314:
    uv run --python 3.14 --isolated pytest --no-cov -q -p no:cacheprovider

# the release and design-review guards
guards:
    uv run python scripts/release_guard.py
    uv run python scripts/design_guard.py

ci: check dead-code cov test314 guards site

# build the docs site into .site/ (Zensical, strict: a broken link fails)
site:
    uv run python scripts/build_site.py

fmt:
    uv run ruff format src tests scripts
    uv run ruff check --fix src tests scripts

# print the public surface
api:
    uv run python -m refdef api

# regenerate the surface snapshot
api-write:
    uv run python -m refdef api > docs/api-snapshot.txt

# bump the version, open a new Unreleased above the version section, run the gate, commit and tag (no push): just release 0.2.0
release V:
    #!/usr/bin/env bash
    set -euo pipefail
    sed -i 's/^version = ".*"/version = "{{V}}"/' pyproject.toml
    sed -i 's/^## Unreleased$/## Unreleased\n\n## {{V}} ('"$(date +%F)"')/' docs/CHANGELOG.md
    just ci
    git add pyproject.toml docs/CHANGELOG.md uv.lock
    git commit -m "Release {{V}}"
    git tag "v{{V}}"

# a coverage-free run
test:
    uv run pytest --no-cov
