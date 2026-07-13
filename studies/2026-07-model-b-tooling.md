# Study: the model-B determinism boundary (2026-07) — METHOD STUB

**Question.** The standard's three deferred "future tooling" items (dictum
ROADMAP) — a model-B drift detector (Part 10d), deterministic
reverse-extraction (Part 10f), and doc↔tracker sync (Part 10c) — all turn on
one research question: **what can the best deterministic (model B) tool
decide with certainty, under which stated preconditions — and where exactly
does certainty end?** The tools built here are the executable evidence; the
boundary map below is the finding.

**Status: first cut, fixture-validated only.** Ground truth is the
**synthetic fixture corpus** (`fixtures/code-map/`, `fixtures/drift-check/`,
`fixtures/tracker-sync/` — invented product shapes, one defect per broken
fixture, boundary probes for the declines). This has **not** yet been
ground-truthed against real pinned repo states per
[`PROTOCOL.md`](../PROTOCOL.md); recall/precision numbers would be
meaningless at this stage and none are claimed. The design posture
throughout: **a smaller check surface that is provably sound over broad
heuristic coverage; where a tool cannot decide, declining loudly is a
success result** (encoded in output shapes and asserted by tests).

## Method

1. Read the normative definitions (STANDARD Parts 10c/10d/10e/10f, Delivery
   11.6, the binding-map and build-status templates, GLOSSARY) and the two
   model-A agents being mechanized (`drift-detector`, `code-cartographer`).
2. For each model-A behavior, classify it: **decidable** (and under what
   precondition), **undecidable-in-principle** for model B, or
   **undecided-yet** (would become decidable with per-stack AST work).
3. Implement only the decidable classes, zero-dependency, on one shared
   code-mapping backend (`tools/code-map`); expose every precondition in the
   output (tier tags, `not-decidable` findings); cap heuristic signals at
   WARN so they can never drive a CI exit code.
4. Build the fixture corpus to probe **both sides of the boundary**: cases
   just inside (must be detected, exactly once) and just outside (the tool
   must decline explicitly rather than guess). `tests/run.sh` asserts both,
   plus byte-identical re-runs (determinism as a testable property).

## The boundary map

### Backend: `code-map`

| Surface | Verdict | Precondition / note |
|---|---|---|
| In-code contract-ID annotations (the `DICT: <ID>` marker token in a host-language comment) | **decidable** | the annotation convention (Part 10f) — the standard fixes the token grammar only, not the comment leader. A token this scanner cannot parse (a leader outside its list, a non-grammar ID) surfaces in `unparsed_annotations`, never guessed; an uncovered leader is a *scanner* limitation, not non-conformance |
| Endpoint/schema inventory | **decidable** | only where a committed/build-emitted machine-readable artifact exists (OpenAPI JSON / plain-YAML-subset, JSON Schema) — the roadmap's named model-B path |
| Routes/entities out of bare source (no artifact) | **undecided-yet** | per-stack AST/route extractors; the output schema reserves `interfaces` families for them |
| Env-key surface | **heuristic, permanently** | regex over source can't see indirection/computed keys; emitted as inventory under an explicit heuristic tier, never a finding |

### `drift-check` (vs the model-A `drift-detector` agent)

Decidable, with preconditions (these drive the exit code):

- **`binding-stale`** — locator `path`/`line` resolution. Unconditional.
  (Symbol resolution is only substring-decidable → heuristic WARN.)
- **doc-end key resolution, tombstones, premature bindings, staleness
  suppression, baseline-mode rollup** — decidable **under the register-form
  ID-minting convention**; an inline-minted ID degrades to a heuristic WARN.
  (Same convention dependence the gate-check study found — it is the single
  convention most of model B stands on.)
- **`doc-ahead-unbuilt`** — narrowed to the provably sound case: a binding
  with **zero recorded code evidence**, because the map's presence claims
  realization (Part 10d). "Never existed vs no longer exists" is not
  decidable, so an all-dangling binding stays `binding-stale`; an *unbound*
  contract stays the legitimate build-new `coverage-gap` WARN (Part 10e).
- **`code-ahead`** — an annotated ID absent from the ID web; under both
  conventions above.
- **`route-diff`** — both directions, only where an artifact exists AND the
  doc states `METHOD /path` on the contract's register line (a convention
  this tool adds; absent it, per-contract loud decline). Doc-ahead only for
  bound contracts.
- **`schema-diff` doc-ahead** — only where the binding itself declares
  `compare_via: openapi` (the template's model-B hook). The name join for
  code-ahead schemas is heuristic (WARN).
- **coverage arithmetic** — honoring the map's `fully_bound`/`curated`
  declaration.

Undecidable-in-principle for model B (stays with model A / the operator):
semantic drift without an executable check; classification beyond
`proposed`; adjudication (doc-stale/code-defect/divergent); the
"under-specification is not drift" call; one-root-cause deduplication across
contracts; direction preference judgment. Deliberately not exercised even
though executable: **INV `run:` selectors** (arbitrary code execution — CI's
gate, model A's evidence; declined with a named INFO). Undecided-yet:
everything requiring AST extraction; doc-side field lists (prose today — a
doc-side machine-readable convention would make field-level ENTITY
comparison decidable).

### `reverse-extract` (vs the model-A `code-cartographer` agent)

Decidable: **identity recovery** (annotation IDs verbatim — the regeneration
-fidelity result that motivated the annotation convention, now mechanized);
**artifact structure** (endpoints/schemas); deterministic **coining**
(`API-GET-NOTES` from `GET /notes`) with exact-ID merge into recovered IDs.
Everything is emitted as DRAFT + `[ASSUMPTION]`, per Part 10f.

Undecidable-in-principle: intent, personas/success, threat model/policy, UX
intent, perf targets, governance, business/legal, and — categorically —
**Non-goals & scope-out kinds** (Part 9). Also declined although model A
*drafts* them at low confidence: `CAP-###` groupings (an intent judgment),
trait derivation, smells. Undecided-yet: the reference web from call
graphs, reachability (hence **delivered-vs-aspirational** classification —
the dominant brownfield signal stays model A's), route→handler correlation
of a coined candidate with a recovered ID.

### `tracker-sync` (Part 10c)

The most decidable of the three: given the **machine-readable declaration**
(a tool convention — the standard pins semantics, not a file format) and the
build-status `## Slices` table, projection, diffing, and repo-wins
reconciliation are pure derived computation, and the boundary invariants
(never write repo files; never touch demand/triage; no stored tracker
back-reference; build gate) are enforceable by construction. Missing
declaration or build-status record → loud decline (exit 2). Undecidable:
whether a tracker-side edit *should* win (the standard already answers it:
never — repo-wins is a rule, not a judgment); triage adjudication
(reproduction is Part 10d's, human).

## Findings about the standard (candidates to fold back)

- **The in-code annotation convention embedded a language assumption —
  folded back.** The standard's earlier wording pinned the annotation as
  `// DICT: <ID>`, but `//` is not a comment leader in every language, and
  the standard does not control language choice — the
  `annotation-syntax-unsupported` fixture (a `;;`-led token) is exactly the
  case a leader-pinned convention silently excludes. *Realized:* the
  standard now fixes **only the token grammar** (`DICT: <ID>` in any
  host-language comment) as the machine-extraction extension point; leader
  coverage is a property of a given scanner, not of conformance.
- **The register-form minting convention is now load-bearing for three
  tools** (gate-check, drift-check, tracker-sync's build gate) — reinforces
  the open gate-check-study item to state it normatively.
- **A doc-side machine-readable route/field convention would move
  `route-diff`/field-diff from convention-dependent to plainly decidable** —
  today the `METHOD /path`-on-register-line pattern is idiomatic but
  unstated; the binding map's `compare_via` is the only normative model-B
  hook.
- **The tracker-binding declaration has no pinned machine-readable form**;
  this tool had to invent one. If sync tooling is ever blessed, 11.6 may
  want to pin (or bless a shape for) the declaration file.

## Open questions

1. Do the certain-tier classes hold precision on real repos? (Needs the
   PROTOCOL.md pinned-state trial — the next step; special attention to
   `route-diff` path normalization and annotation false positives in string
   literals.)
2. Is executing INV `run:` selectors worth re-admitting behind an opt-in
   flag, or is that properly CI's job forever?
3. Should `doc-ahead-unbuilt` also read the build-status record (a slice
   claiming Built over an evidence-free binding) — more recall, one more
   convention dependence?
4. Per-stack AST extractors: which single stack family would move the most
   "undecided-yet" surface for the least code?
5. The tracker-sync build gate is implemented but has no violating fixture
   yet; add one before any real-tracker trial.
