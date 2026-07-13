#!/usr/bin/env bash
# Runs dictum-gate-check across the fixture corpus and asserts expected findings.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../tools/gate-check/dictum-gate-check.py"
FIX="$HERE/../fixtures"
fail=0

expect() { # <fixture> <expected-error-count> <required-pattern>
  out=$(python3 "$CHECK" "$FIX/$1" 2>&1)
  errs=$(echo "$out" | tail -1 | grep -o '^[0-9]\+')
  if [ "$errs" != "$2" ]; then
    echo "FAIL $1: expected $2 error(s), got $errs"; echo "$out" | sed 's/^/    /'; fail=1
  elif [ -n "$3" ] && ! echo "$out" | grep -q "$3"; then
    echo "FAIL $1: expected pattern not found: $3"; echo "$out" | sed 's/^/    /'; fail=1
  else
    echo "PASS $1 ($2 error(s))"
  fi
}

expect clean             0 ""
expect partition-hole    1 "unaccounted"
expect dangling-id       1 "dangling reference"
expect unpublished-built 1 "publish step owed"

[ "$fail" = 0 ] && echo "corpus: all fixtures pass" || echo "corpus: FAILURES"
exit $fail
