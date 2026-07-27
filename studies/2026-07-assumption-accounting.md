---
artifact: research-companion
role: study
anchor: LAB-STUDY-ASSUMPTION-ACCOUNTING
non_normative: true
---

# Study: assumption accounting — is an assumption a node? (2026-07)

**Question.** Dictum records an inferred answer as an inline `[ASSUMPTION]`
subject marker (STANDARD Part 6), durable into published docs, "surfaced for
audit" (Part 0.6). The candidate change under test: promote an assumption that
**something depends on** to a first-class owned contract kind, `ASSUMPTION-###`,
minted register-form like any other ID, so it becomes a **node in the ID web**
and falsifying it propagates through the existing 10d machinery. The research
question: **does an assumption behave like a node on real doc sets — and what
does the promotion cost?**

**Status: retrospective pass complete (2 trials, 3 real doc sets); F5 open.**
Ground truth is a small corpus of real, pinned doc-set states (per
[`PROTOCOL.md`](../PROTOCOL.md)), not synthetic fixtures. Nothing here is
normative; the standard's text is the only definition of conformance. F1-F4 are
answered below and **F4 falsified part of the candidate rule**; F5 needs a
prospective trial and **no change to the standard is proposed until it runs**.

## Background — the diagnosis chain this study comes from

Reported failure, by shape: on a doc set maintained through incoming bug and
feature requests, an AI author repeatedly wrote `[ASSUMPTION]` markers into
docs that remained claimed at **Contract-grade**, and the operator read this as
"the model forgot to downgrade the doc."

Three corrections landed before the candidate rule took its current form, and
they are recorded because each one killed an earlier, worse proposal:

1. **The rung ladder measures determinacy, not correctness.** A doc stating
   `[ASSUMPTION] retention is 30 days` *is* buildable without guessing — the
   contract is definite, testable, unambiguous. The risk is that 30 days is
   **wrong**, i.e. the right thing gets built from the wrong premise. Dictum has
   never claimed the rung measures whether the contract matches the world
   (that is what Verified proves against the *contract*, not against reality).
   → The first proposal — cap the rung on an open assumption — was **withdrawn**:
   it makes the ladder carry correctness risk, which is the rigor/intent axis the
   standard has refused four times (Part 0.4; failure-mode #8) entering by a
   different door.
2. **`[ASSUMPTION]` is a provenance marker, and it is overloaded.** Part 0.6
   already states its purpose: an inferred answer is recorded "and surfaced for
   audit, precisely because no one was asked." But one token currently carries
   three distinct meanings — *nobody was asked* (procedural), *a decision was
   taken that belongs to the operator* (authority), *nobody knows yet*
   (epistemic). Only the third can affect buildability, and when it does the
   contract is simply underdetermined — already a `[GAP]` or a non-observable
   acceptance criterion, caught by machinery that exists.
3. **The obligation attached to the marker has no artifact.** "Surfaced for
   audit" names no surface. The level-up skill's stronger requirement — every
   settled-on-behalf item must be *both* written as `[ASSUMPTION]* and* "read
   back to the operator for an explicit yes/no before it stands" — appears in
   exactly one skill and nothing checks it. The maturity auditor's gap list
   names `[GAP]`/`[REVISIT]` and **not** `[ASSUMPTION]`. So **writing the marker
   silently discharges the obligation.** This is Part 0.7's own limit — gates
   check artifacts, never attention — applied to the one place the standard left
   an obligation resting on attention.

The failure is therefore **not** a maturity-scoring bug and **not** the model
being careless. It is a missing artifact, and the fix is an accounting fix.

## The candidate rule under test

- **New owned kind `ASSUMPTION-###`**, minted on a register line in an owning
  concern doc, conforming to the Part 5 ID token grammar — so it is
  machine-extractable by anything that already reads the register, and the
  review artifact is **derived, never stored** (Part 0.5).
- **Kept alongside the inline `[ASSUMPTION]` marker**, split by one test:
  **mint when a contract depends on it; mark when it is bare provenance on a
  fact.** The split falls out of the mechanism — propagation needs somewhere to
  go — rather than being imposed on it.
- **Dependents reference it by ID** (`API-014` rests on `ASSUMPTION-007`), so
  falsification reuses 10d reverse traversal with no new machinery.
- **Confirmation is a state transition on the node, not a tombstone** — the
  reference survives as provenance ("assumed, then confirmed"). This makes it
  the first ID kind with mutable state, which is a cost, not a freebie.
- **Disclosure gate-bound; review optional.** The build-ready gate reports the
  open-assumption set and does not block. Autonomy is preserved in full: an
  unattended author mints and moves on; a review skill runs later, or never.

## Falsifiers — what would kill or reshape the rule

Stated before measurement. Each is a real objection, not a formality.

| # | Falsifier | Kills / reshapes |
|---|---|---|
| F1 | **Split degenerates.** If ~all real assumptions have dependents, the two-tier design is pointless ceremony (mint everything); if ~none do, the ID kind has no propagation to enable and the marker was already right. | The two-tier split |
| F2 | **Not referenceable.** If an assumption's dependents cannot be named as contract IDs — because the assumption is diffuse ("the PoC is single-tenant") rather than attached to specific contracts — the edge cannot be written and the node buys nothing. | The whole rule |
| F3 | **Registry drowning.** If a real set would mint assumption nodes on the order of its contract count, the ID web's signal-to-noise degrades and `ASSUMPTION-###` becomes the dominant kind. | Population viability |
| F4 | **Lifecycle churn.** If assumptions resolve fast and in bulk, mutable-state nodes accumulate as permanent scar tissue in a registry whose discipline is "never reused, never renamed." | State-vs-tombstone |
| F5 | **Comfort effect.** If a tidy first-class path for inference makes an AI author assume *more* — the autonomy concession leaking into operator-present use, failure-mode #25 accelerated — the accounting win is paid for in worse elicitation. | The rule's net value |
| F6 | **Meta-kind precedent.** `ASSUMPTION-###` is the first kind describing the doc's epistemic state rather than a product commitment. If accepted, the next asks are `GAP-###`, `REVISIT-###`, `DECISION-###` — some of which are worse ideas. | Registry design |

**F5 is not measurable retrospectively** and is deferred to a prospective phase
(below). **F6 is a design judgment, not an experiment.** This pass tests F1–F4.

## Method

Two retrospective trials over pinned real doc-set states, chosen for opposite
properties. Products are described **by shape only**; raw per-repo artifacts
stay outside git (the describe-by-shape constraint).

**Corpus note, recorded because it shapes what is measurable.** A survey of five
real Dictum doc sets found live `[ASSUMPTION]` populations of **25, 0, 0, 0, 0**
(excluding each repo's vendored copy of the standard, its vendored skills, and
the one-per-doc template footer line — an uncorrected count over those inflates
the totals roughly 3×, which is itself worth knowing for any tool that counts
markers). Four of five sets carry none. This is **ambiguous by construction**:
it is consistent with assumptions being a transient authoring-time phenomenon
resolved before publish, *and* with assumptions being made and never marked
(the silent case, failure-mode #25). **A zero count is not evidence of no
assumptions**, and no retrospective read separates the two. Trial B is designed
to attack exactly that ambiguity from the history side.

### Trial A — the split, on the one populated set

Subject: a **multi-realm commerce web application** (three user realms, local
Kubernetes deployment, PoC scope), published and audited, 25 live
`[ASSUMPTION]` occurrences.

For each occurrence: classify as **mint-worthy** (a named contract depends on
it) or **mark-worthy** (bare provenance); where mint-worthy, enumerate the
dependent contract IDs and whether they are stated in the doc or must be
inferred; record which of the three overloaded meanings it carries. Measures
F1, F2, F3.

### Trial B — lifecycle and falsification, on a set plus its blind twin

Subject: a **spreadsheet-shaped formula/grid engine library**, and a second doc
set produced by rebuilding that product **blind from its own docs** by
independent agents. Zero live assumptions in both — so instead:

- **History mine:** recover assumptions that were raised and later resolved from
  the git history of both sets; measure how many, how they resolved (confirmed /
  corrected / converted to `[GAP]` / scoped out / silently deleted), and how long
  they lived. Measures F4, and tests whether the zero live count means *resolved*
  or *never marked*.
- **Divergence probe:** where the blind rebuild's doc set disagrees with the
  original, ask whether the divergence traces to an assumption resolved
  differently. Each such point is a natural experiment in what falsification
  would have had to propagate to.

### Phase 2 — prospective, not run in this pass

F5 needs a forward trial: run one hypothesis-shaped feature delta on the
commerce set under both regimes (marker-only vs `ASSUMPTION-###` available) and
compare elicitation depth and assumption count. Recorded here so the gap is
explicit rather than quietly unmeasured.

## Findings

### Extraction cost of the new kind: zero (measured)

Independent of Trials A and B, and decidable now: **`ASSUMPTION-###` needs no
tooling change to be minted, extracted, or walked.** Executed against the lab's
own shared parser (`tools/common/dictumlib.py`), which is the JS/Python-parity
implementation of the Part 5 grammar and register form:

- `ASSUMPTION-007` and the semantic-suffix variant `ASSUMPTION-TOKEN-TTL` both
  satisfy the ID token grammar exactly.
- All three register-form shapes mint it — table row (ID in first cell),
  list item, and heading — with no parser change.
- The prefix registry is **informational, never a gate** (Part 5: "an
  off-registry prefix is not itself a finding"), so an `ASSUMPTION` prefix is
  reported as unregistered metadata and nothing rejects it.

This closes one plausible objection cheaply: the promotion rides the existing
machine-extraction extension points rather than extending them, so the derived
register is a *query over material that already parses*. It says nothing about
whether the kind is a good idea — F1-F6 remain open.

### Trial A — the split, on the one populated set

Subject as described in Method: 13 published concern docs, all in-scope concerns
claimed Contract-grade, ~249 owned contract IDs.

**Protocol finding, recorded first because it constrains every number below.**
The measured doc set is **untracked in its repo** — the commit SHA pins the
product, not the docs. PROTOCOL.md's pinned-state requirement was therefore not
satisfied by the SHA alone, and the state was preserved as an out-of-git
snapshot instead. Any lab trial over a doc set must **verify the docs are
tracked before pinning by SHA**; this is the second corpus-hygiene trap in this
study, after the vendored-copy over-count.

**Census fragility (both directions).** The expected 25 confirmed exactly, but
the number is soft in three ways: **+2** arrow-form variants (`[ASSUMPTION →
confirm in X]`) that a tool keying the bare literal misses (7% undercount here);
**−7** that are pointers to assumptions asserted elsewhere rather than
assertions, and 3 further restatements, giving **17 distinct marked
propositions**; and **+3 unmarked assumptions** in the same docs ("Push is
assumed", "(assumed yes.)"). That last is this corpus's **first direct
observation of the silent case** (failure-mode #25) — a **15% unmarked rate in
the set that marks best.** *"How many assumptions are there"* has no
tool-stable answer today.

| Falsifier | Verdict | Measurement |
|---|---|---|
| **F1** split degenerates | **not triggered** | Live: **7 mint-worthy / 6 mark-worthy (54/46)**. All 17 marked propositions: 11/6 (65/35). Neither degenerate branch holds. |
| **F2** not referenceable | **reshaped, not triggered** | **No assumption was unattachable.** 10 of 11 mint-worthy had ≥1 dependent whose edge is *stated* today. But raw edges run ≈50/50 stated/inferred, and **3 propositions have their most consequential dependents entirely inferred** (9, 6, and 13 IDs respectively). |
| **F3** registry drowning | **not triggered, comfortably** | **1 : 23 (4.4%)** of owned IDs; 2.8% counting live only; even a naive mint-on-every-marker stays at 10.8%. Would be the registry's 4th-*smallest* kind. |

**F2 must be restated.** Its drafted form — "dependents cannot be named" — is
too strong. The real cost is the **stated-fact / unstated-edge** pattern: the
dependents are each individually written down (an endpoint marked `public`, a
role guard, an audit action list) while the *edge* to the assumption is written
nowhere. Minting therefore requires reading the whole set to discover 9-13
dependents — **an attention-dependent obligation at the mint moment**, which is
exactly what Part 0.7 says a gate cannot enforce. The rule would relocate the
attention problem rather than remove it.

#### The finding that may defuse it

**The split correlates almost perfectly with the *authority* axis.** Of the
three overloaded meanings, the dominant distribution was `not-mine-to-decide`
**9** · `not-asked` **7** · `unknowable-yet` **0 dominant, 1 secondary**. And:
**all 9 `not-mine-to-decide` propositions are mint-worthy (9/9); 6 of 7
`not-asked` are mark-worthy.**

If that replicates, *"does a contract depend on this?"* and *"is this the
operator's call?"* are the **same test** — and the second is answerable at
write time, from the author's own knowledge, with no dependency search. The
mint decision would then cost nothing at the mint moment, and F2's discovery
cost lands on the *review* pass where attention is affordable.

Separately, **`unknowable-yet` being essentially absent** corroborates
diagnosis-chain correction #2 empirically: its single appearance already carried
a `[GAP]` alongside, i.e. existing machinery had caught it. The epistemic case
that motivated the original hypothesis discussion is real but **rare in
published sets** — it lives in the authoring moment, not the artifact.

#### What the method failed to anticipate

1. **`ADR-###` is already the assumption-node kind — for one class.** Two of the
   eleven mint-worthy assumptions are *simultaneously* marked `[ASSUMPTION]` and
   carried as accepted ADRs with context / **status** / consequences: the
   proposed shape, mutable state included. This cuts both ways. It is a
   **necessity objection** for architecture-shaped assumptions (that class is
   already served), and it **weakens F6** — `ADR-###`'s `status:` is already a
   mutable, non-product-commitment attribute, so `ASSUMPTION-###` would not be
   the first meta-ish kind or the first with state. The genuinely uncovered
   classes are **business-terms** and **posture** assumptions. That may be the
   real scope of the problem rather than "assumptions" generally.
2. **Mutable state already appears in the wild, unprompted, in two incompatible
   forms** — `[ASSUMPTION → confirmed: …]` and `**Resolved [ASSUMPTION]:**`.
   Nothing in the standard or the skills asked for this. Independent support for
   *confirmation-as-state-transition*; also evidence the marker grammar is
   **already non-uniform**, which is a tooling problem today, not a future one.
3. **A discharged obligation with an uncleared marker.** One doc still reads
   `[ASSUMPTION → confirm in Architecture]` while ten lines below it records the
   same question **Confirmed** via a named ADR. Diagnosis-chain point #3 in
   inverse: the obligation was *met* and the marker still lies. Nothing reads
   `[ASSUMPTION]`, so neither the maturity auditor nor gate-check catches it. A
   stateful node makes this decidable.
4. **Authors defuse assumptions in prose — a third option the two-tier rule has
   no slot for.** Several markers carry their own falsification-neutralizer
   ("any local k8s works; values-swappable"). That is neither *mint* nor *mark*
   but **"a contract depends on it, parameterized"** — and 3 of 6 mark-worthy
   calls rest on this move, which the rule as drafted would push to MINT,
   producing nodes the author has already argued are inert.
5. **The disclosure surface is already being hand-rolled — and is already
   stale.** The set's README aggregates open assumptions by hand, in the one
   file whose own header declares it *derived from the manifest*. It lists 5 of
   13 live assumptions. This is the strongest evidence in the trial that the
   surface is genuinely wanted, and that the manual version does not survive
   editing.
6. **One marker, two propositions.** A single marker asserts two independent
   claims with different dependents. A per-marker mint collapses them; the bar
   needs a **one-proposition rule** the inline marker never had to carry.

#### Open questions that must be settled before F1's number is trusted

Four classifications were marginal, and they are marginal for two *systematic*
reasons the rule does not currently address:

- **Self-containment** — an assumption sitting *inside a named contract's own
  body* (a threat-mitigation control, a test policy). Is its container a
  dependent? If yes the node points at itself. The rule needs an explicit
  clause; without one this class alone can flip the split.
- **Parameterized dependency** — finding 4 above.

Flipping all four marginals moves live mint/mark from 7/6 to either 4/9 (31%
mint) or 11/2 (85%). **F1's verdict is robust at the reported classification but
not to a wholesale re-reading of the marginals.** 54/46 should not be treated as
settled until both clauses are written.

One further gap the rule cannot express: for one assumption, falsification would
**mint new contracts** rather than change existing ones (there is no
rate-update endpoint to break). Reverse traversal (10d) does not handle
propagation toward contracts that do not yet exist.

### Trial B — lifecycle and falsification, on a set plus its blind twin

**Method limit up front.** The original set's history is **squashed to a single
authoring commit** (reflog exhausted, `fsck --lost-found` empty). Its
doc-authoring history is unrecoverable, so Part 1 is measurable **only on the
blind rebuild** — which carries a complete 22-commit lifecycle (baseline →
audit → Contract-grade + publish → plan → 21 build slices → doc-led delta →
oracle). *Corpus lesson: PROTOCOL.md pins **states**; it does not require
**recoverable history**. Half this trial was unmeasurable for want of a
requirement nobody wrote.*

#### F4 — no lifecycle to measure, because there were no assumptions

**Zero `[ASSUMPTION]` markers ever existed in either set** — not "resolved to
zero", never nonzero. A per-commit census across all 22 rebuild commits and all
3 original commits holds **flat at 2** (the two template footer lines) at every
single commit. Meanwhile `[GAP]` runs 0 → 2 → 26 → 18 → 16 and `[FUTURE-SCOPE]`
13 → 27. **The other markers churn; this one never moves.**

**The traffic went two places instead.**

1. **Into `[REVISIT]` and bare prose.** "*Policy (confirmed for v1)*: worker
   crash is fatal"; "*No hard memory cap* (operator decision)"; provisional perf
   numbers under `[REVISIT]`. The **authority** and **epistemic** senses of
   `[ASSUMPTION]` leak into tokens that mean something else, and into
   parentheticals nothing can find.
2. **Into a spontaneously invented assumption register.** The rebuild's author
   created a decisions file of **27 register-form entries**, self-described as
   "the **elicitation output** — the answers a product owner gives when the
   authoring tooling surfaces a `[GAP]` … this file is the audit trail."

**That second finding is the strongest single result in this study: an author
with no rule for it built the candidate rule's artifact anyway.**

**And the standard could not see it.** The register appears nowhere in the
manifest; no concern owns it; its entry IDs (`D13`) do not match the Part 5
token grammar. So a 27-node register that **65 lines of published contract text
cite** is invisible to gate-check, the maturity auditor, and the drift detector.
The study's "missing artifact" diagnosis is reproduced in the field **with a
twist — the author did build the artifact and the standard still could not
consume it.**

**F4 proper — the state machine would have fired zero times.** All 27 entries
were minted in **one commit**; across 20 subsequent commits and an entire build
there were **zero removals and zero transitions**. Each entry arrives *already
resolved* — the lifecycle collapsed into the elicitation event. The `[GAP]`
proxy behaves the same way: +24 in one commit, then 9-11 cleared in one commit
(every toolchain-version gap at once, because they were all one question).
**No individual resolution occurs anywhere in the history.**

> **F4 verdict: the feared churn did not occur — and neither did any
> transition.** The cost is not scar tissue but a fixed **+27 permanent nodes on
> ~563 IDs ≈ 4.8%**, which independently reproduces Trial A's 4.4%. On this
> evidence **the mutable state field is unearned complexity; the reference edge
> is what carried the value.** Caveat: n=1, on a set whose author front-loaded
> all elicitation into one audit phase. A set maintained through incoming
> requests — Trial A's shape — may churn differently.

#### Ambiguity verdict: "never marked", not "resolved"

**High confidence for the rebuild; inconclusive for the original.** The rebuild's
marker count sits at the footer baseline at *every commit of a complete
authoring-and-build history* — there is no state in which it was ever higher —
while 27 real inferred answers were made and recorded under a different token in
a different file. **The zero is not a resolved population; it is a population
routed elsewhere.** For the original, the squashed history makes the honest
verdict *inconclusive*.

#### Divergence probe: 11 of 15 trace to an unmarked assumption

The rebuild's baseline is **byte-identical** to the original's 13 concern docs,
so every subsequent rebuild edit marks a point where the original
underdetermined something. Of 15 divergences examined: **11 trace to an unmarked
assumption, 1 mixed, 3 other** (deliberate deltas and a conformance correction).

The decisive case: the original set asserts **both** "the default transport is
in-process — no worker at all" (a security-compat contract) **and** "canonical
data + heavy ops in a worker from v1 · accepted" (an ADR), with its own
performance numbers measured through the worker path. The rebuild resolved to
worker-by-default — and its build phase then found a `PERF-###` mount budget
**unreachable** (2.2 s structured clone against a ≤300 ms budget). **An unmarked
assumption falsified a performance contract downstream: exactly the propagation
the candidate rule exists to carry.** Would-be dependents: 8+ IDs spanning
security, architecture, messaging, and performance.

Other cases carried 5-11 dependents each (edit-preemption policy, selection add
policy, a column cap inferred from a packed-key encoding that the original never
states, a `colCount` field three invariants bound themselves with but no entity
defines).

#### F2, re-measured — and the result inverts Trial A's

Unplanned and, I think, decisive: **the rebuild wrote the dependency edges
itself.** 65 `(D##)` citations across 14 files; **23 of 27 nodes have ≥1 inbound
citation; 121 distinct node→contract-ID edges; 19 of 23 cited nodes name at
least one dependent contract ID**; and 16 of 27 entries name contract IDs in
their own body — the edge is written **from both ends**.

Set against Trial A, where dependents were nameable but the *edges were written
nowhere*, this isolates the variable: **the edges get written when the
assumption is authored as a register entry, and do not when it is authored as an
inline prose marker.** F2's cost is not a property of assumptions; it is a
property of the *form*. That is the study's most actionable finding.

#### Incidental findings (outside the question, worth acting on)

- **The Part 5 token grammar over-matches prose and mis-handles elision.** False
  positives: `ISO-8601`, `RFC-4180`, `BCP-47`, `GPL-3`, `YYYY-MM-DD`. Phantom
  mints from suffix-elision style (`` `LIB-SET-DATA`/`-GET-ROWS` `` yielding
  `GET-ROWS`). **~24 of 48 apparent original-only IDs were artifact.** Note the
  standard's pending resolves-to-a-mint clause would kill the first class; the
  lab's three grammar implementations should be checked against both.
- Two performance contracts still carry `[GAP]` at the rebuild's HEAD,
  contradicting both the set's own decision entry ("none may reach the release
  gate un-numbered") and its observation report. **Two tracked deferrals
  survived the release gate un-numbered and nothing detected it.**

## Synthesis

| Falsifier | Verdict | Basis |
|---|---|---|
| **F1** split degenerates | **not triggered** | 54/46 live on the populated set — but marginal-sensitive (see Trial A's open clauses) |
| **F2** not referenceable | **refuted, and reframed** | No assumption was unattachable in either set. Whether the *edge gets written* depends on **form**: register → written from both ends; inline marker → written nowhere |
| **F3** registry drowning | **refuted** | **4.4%** and **4.8%** on two independent sets |
| **F4** lifecycle churn | **refuted — and it takes the state field with it** | 27 nodes, one commit, **zero transitions** across a full build |
| **F5** comfort effect | **unmeasured** | Prospective by nature; phase 2 |
| **F6** meta-kind precedent | **weakened** | `ADR-###` already carries mutable `status:` and is already not a product commitment |

**What the corpus establishes.** Assumptions are real, consequential, and
**mostly unmarked** — 15% unmarked in the set that marks best, and ~73% of
examined blind-rebuild divergences traced to one. They are attachable to named
contracts, they are few enough to mint (~5% of the ID web), and when one is
falsified it moves real contracts across concerns. Two independent authors
**built a register for them without being told to**, and in one case that
register is already the second-class citizen this study predicted: cited by
published contract text, invisible to every tool.

**What the corpus does not support.** Confirmation-as-state-transition. Nothing
transitioned. The value observed is entirely in the **reference edge**, not in
node state.

## Recommendation

**Do not propose `ASSUMPTION-###` to the standard yet — propose the smaller
thing the evidence actually supports, and run phase 2 first.**

1. **Drop the mutable state field** from the candidate rule. Zero transitions
   across a complete build is not weak support, it is none. Confirmation can be
   an ordinary doc edit; the node's value is being *referenceable*, not being
   *stateful*. This also removes the F6 objection almost entirely.
2. **Keep the node, keep the two-tier split, restate the split test.** Trial A's
   authority-axis correlation (9/9 `not-mine-to-decide` mint-worthy) means the
   test can be *"is this the operator's call?"* — answerable at write time
   without a dependency search — rather than *"does a contract depend on it?"*.
   Verify that correlation on a second set before relying on it.
3. **Treat the form, not the kind, as the intervention.** F2's inversion says
   the register form is what causes edges to be written. A rule that adds an ID
   kind but leaves assumptions authored inline may capture little of the
   observed benefit.
4. **Settle the two clauses Trial A exposed** — self-containment (an assumption
   inside a contract's own body) and parameterized dependency (an author's
   written falsification-neutralizer) — before F1's split number is trusted.
5. **Investigate a possibly larger and different problem.** The dominant real
   shape in Trial B was not an inferred answer but **an invariant deferring to a
   named policy that was never written** ("resolves per the commit/cancel
   policy"). That is closer to a dangling reference than to an assumption, and
   the ID web could plausibly already catch it if policies were referenceable
   things. It may deserve its own study rather than being absorbed here.
6. **Run phase 2 (F5) before any normative proposal.** The comfort effect is the
   one falsifier that could invert the value of everything above, and nothing
   retrospective can touch it.

**Standing constraint:** none of this changes the rung ladder. The corpus
supports the diagnosis that this is an accounting problem, and every measured
result is consistent with maturity remaining a determinacy judgment.

## Recommendation

*Pending measurement. No change to the standard is proposed until F1–F4 are
answered; F6 is an explicit design decision for the standard's maintainer, not
an output of this study.*
