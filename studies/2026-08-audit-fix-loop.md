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
the expense is not caused by carelessness. Two effects dominate. First, fixing
*instances* does not lower the recurrence rate; only adding *mechanisms* does,
and the mechanisms must be built one defect-class at a time from the defects
actually observed. Second — and this is the larger finding — a substantial
majority of the cycles were not repairing documentation at all. They were
**making product decisions the interview never surfaced**, at a rate of roughly
one decision per full audit cycle. The loop was doing intake's job, by the most
expensive method available.

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

The observed window covers **audit passes 13–59** and **22 fix passes**. Passes
1–12 are known only through the set's own audit-trail summary and are used here
for trend context, not as measured data.

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

## Finding 2 — instance fixes do not lower the recurrence rate

For the first nine fix passes in the window, every pass fixed its findings
faithfully and every subsequent pass found a comparable number, most of them
newly introduced by the previous fix. Recurrence did not fall.

From the tenth pass, each cycle ended by adding a mechanism aimed at the *class*
just observed. Fifteen mechanisms were built. The blocker count then declined
monotonically over the last five passes — 5, 3, 3, 1, 1, 0 — and the character of
the findings changed from contractual to editorial before reaching zero.

That is one trial and the confound is obvious: the set was also getting more
correct. The claim made here is narrow and is the one the evidence supports —
*the passes that added no mechanism did not reduce the next pass's finding rate;
the passes that added one did.*

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

**Of the last five mechanisms built, three shipped defective**, and one shipped
with three defects at once. Every one of them reported a clean run while checking
nothing, or nearly nothing. Observed failure modes:

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

Schema 4 is the highest-yield single question in the list. Asked once, early, of
the terminal state in that health model, it would have collapsed most of an
eleven-pass sequence — the auditor that finally asked it framed the whole
sequence as one unmade decision about whether the state was absorbing and whether
its write was reversible.

---

## Finding 5 — negative results, reported at equal prominence

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

Offered as candidate distillations, not as text:

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

## Reproducing

The loop protocol, the editing rules it produced, and the mechanism-design rules
are written up prescriptively in `LAB-METHOD-EDIT-LOOP` (`METHOD-EDIT-LOOP.md`),
which is the operational companion to this study.
