---
artifact: research-companion
role: practice
anchor: LAB-PRACTICE-ANNOTATE-BROWNFIELD
non_normative: true
---

# Practice: annotate the code after a brownfield adoption

**The practice.** After reverse-authoring a doc set onto an existing codebase (STANDARD Part 10f),
and only with the code owner's explicit go-ahead, tag each realizing code site with its contract's
`DICT: <ID>` marker. Do it as a **separate step after** the adoption, never as part of it.

## Why it is a separate step

The reverse-authoring flow reads the product and writes only documentation — that read-only stance is
one of its guardrails. Annotation writes into product code, which is a different kind of act needing a
different kind of consent: it touches the artifact the team ships, it will appear in their diffs and
their blame, and it changes nothing about behaviour. Folding it into adoption would smuggle a code
change into a documentation exercise.

## Why doc-led work never needs this practice

A doc-first build gets annotation **for free, and correctly, without anyone deciding to do it**. The
contract and its ID exist before the code does, and the slice that realizes the contract records its
binding as it is written — so the developer is already holding the ID at the moment the code site
comes into being. The tag is a keystroke, and it lands at exactly the right line by construction.

Brownfield inverts every part of that. The code predates the docs entirely, there is no slice to hang
an ID on, and the ID was coined *from* the code rather than the other way round. So the annotation
that a doc-led build accumulates naturally has to be applied deliberately, in one pass, afterwards.
**This practice exists only to close that gap.** A repo that was built doc-first should not need it.

## What it buys

Not, mainly, the ability to re-derive the doc set later — that is a rare event, and a repo with a doc
set does not normally need its contracts recovered from code. The value is in the operations that
**repeat**:

- **Drift detection** locates a contract's site directly instead of inferring it.
- **Change impact** can answer "where does this contract live" without a search whose quality varies
  with whoever is asking.
- **A human or agent reading the code** sees which contract a site realizes, at the site, without
  holding the doc set open beside it.

The last one generalizes the others: an anchor carried *in* the code is the only kind that does not
depend on the competence of the next reader.

## What it costs

- **A diff across much of the repo**, touching files no behaviour change would touch.
- **Consent and review** — someone must approve a change with no functional content.
- **Ongoing upkeep** — a marker can rot like any comment; a moved contract leaves a stale tag.
- **Nothing in conformance.** Annotation is a recommended convention, not a bar. A set without it is
  fully conforming.

## The one rule worth insisting on: complete per kind, or not at all

Annotate a contract *kind* completely, or leave that kind alone. Partial annotation is worse than
none, because a later reader — human or tool — treats the markers as the inventory and stops looking
for what they do not name. Under measurement, an extractor handed a partial marker set found *fewer*
contracts overall than one given no markers at all: it recovered what was tagged and stopped
discovering anything else, losing whole kinds that the untagged run had found unaided
(`LAB-STUDY-ANNOTATION-RECALL`).

So the unit of the decision is the kind, not the contract. If the dependency contracts are not all
going to be marked, mark none of them and let a later pass find them the way it always would.

## Which kinds repay it most

Contracts named after a code artifact — an entity after its class, a dependency after its package —
are re-derivable from the code by anyone, so a marker on them buys location and granularity but little
identity. Contracts that are **rules, decisions, policies or intent** have no name in the code at all,
and nothing recovers them: an invariant, a decision record, a cross-cutting pattern, a security
assertion. Those are where the marker is the only thing standing between the contract and a fresh
invented name.

Some contracts have **no code site whatsoever** — a persona, a success criterion, an assertion that
something is *absent*. There is nothing to annotate, and a marker manufactured near a topically
related line is worse than the gap it hides.

## What four validation rounds showed about writing the rule down

The completeness rule is the hard part to state, and it fails in **both** directions if written loosely.
Written with no exemptions it forbids annotating the kind that most repays it, because one member of an
otherwise markable kind has no code site. Written with exemptions it hollows out: a kind marked at one
site of eight still reads as "complete" once each of the other seven carries an excuse, which rebuilds
the inventory illusion the rule exists to prevent. Both were observed, in the same round, on two repos.

What holds is narrower than either: exemptions explain a gap and never close it, and the marked-over-total
ratio is reported per kind regardless of how well each absence is excused.

Two further lessons from the same rounds. **A binding-map locator is a starting point, not a site** —
taken verbatim it stacks markers on one coarse line and can cost a whole kind. And **an instruction that
asserts a fact about the target repo will eventually be wrong**: measured baselines, line endings and
comment carriers all have to be established by the pass, not supplied to it.

## Sequencing

Adopt (Part 10f) → close the interview's open markers → **then** annotate, with consent → then the
lifecycle tools run sharper. Annotating before the doc set has settled means re-tagging when IDs move.
