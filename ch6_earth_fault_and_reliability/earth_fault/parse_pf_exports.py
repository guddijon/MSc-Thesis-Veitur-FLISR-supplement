"""Parse PowerFactory Flexible Data exports of the earth-fault anchor runs into the common phasor format.

Per anchor run two exports (Spread Sheet Format, no filter), named after the anchor:
  <anchor>_lne.txt   Lines: phase current magnitude and angle, phases A, B, C, at Terminal i and Terminal j
  <anchor>_term.txt  Terminals: line-ground voltage magnitude and angle, phases A, B, C
The residual current of a bay is rebuilt from the three phase currents of the cable segment it measures into, at the
segment end at the bay (tables/bays.csv): 3 I0 = Ia + Ib + Ic (PowerFactory counts a branch current at either end as
flowing from the terminal into the branch, i.e. toward the cable). The zero-sequence voltage at the bay's reference
terminal is V0 = (Va + Vb + Vc) / 3. Building the sequence quantities from phase values avoids any dependence on the
zero-sequence variable names, which differ between PowerFactory versions; if zero-sequence columns are exported as
well they are ignored.

Usage: parse_pf_exports.py <export_dir> <out_phasors.csv> [source_label]
"""
import os, re, sys, csv, math, cmath
HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, 'tables')
A = cmath.exp(2j * math.pi / 3)

def read_pf(fn):
    raw = open(fn, 'rb').read()
    if raw[:2] in (b'\xff\xfe', b'\xfe\xff'): t = raw.decode('utf-16')
    elif raw[1:200:2].count(0) > 50: t = raw.decode('utf-16-le', errors='replace')
    else:
        raw = raw.replace(b'\x00', b'')
        try: t = raw.decode('utf-8-sig')
        except UnicodeDecodeError: t = raw.decode('cp1252')
    lines = [l for l in t.splitlines() if l.strip()]
    h1 = lines[0].split('\t'); h2 = lines[1].split('\t')
    cols = [(a.strip(), (h2[i].strip() if i < len(h2) else '')) for i, a in enumerate(h1)]
    data = [l.split('\t') for l in lines[2:]]
    return cols, data

def num(s):
    s = s.strip().replace(',', '.')
    try: return float(s)
    except ValueError: return None

CUR = r'(Current|^I\b|^Ik")'                    # "Phase Current, Magnitude A", short "I, Magnitude A", or the
                                                 # short-circuit headings 'Ik" A' (magnitude) and 'Ik", Angle A'
VLG = r'(Line-Ground Voltage|^U\b|^u\b)'           # "Line-Ground Voltage, Magnitude A" or short "U, Magnitude A"

def pick(cols, qty_rx, part, phase, end=None, unit=None):
    """index of the column whose description matches quantity (current / line-ground voltage), part (Magnitude /
    Angle), phase, for branches the terminal (i / j) named in the unit row, and if given the unit (the kV and p.u.
    magnitudes of the line-ground voltage share one description)"""
    for k, (d, u) in enumerate(cols):
        dl = d.lower()
        if not re.search(qty_rx, d) or 'zero' in dl or 'line-line' in dl or 'nom' in dl: continue
        if part == 'Magnitude' and re.match(r'^Ik"\s*' + phase + r'$', d.strip()): pass   # 'Ik" A' is the magnitude
        elif not re.search(part + r'\s*' + phase + r'\b', d, re.I): continue
        if end is not None and not re.search(r'Terminal\s+' + end + r'\b', u, re.I): continue
        if unit is not None and not re.search(r'(^|\s)' + re.escape(unit) + r'$', u.strip(), re.I): continue
        return k
    return None

def unit_scale(u):
    u = u.lower()
    if 'ka' in u.split(): return 1000.0
    if re.search(r'\bka\b', u): return 1000.0
    return 1.0

def parse_anchor(d, anchor):
    lc, ld = read_pf(os.path.join(d, f'{anchor}_lne.txt'))
    tc, td = read_pf(os.path.join(d, f'{anchor}_term.txt'))
    I = {}
    for end in ('i', 'j'):
        idx = {ph: (pick(lc, CUR, 'Magnitude', ph, end), pick(lc, CUR, 'Angle', ph, end)) for ph in 'ABC'}
        if None in [x for p in idx.values() for x in p]:
            raise SystemExit(f'{anchor}_lne.txt: phase current magnitude/angle at Terminal {end} not found; columns {lc}')
        sc = unit_scale(lc[idx['A'][0]][1])
        for row in ld:
            name = row[0].strip(); tot = 0j
            for ph in 'ABC':
                m, a = num(row[idx[ph][0]]), num(row[idx[ph][1]])
                if m is None or a is None: tot = None; break
                tot += m * sc * cmath.exp(1j * math.radians(a))
            I[(name, end)] = tot
    V = {}
    idx = {ph: (pick(tc, VLG, 'Magnitude', ph, unit='kV'), pick(tc, VLG, 'Angle', ph, unit='deg')) for ph in 'ABC'}
    if None in [x for p in idx.values() for x in p]:
        raise SystemExit(f'{anchor}_term.txt: line-ground voltage magnitude (kV) / angle not found; columns {tc}')
    for row in td:
        name = row[0].strip(); tot = 0j
        for ph in 'ABC':
            m, a = num(row[idx[ph][0]]), num(row[idx[ph][1]])
            if m is None or a is None: tot = None; break
            tot += m * cmath.exp(1j * math.radians(a))
        V[name] = None if tot is None else tot / 3
    return I, V

def main(d, out, source='pf_gui'):
    anchors = {r['anchor']: r['case_id'] for r in csv.DictReader(open(os.path.join(T, 'anchor_runs.csv')))}
    bays = list(csv.DictReader(open(os.path.join(T, 'bays.csv'))))
    E = 11.15 / math.sqrt(3)
    n = 0
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['case_id', 'source', 'bay_id', 'station', 'I0x3_A', 'ang_I0x3_deg', 'V0_kV', 'ang_V0_deg', 'E_kV', 'expected'])
        for anchor, cid in anchors.items():
            if not os.path.exists(os.path.join(d, f'{anchor}_lne.txt')): continue
            I, V = parse_anchor(d, anchor)
            seen = {}
            for b in bays:
                cur = I.get((b['cable_segment'], b['segment_end_at_bay']))
                if cur is None: continue
                seen[b['bay_id']] = seen.get(b['bay_id'], 0j) + cur
            for b in bays:
                bid = b['bay_id']
                if bid not in seen: continue
                v0 = V.get(b['v0_reference_terminal'])
                if v0 is None: continue
                cur = seen.pop(bid)
                w.writerow([cid, source, bid, b['station'], f'{abs(cur):.5f}', f'{math.degrees(cmath.phase(cur)):.3f}',
                            f'{abs(v0):.6f}', f'{math.degrees(cmath.phase(v0)):.3f}', f'{E:.5f}', ''])
                n += 1
    print(f'{n} bay rows written to {out}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'pf_gui')
