> Fixture: targets Dictum v1.1.0. Defect: forbidden-name

Exercises EDITORIAL Part 3 (describe by shape, never by name) with a fully
INVENTED, safe denylist term committed in `.editorial-denylist` (never a real
forbidden name — the mechanism is committed, the sensitive list is not). A
`STANDARD.md` line contains that invented term once. Run with
`DICTUM_EDITORIAL_DENYLIST` pointing at the fixture's denylist,
`dictum-editorial-lint` must report exactly 1 error (`forbidden-name`). With no
denylist it would instead print the skip note and report 0 errors.
