> Fixture: targets Dictum v1.1.0. Defect: dangling-binding

As `clean`, except `API-LIST-NOTES` carries a second locator whose path
(`src/gone.go`) does not exist. Expected: exactly one certain-tier
`binding-stale` ERROR (a defect in the index, not a code<->doc drift —
Part 10d). The binding's other locator still resolves, so no
`doc-ahead-unbuilt` fires.
