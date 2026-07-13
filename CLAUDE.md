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

- **All tools are zero-dependency by design** (Python 3 stdlib only) — do not
  add imports outside the standard library. Manifests/front-matter are
  constrained to the plain YAML subset the standard's templates use.
- **Shared parsing lives in `tools/common/dictumlib.py`** (YAML subset, front
  matter, doc-set discovery, ID grammar/registry, the register-form owned-ID
  web); the newer tools import it relative to their own path and stay
  runnable as standalone scripts. **`gate-check` keeps its own inline copy on
  purpose** (single-file distribution) — a change to the subset or the
  grammar must land in **both**, verified by `tests/run.sh`.
- **Tools are research instruments, not products.** The question each answers
  is what model B can decide **with certainty** and where certainty ends:
  prefer a small provably-sound check surface over broad heuristics; anything
  heuristic is tiered explicitly (never exit-code-driving, WARN at most); and
  where a tool cannot decide it **declines loudly** (`not-decidable` /
  `unparsed_*` outputs) — declining is a success result, encoded in tests.
  The determinism-boundary map lives in the studies; keep it current when a
  class moves between decidable / undecided-yet / undecidable.
- Every fixture under `fixtures/` is self-contained and pins the standard
  version it targets in its `FIXTURE.md` line. Doc-set fixtures vendor a
  **mini** standard (just the concern-spec tables the checks need); pure-code
  fixtures (e.g. `fixtures/code-map/`) need none. Broken fixtures encode
  exactly one defect each, named by the directory; **boundary probes**
  (asserting a loud decline, not a detection) are first-class fixtures too.
  Gate-check's corpus sits at `fixtures/` top level (historical); newer tools
  use `fixtures/<tool>/`.
- Fixture products are **invented shapes** ("a note-taking service") — the
  describe-by-shape rule applies to fixtures as much as to studies.
- `tests/run.sh` must pass before any commit that touches a tool or the
  fixtures; it also asserts byte-identical re-runs (determinism is testable).
- Studies go under `studies/` as `YYYY-MM-<slug>.md`, method before results,
  ground truth stated explicitly.
- Tool READMEs state the non-normative rule explicitly: the standard's text
  is the only definition of conformance; a disagreement is a bug **here**.
- The `tracker-sync` github adapter shells out to `gh` and is **never invoked
  in tests** — no network anywhere in tests.
- Commit, don't push, until the operator says otherwise.
