"""Reliability Monte Carlo for the Akranes 11 kV network (thesis Section 6.4, RQ5).

Compares three restoration processes on the present network:
  (i)   crew-based sectionalizing (segment-level isolation by the crew),
  (ii)  FPI-assisted remote sectionalizing by the control room (zone-level isolation at the remotely controlled
        stations, crew for the rest),
  (iii) automated FLISR (zone-level isolation at the remotely controlled stations within minutes, crew for the rest).

Inputs: fault record and stage durations of the seven fault days 2020-2026
(data/akranes_fault_stages_2020-2026.csv); customers per station
(data/customers_per_station.csv, OMS register 20 Oct 2026, 3 516 customers in 47 stations);
feeder topology and section lengths of the benchmark model (sld_bays.txt and gis_vs_model_lengths.csv),
December 2025 base configuration with D1018 on circuit 22.

Assumptions (documented in mc_reliability_assumptions.md):
 1. Fault population = the seven fault days (feeder or busbar faults needing sectionalizing): rate 7 / 6.83 a, carried
    as its Jeffreys posterior Gamma(7.5, 6.83 a); a fault lands on a feeder with probability proportional to its cable
    length and on a section with probability proportional to the section length; two of seven faults are busbar events.
 2. Crew and remote stage durations resampled from the seven fault days: response (call-out) 26-68 min for both,
    crew sectionalizing 38-63 min, remote sectionalizing 6-22 min, time to the last customer (repair) 92-941 min.
 3. FLISR: 1-5 min (uniform) for the customers it can restore; isolation only at the remotely controlled stations, so
    the customers between the two nearest remotely controlled switching points wait for the crew (segment isolation
    at response + crew sectionalizing). Customers downstream of a fault with no tie in their subtree wait for repair.
 4. Busbar events: all customers of the busbar's feeders are out for the measured busbar re-closing time (31 or
    41 min) in all three processes; the feeder on which the fault lies is then handled by the process rules.
Every interruption is counted in SAIFI and SAIDI regardless of duration; a second SAIFI counts only interruptions
longer than 5 min (the IEEE 1366 sustained-interruption threshold).
"""
import csv, sys, os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RNG = np.random.default_rng(20261022)
ARRAYS = {}   # block-level arrays of the last run, for the figure script

# ---------------- topology (parent -> child, section length m), December 2025 base, from the model
FEEDERS = {
 '13': {'bus': 2, 'sections': [('A20','D1019',463),('D1019','D1029',602),('D1029','D1066',322),('D1066','D1023',591),
        ('D1023','D1050',439),('D1050','D1025',314),('D1025','D1027',258),('D1027','D1030',475),('D1030','D1041',773),
        ('D1041','D1045',878),('D1041','D1051',383),('D1051','D1058',537)], 'ties': {'D1058'}},
 '08': {'bus': 2, 'sections': [('A20','D1049',751),('D1049','D1061',600),('D1061','D1062',360)], 'ties': {'D1062'}},
 '22': {'bus': 1, 'sections': [('A20','D1028',1293),('D1028','D1005',492),('D1005','D1036',89),('D1036','D1004',132),
        ('D1005','D1003',107),('D1003','D1040',286),('D1040','D1018',176)], 'ties': {'D1004','D1003','D1018'}},
 '21': {'bus': 1, 'sections': [('A20','D1042',528),('D1042','D1026',637),('D1026','D1001',332),('D1001','D1002',937)], 'ties': {'D1002'}},
 '06': {'bus': 1, 'sections': [('A20','D1014',1336),('D1014','D1012',498),('D1012','D1011',365),('D1011','D1052',453),
        ('D1052','D1009',117),('D1009','D1008',461),('D1008','D1017',108)], 'ties': {'D1012','D1008'}},
 '05': {'bus': 1, 'sections': [('A20','D1070',481),('D1070','D1046',526),('D1046','D1015',375),('D1015','D1020',486),
        ('D1020','D1021',655),('D1021','D1013',189),('D1020','D1016',396)], 'ties': {'D1013','D1016'}},
 '10': {'bus': 1, 'sections': [('A20','D1053',15),('D1053','D1034',281),('D1034','D1057',80),('D1057','D1022',609)], 'ties': {'D1022'}},
 '19': {'bus': 1, 'sections': [('A20','D1056',1419),('D1056','D1059',252)], 'ties': set()},
 '11': {'bus': 1, 'sections': [('A20','D1055',272),('D1055','D1054',1276),('D1054','D1067',334)], 'ties': {'D1054'}},
 '09': {'bus': 1, 'sections': [('A20','D1031',1599),('D1031','D1032',1220),('D1032','D1043',501)], 'ties': {'D1031'}},
}
REMOTE = {'D1001','D1004','D1025','D1026','D1029','D1030','D1056','D1061','D1062','D1066','D1070','D1067'}  # 12 in service

# ---------------- measured stage durations (minutes), seven fault days
RESPONSE = np.array([36,26,29,41,31,68,52], float)      # trip to first switching operation, all seven days
SECT_CREW = np.array([63,45,38], float)                 # crew sectionalizing to first restoration (single-feeder crew days)
SECT_REMOTE = np.array([22,6], float)                   # remote sectionalizing to first restoration (2025 days)
LAST = np.array([154,123,116,941,125,92,478], float)    # trip to last customer restored, all seven days
BUSBAR_RECLOSE = np.array([41,31], float)               # busbar days: trip to re-close of the busbar feeders
N_FAULT_DAYS, YEARS, N_BUSBAR = 7, 6.83, 2

def load_customers():
    p = os.path.join(ROOT, 'data', 'customers_per_station.csv')
    return {r['station']: int(r['customers']) for r in csv.DictReader(open(p))}

class Feeder:
    def __init__(self, name, spec, cust):
        self.name = name; self.bus = spec['bus']; self.ties = spec['ties']
        self.parent = {}; self.children = {}; self.length = {}
        for p, c, L in spec['sections']:
            self.parent[c] = p; self.children.setdefault(p, []).append(c); self.children.setdefault(c, []); self.length[c] = L
        self.stations = [s for s in self.parent]            # every node except A20
        self.cust = {s: cust.get(s, 0) for s in self.stations}
        self.total_len = sum(self.length.values())
        self.total_cust = sum(self.cust.values())
    def subtree(self, s):
        out = [s]; stack = [s]
        while stack:
            for c in self.children.get(stack.pop(), []): out.append(c); stack.append(c)
        return out
    def classify(self, c):
        """fault on the section parent(c) -> c. Returns dict of station sets for the three isolation logics."""
        p = self.parent[c]
        down = set(self.subtree(c))
        up = set(self.stations) - down
        down_has_tie = bool(down & self.ties)
        # segment-level (crew): all upstream back at first restoration; downstream back if a tie exists in it
        seg = {'quick': up | (down if down_has_tie else set()), 'repair': set() if down_has_tie else down}
        # zone-level (remote switches only)
        # upstream boundary: nearest remotely controlled station on the path p -> A20
        u = p
        while u != 'A20' and u not in REMOTE: u = self.parent[u]
        if u == 'A20': zone_up = up                             # no remote switch upstream: everything upstream waits for the crew
        else:
            child_on_path = c
            while self.parent[child_on_path] != u: child_on_path = self.parent[child_on_path]
            zone_up = (set(self.subtree(child_on_path)) - down)   # below u towards the fault
        quick_up = up - zone_up
        # downstream: parts below the nearest remote stations (inclusive) that contain a tie are restorable at once
        quick_down = set(); zone_down = set(); repair_down = set()
        if down_has_tie:
            def walk(n):
                if n in REMOTE:
                    sub = set(self.subtree(n))
                    if sub & self.ties: quick_down.update(sub)
                    else: zone_down.update(sub)
                    return
                zone_down.add(n)
                for ch in self.children.get(n, []): walk(ch)
            walk(c)
        else:
            repair_down = down
        zone = {'quick': quick_up | quick_down, 'crew': zone_up | zone_down, 'repair': repair_down}
        return seg, zone

def build(cust):
    return {n: Feeder(n, s, cust) for n, s in FEEDERS.items()}

def customers(fd, S): return sum(fd.cust[s] for s in S)

def simulate(n_blocks=20000, block_years=10, verbose=True, remote=None, label='base'):
    global REMOTE
    if remote is not None: REMOTE = set(remote)
    cust = load_customers(); feeders = build(cust)
    N = sum(cust.values())
    names = list(feeders); lengths = np.array([feeders[n].total_len for n in names], float); pf = lengths / lengths.sum()
    bus_members = {1: [n for n in names if feeders[n].bus == 1], 2: [n for n in names if feeders[n].bus == 2]}
    bus_cust = {b: sum(feeders[n].total_cust for n in m) for b, m in bus_members.items()}
    # pre-compute per section the customer sets (as counts) for both logics
    sections = []   # (feeder, child, prob within feeder, seg counts, zone counts)
    for n in names:
        fd = feeders[n]
        for c in fd.stations:
            seg, zone = fd.classify(c)
            sections.append((n, c, fd.length[c] / fd.total_len,
                             {k: customers(fd, v) for k, v in seg.items()},
                             {k: customers(fd, v) for k, v in zone.items()}))
    sec_prob = np.array([pf[names.index(s[0])] * s[2] for s in sections]); sec_prob /= sec_prob.sum()
    procs = ['crew', 'remote', 'flisr']
    tot_cm = {p: np.zeros(n_blocks) for p in procs}; tot_ci = {p: np.zeros(n_blocks) for p in procs}; tot_ci5 = {p: np.zeros(n_blocks) for p in procs}; tot_ci3 = {p: np.zeros(n_blocks) for p in procs}
    per_fault = {p: [] for p in procs}
    comp = {p: {'busbar': 0.0, 'quick': 0.0, 'crew_zone': 0.0, 'repair': 0.0} for p in procs}; comp_faults = 0
    lam = RNG.gamma(N_FAULT_DAYS + 0.5, 1 / YEARS, n_blocks)        # Jeffreys posterior of the arrival rate
    nf = RNG.poisson(lam * block_years)
    for b in range(n_blocks):
        for _ in range(nf[b]):
            busbar = RNG.random() < N_BUSBAR / N_FAULT_DAYS
            R = RNG.choice(RESPONSE); Sc = RNG.choice(SECT_CREW); Sr = RNG.choice(SECT_REMOTE); F = RNG.uniform(1, 5); T = RNG.choice(LAST)
            T = max(T, R + Sc + 1)
            k = RNG.choice(len(sections), p=sec_prob); fn, c, _, seg, zone = sections[k]
            fd = feeders[fn]
            if busbar:
                bus = fd.bus; Rb = RNG.choice(BUSBAR_RECLOSE)
                others = bus_cust[bus] - fd.total_cust        # customers of the other feeders on the busbar
            else:
                Rb = 0.0; others = 0
            # restoration times per customer group, per process (minutes from the trip)
            t = {'crew':   [(seg['quick'],  max(R + Sc, Rb)), (seg['repair'], max(T, Rb))],
                 'remote': [(zone['quick'], max(R + Sr, Rb)), (zone['crew'], max(R + Sc, Rb)), (zone['repair'], max(T, Rb))],
                 'flisr':  [(zone['quick'], max(F, Rb)),      (zone['crew'], max(R + Sc, Rb)), (zone['repair'], max(T, Rb))]}
            if b < 2000:
                comp_faults += 1
                for p in procs:
                    comp[p]['busbar'] += others * Rb
                    keys = ['quick', 'repair'] if p == 'crew' else ['quick', 'crew_zone', 'repair']
                    for (nc, tm), key in zip(t[p], keys): comp[p][key] += nc * tm
            for p in procs:
                cm = others * Rb + sum(nc * tm for nc, tm in t[p])
                ci = others + sum(nc for nc, _ in t[p])
                ci5 = (others if Rb > 5 else 0) + sum(nc for nc, tm in t[p] if tm > 5)
                ci3 = (others if Rb > 3 else 0) + sum(nc for nc, tm in t[p] if tm > 3)
                tot_cm[p][b] += cm; tot_ci[p][b] += ci; tot_ci5[p][b] += ci5; tot_ci3[p][b] += ci3
                if b < 2000: per_fault[p].append((cm, ci, ci5))
    res = {}
    for p in procs:
        saidi = tot_cm[p] / N / block_years; saifi = tot_ci[p] / N / block_years; saifi5 = tot_ci5[p] / N / block_years; saifi3 = tot_ci3[p] / N / block_years
        pfc = np.array(per_fault[p]); ARRAYS[(label, p)] = dict(saidi=saidi.copy(), saifi=saifi.copy(), cm_per_fault=pfc[:, 0].copy())
        res[p] = dict(saidi_mean=saidi.mean(), saidi_p5=np.percentile(saidi, 5), saidi_p50=np.percentile(saidi, 50), saidi_p95=np.percentile(saidi, 95),
                      saifi_mean=saifi.mean(), saifi_p5=np.percentile(saifi, 5), saifi_p95=np.percentile(saifi, 95),
                      saifi5_mean=saifi5.mean(), saifi5_p5=np.percentile(saifi5, 5), saifi5_p95=np.percentile(saifi5, 95),
                      saifi3_mean=saifi3.mean(), saifi3_p5=np.percentile(saifi3, 5), saifi3_p95=np.percentile(saifi3, 95),
                      cm_per_fault_median=np.median(pfc[:, 0]), cm_per_fault_p5=np.percentile(pfc[:, 0], 5), cm_per_fault_p95=np.percentile(pfc[:, 0], 95),
                      ci_per_fault_mean=pfc[:, 1].mean())
    for p in procs:
        res[p]['components_min_per_customer_year'] = {k: v / comp_faults * float(lam.mean()) / N for k, v in comp[p].items()}
    meta = dict(label=label, remote=sorted(REMOTE), customers=N, lambda_mean=float(lam.mean()), lambda_p5=float(np.percentile(lam, 5)), lambda_p95=float(np.percentile(lam, 95)),
                n_blocks=n_blocks, block_years=block_years, feeders={n: dict(bus=feeders[n].bus, length_m=feeders[n].total_len, customers=feeders[n].total_cust, p_fault=float(pf[i])) for i, n in enumerate(names)})
    if verbose:
        print(f"customers {N}, lambda mean {meta['lambda_mean']:.2f}/a (5-95 % {meta['lambda_p5']:.2f}-{meta['lambda_p95']:.2f}), {n_blocks} blocks of {block_years} years")
        print(f"{'process':8s} {'SAIDI mean':>10s} {'p5':>7s} {'p50':>7s} {'p95':>7s} | {'SAIFI mean':>10s} {'p5':>6s} {'p95':>6s} | {'SAIFI>5min':>10s} | {'cust-min/fault med':>18s} {'p5':>8s} {'p95':>9s}")
        for p in procs:
            r = res[p]
            print(f"{p:8s} {r['saidi_mean']:10.1f} {r['saidi_p5']:7.1f} {r['saidi_p50']:7.1f} {r['saidi_p95']:7.1f} | {r['saifi_mean']:10.3f} {r['saifi_p5']:6.3f} {r['saifi_p95']:6.3f} | {r['saifi5_mean']:10.3f} | {r['cm_per_fault_median']:18.0f} {r['cm_per_fault_p5']:8.0f} {r['cm_per_fault_p95']:9.0f}")
        print("SAIDI components (min per customer-year, at the mean rate): " + "; ".join(f"{p}: " + ", ".join(f"{k} {v:.1f}" for k, v in res[p]['components_min_per_customer_year'].items()) for p in procs))
        print("feeders:", {n: (feeders[n].total_len, feeders[n].total_cust) for n in names})
    return res, meta, sections, feeders

if __name__ == '__main__':
    base_remote = set(REMOTE)
    out_all = {}
    print('== base: 12 remotely controlled stations'); res, meta, sections, feeders = simulate(label='base')
    out_all['base'] = dict(results=res, meta=meta)
    all_st = set(s for f in FEEDERS.values() for _, c, _ in f['sections'] for s in [c])
    print('== sensitivity: every station remotely controlled'); res2, meta2, _, _ = simulate(label='all_remote', remote=all_st)
    out_all['all_remote'] = dict(results=res2, meta=meta2)
    REMOTE = base_remote
    os.makedirs(os.path.join(ROOT, 'output'), exist_ok=True)
    out = os.path.join(ROOT, 'output', 'mc_reliability_results.json')
    json.dump(out_all, open(out, 'w'), indent=1, default=float)
    print('written', out)
