# tools/common

`dictumlib.py` — the shared, zero-dependency (Python 3 stdlib) parsing module
the newer tools (`code-map`, `drift-check`, `reverse-extract`, `tracker-sync`)
import: the plain YAML-subset parser, front-matter reading, doc-set discovery,
the Part 5 ID grammar/registry, and the register-form owned-ID web (`IdWeb`).

Tools import it relative to their own location
(`sys.path.insert(0, …/../common)`), so each remains runnable as
`python3 tools/<tool>/<script>.py …` from any working directory.

**`gate-check` deliberately does not import it** — it ships as a single file
and keeps its own inline copy of the same code (that copy is where the
grammar was originally calibrated). When the YAML subset, the front-matter
handling, or the ID/definition grammar changes, change **both** and re-run
`tests/run.sh`.

Non-normative, like everything in this repo: the standard's text is the only
definition of conformance; a disagreement between this module and the text is
a bug here.
