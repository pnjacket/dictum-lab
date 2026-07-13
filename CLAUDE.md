# CLAUDE.md

Guidance for Claude Code working in the **dictum-lab** repo.

## What this repo is

The **research companion** to the Dictum documentation standard (sibling
checkout: `../dictum`). It hosts everything *empirical and executable*:
deterministic reference tooling, trial protocols, studies, and a synthetic
fixture corpus. It is **non-normative** — the standard's text is the only
definition of conformance; a disagreement between a tool here and the text
there is a bug *here*.

## The boundary rule (load-bearing)

- The **standard repo** holds normative text + the Claude Code authoring
  skills/agents (its Part 10b operationalization). It must **never depend on
  this repo** — no link from a gate, bar, or procedure to a tool here.
- **This repo** holds checkers, extractors, corpora, protocols, and studies.
  Findings flow back to the standard only as distilled rules (failure-mode
  entries, bar changes) via its normal versioned releases.
- Tools iterate fast here; the standard releases slowly and signed there.
  Never couple the two cadences.

## Hard constraint: describe by shape, never by name

No committed file may name a real product, repository, or company that trials
ran against — describe products **by shape** ("a built library through seven
enhancement deltas", "a multi-component engine on local Kubernetes"). Raw
trial artifacts that do name repos stay outside git (scratch only). This is
the same discipline the standard's ROADMAP uses, and it is a legal constraint,
not a style preference.

## Conventions

- `tools/gate-check/dictum-gate-check.py` is **zero-dependency by design**
  (Python 3 stdlib only) — do not add imports outside the standard library.
  Manifests/front-matter it reads are constrained to the plain YAML subset the
  standard's templates use; keep the built-in parser in sync with that subset.
- Every fixture under `fixtures/` is self-contained: it vendors a **mini**
  standard (just the concern-spec tables the checks need) and pins the
  standard version it targets in its README line. Broken fixtures encode
  exactly one defect each, named by the directory.
- `tests/run.sh` must pass before any commit that touches the checker or the
  fixtures.
- Studies go under `studies/` as `YYYY-MM-<slug>.md`, method before results,
  ground truth stated explicitly.
- Commit, don't push, until the operator says otherwise.
