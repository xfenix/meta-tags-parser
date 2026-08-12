# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository.

## Project

`meta-tags-parser` is a small, dependency-light Python library that parses meta tags (OG, Twitter,
basic, other) and the page title out of HTML, and builds social-media snippet previews. It ships
`py.typed` and is fully typed (`mypy --strict`). Runtime dependencies are only `httpx` and `selectolax`.

- `meta_tags_parser/structs.py` — the public data model (frozen, slotted dataclasses) and settings.
- `meta_tags_parser/parse.py` — the core HTML-scanning/extraction logic.
- `meta_tags_parser/snippets.py` — builds `SnippetGroup`/`SocialMediaSnippet` from parsed tags.
- `meta_tags_parser/download.py` — thin sync/async HTTP fetch helpers (httpx).
- `meta_tags_parser/public.py` — convenience `*_from_url` wrappers combining download + parse.
- `meta_tags_parser/__init__.py` — the public export surface.
- `benchmark/` — standalone speed benchmark, excluded from linting (large embedded payload).
- `scripts/generate_coverage_badge.py` — CI helper, generates the coverage badge JSON.

## Supported Python versions

This package supports **Python 3.10 through 3.14** (see `requires-python` in `pyproject.toml` and the
CI matrix in `.github/workflows/main.yml`). Do not use syntax/stdlib features newer than 3.10 unless
you also verify (and ideally test) 3.10 still works — `uv run --python 3.10 pytest .` is the fastest
way to check. `.python-version` pins the local dev interpreter to the newest supported version (3.14)
but must never be tighter than `requires-python`.

## Environment & commands

Package manager is **uv**. Do not use bare `pip`/`venv`.

```bash
uv sync --dev                                    # install deps (dev group included)
uv run pytest -n2 .                              # run tests (parallel, with coverage)
uv run ruff format .                             # format
uv run ruff check --no-fix .                     # lint (ruff, select = ALL)
uv run flake8 meta_tags_parser scripts tests     # lint (community-of-python plugin, COP rules)
uv run mypy --strict meta_tags_parser scripts    # type-check
uv run auto-typing-final --check meta_tags_parser scripts tests   # verify Final/@typing.final coverage
```

Run all five (format, ruff, flake8, mypy, pytest) before considering a change done — this mirrors
what CI (`.github/workflows/main.yml`) enforces. Cross-check anything touching parsing logic against
at least the oldest supported interpreter (`uv run --python 3.10 pytest .`) since this repo's CI runs
the full matrix (3.10–3.14) on every push.

## Code style — follow community-of-python/pylines guidelines

This repo follows the [pylines](https://github.com/community-of-python/pylines) conventions. Key rules
enforced by tooling (not just style preference):

- **100% type annotations.** `mypy --strict` must pass. Don't annotate inferrable scalars
  (`x = "value"`, not `x: str = "value"`) — but do wrap variables in bare `typing.Final` (no inner
  type) where possible. Note: `typing.Final` cannot be used on a variable that is (re)bound inside a
  loop body — mypy rejects it; leave those unannotated instead of removing the loop.
- **Every class gets `@typing.final`** unless it's meant to be subclassed.
- **Dataclasses**: `@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)` by default.
- **Composition over inheritance.**
- **Naming**: functions are verbs (`fetch_`, `build_`, `extract_`, `parse_`, not `get_` unless reading
  from memory); identifiers are generally ≥8 characters, for-loop variables are prefixed `one_`
  (`for one_attr_group in ...`). The `community-of-python-flake8-plugin` (flake8 code prefix `COP`)
  enforces most of this automatically — run it, don't guess.
- **No unnecessary reassignment.** Prefer building the result once (comprehension, small helper
  function with early `return`s, `min()`/`any()`) over declaring a variable and mutating it across
  branches or loop iterations. If you see `COP017` from flake8, restructure rather than suppress it.
- **Immutability**: `typing.Final`, `types.MappingProxyType` for module-level dict constants, frozen
  dataclasses.
- **Imports**: stdlib modules imported whole (`import typing`, not `from typing import Final`) except
  `collections.abc`. Import a module directly (not `from x import a, b, c`) when pulling in more than
  two names from it.
- Full config lives in `pyproject.toml` under `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.mypy]`, and
  `[tool.flake8]`.

### Intentional linter exceptions (do not "fix" these)

`[tool.flake8].per-file-ignores` in `pyproject.toml` suppresses `COP006`/`COP004` (min identifier
length) on:

- `meta_tags_parser/public.py`, `parse.py`, `snippets.py` — the `web_url`/`options` keyword
  arguments on the public `parse_*`/`*_from_url` functions.
- `meta_tags_parser/structs.py` — public dataclass fields (`name`, `value`, `title`, `basic`,
  `twitter`, `other`, `image`, `url`, ...).

These are the stable public API/return-value contract of a published PyPI package. Renaming them is a
breaking change for every downstream consumer and must not be done as a drive-by lint fix — if it's
ever warranted, it needs an explicit major-version bump and a CHANGELOG/README callout, decided with
the maintainer, not silently by an agent.

## Tests

- `pytest` + `pytest-xdist` (parallel) + `hypothesis` (property-based) + `faker` (fixture data).
- Arrange/Act/Assert; prefer parametrized tests over copy-pasted near-duplicates.
- `tests/*.py` gets `S101`/`S311` ruff exemptions (asserts and non-crypto random are fine in tests).
- Keep coverage at 100% for anything reachable without network access; `parse.py`'s `hard_limit_chars`
  branch is a known, pre-existing minor gap (not something to chase in unrelated changes).

## Git / PR hygiene

- Don't bump `[project].version` or touch the coverage badge/CHANGELOG-adjacent generated files by
  hand — those are CI-managed (`scripts/generate_coverage_badge.py`, `git-auto-commit-action`).
- `benchmark/` is intentionally excluded from `ruff`/`flake8` (large embedded fixture payload); don't
  add strict-lint requirements there.
