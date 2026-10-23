"""Offline sequence-network model of the Akranes 11 kV benchmark for the earth-fault study (thesis Section 3.6.2,
Table 3.5; results Section 6.1).

Purpose: one implementation of the study definitions (locations, configurations, bays, expected directions) that
serves the GUI anchor runs, the PowerFactory script and the offline sweep alike. It reads the model topology from
the DGS export (model/dgs/akranes_11kv_benchmark.dgs, December 2025 base switching), the zero-sequence cable data of
the earth-fault parameter sheet (model/parameters/ef_cable_type_values.csv) and the A20 transformer
zero-sequence impedances of the parameter sheet (S1 0.44 ohm, S2 0.535 ohm seen from 11 kV).

Model: nodal admittance matrices of the energised network in the positive and zero sequence, with closed switches
merged and every cable segment as a pi section. Single-phase-to-earth fault on L1 through R_F:
    I0 = E / (Z1 + Z2 + Z0 + 3 R_F),   Z2 = Z1,   V0(node) = -Z0(node, F) I0,
and the residual current of a bay toward its cable 3 I0 = 3 sum over the cable segments at the bay's cable-side
terminal of [(V0_a - V0_b)/z0 + V0_a y0/2]. Loads and distribution transformers (Dyn, delta on 11 kV) carry no
zero-sequence current and are omitted; loads affect Z1 only marginally and are omitted there too. E is the pre-fault
phase-to-earth voltage at the fault, taken as U_pre/sqrt(3) with U_pre = 11.15 kV unless given (winter-peak level).
Angles in degrees; the bay angle phi is referred to -V0 at the bay's busbar, so sin(phi) > 0 means Direction B
(fault in the direction of the cable) under the convention of thesis Eq. (3.x).
"""
import os, sys, re, csv, math, cmath, collections, copy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# benchmark folder: the parent of this package, or ch5_powerfactory_benchmark beside it (this supplement)
ROOT = next(r for r in (os.path.dirname(HERE), os.path.join(os.path.dirname(os.path.dirname(HERE)), 'ch5_powerfactory_benchmark'))
            if os.path.exists(os.path.join(r, 'scripts', 'radial_pf.py')))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import radial_pf as rp            # DGS parser of the benchmark (parse, f)

DGS = os.path.join(ROOT, 'model', 'dgs', 'akranes_11kv_benchmark.dgs')
CABLE_CSV = os.path.join(ROOT, 'model', 'parameters', 'ef_cable_type_values.csv')
W = 2 * math.pi * 50.0
U_N = 11.0                         # kV line-to-line, all impedances referred to 11 kV
f = rp.f

# ---------------------------------------------------------------- study definitions (single source of truth)
# Configurations: switching applied to the December 2025 base (thesis Table tab:pf_ef_configs)
CONFIGS = {
    'split':    dict(desc='split busbar, coupler open, S1 on busbar 1, S2 on busbar 2 (December 2025 base)', close=[], open_=[], out_terms=[], out_lines=[]),
    'coupled':  dict(desc='coupled busbar (N-1): coupler A20_R11-112_coupler closed, S2 out of service (bay A20_R11-207 open)',
                     close=['A20_R11-112_coupler'], open_=['A20_R11-207'], out_terms=[], out_lines=[]),
    'post02':   dict(desc='SCN-02_restored: D1055 busbar out (bays 1055-1-1, 1055-1-2 open), tie 1031-1-2 closed',
                     close=['1031-1-2'], open_=['1055-1-1', '1055-1-2'], out_terms=['D1055_BB'], out_lines=[]),
    'post06':   dict(desc='SCN-06_isolated: cable D1031-D1032 out (five segments), bays 1031-1-1, 1032-1-1 open',
                     close=[], open_=['1031-1-1', '1032-1-1'], out_terms=[],
                     out_lines=['1031-1032A01 (3 x 150 Al PEX 11kV)', '1031-1032A02 (3 x 150 Al PEX 11kV)', '1031-1032A03 (3 x 150 Al PEX 11kV)',
                                '1031-1032A04 (3 x 150 Al PEX 11kV)', '1031-1032A05 (3 x 150 Al PEX 11kV)']),
    'post11':   dict(desc='SCN-11_isolated: cable D1054-D1067 out, bays 1054-1-1, 1067-1-3 open',
                     close=[], open_=['1054-1-1', '1067-1-3'], out_terms=[], out_lines=['1054-1067A01 (3 x 240 Al PEX 11kV)']),
    'post15':   dict(desc='SCN-15_restored: D1026 busbar out, tie 1003-1-6 closed',
                     close=['1003-1-6'], open_=[], out_terms=['D1026_BB'], out_lines=[]),
}
# Cable data sets (ef_parameter_sheet section B / H)
CABLE_SETS = {
    'main':       dict(XLPE='main', PILC='main', desc='NKT AXAL-TT PRO XLPE, PILC C0/C1 0.83 (values in the model)'),
    'xlpe_sens':  dict(XLPE='sens', PILC='main', desc='Prysmian AXALJ-TT XLPE, PILC main (EF-1b)'),
    'pilc_low':   dict(XLPE='main', PILC='sens', desc='XLPE main, PILC C0/C1 0.60 (EF-2b)'),
    'catalog':    dict(XLPE='now',  PILC='now',  desc='ADMS catalog zero-sequence values (reference only)'),
}
def source_y0(earthed, ports, Sk_MVA=500.0):
    """Zero-sequence admittance matrix (siemens at 11 kV) that the 66 kV side adds between the A20 11 kV terminals of S1
    and S2, from the PowerFactory type data. Internal nodes: the 66 kV busbar (Landsnet grid,
    X0/X1 1, R0/X0 0.1, to earth), the S1 star point and the S2 star point, Kron-reduced onto the 11 kV ports.
      S1 YNyn0, 25 MVA: uk0 9.01 %, ur0 0.314 %, leakage split 0.9 HV / 0.1 LV, magnetising branch 100 x uk0 (reactive).
      S2 YN0yn0d1, 16/16/5.33 MVA: pairwise uk0 HV-MV 7.38 % on 16 MVA, MV-LV 4.92 % and LV-HV 3.68 % on 5.33 MVA,
         Re(uk0) 0.3 % each; the delta tertiary shorts the zero sequence, so it is a path to earth at the star point.
    Both 66 kV star points are solidly earthed (Landsnet SLD), so the S2 delta tertiary loads the 66 kV zero-sequence
    network even when S2's 11 kV side is open or isolated; this couples the two A20 busbars in the earthed variant.
    ports: dict 'S1'/'S2' -> matrix index of the transformer's 11 kV terminal when that star point is earthed and the
    terminal is in the circuit (absent otherwise). Returns {(i, j): y}."""
    zg0 = (U_N ** 2 / Sk_MVA) * complex(0.1, 1) / abs(complex(0.1, 1))
    zb1 = U_N ** 2 / 25.0
    z1 = complex(0.00314, math.sqrt(0.0901 ** 2 - 0.00314 ** 2)) * zb1
    s1 = dict(hv=0.9 * z1, lv=0.1 * z1, m=1j * 100 * 0.0901 * zb1)
    zb2 = U_N ** 2 / 16.0; k = 16.0 / 5.33
    pair = lambda uk, ur: complex(ur, math.sqrt(uk ** 2 - ur ** 2))
    hm, ml, lh = pair(0.0738, 0.003), pair(0.0492, 0.003) * k, pair(0.0368, 0.003) * k
    s2 = dict(hv=(hm + lh - ml) / 2 * zb2, mv=(hm + ml - lh) / 2 * zb2, d=(ml + lh - hm) / 2 * zb2)
    if not earthed: ports = {}
    ext = list(ports); n = len(ext)
    names = ext + ['HV66', 'S1*', 'S2*']; ix = {nm: i for i, nm in enumerate(names)}
    Y = np.zeros((len(names), len(names)), complex)
    def br(a, b_, z, ratio=1.0):
        """branch a (11 kV side) - b_ through an ideal transformer a:b_ = 1:ratio (b_ None = earth)"""
        i = ix[a]; y = 1 / z; Y[i, i] += y
        if b_ is not None:
            j = ix[b_]; Y[j, j] += y / ratio ** 2; Y[i, j] -= y / ratio; Y[j, i] -= y / ratio
    zg66 = zg0 * (66.0 / U_N) ** 2                         # grid zero-sequence impedance in ohm at 66 kV
    Y[ix['HV66'], ix['HV66']] += 1 / zg66
    n1, n2 = U_HV_TAP['S1'] / U_N, U_HV_TAP['S2'] / U_N
    br('S1*', 'HV66', s1['hv'], n1); br('S1*', None, s1['m'])
    br('S2*', 'HV66', s2['hv'], n2); br('S2*', None, s2['d'])
    if 'S1' in ports: br('S1', 'S1*', s1['lv'])
    if 'S2' in ports: br('S2', 'S2*', s2['mv'])
    if not n: return {}
    A, B, C, D = Y[:n, :n], Y[:n, n:], Y[n:, :n], Y[n:, n:]
    R = A - B @ np.linalg.solve(D, C)
    return {(ports[ext[a]], ports[ext[b]]): R[a, b] for a in range(n) for b in range(n)}

EARTHING = {
    'isolated': dict(desc='A20 11 kV star points of S1 and S2 open (variant 2)', earthed=False),
    'earthed':  dict(desc='A20 11 kV star points solidly earthed (variant 1); zero-sequence sources from the type data '
                          'of S1, S2 and the 66 kV grid, coupled through the 66 kV side (source_y0)', earthed=True),
}
# Source: Landsnet 66 kV, Sk'' 500 MVA (run value), R/X 0.1; S1 25 MVA uk 10.01 %, ur 0.314 %; S2 HV-MV 7.53 % on 16 MVA
SOURCE = dict(Sk_MVA=500.0, RX=0.1, S1=(25.0, 0.1001, 0.00314), S2=(16.0, 0.0753, 0.0))
# HV tap voltages at the winter peak of 10 Dec 2025 (snapshot_source_settings.csv): S1 66 kV type, tap -4 x 0.9 % ->
# 63.62 kV; S2 63 kV type, tap +1 x 1.6667 % -> 64.05 kV. Impedances on the 66 kV side are referred to 11 kV with
# these ratios; transformer leakage impedances stay on their 11 kV base.
U_HV_TAP = dict(S1=66.0 * (1 - 4 * 0.009), S2=63.0 * (1 + 1 * 0.016667))

# Fault locations: ('term', terminal) or ('line', segment, fraction from bus1 end)
LOCATIONS = [
    dict(loc='SCN02', kind='term', obj='D1055_BB', feeder='11', role='scenario', note='SCN-02, first substation D1055 (busbar)'),
    dict(loc='SCN06', kind='line', obj='1031-1032A03 (3 x 150 Al PEX 11kV)', frac=0.5, feeder='09', role='scenario', note='SCN-06, midline D1031-D1032 (middle of five segments)'),
    dict(loc='SCN11', kind='line', obj='1054-1067A01 (3 x 240 Al PEX 11kV)', frac=0.5, feeder='11', role='scenario', note='SCN-11, branch D1054-D1067 (cable midpoint)'),
    dict(loc='SCN15', kind='term', obj='D1026_BB', feeder='21', role='scenario', note='SCN-15, substation D1026 (busbar)'),
    dict(loc='F11H', kind='term', obj='A20_C11', feeder='11', role='feeder head', note='circuit 11 head, A20 cable terminal'),
    dict(loc='F11E', kind='term', obj='D1067_BB', feeder='11', role='feeder end', note='circuit 11 remote end, D1067 busbar'),
    dict(loc='F09H', kind='term', obj='A20_C09', feeder='09', role='feeder head', note='circuit 09 head, A20 cable terminal'),
    dict(loc='F09E', kind='term', obj='D1043_BB', feeder='09', role='feeder end', note='circuit 09 remote end, D1043 busbar'),
    dict(loc='F21H', kind='term', obj='A20_C21', feeder='21', role='feeder head', note='circuit 21 head, A20 cable terminal'),
    dict(loc='F21E', kind='term', obj='002', feeder='21', role='feeder end', note='circuit 21 remote end, D1002 11 kV node (terminal 002, where D1002_S-11-01 connects)'),
    # busbar 2 section (circuits 13 and 08): locations of the I_C sweep (see README)
    dict(loc='SCN04', kind='line', obj=None, frac=0.5, feeder='13', role='busbar 2 sweep',
         note='SCN-04 location, circuit 13 between D1023 and D1050: two remotely controlled stations upstream (D1029, D1066) and two downstream (D1025, D1030)'),
    dict(loc='F13H', kind='term', obj='A20_C13', feeder='13', role='busbar 2 sweep', note='circuit 13 head, A20 cable terminal'),
    dict(loc='F13E', kind='term', obj='D1058_BB', feeder='13', role='busbar 2 sweep', note='circuit 13 remote end, D1058 busbar'),
    dict(loc='F08E', kind='term', obj='D1062_BB', feeder='08', role='busbar 2 sweep', note='circuit 08 remote end, D1062 busbar'),
]
BB1_LOCS = ['SCN02', 'SCN06', 'SCN11', 'SCN15', 'F11H', 'F11E', 'F09H', 'F09E', 'F21H', 'F21E']
BB2_LOCS = ['SCN04', 'F13H', 'F13E', 'F08E']
def location(loc_id, rows=None):
    L = dict([l for l in LOCATIONS if l['loc'] == loc_id][0])
    if L['loc'] == 'SCN04' and L['obj'] is None: L['obj'] = scn04_segment(rows or load_rows())
    return L
FAULT_RES = [0, 10, 30, 100, 300, 1000, 3000]
IC_TARGETS = [20, 40, 80, 120, 200]
# ComPass line bays (earth-fault indicators JB11): station, ADMS bay, model element. From holdout_build.MAP (line bays)
# plus D1067 (installed, reads zero in SCADA). D1069 is de-energised in every configuration and is not listed.
BAYS = [
    ('D1001', '101', 'ElmLne', '1001-1026A01 - 13'), ('D1001', '102', 'ElmLne', '1001-1002A01 - 13'),
    ('D1004', '102', 'ElmCoup', '1004-1-2'), ('D1004', '103', 'ElmCoup', '1004-1-3'),
    ('D1025', '101', 'ElmCoup', '1025-1-1'), ('D1025', '102', 'ElmCoup', '1025-1-2'),
    ('D1026', '101', 'ElmLne', '1026-1042A01 - 13'), ('D1026', '102', 'ElmLne', '1001-1026A03 - 13'),
    ('D1029', '101', 'ElmCoup', '1029-1-1'), ('D1029', '102', 'ElmCoup', '1029-1-2'),
    ('D1030', '101', 'ElmCoup', '1030-1-1'), ('D1030', '102', 'ElmCoup', '1030-1-2'),
    ('D1056', '101', 'ElmCoup', '1056-1-1'), ('D1056', '102', 'ElmCoup', '1056-1-2'),
    ('D1061', '101', 'ElmCoup', '1061-1-1'), ('D1061', '102', 'ElmCoup', '1061-1-2'),
    ('D1062', '101', 'ElmCoup', '1062-1-1'), ('D1062', '102', 'ElmCoup', '1062-1-2'),
    ('D1066', '101', 'ElmCoup', '1066-1-1'), ('D1066', '102', 'ElmCoup', '1066-1-2'),
    ('D1067', '102', 'ElmCoup', '1067-1-2'), ('D1067', '103', 'ElmCoup', '1067-1-3'),
    ('D1070', '101', 'ElmLne', '1046-1070A04 - 13'), ('D1070', '102', 'ElmLne', 'A020-1070A03 - 13'),
]

# ---------------------------------------------------------------- data
def load_rows():
    return rp.parse(DGS)

def cable_table():
    T = {}
    for r in csv.DictReader(open(CABLE_CSV)):
        T[r['type']] = r
    return T

def zero_seq_type(typ_row, cab, set_name):
    """(r0, x0 ohm/km, b0 uS/km) of a line type for a cable set; jumper stubs and unknown types keep the DGS values."""
    name = typ_row['loc_name']
    if name not in cab:
        return f(typ_row['rline0']), f(typ_row['xline0']), f(typ_row['bline0'])
    c = cab[name]; which = CABLE_SETS[set_name][c['set']]
    if which == 'now':  return float(c['r0_now']), float(c['x0_now']), float(c['b0_now'])
    if which == 'main': return float(c['r0_main']), float(c['x0_main']), float(c['b0_main_uSkm'])
    return float(c['r0_sens']), float(c['x0_sens']), float(c['b0_sens_uSkm'])

# ---------------------------------------------------------------- network
class Net:
    """Energised network for one configuration, earthing variant, cable set and added shunt capacitance."""
    def __init__(self, rows, config='split', earthing='isolated', cable_set='main', c_add_uF=0.0, c_add_bus='A20_BB1',
                 Sk_MVA=None, location=None):
        self.cfg = config; self.earthing = earthing; self.cable_set = cable_set
        self.c_add_uF = c_add_uF; self.c_add_bus = c_add_bus
        r = copy.deepcopy(rows); C = CONFIGS[config]
        coup = {x['loc_name']: k for k, x in r['ElmCoup'].items()}
        for n in C['close']: r['ElmCoup'][coup[n]]['on_off'] = '1'
        for n in C['open_']: r['ElmCoup'][coup[n]]['on_off'] = '0'
        term_by = {t['loc_name']: k for k, t in r['ElmTerm'].items()}
        out_t = {term_by[n] for n in C['out_terms']}
        out_l = set(C['out_lines'])
        self.rows = r; T = r['ElmTerm']
        self.tname = {k: t['loc_name'] for k, t in T.items()}
        # station of each terminal: 'Dxxxx' from its own name or, for the numbered bay terminals of GIS-style
        # stations, from the parent substation object (named 'xxxx-n'); junctions and cable nodes have none
        sub = r['ElmSubstat']; self.tstation = {}
        for k, t in T.items():
            m = re.match(r'^(D\d{4})', t['loc_name'])
            if m: self.tstation[k] = m.group(1); continue
            sb = sub.get(t['fold_id'])
            if sb and re.match(r'^\d{4}', sb['loc_name']): self.tstation[k] = 'D' + sb['loc_name'][:4]
        # cubicles: element -> {bus index: terminal}, skipping open cubicle switches and out-of-service terminals
        sw_open = {s['fold_id'] for s in r['StaSwitch'].values() if s['on_off'] == '0'}
        el = collections.defaultdict(dict)
        for c in r['StaCubic'].values():
            if c['FID'] in sw_open or c['fold_id'] in out_t: continue
            el[c['obj_id']][int(c['obj_bus'])] = c['fold_id']
        # union-find over closed couplers
        par = {k: k for k in T}
        def find(a):
            while par[a] != a: par[a] = par[par[a]]; a = par[a]
            return a
        for k, x in r['ElmCoup'].items():
            t = el.get(k, {})
            if x['on_off'] == '1' and 0 in t and 1 in t: par[find(t[0])] = find(t[1])
        self.find = find
        cab = cable_table(); typ = r['TypLne']
        self.lines = []        # (name, terminal a, terminal b, z1, y1, z0, y0)
        for k, x in r['ElmLne'].items():
            t = dict(el.get(k, {}))
            if x['loc_name'] in out_l or not t: continue
            if len(t) == 1:
                # one end behind an open switch (a normally-open tie): the cable stays energised from the other end
                # and carries its full charging current, as in PowerFactory; its open end becomes a floating node
                open_end = f'open_end:{k}'; par[open_end] = open_end; t[1 - next(iter(t))] = open_end
            ty = typ[x['typ_id']]; L = f(x['dline'])
            r1, x1, b1 = f(ty['rline']), f(ty['xline']), f(ty['bline'])
            r0, x0, b0 = zero_seq_type(ty, cab, cable_set)
            self.lines.append(dict(name=x['loc_name'], a=t[0], b=t[1], L=L,
                                   z1=complex(r1, x1) * L, y1=1j * b1 * 1e-6 * L, z0=complex(r0, x0) * L, y0=1j * b0 * 1e-6 * L))
        # transformers S1 (ElmTr2) and S2 (ElmTr3): LV/MV terminal and in-service flag
        self.src = {}
        for k, x in r['ElmTr2'].items():
            if x['loc_name'] == 'S1':
                t = el.get(k, {}); self.src['S1'] = t.get(1) if (x['outserv'] == '0' and 0 in t) else None
        for k, x in r['ElmTr3'].items():
            if x['loc_name'] == 'S2':
                t = el.get(k, {}); self.src['S2'] = t.get(1) if (x['outserv'] == '0' and 0 in t) else None
        # a transformer whose 11 kV bay is open is out of the circuit
        self.Sk = Sk_MVA or SOURCE['Sk_MVA']
        # energised nodes: union nodes connected to a source through lines; a transformer whose 11 kV node carries no
        # line (its bay open, e.g. S2 in the coupled N-1 configuration) is out of the circuit
        adj = collections.defaultdict(set)
        for ln in self.lines:
            a, b = find(ln['a']), find(ln['b']); adj[a].add(b); adj[b].add(a)
        for s_ in list(self.src):
            if self.src[s_] and not adj.get(find(self.src[s_])): self.src[s_] = None
        start = {find(t) for t in self.src.values() if t}
        seen = set(start); stack = list(start)
        while stack:
            n = stack.pop()
            for m in adj[n]:
                if m not in seen: seen.add(m); stack.append(m)
        self.energised = seen
        self.lines = [ln for ln in self.lines if find(ln['a']) in seen and find(ln['b']) in seen]
        self.loc = None
        if location: self.insert_fault_node(location)
        self.nodes = sorted(seen | ({'FAULT'} if self.loc and self.loc.get('node') == 'FAULT' else set()), key=str)
        self.idx = {n: i for i, n in enumerate(self.nodes)}

    def node(self, term):
        return 'FAULT' if term == 'FAULT' else self.find(term)

    def insert_fault_node(self, loc):
        """Split a line segment at the fault point (line faults); terminal faults use the merged node."""
        self.loc = dict(loc)
        if loc['kind'] == 'term':
            tid = [k for k, n in self.tname.items() if n == loc['obj']]
            if not tid: raise KeyError(loc['obj'])
            if self.find(tid[0]) not in self.energised: raise KeyError(f"{loc['obj']} not energised in {self.cfg}")
            self.loc['node'] = self.find(tid[0]); return
        ln = [x for x in self.lines if x['name'] == loc['obj']]
        if not ln: raise KeyError(f"line {loc['obj']} not energised in {self.cfg}")
        ln = ln[0]; p = loc.get('frac', 0.5); self.lines.remove(ln)
        for (a, b, q) in ((ln['a'], 'FAULT', p), ('FAULT', ln['b'], 1 - p)):
            self.lines.append(dict(name=ln['name'] + (' [a]' if a != 'FAULT' else ' [b]'), a=a, b=b, L=ln['L'] * q,
                                   z1=ln['z1'] * q, y1=ln['y1'] * q, z0=ln['z0'] * q, y0=ln['y0'] * q, parent=ln['name']))
        self.loc['node'] = 'FAULT'

    def Y(self, seq):
        n = len(self.nodes); Y = np.zeros((n, n), complex)
        for ln in self.lines:
            i, j = self.idx[self.node(ln['a'])], self.idx[self.node(ln['b'])]
            z, y = (ln['z1'], ln['y1']) if seq == 1 else (ln['z0'], ln['y0'])
            if i == j: Y[i, i] += y; continue
            Y[i, i] += 1 / z + y / 2; Y[j, j] += 1 / z + y / 2; Y[i, j] -= 1 / z; Y[j, i] -= 1 / z
        if seq == 1:
            zg66 = (66.0 ** 2 / self.Sk) * complex(SOURCE['RX'], 1) / abs(complex(SOURCE['RX'], 1))
            for s in ('S1', 'S2'):
                t = self.src.get(s)
                if not t: continue
                zg = zg66 * (U_N / U_HV_TAP[s]) ** 2
                S, uk, ur = SOURCE[s]; zt = complex(ur, math.sqrt(uk ** 2 - ur ** 2)) * U_N ** 2 / S
                k = self.idx[self.node(t)]; Y[k, k] += 1 / (zg + zt)   # grid and transformer in series (66 kV coupling neglected)
        else:
            ports = {s: self.idx[self.node(self.src[s])] for s in ('S1', 'S2') if self.src.get(s)}
            for (i, j), y in source_y0(EARTHING[self.earthing]['earthed'], ports, self.Sk).items(): Y[i, j] += y
        if self.c_add_uF:
            tid = [k for k, nm in self.tname.items() if nm == self.c_add_bus][0]
            k = self.idx[self.node(tid)]; Y[k, k] += 1j * W * self.c_add_uF * 1e-6     # per-phase capacitance, C0 = C1
        return Y

    def solve(self, RF_list, U_pre_kV=11.15):
        """Returns per R_F: fault quantities and node V0 phasors (kV, phase-to-earth zero sequence)."""
        F = self.idx[self.loc['node']]
        Z1 = np.linalg.inv(self.Y(1)); Z0 = np.linalg.inv(self.Y(0))
        E = U_pre_kV / math.sqrt(3)
        out = []
        for RF in RF_list:
            I0 = E / (2 * Z1[F, F] + Z0[F, F] + 3 * RF)          # kA (kV / ohm)
            V0 = -Z0[:, F] * I0
            out.append(dict(RF=RF, I0=I0, V0=V0, E=E, Z1=Z1[F, F], Z0=Z0[F, F]))
        return out

    # ------------------------------------------------ measurement points
    def bay_lines(self, kind, name, station=None):
        """(terminal at which the bay measures, list of (line, sign)) for a bay; sign +1 if the line's a-end is there.
        Returns (None, []) if the bay is not in an energised part or its own switch is open."""
        r = self.rows
        if kind == 'ElmLne':
            # the bay measures into the named cable segment at its end inside the station (station busbar or the
            # numbered bay terminal of a GIS-style station, which a jumper stub ties to the busbar)
            seg = [ln for ln in self.lines if ln.get('parent', ln['name']) == name]
            st = None
            for ln in seg:
                for end in ('a', 'b'):
                    if ln[end] != 'FAULT' and self.tstation.get(ln[end]) == station: st = ln[end]
            if st is None: return None, []
            return st, [(ln, +1 if ln['a'] == st else -1) for ln in seg if st in (ln['a'], ln['b'])]
        k = [x for x, y in r['ElmCoup'].items() if y['loc_name'] == name]
        if not k or r['ElmCoup'][k[0]]['on_off'] != '1': return None, []
        cub = [c for c in r['StaCubic'].values() if c['obj_id'] == k[0]]
        terms = {int(c['obj_bus']): c['fold_id'] for c in cub}
        cable_t = [t for t in terms.values() if not self.tname[t].endswith('_BB') and not self.tname[t].startswith('A20_BB')]
        if not cable_t: return None, []
        ct = cable_t[0]
        return ct, [(ln, +1 if ln['a'] == ct else -1) for ln in self.lines if ct in (ln['a'], ln['b'])]

    def bay_current(self, V0, kind, name, station=None):
        ct, lines = self.bay_lines(kind, name, station)
        if not lines: return None
        I = 0j
        for ln, s in lines:
            a, b = (ln['a'], ln['b']) if s > 0 else (ln['b'], ln['a'])
            va, vb = V0[self.idx[self.node(a)]], V0[self.idx[self.node(b)]]
            I += (va - vb) / ln['z0'] + va * ln['y0'] / 2
        return 3 * I                                           # kA, residual current 3 I0 toward the cable

    def expected_direction(self, kind, name, station=None):
        """'B' if the fault lies in the direction of the bay's cable (reachable from the cable without passing the
        bay's own node), else 'A'. Radial energised network with open ties."""
        ct, lines = self.bay_lines(kind, name, station)
        if not lines: return None
        busnode = self.node(ct) if kind == 'ElmCoup' else self.node(ct)
        F = self.loc['node']
        if F == busnode: return 'A'
        adj = collections.defaultdict(set)
        for ln in self.lines:
            a, b = self.node(ln['a']), self.node(ln['b']); adj[a].add(b); adj[b].add(a)
        starts = set()
        for ln, s in lines:
            far = ln['b'] if s > 0 else ln['a']; starts.add(self.node(far))
        seen = set(starts); stack = list(starts)
        while stack:
            n = stack.pop()
            if n == F: return 'B'
            for m in adj[n]:
                if m != busnode and m not in seen: seen.add(m); stack.append(m)
        return 'B' if F in seen else 'A'

    def feeder_heads(self):
        """A20 feeder bays in service: (bay name, feeder number)."""
        out = []
        for k, x in self.rows['ElmCoup'].items():
            n = x['loc_name']
            if n.startswith('A20_R11-') and 'coupler' not in n and x['on_off'] == '1':
                out.append((n, n[-2:]))
        return out

    def capacitance_uF(self):
        """Total zero-sequence capacitance (uF per phase) of the energised network, per A20 busbar group."""
        return sum(ln['y0'].imag / W * 1e6 for ln in self.lines) + (self.c_add_uF or 0)

def ic_from_c(C_uF, U_kV=11.0):
    return 3 * W * C_uF * 1e-6 * U_kV / math.sqrt(3) * 1e3            # A

def c_for_ic(I_A, U_kV=11.0):
    return I_A / (3 * W * U_kV / math.sqrt(3) * 1e3) * 1e6            # uF per phase

def scn04_segment(rows):
    """Middle segment of the cable path D1023-D1050 (SCN-04 location)."""
    names = sorted(x['loc_name'] for x in rows['ElmLne'].values() if x['loc_name'].startswith('1023-1050') or x['loc_name'].startswith('1050-1023'))
    return names[len(names) // 2] if names else None
