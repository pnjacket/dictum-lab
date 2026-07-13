# Trial protocol

How dictum-lab runs real-world trials of the Dictum standard and its tooling,
so the evidence in `studies/` is reproducible in method even where the
subject repos are private.

## Subjects

Trials run against real, working repositories documented to the standard —
greenfield doc-first builds, brownfield reverse-authored baselines, and doc
sets carried through enhancement deltas. In published write-ups, subjects are
described **by shape** (traits, scale, stack family, build history), never by
name.

## Ground-truthing (the core discipline)

A tooling trial needs a defect oracle. The strongest one available is a
**pinned-state comparison**:

1. An independent audit (human or LLM, following the standard's
   `doc-maturity-auditor` procedure) establishes findings against a doc set at
   a **pinned git state**, each finding with file/line evidence.
2. The findings are fixed, producing a second pinned state; every fix is
   evidence-grounded (code locators, ledger provenance), never invented.
3. The tool under trial runs against **both states**. Recall is measured
   against the audit's findings on the pre-fix state; precision against the
   near-clean post-fix state. Divergences are adjudicated one by one:
   tool false positive, tool false negative, audit miss (the tool found a real
   defect the audit didn't), or **convention gap** (the doc set does something
   the standard under-specifies — these are findings *about the standard* and
   feed its failure-mode catalog or roadmap).

## Hermeticity

Validation builds are hermetic to their own doc sets: the builder consumes
only the product's docs plus the vendored standard, never external context.
Deviations (operator interventions) are logged in the trial record.

## Reporting

Each study states: the standard version(s) involved, the subject shapes, the
method, the raw counts (before/after, per check), every false-positive and
false-negative class discovered (named, with the mitigation chosen), and what
was folded back into the standard vs. left open. Negative results are
reported with the same prominence as positive ones.
