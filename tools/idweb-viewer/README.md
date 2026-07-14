# dictum-idweb-viewer

Render a Dictum doc set's **owned-ID web** as an interactive graph, and surface
its mechanically-decidable issues — in the browser, fully offline.

**Non-normative.** The standard's text (STANDARD.md + `concerns/` in the
canonical Dictum repository) is the only definition of conformance; where this
tool disagrees with the text, the text wins and this tool has a bug.

## Why a viewer can exist at all

Dictum never stores the ID web (STANDARD Part 0.5: the reference graph is
always *derived*, never a file). What makes derivation mechanical is the
standard's two machine-extraction extension points plus its machine-readable
siblings:

- **register lines** (Part 5) locate every owned ID's one defining line;
- the **pinned ID token grammar** (Part 5) says what counts as an ID;
- `manifest.yaml` carries scope + tombstones; `bindings.yaml` carries the
  contract→code index.

This tool re-derives the web from those on every load — it reads, never writes.

## Use

Open [`dictum-idweb-viewer.html`](dictum-idweb-viewer.html) in a browser
(`file://` works — no server, no network; nothing leaves the page) and open or
drag-and-drop a doc-set folder: the repo root holding `manifest.yaml` /
`docs/` / `bindings.yaml`. You get:

- **The graph** — contracts as nodes (colored by kind class, labeled by ID;
  `CAP` hexagons, `INV` diamonds), references as arrows, binding-map edges
  into code files, tombstones and dangling references visually distinct.
  Layouts: layered (dagre), organic, concentric. Filter by kind, group by
  doc, search by ID.
- **Findings** — the same idweb + bindings checks `gate-check` runs, ported:
  dangling references (ERROR), binding keys with no register-form definition
  (ERROR), missing locator paths (ERROR), inline-mint binding keys, arm
  tokens, unticked ID-like tokens, retired-contract mentions (WARN), plus an
  informational orphan list. Click a finding to jump to the node.

## CLI (same engine, no browser)

```
node idweb.js <repo-root>
```

prints the findings and a `N error(s), M warning(s) — …` tail, exit 1 on
errors — the mode `tests/run.sh` exercises against the fixture corpus.

## Grammar sync (load-bearing)

The ID grammar and register-form definition grammar live in **three places**:
`tools/common/dictumlib.py`, gate-check's inline copy, and [`idweb.js`](idweb.js)
here. A change must land in all three; `tests/run.sh` cross-checks them on the
fixtures. Detection scans looser than the normative grammar (STANDARD Part 5)
on purpose — near-misses are flagged, never minted.

## Files & licensing

| File | Role |
|---|---|
| `dictum-idweb-viewer.html` | The viewer (open this) |
| `idweb.js` | The engine: YAML-subset + front-matter + register-form parsing, resolution, findings, graph derivation. Browser global + Node CLI |
| `vendor/` | Vendored MIT libraries (Cytoscape.js, dagre, cytoscape-dagre) + their license texts — see [`vendor/NOTICES.md`](vendor/NOTICES.md) |

Tool code is MIT like the rest of dictum-lab; the vendored libraries are MIT
with notices retained (see `vendor/NOTICES.md`).
