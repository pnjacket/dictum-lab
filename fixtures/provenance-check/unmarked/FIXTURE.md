> Fixture: targets Dictum v1.2.0. Defect: unmarked (the documented honest miss)

This is a **boundary probe for the undecidable side**, not a detection case. A
non-trivial unit that *looks* copied (a well-known algorithm) carries **no
`SOURCE:` marker at all**. There is no declaration to parse, so the tool
reports **0 errors, 0 warnings** and exits 0 — it does **not** flag the unit.

This is correct and intended. Detecting *undeclared* copying cannot be done
reliably (the source corpus is unbounded), so the tool never pretends to. A
clean run here does **not** clear the unit: an unmarked copy is the residual
the standard records, never something this tool certifies absent.

The optional, non-authoritative fingerprint heuristic can raise a WARN-only
signal when a configured tell-tale phrase happens to appear — `tests/run.sh`
exercises that path against this fixture with a custom `--fingerprints` list
(the `bit-twiddling` comment line) and asserts it stays WARN-only (0 errors,
exit 0). With the default fingerprint list this fixture is 0/0.
