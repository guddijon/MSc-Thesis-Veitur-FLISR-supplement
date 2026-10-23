"""Chapter 6 earth-fault results from the validated offline sweep. Writes results/ch6/*.csv:

  ic_results.csv           solid-fault capacitive current, energised cable and largest feeder share of each system
  feeder_charging.csv      own charging current of every A20 feeder per configuration (solid fault elsewhere, V0 = E)
  v0_coverage.csv          |V0|/E_n against R_F per system, offline model and Eq. (3.x)
  v0_rf_limits.csv         largest fault resistance at which |V0|/E_n stays above 10, 20 and 30 % per system
  fpi_signatures.csv       |3I0| sin(phi) at the FPIs nearest SCN-04 and at the healthy feeder head, per R_F and system
  fpi_phasors_scn04.csv    3I0 phasor referred to -V0 at every ComPass bay of busbar 2, SCN-04, R_F = 0
  direction_probability.csv  per system, calibration, V_NEQ and I_EQ: lowest P(Direction B) at the bays on the
                           A20-to-fault path facing the fault, over all locations and R_F <= 30 ohm, and the highest
                           probability of an opposite indication at any bay
  coverage_rf.csv          per system and setting: largest R_F at which every path bay still indicates B with >= 95 %
  path_probability_rf.csv  per system, setting and R_F: lowest P(Direction B) at the path bays
  windows.csv              per system: pickup range for 99 % at the path bays, and the narrower range that also keeps
                           every bay off the path from indicating B (needed only if the ADMS ignores the direction)
  zones.csv                zones between the twelve ComPass stations: cable length, customers, ComPass upstream or not

Path bay: a bay of a ComPass station on the A20-to-fault path, facing the fault (expected Direction B). Off-path bays
with expected Direction B are the fault-facing bays of stations beyond the fault and the A20-facing bays of stations on
healthy feeders; their indication is correct but carries only the charging current of the cable behind them.
"""
import os, sys, csv, gzip, math, cmath, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ef_network as ef

R = os.path.join(HERE, 'results'); OUT = os.path.join(R, 'ch6'); os.makedirs(OUT, exist_ok=True)
rows = ef.load_rows()
E_N = 11.0 / math.sqrt(3); E = 11.15 / math.sqrt(3)
cases = {c['case_id']: c for c in csv.DictReader(open(os.path.join(HERE, 'tables', 'cases.csv')))}
oc = {c['case_id']: c for c in csv.DictReader(open(os.path.join(R, 'offline_cases.csv')))}
bays = list(csv.DictReader(open(os.path.join(HERE, 'tables', 'bays.csv'))))
COMPASS = sorted({b['station'] for b in bays if b['station'] != 'A20'})

def write(name, header, data):
    with open(os.path.join(OUT, name), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(data)

# ------------------------------------------------------------------ systems
SYSTEMS = [  # key, label, config, c_add_bus, c_add_target, representative location, locations
    ('bb2', 'Busbar 2 (circuits 08, 13)', 'split', '', '', 'F13H'),
    ('bb2_40', 'Busbar 2 + shunt', 'split', 'A20_BB2', '40', 'F13H'),
    ('bb2_80', 'Busbar 2 + shunt', 'split', 'A20_BB2', '80', 'F13H'),
    ('bb2_120', 'Busbar 2 + shunt', 'split', 'A20_BB2', '120', 'F13H'),
    ('bb2_200', 'Busbar 2 + shunt', 'split', 'A20_BB2', '200', 'F13H'),
    ('bb1', 'Busbar 1', 'split', '', '', 'F21H'),
    ('bb1_80', 'Busbar 1 + shunt', 'split', 'A20_BB1', '80', 'F21H'),
    ('bb1_120', 'Busbar 1 + shunt', 'split', 'A20_BB1', '120', 'F21H'),
    ('bb1_200', 'Busbar 1 + shunt', 'split', 'A20_BB1', '200', 'F21H'),
    ('coupled', 'Coupled busbars (N-1)', 'coupled', '', '', 'F21H'),
    ('post02', 'Busbar 1 after SCN-02 restoration', 'post02', '', '', 'F21H'),
    ('post06', 'Busbar 1 after SCN-06 isolation', 'post06', '', '', 'F21H'),
    ('post11', 'Busbar 1 after SCN-11 isolation', 'post11', '', '', 'F21H'),
    ('post15', 'Busbar 1 after SCN-15 restoration', 'post15', '', '', 'F21H'),
]
BB2_LOCS = {'SCN04', 'F13H', 'F13E', 'F08E'}

def case_id(cfg, loc, rf, bus='', target='', earth='iso', cset='main'):
    if bus:
        k = [c for c, x in cases.items() if x['group'] == 'ic_sweep' and x['config'] == cfg and x['loc'] == loc
             and x['RF_ohm'] == str(rf) and x['c_add_bus'] == bus and x['c_add_target_A'] == target]
        return k[0] if k else None
    cid = f'base|{earth}|{cset}|{cfg}|{loc}|{rf}'
    if cid in cases: return cid
    k = [c for c, x in cases.items() if x['group'] == 'sens_cable' and x['earthing'] == ('isolated' if earth == 'iso' else 'earthed')
         and x['cable_set'] == cset and x['config'] == cfg and x['loc'] == loc and x['RF_ohm'] == str(rf)]
    return k[0] if k else None

def sys_locs(key, cfg, bus):
    on_bb2 = key.startswith('bb2')
    out = []
    for c in cases.values():
        if c['config'] != cfg or c['earthing'] != 'isolated' or c['cable_set'] != 'main' or c['Sk_MVA'] != '500': continue
        if bus and (c['group'] != 'ic_sweep' or c['c_add_bus'] != bus): continue
        if not bus and c['group'] != 'base': continue
        if cfg != 'coupled' and (c['loc'] in BB2_LOCS) != on_bb2: continue
        out.append(c['loc'])
    return sorted(set(out))

def net_for(cfg, loc, bus='', target='', cset='main', earthing='isolated'):
    cuf = 0.0
    if bus:
        cuf = float([c for c in cases.values() if c['c_add_bus'] == bus and c['c_add_target_A'] == target][0]['c_add_uF_per_phase'])
    return ef.Net(rows, cfg, earthing, cset, c_add_uF=cuf, c_add_bus=bus or 'A20_BB1', location=ef.location(loc, rows))

# ------------------------------------------------------------------ feeders and their cable
seg_of = {b['bay_id']: b['cable_segment'] for b in bays if b['station'] == 'A20'}
head_el = {b['bay_id']: (b['element_class'], b['element']) for b in bays if b['station'] == 'A20'}

def feeders(net):
    """feeder -> list of energised lines reachable from its first segment without passing the A20 busbars"""
    adj = collections.defaultdict(list)
    for ln in net.lines: adj[net.node(ln['a'])].append(ln); adj[net.node(ln['b'])].append(ln)
    bb = {net.node(t) for t, nm in net.tname.items() if nm in ('A20_BB1', 'A20_BB2')}
    out = {}
    for bid, segs in seg_of.items():
        k, els = head_el[bid]
        if not any(net.bay_lines(k, el, 'A20')[1] for el in els.split('|')): continue   # head breaker open
        for seg in segs.split('|'):
            first = [ln for ln in net.lines if ln['name'] == seg]
            if not first: continue
            seen_l = {id(first[0])}; lines = [first[0]]
            stack = [n for n in (net.node(first[0]['a']), net.node(first[0]['b'])) if n not in bb]
            seen_n = set(stack)
            while stack:
                n = stack.pop()
                for ln in adj[n]:
                    if id(ln) in seen_l: continue
                    seen_l.add(id(ln)); lines.append(ln)
                    for m in (net.node(ln['a']), net.node(ln['b'])):
                        if m not in seen_n and m not in bb: seen_n.add(m); stack.append(m)
            out[bid.replace('A20_F', '')] = lines
    return out

def ic_of(lines, V=E):
    return 3 * sum(ln['y0'].imag for ln in lines) * V * 1000          # A at V0 = V (kV), lines' own charging

def energised_km(net, system_nodes=None):
    return sum(ln['L'] for ln in net.lines if system_nodes is None or net.node(ln['a']) in system_nodes)

def system_nodes(net, src):
    adj = collections.defaultdict(set)
    for ln in net.lines:
        a, b = net.node(ln['a']), net.node(ln['b']); adj[a].add(b); adj[b].add(a)
    start = net.node(net.src[src]); seen = {start}; st = [start]
    while st:
        n = st.pop()
        for m in adj[n]:
            if m not in seen: seen.add(m); st.append(m)
    return seen

# ------------------------------------------------------------------ 1. tab:ic_results and feeder charging
ic_rows, fc = [], collections.defaultdict(dict)
for key, label, cfg, bus, target, rep in SYSTEMS:
    cid = case_id(cfg, rep, 0, bus, target)
    net = net_for(cfg, rep, bus, target)
    src = 'S2' if key.startswith('bb2') else 'S1'
    nodes = system_nodes(net, src)
    km = energised_km(net, nodes)
    fd = {f: lns for f, lns in feeders(net).items() if lns and net.node(lns[0]['a']) in nodes}
    own = {f: ic_of(l) for f, l in fd.items()}
    IF = float(oc[cid]['IF_A'])
    big = max(own, key=own.get)
    ic_rows.append([key, label, cfg, target or '', f'{km:.2f}', f'{IF:.1f}', big, f'{own[big]:.1f}', f'{100 * own[big] / IF:.0f}'])
    if not bus:
        for f, v in own.items(): fc[f][key] = v
# cable-data sensitivity and the catalog basis of Table 4.x for busbar 1
for cset in ('xlpe_sens', 'pilc_low'):
    cid = case_id('split', 'F21H', 0, cset=cset)
    ic_rows.append([f'bb1_{cset}', f'Busbar 1, cable set {cset}', 'split', '', '', f'{float(oc[cid]["IF_A"]):.1f}', '', '', ''])
net = net_for('split', 'F21H'); nodes = system_nodes(net, 'S1')
cat = 3 * sum(ln['y1'].imag for ln in net.lines if net.node(ln['a']) in nodes) * E * 1000
ic_rows.append(['bb1_c0_eq_c1', 'Busbar 1, C0 = C1 (ADMS catalog, Table 4.x basis)', 'split', '', '', f'{cat:.1f}', '', '', ''])
ic_rows.append(['bb1_earthed', 'Busbar 1, star points earthed (fault current, kA)', 'split', '', '',
                f'{float(oc[case_id("split", "F21H", 0, earth="ear")]["IF_A"]) / 1000:.2f}', '', '', ''])
write('ic_results.csv', ['key', 'system', 'config', 'shunt_target_A', 'energised_cable_km', 'IC_solid_A', 'largest_feeder',
                         'largest_feeder_A', 'largest_feeder_share_pct'], ic_rows)
cfgs = ['bb1', 'bb2', 'coupled', 'post02', 'post06', 'post11', 'post15']
write('feeder_charging.csv', ['feeder'] + cfgs,
      [[f] + [f'{fc[f][c]:.2f}' if c in fc[f] else '' for c in cfgs] for f in sorted(fc)])

# ------------------------------------------------------------------ 2. displacement voltage against fault resistance
RFS = [0, 3, 10, 20, 30, 50, 75, 100, 150, 200, 300, 400, 500, 700, 1000, 1500, 2000, 3000, 5000]
cov, lim = [], []
for key, label, cfg, bus, target, rep in SYSTEMS[:10]:
    net = net_for(cfg, rep, bus, target); sols = net.solve(RFS)
    F = net.idx[net.loc['node']]
    IC = abs(3 * sols[0]['I0']) * 1000
    for rf, s in zip(RFS, sols):
        v = abs(s['V0'][F]) / E_N
        eq = (E / E_N) / math.sqrt(1 + (IC * rf / (E * 1000)) ** 2)
        cov.append([key, f'{IC:.1f}', rf, f'{v:.4f}', f'{eq:.4f}'])
    row = [key, f'{IC:.1f}']
    for t in (0.10, 0.20, 0.30):
        lo, hi = 0.0, 1e5                                      # bisection on the offline model
        for _ in range(40):
            mid = (lo + hi) / 2; s = net.solve([mid])[0]
            if abs(s['V0'][F]) / E_N > t: lo = mid
            else: hi = mid
        rf_eq = (E * 1000 / IC) * math.sqrt((E / (t * E_N)) ** 2 - 1)
        row += [f'{lo:.0f}', f'{rf_eq:.0f}']
    lim.append(row)
write('v0_coverage.csv', ['system', 'IC_A', 'RF_ohm', 'V0_over_En_model', 'V0_over_En_eq'], cov)
write('v0_rf_limits.csv', ['system', 'IC_A', 'RF_10pct_model', 'RF_10pct_eq', 'RF_20pct_model', 'RF_20pct_eq',
                           'RF_30pct_model', 'RF_30pct_eq'], lim)

# ------------------------------------------------------------------ path classification per configuration and location
src = open(os.path.join(HERE, 'analysis_selectivity.py')).read(); src = src[:src.index('SYSTEMS = [')]
g = {'__file__': os.path.join(HERE, 'analysis_selectivity.py')}; exec(src, g)
bay_id = {(b['station'], b['element']): b['bay_id'] for b in bays}
PATH = {}                                                   # (config, loc) -> {bay_id: role}
for cfg in ('split', 'coupled', 'post02', 'post06', 'post11', 'post15'):
    for loc in sorted({c['loc'] for c in cases.values() if c['config'] == cfg}):
        try: net = net_for(cfg, loc)
        except KeyError: continue
        s = net.solve([0])[0]
        PATH[(cfg, loc)] = {bay_id[(st, e)]: ('path' if role == 'path' else 'off') + ('B' if iq > 0 else 'A')
                            for st, e, role, iq in g['classify'](net, s['V0'], s['E'])}

# ------------------------------------------------------------------ 3. FPI signatures, SCN-04
def phasors(cid):
    out = {}
    for r in PH.get(cid, []):
        I = float(r['I0x3_A']) * cmath.exp(1j * math.radians(float(r['ang_I0x3_deg'])))
        V = float(r['V0_kV']) * cmath.exp(1j * math.radians(float(r['ang_V0_deg'])))
        if abs(V) < 1e-9: continue
        phi = cmath.phase(I) - cmath.phase(-V)
        out[r['bay_id']] = (abs(I), math.degrees(phi), abs(I) * math.sin(phi), abs(V) / E_N)
    return out
need = set()
for rf in (0, 100, 300, 1000, 3000):
    for t in ('', '40', '80', '120', '200'):
        need.add(case_id('split', 'SCN04', rf, 'A20_BB2' if t else '', t))
PH = collections.defaultdict(list)
PHASORS = os.path.join(R, 'offline_phasors.csv')
with (open(PHASORS) if os.path.exists(PHASORS) else gzip.open(PHASORS + '.gz', 'rt')) as fh:
    for r in csv.DictReader(fh):
        if r['case_id'] in need: PH[r['case_id']].append(r)
roles = PATH[('split', 'SCN04')]
p0 = phasors(case_id('split', 'SCN04', 0))
up = max((b for b, r in roles.items() if r == 'pathB'), key=lambda b: p0[b][0])          # nearest upstream: largest
dn = max((b for b, r in roles.items() if r == 'offB' and b in p0 and not b.startswith('A20')), key=lambda b: p0[b][0])
sig = []
for t in ('', '40', '80', '120', '200'):
    for name, b in (('upstream FPI, bay facing the fault', up), ('downstream FPI, bay facing the fault', dn),
                    ('healthy feeder head (circuit 08)', 'A20_F08')):
        vals = [phasors(case_id('split', 'SCN04', rf, 'A20_BB2' if t else '', t))[b][2] for rf in (0, 100, 300, 1000, 3000)]
        sig.append([t or 'natural', name, b] + [f'{v:.2f}' for v in vals])
write('fpi_signatures.csv', ['system', 'location', 'bay', 'RF_0', 'RF_100', 'RF_300', 'RF_1000', 'RF_3000'], sig)
net4 = net_for('split', 'SCN04'); faces = {}
for b in bays:
    if b['station'] == 'A20': faces[b['bay_id']] = 'feeder head'; continue
    a20 = g['a20_behind'](net4, b['element_class'], b['element'], b['station'])
    if a20 is not None: faces[b['bay_id']] = 'toward A20' if a20 else 'away from A20'
for t, nm in (('', 'fpi_phasors_scn04.csv'), ('120', 'fpi_phasors_scn04_120A.csv')):
    pz = phasors(case_id('split', 'SCN04', 0, 'A20_BB2' if t else '', t))
    write(nm, ['bay', 'role', 'faces', 'I0x3_A', 'phi_deg', 'Iq_A'],
          [[b, roles.get(b, 'head'), faces.get(b, ''), f'{v[0]:.3f}', f'{v[1]:.2f}', f'{v[2]:.3f}'] for b, v in sorted(pz.items())])

# ------------------------------------------------------------------ 4. direction probability
VN = (10, 20, 30); IE = (1, 2, 3, 5, 8, 10, 15, 20)
sysmap = {}
for key, label, cfg, bus, target, rep in SYSTEMS:
    for loc in sys_locs(key, cfg, bus): sysmap.update({(cfg, loc, bus, target): key})
def sys_of(cid):
    c = cases[cid]
    if c['earthing'] != 'isolated' or c['cable_set'] != 'main' or c['Sk_MVA'] != '500': return None
    return sysmap.get((c['config'], c['loc'], c['c_add_bus'], c['c_add_target_A']))
low = collections.defaultdict(lambda: 1.0); wrong = collections.defaultdict(float)
pathcov = collections.defaultdict(lambda: 1.0)              # (key, cal, vn, ie, rf) -> min P(B) at path bays
offB = collections.defaultdict(float); pathmin = collections.defaultdict(lambda: 1e9)
with gzip.open(os.path.join(R, 'offline_emulation.csv.gz'), 'rt') as fh:
    for r in csv.DictReader(fh):
        key = sys_of(r['case_id'])
        if not key: continue
        c = cases[r['case_id']]; role = PATH.get((c['config'], c['loc']), {}).get(r['bay_id'])
        rf = int(c['RF_ohm']); cal = r['calibration']
        for vn in VN:
            for ie in IE:
                pB, pA = float(r[f'pB_v{vn}_i{ie}']), float(r[f'pA_v{vn}_i{ie}'])
                if r['expected'] in ('A', 'B'):
                    k = (key, cal, vn, ie)
                    wrong[k] = max(wrong[k], pA if r['expected'] == 'B' else pB)
                if role == 'pathB':
                    pathcov[(key, cal, vn, ie, rf)] = min(pathcov[(key, cal, vn, ie, rf)], pB)
                    if rf <= 30: low[(key, cal, vn, ie)] = min(low[(key, cal, vn, ie)], pB)
        if cal == 'standard' and rf == 0 and r['bay_id'][:5] != 'A20_F' or (cal == 'standard' and rf == 0):
            I = float(r['I0x3_A'])
            if role == 'pathB': pathmin[key] = min(pathmin[key], I)
            elif role == 'offB': offB[key] = max(offB[key], I)
dp = []
for key, *_ in SYSTEMS:
    for cal in ('standard', 'reference'):
        for vn in VN:
            for ie in IE:
                k = (key, cal, vn, ie)
                dp.append([key, cal, vn, ie, f'{low[k]:.4f}' if k in low else '', f'{wrong.get(k, 0):.4f}'])
write('direction_probability.csv', ['system', 'calibration', 'V_NEQ_pct', 'I_EQ_A', 'min_P_B_path_RF_le_30',
                                    'max_P_opposite_any_bay'], dp)
cv = []
for key, *_ in SYSTEMS:
    for cal in ('standard', 'reference'):
        for vn in VN:
            for ie in IE:
                ok = [rf for rf in (0, 10, 30, 100, 300, 1000, 3000) if pathcov.get((key, cal, vn, ie, rf), 0) >= 0.95]
                # coverage limit: the largest R_F of an unbroken run from 0
                lim_rf = None
                for rf in (0, 10, 30, 100, 300, 1000, 3000):
                    if rf in ok: lim_rf = rf
                    else: break
                cv.append([key, cal, vn, ie, '' if lim_rf is None else lim_rf])
write('coverage_rf.csv', ['system', 'calibration', 'V_NEQ_pct', 'I_EQ_A', 'max_RF_ohm_P95'], cv)
write('path_probability_rf.csv', ['system', 'calibration', 'V_NEQ_pct', 'I_EQ_A', 'RF_ohm', 'min_P_B_path'],
      [[k[0], k[1], k[2], k[3], k[4], f'{v:.4f}'] for k, v in sorted(pathcov.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3], x[0][4]))])
win = []
for key, *_ in SYSTEMS:
    ok99 = [ie for ie in IE if low.get((key, 'standard', 20, ie), 0) >= 0.99 and wrong.get((key, 'standard', 20, ie), 0) <= 0.01]
    lo = offB[key] * 1.03 + 0.1; hi = pathmin[key] / 1.03 - 0.1 if pathmin[key] < 1e9 else None
    win.append([key, f'{pathmin[key]:.2f}' if hi else '', ' '.join(map(str, ok99)), f'{offB[key]:.2f}',
                (f'{lo:.1f} to {hi:.1f}' if hi and hi > lo else 'none') if hi else 'no ComPass on any path'])
write('windows.csv', ['system', 'smallest_path_current_A', 'I_EQ_meeting_99pct_std_cal_VNEQ20',
                      'largest_offpath_forward_current_A', 'strict_window_A'], win)

# ------------------------------------------------------------------ 5. zones between the ComPass stations
CUST = next((p for p in (os.path.join(HERE, '..', 'data', 'reliability', 'customers_per_station.csv'),         # data/reliability/ beside the package
                          os.path.join(HERE, '..', 'reliability', 'data', 'customers_per_station.csv'))         # reliability/data/ in this supplement
             if os.path.exists(p)), None)
cust = {r['station']: int(r['customers']) for r in csv.DictReader(open(CUST))} if CUST else {}
zr = []
for cfg in ('split',):
    net = net_for(cfg, 'F21H')
    st_of = {}
    for t, nm in net.tname.items():
        st = net.tstation.get(t)
        if st: st_of.setdefault(net.node(t), set()).add(st)
    cut = {n for n, s in st_of.items() if s & set(COMPASS)} | {net.node(t) for t, nm in net.tname.items() if nm in ('A20_BB1', 'A20_BB2')}
    adj = collections.defaultdict(list)
    for ln in net.lines: adj[net.node(ln['a'])].append(ln); adj[net.node(ln['b'])].append(ln)
    fd = feeders(net); feeder_of = {id(ln): f for f, ls in fd.items() for ln in ls}
    # a station's customers sit where its transformer connects (HV terminal of Dxxxx_S-11-0k)
    tr_node = collections.defaultdict(set)
    for c in rows['StaCubic'].values():
        tr = rows['ElmTr2'].get(c['obj_id'])
        if tr and c['obj_bus'] == '0' and tr['loc_name'].startswith('D') and c['fold_id'] in net.tname:
            tr_node[tr['loc_name'][:5]].add(net.node(c['fold_id']))
    seen = set(); z = 0
    for ln0 in net.lines:
        if id(ln0) in seen: continue
        a0, b0 = net.node(ln0['a']), net.node(ln0['b'])
        if a0 in cut and b0 in cut and st_of.get(a0, {1}) == st_of.get(b0, {2}): seen.add(id(ln0)); continue   # inside a station
        z += 1; comp = [ln0]; seen.add(id(ln0)); stack = [n for n in (a0, b0) if n not in cut]; vis = set(stack); bounds = set()
        for n in (a0, b0):
            if n in cut: bounds |= st_of.get(n, {'A20'})
        while stack:
            n = stack.pop()
            for ln in adj[n]:
                if id(ln) in seen: continue
                seen.add(id(ln)); comp.append(ln)
                for m in (net.node(ln['a']), net.node(ln['b'])):
                    if m in cut: bounds |= st_of.get(m, {'A20'})
                    elif m not in vis: vis.add(m); stack.append(m)
        stations = {s for s, ns in tr_node.items() if ns & vis}
        km = sum(ln['L'] for ln in comp)
        if km < 0.02: continue
        f = collections.Counter(feeder_of.get(id(ln), '?') for ln in comp).most_common(1)[0][0]
        head = 'A20' in bounds or any(not st_of.get(n) for n in ()) or bool({net.node(t) for t, nm in net.tname.items() if nm in ('A20_BB1', 'A20_BB2')} & set().union(*[{net.node(ln['a']), net.node(ln['b'])} for ln in comp]))
        zr.append([f, z, f'{km:.3f}', len(stations), sum(cust.get(s, 0) for s in stations), 'no' if head else 'yes',
                   ' '.join(sorted(bounds & set(COMPASS))), ' '.join(sorted(stations))])
    for s in COMPASS:                                       # customers at the ComPass stations themselves
        zr.append(['', 'station ' + s, '0.000', 1, cust.get(s, 0), 'station', s, s])
write('zones.csv', ['feeder', 'zone', 'cable_km', 'stations', 'customers', 'compass_upstream', 'bounding_compass', 'stations_list'], zr)
print('written:', sorted(os.listdir(OUT)))

# ------------------------------------------------------------------ 6. zones per feeder
zs = [r for r in zr if r[5] != 'station']; fz = collections.defaultdict(lambda: dict(km=0.0, up=0.0, zones=0, cust=0, custup=0, comp=set()))
for f, zid, km, nst, cu, up, bounding, _ in zs:
    d = fz[f]; d['km'] += float(km); d['zones'] += 1; d['cust'] += cu; d['comp'] |= set(bounding.split())
    if up == 'yes': d['up'] += float(km); d['custup'] += cu
write('zones_by_feeder.csv', ['feeder', 'cable_km', 'compass_stations', 'zones', 'km_with_compass_upstream', 'customers_in_zones',
                              'customers_with_compass_upstream'],
      [[f, f'{d["km"]:.1f}', len(d['comp']), d['zones'], f'{d["up"]:.1f}', d['cust'], d['custup']] for f, d in sorted(fz.items())])
