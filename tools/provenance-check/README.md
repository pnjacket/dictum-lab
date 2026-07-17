# dictum-provenance-check

A deterministic, zero-dependency, **best-effort** checker for the Dictum
**source-provenance** sub-aspect (Governance 11.8; failure-mode #36). Every
non-trivial first-party code unit copied/ported/adapted from elsewhere must be
attested `{origin, license, outbound-compat}` at the code site with a `SOURCE:`
marker; a copy under a license incompatible with the product's outbound license
is a **defect**. This tool decides that.

> **Non-normative.** The standard's text is the only definition of conformance.
> A disagreement between this tool and the text is a bug **here**, not there.
> The standard never depends on the lab, so this checker lives here and runs
> *on* a product's source tree.

## Usage

```
python3 dictum-provenance-check.py <target-src-dir> [--outbound <SPDX>] [--fingerprints <file>]
```

- `--outbound` — the product's outbound license (default `MIT`).
- `--fingerprints` — path to a fingerprint phrase list (one per line, `#`
  comments); overrides the built-in default list. Also settable via the
  `DICTUM_PROVENANCE_FINGERPRINTS` env var.

Prints one finding per line, then a tail line that starts with the error count:

```
ERROR [incompatible-license] src/solver.c:3  `GPL-3.0-only` (strong-copyleft) from `acme-mathlib` incompatible with `MIT` outbound — …
WARN [malformed-marker] src/hash.js:3  SOURCE: marker with no parseable license: // SOURCE: acme-mathlib
1 error(s), 1 warning(s)
```

Findings are sorted by file then line, so output is byte-identical across runs.
**Exit code is 1 iff there is at least one ERROR.** WARN findings are advisory
and never drive the exit code.

## The marker (machine-extraction extension point)

The code-site attestation is the marker token `SOURCE: <origin> <license>` in a
host-language comment — the leader is the host language's own, exactly like
`DICT:`:

```
// SOURCE: acme-mathlib GPL-2.0-or-later
#  SOURCE: https://example.invalid/widget-cookbook MIT
;  SOURCE: acme-mathlib BSD-3-Clause      (Clojure)
```

`<origin>` is one whitespace-free token (a URL or a short name). `<license>` is
the **last** whitespace-separated token: an SPDX id, or `proprietary` /
`non-redistributable` / `unknown`. A `SOURCE:` that is not on a comment leader
(prose, a string literal) is **not** a marker and is never flagged.

## Checks

| Check | Severity | What it flags |
|---|---|---|
| `incompatible-license` | ERROR | A parsed `SOURCE:` whose declared license is incompatible with `--outbound` (strong/weak/network copyleft, or non-free, into a more-permissive product). Also emits a WARN in this check for an `unknown`/unrecognized license (needs human determination) and for an outbound not on the table. |
| `malformed-marker` | WARN | A `SOURCE:` on a comment leader with no parseable license token (origin only, or bare). Compatibility is undecidable without a license, so the tool declines rather than guesses. |
| `unmarked-copy-heuristic` | WARN | A configured fingerprint phrase appears in the source. **Non-authoritative, WARN-only, never exit-driving.** See the boundary section — this cannot establish copying and a clean scan clears nothing. |

## Outbound compatibility table

Licenses are mapped to a permissiveness **rank**; a source of rank *r* may be
included in an outbound of rank *R* iff *r ≤ R* (more-permissive code can go
into a more-restrictive product). Two categories sit outside the rank.

| Category | Examples | Rank |
|---|---|---|
| permissive | MIT, BSD-2/3-Clause, Apache-2.0, ISC, 0BSD, Zlib, Unlicense, CC0-1.0, public-domain | 0 |
| weak-copyleft | LGPL-\*, MPL-\*, EPL-\* | 1 |
| strong-copyleft | GPL-\* | 2 |
| network-copyleft | AGPL-\* | 3 |
| non-free | `proprietary`, `non-redistributable`, commercial | — (never includable → ERROR) |
| unknown | `unknown`, unrecognized token | — (needs a human → WARN) |

For the default **`--outbound MIT`** (rank 0) this reproduces the intended
table exactly: **accepts** MIT / BSD / Apache-2.0 / ISC / public-domain (and
`unknown` as a WARN); **rejects** GPL-\* / AGPL-\* / `non-redistributable` /
`proprietary`. The rank model is deliberately coarse: it does not encode
specific one-way SPDX incompatibilities (e.g. Apache-2.0 into GPL-2.0-only).
That refinement is future work, noted in the study.

## What this can and cannot decide

This is the load-bearing honesty of the tool.

- **Declared copying is decidable.** Parsing a `SOURCE:` marker and attributing
  its `{origin, license}` is exact; checking that license against the declared
  outbound is a mechanical table lookup. A declared-incompatible marker is a
  sound ERROR. This is the tool's real job.

- **Undeclared copying is undecidable.** An LLM (or a person) reproducing
  licensed source with **no marker** cannot be detected reliably — the source
  corpus is unbounded. The tool does **not** pretend to. The `unmarked` fixture
  is a boundary probe: a copied-looking unit with no marker is reported `0/0`,
  i.e. **not flagged**. That is the correct result.

- **A clean run clears nothing on the undeclared side.** Unmarked copies are
  the **residual the standard records** (failure-mode #36 acknowledges the gap);
  they are never certified absent by a green run here. The optional fingerprint
  scan is a courtesy signal at WARN only — it can hint, never conclude, and it
  never affects the exit code.

## Fixtures & tests

Fixtures live in [`../../fixtures/provenance-check/`](../../fixtures/provenance-check/)
— tiny synthetic MIT-outbound products, one case each: `clean` (compatible
declared license → 0/0), `incompatible-declared` (a GPL marker in an MIT
product → 1 error), `malformed-marker` (a `SOURCE:` with no license → 1 warn),
and `unmarked` (the undecidable honest miss → 0/0). All origins are invented
(`acme-mathlib`). Run the suite with `bash ../../tests/run.sh` (see its
`== provenance-check ==` section), which also asserts the `--outbound` behavior,
the WARN-only fingerprint path, and byte-identical re-runs.
