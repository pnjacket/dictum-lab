---
artifact: research-companion
role: study
anchor: LAB-STUDY-AUDIT-FIX-LOOP
non_normative: true
---

# Study: the audit/fix loop as a self-improving system (2026-08)

**Question.** A doc set at target rung is carried to a clean audit by repeated
audit → fix cycles. Does that loop converge? What makes it converge slowly, and
what — if anything — makes it converge faster?

**Short answer.** It converges, but the naive form is extremely expensive, and
the expense is not caused by carelessness. Two effects dominate. First, the loop's
length is set by **the size of the defect taxonomy** and the rate at which an
outside reader discovers it — not by how fast findings are fixed. Mechanisms close
classes permanently but do not shorten the loop while new classes are still
surfacing. Second — and this is the larger finding — a large share of the cycles
were not repairing documentation at all. They were **making product decisions the
interview never surfaced**, at a rate of roughly one decision per full audit cycle.
The loop was doing intake's job, by the most expensive method available.

**The two artifacts to reuse** are the fifteen-class taxonomy (Finding 1) and the
ten intake schemas derived from it (Finding 4). A loop that starts with both does
not have to pay to rediscover them.

---

## Subject (by shape)

A greenfield, doc-first set for an interactive multi-user web application with a
per-tenant ephemeral container runtime:

| | |
|---|---|
| Concerns | 12 in scope of 15, all targeted and claimed at contract-grade |
| Documents | 19 in the declared set, one concern split across six files |
| Packaging / granularity | per-concern, fine |
| Owned IDs | ~450 across 28 registers |
| Code authorship | model-authored (the set is the sole build input) |
| History | intake interview → level-up → this loop |
| State at the start of the observed window | at target rung, unpublished, audit trail recording 12 earlier passes |

**Standard version.** The set declares `authored_against: v1.2.0` and the vendored
standard at the subject's `dictum/` is v1.2.0 throughout. No upgrade delta is in
play anywhere in the window, so **no finding here is version-attributable** — a
distinction that matters if any of this is folded into a later release.

**Window.** Audit passes **13–59** and **22 fix passes**, run consecutively in one
working session, ending with the publish step. Passes 1–12 are known only through
the set's own audit-trail summary and are used for trend context, not as measured
data. The subject remains private; per `PROTOCOL.md` the raw audit outputs and the
pinned SHAs stay outside git in the trial record.

## Method

Each cycle: an independent auditor (LLM, following the standard's
`doc-maturity-auditor` procedure) read the whole set at a pinned git state and
reported findings with file/line evidence; the findings were fixed; the fixes
were committed; a new audit ran against the new state. Every fix pass ran a
deterministic cross-file checker before committing, and the checker was extended
during the loop (see *Mechanisms*). Operator decisions — where a finding needed a
product judgement rather than a wording repair — were escalated rather than
guessed, eight times in the window.

The auditor was asked, from pass 44 onward, to report not only findings but the
**structural reason** the class kept recurring. Those answers are the substance
of this study; the individual findings are not.

---

## Finding 1 — the recurring defect is structural, and there are fifteen classes of it

Every blocker in the window belonged to one of fifteen classes. Each is defined
by *what made it invisible*, not by severity. This taxonomy is the study's main
reusable artifact.

| # | Class | Why nothing saw it |
|---|---|---|
| 1 | **Half-fixed twin** — a fix lands on one of two adjacent sentences, or one of several sibling elements | The edited site is correct; the sibling reads fine alone |
| 2 | **Stale closed enumeration** — "four conditions", "the whole list" | No register to count against; truth lives in other files |
| 3 | **Conditional guarantee written unconditionally** | The qualifier exists — on a neighbouring sentence |
| 4 | **Unreachable contract** — consumed at full strength, supplied by nothing | Both halves read correctly in isolation |
| 5 | **Owned rule restated as *argument*, not copy** | Deleting the copy — the standard cure — does not apply; the restatement carries reasoning the owner lacks |
| 6 | **Column on a table that outlives its instances** | The defect is an *absence*: nothing states the lifecycle |
| 7 | **Paired elements declared equivalent** ("exactly as X does") that diverge in one detail | Field-parity checks count markers, never their contents |
| 8 | **A cadence that shapes contracted behaviour and is minted as no key** | A period with no ID is invisible to every ID-based join |
| 9 | **A predicate input with no seed or no writer** | The predicate reads correctly; nothing says what it reads *at start* |
| 10 | **Re-subjected clause** — an insertion separates a predicate from its subject | One site, edited correctly, whose *neighbour* changed meaning |
| 11 | **An acknowledgement gate with no arm for silence** | Every failure was written as an *arriving* negative acknowledgement |
| 12 | **Added-path invariant erosion** — a new arm walks past guards that still assert it cannot | **No line changes at any guard site** |
| 13 | **A condition that gains a second cause** | Same: the arm already existed; only its cause set grew, and its readers went silently partial |
| 14 | **Text integrity at the edit site** — an edit applied twice, spliced mid-sentence, or leaving markup unbalanced | No arm, count, or marker changed |
| 15 | **Credited and misquoted** — a restatement names its owner correctly and then misstates what it attributes | Naming the owner is the *pass condition* of the check that guards restatement |

Classes 12–15 were discovered only in the last quarter of the window, and they
share a property worth stating on its own: **the defect is invisible because
nothing changed where the defect is.** A ledger keyed on claim lines is silent by
construction against all four.

### The master class

Class 1 accounts for more blockers than any other, and classes 10, 12, 13 and 15
are refinements of it. Its cure is not care. Its cure is to make the *sibling set*
enumerable — which is what most of the mechanisms below do.

---

## Finding 2 — mechanisms close classes; they do not shorten the loop

An earlier draft of this study claimed the blocker count "declined monotonically"
once mechanisms began. **That was wrong**, and the correction is the more useful
result. Blockers per audit over the last ten passes:

| Audit | 50 | 51 | 52 | 53 | 54 | 55 | 56 | 57 | 58 | 59 |
|---|---|---|---|---|---|---|---|---|---|---|
| Blockers | 5 | 4 | 3 | 3 | 3 | 3 | **0** | 1 | 1 | **0** |

Mechanisms began at fix pass 8 (audit 44). **The count did not fall for twelve
further passes.** It sat between two and five while fifteen mechanisms
accumulated, then dropped to zero, produced two single-blocker passes, and went
clean.

What the mechanisms did do is precise and worth having: **no class recurred as a
blocker once its mechanism existed.** The misplaced-field-marker class produced no
further blocker after mechanism 1; the added-path class produced none after
mechanisms 12 and 13. The count stayed high because **new classes kept being
discovered** — fifteen over the window, several of them only in the final quarter.

So the loop's length is not governed by the fix rate. It is governed by **the size
of the defect taxonomy and the rate at which an outside reader discovers it** —
roughly one new class per pass in the later half. That is the strongest argument
in this study for doing the work earlier: the taxonomy is now written down, and a
loop that starts with it does not have to pay to rediscover it.

Confound, stated plainly: this is one trial, the set was also becoming more
correct, and no controlled comparison was run.

### The mechanism catalogue

Built in the order the classes were met. Each is deterministic and zero-dependency;
six ledgers live on disk, four inline in the checker.

| # | Mechanism | Decides |
|---|---|---|
| 1 | **Contract-field parity** | An element states each of its contract fields exactly once |
| 2 | **Mirrors** | Two declared copies of one fact still match (normalised) |
| 3 | **Closed-enumeration ledger** | Gates every prose count; re-verify on change |
| 4 | **Retirement ledger** | A deliberately removed mechanism is asserted nowhere but its retirement note |
| 5 | **Restatement gate** | An owned rule mentioned elsewhere must name its owner |
| 6 | **Instance-column classification** | Every column of a table that outlives its instances is reset-at-start or declared to survive |
| 7 | **Paired elements** | An element claiming another's path names at least one of its effects |
| 8 | **Cadence check** | A clause describing a machine period names a config key |
| 9 | **Predicate inputs** | Every column a predicate reads has a stated seed and a stated writer |
| 10 | **Re-subjected clause** | At a declared wire/column boundary, a mapping sentence names both sides |
| 11 | **Acknowledgement arms** | A gate waiting on an acknowledgement bounds the silence |
| 12 | **Arrow ledger** | Every state-machine transition is recorded; a new or altered arm fails until walked against its guards |
| 13 | **Flag-cause ledger** | When a condition's cause set changes, its *reader* surfaces must be re-walked |
| 14 | **Text integrity** | Repeated phrases, spliced punctuation, unbalanced emphasis |
| 15 | **Ordinal resolution** | A sentence indexing into an owned structure ("the second conjunct") resolves |

Mechanisms 12 and 13 are the pair worth transplanting first: one walks a new path
against its **guards**, the other against its **readers**. Between them they cover
the classes that produced eleven consecutive passes of blockers.

---

## Finding 3 — mechanisms ship broken, at a rate high enough to plan for

**Every one of the last five mechanisms built was found defective after reporting
a clean run**, one of them with three defects at once; two earlier mechanisms were
too. An earlier draft of this study said "three of the last five" — undercounted,
and corrected here. Observed failure modes:

- A ledger wrote the file path where it read a hash, so it never matched and
  would have reported every entry new for ever — then been bulk-accepted.
- A fence-matching regex stopped matching after the fenced block gained a comment
  line; the check passed vacuously, twice, during its own construction.
- A presence test accepted any config token, and so **passed the exact defect it
  was built for**, because the target element named a different key for a
  different arm.
- An ordinal check ran over raw text, so an *emphasised* ordinal — the form the
  original defect used — could not match, leaving the founding site unguarded
  while guarding two others.
- A gate shared another gate's acceptance flag, so routine acceptance of unrelated
  work silently re-recorded it.

### The discipline that caught all of them

**Re-break the original defect and confirm the check fails.** A green run from a
new mechanism is not evidence. This was the only method that caught any of the
above, and it caught all of them.

Corollaries adopted during the loop:

- **A check that can silently pass must fail loudly instead.** Anchor-based checks
  assert their own anchors and report when they move.
- **An exemption is a hole shaped like the defect.** One exemption was granted, to
  the element carrying the densest prose of exactly the kind being counted; it was
  removed by rewording the element instead.
- **Scope beats threshold.** One check compared clauses file-wide and reported
  1142 findings; the same check scoped to a paragraph reported 0. Tuning the
  threshold would have produced a useless gate either way.
- **Prefer a denylist to an allowlist for a gate.** An allowlist of nouns was
  extended four passes running by whatever noun had just bitten. A gate's false
  candidate costs one acceptance; a miss costs a blocker.
- **One acceptance flag per ledger.** Shared flags let unrelated work defeat a gate.
- **Every mechanism owes a stated limit.** Where a limit was defended rather than
  recorded, the next pass found a defect inside it.
- **A check that is mostly blind is worse than no check** — it conveys confidence
  it cannot back. One mechanism carries a standing instruction to delete rather
  than widen it on its next miss.

---

## Finding 4 — the loop was doing intake's job (the central finding)

**Where this came from, since it changes how much weight to give it.** The
hypothesis is the operator's, raised unprompted after the loop closed and the set
published: *the intake was not done to saturation, and that is part of the issue.*
It was not a finding of any audit — no auditor in 59 passes proposed it, because
each saw one pass and the pattern is only visible across the series. The study's
contribution is to test it against the record and to refine it: the record
supports the diagnosis and **contradicts the obvious remedy**. See *Why this is
not merely "the interview was too short"* below. Anyone revisiting this should
know the claim originated as an operator hypothesis and survived adjudication,
rather than being derived from the data in the first place.

Eleven consecutive passes produced blockers in one area: a three-state health
predicate over the container runtime, and the termination protocol around it.
Reviewed as a set, those eleven blockers were not documentation defects. Each was
an **unmade product decision**:

- What does the predicate read, and what writes each input?
- Who evaluates it, and on what period? (A standing condition with no sampler.)
- What does a stored flag mean once its writer goes silent?
- Is the terminal state an **observation** or a **diagnosis** — that is, can it be
  wrong, and can it be revised?
- What happens when an acknowledgement never arrives at all?
- May an automatic trigger restart a session that failed?
- Which threshold bounds which, and is the chain total?

Each was resolved, correctly, one per cycle. Each resolution created the next
question, because a decision made in isolation lands on guards nobody had walked.
The cost per decision was **one full audit** (a complete read of ~19 documents)
**plus one fix pass**.

### Why this is not merely "the interview was too short"

Several of these questions are not askable before the thing they are about
exists. You cannot ask *what happens when this command is unanswered* before the
command is minted. Interview length would not have helped.

What would have helped is that **every one of them is an instance of a question
*schema*** — and the schemas are fixed, small in number, and applicable to each
element at the moment it is minted. Saturation is therefore not a property of how
long an interview runs. It is a property of **whether a fixed set of schemas has
been applied to every owned contract**.

That reframing is the study's recommendation, and the schemas are derivable
directly from the defect taxonomy: **each recurring class is a question that was
not asked.**

### The saturation schemas

Applied per element, at mint time. If an answer requires a *decision* rather than
a lookup, intake is not saturated on that element.

1. **Every stored value**: what seeds it, what writes it afterwards, what reads it,
   and what is its value at first use? *(classes 6, 9)*
2. **Every predicate**: who evaluates it, on what period, and what does it compute
   when one of its inputs has gone silent? *(classes 8, 9)*
3. **Every wait**: what happens when nothing answers? *(class 11)*
4. **Every state**: is it an observation or a diagnosis — can it be wrong? Is it
   absorbing? What does writing it cost that cannot be undone? *(the eleven-pass
   sequence in one question)*
5. **Every absorbing state**: enumerate its entry conditions; is each one positive
   evidence, or is one of them an inference from absence?
6. **Every threshold**: what does it bound, what bounds it, and is the chain
   acyclic and total? *(class 8)*
7. **Every automatic transition**: what is the failure arm of its trigger? *(class 12)*
8. **Every condition**: enumerate its *readers* — routing, runbook, error row,
   payload schema, UI state — at the time the condition is defined. *(class 13)*
9. **Every absolute** ("only", "never", "always"): which paths reach it, and does
   each still satisfy it? *(class 12)*
10. **Every retreat**: when the answer is to remove surface rather than add it,
    record the removal. *(class 4; four of the loop's best fixes were removals)*

### The mapping — which class each schema would have prevented

This is the load-bearing link for anyone folding this into a standard: **each
schema exists because a class exists.**

| Schema | Prevents class |
|---|---|
| 1 stored value: seed / writer / reader / value at first use | 6, 9 |
| 2 predicate: evaluator, period, behaviour when an input goes silent | 8, 9 |
| 3 wait: what happens when nothing answers | 11 |
| 4 state: observation or diagnosis, absorbing, cost of writing it | the eleven-pass sequence; upstream of 11, 12 |
| 5 absorbing state: entry conditions, each positive evidence? | 12, 13 |
| 6 threshold: what it bounds, what bounds it, chain total | 8 |
| 7 automatic transition: the failure arm of its trigger | 12 |
| 8 condition: enumerate its readers at definition time | 13 |
| 9 absolutes: which paths reach them | 12 |
| 10 retreat: record removals | 4 |

Classes **1, 3, 10 and 14** are *not* covered by any schema, and deliberately so —
they are editing defects, not unmade decisions, and no interview prevents them.
They are what the mechanisms and the editing rules are for. Class **2** sits
between: the count is decided, the drift is editorial. Class **5, 7 and 15** are
authoring-discipline defects with the same character.

That split is itself a finding: **roughly two thirds of the taxonomy is
interview-preventable and one third is not.** Anyone budgeting a loop should
expect the second third to remain.

Schema 4 is the highest-yield single question in the list. Asked once, early, of
the terminal state in that health model, it would have collapsed most of an
eleven-pass sequence — the auditor that finally asked it framed the whole
sequence as one unmade decision about whether the state was absorbing and whether
its write was reversible.

---

## Finding 5 — what was never wrong (the negative space)

Equally useful for anyone deciding where to spend effort. Across all 22 fix passes,
these were verified repeatedly and **never produced a single finding**:

- **The vocabulary partition.** Every published sub-aspect key of every in-scope
  concern accounted for, all scope-outs verbatim published keys, on every pass that
  checked it. No hole, no near-miss, no legacy form — across ~90 keys.
- **Register counts against their registers.** ~28 registers, re-derived
  independently several times. The *prose* counts drifted constantly (class 2); the
  registers themselves never did.
- **Cross-reference integrity.** No dangling ID, no reference resolving into a
  scoped-out concern, no arm-suffixed token, in the entire window.
- **The Part 5 register-line rule**, after three early fixes: no owned ID reappeared
  in a lead cell.
- **Tombstones.** Retired IDs stayed retired and were never reused.
- **Index ↔ manifest lockstep.** No drift, ever, on a derived index.

The pattern: **machine-checkable structure over IDs was solid from early on; every
recurring defect lived in prose that reasons *about* that structure.** A standard
that leans on ID-web integrity is leaning on the part that works. The residual risk
is entirely in the argument layer, which is also where the value of the prose is.

## Finding 6 — negative results, reported at equal prominence

- **The deterministic checker never caught a stale prose count**, in the entire
  window, until a ledger was built for exactly that. ID-based joins do not see
  prose. A green structural check was repeatedly mistaken for a read.
- **Mechanism 2 (mirrors) has caught nothing since its first entry**, and its own
  comment argues the better cure is deleting the copy. It is retained only because
  it is the safety net for a deliberate second owner.
- **Mechanism 7 has caught one defect and passed one of its own class.** It carries
  a deletion instruction rather than an exemption.
- **Escalation was not free.** Eight findings were escalated as operator decisions.
  Two of those were later judged by a subsequent auditor to have been settled by
  the set's own mechanics all along — that is, they should have been decided, not
  asked. Over-escalation costs a cycle as surely as under-escalation.
- **One paragraph was revised in four consecutive passes**, each fix wrong in a
  different way: the ordinal, then the argument beneath it, then the topic sentence
  above it. Fixing the span an audit points at is not the same as fixing the
  sentence it lives in. This is the single most instructive failure in the window
  and it is not a tooling failure.

---

## What this suggests for the standard

Split per `PROTOCOL.md` into what looks ready to fold in and what should stay open.

### Candidates to fold in

1. **Failure-mode catalogue entries** for classes 12, 13 and 15 — the three whose
   defining property is that *no line changes at the defect site*. They are not
   covered by the existing entries, which assume an edited site.
2. **An intake bar** phrased as schema coverage rather than interview completeness:
   a concern is interview-saturated when every owned contract it mints has been put
   through the ten schemas above. This is checkable by review and is a stronger bar
   than "the interviewer ran out of questions".
3. **A note in the levelling guidance** that a rung claim can be sustained on
   section completeness while an owned contract inside it is false — three concerns
   in this trial were judged at target on structure and below it on content, in the
   same pass. The two judgements should be reported separately.

### Left open — do not fold these in on this evidence

- **Whether the schemas belong in the standard at all.** They may belong in the
  interview *skill* rather than in normative text; a bar phrased as "schema coverage"
  is only checkable if the schemas are enumerated somewhere normative, and enumerating
  them freezes a list this trial derived from a single subject shape.
- **The one-third of the taxonomy that no schema prevents.** Classes 1, 3, 10 and 14
  are editing defects. Whether a standard should say anything at all about editing
  method is a genuine question and this trial does not answer it.
- **Whether any of the mechanisms generalise.** All fifteen were built against one
  set's conventions. Two (arrow ledger, cause ledger) look transplantable because
  they key on structures the standard itself mandates; the rest key on this set's
  house style. Nothing here justifies shipping them as reference tooling without a
  second subject.
- **The escalation rate.** Eight operator decisions in 22 passes, two of which were
  later judged to have been decidable from the set. There is no evidence here about
  what the right rate is.

## Reproducing

The loop protocol, the editing rules it produced, and the mechanism-design rules
are written up prescriptively in `LAB-METHOD-EDIT-LOOP` (`METHOD-EDIT-LOOP.md`),
which is the operational companion to this study.
