# dictum-lab

**The research companion to the [Dictum](https://github.com/pnjacket/dictum) documentation standard — reference tooling, trial protocols, studies, and a conformance fixture corpus.**

> **Non-normative.** Nothing in this repository defines conformance to Dictum.
> The standard's text — `STANDARD.md` and the concern specifications in the
> canonical repository, under its signed releases — is the only normative
> artifact. The tools here *check* the standard; the studies here *test* it;
> where a tool and the text disagree, the text wins and the tool has a bug.

## Why a separate repository

A standard earns authority by being independent of any implementation. Keeping
executable tooling and empirical work out of the standard's repository keeps
the text the sole source of conformance (no "what the validator accepts"
drift), lets tools iterate fast without touching the standard's solemn,
signed release cadence, and gives real-world trial evidence a citable home.
Findings flow back into the standard only as distilled rules — failure-mode
entries and bar changes — through its normal versioned-release process.

## What's here

| Path | What |
|---|---|
| [`tools/gate-check/`](tools/gate-check) | **`dictum-gate-check`** — a deterministic, zero-dependency (Python 3 stdlib) checker for the mechanically-decidable slice of Dictum's gates: publish state, scope partition, ID-web resolution, binding-map validation, marker vocabulary. Exit-code-gated for CI. |
| [`tools/code-map/`](tools/code-map) | **`dictum-code-map`** — the shared deterministic code-mapping backend: in-code `DICT:` annotations, OpenAPI/JSON-Schema interface artifacts, env-key surface (heuristic tier) → one normalized JSON inventory. |
| [`tools/drift-check/`](tools/drift-check) | **`dictum-drift-check`** — the model-B drift detector (STANDARD Part 10d): binding-stale, code-ahead/doc-ahead, route/schema drift against build-emitted artifacts, coverage arithmetic. Tiered findings (certain vs heuristic); declines loudly where drift is not decidable. |
| [`tools/reverse-extract/`](tools/reverse-extract) | **`dictum-reverse-extract`** — deterministic reverse-extraction (Part 10f): a DRAFT candidate inventory (recovered vs coined IDs), a DRAFT binding map, and a recoverability report of what model B cannot recover. |
| [`tools/tracker-sync/`](tools/tracker-sync) | **`dictum-tracker-sync`** — the doc→tracker execution mirror (Part 10c): projects the derived backlog + build-status into a tracker and reconciles repo-wins. Adapters: `file` (mock, used by tests) and `github` (`gh` CLI). |
| [`tools/common/`](tools/common) | `dictumlib.py` — the shared parsing module (YAML subset, front matter, ID grammar, owned-ID web) the newer tools import; gate-check keeps its own inline copy by design. |
| [`fixtures/`](fixtures) | Synthetic fixtures — conforming and deliberately broken — that regression-test the tooling without touching any real product. Each pins the standard version it targets; broken ones encode exactly one defect, named by directory; boundary probes assert that tools *decline* rather than guess. Top-level dirs belong to gate-check; per-tool corpora live under `fixtures/<tool>/`. |
| [`studies/`](studies) | Trial write-ups. Products are described **by shape** (traits, scale, build history), never by name. |
| [`PROTOCOL.md`](PROTOCOL.md) | How trials are run, so the method behind the evidence is reproducible. |
| [`tests/run.sh`](tests/run.sh) | Runs every tool across the fixture corpus and asserts expected findings, loud declines, and byte-identical re-runs. |

## Quickstart

```sh
# check a Dictum-documented repo (vendored standard expected at <repo>/dictum/)
python3 tools/gate-check/dictum-gate-check.py <repo-root>

# model-B drift check (doc set + code in one repo)
python3 tools/drift-check/dictum-drift-check.py <repo-root>

# reverse-extract a bare repo into DRAFT doc-set raw material
python3 tools/reverse-extract/dictum-reverse-extract.py <repo-root> --out /tmp/drafts

# project the repo's execution items into its declared tracker (dry-run)
python3 tools/tracker-sync/dictum-tracker-sync.py <repo-root>

# run the fixture corpus
tests/run.sh
```

The newer tools are **research instruments**: each answers "what can a
deterministic (model-B) tool decide with certainty, and where does certainty
end" for its slice of the standard — see
[`studies/2026-07-model-b-tooling.md`](studies/2026-07-model-b-tooling.md)
for the boundary map. Certain and heuristic signals are never mixed in one
finding class, and declining loudly is a designed success result.

## License

Everything in this repository is **MIT** (see [`LICENSE`](LICENSE)). The
standard itself is licensed separately in its own repository.
