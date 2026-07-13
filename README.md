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
| [`fixtures/`](fixtures) | Synthetic doc-set fixtures — conforming and deliberately broken — that regression-test the tooling without touching any real product. Each pins the standard version it targets. Seed of a future conformance test suite. |
| [`studies/`](studies) | Trial write-ups. Products are described **by shape** (traits, scale, build history), never by name. |
| [`PROTOCOL.md`](PROTOCOL.md) | How trials are run, so the method behind the evidence is reproducible. |
| [`tests/run.sh`](tests/run.sh) | Runs the checker across the fixture corpus and asserts expected findings. |

## Quickstart

```sh
# check a Dictum-documented repo (vendored standard expected at <repo>/dictum/)
python3 tools/gate-check/dictum-gate-check.py <repo-root>

# run the fixture corpus
tests/run.sh
```

## License

Everything in this repository is **MIT** (see [`LICENSE`](LICENSE)). The
standard itself is licensed separately in its own repository.
