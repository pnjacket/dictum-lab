# dictum-gate-check

A **deterministic, zero-dependency** checker for the mechanically-decidable
slice of Dictum's gates. Single file, Python 3 standard library only. Run it
against a product repo that follows the standard (vendored standard expected
at `<repo>/dictum/`):

```sh
python3 dictum-gate-check.py <product-repo-root>
```

Exit code `1` if any ERROR finding, else `0` — suitable for CI:

```yaml
# .github/workflows/docs.yml (example job)
docs-gate:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: python3 path/to/dictum-gate-check.py .
```

Like all Dictum tooling it is **advisory in posture**: the standard never
requires it, and a product team choosing to make it a hard CI gate is that
team's decision. It is the *model-B complement* to the standard's LLM
tooling — it cannot judge content, but it never tires, never glosses, and
gives the same answer every run. **Non-normative:** where this tool and the
standard's text disagree, the text wins and this tool has a bug.

**Status: experimental.** Calibrated against three real doc sets (a doc-first
PoC, a built library through seven enhancement deltas, and a built
multi-component engine) using pinned-state ground truth — see
[`studies/2026-07-deterministic-gate-checks.md`](../../studies/2026-07-deterministic-gate-checks.md)
and the fixture corpus under [`fixtures/`](../../fixtures).

## What it checks (and what it can't)

| Check | What it validates | Decidable? |
|---|---|---|
| `partition` | Each in-scope concern's `in-scope-subaspects` ∪ manifest `out_of_scope_subaspects` equals the concern spec's published key vocabulary, disjoint (Std Parts 7/9). Vocabulary parsed from the vendored spec's *Sub-aspects* `key` column — so upgrade holes surface once the new standard is re-vendored. | fully |
| `publish` | Part 6 gate binding: build-readiness claimed (all in-scope concerns at target rung) or a build demonstrably done (populated binding map) ⇒ every concern doc `status: published` with no `<!-- BUILD: -->` markers. Evidence-based detection, not a status/implementation coupling. | fully |
| `idweb` | Every referenced contract ID whose prefix is owned resolves to a definition (register row, heading, bold register key, or the manifest tombstone map). Honors `[FUTURE-SCOPE]` forward references, suffix-shorthand continuations, shaped wildcard rows (`EVT-*-X`), arm tokens (warns on parent-only resolution), retired mentions (warns), negated mentions, prefix-elided shorthand. | heuristic, high precision |
| `bindings` | Binding-map keys resolve doc-end (error if defined nowhere, warning if only an inline mention); locator `path`s exist; locator `symbol`s appear in the file (last dotted segment, warning). | fully (doc-end) / heuristic (symbol) |
| `markers` | Subject-marker vocabulary — tokens outside `[GAP] [ASSUMPTION] [REVISIT] [FUTURE-SCOPE]` are warnings. | fully |
| `index` | Derived README mentions every in-scope concern (crude consistency floor). | crude |

**Not decidable — stays with the standard's LLM auditor:** actual-rung
computation (Part 4 *material* section satisfaction), prose-count arithmetic,
cross-doc semantic contradictions, scope-sanity judgment, and whether a
contract's content is any good. This tool is the floor; the auditor is the
judgment layer; run both.

## Conventions it assumes

IDs minted in **register form**: a heading, the first cell of a table row, a
bold list/paragraph key (`- **\`ID\`** — …`, `**ID:**`), or a bare
start-of-line backticked key. An ID minted *inline* mid-cell or mid-sentence
is invisible to it and surfaces as a warning or error — deliberately: inline
mints are also where human readers and future re-adoption lose the register.
Manifests, front-matter, and binding maps must stay in the plain YAML subset
the standard's templates use — that is what keeps this tool dependency-free.
