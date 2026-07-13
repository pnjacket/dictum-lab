> Fixture: targets Dictum v1.1.0. Defect: missing-execution-item

As `clean`, except the slice is built but not yet Verified and the tracker is
empty: the projection derives one OPEN execution item the tracker lacks.
Expected one CREATE action, exit 1 in dry-run; after --apply a re-run is
clean (the created item carries the contract IDs as labels — the only join;
the repo stores no tracker back-reference).
