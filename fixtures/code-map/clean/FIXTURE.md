> Fixture: targets Dictum v1.1.0. Defect: clean

A fully synthetic note-taking service (invented product): a Python domain
module, a Go HTTP server, a small TS/HTML front end, an OpenAPI document and
a JSON Schema. Expected inventory: 5 annotations (leaders `#`, `//`, `/* */`,
`<!-- -->`), 0 unparsed, 2 OpenAPI endpoints + 1 schema, 1 JSON Schema,
3 config keys. Also the shared input for the `dictum-reverse-extract` tests
(the coined `ENTITY-NOTE` from the schema must merge with the recovered
annotation of the same ID).
