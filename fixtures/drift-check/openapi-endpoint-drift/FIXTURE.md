> Fixture: targets Dictum v1.1.0. Defect: openapi-endpoint-drift

As `clean`, except the OpenAPI artifact additionally declares
`DELETE /notes/{id}`, which no owned API/ROUTE contract states. Expected:
exactly one certain-tier `route-diff` ERROR, direction code-ahead —
decidable because a machine-readable artifact exists (the precondition the
roadmap's model-B path names).
