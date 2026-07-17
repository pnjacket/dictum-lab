---
artifact: research-companion
role: study
anchor: LAB-STUDY-GATE-CHECKS
non_normative: true
---

# Study: deterministic tools for Dictum's gates (2026-07)

**Question.** Which of the standard's gate checks are mechanically decidable,
and can a deterministic checker reach useful precision/recall on real doc
sets without changing the standard?

**Verdict.** Five check families are decidable and a zero-dependency
single-file checker reaches full recall on pinned-state ground truth with
near-zero false positives after calibration — *and* it caught one true defect
that two independent LLM passes had missed. Deterministic checking is not
just cheaper than LLM auditing for mechanical invariants; it is more
reliable. The undecidable remainder (rung computation, semantic drift,
content quality) genuinely requires the judgment layer.

## Method

Per [`PROTOCOL.md`](../PROTOCOL.md) pinned-state ground-truthing. Subjects:
three real doc sets, described by shape —

- **S1** — a doc-first marketplace-style PoC: 13 in-scope concerns, authored
  to contract-grade, not yet built (no binding map).
- **S2** — a built front-end library carried through seven enhancement
  deltas: 13 in-scope concerns, ~190 bound contracts, populated build-status.
- **S3** — a built multi-component engine (three components, three
  languages): 14 in-scope concerns, ~129 bound contracts, ~20 verified
  slices.

Ground truth: a full LLM audit (per the standard's `doc-maturity-auditor`
procedure) of each set at a pinned pre-fix git state, every finding
evidence-grounded and subsequently fixed, producing a near-clean post-fix
state. The checker ran against both states; divergences were adjudicated
individually.

## Results

Recall against the audits' mechanical findings (pre-fix states):

| Finding class | Audit found | Checker found |
|---|---|---|
| Dangling binding-map keys (S2 + S3) | 8 | **8/8** (errors) |
| Referenced-but-unowned acceptance body (S3) | 1 | **1/1** (warning tier — correctly nuanced: inline mention only) |
| Scope-partition holes — a new published key unaccounted (S2, S3) | 2 | **2/2** |
| Publish step skipped over a built product (S2) | 13 docs | **13/13** |
| Additional true findings beyond the audit | — | **+2**: a same-class dangling key the audit list omitted (independently corroborated by the fix pass), and S3's never-published doc set — **a true defect two LLM passes missed** |

Precision (post-fix states): S2 converged to **0 errors**; S1 to 2; S3 to 4 —
every residual attributable to one named convention gap (below), none
spurious.

A methodological note: an early run validated S3 against a worktree cut one
commit too early — *before* the newer standard was re-vendored — and the
partition check correctly reported nothing, because the doc set conformed to
the old vocabulary it vendored. The checker validates against the vendored
standard by design; upgrade holes surface only after re-vendoring. This is
the standard's documented upgrade-migration issue made concrete.

## False-positive classes discovered (and mitigations)

Calibration went 239 → 0 errors on S2's post-fix state across ~6 iterations.
Every class found, named:

1. **Definition-form diversity** — paragraph registers (`**\`ID\`** — …`),
   indented list items, multi-ID rows (`` `A` / `B` — ``), unbackticked bold
   keys (`**AC-X:**`), long annotated table cells, IDs on either side of a
   heading's em-dash, bare start-of-line keys, error-code grammar
   (`SOME_CODE`), dotted keys (`Type.field`). → generalized definition
   grammar.
2. **Wildcard families** — shaped wildcard register rows (`EVT-*-X`) are real
   mints; bare family aliases in coverage tables (`A11Y-*`) are not, and
   treating them as mints silently swallowed two true dangles. → shaped
   wildcards only.
3. **Suffix-shorthand continuations** (`` `EVT-EDIT-*`/`-VALIDATION-ERROR` ``)
   and **prefix-elided shorthand** (`` `VENDOR-ORDER` `` for
   `ENTITY-VENDOR-ORDER`). → skip / resolve respectively.
4. **Sanctioned forward references** on `[FUTURE-SCOPE]` lines. → honored.
5. **Negated mentions** ("there is **no** `ENTITY-X`"), **retired mentions**
   (tombstone map + retired-context warning), **prose compounds** that match
   the ID grammar unticked (downgraded to warnings), **placeholder patterns**
   (`API-0NN`). → guarded or tiered.

## Findings about the standard (fed back)

- **Register-form minting is the convention determinism depends on.** Two
  subjects deliberately mint IDs inline mid-cell; those are exactly the
  residual errors. Options: recommend register form normatively, or an
  explicit inline-mint annotation. *(Open.)*
- **Publish-strip ambiguity:** the standard strips `<!-- BUILD: -->` on
  publish; template section annotations (`<!-- rung: … -->`) are unspecified,
  and two independent fix passes interpreted them differently. *(Open.)*
- **Plain-YAML-subset manifests** are what keep tooling zero-dependency —
  worth stating as a template constraint. *(Open.)*
- The **upgrade re-partition check** is now deterministic (vendored-standard
  caveat above); the standard's roadmap item for an install-time upgrade walk
  remains open.

## Limits

Symbol-existence checking is substring-grade (last dotted segment). The
derived-index check is a crude mention floor. Slash-shorthand *expansion*
verification and prose-count arithmetic were not attempted (the latter is
likely undecidable in general). No attempt at rung computation — Part 4's
material-satisfaction rule is judgment by construction.
