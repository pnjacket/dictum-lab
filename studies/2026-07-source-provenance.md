---
artifact: research-companion
role: study
anchor: LAB-STUDY-SOURCE-PROVENANCE
non_normative: true
---

# Study: the source-provenance determinism boundary (2026-07)

**Question.** Dictum's `source-provenance` sub-aspect (Governance 11.8;
failure-mode #36) requires that every non-trivial first-party code unit copied
or adapted from elsewhere be attested `{origin, license, outbound-compat}` at
the code site, and makes copied-under-an-incompatible-license a defect. The
research question this study answers: **what can a deterministic (model-B) tool
decide with certainty about a code tree's provenance, and where exactly does
certainty end?** The tool `tools/provenance-check` is the executable evidence;
the boundary map below is the finding.

**Status: first cut, fixture-validated only.** Ground truth is the synthetic
fixture corpus (`fixtures/provenance-check/` — invented product shapes, one
case per fixture, plus a boundary probe for the undecidable side). This has
**not** been ground-truthed against real pinned repo states per
[`PROTOCOL.md`](../PROTOCOL.md); no recall/precision numbers are claimed. The
design posture throughout: **a small provably-sound check surface over broad
heuristics; where the tool cannot decide, it declines loudly, and declining is
a success result** (encoded in the output and asserted by tests).

## Method

1. Read the normative definition (STANDARD Governance 11.8 `source-provenance`;
   failure-mode #36; the `SOURCE: <origin> <license>` marker as a
   machine-extraction extension point, host-language comment leader like
   `DICT:`).
2. Partition the required behavior into: **decidable** (and under what
   precondition), **undecidable-in-principle** for a deterministic tool, and
   **undecided-yet** (would become decidable with more work but is not today).
3. Implement only the decidable class exactly; expose every precondition in the
   output; cap any heuristic at WARN so it can never drive a CI exit code.
4. Build fixtures that probe **both sides** of the boundary — cases just inside
   (must be detected exactly once) and just outside (the tool must decline, not
   guess) — and assert byte-identical re-runs (determinism as a testable
   property) in `tests/run.sh`.

## The boundary map

| Surface | Verdict | Precondition / note |
|---|---|---|
| A `SOURCE:` marker's declared license vs the product outbound | **decidable** | The marker rides a host-language comment leader; the license is the last token. Parsing and attribution are exact. |
| Marker present but license missing/unparseable | **decidable (declines)** | No license → compatibility is undecidable → `malformed-marker` WARN, never a guess. |
| Exact SPDX one-way incompatibilities (e.g. Apache-2.0 into GPL-2.0-only) | **undecided-yet** | The current table is a coarse permissiveness rank; correct for the common permissive-outbound case, not for every SPDX pairing. Refinement is future work. |
| **Undeclared** copying — licensed source reproduced with **no marker** | **undecidable-in-principle** | The source corpus is unbounded; no deterministic scan can establish it. The tool does not pretend to; a fingerprint scan is offered at WARN only and is non-authoritative. |

## The decidable core (where certainty lives)

Given a `SOURCE: <origin> <license>` marker, the tool parses `{origin, license}`
exactly and checks the license against the declared outbound via a stated
compatibility table (permissiveness rank; non-free is never includable;
`unknown` needs a human). A declared license more restrictive than the outbound
is a **sound ERROR** — for the default MIT outbound this is exact: it accepts
permissive licenses (MIT/BSD/Apache-2.0/ISC/public-domain, `unknown` as a WARN)
and rejects copyleft and non-redistributable/proprietary. The defect is
**relative to the declared outbound**: the same GPL marker that fails under an
MIT outbound is clean under a GPL outbound. This is the tool's real job and it
is provably sound over the parse.

## Where certainty ends (the honest limit)

The dominant real-world risk — an LLM or a person reproducing licensed source
with **no attestation** — is **undecidable in principle** for a deterministic
tool. There is no bounded oracle of "all source that could have been copied".
The tool therefore:

- **Never flags an unmarked unit as a defect.** The `unmarked` fixture (a
  copied-looking, well-known algorithm with no marker) is reported `0/0`. That
  is the correct result, not a miss to be fixed by loosening the bar.
- **Never clears the undeclared side.** A green run does not certify that no
  unmarked copy exists. Unmarked copies are the **residual the standard
  records** (failure-mode #36 acknowledges the gap); the tool's silence is not
  absolution.
- **Offers at most a WARN.** An optional, configurable fingerprint scan (a small
  list of tell-tale phrases a copier may leave) can raise a non-authoritative
  `unmarked-copy-heuristic` WARN. It can hint, never conclude, and it never
  affects the exit code.

## Finding

The provenance check cleanly separates a **sound, exact** decidable core (the
declared side: marker → license → outbound compatibility) from an
**undecidable** residual (the undeclared side). The standard's value here is
the *attestation discipline* — the `SOURCE:` marker makes the decidable side
exist at all; without markers there is nothing sound to check. The tool's
honesty is to decide the declared side exactly and to decline the undeclared
side loudly rather than manufacture false confidence. Describe-by-shape holds
throughout: every fixture origin is invented (`acme-mathlib`), and no real
product, company, or domain appears.
