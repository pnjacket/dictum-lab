#!/usr/bin/env python3
"""dictum-provenance-check — source-provenance checker for a first-party code
tree (Dictum failure-mode #36, Governance 11.8 `source-provenance`). EXPERIMENTAL.

Zero-dependency (stdlib only). This is a research/maintenance instrument and it
is deliberately best-effort: the standard's text is the only definition of
conformance; a disagreement between this tool and the text is a bug HERE.

What this tool can and cannot decide (the whole point of the tool):

  DECIDABLE — the real job. Parse every in-code `SOURCE:` marker and check its
    declared `<license>` against the product's OUTBOUND license. A *declared*
    incompatible license (e.g. a GPL/AGPL/proprietary marker inside an
    MIT-outbound product) is an ERROR. Parsing the marker and attributing the
    declaration is exact.

  UNDECIDABLE — the honest limit. Detecting *undeclared* copying (an LLM or a
    human reproducing licensed source with NO marker) cannot be done reliably;
    the training/source corpus is unbounded. This tool does NOT pretend to. It
    offers at most a non-authoritative WARN-only fingerprint scan (a small,
    configurable list of tell-tale phrases a copier often leaves behind). That
    scan never drives the exit code. Unmarked copies are the residual the
    standard records; they are NEVER "cleared" by a clean run here.

Marker grammar (the machine-extraction extension point, host-language comment
leader exactly like `DICT:`):

    // SOURCE: <origin> <license>     # C/Go/TS/JS/Rust/Java/...
    #  SOURCE: <origin> <license>     # Python/Ruby/shell
    /* SOURCE: <origin> <license> */  ; SOURCE: <origin> <license>  (Clojure)

  <origin>  is one whitespace-free token (a URL or a short name like acme-mathlib).
  <license> is the LAST whitespace-separated token: an SPDX id, or one of
            `proprietary` / `non-redistributable` / `unknown`.

Checks:
  incompatible-license      ERROR  declared license incompatible with --outbound
  malformed-marker          WARN   a `SOURCE:` with no parseable license token
  unmarked-copy-heuristic   WARN   a configured fingerprint phrase (non-authoritative)

Output mimics gate-check: one finding per line, then a tail line that STARTS
with the error count. Findings are sorted by file then line (byte-identical
across runs). Exit code is 1 iff there is >=1 ERROR; WARN never drives the exit
code.
"""
import os, re, sys

# ---------- source discovery

SKIP_DIRS = {'.git', 'node_modules', 'vendor', 'dist', 'build', 'target',
             '__pycache__', '.venv', 'venv', '.tox', '.mypy_cache'}
SOURCE_EXTS = {'.py', '.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx', '.go',
               '.c', '.h', '.cpp', '.hpp', '.cc', '.cs', '.java', '.kt',
               '.rs', '.clj', '.cljs', '.rb', '.php', '.swift', '.scala',
               '.sh', '.bash', '.lua', '.hs', '.ex', '.exs'}
MAX_FILE_BYTES = 1_000_000

def walk_source(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            ext = os.path.splitext(fn)[1].lower()
            if ext not in SOURCE_EXTS:
                continue
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(p) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield p, ext

def read_text(path):
    try:
        return open(path, encoding='utf-8', errors='replace').read()
    except OSError:
        return None

# ---------- SOURCE marker parsing
# Same discipline as code-map's DICT: extraction: the marker rides a
# host-language comment leader. Anything that still says "SOURCE:" but has no
# parseable license is surfaced (malformed-marker), never silently dropped.

MARKER_RE = re.compile(r'(?://|<!--|/\*|#|--|;+|\*)\s*SOURCE:\s*(.*)$')

def parse_marker_tail(tail):
    """Return (origin, license) or (origin_or_None, None) if unparseable.
    The license is the LAST whitespace-separated token; the origin is the
    remainder before it. Trailing block-comment closers are stripped."""
    tail = re.sub(r'(-->|\*/)\s*$', '', tail.strip()).strip()
    toks = tail.split()
    if len(toks) >= 2:
        return ' '.join(toks[:-1]), toks[-1]
    if len(toks) == 1:
        return toks[0], None      # origin only, no license -> malformed
    return None, None             # bare "SOURCE:" -> malformed

# ---------- license classification + outbound compatibility
#
# Compatibility model (deliberately coarse and clearly stated). Each license
# maps to a permissiveness RANK; more-permissive source may be included in a
# more- (or equally-)restrictive product, i.e. a source of rank r is includable
# in an outbound of rank R iff r <= R. Two categories sit outside the rank:
#   - NON_FREE (proprietary / non-redistributable): never includable -> ERROR.
#   - UNKNOWN: not decidable by machine -> WARN (needs human determination).
# This reproduces the intended table exactly for the common permissive-outbound
# case (see README); refining specific SPDX pairings (e.g. Apache-2.0 into
# GPL-2.0-only) is future work and is noted in the study as a boundary.

RANK_PERMISSIVE      = 0   # MIT, BSD-*, Apache-2.0, ISC, 0BSD, Zlib, Unlicense, CC0, public-domain
RANK_COPYLEFT_WEAK   = 1   # LGPL-*, MPL-*, EPL-*
RANK_COPYLEFT_STRONG = 2   # GPL-*
RANK_NETWORK_COPYLEFT= 3   # AGPL-*

# category tags used in findings / classification
CAT_PERMISSIVE, CAT_WEAK, CAT_STRONG, CAT_NETWORK = \
    'permissive', 'weak-copyleft', 'strong-copyleft', 'network-copyleft'
CAT_NON_FREE, CAT_UNKNOWN = 'non-free', 'unknown'

RANK = {
    CAT_PERMISSIVE: RANK_PERMISSIVE,
    CAT_WEAK: RANK_COPYLEFT_WEAK,
    CAT_STRONG: RANK_COPYLEFT_STRONG,
    CAT_NETWORK: RANK_NETWORK_COPYLEFT,
}

PERMISSIVE_IDS = {
    'MIT', 'MIT-0', 'ISC', '0BSD', 'BSD', 'BSD-2-CLAUSE', 'BSD-3-CLAUSE',
    'APACHE-2.0', 'APACHE', 'ZLIB', 'UNLICENSE', 'CC0-1.0', 'CC0',
    'PUBLIC-DOMAIN', 'PUBLICDOMAIN', 'WTFPL', 'BSL-1.0',
}
NON_FREE_IDS = {'PROPRIETARY', 'NON-REDISTRIBUTABLE', 'NONREDISTRIBUTABLE',
                'COMMERCIAL', 'ALL-RIGHTS-RESERVED'}

def classify(license_raw):
    """Map a declared license token to a category tag. Unrecognized tokens are
    treated as UNKNOWN (needs human determination), never guessed permissive."""
    lic = license_raw.strip().strip('.,;').upper()
    if lic in ('UNKNOWN', 'UNDETERMINED', 'TBD'):
        return CAT_UNKNOWN
    if lic.startswith('AGPL'):
        return CAT_NETWORK
    if lic.startswith('LGPL'):
        return CAT_WEAK
    if lic.startswith(('MPL', 'EPL', 'CDDL')):
        return CAT_WEAK
    if lic.startswith('GPL'):
        return CAT_STRONG
    if lic in PERMISSIVE_IDS or lic.startswith('BSD-'):
        return CAT_PERMISSIVE
    if lic in NON_FREE_IDS:
        return CAT_NON_FREE
    return CAT_UNKNOWN   # unrecognized SPDX-ish token -> human determination

def compatibility(source_license, outbound):
    """Return ('ok' | 'error' | 'warn', category, detail). Sound for the
    permissive-outbound default; coarse elsewhere (documented)."""
    src_cat = classify(source_license)
    out_cat = classify(outbound)
    if src_cat == CAT_NON_FREE:
        return 'error', src_cat, 'non-redistributable/proprietary source can never ship'
    if src_cat == CAT_UNKNOWN:
        return 'warn', src_cat, 'license needs human determination'
    if out_cat in (CAT_NON_FREE, CAT_UNKNOWN):
        # Outbound itself is unusual; decline to judge (best-effort WARN).
        return 'warn', src_cat, f'outbound `{outbound}` not on the compatibility table'
    if RANK[src_cat] <= RANK[out_cat]:
        return 'ok', src_cat, ''
    return 'error', src_cat, f'{src_cat} source is more restrictive than `{outbound}` outbound'

# ---------- unmarked-copy fingerprint scan (non-authoritative, WARN-only)
#
# Best-effort ONLY. This can never establish that code was copied, and a clean
# scan NEVER clears the residual: undeclared copying is undecidable. The default
# list holds a couple of INVENTED safe phrases so the mechanism is exercised
# without hard-coding any real project's attribution string. Override with a
# file (one phrase per line, `#` comments) via --fingerprints or the
# DICTUM_PROVENANCE_FINGERPRINTS env var.

DEFAULT_FINGERPRINTS = [
    'ported from acme-mathlib',        # invented attribution phrase
    'adapted from the widget-cookbook',# invented attribution phrase
]

def load_fingerprints(path):
    phrases = []
    for raw in read_text(path).splitlines() if read_text(path) is not None else []:
        s = raw.strip()
        if not s or s.startswith('#'):
            continue
        phrases.append(s)
    return phrases

# ---------- findings

FINDINGS = []   # (relpath, line, sev, check, snippet)

def finding(relpath, line, sev, check, snippet):
    FINDINGS.append((relpath, line, sev, check, snippet.strip()))

def trunc(s, n=100):
    s = s.strip()
    return s if len(s) <= n else s[:n - 1] + '…'

# ---------- driver

def run(root, outbound, fingerprints):
    fps = [(p, p.lower()) for p in fingerprints]
    for path, _ext in walk_source(root):
        text = read_text(path)
        if text is None:
            continue
        rel = os.path.relpath(path, root).replace(os.sep, '/')
        for i, line in enumerate(text.splitlines(), 1):
            m = MARKER_RE.search(line) if 'SOURCE:' in line else None
            # Only a SOURCE: riding a host-language comment leader is a marker;
            # a bare "SOURCE:" in prose or a string is not (never false-flagged).
            if m:
                origin, lic = parse_marker_tail(m.group(1))
                if lic is None:
                    finding(rel, i, 'WARN', 'malformed-marker',
                            trunc(f'SOURCE: marker with no parseable license: {line.strip()}'))
                else:
                    verdict, cat, detail = compatibility(lic, outbound)
                    if verdict == 'error':
                        finding(rel, i, 'ERROR', 'incompatible-license',
                                trunc(f'`{lic}` ({cat}) from `{origin}` incompatible with '
                                      f'`{outbound}` outbound — {detail}'))
                    elif verdict == 'warn':
                        finding(rel, i, 'WARN', 'incompatible-license',
                                trunc(f'`{lic}` from `{origin}`: {detail}'))
            # heuristic fingerprint scan (never on the same branch as a decision)
            low = line.lower()
            for phrase, pl in fps:
                if pl in low:
                    finding(rel, i, 'WARN', 'unmarked-copy-heuristic',
                            trunc(f'fingerprint “{phrase}” (non-authoritative; '
                                  f'declare a SOURCE: marker or confirm original)'))

def main():
    args = sys.argv[1:]
    outbound = 'MIT'
    fp_path = os.environ.get('DICTUM_PROVENANCE_FINGERPRINTS')
    positional = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--outbound' and i + 1 < len(args):
            outbound = args[i + 1]; i += 2; continue
        if a == '--fingerprints' and i + 1 < len(args):
            fp_path = args[i + 1]; i += 2; continue
        positional.append(a); i += 1
    if not positional:
        print('usage: dictum-provenance-check.py <target-src-dir> '
              '[--outbound <SPDX>] [--fingerprints <file>]', file=sys.stderr)
        sys.exit(2)
    root = os.path.abspath(positional[0])
    fingerprints = load_fingerprints(fp_path) if fp_path else list(DEFAULT_FINGERPRINTS)

    run(root, outbound, fingerprints)
    for relpath, line, sev, check, snippet in sorted(
            FINDINGS, key=lambda f: (f[0], f[1], f[3], f[4], f[2])):
        print(f'{sev} [{check}] {relpath}:{line}  {snippet}')
    errs = sum(1 for f in FINDINGS if f[2] == 'ERROR')
    warns = sum(1 for f in FINDINGS if f[2] == 'WARN')
    print(f'{errs} error(s), {warns} warning(s)')
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
