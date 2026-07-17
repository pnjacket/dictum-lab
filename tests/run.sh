#!/usr/bin/env bash
# Runs the lab's tools across the fixture corpus and asserts expected findings.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$HERE/../tools"
FIX="$HERE/../fixtures"
fail=0

# expect_tool <script> <fixture-dir> <label> <expected-error-count> <required-pattern>
# For checkers that print gate-check-style findings + a "N error(s), ..." tail.
expect_tool() {
  out=$(python3 "$1" "$2" 2>&1)
  errs=$(echo "$out" | tail -1 | grep -o '^[0-9]\+')
  if [ "$errs" != "$4" ]; then
    echo "FAIL $3: expected $4 error(s), got $errs"; echo "$out" | sed 's/^/    /'; fail=1
  elif [ -n "$5" ] && ! echo "$out" | grep -q "$5"; then
    echo "FAIL $3: expected pattern not found: $5"; echo "$out" | sed 's/^/    /'; fail=1
  else
    echo "PASS $3 ($4 error(s))"
  fi
}

# assert_grep <label> <pattern> <<< output ; assert_exit <label> <expected> <actual>
assert_exit() {
  if [ "$3" != "$2" ]; then echo "FAIL $1: expected exit $2, got $3"; fail=1; else echo "PASS $1 (exit $2)"; fi
}

echo "== gate-check =="
GATE="$TOOLS/gate-check/dictum-gate-check.py"
expect_tool "$GATE" "$FIX/clean"             gate/clean             0 ""
expect_tool "$GATE" "$FIX/partition-hole"    gate/partition-hole    1 "unaccounted"
expect_tool "$GATE" "$FIX/dangling-id"       gate/dangling-id       1 "dangling reference"
expect_tool "$GATE" "$FIX/unpublished-built" gate/unpublished-built 1 "publish step owed"

echo "== code-map =="
CODEMAP="$TOOLS/code-map/dictum-code-map.py"
TMPJ=$(mktemp)
trap 'rm -f "$TMPJ"' EXIT
python3 "$CODEMAP" "$FIX/code-map/clean" --out "$TMPJ" && python3 - "$TMPJ" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
ids = sorted(a['id'] for a in m['annotations'])
assert ids == ['API-CREATE-NOTE', 'API-LIST-NOTES', 'COMPONENT-NOTES-VIEW',
               'ENTITY-NOTE', 'SCREEN-NOTE-LIST'], ids
assert m['unparsed_annotations'] == [], m['unparsed_annotations']
oa = m['interfaces']['openapi']
assert len(oa) == 1 and len(oa[0]['endpoints']) == 2, oa
assert oa[0]['schemas'] == [{'fields': ['body', 'id', 'title'], 'name': 'Note',
                             'required': ['id', 'title']}], oa[0]['schemas']
assert len(m['interfaces']['json_schema']) == 1, m['interfaces']['json_schema']
keys = sorted(k['name'] for k in m['config_keys']['keys'])
assert keys == ['NOTES_ADDR', 'NOTES_API_BASE', 'NOTES_DB_PATH'], keys
assert m['config_keys']['heuristic'] is True
assert m['tiers']['config_keys']['tier'] == 'heuristic'
EOF
assert_exit "code-map/clean" 0 $?
python3 "$CODEMAP" "$FIX/code-map/annotation-syntax-unsupported" --out "$TMPJ" && python3 - "$TMPJ" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
# The certain tier extracts only the conforming annotation; the two
# non-conforming ones are DECLINED loudly, never guessed.
assert [a['id'] for a in m['annotations']] == ['CAP-NOTES'], m['annotations']
assert len(m['unparsed_annotations']) == 2, m['unparsed_annotations']
texts = ' '.join(u['text'] for u in m['unparsed_annotations'])
assert 'CAP-TAGS' in texts and 'cap-search' in texts, texts
EOF
assert_exit "code-map/annotation-syntax-unsupported (declines loudly)" 0 $?
# Determinism: two runs must be byte-identical.
a=$(python3 "$CODEMAP" "$FIX/code-map/clean") ; b=$(python3 "$CODEMAP" "$FIX/code-map/clean")
[ "$a" = "$b" ] && echo "PASS code-map/deterministic-output" || { echo "FAIL code-map/deterministic-output"; fail=1; }

echo "== drift-check =="
DRIFT="$TOOLS/drift-check/dictum-drift-check.py"
expect_tool "$DRIFT" "$FIX/drift-check/clean"                  drift/clean                  0 ""
expect_tool "$DRIFT" "$FIX/drift-check/dangling-binding"       drift/dangling-binding       1 "binding-stale"
expect_tool "$DRIFT" "$FIX/drift-check/code-ahead-id"          drift/code-ahead-id          1 "code-ahead"
expect_tool "$DRIFT" "$FIX/drift-check/doc-ahead-unbuilt"      drift/doc-ahead-unbuilt      1 "doc-ahead-unbuilt"
expect_tool "$DRIFT" "$FIX/drift-check/openapi-endpoint-drift" drift/openapi-endpoint-drift 1 "route-diff"
# Boundary probe: no artifact -> the tool must DECLINE LOUDLY, not guess.
expect_tool "$DRIFT" "$FIX/drift-check/no-interface-artifact"  drift/no-interface-artifact  0 "not-decidable"
# The pre-built --map path and --json events must agree with the live path.
TMPJ2=$(mktemp)
trap 'rm -f "$TMPJ" "$TMPJ2"' EXIT
python3 "$CODEMAP" "$FIX/drift-check/code-ahead-id" --out "$TMPJ"
python3 "$DRIFT" "$FIX/drift-check/code-ahead-id" --map "$TMPJ" --json > "$TMPJ2"
python3 - "$TMPJ2" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
assert d['counts']['error'] == 1, d['counts']
ev = d['candidate_change_events']
assert len(ev) == 1 and ev[0]['id'] == 'LIB-EXPORT' and ev[0]['direction'] == 'code-ahead', ev
assert ev[0]['classification'] == 'proposed' and ev[0]['adjudication'] == 'pending', ev
EOF
assert_exit "drift/json-map-mode (Part 10d change-event shape)" 0 $?

echo "== reverse-extract =="
REVX="$TOOLS/reverse-extract/dictum-reverse-extract.py"
out=$(python3 "$REVX" "$FIX/code-map/clean") ; rc=$?
ok=1
[ $rc -eq 0 ] || ok=0
echo "$out" | grep -q "DRAFT" || ok=0
echo "$out" | grep -q "\[ASSUMPTION\]" || ok=0
# recovered annotation IDs land as real draft bindings...
echo "$out" | grep -q "^  API-LIST-NOTES:" || ok=0
# ...coined artifact candidates stay commented stubs (identity not decidable)...
echo "$out" | grep -q "# API-GET-NOTES:" || ok=0
# ...a coined ID equal to a recovered one merges instead of duplicating...
echo "$out" | grep -q '"provenance": "recovered+artifact"' || ok=0
# ...and the un-extractables are DECLINED loudly, not guessed.
echo "$out" | grep -q "deliberately excluded" || ok=0
echo "$out" | grep -qi "no rung and no Verified claim" || ok=0
[ $ok -eq 1 ] && echo "PASS reverse-extract/clean (draft + declines)" || { echo "FAIL reverse-extract/clean"; echo "$out" | head -40 | sed 's/^/    /'; fail=1; }
# Determinism: two runs must be byte-identical.
b=$(python3 "$REVX" "$FIX/code-map/clean")
[ "$out" = "$b" ] && echo "PASS reverse-extract/deterministic-output" || { echo "FAIL reverse-extract/deterministic-output"; fail=1; }
# --out writes the three files, and refuses to write into the repo itself.
TMPD=$(mktemp -d)
python3 "$REVX" "$FIX/code-map/clean" --out "$TMPD/rx" >/dev/null
[ -f "$TMPD/rx/candidate-inventory.json" ] && [ -f "$TMPD/rx/bindings.draft.yaml" ] && [ -f "$TMPD/rx/recoverability-report.md" ] \
  && echo "PASS reverse-extract/--out" || { echo "FAIL reverse-extract/--out"; fail=1; }
python3 "$REVX" "$FIX/code-map/clean" --out "$FIX/code-map/clean" >/dev/null 2>&1
assert_exit "reverse-extract/refuses-repo-root" 2 $?
rm -rf "$TMPD"

echo "== tracker-sync =="
TSYNC="$TOOLS/tracker-sync/dictum-tracker-sync.py"
python3 "$TSYNC" "$FIX/tracker-sync/clean" > /dev/null
assert_exit "tracker-sync/clean (in sync)" 0 $?
out=$(python3 "$TSYNC" "$FIX/tracker-sync/tracker-ahead-item"); rc=$?
{ [ $rc -eq 1 ] && echo "$out" | grep -q "UPDATE #1" && echo "$out" | grep -q "repo wins" \
    && echo "$out" | grep -q "1 non-execution tracker item(s) untouched"; } \
  && echo "PASS tracker-sync/tracker-ahead-item (repo-wins update)" \
  || { echo "FAIL tracker-sync/tracker-ahead-item"; echo "$out" | sed 's/^/    /'; fail=1; }
out=$(python3 "$TSYNC" "$FIX/tracker-sync/missing-execution-item"); rc=$?
{ [ $rc -eq 1 ] && echo "$out" | grep -q "CREATE Slice 1"; } \
  && echo "PASS tracker-sync/missing-execution-item (create)" \
  || { echo "FAIL tracker-sync/missing-execution-item"; echo "$out" | sed 's/^/    /'; fail=1; }
# --apply must converge (re-run clean) and mutate ONLY the tracker file
# (the downstream-mirror invariant: no doc-set file is ever written).
TMPD=$(mktemp -d)
for f in tracker-ahead-item missing-execution-item; do
  cp -r "$FIX/tracker-sync/$f" "$TMPD/$f"
  python3 "$TSYNC" "$TMPD/$f" --apply > /dev/null
  ok=$?
  python3 "$TSYNC" "$TMPD/$f" > /dev/null
  rerun=$?
  changed=$(diff -rq "$FIX/tracker-sync/$f" "$TMPD/$f" | grep -cv "tracker.json")
  if [ $ok -eq 0 ] && [ $rerun -eq 0 ] && [ "$changed" = "0" ]; then
    echo "PASS tracker-sync/$f --apply (converges; only the tracker mutated)"
  else
    echo "FAIL tracker-sync/$f --apply (apply=$ok rerun=$rerun non-tracker-diffs=$changed)"; fail=1
  fi
done
rm -rf "$TMPD"
# A missing declaration is DECLINED loudly (exit 2), never guessed.
python3 "$TSYNC" "$FIX/code-map/clean" >/dev/null 2>&1
assert_exit "tracker-sync/no-declaration (declines)" 2 $?

echo "== idweb-viewer (node) =="
# The viewer's engine is a JS port of dictumlib's grammar + gate-check's
# idweb/bindings passes — the grammar lives in THREE places (dictumlib.py,
# gate-check's inline copy, idweb.js); these cases keep the third in sync.
IDWEB="$TOOLS/idweb-viewer/idweb.js"
if command -v node >/dev/null 2>&1; then
  expect_idweb() {
    out=$(node "$1" "$2" 2>&1)
    errs=$(echo "$out" | tail -1 | grep -o '^[0-9]\+')
    if [ "$errs" != "$4" ]; then
      echo "FAIL $3: expected $4 error(s), got $errs"; echo "$out" | sed 's/^/    /'; fail=1
    elif [ -n "$5" ] && ! echo "$out" | grep -q "$5"; then
      echo "FAIL $3: expected pattern not found: $5"; echo "$out" | sed 's/^/    /'; fail=1
    else
      echo "PASS $3 ($4 error(s))"
    fi
  }
  expect_idweb "$IDWEB" "$FIX/clean"                        idweb/clean            0 ""
  expect_idweb "$IDWEB" "$FIX/dangling-id"                  idweb/dangling-id      1 "dangling reference"
  expect_idweb "$IDWEB" "$FIX/drift-check/clean"            idweb/bindings-clean   0 ""
  expect_idweb "$IDWEB" "$FIX/drift-check/dangling-binding" idweb/dangling-binding 1 "locator path missing"
  # grammar sync: the JS finding must equal gate-check's, byte for byte
  # (modulo gate-check's padded check-name column).
  js=$(node "$IDWEB" "$FIX/dangling-id" | grep 'dangling reference')
  py=$(python3 "$GATE" "$FIX/dangling-id" | grep 'dangling reference' | sed 's/\[idweb    \]/[idweb]/')
  [ -n "$js" ] && [ "$js" = "$py" ] && echo "PASS idweb/grammar-sync (js finding == py finding)" \
    || { echo "FAIL idweb/grammar-sync"; echo "    js: $js"; echo "    py: $py"; fail=1; }
else
  echo "SKIP idweb-viewer: node not available"
fi

echo "== editorial-lint =="
# Lints the STANDARD repo's own prose against its Editorial Charter. Non-normative
# maintenance instrument: WARN heuristics never drive the exit code.
EDLINT="$TOOLS/editorial-lint/dictum-editorial-lint.py"
EDFIX="$FIX/editorial-lint"
expect_tool "$EDLINT" "$EDFIX/clean"             editorial/clean             0 ""
expect_tool "$EDLINT" "$EDFIX/standard-lab-link" editorial/standard-lab-link 1 "standard-lab-link"
# Heuristic smells are WARN only: 0 errors, but the warnings must be present.
out=$(python3 "$EDLINT" "$EDFIX/research-prose" 2>&1); rc=$?
{ [ $rc -eq 0 ] && echo "$out" | grep -q "research-prose" && echo "$out" | grep -q "migrated-section" \
    && [ "$(echo "$out" | tail -1 | grep -o '^[0-9]\+')" = "0" ]; } \
  && echo "PASS editorial/research-prose (0 error(s), WARN-only)" \
  || { echo "FAIL editorial/research-prose"; echo "$out" | sed 's/^/    /'; fail=1; }
# forbidden-name needs the (uncommitted-by-charter) denylist via env var.
DL="$EDFIX/forbidden-name/.editorial-denylist"
a=$(DICTUM_EDITORIAL_DENYLIST="$DL" python3 "$EDLINT" "$EDFIX/forbidden-name" 2>&1); rc=$?
errs=$(echo "$a" | tail -1 | grep -o '^[0-9]\+')
{ [ $rc -eq 1 ] && [ "$errs" = "1" ] && echo "$a" | grep -q "forbidden-name"; } \
  && echo "PASS editorial/forbidden-name (1 error via env denylist)" \
  || { echo "FAIL editorial/forbidden-name (exit=$rc errs=$errs)"; echo "$a" | sed 's/^/    /'; fail=1; }
# Determinism: a re-run must be byte-identical.
b=$(DICTUM_EDITORIAL_DENYLIST="$DL" python3 "$EDLINT" "$EDFIX/forbidden-name" 2>&1)
[ "$a" = "$b" ] && echo "PASS editorial/deterministic-output" || { echo "FAIL editorial/deterministic-output"; fail=1; }

[ "$fail" = 0 ] && echo && echo "corpus: all fixtures pass" || { echo; echo "corpus: FAILURES"; }
exit $fail
