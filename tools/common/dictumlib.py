#!/usr/bin/env python3
"""dictumlib — shared, zero-dependency parsing helpers for dictum-lab tools.

Python 3 standard library only. Factored from tools/gate-check/dictum-gate-check.py;
gate-check deliberately keeps its own inline copy (it ships as a single file) —
when the YAML subset, the front-matter handling, or the ID/definition grammar
changes, change BOTH and re-run tests/run.sh.

Non-normative: the standard's text (STANDARD.md + concerns/ in the canonical
Dictum repository) is the only definition of conformance. Where a helper here
disagrees with the text, the text wins and this module has a bug.
"""
import os, re, glob

# ---------- minimal YAML-subset parser (block maps/lists, flow maps/lists, comments)
# The subset is what the standard's templates use for manifests, front matter,
# and binding maps — keeping it plain is what keeps the tooling dependency-free.

def strip_comment(line):
    out, q = [], None
    for ch in line:
        if q:
            if ch == q: q = None
        elif ch in "\"'": q = ch
        elif ch == '#':
            break
        out.append(ch)
    return ''.join(out).rstrip()

def parse_flow(s):
    s = s.strip()
    if s.startswith('{'):
        body, _ = _split_flow(s[1:], '}')
        d = {}
        for part in body:
            if not part.strip(): continue
            k, _, v = part.partition(':')
            d[k.strip().strip('"\'')] = parse_flow(v)
        return d
    if s.startswith('['):
        body, _ = _split_flow(s[1:], ']')
        return [parse_flow(p) for p in body if p.strip()]
    if s in ('true','True'): return True
    if s in ('false','False'): return False
    if s in ('null','~',''): return None
    return s.strip().strip('"\'')

def _split_flow(s, close):
    parts, depth, cur, q = [], 0, [], None
    for i, ch in enumerate(s):
        if q:
            cur.append(ch)
            if ch == q: q = None
            continue
        if ch in "\"'": q = ch; cur.append(ch); continue
        if ch in '{[': depth += 1; cur.append(ch); continue
        if ch in '}]':
            if depth == 0 and ch == close:
                parts.append(''.join(cur)); return parts, i
            depth -= 1; cur.append(ch); continue
        if ch == ',' and depth == 0:
            parts.append(''.join(cur)); cur = []; continue
        cur.append(ch)
    parts.append(''.join(cur))
    return parts, len(s)

def parse_yaml_subset(text):
    lines = []
    for raw in text.splitlines():
        s = strip_comment(raw)
        if s.strip() == '': continue
        indent = len(raw) - len(raw.lstrip(' '))
        lines.append((indent, s.strip()))
    pos = [0]
    def block(min_indent):
        if pos[0] >= len(lines): return None
        ind, s = lines[pos[0]]
        if ind < min_indent: return None
        is_list = s.startswith('- ') or s == '-'
        return _list(ind) if is_list else _map(ind)
    def _map(indent):
        d = {}
        while pos[0] < len(lines):
            ind, s = lines[pos[0]]
            if ind < indent: break
            if ind > indent: pos[0] += 1; continue  # stray deeper line (shouldn't happen)
            m = re.match(r'^([^:]+):\s*(.*)$', s)
            if not m: pos[0] += 1; continue
            key, val = m.group(1).strip().strip('"\''), m.group(2).strip()
            pos[0] += 1
            if val == '':
                child = block(indent + 1)
                d[key] = child if child is not None else None
            else:
                d[key] = parse_flow(val)
        return d
    def _list(indent):
        out = []
        while pos[0] < len(lines):
            ind, s = lines[pos[0]]
            if ind < indent or not (s.startswith('- ') or s == '-'): break
            item = s[1:].strip()
            pos[0] += 1
            if item == '':
                out.append(block(indent + 1))
            elif re.match(r'^[^:{\[]+:\s', item) or re.match(r'^[^:{\[]+:$', item):
                k, _, v = item.partition(':')
                out.append({k.strip(): parse_flow(v)})
            else:
                out.append(parse_flow(item))
        return out
    return block(0)

# ---------- front matter

def front_matter(path):
    try:
        text = open(path, encoding='utf-8').read()
    except OSError:
        return None, ''
    if not text.startswith('---'): return None, text
    end = text.find('\n---', 3)
    if end < 0: return None, text
    fm = parse_yaml_subset(text[3:end])
    return (fm if isinstance(fm, dict) else None), text

# ---------- doc-set discovery (same layout gate-check consumes)

def discover(root):
    def first(*cands):
        for c in cands:
            p = os.path.join(root, c)
            if os.path.exists(p): return p
        return None
    manifest = first('docs/manifest.yaml', 'manifest.yaml')
    standard = first('dictum', 'docs/dictum')
    bindings = first('docs/bindings.yaml', 'bindings.yaml')
    docs = []
    for pat in ('docs/*.md', 'docs/concerns/*.md', '*.md'):
        for p in glob.glob(os.path.join(root, pat)):
            if standard and os.path.commonpath([p, standard]) == standard: continue
            fm, _ = front_matter(p)
            if fm and 'role' in fm:
                docs.append(p)
    return manifest, standard, bindings, sorted(set(docs))

# ---------- ID grammar & registries

STRICT = r'[A-Z][A-Z0-9]+(?:[-_][A-Z0-9*]+)+[a-z]?'   # ID grammar (hyphen or error-code underscore)
ID_RE = re.compile(r'\b(' + STRICT + r')\b')

# The Part 5 ID registry, collected from STANDARD Part 5, GLOSSARY.md and the
# binding-map / build-status templates. Informational only: a doc set may coin
# additional LOCAL prefixes, and "an off-registry prefix is not itself a
# finding" (STANDARD Part 5) — so tools treat this as metadata, never a gate.
REGISTERED_PREFIXES = {
    'CAP', 'ENTITY', 'INV', 'COMPONENT', 'API', 'CLI', 'LIB', 'EVT', 'ROLE',
    'POLICY', 'SCREEN', 'ROUTE', 'ENV', 'DEP', 'PERF', 'LICENSE', 'SUCCESS',
    'PERSONA', 'ADR', 'SEQ', 'ERR', 'SEC', 'WVR', 'AC',
}

# Kinds expected in the binding map — the "Which contract kinds bind" list of
# templates/binding-map.template.md. Kinds outside it are not coverage-tracked.
CODE_REALIZABLE_KINDS = {'API', 'CLI', 'LIB', 'EVT', 'ENTITY', 'SCREEN',
                         'ROUTE', 'COMPONENT', 'INV'}

def id_kind(tok):
    return tok.split('-')[0].split('_')[0]

# ---------- the owned-ID web (register-form definition grammar)
# Ported from gate-check, where it was calibrated against pinned-state ground
# truth (see studies/2026-07-deterministic-gate-checks.md). A definition line:
# heading, table row, list item, or paragraph whose LEAD segment (before the
# first em-dash or end of bold) names one or more backticked IDs.

_ANCHOR = r'\**`?' + STRICT
DEF_LEAD = [
    re.compile(r'^\s*#{2,5}\s+(.{0,160})$'),                            # heading
    re.compile(r'^\s*\|\s*(' + _ANCHOR + r'.{0,250}?)\|'),              # table row, 1st cell
    re.compile(r'^\s*[-*]\s+(' + _ANCHOR + r'.{0,90}?)(?:—|:|$)'),      # list item
    re.compile(r'^\s*(\*\*`?' + STRICT + r'.{0,90}?)(?:—|:)'),          # paragraph register row
    re.compile(r'^\s*[-*]\s+(\*\*`[^`]{2,60}`\*\*.{0,20}?)(?:—|:)'),    # backticked non-ID key
    re.compile(r'^\s*(\*\*`[^`]{2,60}`\*\*\s*)(?:—|:)'),
    re.compile(r'^\s*(`' + STRICT + r'`)\s*[(:—]'),                     # bare start-of-line key
]
STRICT_RE = re.compile(r'\b(' + STRICT + r')\b')
ANYTICK_RE = re.compile(r'`([^`\s]{2,60})`')
OWNS_RE = re.compile(r'[Oo]wns[^.]*?`([A-Z][A-Z0-9]*)-#{2,}`')

class IdWeb:
    """The owned-ID web of a doc set: register-form definitions, prefixes,
    inline mentions, tombstones — plus the resolver gate-check calibrated."""

    def __init__(self, docmeta, tombstones=None):
        # docmeta: {relpath: (front_matter_dict, full_text)}
        self.owned = {}       # tok -> {'file', 'line', 'text'}
        self.prefixes = set()
        self.mentioned = set()
        self.tombstones = set(tombstones or [])
        for rel, (fm, text) in docmeta.items():
            for i, line in enumerate(text.splitlines(), 1):
                for r in DEF_LEAD:
                    m = r.match(line)
                    if m:
                        lead = m.group(1)
                        for t in STRICT_RE.findall(lead):
                            self.owned.setdefault(t, {'file': rel, 'line': i, 'text': line})
                            if '*' not in t:
                                self.prefixes.add(re.split(r'[-_]', t)[0])
                        for t in ANYTICK_RE.findall(lead):
                            self.owned.setdefault(t, {'file': rel, 'line': i, 'text': line})
                        break
                for m in OWNS_RE.finditer(line):
                    self.prefixes.add(m.group(1))
            for t in re.findall(r'`(' + STRICT + r')`', text):
                self.mentioned.add(t)
        for t in self.tombstones:   # supersession references stay resolvable (Part 10d)
            self.owned.setdefault(t, {'file': 'manifest:tombstone', 'line': 0, 'text': ''})

    def resolves(self, tok):
        if tok in self.owned: return True
        for o in self.owned:        # shaped wildcard register rows (EVT-*-X)
            if '*' in o and len([s for s in o.split('-') if s != '*']) >= 2:
                if re.fullmatch(o.replace('*', '[A-Z0-9-]+'), tok): return True
        for o in self.owned:        # prefix-elided shorthand (`VENDOR-ORDER` for ENTITY-VENDOR-ORDER)
            if '*' not in o and o.endswith('-' + tok): return True
        return False

# ---------- doc-set loading convenience

def load_docset(root):
    """Load the doc set at root into one dict; None-valued keys mean absent."""
    manifest_path, standard, bindings_path, docs = discover(root)
    manifest = None
    if manifest_path:
        manifest = parse_yaml_subset(open(manifest_path, encoding='utf-8').read()) or {}
    bindings = None
    if bindings_path:
        bindings = parse_yaml_subset(open(bindings_path, encoding='utf-8').read()) or {}
    docmeta = {}
    for p in docs:
        fm, text = front_matter(p)
        docmeta[os.path.relpath(p, root)] = (fm or {}, text)
    return {
        'root': os.path.abspath(root),
        'manifest_path': manifest_path, 'manifest': manifest,
        'standard_path': standard,
        'bindings_path': bindings_path, 'bindings': bindings,
        'docmeta': docmeta,
    }
