> Fixture: targets Dictum v1.1.0. Defect: research-prose

A concern spec that leaks research evidence into normative text: a war-story
phrase ("surfaced building …") and a migrated `## Design Decisions` heading
that belongs in a lab note. `dictum-editorial-lint` must report 0 errors and at
least 2 warnings (one `research-prose`, one `migrated-section`) — heuristics,
so they never drive the exit code.
