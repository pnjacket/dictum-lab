#!/usr/bin/env python3
"""dictum-tracker-sync — doc->tracker sync adapter (Part 10c execution mirror). EXPERIMENTAL.

Zero-dependency (Python 3 stdlib only). Implements the standard's doc<->tracker
boundary (STANDARD Part 10c; tracker-binding declaration, Delivery Process
11.6): the tracker is a DOWNSTREAM MIRROR of what the repo owns. The tool
reads the product's tracker-binding declaration + build-status record +
derived backlog, computes the projection (execution items), diffs it against
tracker state, and reconciles REPO-WINS.

Boundary invariants it enforces by construction:
  - downstream mirror: the tool NEVER writes doc-set files — the tracker is
    the only mutation target (and only under --apply);
  - the repo stores no tracker back-reference: the join is the stable
    contract ID (and slice ordinal), carried on the item as labels, resolved
    at projection time each run;
  - three item roles: only EXECUTION items (role label) are mirrored;
    demand/triage items are never touched;
  - build gate: an execution item is projected only from Contract-grade
    contract IDs — a violation is reported, never projected.

Adapters: `file` (a JSON file-backed mock tracker — what all tests use) and
`github` (GitHub Issues via the `gh` CLI; requires `gh auth login`; never
invoked in tests, no network here).

Dry-run by default (prints the reconciliation plan); `--apply` executes it.

Exit code: 0 in sync / 1 actions needed or gate violations / 2 usage or
parse error (including a missing/undecidable declaration — declined loudly).

Non-normative: the standard's text is the only definition of conformance;
where this tool and the text disagree, the text wins and this tool has a bug.
The machine-readable `tracker-binding.yaml` file format is a TOOL convention
implementing the declaration 11.6 defines — the standard pins the boundary
semantics, not this file.
"""
import os, re, sys, json, subprocess

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', 'common'))
from dictumlib import (parse_yaml_subset, load_docset, IdWeb, STRICT, id_kind,
                       CODE_REALIZABLE_KINDS)

CG_RUNGS = {'contract-grade', 'verified'}
STRICT_RE = re.compile(r'\b(' + STRICT + r')\b')
STRICT_FULL = re.compile(STRICT + r'$')

# ---------- declaration

def load_declaration(root):
    for cand in ('tracker-binding.yaml', 'docs/tracker-binding.yaml'):
        p = os.path.join(root, cand)
        if os.path.exists(p):
            doc = parse_yaml_subset(open(p, encoding='utf-8').read()) or {}
            tb = doc.get('tracker_binding')
            if not isinstance(tb, dict):
                print(f'error: {cand} has no tracker_binding block', file=sys.stderr)
                sys.exit(2)
            return tb
    print('error: no tracker-binding declaration found (tracker-binding.yaml) — '
          'not decidable which tracker mirrors this repo; declining (Part 10c: '
          'the declaration is the product-local adapter contract)', file=sys.stderr)
    sys.exit(2)

# ---------- build-status record (the standard's build-status template table)

def parse_build_status(text):
    slices, in_section, seen_header = [], False, 0
    for line in text.splitlines():
        if re.match(r'^##\s+Slices', line):
            in_section = True; continue
        if in_section and line.startswith('## '):
            break
        if not in_section or not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if seen_header < 2:            # header + separator rows
            seen_header += 1; continue
        if len(cells) < 6 or not cells[0].isdigit():
            continue
        verified = cells[5].strip()
        slices.append({
            'n': int(cells[0]),
            'name': cells[1],
            'realizes': sorted(set(STRICT_RE.findall(cells[3]))),
            'built': '✅' in cells[4] or cells[4].lower() in ('x', 'yes'),
            'verified': verified not in ('', '—', '-', '–'),
        })
    return slices

# ---------- projection (derived each run; never stored — Part 0.5)

def rung_info(web, docmeta, manifest, tok):
    info = web.owned.get(tok)
    if not info or info['file'] == 'manifest:tombstone':
        return None, None
    fm, _ = docmeta.get(info['file'], ({}, ''))
    cid = fm.get('concern-id')
    c = ((manifest.get('concerns') or {}).get(cid) or {}) if cid else {}
    if isinstance(c, dict) and c:
        return bool(c.get('in_scope')), c.get('current_rung')
    return None, fm.get('current-rung')

def project(root, tb, docset):
    ch = tb.get('channel') if isinstance(tb.get('channel'), dict) else {}
    idp = ch.get('id_label_prefix', 'dict:')
    slp = ch.get('slice_label_prefix', 'dict-slice:')
    rlp = ch.get('role_label_prefix', 'dict-role:')
    role_exec = rlp + 'execution'

    bs_path = os.path.join(root, tb.get('build_status') or 'IMPLEMENTATION.md')
    if not os.path.exists(bs_path):
        print(f'error: build-status record not found: {bs_path} — nothing decidable to '
              'project; declining', file=sys.stderr)
        sys.exit(2)
    slices = parse_build_status(open(bs_path, encoding='utf-8').read())

    manifest = docset['manifest'] or {}
    docmeta = docset['docmeta']
    tombs = set((manifest.get('tombstones') or {}) if isinstance(manifest.get('tombstones'), dict) else [])
    web = IdWeb(docmeta, tombstones=tombs)
    b = docset['bindings'] or {}
    bmap = b.get('bindings') if isinstance(b.get('bindings'), dict) else {}

    items, gate_violations, realized = [], [], set()
    for s in slices:
        bad = []
        for tok in s['realizes']:
            in_scope, rung = rung_info(web, docmeta, manifest, tok)
            if not web.resolves(tok) or rung not in CG_RUNGS:
                bad.append(tok)
        if bad:
            gate_violations.append(
                f"slice {s['n']} '{s['name']}': realizes {', '.join(bad)} — not a resolving "
                'Contract-grade contract ID; BUILD GATE (Part 10c): not projected')
            continue
        realized.update(s['realizes'])
        items.append({
            'title': f"Slice {s['n']}: {s['name']}",
            'labels': sorted([role_exec, f"{slp}{s['n']}"] + [idp + t for t in s['realizes']]),
            'state': 'closed' if s['verified'] else 'open',
            'body': 'Execution item mirrored from the repo doc set (Dictum Part 10c: '
                    'downstream mirror; repo wins). Realizes: ' + ', '.join(s['realizes']) +
                    '. Contracts live in the repo — reference only, never restate.',
        })
    # derived backlog (Part 10e build-new): in-scope Contract-grade code-realizable,
    # unbound, and not realized by any slice row
    for tok in sorted(web.owned):
        if '*' in tok or not STRICT_FULL.fullmatch(tok): continue
        if tok in tombs or id_kind(tok) not in CODE_REALIZABLE_KINDS: continue
        if tok in bmap or tok in realized: continue
        in_scope, rung = rung_info(web, docmeta, manifest, tok)
        if in_scope is not True or rung not in CG_RUNGS: continue
        items.append({
            'title': f'Build: {tok}',
            'labels': sorted([role_exec, idp + tok]),
            'state': 'open',
            'body': 'Build-new execution item derived from the repo doc set (Dictum '
                    f'Part 10e: Contract-grade, code-realizable, unbound). Realizes: {tok}. '
                    'Repo wins.',
        })
    return items, gate_violations, role_exec, slp

# ---------- adapters

class FileTracker:
    """JSON-file-backed mock tracker (what all tests/fixtures use)."""
    def __init__(self, root, cfg):
        self.path = os.path.join(root, (cfg or {}).get('path') or 'tracker.json')
        if os.path.exists(self.path):
            self.data = json.load(open(self.path, encoding='utf-8'))
        else:
            self.data = {'next_key': 1, 'items': []}
    def _save(self):
        open(self.path, 'w', encoding='utf-8').write(
            json.dumps(self.data, indent=2, sort_keys=True) + '\n')
    def list_items(self):
        return [dict(i) for i in self.data.get('items') or []]
    def create(self, item):
        key = self.data.get('next_key') or 1
        self.data['next_key'] = key + 1
        self.data.setdefault('items', []).append({
            'key': key, 'title': item['title'], 'labels': sorted(item['labels']),
            'state': item['state'], 'body': item['body']})
        self._save()
    def update(self, key, fields):
        for it in self.data.get('items') or []:
            if it.get('key') == key:
                it.update(fields)
                if 'labels' in fields: it['labels'] = sorted(it['labels'])
        self._save()
    def close(self, key):
        self.update(key, {'state': 'closed'})

class GithubTracker:
    """GitHub Issues via the `gh` CLI. Requires `gh auth login` and existing
    labels; never invoked by tests (no network in tests)."""
    def __init__(self, root, cfg):
        self.repo = (cfg or {}).get('repo')
        if not self.repo:
            print('error: github adapter needs `github: { repo: owner/name }`', file=sys.stderr)
            sys.exit(2)
    def _gh(self, *args, capture=False):
        r = subprocess.run(['gh'] + list(args), text=True,
                           capture_output=capture, check=True)
        return r.stdout if capture else None
    def list_items(self):
        out = self._gh('issue', 'list', '--repo', self.repo, '--state', 'all',
                       '--limit', '500', '--json', 'number,title,labels,state', capture=True)
        return [{'key': i['number'], 'title': i['title'],
                 'labels': sorted(l['name'] for l in i.get('labels') or []),
                 'state': 'closed' if i['state'].lower() == 'closed' else 'open'}
                for i in json.loads(out or '[]')]
    def create(self, item):
        args = ['issue', 'create', '--repo', self.repo, '--title', item['title'],
                '--body', item['body']]
        for l in item['labels']: args += ['--label', l]
        url = (self._gh(*args, capture=True) or '').strip()
        if item['state'] == 'closed' and url:
            self._gh('issue', 'close', url, '--repo', self.repo)
    def update(self, key, fields):
        num = str(key)
        if 'title' in fields:
            self._gh('issue', 'edit', num, '--repo', self.repo, '--title', fields['title'])
        if 'add_labels' in fields:
            for l in fields['add_labels']:
                self._gh('issue', 'edit', num, '--repo', self.repo, '--add-label', l)
        if 'remove_labels' in fields:
            for l in fields['remove_labels']:
                self._gh('issue', 'edit', num, '--repo', self.repo, '--remove-label', l)
        if fields.get('state') == 'closed':
            self._gh('issue', 'close', num, '--repo', self.repo)
        elif fields.get('state') == 'open':
            self._gh('issue', 'reopen', num, '--repo', self.repo)
    def close(self, key):
        self._gh('issue', 'close', str(key), '--repo', self.repo)

def make_adapter(root, tb):
    kind = tb.get('adapter')
    if kind == 'file':
        return FileTracker(root, tb.get('file'))
    if kind == 'github':
        return GithubTracker(root, tb.get('github'))
    print(f'error: unknown adapter `{kind}` (file | github)', file=sys.stderr)
    sys.exit(2)

# ---------- diff & reconcile (REPO-WINS)

def diff(projected, tracker_items, role_exec, slp):
    exec_items = [t for t in tracker_items if role_exec in (t.get('labels') or [])]
    other = len(tracker_items) - len(exec_items)
    by_slice, by_labels = {}, {}
    for p in projected:
        sl = next((l for l in p['labels'] if l.startswith(slp)), None)
        if sl: by_slice[sl] = p
        else: by_labels[frozenset(p['labels'])] = p
    actions, matched = [], set()
    for t in exec_items:
        labels = t.get('labels') or []
        sl = next((l for l in labels if l.startswith(slp)), None)
        p = by_slice.pop(sl, None) if sl else by_labels.pop(frozenset(labels), None)
        if p is None:
            if t.get('state') != 'closed':
                actions.append({'op': 'close', 'key': t['key'],
                                'reason': 'execution item with no repo projection — repo wins '
                                          '(demand/triage items are never touched)'})
            continue
        changes, notes = {}, []
        if t.get('title') != p['title']:
            changes['title'] = p['title']; notes.append(f"title -> '{p['title']}'")
        if t.get('state') != p['state']:
            changes['state'] = p['state']; notes.append(f"state {t.get('state')} -> {p['state']}")
        cur, want = set(t.get('labels') or []), set(p['labels'])
        if cur != want:
            changes['labels'] = sorted(want)
            changes['add_labels'] = sorted(want - cur)
            changes['remove_labels'] = sorted(cur - want)
            notes.append('labels reconciled')
        if changes:
            actions.append({'op': 'update', 'key': t['key'], 'changes': changes,
                            'reason': '; '.join(notes) + ' (repo wins)'})
    for p in list(by_slice.values()) + list(by_labels.values()):
        actions.append({'op': 'create', 'item': p, 'reason': 'projected execution item missing from tracker'})
    return actions, other

def main():
    args = sys.argv[1:]
    apply_mode = '--apply' in args
    if apply_mode: args.remove('--apply')
    if len(args) != 1 or args[0].startswith('-'):
        print('usage: dictum-tracker-sync.py <repo-root> [--apply]', file=sys.stderr)
        sys.exit(2)
    root = os.path.abspath(args[0])
    if not os.path.isdir(root):
        print(f'error: not a directory: {root}', file=sys.stderr)
        sys.exit(2)
    tb = load_declaration(root)
    docset = load_docset(root)
    if not docset['manifest_path']:
        print(f'error: no manifest.yaml found under {root}', file=sys.stderr)
        sys.exit(2)
    projected, gate_violations, role_exec, slp = project(root, tb, docset)
    adapter = make_adapter(root, tb)
    actions, untouched = diff(projected, adapter.list_items(), role_exec, slp)

    for g in gate_violations:
        print(f'GATE   {g}')
    for a in actions:
        if a['op'] == 'create':
            print(f"CREATE {a['item']['title']} [{a['item']['state']}] — {a['reason']}")
        elif a['op'] == 'update':
            print(f"UPDATE #{a['key']} — {a['reason']}")
        else:
            print(f"CLOSE  #{a['key']} — {a['reason']}")
    print(f'\n{len(actions)} action(s), {len(gate_violations)} gate violation(s); '
          f'{len(projected)} projected execution item(s); {untouched} non-execution '
          'tracker item(s) untouched (demand/triage)')
    if apply_mode and actions:
        for a in actions:
            if a['op'] == 'create': adapter.create(a['item'])
            elif a['op'] == 'update': adapter.update(a['key'], a['changes'])
            else: adapter.close(a['key'])
        print(f'applied {len(actions)} action(s) to the tracker (repo files untouched — '
              'downstream-mirror invariant)')
        sys.exit(1 if gate_violations else 0)
    sys.exit(1 if (actions or gate_violations) else 0)

if __name__ == '__main__':
    main()
