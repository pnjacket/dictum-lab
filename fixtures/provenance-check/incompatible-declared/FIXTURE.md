> Fixture: targets Dictum v1.2.0. Defect: incompatible-declared

A synthetic MIT-outbound product whose ported unit **honestly declares** a
`SOURCE:` marker with an incompatible license (`GPL-3.0-only`). This is the
decidable core of the tool: the declaration is parsed exactly and the license
is strong-copyleft, which cannot ship inside an MIT-outbound product. Expected
under the default `--outbound MIT`: **1 error** (`incompatible-license`).

Boundary note: run with `--outbound GPL-3.0-or-later` and the same marker is
**0 errors** — a GPL source inside a GPL product is compatible. The defect is
relative to the declared outbound, not absolute.
