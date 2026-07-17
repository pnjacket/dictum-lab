# dictum-editorial-lint

A deterministic, zero-dependency linter that checks the **Dictum standard
repo's own prose** against its [Editorial Charter](../../../dictum/EDITORIAL.md)
(Part 6 / Appendix B). It implements only the *mechanically checkable* subset;
tier-placement and "rule + one-line why" judgement stay with the human gate.

> **Non-normative.** The standard's text (and its charter) is the only
> definition of conformance. A disagreement between this tool and the charter
> is a bug **here**, not there. Per the charter's Part 2, the standard never
> depends on the lab, so this linter lives here and runs *on* the standard repo.

## Usage

```
python3 dictum-editorial-lint.py <path-to-dictum-repo>
```

Prints one finding per line, then a tail line that starts with the error count:

```
ERROR [standard-lab-link] concerns/11.4-interfaces.md:14  ](../dictum-lab/…)
WARN [research-prose] STANDARD.md:30  “in practice”
1 error(s), 1 warning(s)
```

Findings are sorted by file then line, so output is byte-identical across runs.
**Exit code is 1 iff there is at least one ERROR.** WARN findings are advisory
heuristics and never drive the exit code.

## Checks

| Check | Severity | Scope | What it flags |
|---|---|---|---|
| `standard-lab-link` | ERROR | `STANDARD.md`, `GLOSSARY.md`, `concerns/*.md` | A markdown link whose target references the lab (`](…dictum-lab…)`). A bare prose mention of "the lab" is allowed (non-normative pointers, Part 2) — only an actual link target is an error. |
| `forbidden-name` | ERROR | all `*.md` | A denylisted term appears (case-insensitive substring, per line). Enforces describe-by-shape (Part 3). |
| `research-prose` | WARN | `STANDARD.md`, `concerns/*.md` | War-story / research-process phrases (`in practice`, `surfaced building/when/as`, `a validation build`, `(round N)`, `round-N`, `the v0.x`, `verified in practice`, `422'd`). Excludes `failure-mode-catalog.md` (holds war-stories by design) and `EDITORIAL.md` (quotes the phrases as examples). |
| `migrated-section` | WARN | `concerns/*.md` | A `## Worked Example` or `## Design Decisions` heading — those sections migrated to the lab (Appendix A); their reappearance is a regression. |

## The denylist (committed mechanism, uncommitted list)

The forbidden-name list is **never committed here** — hard-coding a real
forbidden term would itself violate Part 3. The tool reads a denylist file
(one term per line; `#` comments and blank lines ignored) from, in order:

1. the `DICTUM_EDITORIAL_DENYLIST` environment variable, else
2. `<target-repo>/.editorial-denylist`.

If neither exists it prints one informational line and skips the check (this is
**not** an error):

```
note: no denylist found (set DICTUM_EDITORIAL_DENYLIST); forbidden-name check skipped
```

## Fixtures & tests

Fixtures live in [`../../fixtures/editorial-lint/`](../../fixtures/editorial-lint/)
— tiny fake dictum-repo-shaped trees, one defect each (`clean`,
`standard-lab-link`, `research-prose`, `forbidden-name`). The
`forbidden-name` fixture commits a denylist holding a single **invented, safe**
term. Run the suite with `bash ../../tests/run.sh` (see its `== editorial-lint ==`
section).
