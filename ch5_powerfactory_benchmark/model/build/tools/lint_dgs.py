"""Consistency checks of a DGS file (FIDs, pointers, column counts, decimal separators, types, cubicles).
Usage: python3 lint_dgs.py file.dgs"""
import sys, re, collections
path = sys.argv[1]
raw = open(path, 'rb').read()
print("BOM:", raw[:3] == b'\xef\xbb\xbf')
txt = raw.decode('utf-8-sig')
lines = txt.splitlines()
tables = {}   # name -> (cols, [(lineno, fields)])
cur = None
for i, l in enumerate(lines, 1):
    if l.startswith('$$'):
        parts = l[2:].split(';')
        cur = parts[0]
        tables.setdefault(cur, (parts[1:], []))
        continue
    if cur is None or not l.strip() or l.startswith('*'):
        continue
    tables[cur][1].append((i, l.strip().split(';')))

print("\n== row counts ==")
for t, (cols, rows) in tables.items():
    print(f"{t:14s} {len(rows):5d}")

# FID uniqueness + pointer index
fid2 = {}
dups = []
for t, (cols, rows) in tables.items():
    if t in ('General', 'Matrix'): continue
    for ln, f in rows:
        if f[0] in fid2: dups.append((f[0], fid2[f[0]][0], t, ln))
        else: fid2[f[0]] = (t, ln, f)
print("\n== duplicate FIDs ==", len(dups)); [print(d) for d in dups[:10]]

# column count mismatches
print("\n== column count mismatches ==")
for t, (cols, rows) in tables.items():
    for ln, f in rows:
        if len(f) != len(cols):
            print(t, ln, len(f), "vs", len(cols), f[:4])

# decimal separators: for each (r) column, count comma vs point vs other
print("\n== numeric fields: comma / point / bad ==")
num_re_pt = re.compile(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$')
num_re_cm = re.compile(r'^-?\d+(,\d+)?([eE][-+]?\d+)?$')
for t, (cols, rows) in tables.items():
    c_pt = c_cm = c_bad = c_int_only = 0
    bad = []
    for ln, f in rows:
        for c, v in zip(cols, f):
            if '(r)' in c or t == 'Matrix' and c.startswith('Val'):
                if v == '': continue
                if ',' in v and num_re_cm.match(v): c_cm += 1
                elif '.' in v and num_re_pt.match(v): c_pt += 1
                elif num_re_pt.match(v): c_int_only += 1
                else: c_bad += 1; bad.append((ln, c, v))
    if c_pt or c_cm or c_bad:
        print(f"{t:12s} comma={c_cm:5d} point={c_pt:5d} intonly={c_int_only:5d} bad={c_bad}", bad[:3])

# pointer resolution
print("\n== unresolved pointers ==")
unres = collections.Counter(); ex = {}
for t, (cols, rows) in tables.items():
    for ln, f in rows:
        for c, v in zip(cols, f):
            if c.endswith('(p)') and v != '' and v not in fid2:
                unres[(t, c)] += 1; ex.setdefault((t, c), (ln, v))
for k, n in unres.items(): print(k, n, ex[k])
print("total", sum(unres.values()))

# elements with empty fold_id
print("\n== empty fold_id by table ==")
for t, (cols, rows) in tables.items():
    if 'fold_id(p)' in cols:
        idx = cols.index('fold_id(p)')
        n = sum(1 for ln, f in rows if f[idx] == '')
        if n: print(t, n)

# empty typ_id
print("\n== empty typ_id by table ==")
for t, (cols, rows) in tables.items():
    if 'typ_id(p)' in cols:
        idx = cols.index('typ_id(p)')
        n = sum(1 for ln, f in rows if f[idx] == '')
        if n: print(t, n, "of", len(rows))

def col(t, name):
    cols, rows = tables[t]; return cols.index(name)
def fl(v): return float(v.replace(',', '.')) if v else None

# ElmLne dline stats
cols, rows = tables['ElmLne']; i = col('ElmLne', 'dline(r)'); ity = col('ElmLne','typ_id(p)')
d = [fl(f[i]) for ln, f in rows]
print("\n== ElmLne dline km: min/max/mean ==", min(d), max(d), sum(d)/len(d), "count>5:", sum(1 for x in d if x > 5), "count==0:", sum(1 for x in d if x == 0))
print("ElmLne typ_id classes:", collections.Counter(fid2[f[ity]][0] for ln, f in rows if f[ity] in fid2))

# TypLne
cols, rows = tables['TypLne']
print("\n== TypLne ==")
for ln, f in rows:
    r = dict(zip(cols, f))
    print(f"{r['loc_name(a:80)'][:38]:38s} u={r['uline(r)']:>5} sline={r['sline(r)']:>6} r1={r['rline(r)']:>8} x1={r['xline(r)']:>8} r0={r['rline0(r)']:>8} x0={r['xline0(r)']:>8} b1={r['bline(r)']:>8} b0={r['bline0(r)']:>8} nph={r['nlnph(i)']} nneut={r['nneutral(i)']} mlei={r['mlei(a:4)']} | {r['desc(a:255)'][:60]}")

# TypTr2
cols, rows = tables['TypTr2']
print("\n== TypTr2 ==")
for ln, f in rows:
    r = dict(zip(cols, f))
    print(f"{r['loc_name(a:80)'][:36]:36s} S={r['strn(r)']:>6} Uh={r['utrn_h(r)']:>5} Ul={r['utrn_l(r)']:>5} uk={r['uktr(r)']:>5} Pcu={r['pcutr(r)']:>7} uk0={r['uk0tr(r)']:>5} ur0={r['ur0tr(r)']:>5} vg={r['tr2cn_h(a:4)']}{r['tr2cn_l(a:4)']}{r['nt2ag(r)']} pfe={r['pfe(r)']} i0={r['curmg(r)']} tap={r['itapch(i)']}/{r['dutap(r)']}/{r['nntap0(i)']}/{r['ntpmn(i)']}/{r['ntpmx(i)']} | {r['desc(a:255)'][:50]}")

# TypTr3
cols, rows = tables['TypTr3']
print("\n== TypTr3 ==")
for ln, f in rows:
    r = dict(zip(cols, f)); print({k: v for k, v in r.items() if k not in ('OP(a:1)','FID(a:40)')})

# ElmTr2 usage of types
cols, rows = tables['ElmTr2']; ity = col('ElmTr2','typ_id(p)')
print("\n== ElmTr2 type usage ==")
print(collections.Counter(fid2[f[ity]][2][2] if f[ity] in fid2 else 'MISSING' for ln, f in rows))
print("ElmTr2 nntap values:", collections.Counter(f[col('ElmTr2','nntap(i)')] for ln,f in rows))

# ElmTerm
cols, rows = tables['ElmTerm']
print("\n== ElmTerm uknom / iUsage / systype ==")
print(collections.Counter((f[col('ElmTerm','uknom(r)')], f[col('ElmTerm','iUsage(i)')]) for ln,f in rows))
print("ElmTerm fold classes:", collections.Counter(fid2[f[col('ElmTerm','fold_id(p)')]][0] if f[col('ElmTerm','fold_id(p)')] in fid2 else 'EMPTY/MISSING' for ln,f in rows))

# StaCubic consistency: obj_id -> element; element bus pointers absent in this format (cubicle-based). check cubicles' fold is ElmTerm and obj_id element exists; each branch element should have 2 cubicles
cols, rows = tables['StaCubic']; io = col('StaCubic','obj_id(p)'); ifo = col('StaCubic','fold_id(p)'); ib = col('StaCubic','obj_bus(i)')
cnt = collections.Counter(); fold_cls = collections.Counter(); empty_obj = 0; bus_by_el = collections.defaultdict(list)
for ln, f in rows:
    fold_cls[fid2[f[ifo]][0] if f[ifo] in fid2 else 'MISSING'] += 1
    if f[io] == '': empty_obj += 1
    else: cnt[f[io]] += 1; bus_by_el[f[io]].append(f[ib])
print("\n== StaCubic ==", "fold classes:", dict(fold_cls), "empty obj_id:", empty_obj)
exp = {'ElmLne':2,'ElmCoup':2,'ElmTr2':2,'ElmTr3':3,'ElmLod':1,'ElmXnet':1}
probs = collections.Counter()
for t, (c2, r2) in tables.items():
    if t in exp:
        for ln, f in r2:
            n = cnt.get(f[0], 0)
            if n != exp[t]: probs[(t, n)] += 1
            elif sorted(bus_by_el[f[0]]) != [str(i) for i in range(exp[t])]: probs[(t, 'obj_bus', tuple(sorted(bus_by_el[f[0]])))] += 1
print("elements with wrong cubicle count / obj_bus:", dict(probs))
# cubicles pointing to things that aren't elements
print("obj_id classes:", collections.Counter(fid2[f[io]][0] for ln,f in rows if f[io] in fid2))

# StaSwitch
cols, rows = tables['StaSwitch']
print("\n== StaSwitch ==", "fold classes:", collections.Counter(fid2[f[col('StaSwitch','fold_id(p)')]][0] if f[col('StaSwitch','fold_id(p)')] in fid2 else 'MISSING' for ln,f in rows),
      "aUsage:", collections.Counter(f[col('StaSwitch','aUsage(a)')] for ln,f in rows), "on_off:", collections.Counter(f[col('StaSwitch','on_off(i)')] for ln,f in rows), "typ empty:", sum(1 for ln,f in rows if f[col('StaSwitch','typ_id(p)')]==''))
cols, rows = tables['ElmCoup']
print("== ElmCoup == aUsage:", collections.Counter(f[col('ElmCoup','aUsage(a:4)')] for ln,f in rows), "on_off:", collections.Counter(f[col('ElmCoup','on_off(i)')] for ln,f in rows), "typ empty:", sum(1 for ln,f in rows if f[col('ElmCoup','typ_id(p)')]==''))

# ElmLod
cols, rows = tables['ElmLod']
print("\n== ElmLod == plini values:", collections.Counter(f[col('ElmLod','plini(r)')] for ln,f in rows).most_common(5))

# PLACEHOLDER markers
print("\n== PLACEHOLDER / TODO markers ==")
for t, (cols, rows) in tables.items():
    n = sum(1 for ln, f in rows if any(('PLACEHOLDER' in v or 'TODO' in v) for v in f))
    if n: print(t, n)

# ElmNet / IntGrfnet / IntFolder tree
print("\n== ElmNet rows ==")
for ln,f in tables['ElmNet'][1]: print(f)
print("== IntGrfnet rows ==")
for ln,f in tables['IntGrfnet'][1]: print(f)
print("== IntPrjfolder rows ==")
for ln,f in tables['IntPrjfolder'][1]: print(f)
print("== IntRef rows ==")
for ln,f in tables['IntRef'][1]: print(f, fid2.get(f[4], ('?',))[0])
# which top-level folds reference ElmNet 259/260/261
print("\n== objects per ElmNet (direct children) ==")
c = collections.Counter()
for t, (cols, rows) in tables.items():
    if 'fold_id(p)' in cols:
        idx = cols.index('fold_id(p)')
        for ln, f in rows:
            if f[idx] in ('259','260','261'): c[(f[idx], t)] += 1
print(c)
# OP values
print("\n== OP values ==", collections.Counter(f[1] for t,(cols,rows) in tables.items() if 'OP(a:1)' in cols for ln,f in rows))
# string length overflow
print("\n== string length overflow ==")
for t, (cols, rows) in tables.items():
    for c_i, c in enumerate(cols):
        m = re.search(r'\(a:(\d+)\)', c)
        if m:
            lim = int(m.group(1)); n = sum(1 for ln,f in rows if len(f[c_i]) > lim)
            if n: print(t, c, n)
