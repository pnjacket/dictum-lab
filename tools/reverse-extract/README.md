# dictum-reverse-extract

The **deterministic reverse-extraction backend** for the standard's
brownfield code→doc bootstrap (STANDARD Part 10f), whose judgment layer is
the advisory model-A agent (`agents/code-cartographer.md` in the standard
repo). Zero-dependency (Python 3 stdlib only); built on the
[`code-map`](../code-map) backend.

```sh
python3 dictum-reverse-extract.py <repo-root>              # bundle to stdout
python3 dictum-reverse-extract.py <repo-root> --out DIR    # three files to DIR
```

Exit code `0` on success, `2` on usage error. It **never writes into the
scanned repo** (the flow reads code, writes drafts elsewhere — `--out` into
the repo root is refused).

**Non-normative:** the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.

**Status: experimental.** Validated on the synthetic fixture corpus only,
not yet ground-truthed against real pinned repo states per
[`PROTOCOL.md`](../../PROTOCOL.md).

## What it emits (all three artifacts are DRAFT, per Part 10f semantics)

| Artifact | Content |
|---|---|
| `candidate-inventory.json` | Candidate contracts, split by identity provenance: **recovered** — IDs read verbatim from in-code `DICT:` annotations (identity certain *under the convention*; meaning unconfirmed) with heuristic-tier symbol sniffs; **coined** — candidates minted deterministically from interface artifacts (`API-GET-NOTES` from `GET /notes`, `ENTITY-NOTE` from schema `Note`): structure certain over the artifact, identity coined. A coined ID that exactly equals a recovered one merges (`recovered+artifact`); any other correspondence is *declined* (route→handler resolution needs AST work). Every entry carries `assumption: true`. Config keys appear as a heuristic-tier prose surface only — never as contracts. |
| `bindings.draft.yaml` | A DRAFT binding map in the standard's template shape (`templates/binding-map.template.md`), from recovered annotations only; coined artifact candidates appear as commented stubs (no code locator is recoverable without AST). Not a validated map — nothing is Contract-grade yet. |
| `recoverability-report.md` | The loud declines, mirroring Part 10f's recoverability partition: intent, personas/success, threat model/policy, UX intent, perf targets, governance, business/legal, and — categorically — Non-goals & scope-out kinds. Also declined (unlike model A, which drafts them at low confidence): `CAP-###` groupings and delivered-vs-aspirational adjudication. |

## The determinism boundary this tool demonstrates

Model B recovers **identity** (annotations) and **artifact structure**
(OpenAPI/JSON Schema) with certainty, and *nothing else*: everything model A
extracts by judgment (capability groupings, the reference web from call
graphs, smells, reachability/aspirational classification, trait derivation)
is either declined outright or "undecided-yet" pending per-stack AST
extractors. The output is raw material for `doc-excavate`'s confirm-and-fill
interview — a baseline, never build-ready, no rung or Verified claim
(Part 10f "honest rung outcome").
