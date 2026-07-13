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

## Limits

- Four builds by a small number of implementers, all internal — not
  ecosystem-scale adoption evidence; the standard's positioning paper says
  so explicitly.
- The regeneration control ran on one codebase; the recall figures are
  point observations, not estimates with spread.
