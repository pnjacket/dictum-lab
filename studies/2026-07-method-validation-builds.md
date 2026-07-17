---
artifact: research-companion
role: study
anchor: LAB-STUDY-VALIDATION-BUILDS
non_normative: true
---

# Method validation — four builds and a regeneration-fidelity control

**Status:** write-up of completed trials, relocated here from the standard
repository (2026-07 boundary audit: empirical narrative belongs in the lab;
the standard keeps only the distilled claims and rules). Describe-by-shape
throughout, per this repo's charter. Raw trial artifacts (which name real
repositories) stay outside git; this document records the shapes, methods,
and outcomes.

## Method

The standard was distilled from a real AI-driven build study, then
stress-tested by **authoring doc sets and building four deliberately
different products** — chosen to pull the method in different directions
(interface style, deployment surface, tenancy, real-time behavior, UI
weight). Each build ran hermetically against its own doc set; every friction
observed was adjudicated and, where it exposed a method weakness, folded back
into the standard as a failure-mode entry or bar change. Separately, one
**regeneration-fidelity control** tested the reverse-authoring flow's
identity-recovery claim.

Ground truth: the built products themselves (their test suites and deployed
behavior) and the pinned doc-set states at each adjudication.

## The four validation builds

1. **A CLI** — a tiny single-user task-list CLI persisting to a local JSON
   file. The doc set was looped to zero definition-friction: the build
   completed with no question an implementer had to guess at. Exercised the
   single-file doc-set form and the method's floor (a ~200-line product must
   not owe platform-scale ceremony).
2. **A multi-user record-management web app** with role-based access —
   authored as a doc set, then built and deployed on local Kubernetes.
   Exercised roles/permissions vocabulary and the merge-vs-release fidelity
   split.
3. **A real-time, multi-tenant messaging SaaS** exercising **all 15
   concerns** — authored doc-first to Contract-grade, then built and
   **Verified** by real-flow E2E on local Kubernetes: real OIDC login with
   no test bypass, cross-replica WebSocket fan-out, and tenant isolation
   enforced on both the REST surface and the live event surface. The
   heaviest single trial; most of the security/observability/delivery bars
   trace here.
4. **A client-only browser voxel game** (pure JS/HTML, zero runtime
   dependencies) — built doc-first through every slice and **Verified at
   merge fidelity** by 67 real-flow Playwright E2E, with the hardware
   release gate honestly waived as blocked-by-environment. Source of the
   blocked-by-environment/evidence-run machinery and the
   generalize-by-behavior umbrella.

Every bar change from these trials is recorded in the standard's
`failure-mode-catalog.md` — that catalog is the distilled interface between
these trials and the normative text.

## The regeneration-fidelity control (annotations buy identity)

**Design:** reverse-author the same existing codebase twice — once with its
in-code contract-ID annotations present, once with them stripped — and
compare the recovered doc sets against the incumbent authored set.

**Result:** structural recovery was roughly equal either way (~90% of
contracts recovered by structure), but **exact-ID recall fell from ~47% to
~8%** without annotations, invariant/decision identity was lost, and
re-adoption onto the incumbent web went from mechanizable to manual.

**Fold-back (distilled into the standard):** structure is
annotation-independent, identity is not — hence the recommended in-code
`DICT: <ID>` marker convention and the mandatory ID-reconciliation step
before re-adopting a regenerated set (failure-mode #28, STANDARD Part 10f).

## The blind-rebuild trial (upgrade-safety under a full re-implementation)

A fifth trial, run differently from the four above: instead of authoring a
new doc set and building it, an **existing, fully-documented product** (a
client-side interactive-UI library with a substantial in-process compute
engine and per-framework adapters) was **rebuilt from its doc set alone** —
the doc set copied into a fresh repository as the *only* input, no code, no
binding map — under a **standard-version upgrade** (the set authored against
the prior MINOR, the vendored standard one MINOR newer). Authoring and
implementation were done by fresh-context agents blind to the original code;
the frozen build was then compared, post-hoc, against the original's own
independently-authored tests. The goal was to exercise the whole pipeline
end to end (audit → author-to-Contract-grade → gate-bound publish → plan →
build → verify → one doc-led enhancement delta) and, specifically, whether
the *upgrade*-facing machinery fires.

**Headline outcomes (describe-by-shape).** The pipeline carried a set that
failed the build-ready gate (several blockers surfaced by the audit *before*
any code) to a published set that passed it, and from there to a
release-gate build with zero build-time blockers across the slice sequence.
The gate-bound publish step (failure-mode #30) fired cleanly — including a
*selective* re-publish of only the touched docs on the enhancement delta.
The post-hoc oracle confirmed same-product convergence: the rebuilt public
API matched the original's method-for-method, the two sets shared the great
majority of contract IDs, and the original's behavior tests passed against
the rebuild with **no behavioral divergences** — while the internal
architecture legitimately diverged (different module decomposition from the
same contracts), vindicating the "binding map is an output, started empty"
discipline. As with the earlier blind-detection work, **audit and build
caught different defect classes**: the LLM audit found structure/ownership/
register-form issues; only building-and-measuring surfaced two cross-concern
*contradictions* (a budget unreachable under the same doc set's own
architecture; a derived-count definition self-contradictory once a subject
is hidden).

**What the trial found about the standard, and where each finding was
placed.** Five weaknesses surfaced. The dividing principle for placement:
the *standard* takes only what is irreducibly about **what conformance
means**; the deterministic checks, the conformance fixtures, and this
narrative stay **here**.

- **Re-partition check too narrow (the headline).** The named vocabulary
  re-partition check (failure-mode #32) **ran clean and passed a defective
  set**: the upgrade added no sub-aspect *keys* — its additions were a new
  owned contract *kind* under an existing key, and a *broadened concern
  trigger* — so a key-diff had nothing to catch. → **Standard:** the
  `doc-maturity-auditor` now reconciles kinds and triggers too (a model-A
  judgment step; failure-mode #33). → **Here:** a deterministic backstop is
  possible only once concern specs expose owned-kinds/triggers as
  machine-readable fields — an **open tooling item** (a `partition-hole`
  fixture pair, kind-hole and trigger-hole, is the natural first artifact).

- **Register-form tie-break.** About a set's worth of owned IDs appeared on
  more than one register-*shaped* line (a Contracts recap of Requirements; a
  cross-concern accountability table). → **Standard:** Part 5 now keeps one
  register line per ID **by construction, order-independently** (owning-
  concern doc; recap tables must not take register-form position; failure-
  mode #34). An order-dependent "first line wins" was explicitly rejected as
  fragile. → **Here:** a `register-collision` fixture validates the
  extractor resolves ownership without guessing.

- **Doc-set membership — no standard change.** An owning-spec file (a
  feature spec re-homing a large list-shaped contract, Part 8) was
  under-copied when the set was seeded, and the loss surfaced only deep in
  the audit. The tempting fix — a first-class `doc_set_members` manifest
  field — was **rejected as redundant**: a missing owning-spec file makes
  its would-be-minted IDs *referenced-but-unminted*, i.e. exactly the
  dangling-reference case the idweb check already errors on. **Verified in
  this repo:** `gate-check fixtures/dangling-id` →
  `ERROR [idweb] … dangling reference … (owned prefix, no definition
  found)`. So the finding is a **fixture, not a bar change** — add a
  membership variant to `fixtures/dangling-id` and note that the existing
  check subsumes it. (The real cause was an operator input-selection slip,
  not a standard gap.)

- **Build-status record went stale.** An unattended build ran the slice
  sequence to green while the Delivery-owned build-status record still
  declared everything unbuilt — nothing forced the per-slice update. →
  **Standard:** Part 10e now names recording build-status an **explicit
  slice exit criterion** (failure-mode #35). → **Here:** the *detection*
  (built-but-record-unbuilt — an evidence-based, decidable check) belongs
  with the deterministic checkers, **not** the doc-maturity-auditor (reading
  build evidence there would blur doc-maturity ≠ implementation-status); an
  `unpublished-built` fixture variant is the home. The root cause, though,
  is builder discipline — a harness/DoD-checklist fix, outside both repos.

- **Toolchain-register home.** A set momentarily scoped Operations out while
  pinning build/test tooling, leaving `TOOL-###` homeless. → **Standard:** a
  one-line 11.10 clarification — pinning `TOOL-###` is itself an environment
  fact, so Ops is in and the register has a single home. A conditional
  "falls to Quality when Ops is absent" fallback was **rejected** as
  complicating owned-once for a near-empty case; no lab artifact (pure
  ownership adjudication, no empirical dimension).

**The residue that reached the standard is small on purpose.** Two of the
five (membership, toolchain-home) needed no new mechanism or no more than a
clarification; the deterministic halves of two others (kind/trigger backstop,
built-record detector) stay here as tooling until earned. Only what changes
*what conformance means* — the auditor's reconciliation remit, the Part 5
uniqueness rule, the Part 10e slice-exit criterion — landed as normative
text. A single trial is weak evidence for a bar change; routing the rest
through fixtures and this write-up is the discipline the boundary rule
already prescribes.

## Limits

- Four builds by a small number of implementers, all internal — not
  ecosystem-scale adoption evidence; the standard's positioning paper says
  so explicitly.
- The regeneration control ran on one codebase; the recall figures are
  point observations, not estimates with spread.
- The blind-rebuild trial is **n=1**: one product, one implementation
  language, one MINOR upgrade delta. Its findings are directional, not
  general — which is precisely why only the conformance-meaning residue was
  folded into the standard and the rest is staged here as fixtures pending a
  second trial. The rebuild's own test suite was authored by the same agents
  that wrote the code (self-confirming); the load-bearing evidence is the
  post-hoc oracle against the original's independent tests, not that count.
