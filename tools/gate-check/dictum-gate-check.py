#!/usr/bin/env python3
"""dictum-gate-check — deterministic gate checks for a Dictum doc set. EXPERIMENTAL.

Zero-dependency (stdlib only). Checks implemented:
  vocab      parse published sub-aspect keys from the vendored concern specs
  partition  manifest out-list + doc in-list == published vocabulary, disjoint
  publish    status/build-marker state vs build-ready claim / build evidence
  idweb      every referenced owned-prefix ID resolves to a definition
  bindings   binding-map keys resolve doc-end; locator paths exist; symbols grep
  markers    subject-marker vocabulary (unknown all-caps tokens -> warning)
  index      derived README lists every in-scope concern (crude consistency)

Exit code: 1 if any ERROR finding, else 0.
"""
import os, re, sys, glob

# ---------- minimal YAML-subset parser (block maps/lists, flow maps/lists, comments)

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
        # decide map or list from first line
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
                # inline "key: value" list-item map (single-line only in our corpus)
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

# ---------- findings

FINDINGS = []
def finding(sev, check, where, msg):
    FINDINGS.append((sev, check, where, msg))

# ---------- discovery

def discover(root):
    def first(*cands):
        for c in cands:
            p = os.path.join(root, c)
            if os.path.exists(p): return p
        return None
    manifest = first('docs/manifest.yaml', 'manifest.yaml')
    standard = first('dictum', 'docs/dictum', 'keystone', 'docs/keystone')
    bindings = first('docs/bindings.yaml', 'bindings.yaml')
    docs = []
    for pat in ('docs/*.md', 'docs/concerns/*.md', '*.md'):
        for p in glob.glob(os.path.join(root, pat)):
            if standard and os.path.commonpath([p, standard]) == standard: continue
            fm, _ = front_matter(p)
            if fm and 'role' in fm:
                docs.append(p)
    return manifest, standard, bindings, sorted(set(docs))

# ---------- check: vocabulary from concern specs

def load_vocab(standard):
    vocab = {}
    for spec in glob.glob(os.path.join(standard, 'concerns', '11.*.md')):
        cid = re.sub(r'^11\.\d+-', '', os.path.basename(spec))[:-3]
        keys, in_table = [], False
        for line in open(spec, encoding='utf-8'):
            if re.match(r'^##.*Sub-aspects', line): in_table = True; continue
            if in_table and line.startswith('## '): break
            if in_table:
                m = re.match(r'^\|[^|]*\|\s*`([a-z0-9-]+)`\s*\|', line)
                if m: keys.append(m.group(1))
        vocab[cid] = keys
    return vocab

# ---------- main checks

ID_RE = re.compile(r'\b([A-Z][A-Z0-9]+(?:-[A-Z0-9*]+)+[a-z]?)\b')

def run(root):
    manifest_path, standard, bindings_path, docs = discover(root)
    if not manifest_path: finding('ERROR', 'discover', root, 'no manifest.yaml found'); return
    if not standard: finding('ERROR', 'discover', root, 'no vendored standard found'); return
    manifest = parse_yaml_subset(open(manifest_path, encoding='utf-8').read()) or {}
    concerns = manifest.get('concerns') or {}
    vocab = load_vocab(standard)

    # concern docs by concern-id
    docmeta = {}
    for p in docs:
        fm, text = front_matter(p)
        docmeta[p] = (fm, text)

    concern_docs = {}
    for p, (fm, _) in docmeta.items():
        if fm.get('role') == 'concern' and fm.get('concern-id'):
            concern_docs[fm['concern-id']] = p

    # --- partition
    for cid, cfg in concerns.items():
        if not isinstance(cfg, dict) or not cfg.get('in_scope'): continue
        keys = set(vocab.get(cid) or [])
        if not keys:
            finding('WARN', 'partition', cid, 'no published key vocabulary parsed from spec'); continue
        out = set(x for x in (cfg.get('out_of_scope_subaspects') or []) if isinstance(x, str))
        dp = concern_docs.get(cid)
        ins = set()
        if dp:
            ins = set(docmeta[dp][0].get('in-scope-subaspects') or [])
        for k in out - keys: finding('ERROR', 'partition', f'{cid}', f'manifest scopes out unknown key `{k}`')
        for k in ins - keys: finding('ERROR', 'partition', f'{cid}', f'doc front-matter claims unknown key `{k}`')
        if dp:
            both = ins & out
            for k in both: finding('ERROR', 'partition', cid, f'key `{k}` both in and out of scope')
            missing = keys - ins - out
            for k in missing: finding('ERROR', 'partition', cid, f'published key `{k}` unaccounted (neither in nor out)')

    # --- publish state + claims
    build_evidence = False
    if bindings_path:
        b = parse_yaml_subset(open(bindings_path, encoding='utf-8').read()) or {}
        bmap = b.get('bindings') or {}
        if isinstance(bmap, dict):
            for v in bmap.values():
                locs = (v or {}).get('locators') if isinstance(v, dict) else None
                if locs: build_evidence = True; break
    at_target = all(
        (c.get('current_rung') == c.get('target_rung'))
        for c in concerns.values() if isinstance(c, dict) and c.get('in_scope'))
    for cid, p in concern_docs.items():
        fm, text = docmeta[p]
        status = fm.get('status')
        nmark = len(re.findall(r'<!--\s*BUILD:', text))
        ncomm = len(re.findall(r'<!--', text))
        rel = os.path.relpath(p, root)
        if status == 'published' and nmark:
            finding('ERROR', 'publish', rel, f'published doc still carries {nmark} build marker(s)')
        if (at_target or build_evidence) and status != 'published':
            why = 'build evidence exists (populated binding map)' if build_evidence else 'all in-scope concerns at target rung'
            finding('ERROR', 'publish', rel, f'publish step owed: status `{status}` but {why}')
        elif status != 'published' and nmark:
            finding('INFO', 'publish', rel, 'draft with build markers (fine pre-gate)')

    # --- id web: definitions
    owned = {}       # id -> file
    prefixes = set()
    # A definition line: heading, table row, list item, or paragraph whose lead
    # segment (before the first em-dash or end of bold) names one or more
    # backticked IDs. All IDs in the lead segment are defined by that line.
    STRICT = r'[A-Z][A-Z0-9]+(?:[-_][A-Z0-9*]+)+[a-z]?'   # ID grammar (hyphen or error-code underscore)
    ANCHOR = r'\**`?' + STRICT                              # optionally bold / backticked
    DEF_LEAD = [
        re.compile(r'^\s*#{2,5}\s+(.{0,160})$'),                           # heading (IDs on either side of an em-dash)
        re.compile(r'^\s*\|\s*(' + ANCHOR + r'.{0,250}?)\|'),              # table row, 1st cell (annotations can be long)
        re.compile(r'^\s*[-*]\s+(' + ANCHOR + r'.{0,90}?)(?:—|:|$)'),      # list item
        re.compile(r'^\s*(\*\*`?' + STRICT + r'.{0,90}?)(?:—|:)'),         # paragraph register row
        re.compile(r'^\s*[-*]\s+(\*\*`[^`]{2,60}`\*\*.{0,20}?)(?:—|:)'),   # backticked non-ID key (e.g. `GridState.version`)
        re.compile(r'^\s*(\*\*`[^`]{2,60}`\*\*\s*)(?:—|:)'),
        re.compile(r'^\s*(`' + STRICT + r'`)\s*[(:—]'),                    # bare start-of-line register key
    ]
    STRICT_RE = re.compile(r'\b(' + STRICT + r')\b')
    ANYTICK_RE = re.compile(r'`([^`\s]{2,60})`')
    OWNS_RE = re.compile(r'[Oo]wns[^.]*?`([A-Z][A-Z0-9]*)-#{2,}`')
    for p, (fm, text) in docmeta.items():
        rel = os.path.relpath(p, root)
        for line in text.splitlines():
            for r in DEF_LEAD:
                m = r.match(line)
                if m:
                    lead = m.group(1)
                    for t in STRICT_RE.findall(lead):
                        owned.setdefault(t, rel)
                        if '*' not in t: prefixes.add(re.split(r'[-_]', t)[0])
                    for t in ANYTICK_RE.findall(lead):
                        owned.setdefault(t, rel)   # bindings-key resolution only
                    break
            for m in OWNS_RE.finditer(line):
                prefixes.add(m.group(1))

    # tombstoned IDs resolve (supersession references are legal; 10d owns liveness rules)
    tombs = manifest.get('tombstones') or {}
    if isinstance(tombs, dict):
        for t in tombs: owned.setdefault(t, 'manifest:tombstone')

    mentioned = set()   # weaker tier: backticked anywhere in a role-doc (inline mints)
    for p, (fm, text) in docmeta.items():
        for t in re.findall(r'`(' + STRICT + r')`', text):
            mentioned.add(t)

    def resolves(tok):
        if tok in owned: return True
        for o in owned:            # wildcard register rows like EVT-*-X / COMPONENT-ADAPTER-*
            if '*' in o and len([s for s in o.split('-') if s != '*']) >= 2:
                # a bare family alias (`A11Y-*`) is not a mint; a shaped wildcard is
                if re.fullmatch(o.replace('*', '[A-Z0-9-]+'), tok): return True
        for o in owned:            # prefix-elided shorthand: `VENDOR-ORDER` for ENTITY-VENDOR-ORDER
            if '*' not in o and o.endswith('-' + tok): return True
        return False

    # --- id web: references in docs
    for p, (fm, text) in docmeta.items():
        rel = os.path.relpath(p, root)
        for i, line in enumerate(text.splitlines(), 1):
            if '[FUTURE-SCOPE]' in line: continue   # sanctioned forward references (Std Part 5)
            for m in ID_RE.finditer(line):
                tok = m.group(1)
                if '*' in tok or tok.split('-')[0] not in prefixes: continue
                nxt = line[m.end():m.end()+2]
                if nxt.startswith('-*') or nxt.startswith('-#'): continue  # wildcard family / ID-scheme mention
                if m.start() > 0 and line[m.start()-1] == '-': continue    # suffix-shorthand continuation `-FOO-BAR`
                ctx = line[max(0, m.start()-30):m.start()]
                if re.search(r'\b(no|not|never|without)\s+\**`?$', ctx): continue  # negated mention
                if not resolves(tok):
                    if re.search(r'retired|tombstone', line, re.I):
                        finding('WARN', 'idweb', f'{rel}:{i}', f'retired-contract mention `{tok}` (tombstone owed if ever referenced live)')
                        continue
                    base = re.sub(r'[a-z]$', '', tok)
                    ticked = m.start() > 0 and line[m.start()-1] == '`'
                    if base != tok and resolves(base):
                        finding('WARN', 'idweb', f'{rel}:{i}', f'arm token `{tok}` resolves only to parent `{base}`')
                    elif ticked:
                        finding('ERROR', 'idweb', f'{rel}:{i}', f'dangling reference `{tok}` (owned prefix, no definition found)')
                    else:
                        finding('WARN', 'idweb', f'{rel}:{i}', f'unticked ID-like token `{tok}` resolves to nothing (prose compound, or a dangling reference)')

    # --- bindings
    if bindings_path:
        rel_b = os.path.relpath(bindings_path, root)
        b = parse_yaml_subset(open(bindings_path, encoding='utf-8').read()) or {}
        bmap = b.get('bindings') or {}
        for key, v in (bmap.items() if isinstance(bmap, dict) else []):
            if not resolves(key):
                if key in mentioned:
                    finding('WARN', 'bindings', f'{rel_b}::{key}', 'binding key found only as an inline mention, not a register-form definition (inline mint)')
                else:
                    finding('ERROR', 'bindings', f'{rel_b}::{key}', 'binding key resolves to no owning doc definition')
            locs = (v or {}).get('locators') if isinstance(v, dict) else None
            for loc in (locs or []):
                if not isinstance(loc, dict): continue
                path, sym = loc.get('path'), loc.get('symbol')
                if path:
                    fs = os.path.join(root, path)
                    if not os.path.exists(fs):
                        finding('ERROR', 'bindings', f'{rel_b}::{key}', f'locator path missing: {path}')
                    elif sym and ' ' not in sym and os.path.isfile(fs):
                        # dotted composite symbols: require the last segment in-file
                        probe = sym.split('.')[-1]
                        if probe not in open(fs, encoding='utf-8', errors='replace').read():
                            finding('WARN', 'bindings', f'{rel_b}::{key}', f'symbol `{sym}` (probe `{probe}`) not found in {path}')

    # --- markers
    KNOWN = {'GAP','ASSUMPTION','REVISIT','FUTURE-SCOPE'}
    seen = {}
    for p, (fm, text) in docmeta.items():
        for i, line in enumerate(text.splitlines(), 1):
            for m in re.finditer(r'\[([A-Z][A-Z-]{2,})\]', line):
                tok = m.group(1)
                if tok not in KNOWN and not ID_RE.fullmatch(tok):
                    seen.setdefault(tok, (os.path.relpath(p, root), i))
    for tok, (f, i) in sorted(seen.items()):
        finding('WARN', 'markers', f'{f}:{i}', f'non-standard marker `[{tok}]` (declare or replace)')

    # --- index/README consistency (crude)
    for cand in ('docs/README.md', 'README.md'):
        rp = os.path.join(root, cand)
        if os.path.exists(rp):
            rtext = open(rp, encoding='utf-8').read().lower()
            missing = [cid for cid, c in concerns.items()
                       if isinstance(c, dict) and c.get('in_scope')
                       and cid.replace('-', ' ') not in rtext.replace('&', 'and').replace('-', ' ')]
            if missing:
                finding('WARN', 'index', cand, f'in-scope concerns not mentioned: {", ".join(missing)}')
            break

    return manifest_path

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    run(os.path.abspath(root))
    errs = sum(1 for s, *_ in FINDINGS if s == 'ERROR')
    order = {'ERROR': 0, 'WARN': 1, 'INFO': 2}
    for sev, check, where, msg in sorted(FINDINGS, key=lambda f: (order[f[0]], f[1])):
        print(f'{sev:5} [{check:9}] {where} — {msg}')
    print(f'\n{errs} error(s), {sum(1 for s,*_ in FINDINGS if s=="WARN")} warning(s), '
          f'{sum(1 for s,*_ in FINDINGS if s=="INFO")} info')
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
