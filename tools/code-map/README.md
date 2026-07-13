# dictum-code-map

The **deterministic code-mapping backend** shared by `dictum-drift-check`
(model-B drift detection, STANDARD Part 10d) and `dictum-reverse-extract`
(deterministic reverse-extraction, Part 10f) — the "one code-mapping backend"
the standard's roadmap notes those two flows could share. Zero-dependency
(Python 3 stdlib only). It scans a product repo and emits a normalized JSON
inventory; it checks nothing itself.

It is a **research instrument, not a product**: the question it answers is
*what can a deterministic pass extract from a repo with certainty, and where
exactly does certainty end*. Each output section carries an explicit tier in
the `tiers` block — `certain` (with its stated precondition) or `heuristic` —
and where the tool cannot decide it **declines loudly** (e.g.
`unparsed_annotations`) instead of guessing. Downstream tools must never let
a heuristic section drive a hard finding.

```sh
python3 dictum-code-map.py <repo-root>            # JSON to stdout
python3 dictum-code-map.py <repo-root> --out map.json
```

Exit code `0` on success, `2` on usage error. (There is no findings exit —
this is an inventory, not a checker.)

**Non-normative:** the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.

**Status: experimental.** Validated on the synthetic fixture corpus only
(`fixtures/code-map/`), not yet ground-truthed against real pinned repo
states per [`PROTOCOL.md`](../../PROTOCOL.md).

## What it extracts

| Section | What | Confidence |
|---|---|---|
| `annotations` | In-code contract-ID annotations — `// DICT: <ID>` and the common comment leaders: `//`, `#`, `/* */`, `<!-- -->`, `--`, `*` (continuation lines) — across Go/TS/JS/Python/Rust/C#/Java/Ruby/shell/HTML/SQL/YAML. IDs must match the standard's Part 5 grammar; several IDs per annotation may be comma-separated. `registered_prefix` marks whether the prefix is in the Part 5 registry (informational — off-registry local prefixes are legal, Part 5). | deterministic |
| `unparsed_annotations` | Lines that say `DICT:` but parse to no valid ID — an unsupported comment leader (e.g. Lisp `;;`) or a non-grammar ID. Surfaced, never silently dropped, so a mis-written annotation is visible downstream. | deterministic |
| `interfaces.openapi` | OpenAPI documents (JSON, or YAML **in the plain YAML subset** the lab's parser reads — anchors/multi-line scalars are not supported) → endpoint inventory (`method`, `path`, `operation_id`) + `components.schemas` / `definitions` (`name`, `fields`, `required`). | deterministic over the artifact |
| `interfaces.json_schema` | JSON Schema files (`$schema` key or `*.schema.json`) → `name` (title or filename), `fields`, `required`. | deterministic over the artifact |
| `config_keys` | Referenced env-var names via common patterns (`os.environ`/`os.getenv`, `process.env`, `os.Getenv`/`LookupEnv`, `env::var`, `Environment.GetEnvironmentVariable`, `System.getenv`). **Marked `heuristic: true` in the output** — regex-grade, no evaluation; shell `$VAR` expansion is deliberately not covered (too noisy). | heuristic |

Skipped: `.git`, dependency/build/output dirs (`node_modules`, `vendor`,
`target`, `dist`, `build`, …), files over 1 MB, and Markdown (a Dictum doc
set living in the same repo must not read as code annotations).

## Output shape (`schema_version: 1`)

```json
{
  "tool": "dictum-code-map", "schema_version": 1, "root": "/abs/path",
  "annotations": [ {"id": "API-LIST-NOTES", "file": "src/server.go", "line": 4,
                    "registered_prefix": true} ],
  "unparsed_annotations": [ {"file": "src/core.clj", "line": 2, "text": ";; DICT: CAP-NOTES"} ],
  "interfaces": {
    "openapi": [ {"source": "openapi.yaml",
                  "endpoints": [{"method": "GET", "path": "/notes", "operation_id": "listNotes"}],
                  "schemas":   [{"name": "Note", "fields": ["body","id","title"], "required": ["id","title"]}]} ],
    "json_schema": [ {"source": "schemas/note.schema.json", "name": "Note",
                      "fields": ["body","id","title"], "required": ["id"]} ]
  },
  "config_keys": {"heuristic": true,
                  "keys": [ {"name": "NOTES_ADDR", "file": "src/server.go", "line": 9,
                             "pattern": "os.Getenv"} ]},
  "stats": {"files_scanned": 5}
}
```

All lists are sorted; two runs over the same tree produce byte-identical
output.

## Deliberately out of scope (first cut)

**No per-stack AST parsing.** Route tables, handler signatures, ORM models
etc. are *not* parsed out of source code — only committed/build-emitted
machine-readable artifacts (OpenAPI, JSON Schema) and explicit annotations
are read. That is the roadmap's "comparison against build-emitted
OpenAPI/JSON-schema" path. Per-stack extractors can be added later as new
families under `interfaces` (e.g. `"go-http"`, `"ts-routes"`) emitting the
same endpoint/schema shapes, without changing consumers.
