#!/usr/bin/env python3
"""dictum-editorial-lint — lints the Dictum standard repo's own prose against
its Editorial Charter (../dictum/EDITORIAL.md). EXPERIMENTAL / non-normative.

Zero-dependency (stdlib only). This is a research/maintenance instrument: the
standard's text (and its charter) is the only definition of conformance; a
disagreement between this tool and the charter is a bug HERE. It implements
only the *mechanically checkable* subset of EDITORIAL.md Part 6 / Appendix B.

Checks:
  standard-lab-link  ERROR  a markdown link in normative prose whose target
                            references the lab (STANDARD/GLOSSARY/concerns only)
  forbidden-name     ERROR  a denylisted term appears in any *.md (denylist is
                            NOT committed here; read from env or <repo>/.editorial-denylist)
  research-prose     WARN   war-story / research-process phrases in STANDARD.md
                            or a concern spec
  migrated-section   WARN   a `## Worked Example` / `## Design Decisions` heading
                            back in a concern spec (those migrated to the lab)

Output mimics gate-check: one finding per line, then a tail line that STARTS
with the error count. Findings are sorted by file then line (deterministic /
byte-identical across runs). Exit code is 1 iff there is >=1 ERROR; WARN never
drives the exit code (heuristics are advisory only).
"""
import os, re, sys, glob

# ---------- findings: (relpath, line, sev, check, snippet)

FINDINGS = []
NOTES = []

def finding(relpath, line, sev, check, snippet):
    FINDINGS.append((relpath, line, sev, check, snippet.strip()))

def rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, '/')

def read_lines(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            return fh.read().splitlines()
    except OSError:
        return []

def trunc(s, n=100):
    s = s.strip()
    return s if len(s) <= n else s[:n - 1] + '…'

# ---------- discovery

def normative_files(root):
    """STANDARD.md, GLOSSARY.md, concerns/*.md — the files a rule binds."""
    files = []
    for name in ('STANDARD.md', 'GLOSSARY.md'):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            files.append(p)
    files += sorted(glob.glob(os.path.join(root, 'concerns', '*.md')))
    return files

def all_md_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in filenames:
            if fn.endswith('.md'):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)

def concern_specs(root):
    return sorted(glob.glob(os.path.join(root, 'concerns', '*.md')))

# ---------- check: standard -> lab dependency link

LINK_RE = re.compile(r'\]\(([^)]*)\)')

def check_standard_lab_link(root):
    for p in normative_files(root):
        rp = rel(p, root)
        for i, line in enumerate(read_lines(p), 1):
            for m in LINK_RE.finditer(line):
                target = m.group(1)
                if 'dictum-lab' in target:
                    finding(rp, i, 'ERROR', 'standard-lab-link',
                            trunc(f']({target})'))

# ---------- check: forbidden-name scan (denylist NOT committed here)

def load_denylist(root):
    path = os.environ.get('DICTUM_EDITORIAL_DENYLIST') \
        or os.path.join(root, '.editorial-denylist')
    if not os.path.isfile(path):
        return None
    terms = []
    for raw in read_lines(path):
        s = raw.strip()
        if not s or s.startswith('#'):
            continue
        terms.append(s)
    return terms

def check_forbidden_name(root):
    terms = load_denylist(root)
    if terms is None:
        NOTES.append('note: no denylist found (set DICTUM_EDITORIAL_DENYLIST); '
                     'forbidden-name check skipped')
        return
    lowered = [(t, t.lower()) for t in terms]
    for p in all_md_files(root):
        rp = rel(p, root)
        for i, line in enumerate(read_lines(p), 1):
            low = line.lower()
            for term, tl in lowered:
                if tl and tl in low:
                    finding(rp, i, 'ERROR', 'forbidden-name',
                            trunc(f'forbidden term `{term}`'))

# ---------- check: research-prose smells (WARN only)

PROSE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    r'\bin practice\b',
    r'surfaced (building|when|as)\b',
    r'\ba validation build\b',
    r'\(round \d+\)',
    r'\bround-\d+\b',
    r'\bthe v0\.\d+\b',
    r'verified in practice',
    r"422'd",
)]

def check_research_prose(root):
    scope = [os.path.join(root, 'STANDARD.md')] + concern_specs(root)
    for p in scope:
        if not os.path.isfile(p):
            continue
        rp = rel(p, root)
        for i, line in enumerate(read_lines(p), 1):
            for pat in PROSE_PATTERNS:
                m = pat.search(line)
                if m:
                    finding(rp, i, 'WARN', 'research-prose',
                            trunc(f'“{m.group(0)}”'))

# ---------- check: migrated-section heading back in a concern spec (WARN)

MIGRATED_RE = re.compile(r'^##\s+(Worked Example|Design Decisions)\b')

def check_migrated_section(root):
    for p in concern_specs(root):
        rp = rel(p, root)
        for i, line in enumerate(read_lines(p), 1):
            if MIGRATED_RE.match(line):
                finding(rp, i, 'WARN', 'migrated-section', trunc(line))

# ---------- driver

def run(root):
    check_standard_lab_link(root)
    check_forbidden_name(root)
    check_research_prose(root)
    check_migrated_section(root)

def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
    run(root)
    for note in NOTES:
        print(note)
    for relpath, line, sev, check, snippet in sorted(
            FINDINGS, key=lambda f: (f[0], f[1], f[3], f[4], f[2])):
        print(f'{sev} [{check}] {relpath}:{line}  {snippet}')
    errs = sum(1 for f in FINDINGS if f[2] == 'ERROR')
    warns = sum(1 for f in FINDINGS if f[2] == 'WARN')
    print(f'{errs} error(s), {warns} warning(s)')
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
