#!/usr/bin/env python3
"""dictum-reverse-extract — deterministic reverse-extraction (Part 10f backend). EXPERIMENTAL.

Zero-dependency (Python 3 stdlib only). The mechanically-decidable slice of the
standard's code-cartographer flow (STANDARD Part 10f; model A is the advisory
LLM agent agents/code-cartographer.md). From a repo path (via the code-map
backend) it emits three DRAFT artifacts:

  candidate-inventory.json   candidate contracts: IDs RECOVERED from in-code
                             DICT annotations (identity certain under the
                             convention) + candidates COINED from interface
                             artifacts (structure certain over the artifact,
                             identity coined) — every entry [ASSUMPTION]
  bindings.draft.yaml        a DRAFT binding map in the standard's template
                             shape (never validated: nothing is Contract-grade)
  recoverability-report.md   what deterministic extraction can NOT recover —
                             the loud declines mirroring Part 10f's
                             recoverability partition

A research instrument, not a product: it recovers identity and artifact
structure with certainty and DECLINES everything else (intent, non-goals,
CAP groupings, delivered-vs-aspirational) rather than guessing — model A
drafts those for confirmation; model B cannot.

Exit code: 0 on success, 2 on usage error.

Non-normative: the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.
"""
import os, re, sys, json, importlib.util

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', 'common'))
from dictumlib import id_kind

SCHEMA_VERSION = 1

def _load_code_map_module():
    p = os.path.join(_HERE, '..', 'code-map', 'dictum-code-map.py')
    spec = importlib.util.spec_from_file_location('dictum_code_map', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ---------- heuristic symbol sniff (marked as such in output)

SYM_RES = [
    re.compile(r'^\s*(?:export\s+)?(?:async\s+)?(?:def|class|function|interface|type|const|let|var)\s+([A-Za-z_]\w*)'),
    re.compile(r'^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)'),
    re.compile(r'^\s*(?:pub\s+)?(?:fn|struct|enum|trait)\s+([A-Za-z_]\w*)'),
    re.compile(r'^\s*(?:public|private|internal|protected)?\s*(?:static\s+)?(?:class|interface|record|void|int|string)\s+([A-Za-z_]\w*)'),
]

def sniff_symbol(root, path, line):
    try:
        lines = open(os.path.join(root, path), encoding='utf-8', errors='replace').read().splitlines()
    except OSError:
        return None
    for cand in lines[line - 1:line + 3]:   # the annotation line + the next 3
        for rx in SYM_RES:
            m = rx.match(cand)
            if m: return m.group(1)
    return None

# ---------- coined IDs (deterministic)

def coin_api_id(method, path):
    segs = [s.strip('{}').strip(':') for s in path.strip('/').split('/') if s]
    slug = '-'.join(re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').upper() for s in segs) or 'ROOT'
    return f'API-{method.upper()}-{slug}'

def coin_entity_id(name):
    slug = re.sub(r'[^A-Za-z0-9]+', '-', re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '-', name)).strip('-').upper()
    return f'ENTITY-{slug}'

# ---------- extraction

def extract(root, codemap):
    candidates = {}
    for a in codemap.get('annotations') or []:
        c = candidates.setdefault(a['id'], {
            'id': a['id'], 'kind': id_kind(a['id']), 'provenance': 'recovered',
            'assumption': True,
            'confidence': 'identity certain under the in-code DICT convention; meaning unconfirmed',
            'evidence': [], 'locators': [],
        })
        sym = sniff_symbol(root, a['file'], a['line'])
        c['evidence'].append(f"in-code annotation {a['file']}:{a['line']}")
        c['locators'].append({'path': a['file'], 'line': a['line'],
                              'symbol': sym, 'symbol_tier': 'heuristic' if sym else None})
    coined = {}
    for art in (codemap.get('interfaces') or {}).get('openapi') or []:
        for ep in art['endpoints']:
            cid = coin_api_id(ep['method'], ep['path'])
            ev = f"artifact {art['source']} `{ep['method']} {ep['path']}`"
            if cid in candidates:
                candidates[cid]['evidence'].append(ev)
                candidates[cid]['provenance'] = 'recovered+artifact'
            else:
                c = coined.setdefault(cid, {
                    'id': cid, 'kind': 'API', 'provenance': 'coined', 'assumption': True,
                    'confidence': 'structure certain over the artifact; the ID itself is coined '
                                  '(re-adoption must reconcile it — Part 10f)',
                    'evidence': [], 'locators': []})
                c['evidence'].append(ev)
        for s in art['schemas']:
            cid = coin_entity_id(s['name'])
            ev = f"artifact {art['source']} schema `{s['name']}` fields={s['fields']}"
            if cid in candidates:
                candidates[cid]['evidence'].append(ev)
                candidates[cid]['provenance'] = 'recovered+artifact'
            else:
                c = coined.setdefault(cid, {
                    'id': cid, 'kind': 'ENTITY', 'provenance': 'coined', 'assumption': True,
                    'confidence': 'structure certain over the artifact; the ID itself is coined '
                                  '(re-adoption must reconcile it — Part 10f)',
                    'evidence': [], 'locators': []})
                c['evidence'].append(ev)
    for js in (codemap.get('interfaces') or {}).get('json_schema') or []:
        cid = coin_entity_id(js['name'])
        ev = f"artifact {js['source']} (JSON Schema) fields={js['fields']}"
        if cid in candidates:
            candidates[cid]['evidence'].append(ev)
            candidates[cid]['provenance'] = 'recovered+artifact'
        elif cid in coined:
            coined[cid]['evidence'].append(ev)
        else:
            c = coined.setdefault(cid, {
                'id': cid, 'kind': 'ENTITY', 'provenance': 'coined', 'assumption': True,
                'confidence': 'structure certain over the artifact; the ID itself is coined '
                              '(re-adoption must reconcile it — Part 10f)',
                'evidence': [], 'locators': []})
            c['evidence'].append(ev)
    return candidates, coined

DECLINED = [
    'intent: why each capability exists; personas; success metrics (interview)',
    'Non-goals & scope-out kinds — categorically: code cannot distinguish '
    '"deliberately excluded" from "not built yet" (Part 9 / Part 10f)',
    'threat model / security policy; UX journeys, states, design intent; '
    'performance targets / SLAs; governance & compliance; business & legal',
    'CAP-### groupings: a capability boundary is an intent judgment — model A '
    'proposes them at low confidence; model B declines entirely',
    'delivered-vs-aspirational adjudication (structure-without-behavior needs '
    'reachability analysis: undecided-yet, per-stack AST work)',
    'correlating a coined artifact candidate with a recovered annotated ID '
    '(e.g. an endpoint vs the handler annotation) needs route-to-handler '
    'resolution: undecided-yet, per-stack AST work',
]

# ---------- rendering

def render_inventory(root, candidates, coined, codemap):
    inv = {
        'tool': 'dictum-reverse-extract', 'schema_version': SCHEMA_VERSION, 'root': root,
        'status': 'DRAFT — every candidate is an [ASSUMPTION] until the doc-excavate '
                  'confirm-and-fill interview confirms it (STANDARD Part 10f); '
                  'no rung and no Verified claim is made',
        'candidates': sorted(candidates.values(), key=lambda c: c['id']),
        'coined_candidates': sorted(coined.values(), key=lambda c: c['id']),
        'unparsed_annotations': codemap.get('unparsed_annotations') or [],
        'config_key_surface': {
            'tier': 'heuristic',
            'note': 'candidate PROSE for the ENV-### fidelity map / a parked CONFIG-### kind '
                    '(dictum ROADMAP) — never minted as contracts here',
            'keys': sorted({k['name'] for k in (codemap.get('config_keys') or {}).get('keys') or []}),
        },
        'declined': DECLINED,
    }
    return json.dumps(inv, indent=2, sort_keys=True)

def render_bindings(candidates, coined):
    out = [
        '# bindings.draft.yaml — DRAFT (reverse-extracted, STANDARD Part 10f).',
        '# NOT a validated binding map: nothing is Contract-grade yet, the doc set it',
        '# binds does not exist yet, and every entry is an [ASSUMPTION] until the',
        '# doc-excavate interview confirms it. Symbols are heuristic sniffs — verify.',
        'bindings:',
        '',
    ]
    for c in sorted(candidates.values(), key=lambda c: c['id']):
        out.append(f"  {c['id']}:{' ':<{max(1, 24 - len(c['id']))}}# [ASSUMPTION] {c['provenance']} — confirm in interview")
        out.append('    locators:')
        for loc in c['locators']:
            if loc['symbol']:
                out.append(f"      - {{ path: {loc['path']}, symbol: {loc['symbol']} }}   # line {loc['line']}; symbol is a heuristic sniff")
            else:
                out.append(f"      - {{ path: {loc['path']} }}   # line {loc['line']}; symbol unrecovered — confirm")
        out.append('')
    if coined:
        out.append('  # Coined artifact candidates — no code locator recoverable without')
        out.append('  # per-stack AST extraction (declined); bind after the interview:')
        for c in sorted(coined.values(), key=lambda c: c['id']):
            out.append(f"  # {c['id']}:   # coined from {c['evidence'][0]}")
        out.append('')
    return '\n'.join(out)

def render_report(root, candidates, coined, codemap):
    nrec = len(candidates)
    ncoin = len(coined)
    nunp = len(codemap.get('unparsed_annotations') or [])
    nkeys = len({k['name'] for k in (codemap.get('config_keys') or {}).get('keys') or []})
    lines = [
        '# Reverse-extraction recoverability report — DRAFT',
        '',
        '> **[ASSUMPTION]-laden by construction** (STANDARD Part 10f): every candidate',
        '> is provisional until the doc-excavate confirm-and-fill interview confirms',
        '> it. This is raw material for a faithful BASELINE — never build-ready; no',
        '> rung and no Verified claim is made (Verified is Delivery\'s, Part 3).',
        '',
        '## Extracted — the certain surface, each under its stated precondition',
        '',
        f'- **{nrec} recovered** contract ID(s) from in-code `DICT:` annotations — identity',
        '  is certain under the annotation convention; *meaning* is not (confirm track).',
        f'- **{ncoin} coined** candidate(s) from machine-readable interface artifacts',
        '  (OpenAPI / JSON Schema) — structure is certain over the artifact; the ID is',
        '  coined, so any correspondence with a prior authoring must go through the',
        '  Part 10f ID-reconciliation step (tombstone-alias + roll-up), never assumed.',
        f'- **{nunp} unparsed annotation(s)** declined loudly (see the inventory), never guessed.',
        f'- **{nkeys} config key(s)** — heuristic tier only: candidate prose for the `ENV-###`',
        '  fidelity map (or a future CONFIG-### kind, parked in the dictum ROADMAP);',
        '  never minted as contracts here.',
        '',
        '## Not recoverable deterministically — declined, must interview',
        '',
        'Mirrors the Part 10f recoverability partition. Model A (the code-cartographer',
        'agent) *drafts* the partially-derivable intent halves for confirmation; model B',
        'declines them outright:',
        '',
    ]
    lines += [f'- {d}' for d in DECLINED]
    lines += [
        '',
        '## Next step',
        '',
        'Hand to `doc-excavate` (Part 10f): the confirm track replays each extracted',
        'inference; the fill track interviews the declined list to saturation. The',
        'draft binding map is finalized only after IDs are confirmed.',
    ]
    return '\n'.join(lines) + '\n'

def main():
    args = sys.argv[1:]
    out_dir = None
    if '--out' in args:
        i = args.index('--out')
        try:
            out_dir = args[i + 1]
        except IndexError:
            print('usage: dictum-reverse-extract.py <repo-root> [--out DIR]', file=sys.stderr)
            sys.exit(2)
        del args[i:i + 2]
    if len(args) != 1 or args[0].startswith('-'):
        print('usage: dictum-reverse-extract.py <repo-root> [--out DIR]', file=sys.stderr)
        sys.exit(2)
    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print(f'error: not a directory: {root}', file=sys.stderr)
        sys.exit(2)
    codemap = _load_code_map_module().build_code_map(root)
    candidates, coined = extract(root, codemap)
    artifacts = {
        'candidate-inventory.json': render_inventory(root, candidates, coined, codemap) + '\n',
        'bindings.draft.yaml': render_bindings(candidates, coined) + '\n',
        'recoverability-report.md': render_report(root, candidates, coined, codemap),
    }
    if out_dir:
        if os.path.abspath(out_dir) == root:
            print('error: refusing to write into the scanned repo root (the flow reads code, '
                  'writes drafts elsewhere)', file=sys.stderr)
            sys.exit(2)
        os.makedirs(out_dir, exist_ok=True)
        for name, text in artifacts.items():
            open(os.path.join(out_dir, name), 'w', encoding='utf-8').write(text)
        print(f'wrote {", ".join(sorted(artifacts))} to {out_dir}')
    else:
        for name in ('candidate-inventory.json', 'bindings.draft.yaml', 'recoverability-report.md'):
            print(f'=== {name} ===')
            print(artifacts[name])

if __name__ == '__main__':
    main()
