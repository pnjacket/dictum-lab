# dictum-drift-check

The **deterministic (model B) drift detector** — the mechanically-decidable
slice of the standard's drift detection (STANDARD Part 10d), whose judgment
layer is the advisory model-A agent (`agents/drift-detector.md` in the
standard repo). Zero-dependency (Python 3 stdlib only).

It is a **research instrument, not a product**: the question it answers is
*which drift finding classes can be decided with certainty, under which
preconditions* — and where certainty ends it **declines loudly** (an INFO
`not-decidable` finding) instead of guessing. Every finding carries a tier
(`certain`/`heuristic`); **only certain-tier ERRORs drive the exit code**,
and heuristic findings are capped at WARN.

```sh
python3 dictum-drift-check.py <docset-root>                 # code = the same repo
python3 dictum-drift-check.py <docset-root> --repo <path>   # code elsewhere
python3 dictum-drift-check.py <docset-root> --map map.json  # pre-built code-map inventory
python3 dictum-drift-check.py <docset-root> --json
```

Inputs: the doc-set layout gate-check consumes (`manifest.yaml`, docs with
front matter, `bindings.yaml` per `templates/binding-map.template.md`) plus a
[`dictum-code-map`](../code-map) inventory (built on the fly unless `--map`
is given). Exit code: `0` clean · `1` any ERROR finding · `2` usage/parse
error (extends gate-check's 0/1 convention with an explicit usage tier).

**Non-normative:** the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.

**Status: experimental.** Validated on the synthetic fixture corpus only
(`fixtures/drift-check/`), not yet ground-truthed against real pinned repo
states per [`PROTOCOL.md`](../../PROTOCOL.md); see
[`studies/2026-07-model-b-tooling.md`](../../studies/2026-07-model-b-tooling.md).

## Finding classes and their decidability

| Category | Finding | Tier / precondition |
|---|---|---|
| `binding-stale` | A locator `path` (or optional `line`) no longer exists — a defect in the *index*, not a code↔doc drift (Part 10d; no direction, no adjudication). | **certain** |
| `binding-stale` | A locator `symbol` not found — substring probe of the last dotted segment. | heuristic → WARN only |
| `doc-end` | Binding key resolves to no register-form definition, or to a tombstone; premature binding (sub-Contract-grade owning concern → WARN; rolled up to one INFO in reverse-authored-baseline mode, per the model-A agent). | **certain** under the register-form ID-minting convention; an inline-mint key is WARN/heuristic |
| `doc-ahead-unbuilt` | A binding records **no code evidence at all** (no `locators`, no `asserted_by`). The map's presence claims realization (bindings are populated as each slice is built), so zero evidence is decidably doc-ahead. | **certain**. Note the deliberate narrowness: "never existed vs no longer exists" is not decidable, so an all-dangling binding stays `binding-stale`; a merely *unbound* contract is the legitimate build-new state (Part 10e), reported as `coverage-gap`, never as unbuilt |
| `code-ahead` | An in-code `DICT: <ID>` annotation absent from the doc set's ID web (or naming a tombstoned contract). Deduplicated per ID across sites. | **certain** under the DICT-annotation + register-form conventions; unparsed annotations surface as one heuristic WARN |
| `route-diff` | OpenAPI artifact endpoints vs owned `API`/`ROUTE` contracts, both directions. Doc-side route = the `METHOD /path` stated on the contract's register line; path params normalized (`{id}`, `:id` → `{}`). Doc-ahead fires **only for bound contracts** (unbound = build-new, not drift). | **certain**, only where a machine-readable artifact exists — the roadmap's model-B path. No artifact → loud decline. A register line stating no route → loud decline for that contract |
| `schema-diff` | ENTITY vs artifact schemas. Doc-ahead is claimed only where the binding itself declares `compare_via: openapi` (the binding-map template's model-B hook) and no schema matches; an artifact schema matching no ENTITY is a heuristic WARN (name-normalization join). Field-level comparison is **declined**: doc-side field lists are prose. | **certain** only under `compare_via`; presence-level only |
| `coverage-gap` | An in-scope, Contract-grade, code-realizable contract with no binding — drift undetectable there; the forward flow's build-new signal. Honors the map's `coverage:` block (`fully_bound` vs `curated`). | **certain** arithmetic → WARN (it is a flag, not a detection — model A vocabulary) |
| `suppressed` | A finding on a contract with an open manifest `staleness` cause — reported once as INFO, never re-raised (Part 10d suppression). | **certain** |
| `not-decidable` | The loud declines: no interface artifact; register line without a route; prose field lists; INV `run:` selectors (deliberately not executed — executable evidence is CI's/model A's, not this checker's). | the boundary itself |

`--json` emits the findings plus **candidate change events** in the Part 10d
shape (`{id, source: drift, classification: proposed, ref: WORKING-TREE,
direction, by, evidence, adjudication: pending}`) for ERROR-tier directional
findings — same vocabulary as the model-A agent where the categories map
(`binding-stale`, coverage gap, code-ahead/doc-ahead directions,
`WORKING-TREE` ref). Like model A it **detects only**: it never adjudicates,
never edits, and a `binding-stale` is never given a direction.

## Left to the judgment layer (model A / the operator)

Semantic drift without an executable check, classification beyond `proposed`,
adjudication (doc-stale vs code-defect vs divergent), "under-specification is
not drift" calls, one-root-cause deduplication across contracts, and anything
requiring per-stack AST extraction (an "undecided-yet" class — see the study).
