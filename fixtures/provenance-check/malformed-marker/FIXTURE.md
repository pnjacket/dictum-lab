> Fixture: targets Dictum v1.2.0. Defect: malformed-marker

A synthetic MIT-outbound product whose ported unit carries a `SOURCE:` marker
that names an origin but **no license token** (`// SOURCE: acme-mathlib`). The
tool cannot check compatibility without a license, so it declines loudly rather
than guessing: expected **0 errors, 1 warning** (`malformed-marker`). WARN
never drives the exit code, so the tool exits 0.
