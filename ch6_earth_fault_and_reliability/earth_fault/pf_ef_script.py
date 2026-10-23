"""PowerFactory 2025 script for the earth-fault study matrix (thesis Table 3.5). Not used for the results.

Runs inside PowerFactory (Python command object, ComPython) on the benchmark model with the study
objects of the GUI run sheet (operation scenario EF_coupled_N-1, shunts EF_Cadd_BB1 / EF_Cadd_BB2 in variation
EF_variant3_Cadd). Reads the shared study tables from tables/ next to the script (or the folder TABLES names)
and writes the residual currents and zero-sequence voltages in the common format, so that compass_emulation.py and
compare_sources.py treat its output exactly like the offline sweep and the GUI anchor runs.

Order of use:
  1. MODE = 'preflight'  checks that every object named in the tables exists and that the result attributes return
                         numbers after one short-circuit run; prints what to fix. Changes nothing in the model.
  2. MODE = 'anchors'    runs the eight anchor cases only; compare with the GUI exports (compare_sources.py).
  3. MODE = 'all'        runs all 1904 cases; resumable (case_ids already in the output are skipped).
The script restores every parameter it changes (cable zero-sequence data, grid Sk'', shunts, variation and scenario
activation) in a finally block. Lines marked VERIFY carry PowerFactory names that could not be checked offline.
"""
import os, csv, math, cmath, time
import powerfactory as pf

MODE = 'preflight'
TABLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tables')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pf_script_phasors.csv')
CABLE_CSV = os.path.join(TABLES, 'ef_cable_type_values.csv')     # copy of model/parameters/ef_cable_type_values.csv

app = pf.GetApplication()
app.ClearOutputWindow()
log = app.PrintPlain

def rd(fn): return list(csv.DictReader(open(os.path.join(TABLES, fn))))

cases = rd('cases.csv'); locs = {r['loc']: r for r in rd('locations.csv')}; bays = rd('bays.csv')
anchors = {r['case_id'] for r in rd('anchor_runs.csv')}

# ------------------------------------------------------------------ objects
def one(pattern, name):
    objs = [o for o in app.GetCalcRelevantObjects(pattern) if o.loc_name == name]
    return objs[0] if objs else None

def find_all():
    missing = []
    lines = {}
    for b in bays:
        o = one('*.ElmLne', b['cable_segment']); lines[b['cable_segment']] = o
        if o is None: missing.append('line ' + b['cable_segment'])
    terms = {}
    for t in {b['v0_reference_terminal'] for b in bays} | {l['pf_object'] for l in locs.values() if l['kind'] == 'term'}:
        o = one('*.ElmTerm', t); terms[t] = o
        if o is None: missing.append('terminal ' + t)
    for l in locs.values():
        if l['kind'] == 'line' and one('*.ElmLne', l['pf_object']) is None: missing.append('fault line ' + l['pf_object'])
    scen_folder = app.GetProjectFolder('scen')
    scen = {s.loc_name: s for s in scen_folder.GetContents('*.IntScenario', 1)}
    for c in {c['pf_operation_scenario'] for c in cases}:
        if c not in scen: missing.append('operation scenario ' + c)
    var_folder = app.GetProjectFolder('scheme')
    var = {v.loc_name: v for v in var_folder.GetContents('*.IntScheme', 1)}
    for v in ('EF_variant1_earthed', 'EF_variant2_isolated', 'EF_variant3_Cadd'):
        if v not in var: missing.append('variation ' + v)
    return lines, terms, scen, var, missing

# ------------------------------------------------------------------ parameter changes (restored at the end)
cab = {r['type']: r for r in csv.DictReader(open(CABLE_CSV))} if os.path.exists(CABLE_CSV) else {}
SET_COLS = {'main': ('r0_main', 'x0_main', 'b0_main_uSkm'), 'sens': ('r0_sens', 'x0_sens', 'b0_sens_uSkm'), 'now': ('r0_now', 'x0_now', 'b0_now')}
CABLE_SETS = {'main': {'XLPE': 'main', 'PILC': 'main'}, 'xlpe_sens': {'XLPE': 'sens', 'PILC': 'main'},
              'pilc_low': {'XLPE': 'main', 'PILC': 'sens'}, 'catalog': {'XLPE': 'now', 'PILC': 'now'}}
saved = {}          # full name -> (object, original values)

def set_cable(set_name):
    for t in app.GetCalcRelevantObjects('*.TypLne'):
        if t.loc_name not in cab: continue
        if t.GetFullName() not in saved: saved[t.GetFullName()] = (t, (t.rline0, t.xline0, t.bline0))   # VERIFY: TypLne zero-sequence fields
        c = cab[t.loc_name]; cols = SET_COLS[CABLE_SETS[set_name][c['set']]]
        t.rline0, t.xline0, t.bline0 = float(c[cols[0]]), float(c[cols[1]]), float(c[cols[2]])

def set_sk(sk):
    g = one('*.ElmXnet', 'Landsnet_66kV')
    if g.GetFullName() not in saved: saved[g.GetFullName()] = (g, (g.snss,))
    g.snss = float(sk)

def set_shunt(bus, uF):
    for nm in ('EF_Cadd_BB1', 'EF_Cadd_BB2'):
        s = one('*.ElmShnt', nm)
        if s is None: continue
        if s.GetFullName() not in saved: saved[s.GetFullName()] = (s, (s.outserv,))
        on = bool(uF) and nm.endswith(bus[-3:])
        s.outserv = 0 if on else 1
        if on:
            s.qcapn = 2 * math.pi * 50 * float(uF) * 1e-6 * 11.0 ** 2       # Mvar at 11 kV; VERIFY: ElmShnt C-type rated Q field (alternatively s.ccap in uF)

def restore():
    for o, v in saved.values():
        if o.GetClassName() == 'TypLne': o.rline0, o.xline0, o.bline0 = v
        elif o.GetClassName() == 'ElmXnet': o.snss = v[0]
        elif o.GetClassName() == 'ElmShnt': o.outserv = v[0]

# ------------------------------------------------------------------ short-circuit command
shc = app.GetFromStudyCase('ComShc')
def setup_shc():
    shc.iopt_mde = 3        # complete method (superposition), VERIFY enumeration value in PF 2025
    shc.iopt_shc = 'spgf'   # single phase to ground
    shc.iopt_allbus = 0     # user-selected fault location
    shc.i_pspgf = 0         # faulted phase L1 (A)                                   VERIFY attribute name
    shc.iopt_lflow = 1      # initialise from load flow (pre-fault state retained)   VERIFY attribute name
    shc.Xf = 0.0

def set_location(loc):
    if loc['kind'] == 'term':
        shc.shcobj = one('*.ElmTerm', loc['pf_object'])
    else:
        shc.shcobj = one('*.ElmLne', loc['pf_object'])
        shc.ppro = float(loc['fraction_from_terminal_i']) * 100.0   # fault position on the line, % from terminal i; VERIFY

# ------------------------------------------------------------------ results
def phasor(obj, mag, ang, scale=1.0):
    m = obj.GetAttribute(mag); a = obj.GetAttribute(ang)       # VERIFY names, see preflight
    return None if m is None or a is None else m * scale * cmath.exp(1j * math.radians(a))

def bay_rows(case_id, lines, terms):
    out = []; acc = {}
    for b in bays:
        ln = lines.get(b['cable_segment'])
        if ln is None or ln.outserv: continue
        bus = 'bus1' if b['segment_end_at_bay'] == 'i' else 'bus2'
        I = 0j
        for p in 'ABC':
            x = phasor(ln, f'm:I:{bus}:{p}', f'm:phii:{bus}:{p}', 1000.0)   # kA -> A
            if x is None: I = None; break
            I += x
        if I is None: continue
        acc[b['bay_id']] = (b, acc.get(b['bay_id'], (b, 0j))[1] + I)
    for bid, (b, I) in acc.items():
        t = terms[b['v0_reference_terminal']]
        V = 0j
        for p in 'ABC':
            x = phasor(t, f'm:U:{p}', f'm:phiu:{p}')                       # line-ground kV
            if x is None: V = None; break
            V += x
        if V is None: continue
        V /= 3
        out.append([case_id, 'pf_script', bid, b['station'], f'{abs(I):.5f}', f'{math.degrees(cmath.phase(I)):.3f}',
                    f'{abs(V):.6f}', f'{math.degrees(cmath.phase(V)):.3f}', f'{11.15 / math.sqrt(3):.5f}', ''])
    return out

# ------------------------------------------------------------------ main
lines, terms, scen, var, missing = find_all()
if missing:
    log('MISSING OBJECTS (fix before running):'); [log('  ' + m) for m in missing]
    if MODE != 'preflight': raise SystemExit
setup_shc()
done = set()
if os.path.exists(OUT):
    done = {r['case_id'] for r in csv.DictReader(open(OUT))}
todo = [c for c in cases if (MODE != 'anchors' or c['case_id'] in anchors) and c['case_id'] not in done]
if MODE == 'preflight': todo = [c for c in cases if c['case_id'] == 'base|iso|main|split|SCN15|0']
new = not os.path.exists(OUT)
fh = open(OUT, 'a', newline=''); w = csv.writer(fh)
if new: w.writerow(['case_id', 'source', 'bay_id', 'station', 'I0x3_A', 'ang_I0x3_deg', 'V0_kV', 'ang_V0_deg', 'E_kV', 'expected'])
state = None; t0 = time.time()
try:
    for k, c in enumerate(todo):
        key = (c['earthing'], c['cable_set'], c['pf_operation_scenario'], c['Sk_MVA'], c['c_add_bus'], c['c_add_uF_per_phase'])
        if key != state:
            if c['earthing'] == 'isolated': var['EF_variant2_isolated'].Activate()
            else: var['EF_variant2_isolated'].Deactivate()
            if c['c_add_uF_per_phase']: var['EF_variant3_Cadd'].Activate()
            else: var['EF_variant3_Cadd'].Deactivate()
            scen[c['pf_operation_scenario']].Activate()
            set_cable(c['cable_set']); set_sk(c['Sk_MVA']); set_shunt(c['c_add_bus'] or 'BB1', c['c_add_uF_per_phase'])
            state = key
        set_location(locs[c['loc']]); shc.Rf = float(c['RF_ohm'])
        if shc.Execute() != 0:
            log(f"FAILED {c['case_id']}"); continue
        rows = bay_rows(c['case_id'], lines, terms)
        if MODE == 'preflight':
            b = bays[0]; ln = lines[b['cable_segment']]; t = terms[b['v0_reference_terminal']]
            for a in ('m:I:bus1:A', 'm:phii:bus1:A', 'm:I:bus2:A', 'm:phii:bus2:A'): log(f'{ln.loc_name} {a} = {ln.GetAttribute(a)}')
            for a in ('m:U:A', 'm:phiu:A', 'm:u:A'): log(f'{t.loc_name} {a} = {t.GetAttribute(a)}')
            log(f'preflight: {len(rows)} bay rows from the first case (expected about 33); expected I0x3 at D1026_101 about 56.6 A')
            for r in rows: log('  ' + ' '.join(r[2:8]))
        w.writerows(rows); fh.flush()
        if k % 25 == 0: log(f"{k + 1}/{len(todo)} {c['case_id']} {time.time() - t0:.0f} s")
finally:
    fh.close(); restore()
    var['EF_variant2_isolated'].Deactivate(); var['EF_variant3_Cadd'].Deactivate()
    scen['winter_peak_boiler_off'].Activate()
    log('parameters restored; base scenario re-activated')
