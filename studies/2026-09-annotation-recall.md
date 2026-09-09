---
artifact: research-companion
role: study
anchor: LAB-STUDY-ANNOTATION-RECALL
non_normative: true
---

# Study: what in-code ID annotation actually buys (2026-09)

**Question.** The standard recommends tagging each realizing code site with its contract's
`DICT: <ID>` marker, and states that reverse-authoring the same codebase with and without such
annotation recovers structure about equally, while exact-ID recall "falls from roughly half to
near-zero" without it (STANDARD Part 10f; catalog #28). Two things were untested: whether those
figures hold, and whether recovery is even the benefit worth citing.

## Subject (by shape)

Two products, each already carrying a reverse-authored doc set, annotated in a separate pass:

- **A.** A static-analysis command-line tool with a library core. One language, ~2.7k lines,
  108 contracts across 15 kinds. Mechanism-heavy: almost every contract is a rule or a code artifact.
- **B.** A self-hosted web application — single-page client, HTTP API, embedded database, event push.
  ~4.9k lines, 201 contracts across 34 kinds, including personas, journeys, accessibility bars,
  policies and success criteria that product A has no equivalent of.

## Method

For each product, two copies of the code were prepared: one as-is, one carrying the annotation pass's
markers. **The doc set was deleted from both copies**, so neither could read the answer. Each copy was
given to a separate agent with identical instructions: read the code, list the contracts it realizes,
give each an ID, and label each ID recovered or coined. Output was compared against the product's real
doc set. Verified before comparing: the two copies differed only by marker lines, and the unmarked copy
contained zero contract-ID tokens.

## Finding 1 — the standard's figures are wrong in both directions

| | unmarked | marked |
|---|---|---|
| Product A | 41% | 92% |
| Product B | 30% | 69% |

Annotation roughly doubles exact-ID recall, which supports the recommendation. But "near-zero" without
it is wrong by a wide margin in both products, and "roughly half" understates the annotated case.

## Finding 2 — recall is set by coverage, not by quality

Both marked runs recovered **essentially every ID that carried a marker, and almost nothing else**.
Product A marked 92% of its contracts and scored 92%; product B marked 69% and scored 69%. The gap
between the two products is entirely explained by how much was markable, not by how well it was done.

## Finding 3 — what survives an unmarked pass is whatever the code names

Unmarked recall splits cleanly by whether a contract has a **name in the code**. Output schemas, events,
config keys and endpoints came back at or near 100%; entities and dependencies high. Decisions, patterns,
security assertions, accessibility bars, journeys, policies, runbooks, personas and success criteria came
back at **zero** in both products, and invariants at 7–13%.

The share of a product that is unrecoverable this way **scales with how much of it is judgement rather
than mechanism**: 18% of contracts in the mechanism-heavy tool, 35% in the web application.

## Finding 4 — a partial marker set suppresses discovery (the finding that changes practice)

The marked run on product B produced **fewer contracts in total** than the unmarked run — 144 against
153 — despite being handed 138 of them for free. It coined **6** IDs where the unmarked run coined 153.
Whole kinds the unmarked run had found unaided came back empty: its dependency and tooling contracts
went from 6/9 and 7/9 to zero and zero, those kinds having carried no markers.

The reading: an extractor handed markers treats them as the inventory and stops discovering. So partial
annotation is worse than none for the unmarked remainder, and the unit of the decision is the **kind**
(`LAB-PRACTICE-ANNOTATE-BROWNFIELD`).

## Finding 5 — recovery is the wrong justification

The measurement above simulates re-deriving a doc set from code that already has one. That is a rare
event: in the ordinary lifecycle the docs lead, the code follows, and nothing needs recovering. The
benefits that recur are drift detection, change-impact location, and a reader seeing the contract at the
site — none of which this method measured. **The recall numbers justify the recommendation less than the
standard's framing implies**; they mostly bound the re-adoption case.

## Limits

Two products, two languages, one model family, one annotation style. Ground truth is itself a
reverse-authored doc set that adversarial review showed to contain defects, so "recall" measures
agreement with an imperfect reference. Product A's naming is unusually literal, likely flattering its
unmarked score. Finding 4 rests on one observation with a real confound: the two extractions ran as
separate agent instances, so some of the gap may be instance variation rather than the marker effect.
It wants a controlled re-run before it is treated as settled.
