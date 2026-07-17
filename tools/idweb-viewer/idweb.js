/*! dictum-idweb — derive and check the owned-ID web of a Dictum doc set.
 *
 * Part of dictum-lab (MIT). NON-NORMATIVE: the standard's text (STANDARD.md +
 * concerns/ in the canonical Dictum repository) is the only definition of
 * conformance; where this tool disagrees with the text, the text wins and
 * this tool has a bug.
 *
 * A JavaScript port of the parsing/resolution slice of
 * tools/common/dictumlib.py plus gate-check's idweb + bindings passes. The ID
 * grammar and the register-form definition grammar now live in THREE places —
 * dictumlib.py, gate-check's inline copy, and this file; a change must land
 * in all three, cross-checked by tests/run.sh over the fixture corpus.
 *
 * Dual-use: browser global `DictumIdweb` (consumed by
 * dictum-idweb-viewer.html), or `node idweb.js <repo-root>` for a
 * deterministic CLI findings run (what tests/run.sh executes).
 */
(function (global, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else global.DictumIdweb = factory();
})(typeof self !== 'undefined' ? self : this, function () {
'use strict';

// ---------- minimal YAML-subset parser (port of dictumlib.parse_yaml_subset)
// The subset is what the standard's templates use for manifests, front matter,
// and binding maps.

function stripComment(line) {
  var out = [], q = null;
  for (var i = 0; i < line.length; i++) {
    var ch = line[i];
    if (q) { if (ch === q) q = null; }
    else if (ch === '"' || ch === "'") q = ch;
    else if (ch === '#') break;
    out.push(ch);
  }
  return out.join('').replace(/\s+$/, '');
}

function splitFlow(s, close) {
  var parts = [], depth = 0, cur = [], q = null;
  for (var i = 0; i < s.length; i++) {
    var ch = s[i];
    if (q) { cur.push(ch); if (ch === q) q = null; continue; }
    if (ch === '"' || ch === "'") { q = ch; cur.push(ch); continue; }
    if (ch === '{' || ch === '[') { depth += 1; cur.push(ch); continue; }
    if (ch === '}' || ch === ']') {
      if (depth === 0 && ch === close) { parts.push(cur.join('')); return [parts, i]; }
      depth -= 1; cur.push(ch); continue;
    }
    if (ch === ',' && depth === 0) { parts.push(cur.join('')); cur = []; continue; }
    cur.push(ch);
  }
  parts.push(cur.join(''));
  return [parts, s.length];
}

function unquote(s) { return s.replace(/^["']/, '').replace(/["']$/, ''); }

function parseFlow(s) {
  s = s.trim();
  if (s.startsWith('{')) {
    var body = splitFlow(s.slice(1), '}')[0], d = {};
    for (var i = 0; i < body.length; i++) {
      var part = body[i];
      if (!part.trim()) continue;
      var j = part.indexOf(':');
      var k = j < 0 ? part : part.slice(0, j), v = j < 0 ? '' : part.slice(j + 1);
      d[unquote(k.trim())] = parseFlow(v);
    }
    return d;
  }
  if (s.startsWith('[')) {
    var items = splitFlow(s.slice(1), ']')[0];
    return items.filter(function (p) { return p.trim(); }).map(parseFlow);
  }
  if (s === 'true' || s === 'True') return true;
  if (s === 'false' || s === 'False') return false;
  if (s === 'null' || s === '~' || s === '') return null;
  return unquote(s.trim());
}

function parseYamlSubset(text) {
  var lines = [];
  String(text).split('\n').forEach(function (raw) {
    var s = stripComment(raw);
    if (s.trim() === '') return;
    var indent = raw.length - raw.replace(/^ */, '').length;
    lines.push([indent, s.trim()]);
  });
  var pos = [0];
  function block(minIndent) {
    if (pos[0] >= lines.length) return null;
    var ind = lines[pos[0]][0], s = lines[pos[0]][1];
    if (ind < minIndent) return null;
    var isList = s.startsWith('- ') || s === '-';
    return isList ? _list(ind) : _map(ind);
  }
  function _map(indent) {
    var d = {};
    while (pos[0] < lines.length) {
      var ind = lines[pos[0]][0], s = lines[pos[0]][1];
      if (ind < indent) break;
      if (ind > indent) { pos[0] += 1; continue; } // stray deeper line
      var m = /^([^:]+):\s*(.*)$/.exec(s);
      if (!m) { pos[0] += 1; continue; }
      var key = unquote(m[1].trim()), val = m[2].trim();
      pos[0] += 1;
      if (val === '') {
        var child = block(indent + 1);
        d[key] = child !== null ? child : null;
      } else {
        d[key] = parseFlow(val);
      }
    }
    return d;
  }
  function _list(indent) {
    var out = [];
    while (pos[0] < lines.length) {
      var ind = lines[pos[0]][0], s = lines[pos[0]][1];
      if (ind < indent || !(s.startsWith('- ') || s === '-')) break;
      var item = s.slice(1).trim();
      pos[0] += 1;
      if (item === '') out.push(block(indent + 1));
      else if (/^[^:{[]+:\s/.test(item) || /^[^:{[]+:$/.test(item)) {
        var j = item.indexOf(':');
        var o = {};
        o[item.slice(0, j).trim()] = parseFlow(item.slice(j + 1));
        out.push(o);
      } else out.push(parseFlow(item));
    }
    return out;
  }
  return block(0);
}

// ---------- front matter

function frontMatter(text) {
  text = String(text == null ? '' : text);
  if (!text.startsWith('---')) return [null, text];
  var end = text.indexOf('\n---', 3);
  if (end < 0) return [null, text];
  var fm = parseYamlSubset(text.slice(3, end));
  return [fm && typeof fm === 'object' && !Array.isArray(fm) ? fm : null, text];
}

// ---------- ID grammar & registries (dictumlib parity)
// The normative token grammar is STANDARD Part 5: [A-Z][A-Z0-9]+(-[A-Z0-9]+)+ .
// Detection here scans deliberately LOOSER (underscore joiners, wildcard
// segments, a trailing lowercase arm) — near-misses are flagged, never minted.

var STRICT = '[A-Z][A-Z0-9]+(?:[-_][A-Z0-9*]+)+[a-z]?';
var NORMATIVE = '[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+';   // STANDARD Part 5, verbatim

var REGISTERED_PREFIXES = ['CAP', 'ENTITY', 'INV', 'COMPONENT', 'API', 'CLI',
  'LIB', 'EVT', 'ROLE', 'POLICY', 'SCREEN', 'ROUTE', 'ENV', 'DEP', 'PERF',
  'LICENSE', 'SUCCESS', 'PERSONA', 'ADR', 'SEQ', 'ERR', 'SEC', 'WVR', 'AC'];

// Register-form definition-line grammar (the Part 5 extension point), ported
// from dictumlib.DEF_LEAD: heading, table row (1st cell), list item, paragraph
// register row, backticked non-ID key, bare start-of-line key.
var _ANCHOR = '\\**`?' + STRICT;
var DEF_LEAD = [
  new RegExp('^\\s*#{2,5}\\s+(.{0,160})$'),
  new RegExp('^\\s*\\|\\s*(' + _ANCHOR + '.{0,250}?)\\|'),
  new RegExp('^\\s*[-*]\\s+(' + _ANCHOR + '.{0,90}?)(?:—|:|$)'),
  new RegExp('^\\s*(\\*\\*`?' + STRICT + '.{0,90}?)(?:—|:)'),
  new RegExp('^\\s*[-*]\\s+(\\*\\*`[^`]{2,60}`\\*\\*.{0,20}?)(?:—|:)'),
  new RegExp('^\\s*(\\*\\*`[^`]{2,60}`\\*\\*\\s*)(?:—|:)'),
  new RegExp('^\\s*(`' + STRICT + '`)\\s*[(:—]'),
];

function allMatches(reSource, flags, s) {
  var re = new RegExp(reSource, flags.indexOf('g') >= 0 ? flags : flags + 'g');
  var out = [], m;
  while ((m = re.exec(s)) !== null) {
    out.push(m);
    if (m.index === re.lastIndex) re.lastIndex++; // zero-width safety
  }
  return out;
}

function idKind(tok) { return tok.split('-')[0].split('_')[0]; }

// ---------- doc-set discovery (port of dictumlib.discover, over a file list)
// files: [{path: 'rel/posix/path', text: string|null}] — text null = unread
// (binary/oversize); existence checks still work.

function discover(files) {
  var byPath = new Map();
  files.forEach(function (f) { byPath.set(f.path.replace(/\\/g, '/'), f); });
  function first(cands) {
    for (var i = 0; i < cands.length; i++) if (byPath.has(cands[i])) return cands[i];
    return null;
  }
  var manifestPath = first(['docs/manifest.yaml', 'manifest.yaml']);
  var bindingsPath = first(['docs/bindings.yaml', 'bindings.yaml']);
  var standardDir = null;
  ['dictum', 'docs/dictum'].some(function (d) {
    var hit = false;
    byPath.forEach(function (_, p) { if (p === d || p.startsWith(d + '/')) hit = true; });
    if (hit) standardDir = d;
    return hit;
  });
  var docPats = [/^docs\/[^/]+\.md$/, /^docs\/concerns\/[^/]+\.md$/, /^[^/]+\.md$/];
  var docs = [];
  byPath.forEach(function (f, p) {
    if (!docPats.some(function (r) { return r.test(p); })) return;
    if (standardDir && (p === standardDir || p.startsWith(standardDir + '/'))) return;
    var fm = frontMatter(f.text || '')[0];
    if (fm && Object.prototype.hasOwnProperty.call(fm, 'role')) docs.push(p);
  });
  docs.sort();
  return { manifestPath: manifestPath, bindingsPath: bindingsPath,
           standardDir: standardDir, docs: docs, byPath: byPath };
}

// ---------- the owned-ID web

function buildWeb(files) {
  var d = discover(files);
  var byPath = d.byPath;
  var manifest = d.manifestPath
    ? (parseYamlSubset(byPath.get(d.manifestPath).text || '') || {}) : null;
  var bindings = d.bindingsPath
    ? (parseYamlSubset(byPath.get(d.bindingsPath).text || '') || {}) : null;

  var docmeta = {};   // rel -> {fm, text}
  d.docs.forEach(function (rel) {
    var pair = frontMatter(byPath.get(rel).text || '');
    docmeta[rel] = { fm: pair[0] || {}, text: pair[1] };
  });

  var findings = [];
  function finding(sev, check, where, msg) {
    findings.push({ sev: sev, check: check, where: where, msg: msg });
  }

  // --- mint pass: register-form definitions, prefixes (gate-check parity)
  var owned = new Map();      // tok -> {file, line, text, anytick, tombstone}
  var prefixes = new Set();
  d.docs.forEach(function (rel) {
    var lines = docmeta[rel].text.split('\n');
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      for (var r = 0; r < DEF_LEAD.length; r++) {
        var m = DEF_LEAD[r].exec(line);
        if (m) {
          var lead = m[1];
          allMatches('\\b(' + STRICT + ')\\b', 'g', lead).forEach(function (mm) {
            var t = mm[1];
            if (!owned.has(t)) owned.set(t, { file: rel, line: i + 1, text: line.trim(), anytick: false, tombstone: false });
            if (t.indexOf('*') < 0) prefixes.add(t.split(/[-_]/)[0]);
          });
          allMatches('`([^`\\s]{2,60})`', 'g', lead).forEach(function (mm) {
            var t = mm[1];   // bindings-key resolution only (non-ID keys)
            if (!owned.has(t)) owned.set(t, { file: rel, line: i + 1, text: line.trim(), anytick: true, tombstone: false });
          });
          break;
        }
      }
      allMatches('[Oo]wns[^.]*?`([A-Z][A-Z0-9]*)-#{2,}`', 'g', line).forEach(function (mm) {
        prefixes.add(mm[1]);
      });
    }
  });

  // tombstoned IDs resolve (supersession references are legal; Part 10d owns liveness)
  var tombstones = new Set();
  var tombs = manifest && manifest.tombstones;
  if (tombs && typeof tombs === 'object' && !Array.isArray(tombs)) {
    Object.keys(tombs).forEach(function (t) {
      tombstones.add(t);
      if (!owned.has(t)) owned.set(t, { file: 'manifest:tombstone', line: 0, text: '', anytick: false, tombstone: true });
      else owned.get(t).tombstone = true;
    });
  }

  // weaker tier: backticked anywhere in a role-doc (inline mints)
  var mentioned = new Set();
  d.docs.forEach(function (rel) {
    allMatches('`(' + STRICT + ')`', 'g', docmeta[rel].text).forEach(function (mm) {
      mentioned.add(mm[1]);
    });
  });

  var ownedKeys = Array.from(owned.keys());
  function resolveKey(tok) {
    if (owned.has(tok)) return tok;
    for (var i = 0; i < ownedKeys.length; i++) {   // shaped wildcard rows (EVT-*-X)
      var o = ownedKeys[i];
      if (o.indexOf('*') >= 0 && o.split('-').filter(function (s) { return s !== '*'; }).length >= 2) {
        if (new RegExp('^' + o.replace(/\*/g, '[A-Z0-9-]+') + '$').test(tok)) return o;
      }
    }
    for (var j = 0; j < ownedKeys.length; j++) {   // prefix-elided shorthand
      var o2 = ownedKeys[j];
      if (o2.indexOf('*') < 0 && o2.endsWith('-' + tok)) return o2;
    }
    return null;
  }
  function resolves(tok) { return resolveKey(tok) !== null; }

  // --- reference pass: findings (gate-check parity) + edges (viewer derivation)
  // Edge attribution: a reference belongs to the most recent register-line ID
  // in the same doc; a non-register heading resets attribution to the doc node.
  var edgeMap = new Map();    // 'src dst' -> {from,to,sites:[{file,line}]}
  function addEdge(from, to, rel, lineNo) {
    var k = from + ' ' + to;
    if (!edgeMap.has(k)) edgeMap.set(k, { from: from, to: to, sites: [] });
    edgeMap.get(k).sites.push({ file: rel, line: lineNo });
  }
  var referenced = new Set();  // owned keys with >=1 inbound reference
  var ghosts = new Map();      // dangling tok -> [{file,line}]

  d.docs.forEach(function (rel) {
    var lines = docmeta[rel].text.split('\n');
    var currentOwner = null;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line.indexOf('[FUTURE-SCOPE]') >= 0) continue; // sanctioned forward references (Std Part 5)

      var isReg = false;
      for (var r = 0; r < DEF_LEAD.length; r++) {
        var dm = DEF_LEAD[r].exec(line);
        if (dm) {
          var leadIds = allMatches('\\b(' + STRICT + ')\\b', 'g', dm[1]).map(function (x) { return x[1]; });
          if (leadIds.length) { currentOwner = leadIds[0]; isReg = true; }
          break;
        }
      }
      if (!isReg && /^\s*#{1,6}\s/.test(line)) currentOwner = null;

      var ms = allMatches('\\b(' + STRICT + ')\\b', 'g', line);
      for (var x = 0; x < ms.length; x++) {
        var tok = ms[x][1], start = ms[x].index, end = start + ms[x][0].length;
        if (tok.indexOf('*') >= 0 || !prefixes.has(tok.split('-')[0])) continue;
        var nxt = line.slice(end, end + 2);
        if (nxt.startsWith('-*') || nxt.startsWith('-#')) continue;  // wildcard family / ID-scheme mention
        if (start > 0 && line[start - 1] === '-') continue;          // suffix-shorthand continuation
        var ctx = line.slice(Math.max(0, start - 30), start);
        if (/\b(no|not|never|without)\s+\**`?$/.test(ctx)) continue; // negated mention

        var key = resolveKey(tok);
        if (key !== null) {
          if (key !== currentOwner) {
            var src = currentOwner ? 'id:' + currentOwner : 'doc:' + rel;
            addEdge(src, 'id:' + key, rel, i + 1);
            referenced.add(key);
          }
          continue;
        }
        // unresolved (gate-check idweb findings, verbatim semantics)
        if (/retired|tombstone/i.test(line)) {
          finding('WARN', 'idweb', rel + ':' + (i + 1),
            'retired-contract mention `' + tok + '` (tombstone owed if ever referenced live)');
          continue;
        }
        var base = tok.replace(/[a-z]$/, '');
        var ticked = start > 0 && line[start - 1] === '`';
        if (base !== tok && resolves(base)) {
          finding('WARN', 'idweb', rel + ':' + (i + 1),
            'arm token `' + tok + '` resolves only to parent `' + base + '`');
        } else if (ticked) {
          finding('ERROR', 'idweb', rel + ':' + (i + 1),
            'dangling reference `' + tok + '` (owned prefix, no definition found)');
          if (!ghosts.has(tok)) ghosts.set(tok, []);
          ghosts.get(tok).push({ file: rel, line: i + 1 });
          addEdge(currentOwner ? 'id:' + currentOwner : 'doc:' + rel, 'ghost:' + tok, rel, i + 1);
        } else {
          finding('WARN', 'idweb', rel + ':' + (i + 1),
            'unticked ID-like token `' + tok + '` resolves to nothing (prose compound, or a dangling reference)');
        }
      }
    }
  });

  // --- bindings pass (gate-check parity) + code edges
  // gate-check's locator existence check is os.path.exists — directories
  // count. A flat file index can't hold directories, so derive them.
  var dirPrefixes = new Set();
  byPath.forEach(function (_, p) {
    var parts = p.split('/');
    for (var i = 1; i < parts.length; i++) dirPrefixes.add(parts.slice(0, i).join('/'));
  });
  var codeFiles = new Set();
  if (bindings) {
    var relB = d.bindingsPath;
    var bmap = bindings.bindings || {};
    if (bmap && typeof bmap === 'object' && !Array.isArray(bmap)) {
      Object.keys(bmap).forEach(function (key) {
        var v = bmap[key];
        if (!resolves(key)) {
          if (mentioned.has(key)) {
            finding('WARN', 'bindings', relB + '::' + key,
              'binding key found only as an inline mention, not a register-form definition (inline mint)');
          } else {
            finding('ERROR', 'bindings', relB + '::' + key,
              'binding key resolves to no owning doc definition');
          }
        }
        var locs = (v && typeof v === 'object') ? v.locators : null;
        (Array.isArray(locs) ? locs : []).forEach(function (loc) {
          if (!loc || typeof loc !== 'object') return;
          var pth = loc.path, sym = loc.symbol;
          if (!pth) return;
          if (!byPath.has(pth) && !dirPrefixes.has(pth)) {
            finding('ERROR', 'bindings', relB + '::' + key, 'locator path missing: ' + pth);
            return;
          }
          // a directory locator exists but gets no symbol probe (isfile parity)
          var f = byPath.has(pth) ? byPath.get(pth) : null;
          if (f && sym && String(sym).indexOf(' ') < 0 && f.text != null) {
            var probe = String(sym).split('.').pop();   // dotted composite symbols
            if (f.text.indexOf(probe) < 0) {
              finding('WARN', 'bindings', relB + '::' + key,
                'symbol `' + sym + '` (probe `' + probe + '`) not found in ' + pth);
            }
          }
          var target = resolveKey(key);
          if (target !== null) {
            codeFiles.add(pth);
            addEdge('id:' + target, 'code:' + pth, relB, 0);
          }
        });
      });
    }
  }

  // --- orphans (informational): minted, never referenced, unbound
  var orphans = [];
  owned.forEach(function (info, tok) {
    if (info.anytick || info.file === 'manifest:tombstone') return;
    if (!referenced.has(tok)) orphans.push(tok);
  });
  orphans.sort();

  var realOwned = 0;
  owned.forEach(function (info) {
    if (!info.anytick && info.file !== 'manifest:tombstone') realOwned++;
  });

  return {
    manifestPath: d.manifestPath, bindingsPath: d.bindingsPath,
    standardDir: d.standardDir, docs: d.docs,
    manifest: manifest, bindings: bindings,
    owned: owned, prefixes: prefixes, tombstones: tombstones,
    mentioned: mentioned, edges: Array.from(edgeMap.values()),
    ghosts: ghosts, orphans: orphans, findings: findings,
    counts: {
      docs: d.docs.length, owned: realOwned,
      references: Array.from(edgeMap.values()).reduce(function (n, e) { return n + e.sites.length; }, 0),
      errors: findings.filter(function (f) { return f.sev === 'ERROR'; }).length,
      warnings: findings.filter(function (f) { return f.sev === 'WARN'; }).length,
    },
    codeFiles: codeFiles,
  };
}

// ---------- viewer derivation: cytoscape elements

var KIND_CLASSES = [
  { cls: 'interface',    kinds: ['API', 'CLI', 'LIB', 'EVT', 'MSG', 'OUT'],           label: 'Interface' },
  { cls: 'domain',       kinds: ['ENTITY'],                                            label: 'Domain' },
  { cls: 'product',      kinds: ['CAP', 'SUCCESS', 'PERSONA'],                         label: 'Product' },
  { cls: 'invariant',    kinds: ['INV'],                                               label: 'Invariant' },
  { cls: 'architecture', kinds: ['COMPONENT', 'ADR'],                                  label: 'Architecture' },
  { cls: 'ux',           kinds: ['SCREEN', 'ROUTE', 'BIND', 'DOM'],                    label: 'UX' },
  { cls: 'opspolicy',    kinds: ['ENV', 'CONFIG', 'DEP', 'PERF', 'SEQ', 'ERR', 'SEC',
                                 'POLICY', 'ROLE', 'WVR', 'AC', 'LICENSE'],            label: 'Ops / Policy' },
];
var KIND_TO_CLASS = {};
KIND_CLASSES.forEach(function (kc) {
  kc.kinds.forEach(function (k) { KIND_TO_CLASS[k] = kc.cls; });
});
function kindClass(tok) { return KIND_TO_CLASS[idKind(tok)] || 'other'; }

function toElements(model, opts) {
  opts = opts || {};
  var groupByDoc = !!opts.groupByDoc, showCode = opts.showCode !== false,
      showOrphans = opts.showOrphans !== false;
  var els = [], present = new Set();
  var orphanSet = new Set(model.orphans);

  var boundIds = new Set();
  model.edges.forEach(function (e) {
    if (e.to.startsWith('code:')) boundIds.add(e.from.slice(3));
  });

  function docNode(rel) {
    var id = 'doc:' + rel;
    if (present.has(id)) return;
    present.add(id);
    els.push({ data: { id: id, label: rel.split('/').pop(), full: rel },
               classes: groupByDoc ? 'docgroup' : 'docnode' });
  }

  model.owned.forEach(function (info, tok) {
    if (info.anytick) return;
    var isTomb = info.tombstone || info.file === 'manifest:tombstone';
    if (!showOrphans && orphanSet.has(tok) && !isTomb && !boundIds.has(tok)) return;
    var id = 'id:' + tok;
    present.add(id);
    var data = { id: id, label: tok, kind: idKind(tok), file: info.file, line: info.line, register: info.text };
    if (groupByDoc && !isTomb) { docNode(info.file); data.parent = 'doc:' + info.file; }
    els.push({ data: data, classes: isTomb ? 'tombstone' : kindClass(tok) });
  });

  model.ghosts.forEach(function (sites, tok) {
    var id = 'ghost:' + tok;
    present.add(id);
    els.push({ data: { id: id, label: tok, kind: idKind(tok), sites: sites }, classes: 'ghost' });
  });

  if (showCode) {
    model.codeFiles.forEach(function (pth) {
      var id = 'code:' + pth;
      present.add(id);
      els.push({ data: { id: id, label: pth.split('/').pop(), full: pth }, classes: 'code' });
    });
  }

  model.edges.forEach(function (e, i) {
    if (e.to.startsWith('code:') && !showCode) return;
    if (e.from.startsWith('doc:') && !present.has(e.from)) docNode(e.from.slice(4));
    if (!present.has(e.from) || !present.has(e.to)) return;
    var cls = e.to.startsWith('code:') ? 'bind' : (e.to.startsWith('ghost:') ? 'dangle' : 'ref');
    els.push({ data: { id: 'e' + i, source: e.from, target: e.to,
                       weight: e.sites.length, sites: e.sites }, classes: cls });
  });
  return els;
}

// ---------- public API

var api = {
  STRICT: STRICT, NORMATIVE: NORMATIVE,
  REGISTERED_PREFIXES: REGISTERED_PREFIXES, KIND_CLASSES: KIND_CLASSES,
  stripComment: stripComment, parseFlow: parseFlow, parseYamlSubset: parseYamlSubset,
  frontMatter: frontMatter, discover: discover, idKind: idKind, kindClass: kindClass,
  buildWeb: buildWeb, toElements: toElements,
};
return api;
});

// ---------- Node CLI (what tests/run.sh executes; not reached in a browser)
//   node idweb.js <repo-root>              findings run (exit 1 on errors)
//   node idweb.js <repo-root> --data <out> also write a snapshot data file
//                                          (window.__DICTUM_TEST_FILES__ = …)
//                                          the viewer's test hook consumes
if (typeof require !== 'undefined' && typeof module !== 'undefined' &&
    require.main === module) {
  var fs = require('fs'), path = require('path');
  var DictumIdweb = module.exports;
  var argv = process.argv.slice(2);
  var dataOut = null, di = argv.indexOf('--data');
  if (di >= 0) { dataOut = argv[di + 1]; argv.splice(di, 2); }
  var root = argv[0];
  if (!root) { console.error('usage: node idweb.js <repo-root> [--data <out.js>]'); process.exit(2); }
  var SKIP = { '.git': 1, node_modules: 1, __pycache__: 1, vendor: 1, dist: 1, build: 1 };
  var MAX = 2 * 1024 * 1024;

  // pass 1: paths only — a repo's full text does not fit in memory and is
  // not needed; only docs, manifest/bindings, and binding-locator files are.
  var paths = [];
  (function walk(dir) {
    fs.readdirSync(dir, { withFileTypes: true }).forEach(function (e) {
      if (SKIP[e.name]) return;
      var p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.isFile()) paths.push(path.relative(root, p).split(path.sep).join('/'));
    });
  })(root);

  function readText(rel) {
    var p = path.join(root, rel);
    try {
      if (fs.statSync(p).size <= MAX) return fs.readFileSync(p, 'utf8');
    } catch (err) { /* unreadable: existence-only */ }
    return null;
  }

  // pass 2: texts for the needed slice
  var DOC_PATS = [/^docs\/[^/]+\.md$/, /^docs\/concerns\/[^/]+\.md$/, /^[^/]+\.md$/];
  var need = new Set(['docs/manifest.yaml', 'manifest.yaml',
                      'docs/bindings.yaml', 'bindings.yaml']);
  paths.forEach(function (rel) {
    if (DOC_PATS.some(function (r) { return r.test(rel); })) need.add(rel);
  });
  ['docs/bindings.yaml', 'bindings.yaml'].forEach(function (b) {
    if (paths.indexOf(b) < 0) return;
    var parsed = DictumIdweb.parseYamlSubset(readText(b) || '');
    (function collectPaths(v) {   // every `path:` value anywhere in the map
      if (Array.isArray(v)) v.forEach(collectPaths);
      else if (v && typeof v === 'object') {
        if (typeof v.path === 'string') need.add(v.path);
        Object.keys(v).forEach(function (k) { collectPaths(v[k]); });
      }
    })(parsed);
  });
  var files = paths.map(function (rel) {
    return { path: rel, text: need.has(rel) ? readText(rel) : null };
  });

  if (dataOut) {
    fs.writeFileSync(dataOut,
      'window.__DICTUM_TEST_FILES__ = ' + JSON.stringify(files) + ';\n');
    console.log('snapshot data written: ' + dataOut + ' (' + files.length + ' paths)');
  }
  var model = DictumIdweb.buildWeb(files);
  model.findings.forEach(function (f) {
    console.log(f.sev.padEnd(5) + ' [' + f.check + '] ' + f.where + ' — ' + f.msg);
  });
  console.log(model.counts.errors + ' error(s), ' + model.counts.warnings +
    ' warning(s) — ' + model.counts.owned + ' owned ID(s), ' +
    model.counts.references + ' reference site(s), ' + model.counts.docs + ' doc(s)');
  process.exit(model.counts.errors ? 1 : 0);
}
