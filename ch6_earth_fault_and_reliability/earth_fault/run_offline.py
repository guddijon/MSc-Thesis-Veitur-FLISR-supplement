"""Offline sweep of the earth-fault study matrix (tables/cases.csv) with the sequence-network model ef_network.py.
Writes results in the common format shared with the GUI parser and the PowerFactory script:

  results/offline_phasors.csv   one row per case and measuring point:
      case_id, source, bay_id, station, I0x3_A, ang_I0x3_deg, V0_kV, ang_V0_deg, E_kV, expected
      (I0x3 = residual current 3 I0 toward the cable; V0 = zero-sequence phase-to-earth voltage at the bay's V0
       reference terminal; expected = A / B per the topology rule, 'none' for bays in the other busbar section)
  results/offline_cases.csv     one row per case: fault current |3 I0|, |V0|/E at the fault, Z1, Z0 at the fault
"""
import os, sys, csv, math, cmath, collections, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ef_network as ef

T = os.path.join(HERE, 'tables'); R = os.path.join(HERE, 'results'); os.makedirs(R, exist_ok=True)
rows = ef.load_rows()
cases = list(csv.DictReader(open(os.path.join(T, 'cases.csv'))))
bays = list(csv.DictReader(open(os.path.join(T, 'bays.csv'))))
bay_el = collections.OrderedDict()
for b in bays: bay_el.setdefault(b['bay_id'], (b['station'], b['element_class'], b['element'], b['v0_reference_terminal']))

groups = collections.defaultdict(list)
for c in cases:
    key = (c['earthing'], c['cable_set'], c['config'], c['loc'], c['Sk_MVA'], c['c_add_bus'], c['c_add_uF_per_phase'])
    groups[key].append(c)

t0 = time.time()
with open(os.path.join(R, 'offline_phasors.csv'), 'w', newline='') as fp, open(os.path.join(R, 'offline_cases.csv'), 'w', newline='') as fc:
    wp = csv.writer(fp); wc = csv.writer(fc)
    wp.writerow(['case_id', 'source', 'bay_id', 'station', 'I0x3_A', 'ang_I0x3_deg', 'V0_kV', 'ang_V0_deg', 'E_kV', 'expected'])
    wc.writerow(['case_id', 'IF_A', 'V0_over_E_at_fault', 'Z1_ohm', 'Z0_ohm', 'C0_energised_uF'])
    for (earth, cset, cfg, loc, sk, cbus, cuf), cs in groups.items():
        net = ef.Net(rows, cfg, earth, cset, c_add_uF=float(cuf) if cuf else 0.0, c_add_bus=cbus or 'A20_BB1',
                     Sk_MVA=float(sk), location=ef.location(loc, rows))
        sols = net.solve([float(c['RF_ohm']) for c in cs])
        def first(fun, k, e, st):
            for el in e.split('|'):                    # A20 feeder heads: the closed one of the two busbar bays
                v = fun(k, el, st)
                if v is not None: return v
            return None
        exp = {bid: first(net.expected_direction, k, e, st) for bid, (st, k, e, vref) in bay_el.items()}
        vref_node = {}
        for bid, (st, k, e, vref) in bay_el.items():
            tid = [x for x, nm in net.tname.items() if nm == vref]
            vref_node[bid] = net.idx.get(net.node(tid[0])) if tid and net.node(tid[0]) in net.idx else None
        for c, s in zip(cs, sols):
            F = net.idx[net.loc['node']]
            wc.writerow([c['case_id'], f"{abs(3 * s['I0']) * 1000:.4f}", f"{abs(s['V0'][F]) / s['E']:.5f}",
                         f"{s['Z1']:.5f}", f"{s['Z0']:.3f}", f"{net.capacitance_uF():.4f}"])
            for bid, (st, k, e, vref) in bay_el.items():
                I = first(lambda k_, e_, st_: net.bay_current(s['V0'], k_, e_, st_), k, e, st)
                if I is None or vref_node[bid] is None: continue
                v0 = s['V0'][vref_node[bid]]
                # a bay in the other, galvanically separate busbar section sees no displacement voltage: no indication expected
                e_dir = (exp[bid] or '') if abs(v0) > 1e-6 * s['E'] else 'none'
                wp.writerow([c['case_id'], 'offline', bid, st, f"{abs(I) * 1000:.5f}", f"{math.degrees(cmath.phase(I)):.3f}",
                             f"{abs(v0):.6f}", f"{math.degrees(cmath.phase(v0)):.3f}", f"{s['E']:.5f}", e_dir])
print(f'{len(groups)} network solutions, {len(cases)} cases, {time.time() - t0:.0f} s')
