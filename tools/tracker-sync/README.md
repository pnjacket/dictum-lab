# dictum-tracker-sync

The **doc→tracker sync adapter** for the standard's doc↔tracker boundary
(STANDARD Part 10c; the tracker-binding declaration owned by Delivery
Process 11.6). Zero-dependency (Python 3 stdlib only; the `github` adapter
shells out to the `gh` CLI).

The tracker is a **downstream mirror of what the repo owns**. Each run the
tool reads the product's tracker-binding declaration, the build-status
record, and the doc set; **derives** the projection of execution items
(never stored — Part 0.5); diffs it against tracker state; and reconciles
**repo-wins**. Dry-run by default; `--apply` executes.

```sh
python3 dictum-tracker-sync.py <repo-root>           # dry-run: print the plan
python3 dictum-tracker-sync.py <repo-root> --apply   # execute against the tracker
```

Exit code: `0` in sync · `1` actions needed or build-gate violations ·
`2` usage/parse error — including a missing declaration or build-status
record, which is **declined loudly** (nothing decidable to project), never
guessed.

**Non-normative:** the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.
The machine-readable `tracker-binding.yaml` format below is a **tool
convention** implementing the declaration 11.6 defines — the standard pins
the boundary semantics (channel, three roles, two gates), not a file format.

**Status: experimental.** Validated on the synthetic fixture corpus only
(`fixtures/tracker-sync/`), not yet trialed against a real tracker per
[`PROTOCOL.md`](../../PROTOCOL.md).

## Boundary invariants, enforced by construction

- **Downstream mirror:** the tool never writes doc-set files — the tracker is
  the only mutation target, and only under `--apply`.
- **No stored back-reference:** the repo stores no tracker item ID/URL
  (Part 0.5). The join is the stable contract ID + slice ordinal, carried on
  the item as labels (`dict:<ID>`, `dict-slice:<n>`, `dict-role:execution` —
  prefixes configurable in the declaration's `channel`), resolved at
  projection time each run.
- **Three item roles:** only items carrying the execution role label are
  mirrored/reconciled. Demand and triage items are **never touched** (they
  are the tracker's own upstream content; triage stays repo-invisible until
  reproduced — Part 10c).
- **Build gate:** an execution item is projected only from resolving,
  Contract-grade contract IDs; a slice row violating that is reported as a
  `GATE` finding and not projected.
- **Write gate:** trivially honored — the tool writes no repo files at all.

## What gets projected

1. One execution item per **build-status slice row** (the standard's
   build-status template, `## Slices` table): title `Slice <n>: <name>`,
   labels from the Realizes column, state `closed` when the Verified column
   records a stage (`merge`/`release`), else `open`.
2. One `Build: <ID>` item per **derived build-new contract** (Part 10e):
   in-scope, Contract-grade, code-realizable, unbound in `bindings.yaml`,
   and not realized by any slice row.

Reconciliation (repo-wins): missing projected item → CREATE; divergent
title/state/labels → UPDATE; a tracker *execution* item matching no
projection → CLOSE (it did not derive from the repo).

## Declaration file (tool convention)

The standard deliberately pins only the declaration's *semantics* (the 11.6
tracker-binding declaration: mirror invariant, item roles, gates), never a
file shape — how execution items are tracked does not matter as long as they
are tracked, so binding a shape would privilege one tracker workflow over
others. The shape below is this example's suggestion; any tool that reads
the same semantics conforms just as well.

```yaml
# tracker-binding.yaml (repo root or docs/)
tracker_binding:
  adapter: file                    # file | github
  file: { path: tracker.json }     # file adapter: the JSON mock tracker
  github: { repo: owner/name }     # github adapter: gh CLI; requires `gh auth login`
  build_status: IMPLEMENTATION.md  # the build-status record to project from
  channel:                         # the ID-carrying channel (defaults shown)
    id_label_prefix: "dict:"
    slice_label_prefix: "dict-slice:"
    role_label_prefix: "dict-role:"
```

Adapters: **`file`** — a JSON-file mock tracker (`{next_key, items:[{key,
title, labels, state, body}]}`); what all tests use. **`github`** — GitHub
Issues via `gh` (list/create/edit/close); requires authentication and
existing labels, is **never invoked in tests**, and passes `gh` errors
through.
