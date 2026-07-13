> Fixture: targets Dictum v1.1.0. Defect: none (boundary probe)

As `clean`, but with the OpenAPI artifact removed and the binding's
`compare_via: openapi` dropped. This probes just OUTSIDE the decidable
boundary: with no machine-readable interface artifact, endpoint/entity drift
is not decidable for model B, and the tool must DECLINE LOUDLY (an INFO
`not-decidable` finding) rather than guess. Expected: 0 errors + the decline.
