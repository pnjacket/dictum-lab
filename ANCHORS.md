# Lab anchors — the citeable surface

Stable identifiers for lab content that the Dictum standard (or anything else)
may cite for deeper insight. An anchor is **stable across reorganization** — a
file may move or be renamed, but its `anchor:` (in front-matter) does not
change — so a citation survives where a path would rot.

**How the standard cites these:** non-normatively, and **pinned by lab commit
SHA per standard release** (the pin table in the standard's `RELEASES.md`). The
lab keeps its own cadence — an anchor names *what*, the release pin names *which
commit* it resolves against. Nothing here defines conformance; the standard's
text stands alone (its `EDITORIAL.md` Part 2).

**Retirement:** an anchor is never reused or repointed at different content. If
content is removed, its anchor is tombstoned here (struck through, with a note),
mirroring the standard's owned-once discipline.

## Studies

| Anchor | Path | What |
|---|---|---|
| `LAB-STUDY-VALIDATION-BUILDS` | `studies/2026-07-method-validation-builds.md` | The four validation builds, the regeneration-fidelity control, and the blind-rebuild trial — the evidence behind the failure-mode catalog. |
| `LAB-STUDY-MODEL-B` | `studies/2026-07-model-b-tooling.md` | The deterministic (model-B) determinism-boundary study: what a deterministic tool can decide with certainty, and where certainty ends. |
| `LAB-STUDY-GATE-CHECKS` | `studies/2026-07-deterministic-gate-checks.md` | The deterministic gate-check study (decidable gate checks over the standard's extension points). |
| `LAB-STUDY-SOURCE-PROVENANCE` | `studies/2026-07-source-provenance.md` | The source-provenance determinism boundary: a declared `SOURCE:` marker's license vs the outbound is decidable and exact; undeclared copying is undecidable and recorded as residual, never cleared. |
| `LAB-STUDY-ASSUMPTION-ACCOUNTING` | `studies/2026-07-assumption-accounting.md` | Whether an assumption behaves like a **node**: promoting a depended-on `[ASSUMPTION]` to an owned `ASSUMPTION-###` kind so falsification propagates through the existing ID web — with the falsifiers that would kill it. |
| `LAB-STUDY-AUDIT-FIX-LOOP` | `studies/2026-08-audit-fix-loop.md` | Whether an audit/fix loop converges: a fifteen-class defect taxonomy and the ten intake schemas derived from it, the fifteen mechanisms built against the taxonomy, the rate at which mechanisms themselves ship broken, and the finding that the loop's length is set by the size of the taxonomy rather than the fix rate — most cycles being unmade product decisions rather than documentation defects. |
| `LAB-STUDY-ANNOTATION-RECALL` | `studies/2026-09-annotation-recall.md` | What in-code ID annotation buys: measured exact-ID recall with and without markers across two products, the finding that recall is set by marker coverage rather than quality, that a partial marker set suppresses discovery of everything it does not name, and that recovery is the weakest of the benefits worth citing. |
| `LAB-STUDY-OKF-FORMAT-REVIEW` | `studies/2026-09-okf-format-review.md` | Whether an external container format (Google's Open Knowledge Format v0.2) can become the standard's base document format: the container-versus-method framing, a ten-row full-adoption conflict ledger, the gains-and-losses ledger, the netted fixed context cost per editorial session, and the finding that a one-way export plus three native lines beats adoption. |

## Practices

| Anchor | Path | What |
|---|---|---|
| `LAB-PRACTICE-ANNOTATE-BROWNFIELD` | `practices/annotate-after-brownfield.md` | Annotating code with contract IDs as a separate, consent-gated step after a brownfield adoption — why doc-led builds get it free, what it buys in the recurring lifecycle rather than in recovery, what it costs, and why the unit of the decision is the contract kind. |

## Method

Prescriptive companions to the studies. `PROTOCOL.md` is unanchored by design —
it governs how the lab itself runs trials, and nothing outside cites it.

| Anchor | Path | What |
|---|---|---|
| `LAB-METHOD-EDIT-LOOP` | `METHOD-EDIT-LOOP.md` | The operational companion to `LAB-STUDY-AUDIT-FIX-LOOP`: the loop protocol, the editing rules, the mechanism-design rules, and the ten intake-saturation schemas. Written to be applied, not cited. |

## Concern notes (worked examples & design rationale)

Migrated out of the standard's concern specs in the 2026-07 compaction audit.
One per concern; anchor `LAB-NOTE-11.x` ↔ `concern-notes/11.x-<slug>.md`.

| Anchor | Concern |
|---|---|
| `LAB-NOTE-11.1` | Product & Requirements |
| `LAB-NOTE-11.2` | Domain & Data |
| `LAB-NOTE-11.3` | Architecture |
| `LAB-NOTE-11.4` | Interfaces & Contracts |
| `LAB-NOTE-11.5` | Quality & Testing |
| `LAB-NOTE-11.6` | Delivery Process |
| `LAB-NOTE-11.7` | Security & Privacy |
| `LAB-NOTE-11.8` | Governance & Compliance |
| `LAB-NOTE-11.9` | User Experience |
| `LAB-NOTE-11.10` | Operations & Infrastructure |
| `LAB-NOTE-11.11` | Observability & Monitoring |
| `LAB-NOTE-11.12` | Integrations & External Dependencies |
| `LAB-NOTE-11.13` | Performance & Scalability |
| `LAB-NOTE-11.14` | Accessibility & Internationalization |
| `LAB-NOTE-11.15` | Business & Legal |
