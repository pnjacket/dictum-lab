---
artifact: research-companion
role: method
anchor: LAB-METHOD-EDIT-LOOP
non_normative: true
---

# Method: running an audit/fix loop without paying for it twice

Operational companion to `LAB-STUDY-AUDIT-FIX-LOOP`. That study reports what
happened across 22 fix passes on one doc set. This document is the part you can
apply, written so that someone starting a comparable loop needs far fewer rounds
than we did.

Every rule below is here because breaking it cost at least one full audit cycle.
The reason is attached to each rule, because a rule without its reason gets
dropped the first time it is inconvenient.

---

## 0. The single most valuable thing in this document

**Most of what an audit loop finds late, an interview could have decided early —
and the decisions are not arbitrary, they are instances of ten fixed question
schemas.** Read §4 before you start authoring. It is worth more than the rest of
this document combined.

The second most valuable: **fixing the span an audit points at is not the same as
fixing the sentence it lives in.** One paragraph in our trial was revised in four
consecutive passes, each fix correct about the thing it touched and wrong about
its neighbour.

---

## 1. The loop

```
analyse  →  fix  →  add a mechanism  →  re-audit
```

The third step is the one people skip, and skipping it is why loops do not
converge. In our trial the passes that added no mechanism did not reduce the next
pass's finding rate; the passes that added one did.

**Stop conditions.** Two, and only two: the audit comes out clean, or a finding
needs a decision that is genuinely the operator's. Everything else is work to do,
not a reason to stop.

**Escalate sparingly and specifically.** Over-escalation costs a cycle as surely as
under-escalation. Before asking, check whether the set's own mechanics already
settle it — twice in our trial a question was escalated that the documents had
already answered. When you do ask, give real options with their consequences, say
which you would take and why, and never present a decision that is really a
lookup.

**Between passes, keep the analysis loop closed.** Read every affected document end
to end, follow every affected ID into every other document, and iterate until
nothing new surfaces. Reading the *region* is how twins survive.

---

## 2. Editing rules

### Before you edit

1. **Read the whole document, not the region.** The reason a defect is a defect is
   usually somewhere else in the same file.
2. **Identify the element, not the sentence.** A contract element — a register
   line, a runbook row, a state — is the unit that has to stay true. Sentences are
   not.
3. **Enumerate the siblings before touching one.** If you are changing one of
   several things that were written together, list all of them first. The
   half-fixed twin is the single most common defect class and this is its whole
   cure.
4. **Follow the ID into every other document.** Not a grep for references — a read
   of what each consumer *derives* from it. References are cheap to check and
   rarely wrong; derivations are expensive to check and usually wrong.
5. **Ask what the change obliges.** A new arm, a new column, a new cause, a new
   parameter — each creates obligations at sites that will not change and
   therefore cannot be found by diffing.

### While you edit

6. **Assert before replacing, and write the file once at the end.** But know the
   trap: if a later assertion in the same script fails, every earlier successful
   replacement in that script is silently discarded. We reported a fix as done
   that had never reached the file.
7. **Read back every changed region, every time.** This is the rule that catches
   rule 6's trap, and it is not optional.
8. **Never edit a topic sentence and its evidence in separate passes.** If the
   evidence changes, re-derive the claim above it. Our four-pass paragraph was a
   correct clause under a topic sentence that had stopped matching it.
9. **Re-derive counts; never adjust them.** When you touch anything a count
   covers, recount from the sites. Adjusting "four" to "five" is how a count that
   was already wrong stays wrong.
10. **Prefer deleting a copy to synchronising two.** If a fact has two homes, one
    of them is a second thing to keep true. Give it one owner and leave a pointer.
    Where the second site carries *reasoning the owner does not*, deletion does not
    apply — make it name the owner instead.
11. **Retreat before adding.** In our trial the right answer was to remove surface
    four separate times. An addition that generates obligations at ten sites is
    usually the wrong shape of fix.
12. **When a "fix" makes something enforceable, ask what it now forbids.** We added
    a uniqueness index to enforce a guarantee; it would have broken the whole
    transaction on any ordinary restart-then-fail sequence.

### After you edit

13. **A green checker is not a read.** Structural checks see IDs. They do not see
    prose, counts, or arguments. In our whole trial the checker never once caught a
    stale prose count until a ledger was built for exactly that.
14. **Verify the class, not the instance.** After fixing one, search for the shape
    you just fixed. If you cannot express the shape as a search, that is the signal
    to build a mechanism.
15. **Record removals, not just additions.** A mechanism you deleted will be
    re-asserted by a document that reads perfectly well on its own, and nothing
    else can find it.

### Never

- **Never trust a new mechanism's green run.** See §3.
- **Never bulk-accept a gate** to clear unrelated work. If a gate can be defeated
  as a side effect, it is not a gate.
- **Never let a count claim survive an edit unverified**, including in your own
  commit message. Ours were wrong twice, in text describing the fix for wrong
  counts.

---

## 3. Building mechanisms

A mechanism is a deterministic check that makes a defect *class* harder to repeat.
Build one per pass, from the class you just met — not from a list of good ideas.

### The rule that matters most

**Re-break the original defect and confirm the check fails.**

Of the last five mechanisms we built, **three shipped broken** — one with three
defects at once — and every one of them reported a clean run while checking
nothing. The re-break test caught all of them and nothing else did. A new
mechanism's green run is not evidence; it is an untested claim.

### Design rules

- **A check that can silently pass must fail loudly instead.** If a check depends
  on an anchor — a fence, a heading, a field name — assert the anchor and report
  when it moves. Two of ours passed vacuously because their anchors had drifted.
- **An exemption is a hole shaped like the defect.** Ours was granted to the one
  element carrying the densest prose of exactly the kind being counted. Reword the
  content instead and keep the check at zero exemptions.
- **Scope beats threshold.** One of our checks reported 1142 findings file-wide and
  0 scoped to a paragraph. If a gate is noisy, ask what unit the defect lives in
  before you touch the numbers.
- **For a gate, prefer a denylist to an allowlist.** A false candidate costs one
  acceptance; a miss costs a blocker. We extended an allowlist four passes running
  with whatever noun had just bitten us — that is feeding the loop, not breaking it.
- **One acceptance flag per ledger.** Shared flags let routine work defeat an
  unrelated gate silently.
- **Every mechanism owes a written limit.** State what it cannot see, in the file,
  next to the code. Where we defended a limit instead of recording it, the next
  pass found a defect inside it.
- **Ledger the paths, not only the claims.** A ledger keyed on claim lines is
  silent by construction when a *new path* walks past an unchanged guard. Record
  the transitions themselves; a new or altered one fails until it has been walked.
- **A mostly-blind check is worse than none** — it conveys confidence it cannot
  back. Give such a check a standing deletion test: if a later pass finds it
  passing a defect of its own class, delete it rather than widen it again.

### Two mechanisms worth building first

If you build only two, build these. Between them they cover the classes that
produced eleven consecutive passes of blockers in our trial.

- **An arrow ledger** — every state transition recorded; a new or altered arm fails
  until walked against the guards it now passes (who may delete, who may raise,
  what must acknowledge).
- **A cause ledger** — when a condition gains a second cause, its *reader* surfaces
  fail until re-walked: routing table, runbook title and body, error-row meaning,
  payload schema, UI state.

One walks a new path against its **guards**; the other against its **readers**.

---

## 4. Intake saturation — the schemas

**Saturation is not a property of how long the interview runs.** Several of the
questions we paid an audit cycle for are not askable before the thing they are
about exists. Saturation is a property of **whether a fixed set of schemas has
been applied to every owned contract, at the moment it is minted.**

Apply these per element. **If the answer requires a decision rather than a lookup,
you are not saturated on that element** — and every one of those decisions, left
unmade, costs roughly one full audit cycle later.

| # | Schema | Ask of |
|---|---|---|
| 1 | What seeds it, what writes it afterwards, what reads it, and what is its value at first use? | every stored value |
| 2 | Who evaluates it, on what period, and what does it compute when an input has gone silent? | every predicate |
| 3 | What happens when nothing answers? | every wait |
| 4 | **Is it an observation or a diagnosis — can it be wrong? Is it absorbing? What does writing it cost that cannot be undone?** | every state |
| 5 | Enumerate the entry conditions: is each positive evidence, or is one an inference from absence? | every absorbing state |
| 6 | What does it bound, what bounds it, is the chain acyclic and total? | every threshold |
| 7 | What is the failure arm of its trigger? | every automatic transition |
| 8 | Enumerate its readers — routing, runbook, error row, payload schema, UI state. | every condition |
| 9 | Which paths reach it, and does each still satisfy it? | every "only", "never", "always" |
| 10 | If the answer is to remove surface rather than add it, record the removal. | every retreat |

**Schema 4 is the highest-yield question in this document.** Asked once, early, of
the terminal state in a health model, it would have collapsed most of an
eleven-pass sequence. The auditor that finally asked it reframed eleven passes of
apparently unrelated blockers as one unmade decision: whether that state was
absorbing, and whether its write could be taken back.

Each schema exists because a defect class exists. The mapping is in the study's
taxonomy: **each recurring class is a question that was not asked.**

---

## 5. One-page checklist

**Per fix pass**

- [ ] Read every affected document end to end — not the region
- [ ] Enumerate the siblings of everything you are about to change
- [ ] Follow each affected ID into every consumer, and check derivations not references
- [ ] Make the edits; assert before replacing; **read back every changed region**
- [ ] Re-derive every count the change touches, from the sites
- [ ] Run the checker — and remember it has not read the prose
- [ ] Search for the *shape* you just fixed, elsewhere
- [ ] Add or extend one mechanism against this pass's class
- [ ] **Re-break the original defect; confirm the mechanism fails**
- [ ] Commit with the reasoning, including what you removed
- [ ] Re-audit

**Per new mechanism**

- [ ] Does it fail loudly if its own anchor moves?
- [ ] Zero exemptions?
- [ ] Is its scope the unit the defect lives in?
- [ ] Its own acceptance flag?
- [ ] Its limits written in the file?
- [ ] Re-break test passed?

**Before authoring any element**

- [ ] All ten schemas in §4 answered by lookup, not by decision

---

## 6. What we would do differently

In order of expected saving:

1. **Run §4's schemas during intake**, per element, and record the answers as the
   element is minted. Most of our loop was an interview conducted through an
   auditor, one decision per cycle, with a full re-read of the set between each.
2. **Build the arrow ledger and the cause ledger before the first audit**, not at
   pass 53 and 54. They are cheap and they cover the most expensive classes.
3. **Adopt the re-break test from the first mechanism**, not the fifth.
4. **Separate the two rung judgements** — structure and content — from the start.
   Three concerns in our trial were at target on section completeness and below it
   on the truth of an owned contract, in the same pass. Reporting one number hides
   which is which.
5. **Treat "the auditor pointed here" as the start of the read, not the end of it.**
