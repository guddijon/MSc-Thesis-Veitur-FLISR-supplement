"""Station order of the A20 circuits and the open points between them in the switching state of the DGS file (the
December 2025 base state, winter peak of 10 Dec 2025); the trace behind the open-ring table of thesis Chapter 4
(Table 4.12).

Each circuit is traced from its A20 cubicle through closed elements, without passing back through A20. A station belongs
to the circuit whose trace reaches its transformer (its 0.4 kV terminal; the busbar for a station without one); its
distance is the cable length from A20 to that terminal and its upstream station the last other station passed on the
way. Each open coupler or switch outside A20 is listed with, on either side, the circuit, the station of the open
element (or the nearest station passed) and the station the trace came from.
Output: output/open_rings_stations.csv, output/open_rings_open_points.csv.
Run: python3 open_rings.py"""
import re, csv, heapq, collections
import radial_pf as rp, restoration_sweep as rs
from paths import data, out

r = rp.parse(data('akranes_11kv_benchmark.dgs'))
T = r['ElmTerm']; name = {k: v['loc_name'] for k, v in T.items()}; byname = {v: k for k, v in name.items()}
sub = {k: v['loc_name'] for k, v in r['ElmSubstat'].items()}

def station(t):
    """Station of a terminal from its name or its substation folder ('1012-1' -> D1012; A20 is 'Millispennustæði 20')."""
    s = rs.station_of(name[t])
    if s: return s
    folder = sub.get(T[t]['fold_id'], '')
    m = re.match(r'(\d{4})-', folder)
    return 'D' + m.group(1) if m else ('A20' if folder.startswith('Millispennust') else None)

lv = {station(t) for t in T if '_LV' in name[t]}
def anchor(t):
    """Terminal that places a station on a circuit: its 0.4 kV terminal, or a busbar for a station without one."""
    s = station(t)
    if s in (None, 'A20'): return False
    return '_LV' in name[t] if s in lv else T[t]['iUsage'] == '0'
net = rs.Net.__new__(rs.Net); net.rows0 = r
edges = net.graph(r, include_open=True)
adj = collections.defaultdict(list)
for e in edges:
    e['km'] = rp.f(r['ElmLne'][e['fid']]['dline']) if e['kind'] == 'lne' else 0.0
    adj[e['a']].append((e['b'], e)); adj[e['b']].append((e['a'], e))

# circuits energised from A20: cubicle terminal A20_Cnn connected to a busbar through closed elements inside A20
live = set(byname[b] for b in ('A20_BB1', 'A20_BB2')); stack = list(live)
while stack:
    t = stack.pop()
    for y, e in adj[t]:
        if not e['open'] and y not in live and station(y) == 'A20': live.add(y); stack.append(y)
heads = sorted(name[t][-2:] for t in live if re.fullmatch(r'A20_C\d\d', name[t]))

reach = {}                                             # terminal -> (circuit, km from A20, last station passed)
# up[t]: the last two distinct stations passed on the way to t (a station's own terminals can lie on either side of a joint)
rows = []
for c in heads:
    t0 = byname['A20_C' + c]; dist = {t0: 0.0}; up = {t0: ('A20',)}; heap = [(0.0, t0)]; done = set()
    while heap:
        d, t = heapq.heappop(heap)
        if t in done: continue
        done.add(t); reach[t] = (c, d, up[t]); s = station(t)
        for y, e in adj[t]:
            if e['open'] or station(y) == 'A20': continue
            if d + e['km'] < dist.get(y, 1e9):
                dist[y] = d + e['km']; up[y] = (up[t] + (s,))[-2:] if s and s != up[t][-1] else up[t]; heapq.heappush(heap, (dist[y], y))
    first = {}
    for t in done:
        if anchor(t) and (station(t) not in first or dist[t] < first[station(t)][0]): first[station(t)] = (dist[t], [u for u in up[t] if u != station(t)][-1])
    for i, (s, (d, u)) in enumerate(sorted(first.items(), key=lambda x: x[1][0]), 1):
        rows.append((c, i, s, u, round(d, 3)))
fed = {s for _, _, s, _, _ in rows}
dead = sorted({station(t) for t in T if anchor(t)} - fed)

opens = []
for e in edges:
    if not e['open'] or 'A20' in (station(e['a']), station(e['b'])): continue
    side = []
    for t in (e['a'], e['b']):
        c, d, u = reach.get(t, ('', None, ('',)))
        s = station(t) or u[-1]
        side += [c or 'not energised', s, ([x for x in u if x != s] or [''])[-1], '' if d is None else round(d, 3)]
    if e['kind'] == 'cpl': label = e['name']
    else:                                              # open switch in a cable cubicle: cable name and switch station
        sw = next(x for x in r['StaSwitch'].values() if x['loc_name'] == e['opensw'])
        label = f"{e['name'].split(' (')[0]} open at {station(r['StaCubic'][sw['fold_id']]['fold_id'])}"
    opens.append([label] + side)

with open(out('open_rings_stations.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['circuit', 'order', 'station', 'upstream_station', 'km_from_A20'])
    w.writerows(rows); w.writerows(('', '', s, 'not energised', '') for s in dead)
with open(out('open_rings_open_points.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['open_element', 'circuit_a', 'station_a', 'from_a', 'km_a', 'circuit_b', 'station_b', 'from_b', 'km_b'])
    w.writerows(sorted(opens))
for c in heads:
    print(f'{c}: ' + ', '.join(f'{s}' + (f' (from {u})' if u != prev else '')
                               for prev, (_, _, s, u, _) in zip(['A20'] + [x[2] for x in rows if x[0] == c],
                                                                [x for x in rows if x[0] == c])))
print('not energised:', ', '.join(dead))
for o in sorted(opens): print('open', o)
