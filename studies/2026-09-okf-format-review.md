---
artifact: research-companion
role: study
anchor: LAB-STUDY-OKF-FORMAT-REVIEW
non_normative: true
---

# Study: OKF as Dictum's base document format? (2026-09)

**Question.** Can Google's Open Knowledge Format (OKF) v0.2 become the base document format for Dictum v1.2.0 doc sets, what would it cost in tokens and migration, and what would the move actually buy?

**Verdict.** No. OKF is a container for agent-consumed knowledge; Dictum is a method for build-ready software specification. Full conformance is a MAJOR that changes the core model and adds a permanent fixed cost to every editorial session, for an interoperability that a one-way export delivers at zero ongoing cost. Three OKF ideas are worth taking as Dictum's own optional rules. Nothing here is normative; the standard's text is the only definition of conformance.

Two assumptions govern the analysis. Both were set by the standard's maintainer.

- Full conformance. Partial adoption is not an option, because every OKF feature Dictum declines becomes an exception rule the model holds and fights on every turn.
- Fixed context cost. Editorial guidance is loaded at the start of a job and stays in the window for the whole job, so adopted standard text is paid on every turn of every session for the life of every downstream product, not once at migration.

Baselines:

- Dictum v1.2.0: the signed tag at commit `48040ba`, read from a detached checkout. The branch head was one editorial commit ahead and was not used.
- OKF v0.2: SPEC.md at commit `ad30107` (2026-08-21). The repo has no tags or releases; the spec's own version line is the only release marker.

## Method and ground truth

Per [`PROTOCOL.md`](../PROTOCOL.md), every number below is measured, not estimated from memory, and the inputs are pinned:

- **Rule-text sizes** are byte counts of the v1.2.0 files a skill or agent instructs the model to load (STANDARD.md, GLOSSARY.md, the concern specs, a template, the skill or agent file itself), and of OKF's SPEC.md by section. Tokens are approximated at four characters per token throughout; the ratio is stated so a reader can re-derive with a real tokenizer.
- **Session prefixes** are modeled as the sum of the files each tool's procedure names, for four representative sessions (level-up on one concern, a feature delta across two, a greenfield intake, a full audit).
- **Document-text costs** come from a read-only census of six private doc sets from the standard's validation builds and their rebuilds, ranging from a CLI to a real-time multi-user service, described by shape per the lab's rule: docs carrying Dictum front matter, bytes, front-matter bytes, unique IDs, ID references, register lines.
- **Conversion costs** come from a mechanical prototype conversion of the standard's published worked example (`examples/jotdo`) into each candidate OKF shape, with byte and file counts taken from the output.
- **The OKF side** is SPEC.md v0.2, its README, the reference agent's source and prompts, and the four sample bundles it ships, read in full.

What is not measured: the size of the reconciliation text a full adoption would force into Dictum (about 5 KB is a judgment, stated as such), and any per-tokenizer variation.

## 1. Verdict

Do not adopt OKF as the base format. In full it is a MAJOR that changes the core model, adds a permanent 12 to 42% to every editorial session's context after netting out the Dictum text it would replace, and buys interoperability that a one-way export delivers at zero ongoing cost. Keep Dictum as it is, take three OKF ideas as Dictum's own optional rules, and serve OKF consumers through an advisory exporter skill.

- Different layers. OKF is an envelope: frontmatter families, links, index files, a permissive conformance rule. Its own non-goals say it does not replace domain schemas. Dictum's Parts 0 to 5, 9, 10 and 11 are such a schema. Adopting OKF changes the wrapper and nothing about what a doc must say.
- Ten collisions, four of them core. Full adoption meets a Dictum rule in ten places. The Verified rung, layout-independent IDs, no parallel history and the one stored index are core-model changes. Under the versioning policy that is MAJOR with no mechanical repair.
- The trade is lopsided. Of six gains, one needs the migration, and only under a condition that does not hold today. Of fourteen losses, nine re-open a catalogued failure that a real build already paid for once.
- The fixed cost dominates. Net of the Dictum envelope text OKF would replace, the addition is between 5.5K and 10.5K tokens re-read on every turn of every session, forever, on every downstream product. A 40-turn levelup session pays between 221K and 419K tokens of context reads for OKF alone. The sign does not flip, because OKF's envelope text is larger than the Dictum text it displaces.
- The cheap shape is the forbidden one. One OKF concept per Dictum doc with four keys added is Strategy C. It costs +1.3% of doc text, declines four OKF families and overrides three rules. Under full conformance each of those is a standing exception the model fights.
- Recommended: Strategy D. Three OKF ideas as Dictum's own optional rules, plus an advisory exporter skill that derives an OKF bundle on demand. Zero context cost while authoring, zero migration, one MINOR.

## 2. What each standard is

OKF is a container for agent-consumed knowledge. Dictum is a method for build-ready software specification. The two are not the same kind of thing at different breadth. OKF is not built around engineering. Its sample concepts are tables, datasets, metrics and policies. Its reference agent crawls warehouse metadata. Its one substantial v0.2 addition proves a SQL query ran the sanctioned way. It answers "can an agent trust this document it found?" Dictum answers "can an implementer build from this document without asking a question?" A container cannot be extended into a method, and a method does not need a particular container.

The comparison below is the whole picture in one pass. The rows that decide the design are identity, references and the two name collisions. The ledger in the next section takes each of them up.

| | Dictum v1.2.0 | OKF v0.2 |
|---|---|---|
| Purpose | What a build-ready software spec set must contain so an implementer builds without guessing | A universal container for knowledge documents: the metadata, context and curated insight around data and systems |
| Unit | A doc set: manifest, concern docs (or one single-file spec), binding map | A bundle: a directory tree of concepts, one markdown file each |
| Identity | Stable contract IDs (`CAP-###`, `API-###`) minted inline on register lines; layout-independent by design (Part 5) | Concept ID is the file path minus `.md`; layout-bound |
| References | Backticked ID tokens with a pinned grammar; a dangling reference is an error; retirement needs a tombstone | Markdown links; untyped edges; broken links must be tolerated |
| Required frontmatter | `artifact`, `role`, `status`, `version`; concern docs add `concern-id`, `behavior`, `trigger`, `current-rung` | `type` only |
| Lifecycle | `status: draft | published`; publish is gate-bound (strip build markers, flip, bump version) | `status: draft | stable | deprecated`, absent means stable; `stale_after` instant |
| Maturity | Five-rung ladder per concern; sections map to rungs | None |
| Scope | Manifest: traits, in-scope concerns, sub-aspect keys | None |
| Provenance | `[ASSUMPTION]` markers, `code_authorship` trait, manifest `provenance:`, `SOURCE:` in-code marker | `generated {by, at}`, `verified [{by, at}]`, `sources[]` with credibility signals, actor convention |
| Index | README derived from the manifest; the auditor flags drift | `index.md` per directory, generated, no frontmatter |
| History | Git only; parallel copies forbidden (Part 6) | Optional `log.md` per directory |
| Executable checks | `INV-###` with `asserted_by.run` in the binding map; drift-detector; evidence runs | `Attested Computation`: runtime, parameters, executor, receipt, attester |
| Conformance | Gate-based; errors block build-ready | Permissive; a consumer must never reject a bundle |
| Versioning | SemVer calibrated to impact on existing sets; signed tags; MINOR notes must name re-conformance steps | `major.minor`; `okf_version` in root `index.md`; no tags, no signed releases; two breaking renames between v0.1 and v0.2 |
| Domain lean | Software products of any shape | Data catalogs: 22 of 54 sample concepts are BigQuery tables; the reference agent emits `# Schema` and `# Common query patterns` |
| License | Prose CC BY 4.0, tooling MIT | Apache 2.0; Google CLA for contributions |

### Where they agree

- Plain markdown plus YAML frontmatter in git, readable without tooling. Dictum's "markdown-first, tooling never blocks" (Part 10b) and OKF's "no required tooling" are the same stance.
- Humans and agents as co-equal consumers; a draft state; a derived index a tool regenerates.
- Provenance first-class. OKF's actor convention (`human:<id>` vs `<producer>/<version>`) is the machine-readable form of Dictum's interactive-versus-autonomous distinction (Part 0.6, failure-mode #25).
- A pinned format version per set (`authored_against` vs `okf_version`), and `deprecated` carries the same intent as a tombstone.
- Attested Computation is the same idea as an invariant bound to a runnable assertion: executor is the test runner, receipt the evidence artifact, attester the assertion.
- OKF permits arbitrary extension keys and forbids consumers from rejecting them, so every Dictum key survives as-is. Dictum IDs are valid OKF concept-id segments.

## 3. Where they collide: the full-adoption ledger

Under full conformance every OKF rule applies. Each row is where it meets a Dictum rule and what resolving it forces. An "exception rule" is text Dictum would carry, loaded every session, telling the model where OKF does not apply.

| # | OKF rule | Dictum rule it meets | Full adoption forces |
|---|---|---|---|
| 1 | `verified [{by, at}]` is a content sign-off; a `human:` entry makes the doc human-reviewed (5.2, 5.3) | Verified is the fifth rung: built and proven, owned by Delivery; doc maturity is not implementation status (Part 3) | Rename the rung (MAJOR) or a standing disambiguation rule |
| 2 | Absent `status` means `stable` (5.4) | `status` is required and publish is gate-bound (Part 6, failure-mode #30) | Accept a missing key as consumable, or an override |
| 3 | `stale_after` is an instant; consumers warn or refuse past it (5.5, 10.5) | Staleness is a cause-attributed set of change events blocking the release gate (10d) | Two staleness mechanisms that can disagree on one doc |
| 4 | `log.md` records history per directory (9) | History rides on git; no parallel copies (Part 6, Part 0.5) | A maintained log that drifts from git, the failure Part 0.5 exists to prevent |
| 5 | Relationships are markdown links (6.1) | The ID web is backticked tokens on register lines (Part 5) | References become links: +9% to +19% per doc set, measured |
| 6 | Broken links are not malformed; consumers must not reject (6.1, 11) | A dangling reference is an error; retirement needs a tombstone (Part 5, 10d) | The model holds both postures at once |
| 7 | Concept ID is the file path (2) | IDs are layout-independent so merge and split never break a reference (Part 5) | One file per contract with a pinned layout (Strategy B) |
| 8 | `sources[]` with per-claim footnotes keyed to `sources[].id` (5.1) | Provenance via markers, the manifest, and the `SOURCE:` code marker (Parts 5, 6) | Per-claim footnotes across spec prose; OKF's own bundles spend 24% of bytes on frontmatter |
| 9 | Attested Computation carries executor, receipt, attester in frontmatter (10) | `INV-###` binds to `asserted_by.run` in the one permitted stored index (10d) | The same assertion stored twice, the owned-twice smell Part 0.5 forbids |
| 10 | Permissive conformance: never reject a bundle (11) | Gate-based conformance: errors block build-ready (Part 10) | Dictum's gates become a stricter profile the model must know overrides the spec |

Rows 1, 4, 7 and 9 change the core model. Under the RELEASES policy that is MAJOR with no mechanical repair. The other six are exception rules, and exception rules are the fight the full-conformance assumption forbids. Row 7 names Strategy B. It is one of the four adoption shapes read against this ledger later, and the only shape that satisfies that row.

Two further facts about OKF itself bear on any adoption. Its link form is underdetermined. The spec recommends `/bundle-absolute` links, the reference agent's prompt forbids a leading slash because GitHub rendering breaks, and the index generator writes relative links. And it is 0.x, one month old at the analyzed commit, with breaking renames already between minors and no signed releases. Dictum's authenticity model cannot cover it.

## 4. What full adoption would gain and lose

This is the part that decides the matter. Cost can be argued about. What a full adoption gives Dictum and what it takes away cannot. Each gain is tagged with the cheapest way to get it, because a gain that does not need the migration is not a reason for the migration. Each loss is tagged with the failure the catalog ties it to, because that is what adopters would feel.

### What Dictum gains

| Gain | What it is worth | Cheapest way to get it |
|---|---|---|
| Ecosystem membership | A Dictum set readable by anything that speaks OKF (catalog exports, graph viewers, knowledge tools, LLM context loaders) and able to sit beside data-catalog knowledge in one bundle. The only gain that needs the set to *be* OKF, and only if those tools must write, not just read. Today the ecosystem is one reference agent, one viewer, a month-old 0.2 spec. | Migration, if write access is needed. Export, if read access is enough. |
| Per-doc authoring actor | `generated.by` with `human:` versus `producer/version`: the first machine-readable record of whether an operator was present when a doc was written. Makes failure-mode #25 detectable after the fact. | Native rule: one optional front-matter key, one line in Part 6. |
| Keyed per-claim attribution | Footnotes joined to a stable `sources[].id`, chosen because agents reorder lists. Useful for reverse-authored sets where a claim traces to a code site or an interview answer. | Native rule, optional, or nothing. Markers already carry claim-level provenance. |
| Attested computation | A sanctioned computation with typed parameters the agent may fill but never rewrite, an executor that returns a receipt, a deterministic attester that checks what actually ran. OKF's strongest idea. Dictum's Proof column names a test in a cell and nothing attests that it ran against that commit; a receipt-shaped proof for the Verified rung would close that gap. | Native rule in Delivery (11.6) and Quality (11.5). A format-independent idea. |
| Conventional index and `deprecated` | A per-directory index shape and a retired-doc state that other tools recognize. | Export, from the manifest and tombstones. |
| Trust tiers, time-based staleness, source credibility signals | Doc-level trust inferred after the fact; a clock-based stale instant; usage counts and authority per source. | Not wanted. Coarser than markers plus gate-bound publish; weaker than cause-attributed staleness; usage signals are a data-catalog concern with no spec analogue. |

### What Dictum loses

| Loss | What goes | Failure re-opened |
|---|---|---|
| Doc maturity separate from implementation status | OKF's `verified` and its human-reviewed tier read, to every consumer and to the model, as the Verified rung. The Part 3 principle stops being expressible in the front matter. | #13, #30, #35: status claims outrunning evidence |
| Layout-independent identity | Concept ID is the path. Part 8's promise that merge, split and rename never break a reference is gone, and with it single-file packaging and the LEAN tier that lands on it. | #14: dangling references after a move or retirement |
| Sections map to rungs | One file per contract scatters a concern's doc; Part 4's instrument for measuring depth has nothing to measure. The depth axis keeps its vocabulary and loses its ruler. | The two-axes model (design decision 1) |
| Cause-attributed staleness | `stale_after` is a clock. Dictum's staleness is a set of change-event IDs that clears only when empty and blocks the release gate. Both coexist; an OKF consumer may refuse a doc Dictum calls current or serve one Dictum calls stale. | #12, #13 |
| The gate-bound publish step | Absent `status` means stable. The version bump has no OKF home at all. | #30: an unenforced lifecycle field rots |
| "Conformant" meaning build-ready | A set with every concern at Sketch is a fully conformant OKF bundle. The re-partition check has no standing against a spec that tells consumers to attempt best-effort consumption of versions they do not understand. | #32, #33: silent partition holes on upgrade |
| Dangling references as errors | OKF: a broken link "may simply represent not-yet-written knowledge". Dictum names that seam (described-here, minted-by-X) and tightens it at Contract-grade. Tolerated silence replaces a tracked placeholder. | #14; the forward-reference design decision |
| The binding map as the one stored index | Assertions in concept front matter as executor and attester leave the coverage check (every code-realizable Contract-grade contract is bound) with no single index to run over; the drift-detector's binding gate breaks. | #15: code evolved, docs silently lied |
| The machine-extraction extension points | The register-line bar, the ID grammar, and every deterministic checker built on them (gate-check, idweb, drift-check, reverse-extract, the JS/Python parity test) key on backticked tokens. Links replace them; the model-B structural slice is redefined from scratch. | #34 and the grammar decision; the lab's conformance corpus |
| Control of the base format | The RELEASES model (signed tags, checksums, MAJOR/MINOR calibrated to impact on existing sets, named re-conformance steps) sits on an unsigned root that shipped two breaking renames in a minor. An upstream change forces a Dictum release on someone else's schedule; fixing upstream needs a Google CLA. | The one-canonical-version guarantee |
| Interview-first doctrine | OKF is built for a corpus continuously rewritten by agents, with trust inferred afterwards. Dictum pays for trust at authoring time and treats inference as a concession. Adopting OKF's trust model imports the posture #25 was written to keep out. | #25 |
| Domain-clean, product-agnostic text | Full conformance vendors SPEC.md into every product repo (tools resolve the standard locally). Its worked examples are drawn from one business domain, so that domain's vocabulary would enter every product repo, against the standard's product-agnostic rule. | Product-agnosticism (Part 0) |
| The implementer's read | Link syntax alone lengthens every doc set 9 to 19%, and OKF's own bundles spend 24% of their bytes on front matter. The read an AI builds from is the product's whole purpose. | Part 0.3: build without guessing, at the cost of reading more |
| One provenance vocabulary, one heading convention | Provenance twice (markers and keyed footnotes); headings twice (the document contract and `# Schema`, `# Examples`, `# Computation`). | Owned-twice at the meta level |

### The line for adopters

What survives untouched is the manifest, the trait and sub-aspect vocabulary, and the concern specs' content, because OKF is silent about non-markdown files and about what a body must say. Everything Dictum loses is in the layer where OKF speaks, and that layer is where the gates live. Full conformance replaces Dictum's gate layer with a permissive envelope. For Dictum's purpose that is a downgrade, while three of OKF's ideas are worth adopting as native rules.

Of the six gains, one needs the migration and only under a condition that does not hold today. Three are ideas worth taking as native rules at the cost of a few lines. Two are served by an export. Of the fourteen losses, nine re-open a catalogued failure that a real build already paid for once. That asymmetry holds before any token is counted. The next section counts them.

## 5. What it would cost

### The fixed context cost

Editorial sessions load the standard material at the start and hold it for the whole job. Measured from the v1.2.0 file sizes at four characters per token. Two bounds are shown. The net column is the best case for OKF: only its normative core is loaded (27.1 KB, the 36.9 KB spec minus its motivation, changelog and worked-example appendix), about 5 KB of reconciliation rules are added, and the 10 KB of Dictum envelope text OKF would replace (Parts 6, 7, 8; template front matter; publish and index steps; glossary entries) is subtracted. The gross column loads the whole spec and subtracts nothing.

| Session type | Today | With OKF, net | Delta | With OKF, gross | Delta |
|---|---|---|---|---|---|
| doc-levelup, one concern (STANDARD, GLOSSARY, one concern spec, template, skill) | 99.5 KB, ~24.9K tokens | 121.6 KB, ~30.4K tokens | +22% | 141.4 KB, ~35.4K tokens | +42% |
| doc-feature, a delta across two concerns | 102.1 KB, ~25.5K tokens | 124.2 KB, ~31.1K tokens | +22% | 144.0 KB, ~36.0K tokens | +41% |
| doc-scaffold, intake over the eight always-present specs | 144.1 KB, ~36.0K tokens | 166.2 KB, ~41.6K tokens | +15% | 186.0 KB, ~46.5K tokens | +29% |
| doc-maturity-auditor, all fifteen specs | 184.9 KB, ~46.2K tokens | 207.0 KB, ~51.8K tokens | +12% | 226.8 KB, ~56.7K tokens | +23% |

Why netting does not flip the sign: Dictum's envelope rules are about 10 KB. The OKF sections that cover the same ground are about 15 KB, and its normative core is 27 KB, because OKF also specifies things Dictum never needed to write down: source credibility signals, trust tiers, attested computation, the actor convention, its own versioning. Under full conformance all of that loads. Subtracting Dictum's 10 KB leaves the addition between 5.5K and 10.5K tokens per session.

The prefix is re-read on every turn. A 40-turn levelup session re-reads the OKF addition 40 times, between 221K and 419K tokens of context reads for OKF alone; an 80-turn session between 442K and 838K. Prompt caching discounts the price of those reads, not their occupancy: the addition takes 5.5K to 10.5K tokens of the window on every turn, and that share is not available for the product's own docs.

This cost has no end date. It is paid by every session on every downstream product, six sets today, for as long as they use the standard, and it grows with each OKF minor version. The migration cost is paid once; this one overtakes it within a handful of sessions.

### Rule text a downstream agent must hold

The per-session figures above load SPEC.md in full. The table below breaks the rule text down and shows what a restated profile would change.

| Text | Bytes | Approx. tokens |
|---|---|---|
| Dictum envelope rules today (Parts 6, 7, 8; template front matter and rung comments; templates README usage; auditor steps 8–9; scaffold steps 6–8; feature step 7; levelup steps 8–9; glossary entries) | ~10,000 | ~2,500 |
| OKF sections that overlap them (3, 4, 5.2, 5.4, 6, 7, 8, 11, 12) | ~15,000 | ~3,800 |
| OKF SPEC.md in full | 36,900 | ~9,200 |
| Proposed Dictum bundle profile, replacing most of the first row | ~2,000 | ~500 |

The profile is the whole cost case. With a 2 KB profile the rule footprint is roughly neutral, a few hundred tokens lighter. If the tools are instead told to read SPEC.md, every session that loads it pays about 6,700 tokens more than today. OKF does not remove rules; it replaces Dictum's envelope rules with a larger external spec, and only a restated profile makes that affordable.

### Document text an implementer reads

Inventory of the six private validation doc sets named in the method section, measured read-only. Token figures use four characters per token.

| Measure | Value |
|---|---|
| Docs carrying Dictum front matter | 87 |
| Bytes | 1,720,897 (~430K tokens) |
| Front-matter bytes today | 27,199 (1.6%) |
| Unique IDs | 1,481 |
| ID references | 6,276 |
| Register lines | 1,061 |
| `<!-- rung: -->` comments still present in published docs | 374 |
| Derived READMEs (none carry front matter, so the `index.md` rename is clean) | 7 |
| Strategy C growth | +22 KB (+1.3%) |
| Strategy B growth | +118% on jotdo; +9% to +19% link inflation alone on the larger sets |

### Measured on the jotdo worked example

Mechanical conversion of the published single-file spec; the prototype is a scratch artifact and is not committed.

| Form | Files | Bytes | Approx. tokens |
|---|---|---|---|
| Dictum single-file spec | 1 | 8,924 | 2,230 |
| Strategy C | 2 | 9,186 | 2,300 |
| Strategy B | 24 | 19,498 | 4,870 |

Under B the 21 contract files carry 5,101 bytes of front matter, 26% of the set. OKF's own sample bundles run at 24%, so this is the format's normal shape, not a prototype artifact.

### Edit surface of full adoption

Full adoption is one file per owned contract, the shape ledger row 7 forces and Strategy B names, plus ledger rows 1, 4, 8 and 9 on top.

| Where | Full adoption (B plus the ledger) |
|---|---|
| STANDARD.md | Parts 3, 4, 5, 6, 7, 8, 10d rewritten; a bundle profile added |
| Templates | All five rewritten around per-contract files |
| Skills and agents | All eleven rewritten (rung computation, register-line rule, publish step, index generation, drift detection over links) |
| GLOSSARY, catalog, RELEASES | Rung rename, new vocabulary, MAJOR release notes |
| dictum-lab | All seven tools, 24 fixture docs, the JS/Python grammar parity |
| Downstream | About 1,500 new files across 6 sets plus the jotdo example; per-claim source footnotes; a `log.md` per directory to maintain |

Classification: MAJOR with no mechanical repair. No compatibility window makes it MINOR, because rows 1, 4, 7 and 9 change what a conforming set is.

## 6. Four ways to do it, read under both assumptions

With the ledger, the gains and losses, and the costs in hand, the four adoption shapes read as follows.

### A. Minimal conformance (partial)

Add `type:` to every doc. Conformant by OKF section 11, and partial by construction: "OKF, but only one key" is the fight the assumption forbids. +1 line per doc. Not a design.

### B. One concept per contract (rejected)

Each owned ID becomes `contracts/<ID>.md`; references become links; `deprecated` replaces tombstones. The only shape that satisfies ledger row 7, and it carries rows 1, 4, 8 and 9 on top. Scaled to the 1,481 unique IDs downstream it is about 1,500 new files. Breaks Part 4, where a concern's rung is computed from section completeness in one doc; re-bases Part 5; rewrites all eleven tools, six skills and five agents, and every lab tool. MAJOR, and it still pays the fixed cost forever. jotdo: 1 to 24 files, +118% bytes. Downstream: ~1,500 new files, +9% to +19% links.

### C. OKF envelope, Dictum content (partial)

One concept per Dictum doc, four keys added, Dictum keys kept as extensions, `published` mapped to `stable`, README replaced by `index.md`; `verified`, `stale_after`, `log.md` and Attested Computation declined. The cheapest shape in the first pass, and exactly a partial adoption: four declined families, three overridden rules. jotdo: +2.9%. Downstream: +1.3%. Not viable under full conformance. Its plan is kept in the appendix.

### D. Native lines plus an exporter skill (recommended)

Keep Dictum as it is. Take three OKF ideas as Dictum's own optional rules. Add an advisory `doc-export-okf` skill that derives an OKF bundle from a Dictum set on demand. Context cost while authoring: 0. Migration: 0. Standard change: three optional lines (MINOR) and one skill. The next section gives the design.

## 7. The recommended direction

The exporter derives an OKF bundle from a Dictum set on demand:

- concern docs become concepts with `type`, `title`, `description` and `generated` derived from the manifest and front matter;
- register lines optionally become per-contract concept files, with backticked references rewritten to links;
- the derived README becomes `index.md`; tombstones become `deprecated`; the root carries `okf_version`;
- Dictum staleness, markers, rungs and the manifest are carried as extension keys or omitted, never reinterpreted.

The bundle is regenerated, never edited. That is the same derived-not-stored discipline as the reverse-reference graph in Part 0.5 and the same one-way posture as the tracker mirror in Part 10c. Strategy D's limitation is the point: OKF consumers get a read-only mirror, and edits made there do not flow back. Dictum stays the source of truth, which is the direction of truth the standard already fixes for every external mirror. The model is never told OKF exists while authoring, so the fixed context cost is zero and nothing migrates.

Why a skill and not a deterministic tool. Dictum enforces form only at its extension points: the front-matter keys, the ID grammar, the register line, the manifest and binding map. Those give a deterministic skeleton: which concepts exist, their IDs, their edges, their status. Everything else OKF wants is unenforced on the Dictum side and needs judgment: a one-sentence `description` per concept, a `type` for a local prefix, where a register line's definition ends when it runs into a table or a paragraph, which interview answer or decision record becomes a `sources` entry. So the exporter is model-A work in a skill. A lab validator can still check the result deterministically against OKF section 11 and the skeleton, so a bad export is caught without making the export itself deterministic.

The three native lines, and one naming rule. Each is an optional addition with no re-conformance owed, so together they are a MINOR.

1. Authoring actor. An optional front-matter `generated: { by, at }` using the actor convention (`human:<id>`, `<producer>/<version>`), stated in Part 6 as Dictum's own record of whether an operator was present. Written by the scaffold, level-up and feature skills; read by the auditor to attribute unattended authoring.
2. Keyed per-claim attribution. An optional `sources` list with footnotes keyed to a stable `sources[].id`, offered by Part 10f for reverse-authored sets where a claim traces to a code site or an interview answer.
3. Receipt-shaped proof. The build-status Proof column may carry a receipt (commit, run id, artifact) that a check re-reads, stated in Delivery 11.6 with the Quality 11.5 evidence-run vocabulary, so Verified rests on an artifact rather than a cell.

Credit. Each of the three lines adapts an idea OKF states first: the actor convention and `generated` (SPEC.md v0.2, sections 5.2 and 7), keyed per-claim footnotes over `sources[].id` (section 5.1), and the receipt-and-attester shape of an attested computation (section 10). The wording in the standard is Dictum's own, so no license text travels with it (OKF is Apache-2.0; ideas and field names are not what that license covers), but the origin is recorded here and belongs in the standard's prior-art ledger and in the release note that lands the lines.

The naming rule: use OKF's key name verbatim where the semantics match exactly (`generated`, `sources`), so the exporter copies the field; never where they collide (`verified`, the `status` values), so no adopter reads a Dictum key with OKF's meaning. These are Dictum rules that happen to be OKF-compatible, not a partial adoption of OKF; the model is never told OKF exists while authoring.

## 8. What would reopen the decision

The decision would change under three conditions. An organization mandates OKF as its corpus format, a policy reason rather than a technical one. An OKF tool ecosystem appears that must *write* Dictum sets, so a one-way export is no longer enough. Or Dictum's purpose widens from build-time specs to run-time knowledge serving, where agents answer questions from the docs and attestation becomes load-bearing.

## Appendix: the Strategy C plan, if adoption were chosen anyway

Recorded for completeness; under Strategy D none of this happens. The plan below is the Strategy C plan from the first pass. It is a MINOR only because C declines part of OKF, and C is not viable under the full-conformance assumption. The edit surface of full adoption is in section 5 above.

### What a concern doc's front matter becomes under C

Dictum v1.2.0 today:

```yaml
---
artifact: product-doc
role: concern
concern-id: interfaces-and-contracts
behavior: core
trigger: always
current-rung: contract-grade
status: published
version: 1.3.0
---
```

Strategy C (added keys first, `status` value changed, `artifact` kept as an extension):

```yaml
---
type: Dictum Concern
title: Interfaces & Contracts — jotdo
description: CLI surface, error model, output shapes.
generated: { by: doc-scaffold/claude-fable-5-1, at: 2026-07-13T00:00:00Z }
status: stable
artifact: product-doc
concern-id: interfaces-and-contracts
behavior: core
trigger: always
current-rung: contract-grade
version: 1.3.0
---
```

Under C the following OKF features are deliberately not adopted, each recorded with its reason in the profile: `log.md` (Part 6), `stale_after` as a staleness model (Part 10d), `verified` (Verified-rung collision), Attested Computation (already covered by `INV` plus the binding map; may map later). The root `index.md` carries `okf_version: "0.2"`.

### Edit surface under C

| Where | What changes |
|---|---|
| Standard, self-exemplifying files | 27 files gain `type:`; `status: published` becomes `stable` |
| STANDARD.md | Part 6 (vocabulary; publish also sets `generated.at`), Part 7 (`index.md` as the derived index), Part 8 (bundle = directory), new ~2 KB bundle-profile sub-part |
| Templates | concern-doc and single-file front matter (+4 lines each); templates README |
| Skills and agents | doc-scaffold 6–8, doc-feature 7, doc-levelup 8–9, doc-excavate 8, doc-maturity-auditor 8–9, implementation-planner draft warning; about ten edits |
| Glossary, catalog, RELEASES, README, CLAUDE.md, EDITORIAL | Vocabulary entries; one design-decision row; release notes with named re-conformance steps; the "stands alone" rule reconciled with an external pin |
| dictum-lab | `dictumlib.discover()` keys on `role` today; gate-check publish check reads `published`; tracker-sync, drift-check, reverse-extract status reads; 24 fixture docs; one new envelope check |
| Downstream | 87 docs, 7 indexes; 6 manifests and binding maps untouched; the jotdo example |

Strategy C classification: MINOR, v1.3.0. Every change is a bounded mechanical step. The `status` value rename is the borderline item. A one-release compatibility window keeps it MINOR: tools accept `published` as an alias of `stable`, and `role` as a fallback for `type`. The aliases drop at the next MAJOR.

### Named re-conformance steps for the release notes

1. Add `type:`, `title:`, `description:`, `generated:` to every doc in the set, values per the bundle profile.
2. Replace `status: published` with `status: stable`.
3. Replace the derived README with a generated `index.md` in the OKF list form, no front matter; add `okf_version: "0.2"` at the bundle root.
4. Add one markdown link per consumed doc in each Dependencies & Cross-references section.
5. Set `authored_against: v1.3.0` after the walk.

### Phases

1. Decide and pin. Record OKF v0.2 at commit `ad30107` in RELEASES as an unsigned upstream pin. State that the Dictum profile, not SPEC.md, is normative.
2. Standard. Author the profile and the edits above. Re-run the standard's own self-exemplification check.
3. Lab. Update the five tools and 24 fixture docs; add the envelope check; keep the JS-versus-Python parity test green.
4. Downstream, one set at a time. A conversion script does steps 1 to 4 (the prototype's core exists); run the auditor and gate-check; commit. Order: the worked example first, then the sets from smallest to largest. One to two hours of operator review per set, one to two days total.
5. Compatibility window. Tools accept both vocabularies for one MINOR, then the aliases go at v2.

### Risks

- OKF churn. Mitigated by the commit pin and a normative profile. Re-evaluate only at OKF 1.0.
- `verified` collision. Mitigated by not adopting the key.
- Index name. The generated `index.md` lives beside the docs; a product's own README is not touched.
- Absent `status` means stable in OKF. The profile keeps the key required.
- Half-migrated sets. The auditor's status-claim check and the lab's publish check must accept both vocabularies during the window, or every partially converted set reads as an error.

---

Sources: Dictum `v1.2.0` (STANDARD.md, GLOSSARY.md, templates, skills, agents, failure-mode catalog, RELEASES.md, examples/jotdo); OKF `SPEC.md` v0.2, README, reference-agent source and the four sample bundles; six private validation doc sets and this lab's tools, read-only. Token counts are estimates at four characters per token.
