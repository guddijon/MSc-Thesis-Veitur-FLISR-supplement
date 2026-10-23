"""ComPass sin(phi) emulation with the residual current formed from three phase-current sensors (3CT), alongside the
first run with a fixed residual error (+/-3 % or 0.1 A, labelled SumCT in the tables) from the same code.
Only the device-error model changes: the network cases, the sweep and the PowerFactory anchors are those of run_offline.py.

3CT residual current per sample:
    3I0_meas = sum_k  m_k(I_k) * exp(j theta_k)
    m_k(I) = I (1 + g_k), g_k ~ U(-g, +g)           for |I_k| >= 50 A   (g = 1 % split-core 49-6024, 0.5 % bushing 49-6025)
    m_k(I) = I + e_k, |e_k| ~ U(0, 0.5 A), random angle   below 50 A   (manual 104101-0124, p. 37: +/-1 % or +/-0.5 A)
    theta_k ~ U(-theta, +theta): not stated in the manual; run at 0.5, 1 and 2 deg (and 0 as a check)
Phase currents I_k = pre-fault load (positive sequence, optional negative-sequence unbalance) + fault contribution
(zero sequence 3I0/3, positive and negative sequence from the faulted-network solution, Z2 = Z1). The +/-5 deg angle
error, the displacement-voltage errors and the standing V0 of compass_emulation.py are kept and drawn in the same
order from the same seed, so SumCT and 3CT see identical voltage errors; the 3CT draws come from a separate stream,
paired across load levels. LimitIE (0.1 A) is a display limit only (manual p. 40) and is not applied.

Load levels: Akranes systems at the hold-out snapshots winter_peak_boiler_off and summer_night_min (offline
positive-sequence load flow of the allocated loads, checked against the feeder-head currents of the allocation);
systems with added capacitance at a uniform bay load of 50, 150, 300 and 450 A, power factor 0.95 inductive, flowing
away from A20. Unbalance: none, or the measured median or maximum max/min phase ratio (holdout_validation_metrics.csv)
as a negative-sequence load component of random angle.

Writes results/ch6/: direction_probability_3ct.csv, path_probability_rf_3ct.csv, coverage_rf_3ct.csv, windows_3ct.csv
(layouts of the SumCT files with the error model, sensor class, theta, unbalance and load level after 'system'),
summary_3ct.csv, ies_check_3ct.csv, bay_loads_3ct.csv. Run time about 7 min; --summary rebuilds summary_3ct.csv alone.
"""
import os, sys, csv, gzip, math, cmath, collections, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import compass_emulation as ce

# definitions of ch6_results.py (systems, case ids, path classification) without its result sections
_src = open(os.path.join(HERE, 'ch6_results.py')).read()
_mark = lambda s: _src.index('# ' + '-' * 66 + ' ' + s)
exec(_src[:_mark('1. tab:ic_results')])
exec(_src[_mark('path classification'):_mark('3. FPI signatures')])
a20_behind = g['a20_behind']

def summarize():
    """summary_3ct.csv from direction_probability_3ct.csv and coverage_rf_3ct.csv (standard calibration, V_NEQ> 20 %):
    smallest I_EQ> with >= 99 % Direction B at every on-path bay for R_F <= 30 ohm; the same with at most 1 % opposite or
    false indications on every off-path ComPass bay as well; reach (largest R_F with >= 95 %) at 5 and 10 A; and the
    probabilities at 10 A."""
    dp = [r for r in csv.DictReader(open(os.path.join(OUT, 'direction_probability_3ct.csv')))
          if r['calibration'] == 'standard' and r['V_NEQ_pct'] == '20']
    cv = {tuple(r[c] for c in HDR) + (r['I_EQ_A'],): r['max_RF_ohm_P95'] for r in csv.DictReader(open(os.path.join(OUT, 'coverage_rf_3ct.csv')))
          if r['calibration'] == 'standard' and r['V_NEQ_pct'] == '20'}
    grp = collections.OrderedDict()
    for r in dp: grp.setdefault(tuple(r[c] for c in HDR), {})[int(r['I_EQ_A'])] = r
    out = []
    for key, d in grp.items():
        has = d[IE[0]]['min_P_B_path_RF_le_30'] != ''
        path = [i for i in IE if has and float(d[i]['min_P_B_path_RF_le_30']) >= 0.99]
        both = [i for i in path if float(d[i]['max_P_opposite_or_false_offpath']) <= 0.01]
        nz = lambda x: (min(x) if x else 'none') if has else 'no path'
        out.append(list(key) + [nz(path), nz(both), cv.get(key + ('5',), ''), cv.get(key + ('10',), ''),
                                d[10]['min_P_B_path_RF_le_30'], d[10]['max_P_opposite_or_false_offpath'], d[10]['max_P_opposite_any_bay']])
    write('summary_3ct.csv', HDR + ['min_I_EQ_99pct_path_RF_le_30', 'min_I_EQ_99pct_path_and_offpath_le_1pct',
                                    'reach_RF_ohm_P95_IEQ5_VNEQ20', 'reach_RF_ohm_P95_IEQ10_VNEQ20', 'min_P_B_path_RF_le_30_IEQ10_VNEQ20',
                                    'max_P_opposite_or_false_offpath_IEQ10_VNEQ20', 'max_P_opposite_any_bay_IEQ10_VNEQ20'], out)


sysmap = {}
for key, label, cfg, bus, target, rep in SYSTEMS:
    for loc in sys_locs(key, cfg, bus): sysmap[(cfg, loc, bus, target)] = key
def sys_of(c):
    if c['earthing'] != 'isolated' or c['cable_set'] != 'main' or c['Sk_MVA'] != '500': return None
    return sysmap.get((c['config'], c['loc'], c['c_add_bus'], c['c_add_target_A']))

SEED, N, CHUNK, BLOCK = 20261022, ce.N, 4000, 500
VN = (10, 20, 30); IE = (5, 10, 15, 20, 30); GRID = [(v, i) for v in VN for i in IE]
RFS = (0, 10, 30, 100, 300, 1000, 3000)
A = cmath.exp(2j * math.pi / 3); PF_ANG = math.acos(0.95)
SNAP = {'winter_peak': 'winter_peak_boiler_off', 'summer_min': 'summer_night_min'}
UNIFORM = (50, 150, 300, 450)
um = {r['snapshot']: r for r in csv.DictReader(open(os.path.join(ef.ROOT, 'data', 'validation', 'holdout_validation_metrics.csv')))}
UNB = {lv: {'none': 1.0, 'median': float(um[s]['unb_median']), 'max': float(um[s]['unb_max'])} for lv, s in SNAP.items()}
for L in UNIFORM: UNB[L] = UNB['winter_peak']
COMBOS = [dict(gain=0.01, theta=t, unb=u) for t in (0.5, 1.0, 2.0) for u in ('none', 'median', 'max')] + \
         [dict(gain=0.005, theta=t, unb='none') for t in (0.5, 1.0, 2.0)] + [dict(gain=0.01, theta=0.0, unb='none')]
def ctag(c): return ('3CT', 'split-core 1 %' if c['gain'] == 0.01 else 'bushing 0.5 %', f"{c['theta']:g}", c['unb'])
REF = ('SumCT', 'summation 3 %', '', '')
AKR_CFG = ('split', 'coupled', 'post02', 'post06', 'post11', 'post15')
HDR = ['system', 'error_model', 'phase_sensor', 'theta_deg', 'unbalance', 'load_level']
if '--summary' in sys.argv: summarize(); sys.exit()

def first(fun, kind, els, st):
    for el in els.split('|'):
        v = fun(kind, el, st)
        if v is not None: return v
    return None

def bay_seq_current(net, V, kind, el, st):
    """Positive- (or negative-) sequence current of a bay into its cable, kA, from node voltages V (kV)."""
    ct, lines = net.bay_lines(kind, el, st)
    if not lines: return None
    I = 0j
    for ln, s in lines:
        a, b = (ln['a'], ln['b']) if s > 0 else (ln['b'], ln['a'])
        va, vb = V[net.idx[net.node(a)]], V[net.idx[net.node(b)]]
        I += (va - vb) / ln['z1'] + va * ln['y1'] / 2
    return I

# ------------------------------------------------------------------ 1. pre-fault load flow per configuration and snapshot
def load_flow(net, S_kva, U_kV=11.15, iters=30):
    """Positive-sequence load flow: sources as EMF U/sqrt3 behind grid and transformer impedance (as Net.Y), loads as
    constant current at nominal voltage (ZIP 50/50 of the allocation, within 1 % at 11.15 kV)."""
    Y = net.Y(1); E_src = U_kV / math.sqrt(3); inj = np.zeros(len(net.nodes), complex)
    zg66 = (66.0 ** 2 / net.Sk) * complex(ef.SOURCE['RX'], 1) / abs(complex(ef.SOURCE['RX'], 1))
    for s in ('S1', 'S2'):
        t = net.src.get(s)
        if not t: continue
        S, uk, ur = ef.SOURCE[s]; zt = complex(ur, math.sqrt(uk ** 2 - ur ** 2)) * ef.U_N ** 2 / S
        inj[net.idx[net.node(t)]] += E_src / (zg66 * (ef.U_N / ef.U_HV_TAP[s]) ** 2 + zt)
    sw_open = {x['fold_id'] for x in net.rows['StaSwitch'].values() if x['on_off'] == '0'}
    lod = {k: x['loc_name'] for k, x in net.rows['ElmLod'].items()}
    # the loads sit on the 0.4 kV terminals of the distribution transformers: move them to the 11 kV side
    # (transformer losses neglected)
    tr = collections.defaultdict(dict)
    for c in net.rows['StaCubic'].values():
        if c['obj_id'] in net.rows['ElmTr2'] and c['FID'] not in sw_open: tr[c['obj_id']][int(c['obj_bus'])] = c['fold_id']
    hv_of = {t[1]: t[0] for t in tr.values() if 0 in t and 1 in t}
    node_S = collections.defaultdict(complex)
    for c in net.rows['StaCubic'].values():
        if c['obj_id'] in lod and c['FID'] not in sw_open and lod[c['obj_id']] in S_kva:
            n = net.node(hv_of.get(c['fold_id'], c['fold_id']))
            if n in net.idx: node_S[net.idx[n]] += S_kva[lod[c['obj_id']]] / 3000.0       # MVA per phase
    V = np.full(len(net.nodes), E_src, complex)
    for _ in range(iters):
        I = inj.copy()
        for k, S in node_S.items(): I[k] -= np.conj(S / V[k]) * abs(V[k]) / E_N
        V = np.linalg.solve(Y, I)
    return V

bay_el = collections.OrderedDict()
for b in bays: bay_el.setdefault(b['bay_id'], (b['station'], b['element_class'], b['element']))
LOAD = {}; FACES = {}; lf_rows = []
for cfg in AKR_CFG:
    net = ef.Net(rows, cfg, 'isolated', 'main')
    for bid, (st, k, e) in bay_el.items():
        fa = first(lambda k_, e_, s_: a20_behind(net, k_, e_, s_), k, e, st)
        if fa is not None: FACES[(cfg, bid)] = fa
    for lv, snap in SNAP.items():
        S = {r['load']: complex(float(r['P0_kW']), float(r['Q0_kvar']))
             for r in csv.DictReader(open(os.path.join(ef.ROOT, 'data', 'allocation', f'scenario_{snap}_loads.csv')))
             if r['feeder'] != '-'}
        V = load_flow(net, S)
        tun = {r['feeder'][-2:]: r for r in csv.DictReader(open(os.path.join(ef.ROOT, 'data', 'allocation', f'tuning_{snap}.csv')))}
        for bid, (st, k, e) in bay_el.items():
            I = first(lambda k_, e_, s_: bay_seq_current(net, V, k_, e_, s_), k, e, st)
            if I is None: continue
            LOAD[(cfg, lv, bid)] = I * 1000
            ref = tun.get(bid[-2:], {}).get('I_sim', '') if st == 'A20' and cfg == 'split' else ''
            lf_rows.append([cfg, lv, bid, f'{abs(I) * 1000:.2f}', f'{math.degrees(cmath.phase(I)):.2f}',
                            'toward A20' if FACES.get((cfg, bid)) else 'away from A20', ref])
write('bay_loads_3ct.csv', ['config', 'load_level', 'bay_id', 'I_load_A', 'angle_deg', 'faces',
                            'allocation_feeder_head_A'], lf_rows)
# check: winter peak feeder heads against the allocation sweep (same switching state; the summer snapshots had the
# August open points, so their per-feeder split differs from the study configuration)
dev = [abs(float(r[3]) - float(r[6])) / float(r[6]) for r in lf_rows if r[1] == 'winter_peak' and r[6] and float(r[6]) > 10]
print(f'load flow: {len(lf_rows)} bay currents; winter-peak feeder heads above 10 A against the allocation sweep: '
      f'max deviation {100 * max(dev):.1f} % over {len(dev)} feeders', flush=True)

# ------------------------------------------------------------------ 2. fault contribution per case and bay
need = {cid for cid, c in cases.items() if c['cable_set'] == 'main' and c['Sk_MVA'] == '500' and c['group'] in ('base', 'ic_sweep')}
groups = collections.defaultdict(list)
for cid in sorted(need):
    c = cases[cid]; groups[(c['earthing'], c['config'], c['loc'], c['c_add_bus'], c['c_add_uF_per_phase'])].append(c)
FC = {}; t0 = time.time()
for (earth, cfg, loc, cbus, cuf), cs in groups.items():
    net = ef.Net(rows, cfg, earth, 'main', c_add_uF=float(cuf) if cuf else 0.0, c_add_bus=cbus or 'A20_BB1',
                 location=ef.location(loc, rows))
    sols = net.solve([float(c['RF_ohm']) for c in cs]); F = net.idx[net.loc['node']]
    e = np.zeros(len(net.nodes), complex); e[F] = 1.0; z1c = np.linalg.solve(net.Y(1), e)
    for c, s in zip(cs, sols):
        dV1 = -z1c * s['I0']
        for bid, (st, k, el) in bay_el.items():
            I0x3 = first(lambda k_, e_, s_: net.bay_current(s['V0'], k_, e_, s_), k, el, st)
            if I0x3 is None: continue
            I1 = first(lambda k_, e_, s_: bay_seq_current(net, dV1, k_, e_, s_), k, el, st)
            FC[(c['case_id'], bid)] = (I0x3 * 1000, I1 * 1000)
print(f'fault contributions: {len(groups)} network solutions, {len(FC)} bay rows, {time.time() - t0:.0f} s', flush=True)

# ------------------------------------------------------------------ 3. emulation
PHASORS = os.path.join(R, 'offline_phasors.csv')
with (open(PHASORS) if os.path.exists(PHASORS) else gzip.open(PHASORS + '.gz', 'rt')) as fh:
    allrows = [r for r in csv.DictReader(fh) if r['expected'] in ('A', 'B', 'none')]
if os.environ.get('EF3CT_TEST'):                            # smoke test: first rows only, output to the given folder
    allrows = allrows[:int(os.environ.get('EF3CT_ROWS', 8000))]; OUT = os.environ['EF3CT_TEST']; os.makedirs(OUT, exist_ok=True)
ref_em = {}
with gzip.open(os.path.join(R, 'offline_emulation.csv.gz'), 'rt') as fh:
    for r in csv.DictReader(fh): ref_em[(r['case_id'], r['bay_id'], r['calibration'])] = r
maxdiff = 0.0; chk3i0 = 0.0
LOW, COV, OPP, OFF, OFFB = (collections.defaultdict(lambda x=x: np.full(len(GRID), x)) for x in (1.0, 1.0, 0.0, 0.0, 0.0))
IES = collections.defaultdict(lambda: [0.0, 0.0, 0.0, ''])    # (tag, config) -> [max |3I0m|, max |error|, max P(>=10 A), where]
pathmin = collections.defaultdict(lambda: 1e9); offBmax = collections.defaultdict(float)

def meta(r):
    c = cases[r['case_id']]
    role = PATH.get((c['config'], c['loc']), {}).get(r['bay_id'])
    return c, role

def aggregate(tag, sysk, rf, rmeta, pB, pA, cal):
    """Fold per-row probabilities (rows x GRID) into the minimum/maximum tables."""
    exp = np.array([m[0] for m in rmeta]); role = np.array([m[1] or '' for m in rmeta]); a20 = np.array([m[2] for m in rmeta])
    opp = np.where(exp == 'B', pA, 0) + np.where(exp == 'A', pB, 0) if pB.ndim == 1 else \
          np.where((exp == 'B')[:, None], pA, 0) + np.where((exp == 'A')[:, None], pB, 0)
    k = tag + (sysk, cal)
    pb = role == 'pathB'
    if pb.any():
        COV[k + (rf,)] = np.minimum(COV[k + (rf,)], pB[pb].min(0))
        if rf <= 30: LOW[k] = np.minimum(LOW[k], pB[pb].min(0))
    ab = (exp == 'A') | (exp == 'B')
    if ab.any(): OPP[k] = np.maximum(OPP[k], opp[ab].max(0))
    off = ~a20 & ((role == '') | np.char.startswith(role.astype(str), 'off'))
    if off.any():
        bad = np.where((exp == 'none')[:, None], pA + pB, opp)
        OFF[k] = np.maximum(OFF[k], bad[off].max(0))
    ob = role == 'offB'
    if ob.any(): OFFB[k] = np.maximum(OFFB[k], pB[ob].max(0))

def decide(Im, aIm, ref, vf):
    pB = np.empty((Im.shape[0], len(GRID))); pA = np.empty_like(pB)
    Iq = Im * np.sin(aIm - ref)
    for j, (v, i) in enumerate(GRID):
        on = vf > v / 100
        pB[:, j] = (on & (Iq > i)).mean(1); pA[:, j] = (on & (Iq < -i)).mean(1)
    return pB, pA

t0 = time.time()
for s0 in range(0, len(allrows), CHUNK):
    part = allrows[s0:s0 + CHUNK]; n = len(part); rng = np.random.default_rng(SEED + s0)
    I = np.array([float(r['I0x3_A']) for r in part]); aI = np.radians([float(r['ang_I0x3_deg']) for r in part])
    V = np.array([float(r['V0_kV']) for r in part]); aV = np.radians([float(r['ang_V0_deg']) for r in part])
    VD = {}
    for cal, ev in ce.CAL.items():                          # the draws of compass_emulation.emulate, in its order
        eI = rng.uniform(-1, 1, (n, N)) * np.maximum(0.03 * I, 0.1)[:, None]
        ang = np.radians(rng.uniform(-5, 5, (n, N)))
        Vm = V[:, None] * (1 + rng.uniform(-ev, ev, (n, N))) * np.exp(1j * aV[:, None]) \
             + rng.uniform(0, 0.02, (n, N)) * ce.E_N * np.exp(1j * rng.uniform(0, 2 * np.pi, (n, N)))
        ref, vf = np.angle(-Vm), np.abs(Vm) / ce.E_N
        VD[cal] = (ang, ref, vf)
        # SumCT reference: reproduce the published emulation on its grid, then evaluate on the 3CT grid
        Im = np.abs(I[:, None] + eI); aIm = aI[:, None] + ang; Iq = Im * np.sin(aIm - ref)
        for kr, r in enumerate(part):
            old = ref_em[(r['case_id'], r['bay_id'], cal)]
            for v in ce.V_NEQ:
                on = vf[kr] > v
                for i in ce.I_EQ:
                    maxdiff = max(maxdiff, abs((on & (Iq[kr] > i)).mean() - float(old[f'pB_v{int(v * 100)}_i{i}'])),
                                  abs((on & (Iq[kr] < -i)).mean() - float(old[f'pA_v{int(v * 100)}_i{i}'])))
        pB, pA = decide(Im, aIm, ref, vf)
        by = collections.defaultdict(list)
        for kr, r in enumerate(part):
            c, role = meta(r); sk = sys_of(c)
            if sk: by[(sk, int(c['RF_ohm']))].append(kr)
        for (sk, rf), idx in by.items():
            rm = [(part[x]['expected'], PATH.get((cases[part[x]['case_id']]['config'], cases[part[x]['case_id']]['loc']), {}).get(part[x]['bay_id']),
                   part[x]['station'] == 'A20') for x in idx]
            aggregate(REF + ('',), sk, rf, rm, pB[idx], pA[idx], cal)
            if cal == 'standard' and rf == 0:
                for x, m in zip(idx, rm):
                    if m[1] == 'pathB': pathmin[sk] = min(pathmin[sk], I[x])
                    elif m[1] == 'offB': offBmax[sk] = max(offBmax[sk], I[x])
    # 3CT on the rows of the main-cable 500 MVA base and shunt cases
    sel = [kr for kr, r in enumerate(part) if (r['case_id'], r['bay_id']) in FC]
    for b0 in range(0, len(sel), BLOCK):
        idx = np.array(sel[b0:b0 + BLOCK]); nb = len(idx)
        info = []
        for kr in idx:
            r = part[kr]; c, role = meta(r); sk = sys_of(c)
            if c['earthing'] == 'earthed': levels = ['winter_peak']
            elif sk and cases[r['case_id']]['group'] == 'ic_sweep': levels = list(UNIFORM)
            elif sk: levels = list(SNAP)
            else: levels = []
            info.append((r, c, role, sk, levels))
        I0x3 = np.array([FC[(r['case_id'], r['bay_id'])][0] for r, *_ in info])
        I1f = np.array([FC[(r['case_id'], r['bay_id'])][1] for r, *_ in info])
        chk3i0 = max(chk3i0, float(np.max(np.abs(np.abs(I0x3) - I[idx]))))
        fault = np.stack([I0x3 / 3 + I1f + I1f, I0x3 / 3 + A ** 2 * I1f + A * I1f, I0x3 / 3 + A * I1f + A ** 2 * I1f], 1)
        for ci, cb in enumerate(COMBOS):
            r2 = np.random.default_rng([SEED, s0, b0, ci])
            gk = r2.uniform(-cb['gain'], cb['gain'], (nb, N, 3))
            th = np.exp(1j * np.radians(r2.uniform(-cb['theta'], cb['theta'], (nb, N, 3)))) if cb['theta'] else 1.0
            ek = r2.uniform(0, 0.5, (nb, N, 3)) * np.exp(1j * r2.uniform(0, 2 * np.pi, (nb, N, 3)))
            psi = np.exp(1j * r2.uniform(0, 2 * np.pi, (nb, N)))
            for lv in ('winter_peak', 'summer_min') + UNIFORM:
                rows_lv = [j for j, x in enumerate(info) if lv in x[4]]
                if not rows_lv: continue
                IL = np.zeros(nb, complex)
                for j in rows_lv:
                    r, c, role, sk, _ = info[j]
                    if isinstance(lv, int):
                        IL[j] = lv * cmath.exp(-1j * PF_ANG) * (-1 if FACES.get((c['config'], r['bay_id'])) else 1)
                    else:
                        IL[j] = LOAD.get((c['config'], lv, r['bay_id']), 0j)
                rr = np.array(rows_lv)
                ratio = UNB[lv][cb['unb']]; m2 = (ratio - 1) / (ratio + 1)
                Ik = (IL[:, None] * np.array([1, A ** 2, A]) + fault)[rr]                      # true phase currents
                Ik_s = Ik[:, None, :] + (m2 * np.abs(IL[rr])[:, None] * psi[rr])[:, :, None] * np.array([1, A, A ** 2])
                big = (np.abs(Ik) >= 50)[:, None, :]
                meas = (np.where(big, Ik_s * (1 + gk[rr]), Ik_s + ek[rr]) * (th[rr] if cb['theta'] else 1.0)).sum(2)
                Im, aIm0 = np.abs(meas), np.angle(meas)
                iso = []
                for k, j in enumerate(rows_lv):
                    r, c, role, sk, _ = info[j]
                    if c['earthing'] != 'earthed': iso.append(k); continue
                    if r['station'] == 'A20' or role in ('pathB', 'pathA'): continue              # healthy ComPass bays only
                    key = (ctag(cb), c['config'])
                    mx = float(Im[k].max()); er = float(np.abs(meas[k] - I0x3[j]).max()); p10 = float((Im[k] >= 10).mean())
                    st = IES[key]
                    if mx > st[0]: st[0], st[3] = mx, f"{r['bay_id']} {c['loc']} RF {c['RF_ohm']}"
                    st[1] = max(st[1], er); st[2] = max(st[2], p10)
                if not iso: continue
                iso = np.array(iso); gi = idx[rr][iso]
                for cal in ce.CAL:
                    ang, ref, vf = VD[cal]
                    pB, pA = decide(Im[iso], aIm0[iso] + ang[gi], ref[gi], vf[gi])
                    by = collections.defaultdict(list)
                    for k, kk in enumerate(iso): by[(info[rows_lv[kk]][3], int(info[rows_lv[kk]][1]['RF_ohm']))].append(k)
                    for (sk, rf), ks in by.items():
                        rm = [(info[rows_lv[iso[k]]][0]['expected'], info[rows_lv[iso[k]]][2], info[rows_lv[iso[k]]][0]['station'] == 'A20') for k in ks]
                        aggregate(ctag(cb) + (str(lv),), sk, rf, rm, pB[ks], pA[ks], cal)
    print(f'{min(s0 + CHUNK, len(allrows))}/{len(allrows)}  {time.time() - t0:.0f} s', flush=True)
print(f'SumCT reproduction: largest difference to offline_emulation.csv.gz {maxdiff:.4f} (3-decimal rounding: <= 0.0005)')
print(f'3I0 of the fault-contribution solve against offline_phasors.csv: largest difference {chk3i0:.2e} A')

# ------------------------------------------------------------------ 4. outputs
tags = sorted({k[:5] for k in LOW} | {k[:5] for k in OPP}, key=str)
sys_order = [s[0] for s in SYSTEMS]
def keys_for(sk): return [t for t in tags if any(k[:5] == t and k[5] == sk for k in OPP)]
dp, cv, pr, win = [], [], [], []
for sk in sys_order:
    for t in keys_for(sk):
        for cal in ce.CAL:
            k = t + (sk, cal)
            for j, (v, i) in enumerate(GRID):
                dp.append([sk, *t, cal, v, i, f'{LOW[k][j]:.4f}' if k in LOW else '', f'{OPP[k][j]:.4f}', f'{OFF[k][j]:.4f}'])
                lim = None
                for rf in RFS:
                    if k + (rf,) in COV and COV[k + (rf,)][j] >= 0.95: lim = rf
                    else: break
                cv.append([sk, *t, cal, v, i, '' if lim is None else lim])
                for rf in RFS:
                    if k + (rf,) in COV: pr.append([sk, *t, cal, v, i, rf, f'{COV[k + (rf,)][j]:.4f}'])
        k = t + (sk, 'standard'); j20 = [j for j, (v, i) in enumerate(GRID) if v == 20]
        ok99 = [GRID[j][1] for j in j20 if k in LOW and LOW[k][j] >= 0.99 and OPP[k][j] <= 0.01]
        quiet = [GRID[j][1] for j in j20 if OFFB[k][j] <= 0.01]
        both = [i for i in ok99 if i in quiet]
        win.append([sk, *t, f'{pathmin[sk]:.2f}' if pathmin[sk] < 1e9 else '', ' '.join(map(str, ok99)),
                    f'{offBmax[sk]:.2f}', (f'{min(both)} to {max(both)}' if both else 'none') if pathmin[sk] < 1e9 else 'no ComPass on any path'])
cols = HDR + ['calibration', 'V_NEQ_pct', 'I_EQ_A']
write('direction_probability_3ct.csv', cols + ['min_P_B_path_RF_le_30', 'max_P_opposite_any_bay', 'max_P_opposite_or_false_offpath'], dp)
write('coverage_rf_3ct.csv', cols + ['max_RF_ohm_P95'], cv)
write('path_probability_rf_3ct.csv', cols + ['RF_ohm', 'min_P_B_path'], pr)
write('windows_3ct.csv', HDR + ['smallest_path_current_A', 'I_EQ_meeting_99pct_std_cal_VNEQ20', 'largest_offpath_forward_current_A',
                               'strict_window_A'], win)
summarize()

# IES> check (earthed, healthy ComPass bays, winter peak) and the load error alone (no fault)
ies = [[*key[0], key[1], f'{v[0]:.2f}', f'{v[1]:.2f}', f'{v[2]:.4f}', v[3]] for key, v in sorted(IES.items(), key=str)]
alone = []
for cb in COMBOS:
    r2 = np.random.default_rng([SEED, 99, COMBOS.index(cb)])
    for cfg in ('split',):
        for lv in SNAP:
            bids = [b for b in bay_el if (cfg, lv, b) in LOAD and not b.startswith('A20')]
            IL = np.array([LOAD[(cfg, lv, b)] for b in bids]); nb = len(bids)
            ratio = UNB[lv][cb['unb']]; m2 = (ratio - 1) / (ratio + 1)
            Ik = IL[:, None] * np.array([1, A ** 2, A])
            psi = np.exp(1j * r2.uniform(0, 2 * np.pi, (nb, N)))
            Ik_s = Ik[:, None, :] + (m2 * np.abs(IL)[:, None] * psi)[:, :, None] * np.array([1, A, A ** 2])
            gk = r2.uniform(-cb['gain'], cb['gain'], (nb, N, 3)); ek = r2.uniform(0, 0.5, (nb, N, 3)) * np.exp(1j * r2.uniform(0, 2 * np.pi, (nb, N, 3)))
            th = np.exp(1j * np.radians(r2.uniform(-cb['theta'], cb['theta'], (nb, N, 3))))
            big = (np.abs(Ik) >= 50)[:, None, :]
            err = np.abs((np.where(big, Ik_s * (1 + gk), Ik_s + ek) * th).sum(2))
            w = int(err.max(1).argmax())
            alone.append([*ctag(cb), f'{cfg} no fault', lv, f'{err.max():.2f}', f'{np.percentile(err, 99):.2f}', f'{(err >= 10).mean(1).max():.4f}',
                          f'{bids[w]} ({abs(IL[w]):.0f} A)'])
write('ies_check_3ct.csv', ['error_model', 'phase_sensor', 'theta_deg', 'unbalance', 'case', 'load_level', 'max_3I0_meas_A',
                            'p99_or_max_error_A', 'max_P_ge_10A', 'where'],
      [r[:4] + [f'earthed faults, {r[4]}', 'winter_peak', r[5], r[6], r[7], r[8]] for r in ies] + alone)
print('written: results/ch6/*_3ct.csv')
