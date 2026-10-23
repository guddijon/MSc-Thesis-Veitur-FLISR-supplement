"""Write the study tables shared by the GUI anchor runs, the PowerFactory script and the offline sweep:

  tables/locations.csv       fault locations (PowerFactory object, fraction for line faults, section, role)
  tables/configurations.csv  switching configurations (operation scenario name in PowerFactory, switching from base)
  tables/bays.csv            ComPass line bays and A20 feeder heads: the cable segment each measures into, the end of
                             that segment at the bay (i = bus1, j = bus2) and the terminal used as the V0 reference
  tables/cases.csv           the enumerated study matrix (thesis Table 3.5 plus the sensitivities of the parameter sheet)
  tables/anchor_runs.csv     the subset run in the PowerFactory GUI to validate the offline model and the script
"""
import os, sys, csv, itertools, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ef_network as ef

OUT = os.path.join(HERE, 'tables'); os.makedirs(OUT, exist_ok=True)
rows = ef.load_rows()
PF_SCEN = {'split': 'winter_peak_boiler_off', 'coupled': 'EF_coupled_N-1', 'post02': 'SCN-02_restored',
           'post06': 'SCN-06_isolated', 'post11': 'SCN-11_isolated', 'post15': 'SCN-15_restored'}
VARIATION = {'isolated': 'EF_variant2_isolated', 'earthed': 'EF_variant1_earthed'}

def w(name, header, data):
    with open(os.path.join(OUT, name), 'w', newline='') as fh:
        wr = csv.writer(fh); wr.writerow(header); wr.writerows(data)
    print(f'{name}: {len(data)} rows')

# ---------------------------------------------------------------- locations
loc_rows = []
for l in ef.LOCATIONS:
    L = ef.location(l['loc'], rows)
    sec = 'BB1' if l['loc'] in ef.BB1_LOCS else 'BB2'
    loc_rows.append([L['loc'], L['kind'], L['obj'], L.get('frac', ''), L['feeder'], sec, L['role'], L['note']])
w('locations.csv', ['loc', 'kind', 'pf_object', 'fraction_from_terminal_i', 'feeder', 'section', 'role', 'note'], loc_rows)

# ---------------------------------------------------------------- configurations
w('configurations.csv', ['config', 'pf_operation_scenario', 'close', 'open', 'out_of_service_terminals', 'out_of_service_lines', 'description'],
  [[k, PF_SCEN[k], ' '.join(v['close']), ' '.join(v['open_']), ' '.join(v['out_terms']), ' | '.join(v['out_lines']), v['desc']] for k, v in ef.CONFIGS.items()])

# ---------------------------------------------------------------- bays (from the base network)
net = ef.Net(rows, 'split', 'isolated', 'main')
lid = {x['loc_name']: k for k, x in rows['ElmLne'].items()}
cub_end = {}
for c in rows['StaCubic'].values():
    cub_end[(c['obj_id'], c['fold_id'])] = 'i' if c['obj_bus'] == '0' else 'j'
bay_rows = []
def add_bay(bay_id, station, adms, kind, name, vref):
    ct, lines = net.bay_lines(kind, name, station)
    if not lines:
        # open bay in the base (e.g. a normally-open tie): record the cable segment at its cable-side terminal anyway
        k = [x for x, y in rows['ElmCoup'].items() if y['loc_name'] == name]
        cubs = [c for c in rows['StaCubic'].values() if k and c['obj_id'] == k[0]]
        ct = next((c['fold_id'] for c in cubs if not net.tname[c['fold_id']].endswith('_BB') and not net.tname[c['fold_id']].startswith('A20_BB')), None)
        segs = [(x['loc_name'], cub_end[(lid[x['loc_name']], ct)]) for x in rows['ElmLne'].values() if (lid[x['loc_name']], ct) in cub_end] if ct else []
    else:
        segs = [(ln.get('parent', ln['name']), cub_end[(lid[ln.get('parent', ln['name'])], ct)]) for ln, s in lines]
    for seg, end in segs:
        bay_rows.append([bay_id, station, adms, kind, name, net.tname.get(ct, ''), seg, end, vref])
for st, adms, kind, name in ef.BAYS:
    add_bay(f'{st}_{adms}', st, adms, kind, name, f'{st}_BB')
# A20 feeder heads: one measuring point per circuit at its cable terminal A20_Cxx, whichever busbar bay is closed
heads = sorted({x['loc_name'][-2:] for x in rows['ElmCoup'].values() if x['loc_name'].startswith('A20_R11-') and 'coupler' not in x['loc_name']})
for feeder in heads:
    if feeder in ('01', '02', '03', '07', '12', '14', '15', '16', '17', '18', '20', '23'): continue     # transformer, spare or open circuits
    pair = f'A20_R11-1{feeder}|A20_R11-2{feeder}'
    for nm in pair.split('|'):
        before = len(bay_rows)
        add_bay(f'A20_F{feeder}', 'A20', feeder, 'ElmCoup', nm, f'A20_C{feeder}')
        if len(bay_rows) > before:
            for r in bay_rows[before:]: r[4] = pair
            break
w('bays.csv', ['bay_id', 'station', 'adms_bay', 'element_class', 'element', 'cable_side_terminal', 'cable_segment', 'segment_end_at_bay', 'v0_reference_terminal'], bay_rows)

# ---------------------------------------------------------------- shunt sizes (from shunt_sizing.csv)
shunt = {(r['busbar'], int(r['target_Ic_A'])): r for r in csv.DictReader(open(os.path.join(HERE, 'shunt_sizing.csv')))}

# ---------------------------------------------------------------- cases
RF = ef.FAULT_RES
cases = []
def add(group, earthing, cset, config, loc, rf, sk=500, cadd_bus='', cadd_target='', cadd_uF=0.0):
    cid = f"{group}|{earthing[:3]}|{cset}|{config}|{loc}|{rf}" + (f"|C{cadd_target}{cadd_bus[-1]}" if cadd_target else '') + (f"|Sk{sk}" if sk != 500 else '')
    cases.append([cid, group, earthing, VARIATION[earthing], cset, config, PF_SCEN[config], loc, rf, sk, cadd_bus, cadd_target, f'{cadd_uF:.4f}' if cadd_uF else ''])
valid = {}
for cfg in ef.CONFIGS:
    for l in ef.BB1_LOCS + ef.BB2_LOCS:
        try: ef.Net(rows, cfg, 'isolated', 'main', location=ef.location(l, rows)); valid[(cfg, l)] = True
        except KeyError: valid[(cfg, l)] = False
for earthing in ('isolated', 'earthed'):                                   # G1, G2: base study, all configurations
    for cfg in ef.CONFIGS:
        for l in ef.BB1_LOCS + ef.BB2_LOCS:
            if valid[(cfg, l)]:
                for rf in RF: add('base', earthing, 'main', cfg, l, rf)
for bus, locs in (('A20_BB2', ef.BB2_LOCS), ('A20_BB1', ef.BB1_LOCS)):  # G3, G4: I_C sweep with added shunt, split
    for tgt in ef.IC_TARGETS:
        s = shunt[(bus, tgt)]
        if not s['C_add_uF_per_phase']: continue
        for l in locs:
            for rf in RF: add('ic_sweep', 'isolated', 'main', 'split', l, rf, cadd_bus=bus, cadd_target=tgt, cadd_uF=float(s['C_add_uF_per_phase']))
for earthing, cset in (('earthed', 'xlpe_sens'), ('isolated', 'pilc_low'), ('isolated', 'xlpe_sens')):   # G5 cable sensitivities (EF-1b, EF-2b)
    for l in ef.BB1_LOCS + ef.BB2_LOCS:
        for rf in RF: add('sens_cable', earthing, cset, 'split', l, rf)
for earthing in ('earthed', 'isolated'):                                    # G6 source sensitivity (EF-1c, EF-2c)
    for l in ef.BB1_LOCS + ef.BB2_LOCS:
        for rf in RF: add('sens_source', earthing, 'main', 'split', l, rf, sk=373)
HDR = ['case_id', 'group', 'earthing', 'pf_variation', 'cable_set', 'config', 'pf_operation_scenario', 'loc', 'RF_ohm', 'Sk_MVA', 'c_add_bus', 'c_add_target_A', 'c_add_uF_per_phase']
w('cases.csv', HDR, cases)

# ---------------------------------------------------------------- GUI anchor runs (validation of offline model and script)
ANCHORS = [
    ('A1', 'base|iso|main|split|SCN15|0', 'isolated reference: solid fault at the D1026 busbar, busbar 1 section'),
    ('A2', 'base|iso|main|split|SCN15|300', 'same with R_F = 300 ohm: displacement voltage and current reduction'),
    ('A3', 'base|iso|main|split|SCN04|0', 'circuit 13 midline (busbar 2): chain of four remotely controlled stations'),
    ('A4', 'base|iso|main|coupled|SCN15|0', 'coupled busbar N-1: whole network connected'),
    ('A5', 'base|iso|main|post15|F21H|0', 'post-restoration configuration SCN-15 (D1001, D1002 fed from circuit 22)'),
    ('A6', 'ic_sweep|iso|main|split|SCN04|0|C120' + '2', 'added shunt on busbar 2 sized for 120 A: checks the shunt element'),
    ('A7', 'base|ear|main|split|SCN15|0', 'earthed variant, solid fault'),
    ('A8', 'base|ear|main|split|SCN15|30', 'earthed variant, R_F = 30 ohm'),
]
ids = {c[0] for c in cases}
for a, cid, why in ANCHORS: assert cid in ids, cid
w('anchor_runs.csv', ['anchor', 'case_id', 'purpose'], ANCHORS)
print('cases per group:', {g: sum(1 for c in cases if c[1] == g) for g in sorted({c[1] for c in cases})})
shutil.copy(ef.CABLE_CSV, os.path.join(OUT, 'ef_cable_type_values.csv'))   # read by pf_ef_script.py
shutil.copy(os.path.join(HERE, 'shunt_sizing.csv'), os.path.join(OUT, 'shunt_sizing.csv'))
