> Fixture: targets Dictum v1.1.0. Defect: tracker-ahead-item

As `clean`, except a tracker-side user renamed the execution item and
reopened it — the tracker has run ahead of the repo. The reconciliation rule
is REPO-WINS (Part 10c: a divergent tracker edit is a convenience, not a
source): expected one UPDATE action restoring title and state, exit 1 in
dry-run; after --apply a re-run is clean. The demand item stays untouched.
