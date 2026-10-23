"""Rerun the analyses and figures of the supplement in thesis order.

    python3 reproduce.py                 all chapters
    python3 reproduce.py ch5 ch6         selected parts (ch4, ch5, ch6, figs)

Every script writes into the output/ folder of its part, so the files of record in data/, results/ and thesis_figures/ stay
as published; at the end the rerun is compared with them. Exceptions: the earth-fault package writes its tables/ and
results/ (with results/ch6/) in place (deterministic, fixed seeds). Steps that need inputs outside the supplement (per-bay ComPass
measurements, the START report PDFs, the PowerFactory GUI) are listed and skipped.
"""
import os, sys, csv, json, subprocess, time, filecmp

ROOT = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ, MATPLOTLIBRC=os.path.join(ROOT, 'matplotlibrc'), PYTHONDONTWRITEBYTECODE='1',
           EF_FIG_DIR=os.path.join(ROOT, 'ch6_earth_fault_and_reliability', 'output'))
C4, C5, C6, TF = (os.path.join(ROOT, d) for d in ('ch4_data_audit', 'ch5_powerfactory_benchmark',
                                                   'ch6_earth_fault_and_reliability', 'thesis_figures'))
S5 = os.path.join(C5, 'scripts'); EF = os.path.join(C6, 'earth_fault'); RL = os.path.join(C6, 'reliability')
SNAPSHOTS = ('winter_peak_boiler_off', 'winter_night_min', 'summer_peak', 'summer_night_min')

STEPS = {
    'ch4': [(os.path.join(C4, 'scripts'), ['dpa_coverage_fig.py']),
            (os.path.join(C4, 'scripts'), ['dpa_timeline_fig.py']),
            (os.path.join(C4, 'scripts'), ['a20_station_figs.py'])],
    'ch5': [(S5, ['snapshot_alloc.py', s]) for s in SNAPSHOTS] + [
            (S5, ['open_rings.py']),
            (S5, ['restoration_sweep.py']),
            (S5, ['restoration_results_table.py']),
            (S5, ['defect_expect.py']),
            (S5, ['pf_adms_layout.py']),
            (S5, ['pf_voltage_profile_fig.py']),
            (S5, ['pf_constraints_fig.py'])],
    'ch6': [(EF, ['build_cases.py']),
            (EF, ['run_offline.py']),
            (EF, ['compass_emulation.py', 'results/offline_phasors.csv', 'results/offline_emulation.csv.gz']),
            (EF, ['analysis_selectivity.py']),
            (EF, ['parse_pf_exports.py', 'anchors', 'results/pf_gui_phasors.csv', 'pf_gui']),
            (EF, ['compare_sources.py', 'results/offline_phasors.csv', 'results/pf_gui_phasors.csv',
                  'results/compare_gui_offline.csv']),
            (EF, ['ch6_results.py']),
            (EF, ['ch6_figures.py']),
            (EF, ['ef_3ct.py']),
            (EF, ['ch6_figures_3ct.py']),
            (os.path.join(RL, 'scripts'), ['record_indices.py']),
            (os.path.join(RL, 'scripts'), ['mc_reliability.py']),
            (os.path.join(RL, 'scripts'), ['mc_reliability_bars.py']),
            (os.path.join(RL, 'scripts', 'start'), ['build_series.py', '../../data/start_reykjavik_rows_raw.csv'],
             os.path.join(RL, 'output', 'start_veitur_series_1996-2024.csv')),
            (os.path.join(RL, 'scripts', 'start'), ['start_series_fig.py', '../../output/start_veitur_series_1996-2024.csv',
                                                     '../../output/start_veitur_indices_1996-2024'])],
    'figs': [(os.path.join(TF, 'scripts'), ['glover_tx.py']),
             (os.path.join(TF, 'scripts'), ['glover_slg.py']),
             (os.path.join(TF, 'scripts'), ['ch3_method_diagrams.py']),
             (os.path.join(TF, 'scripts'), ['ef_pipeline_fig.py']),
             (os.path.join(TF, 'scripts'), ['ch2_impedance_protocol_figs.py']),
             (os.path.join(TF, 'scripts'), ['ch2_figures.py']),
             (os.path.join(TF, 'scripts'), ['ch2_linear_fpi.py']),
             (os.path.join(TF, 'scripts'), ['ch2_adms_pipeline.py'])],
}
NOT_RUN = [
    ('ch5', 'holdout_build.py, holdout_pf.py, holdout_validation.py, sensitivity.py, pf_validation_scatter.py',
     'need the per-bay ComPass measurements (station-level results are in data/validation/)'),
    ('ch5', 'PowerFactory runs', 'procedures/ and model/; exports of record in data/pf_exports/'),
    ('ch6', 'earth_fault/pf_ef_script.py', 'PowerFactory script, not used for the results (the anchors were run in the GUI)'),
    ('ch6', 'reliability/scripts/start/parse_start.py', 'needs the START report PDFs (public, cited in the thesis)'),
    ('figs', 'thesis_figures/scripts/ch2_figures.py, Figure 2.23', 'needs the national energy forecast workbook (cited in the thesis), '
     'path in ORKUSPA_XLSX; Figure 2.5 needs networkx'),
]
# (rerun output, file of record): compared after the run
CHECKS = [(os.path.join(C5, 'output', f'scenario_{s}_loads.csv'), os.path.join(C5, 'data', 'allocation', f'scenario_{s}_loads.csv')) for s in SNAPSHOTS] + [
    (os.path.join(C5, 'output', f'tuning_{s}.csv'), os.path.join(C5, 'data', 'allocation', f'tuning_{s}.csv')) for s in SNAPSHOTS] + [
    (os.path.join(C5, 'output', f'open_rings_{n}.csv'), os.path.join(C5, 'data', 'snapshots', f'open_rings_{n}.csv')) for n in ('stations', 'open_points')] + [
    (os.path.join(C5, 'output', 'restoration_pf_results.json'), os.path.join(C5, 'data', 'scenarios', 'restoration_pf_results.json')),
    (os.path.join(RL, 'output', 'record_indices.csv'), os.path.join(RL, 'results', 'record_indices.csv')),
    (os.path.join(RL, 'output', 'mc_reliability_results.json'), os.path.join(RL, 'results', 'mc_reliability_results.json')),
    (os.path.join(RL, 'output', 'start_veitur_series_1996-2024.csv'), os.path.join(RL, 'data', 'start_veitur_series_1996-2024.csv'))]
# files the earth-fault package rewrites in place: compared with a copy taken before the run
IN_PLACE = [os.path.join(EF, 'results', f) for f in ('offline_cases.csv', 'selectivity.csv', 'pf_gui_phasors.csv', 'compare_gui_offline.csv')] + [
    os.path.join(EF, 'results', 'ch6', f) for f in ('ic_results.csv', 'feeder_charging.csv', 'v0_coverage.csv', 'v0_rf_limits.csv',
    'fpi_signatures.csv', 'fpi_phasors_scn04.csv', 'fpi_phasors_scn04_120A.csv', 'direction_probability.csv', 'coverage_rf.csv',
    'path_probability_rf.csv', 'windows.csv', 'zones.csv', 'zones_by_feeder.csv')] + [
    os.path.join(EF, 'results', 'ch6', f'{n}_3ct.csv') for n in ('direction_probability', 'path_probability_rf', 'coverage_rf',
    'windows', 'summary', 'ies_check', 'bay_loads')]


def same_numbers(a, b, tol=1e-6):
    """True if two CSV or JSON files hold the same values (numbers within tol, text identical)."""
    def load(p):
        if p.endswith('.json'): return json.load(open(p))
        return list(csv.reader(open(p, encoding='utf-8')))
    def eq(x, y):
        if isinstance(x, dict) and isinstance(y, dict): return x.keys() == y.keys() and all(eq(x[k], y[k]) for k in x)
        if isinstance(x, list) and isinstance(y, list): return len(x) == len(y) and all(eq(u, v) for u, v in zip(x, y))
        try: return abs(float(x) - float(y)) <= tol * max(1.0, abs(float(y)))
        except (TypeError, ValueError): return x == y
    return eq(load(a), load(b))


def main(parts):
    t0 = time.time(); failed = []
    before = {p: open(p, 'rb').read() for p in IN_PLACE if os.path.exists(p)}
    for part in parts:
        for step in STEPS[part]:
            cwd, args = step[0], step[1]
            print(f'[{part}] {os.path.relpath(cwd, ROOT)}: {" ".join(args)}', flush=True)
            stdout = None
            if len(step) > 2: os.makedirs(os.path.dirname(step[2]), exist_ok=True); stdout = open(step[2], 'w')
            r = subprocess.run([sys.executable] + args, cwd=cwd, env=ENV, stdout=stdout or subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if r.returncode: failed.append(' '.join(args)); print(r.stderr[-1500:])
    print(f'\nfinished in {time.time() - t0:.0f} s, {len(failed)} step(s) failed' + (': ' + '; '.join(failed) if failed else ''))
    print('\nnot run here:')
    for part, what, why in NOT_RUN:
        if part in parts: print(f'  [{part}] {what}: {why}')
    print('\ncomparison with the files of record:')
    if failed: print('  (steps failed above: their outputs were not rewritten, so a "same" below can be a stale file)')
    for a, b in CHECKS:
        if not os.path.exists(a): continue
        ok = filecmp.cmp(a, b, shallow=False) or same_numbers(a, b)
        print(f'  {"same     " if ok else "DIFFERENT"} {os.path.relpath(a, ROOT)}')
    for p, b in before.items():
        ok = open(p, 'rb').read() == b
        print(f'  {"same     " if ok else "DIFFERENT"} {os.path.relpath(p, ROOT)} (rewritten in place)')
    return 1 if failed else 0


if __name__ == '__main__':
    parts = [p for p in sys.argv[1:] if p in STEPS] or list(STEPS)
    sys.exit(main(parts))
