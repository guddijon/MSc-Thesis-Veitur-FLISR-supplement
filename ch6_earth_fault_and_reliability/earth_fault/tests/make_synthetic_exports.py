"""Round-trip test of parse_pf_exports.py: writes Flexible Data exports in the PowerFactory format (UTF-16, two header
rows, comma decimals, phase values at Terminal i and j) from the offline phasors of the anchor cases, with an arbitrary
positive-sequence load current and voltage added, so that parsing them back must reproduce the offline residual
currents and zero-sequence voltages exactly."""
import os, sys, csv, math, cmath, random
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(HERE, 'tables'); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
A = cmath.exp(2j * math.pi / 3); random.seed(1)
anchors = {r['anchor']: r['case_id'] for r in csv.DictReader(open(os.path.join(T, 'anchor_runs.csv')))}
bays = list(csv.DictReader(open(os.path.join(T, 'bays.csv'))))
ph = {}
for r in csv.DictReader(open(os.path.join(HERE, 'results', 'offline_phasors.csv'))): ph[(r['case_id'], r['bay_id'])] = r
DEC = dict(I=int(os.environ.get('DEC_I', 6)), ang=int(os.environ.get('DEC_ANG', 3)), U=int(os.environ.get('DEC_U', 5)))
SHORT = os.environ.get('SHORT_HEADERS', '1') == '1'
fmt = lambda x, d: f'{x:.{d}f}'.replace('.', ',')
def write(fn, cols, units, rows):
    txt = '\t'.join(cols) + '\r\n' + '\t'.join(units) + '\r\n' + ''.join('\t'.join(r) + '\r\n' for r in rows)
    open(fn, 'wb').write(txt.encode('utf-16'))
for anc, cid in anchors.items():
    seg = {}; term = {}
    for b in bays:
        r = ph.get((cid, b['bay_id']))
        if not r: continue
        I0 = float(r['I0x3_A']) / 3000 * cmath.exp(1j * math.radians(float(r['ang_I0x3_deg'])))   # kA, per phase
        I1 = random.uniform(0.005, 0.15) * cmath.exp(1j * math.radians(random.uniform(-60, 60)))
        seg[(b['cable_segment'], b['segment_end_at_bay'])] = [I1 + I0, A * A * I1 + I0, A * I1 + I0]
        V0 = float(r['V0_kV']) * cmath.exp(1j * math.radians(float(r['ang_V0_deg']))); V1 = float(r['E_kV'])
        term[b['v0_reference_terminal']] = [V1 + V0, A * A * V1 + V0, A * V1 + V0]
    # lines as defined in the GUI: three result columns, then I and phii interleaved bus1/bus2 per phase
    cols = ['Name', 'In Folder', 'Grid', 'Loading, max.', 'Capacitive Losses, total', 'Nominal Current']
    units = ['', '', '', '%', 'Mvar', 'kA']; spec = []
    for q in ('I', 'phii'):
        for p in 'ABC':
            for end in ('i', 'j'):
                cols.append(f'Phase Current, {"Magnitude" if q == "I" else "Angle"} {p}')
                units.append(f'Terminal {end} in {"kA" if q == "I" else "deg"}'); spec.append((q, p, end))
    rows = []
    for nm in sorted({s for s, e in seg}):
        r = [nm, 'VeiturRegion', 'VeiturRegion', '12,3', '', '0,24']
        for q, p, end in spec:
            x = seg.get((nm, end), [0j, 0j, 0j])['ABC'.index(p)]
            r.append(fmt(abs(x), DEC['I']) if q == 'I' else fmt(math.degrees(cmath.phase(x)), DEC['ang']))
        rows.append(r)
    write(os.path.join(OUT, f'{anc}_lne.txt'), cols, units, rows)
    # terminals: nominal L-L voltage, U (kV), u (p.u.), angle; short or long headers
    lab = (lambda q, p: f'{q}, {"Angle" if q == "phi" else "Magnitude"} {p}') if SHORT else (lambda q, p: f'Line-Ground Voltage, {"Angle" if q == "phi" else "Magnitude"} {p}')
    cols = ['Name', 'In Folder', 'Grid', 'Nom.L-L Volt.'] + [lab('U', p) for p in 'ABC'] + [lab('u', p) for p in 'ABC'] + \
           [(f'U, Angle {p}' if SHORT else lab('phi', p)) for p in 'ABC']
    units = ['', '', '', 'kV'] + ['kV'] * 3 + ['p.u.'] * 3 + ['deg'] * 3
    write(os.path.join(OUT, f'{anc}_term.txt'), cols, units,
          [[nm, 'VeiturRegion', 'VeiturRegion', '11,0'] + [fmt(abs(x), DEC['U']) for x in v] + [fmt(abs(x) / (11 / math.sqrt(3)), 4) for x in v]
           + [fmt(math.degrees(cmath.phase(x)), DEC['ang']) for x in v] for nm, v in sorted(term.items())])
print('synthetic exports written for', len(anchors), 'anchors')
