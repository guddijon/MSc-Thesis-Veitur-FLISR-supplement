"""Selectivity of the ComPass sin(phi) indication on the Akranes topology (offline model).

Every energised ComPass line bay is classed by its role relative to the fault:
  strong   : expected B and the bay faces away from A20 toward the fault, i.e. it lies on the path A20 -> fault and
             carries the return current of the whole system minus what lies beyond it
  weak     : expected B but A20 lies in the direction of its cable (downstream stations of the faulted feeder, the
             A20-facing bay of every station on a healthy feeder): it carries only the charging current of the cable
             behind it
  reverse  : expected A (charging current of the cable in front of it)
For FLISR the useful pattern is: strong bays indicate, all others stay silent. A pickup I_EQ gives that pattern if
min(strong) > I_EQ > max(weak, reverse) with the measurement margin. Both groups scale with V0, so the ratio is fixed
by the topology and the system size, and fault resistance only moves both down together.

Writes results/selectivity.csv (one row per case at R_F = 0) and prints a summary per system size.
"""
import os, sys, csv, math, cmath, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ef_network as ef

rows = ef.load_rows()
bays = [(st, k, e) for st, _, k, e in ef.BAYS]

def a20_behind(net, kind, name, st):
    """True if A20 is reached through the bay's cable without passing the bay's own node."""
    ct, lines = net.bay_lines(kind, name, st)
    if not lines: return None
    busnode = net.node(ct)
    adj = collections.defaultdict(set)
    for ln in net.lines:
        a, b = net.node(ln['a']), net.node(ln['b']); adj[a].add(b); adj[b].add(a)
    srcs = {net.node(t) for t in net.src.values() if t}
    starts = {net.node(ln['b'] if s > 0 else ln['a']) for ln, s in lines}
    seen = set(starts); stack = list(starts)
    while stack:
        n = stack.pop()
        if n in srcs: return True
        for m in adj[n]:
            if m != busnode and m not in seen: seen.add(m); stack.append(m)
    return False

def classify(net, V0, E):
    out = []
    for st, k, e in bays:
        I = net.bay_current(V0, k, e, st)
        if I is None: continue
        ct, _ = net.bay_lines(k, e, st); v0 = V0[net.idx[net.node(ct)]]
        if abs(v0) < 1e-6 * E: continue                                    # other busbar section
        phi = cmath.phase(I) - cmath.phase(-v0); iq = abs(I) * 1000 * math.sin(phi)
        exp = net.expected_direction(k, e, st)
        # on the A20 -> fault path exactly one of A20 and the fault lies through the bay's cable
        a20 = a20_behind(net, k, e, st)
        role = 'path' if ((exp == 'B') != a20) else 'offpath'
        out.append((st, e, role, iq))
    return out

SYSTEMS = [('BB2 natural (21 A)', 'split', 'A20_BB2', 0.0, ef.BB2_LOCS), ('BB1 natural (60 A)', 'split', 'A20_BB1', 0.0, ef.BB1_LOCS),
           ('coupled N-1 (82 A)', 'coupled', 'A20_BB1', 0.0, ef.BB1_LOCS + ef.BB2_LOCS)]
for r in csv.DictReader(open(os.path.join(HERE, 'shunt_sizing.csv'))):
    if r['busbar'] == 'A20_BB2' and r['C_add_uF_per_phase']:
        SYSTEMS.append((f"BB2 + shunt ({r['target_Ic_A']} A)", 'split', 'A20_BB2', float(r['C_add_uF_per_phase']), ef.BB2_LOCS))

out = []
print(f"{'system':22s} {'loc':6s} {'IF':>6s} {'path n':>7s} {'path min':>9s} {'off max':>8s} {'window':>18s}")
for name, cfg, bus, cuf, locs in SYSTEMS:
    for loc in locs:
        try: net = ef.Net(rows, cfg, 'isolated', 'main', c_add_uF=cuf, c_add_bus=bus, location=ef.location(loc, rows))
        except KeyError: continue
        s = net.solve([0])[0]
        cl = classify(net, s['V0'], s['E'])
        strong = [abs(iq) for st, e, r, iq in cl if r == 'path']
        other = [abs(iq) for st, e, r, iq in cl if r != 'path']
        smin = min(strong) if strong else None; omax = max(other) if other else 0.0
        # measurement margin: 3 % or 0.1 A on each side, plus 5 deg angle (sin 85 deg = 0.996, negligible at 90 deg)
        lo = omax * 1.03 + 0.1; hi = smin / 1.03 - 0.1 if smin else None
        win = f'{lo:5.1f} to {hi:5.1f} A' if hi and hi > lo else ('none' if strong else 'no ComPass on path')
        print(f"{name:22s} {loc:6s} {abs(3 * s['I0']) * 1000:6.1f} {len(strong):7d} {(smin or 0):9.2f} {omax:8.2f} {win:>18s}")
        out.append([name, loc, f"{abs(3 * s['I0']) * 1000:.2f}", len(strong), f'{smin:.3f}' if smin else '', f'{omax:.3f}',
                    f'{lo:.2f}', f'{hi:.2f}' if hi else '', ';'.join(f'{st}:{e}' for st, e, r, iq in cl if r == 'path')])
with open(os.path.join(HERE, 'results', 'selectivity.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['system', 'loc', 'IF_A', 'n_path_bays', 'path_min_absIq_A', 'offpath_max_absIq_A', 'window_lo_A', 'window_hi_A', 'path_bays'])
    w.writerows(out)
