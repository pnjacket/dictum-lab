#!/usr/bin/env python3
"""dictum-code-map — deterministic code-mapping backend for Dictum tooling. EXPERIMENTAL.

Zero-dependency (Python 3 stdlib only). Scans a product repo and emits a
normalized JSON inventory consumed by dictum-drift-check (model-B drift
detection, STANDARD Part 10d) and dictum-reverse-extract (deterministic
reverse-extraction, Part 10f):

  annotations   in-code contract-ID annotations (`// DICT: <ID>` and the
                common comment leaders) -> {id, file, line}
  interfaces    machine-readable interface artifacts, stack-light: OpenAPI
                documents (JSON or the plain YAML subset) and JSON Schema
                files -> endpoint/schema inventories
  config_keys   referenced env-var names (best-effort, HEURISTIC)

Exit code: 0 on success, 2 on usage/parse error. This tool checks nothing —
it is an inventory backend; the checkers sit downstream.

Non-normative: the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.
"""
import os, re, sys, json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from dictumlib import STRICT, REGISTERED_PREFIXES, parse_yaml_subset, id_kind

SCHEMA_VERSION = 1

# ---------- file walk

SKIP_DIRS = {'.git', 'node_modules', 'vendor', 'target', 'dist', 'build', 'out',
             '__pycache__', '.venv', 'venv', '.idea', '.vscode', '.next',
             'generated', 'bin', 'obj'}
SOURCE_EXTS = {'.py', '.go', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.rs', '.cs',
               '.java', '.kt', '.rb', '.sh', '.bash', '.html', '.htm', '.vue',
               '.svelte', '.c', '.h', '.cpp', '.hpp', '.css', '.sql', '.yaml',
               '.yml', '.toml', '.tf', '.clj', '.lua', '.hs', '.ex', '.exs'}
MAX_FILE_BYTES = 1_000_000

def walk_source(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            ext = os.path.splitext(fn)[1].lower()
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(p) > MAX_FILE_BYTES: continue
            except OSError:
                continue
            yield p, ext

def read_text(path):
    try:
        return open(path, encoding='utf-8', errors='replace').read()
    except OSError:
        return None

# ---------- DICT annotations
# Convention (STANDARD Part 10f / binding-map template): `// DICT: <ID>` at the
# realizing code site. Covered comment leaders: // (Go/TS/JS/Rust/C#/Java/C++),
# # (Python/Ruby/shell/YAML), /* ... */ (C-family block), <!-- ... --> (HTML/
# XML/Vue), -- (SQL/Lua/Haskell), * (block-comment continuation lines).
# Anything else that still says "DICT:" is surfaced in unparsed_annotations
# rather than silently dropped.

ANN_RE = re.compile(r'(?://|<!--|/\*|#|--|\*)\s*DICT:\s*(.*)$')
ID_FULL = re.compile(STRICT + r'$')

def parse_annotation_tail(tail):
    """Leading comma/whitespace-separated ID tokens; stop at the first
    non-ID token (trailing prose after an em-dash is tolerated)."""
    tail = re.sub(r'(-->|\*/)\s*$', '', tail.strip()).strip()
    ids = []
    for part in re.split(r'[,\s]+', tail):
        if not part: continue
        if ID_FULL.fullmatch(part):
            ids.append(part)
        else:
            break
    return ids

def scan_annotations(root):
    annotations, unparsed = [], []
    files_scanned = 0
    for path, ext in walk_source(root):
        if ext not in SOURCE_EXTS: continue
        text = read_text(path)
        if text is None: continue
        files_scanned += 1
        rel = os.path.relpath(path, root)
        for i, line in enumerate(text.splitlines(), 1):
            if 'DICT:' not in line: continue
            m = ANN_RE.search(line)
            ids = parse_annotation_tail(m.group(1)) if m else []
            if ids:
                for tok in ids:
                    annotations.append({
                        'id': tok, 'file': rel, 'line': i,
                        'registered_prefix': id_kind(tok) in REGISTERED_PREFIXES,
                    })
            else:
                unparsed.append({'file': rel, 'line': i, 'text': line.strip()[:160]})
    annotations.sort(key=lambda a: (a['file'], a['line'], a['id']))
    unparsed.sort(key=lambda a: (a['file'], a['line']))
    return annotations, unparsed, files_scanned

# ---------- structural interface artifacts (OpenAPI / JSON Schema)
# Stack-light by design: only build-emitted or committed machine-readable
# artifacts are parsed in this first cut. Per-stack AST/route extractors can
# be added later as further families under "interfaces" with the same
# endpoint/schema shapes.

HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}

def _extract_openapi(doc, source):
    endpoints = []
    paths = doc.get('paths') or {}
    if isinstance(paths, dict):
        for path, ops in paths.items():
            if not isinstance(ops, dict): continue
            for method, op in ops.items():
                if str(method).lower() in HTTP_METHODS:
                    endpoints.append({
                        'method': str(method).upper(), 'path': str(path),
                        'operation_id': (op or {}).get('operationId') if isinstance(op, dict) else None,
                    })
    schemas = []
    comps = ((doc.get('components') or {}).get('schemas')
             if isinstance(doc.get('components'), dict) else None) or doc.get('definitions') or {}
    if isinstance(comps, dict):
        for name, sch in comps.items():
            sch = sch if isinstance(sch, dict) else {}
            props = sch.get('properties') or {}
            schemas.append({
                'name': str(name),
                'fields': sorted(props) if isinstance(props, dict) else [],
                'required': sorted(x for x in (sch.get('required') or []) if isinstance(x, str)),
            })
    endpoints.sort(key=lambda e: (e['path'], e['method']))
    schemas.sort(key=lambda s: s['name'])
    return {'source': source, 'endpoints': endpoints, 'schemas': schemas}

def _extract_json_schema(doc, source):
    props = doc.get('properties') or {}
    name = doc.get('title') or os.path.splitext(os.path.basename(source))[0].replace('.schema', '')
    return {
        'source': source, 'name': str(name),
        'fields': sorted(props) if isinstance(props, dict) else [],
        'required': sorted(x for x in (doc.get('required') or []) if isinstance(x, str)),
    }

def scan_interfaces(root):
    openapi, json_schema = [], []
    for path, ext in walk_source(root):
        rel = os.path.relpath(path, root)
        if ext == '.json':
            text = read_text(path)
            if not text: continue
            probe = ('"openapi"' in text or '"swagger"' in text or '"$schema"' in text
                     or rel.endswith('.schema.json'))
            if not probe: continue
            try:
                doc = json.loads(text)
            except ValueError:
                continue
            if not isinstance(doc, dict): continue
            if 'openapi' in doc or 'swagger' in doc:
                openapi.append(_extract_openapi(doc, rel))
            elif '$schema' in doc or rel.endswith('.schema.json'):
                json_schema.append(_extract_json_schema(doc, rel))
        elif ext in ('.yaml', '.yml'):
            text = read_text(path)
            if not text: continue
            if not re.search(r'^\s*(openapi|swagger)\s*:', text, re.M): continue
            doc = parse_yaml_subset(text)   # the plain YAML subset only (documented limit)
            if isinstance(doc, dict) and ('openapi' in doc or 'swagger' in doc):
                openapi.append(_extract_openapi(doc, rel))
    openapi.sort(key=lambda a: a['source'])
    json_schema.sort(key=lambda a: a['source'])
    return {'openapi': openapi, 'json_schema': json_schema}

# ---------- config-key surface (HEURISTIC)

ENV_PATTERNS = [
    (re.compile(r'os\.environ\.get\(\s*[\'"]([A-Z][A-Z0-9_]*)[\'"]'), 'os.environ.get'),
    (re.compile(r'os\.environ\[\s*[\'"]([A-Z][A-Z0-9_]*)[\'"]\s*\]'), 'os.environ[]'),
    (re.compile(r'os\.getenv\(\s*[\'"]([A-Z][A-Z0-9_]*)[\'"]'), 'os.getenv'),
    (re.compile(r'process\.env\.([A-Z][A-Z0-9_]*)'), 'process.env'),
    (re.compile(r'process\.env\[[\'"]([A-Z][A-Z0-9_]*)[\'"]\]'), 'process.env[]'),
    (re.compile(r'os\.Getenv\(\s*"([A-Z][A-Z0-9_]*)"'), 'os.Getenv'),
    (re.compile(r'os\.LookupEnv\(\s*"([A-Z][A-Z0-9_]*)"'), 'os.LookupEnv'),
    (re.compile(r'(?:std::)?env::var(?:_os)?\(\s*"([A-Z][A-Z0-9_]*)"'), 'env::var'),
    (re.compile(r'Environment\.GetEnvironmentVariable\(\s*"([A-Z][A-Z0-9_]*)"'), 'GetEnvironmentVariable'),
    (re.compile(r'System\.getenv\(\s*"([A-Z][A-Z0-9_]*)"'), 'System.getenv'),
]

def scan_config_keys(root):
    keys = []
    for path, ext in walk_source(root):
        if ext not in SOURCE_EXTS or ext in ('.yaml', '.yml', '.html', '.htm', '.css', '.sql'):
            continue
        text = read_text(path)
        if text is None: continue
        rel = os.path.relpath(path, root)
        for i, line in enumerate(text.splitlines(), 1):
            for rx, label in ENV_PATTERNS:
                for m in rx.finditer(line):
                    keys.append({'name': m.group(1), 'file': rel, 'line': i, 'pattern': label})
    keys.sort(key=lambda k: (k['name'], k['file'], k['line']))
    return {'heuristic': True, 'keys': keys}

# ---------- assembly

def build_code_map(root):
    root = os.path.abspath(root)
    annotations, unparsed, files_scanned = scan_annotations(root)
    return {
        'tool': 'dictum-code-map',
        'schema_version': SCHEMA_VERSION,
        'root': root,
        # Determinism tiers (the research question this tool answers): which
        # sections are CERTAIN, under which stated precondition, and which are
        # heuristic. Downstream tools must never let a heuristic section drive
        # a hard (exit-code) finding.
        'tiers': {
            'annotations': {'tier': 'certain',
                            'precondition': 'the in-code `DICT: <ID>` annotation convention; '
                                            'a non-conforming annotation is DECLINED into unparsed_annotations, never guessed'},
            'interfaces': {'tier': 'certain',
                           'precondition': 'a committed/build-emitted machine-readable artifact exists '
                                           '(OpenAPI JSON / plain-YAML-subset, JSON Schema); no artifact -> no claim'},
            'config_keys': {'tier': 'heuristic',
                            'precondition': 'regex over source; inventory only, never a finding'},
        },
        'annotations': annotations,
        'unparsed_annotations': unparsed,
        'interfaces': scan_interfaces(root),
        'config_keys': scan_config_keys(root),
        'stats': {'files_scanned': files_scanned},
    }

def main():
    args = [a for a in sys.argv[1:]]
    out_file = None
    if '--out' in args:
        i = args.index('--out')
        try:
            out_file = args[i + 1]
        except IndexError:
            print('usage: dictum-code-map.py <repo-root> [--out FILE]', file=sys.stderr)
            sys.exit(2)
        del args[i:i + 2]
    if len(args) != 1 or args[0].startswith('-'):
        print('usage: dictum-code-map.py <repo-root> [--out FILE]', file=sys.stderr)
        sys.exit(2)
    root = args[0]
    if not os.path.isdir(root):
        print(f'error: not a directory: {root}', file=sys.stderr)
        sys.exit(2)
    doc = build_code_map(root)
    text = json.dumps(doc, indent=2, sort_keys=True)
    if out_file:
        open(out_file, 'w', encoding='utf-8').write(text + '\n')
    else:
        print(text)

if __name__ == '__main__':
    main()
