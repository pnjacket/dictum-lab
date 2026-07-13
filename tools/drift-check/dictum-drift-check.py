#!/usr/bin/env python3
"""dictum-drift-check — deterministic (model B) code<->doc drift checks. EXPERIMENTAL.

Zero-dependency (Python 3 stdlib only). The mechanically-decidable slice of the
standard's drift-detector (STANDARD Part 10d; model A is the advisory LLM agent
agents/drift-detector.md). A research instrument, not a product: every finding
carries a determinism TIER, only `certain`-tier ERRORs drive the exit code, and
where a comparison is not decidable the tool DECLINES LOUDLY (INFO
`not-decidable`) instead of guessing.

Inputs: a doc set (manifest + docs + binding map, the layout gate-check
consumes) and a code-map inventory (tools/code-map), built on the fly from
--repo (default: the doc-set root) or loaded from --map FILE.

Checks:
  binding-stale      locator path/line no longer exists (certain);
                     symbol probe absent (heuristic -> WARN only)
  doc-end            binding key resolves to no register-form definition /
                     to a tombstone; premature binding (sub-Contract-grade)
  doc-ahead-unbuilt  binding records NO code evidence at all while the map's
                     presence claims realization (certain)
  code-ahead         in-code DICT annotation absent from the doc ID web
  route-diff         OpenAPI endpoints vs owned API/ROUTE register lines
                     (certain, only where an artifact exists)
  schema-diff        OpenAPI/JSON-Schema entities vs ENTITY contracts
                     (certain only under a binding's `compare_via: openapi`)
  coverage-gap       unbound in-scope Contract-grade code-realizable contract
                     (WARN — the legitimate build-new signal, Part 10e)

Exit code: 0 clean · 1 any (certain) ERROR finding · 2 usage or parse error.
(gate-check's convention is 0/1; the explicit 2 tier is this tool's addition.)

Non-normative: the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.
"""
import os, re, sys, json, importlib.util

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', 'common'))
from dictumlib import (load_docset, IdWeb, STRICT, id_kind,
                       CODE_REALIZABLE_KINDS)

CG_RUNGS = {'contract-grade', 'verified'}
STRICT_FULL = re.compile(STRICT + r'$')

def _load_code_map_module():
    p = os.path.join(_HERE, '..', 'code-map', 'dictum-code-map.py')
    spec = importlib.util.spec_from_file_location('dictum_code_map', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ---------- findings

FINDINGS = []   # dicts: severity, tier, category, where, msg, id, direction

def finding(sev, tier, cat, where, msg, id=None, direction=None):
    FINDINGS.append({'severity': sev, 'tier': tier, 'category': cat,
                     'where': where, 'msg': msg, 'id': id, 'direction': direction})

# ---------- doc-side helpers

def rung_info(web, docmeta, manifest, tok):
    """(in_scope, rung) of the concern owning tok; (None, None) if unknowable."""
    info = web.owned.get(tok)
    if not info or info['file'] == 'manifest:tombstone':
        return None, None
    fm, _ = docmeta.get(info['file'], ({}, ''))
    cid = fm.get('concern-id')
    c = ((manifest.get('concerns') or {}).get(cid) or {}) if cid else {}
    if isinstance(c, dict) and c:
        return bool(c.get('in_scope')), c.get('current_rung')
    return None, fm.get('current-rung')

ROUTE_LINE_RE = re.compile(r'\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[^\s`,)]*)')

def norm_path(p):
    p = re.sub(r'\{[^}]*\}', '{}', p)
    p = re.sub(r':[A-Za-z_][A-Za-z0-9_]*', '{}', p)
    return p.rstrip('/') or '/'

def norm_name(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

# ---------- the run

def run(root, codemap):
    ds = load_docset(root)
    if not ds['manifest_path']:
        print(f'error: no manifest.yaml found under {root}', file=sys.stderr)
        sys.exit(2)
    manifest = ds['manifest'] or {}
    docmeta = ds['docmeta']
    tombs = set((manifest.get('tombstones') or {}) if isinstance(manifest.get('tombstones'), dict) else [])
    stale = set((manifest.get('staleness') or {}) if isinstance(manifest.get('staleness'), dict) else [])
    web = IdWeb(docmeta, tombstones=tombs)
    b = ds['bindings'] or {}
    bmap = b.get('bindings') if isinstance(b.get('bindings'), dict) else {}
    cov = b.get('coverage') if isinstance(b.get('coverage'), dict) else {}
    rel_b = os.path.relpath(ds['bindings_path'], root) if ds['bindings_path'] else 'bindings.yaml'

    def suppressed(tok, cat, where, msg):
        if tok in stale:
            finding('INFO', 'certain', 'suppressed', where,
                    f'[{cat}] {msg} — suppressed: contract already flagged stale in the manifest (Part 10d)', id=tok)
            return True
        return False

    # Reverse-authored baseline mode (Part 10f / drift-detector agent): roll up
    # premature-binding warnings when nothing is Contract-grade yet.
    prov = manifest.get('provenance') if isinstance(manifest.get('provenance'), dict) else {}
    any_cg = any(isinstance(c, dict) and c.get('in_scope') and c.get('current_rung') in CG_RUNGS
                 for c in (manifest.get('concerns') or {}).values())
    baseline = prov.get('authored') == 'reverse-from-code' and not any_cg
    premature = []

    # --- bindings: doc end + code end + unbuilt
    have_asserted_by = False
    for key, v in sorted(bmap.items()):
        v = v if isinstance(v, dict) else {}
        where = f'{rel_b}::{key}'
        # doc end
        if key in tombs:
            finding('ERROR', 'certain', 'doc-end', where,
                    'binding key is tombstoned — the binding must be dropped on retirement', id=key)
        elif not web.resolves(key):
            if key in web.mentioned:
                finding('WARN', 'heuristic', 'doc-end', where,
                        'binding key found only as an inline mention, not a register-form definition (inline mint)', id=key)
            else:
                finding('ERROR', 'certain', 'doc-end', where,
                        'binding key resolves to no owning register-form definition', id=key)
        else:
            in_scope, rung = rung_info(web, docmeta, manifest, key)
            if rung is not None and rung not in CG_RUNGS:
                premature.append((key, where, rung))
        # code end
        locs = v.get('locators') or []
        abys = v.get('asserted_by') or []
        if abys: have_asserted_by = True
        evidence = 0
        for loc in list(locs) + list(abys):
            if not isinstance(loc, dict): continue
            path, sym, line = loc.get('path'), loc.get('symbol'), loc.get('line')
            if not path: continue
            fs = os.path.join(root, path)
            if not os.path.exists(fs):
                finding('ERROR', 'certain', 'binding-stale', where,
                        f'locator path missing: {path}', id=key)
                continue
            if line is not None and os.path.isfile(fs):
                try:
                    n = str(line)
                    nlines = sum(1 for _ in open(fs, encoding='utf-8', errors='replace'))
                    if n.isdigit() and int(n) > nlines:
                        finding('ERROR', 'certain', 'binding-stale', where,
                                f'locator line {n} beyond end of {path} ({nlines} lines)', id=key)
                        continue
                except OSError:
                    pass
            evidence += 1
            if sym and ' ' not in str(sym) and os.path.isfile(fs):
                probe = str(sym).split('.')[-1]
                if probe not in open(fs, encoding='utf-8', errors='replace').read():
                    finding('WARN', 'heuristic', 'binding-stale', where,
                            f'symbol `{sym}` (substring probe `{probe}`) not found in {path}', id=key)
        if not locs and not abys:
            if not suppressed(key, 'doc-ahead-unbuilt', where,
                              'bound but no code evidence recorded'):
                finding('ERROR', 'certain', 'doc-ahead-unbuilt', where,
                        'binding records no code evidence at all (no locators, no asserted_by) — '
                        'the map claims realization (Part 10d), the code side is absent',
                        id=key, direction='doc-ahead')

    if premature:
        if baseline:
            finding('INFO', 'certain', 'doc-end', rel_b,
                    f'all {len(premature)} binding(s) premature — expected for a reverse-authored '
                    'baseline (no concern Contract-grade yet); not repeated per binding')
        else:
            for key, where, rung in premature:
                finding('WARN', 'certain', 'doc-end', where,
                        f'premature binding: owning concern at rung `{rung}` (sub-Contract-grade)', id=key)

    if have_asserted_by:
        finding('INFO', 'certain', 'not-decidable', rel_b,
                'INV assertion execution declined: `run:` selectors are CI-executable evidence, '
                'not this checker\'s to run (a failing assertion is model A / CI territory)')

    # --- coverage (certain arithmetic; rung- and scope-gated; honors coverage:)
    fully = set(cov.get('fully_bound') or [])
    curated = cov.get('curated') if isinstance(cov.get('curated'), dict) else {}
    for tok in sorted(web.owned):
        if '*' in tok or not STRICT_FULL.fullmatch(tok): continue
        if tok in tombs: continue
        kind = id_kind(tok)
        if kind not in CODE_REALIZABLE_KINDS: continue
        if kind in curated: continue          # curated = intentional partial (declared)
        in_scope, rung = rung_info(web, docmeta, manifest, tok)
        if in_scope is not True or rung not in CG_RUNGS: continue
        if tok not in bmap:
            info = web.owned[tok]
            finding('WARN', 'certain', 'coverage-gap', f"{info['file']}:{info['line']}",
                    f'`{tok}` is in-scope, Contract-grade and code-realizable but unbound — '
                    'drift is undetectable here; the forward flow reads this as build-new (Part 10e)',
                    id=tok, direction='doc-ahead')

    # --- code-ahead: in-code annotations vs the ID web
    ann_by_id = {}
    for a in codemap.get('annotations') or []:
        ann_by_id.setdefault(a['id'], []).append(f"{a['file']}:{a['line']}")
    for tok in sorted(ann_by_id):
        sites = ann_by_id[tok]
        where = sites[0] + (f' (+{len(sites)-1} more)' if len(sites) > 1 else '')
        if tok in tombs:
            if not suppressed(tok, 'code-ahead', where, 'annotates tombstoned contract'):
                finding('ERROR', 'certain', 'code-ahead', where,
                        f'code still annotates retired (tombstoned) contract `{tok}`',
                        id=tok, direction='code-ahead')
        elif not web.resolves(tok):
            if tok in web.mentioned:
                finding('WARN', 'heuristic', 'code-ahead', where,
                        f'annotated ID `{tok}` resolves only to an inline mention (inline mint) — '
                        'undecidable under the register-form convention', id=tok)
            elif not suppressed(tok, 'code-ahead', where, 'annotated ID absent from ID web'):
                finding('ERROR', 'certain', 'code-ahead', where,
                        f'in-code annotation `{tok}` is absent from the doc set\'s ID web '
                        '(code-ahead drift: the code realizes a contract no doc owns)',
                        id=tok, direction='code-ahead')
    if codemap.get('unparsed_annotations'):
        n = len(codemap['unparsed_annotations'])
        first = codemap['unparsed_annotations'][0]
        finding('WARN', 'heuristic', 'code-ahead', f"{first['file']}:{first['line']}",
                f'{n} unparsed DICT annotation(s) in code (unsupported syntax or non-grammar ID) — '
                'not comparable; fix the annotation (see code-map unparsed_annotations)')

    # --- interface artifacts vs owned contracts
    arts = (codemap.get('interfaces') or {}).get('openapi') or []
    jschemas = (codemap.get('interfaces') or {}).get('json_schema') or []
    if not arts and not jschemas:
        finding('INFO', 'certain', 'not-decidable', '(repo)',
                'interface comparison not attempted: no machine-readable interface artifact '
                '(OpenAPI / JSON Schema) found — endpoint/entity drift is undecidable for '
                'model B without one (or per-stack extractors, not in this cut)')
    else:
        # doc-side routes: `METHOD /path` stated on the owning register line
        doc_routes, undeclared = {}, []
        for tok in sorted(web.owned):
            if '*' in tok or not STRICT_FULL.fullmatch(tok): continue
            if id_kind(tok) not in ('API', 'ROUTE') or tok in tombs: continue
            info = web.owned[tok]
            if info['file'] == 'manifest:tombstone' or '[FUTURE-SCOPE]' in info['text']: continue
            m = ROUTE_LINE_RE.search(info['text'])
            if m:
                doc_routes[(m.group(1), norm_path(m.group(2)))] = tok
            else:
                undeclared.append(tok)
        code_eps = {}
        for art in arts:
            for ep in art['endpoints']:
                code_eps.setdefault((ep['method'], norm_path(ep['path'])), art['source'])
        if arts:
            for (meth, path), src in sorted(code_eps.items()):
                if (meth, path) not in doc_routes:
                    finding('ERROR', 'certain', 'route-diff', src,
                            f'artifact endpoint `{meth} {path}` has no owning API/ROUTE contract '
                            'stating that route in the doc set', direction='code-ahead')
            for (meth, path), tok in sorted(doc_routes.items()):
                if tok not in bmap: continue          # unbound = build-new, not drift
                in_scope, rung = rung_info(web, docmeta, manifest, tok)
                if rung is not None and rung not in CG_RUNGS: continue
                if (meth, path) not in code_eps:
                    if not suppressed(tok, 'route-diff', web.owned[tok]['file'],
                                      f'`{meth} {path}` missing from artifact'):
                        finding('ERROR', 'certain', 'route-diff',
                                f"{web.owned[tok]['file']}:{web.owned[tok]['line']}",
                                f'`{tok}` states `{meth} {path}` and is bound as built, but no '
                                'artifact endpoint matches', id=tok, direction='doc-ahead')
        if undeclared:
            finding('INFO', 'certain', 'not-decidable', '(docs)',
                    f'route comparison declined for {len(undeclared)} API/ROUTE contract(s) whose '
                    f'register line states no `METHOD /path`: {", ".join(undeclared)}')

        # entities: certain only under a binding's compare_via: openapi declaration
        schema_names = {}
        for art in arts:
            for s in art['schemas']:
                schema_names.setdefault(norm_name(s['name']), (s['name'], art['source']))
        for js in jschemas:
            schema_names.setdefault(norm_name(js['name']), (js['name'], js['source']))
        declined_fields = []
        for key, v in sorted(bmap.items()):
            v = v if isinstance(v, dict) else {}
            if v.get('compare_via') != 'openapi' or id_kind(key) != 'ENTITY': continue
            if norm_name(key[len('ENTITY-'):]) not in schema_names:
                if not suppressed(key, 'schema-diff', f'{rel_b}::{key}', 'no artifact schema matches'):
                    finding('ERROR', 'certain', 'schema-diff', f'{rel_b}::{key}',
                            f'binding declares `compare_via: openapi` but no artifact schema matches '
                            f'`{key}`', id=key, direction='doc-ahead')
            else:
                declined_fields.append(key)
        owned_entities = {norm_name(tok[len('ENTITY-'):]) for tok in web.owned
                          if STRICT_FULL.fullmatch(tok) and id_kind(tok) == 'ENTITY' and '*' not in tok}
        for nm, (name, src) in sorted(schema_names.items()):
            if nm not in owned_entities:
                finding('WARN', 'heuristic', 'schema-diff', src,
                        f'artifact schema `{name}` matches no owned ENTITY contract '
                        '(name-normalization join — heuristic)', direction='code-ahead')
        if declined_fields:
            finding('INFO', 'certain', 'not-decidable', rel_b,
                    f'field-level comparison declined for {len(declined_fields)} entity binding(s) '
                    f'({", ".join(declined_fields)}): doc-side field lists are prose — undecidable '
                    'without a doc-side machine-readable convention')

# ---------- output

def emit(as_json):
    order = {'ERROR': 0, 'WARN': 1, 'INFO': 2}
    fs = sorted(FINDINGS, key=lambda f: (order[f['severity']], f['category'], f['where']))
    errs = sum(1 for f in fs if f['severity'] == 'ERROR')
    warns = sum(1 for f in fs if f['severity'] == 'WARN')
    infos = sum(1 for f in fs if f['severity'] == 'INFO')
    if as_json:
        events = [{'id': f['id'], 'source': 'drift', 'classification': 'proposed',
                   'ref': 'WORKING-TREE', 'direction': f['direction'],
                   'by': f['category'], 'evidence': f['msg'], 'adjudication': 'pending'}
                  for f in fs if f['severity'] == 'ERROR' and f['direction']]
        print(json.dumps({'tool': 'dictum-drift-check', 'findings': fs,
                          'candidate_change_events': events,
                          'counts': {'error': errs, 'warn': warns, 'info': infos}},
                         indent=2, sort_keys=True))
    else:
        for f in fs:
            print(f"{f['severity']:5} {f['tier']:9} [{f['category']:17}] {f['where']} — {f['msg']}")
        print(f'\n{errs} error(s), {warns} warning(s), {infos} info')
    return errs

def main():
    args = sys.argv[1:]
    as_json = '--json' in args
    if as_json: args.remove('--json')
    map_file = repo = None
    for flag in ('--map', '--repo'):
        if flag in args:
            i = args.index(flag)
            try:
                val = args[i + 1]
            except IndexError:
                val = None
            if val is None:
                print('usage: dictum-drift-check.py <docset-root> [--repo PATH | --map FILE] [--json]',
                      file=sys.stderr)
                sys.exit(2)
            if flag == '--map': map_file = val
            else: repo = val
            del args[i:i + 2]
    if len(args) != 1 or args[0].startswith('-'):
        print('usage: dictum-drift-check.py <docset-root> [--repo PATH | --map FILE] [--json]',
              file=sys.stderr)
        sys.exit(2)
    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print(f'error: not a directory: {root}', file=sys.stderr)
        sys.exit(2)
    if map_file:
        try:
            codemap = json.load(open(map_file, encoding='utf-8'))
        except (OSError, ValueError) as e:
            print(f'error: cannot read code map {map_file}: {e}', file=sys.stderr)
            sys.exit(2)
    else:
        codemap = _load_code_map_module().build_code_map(repo or root)
    run(root, codemap)
    sys.exit(1 if emit(as_json) else 0)

if __name__ == '__main__':
    main()
