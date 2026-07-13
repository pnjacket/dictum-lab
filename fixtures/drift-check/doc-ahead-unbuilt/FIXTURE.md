> Fixture: targets Dictum v1.1.0. Defect: doc-ahead-unbuilt

As `clean`, plus a doc-owned `COMPONENT-EXPORTER` whose binding-map entry
records no code evidence at all (no locators, no asserted_by). The map's
presence claims realization (Part 10d: populated as each slice is built), so
zero evidence is the deterministically decidable doc-ahead/unbuilt state.
Expected: exactly one certain-tier `doc-ahead-unbuilt` ERROR. (A merely
UNBOUND contract is deliberately NOT this finding — that is the legitimate
build-new coverage gap, Part 10e, reported as a WARN.)
