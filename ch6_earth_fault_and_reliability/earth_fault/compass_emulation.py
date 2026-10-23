"""ComPass sin(phi) direction logic under sampled measurement errors (thesis Section 3.6.3, Eq. 3.x and Table
tab:ef_errors), applied to a phasor table in the common format (offline, GUI or script).

Decision per sample (V0 referred to the nominal phase-to-earth voltage E_n = 11 kV / sqrt 3, the assumed reference
of the ComPass V_NEQ percentage; the manual does not state it):
    |V0| / E_n > V_NEQ  and  |3I0| sin(phi) > +I_EQ   ->  Direction B (fault in the direction of the cable)
    |V0| / E_n > V_NEQ  and  |3I0| sin(phi) < -I_EQ   ->  Direction A
    otherwise                                          ->  none
with phi the angle of 3I0 referred to -V0. Errors, uniform: residual current +/-3 % or +/-0.1 A whichever larger;
displacement voltage +/-10 % (standard calibration) or +/-1 % (reference calibration); angle +/-5 deg; standing
displacement voltage of up to 2 % of E_n with random phase (capacitance unbalance). 1000 samples per case and bay.

Usage: compass_emulation.py <phasors.csv> <out.csv.gz>
Output: one row per case, bay and calibration with, for every (V_NEQ, I_EQ) pair, the probabilities of a B and an A
indication; 'correct' is B where B is expected, A where A is expected, no indication where none is expected.
"""
import sys, csv, gzip, math
import numpy as np

V_NEQ = [0.10, 0.20, 0.30]
I_EQ = [1, 2, 3, 5, 8, 10, 15, 20]
CAL = {'standard': 0.10, 'reference': 0.01}
N = 1000
E_N = 11.0 / math.sqrt(3)

def emulate(rows, seed=20261022):
    rng = np.random.default_rng(seed)
    I = np.array([float(r['I0x3_A']) for r in rows]); aI = np.radians([float(r['ang_I0x3_deg']) for r in rows])
    V = np.array([float(r['V0_kV']) for r in rows]); aV = np.radians([float(r['ang_V0_deg']) for r in rows])
    n = len(rows); out = {}
    for cal, ev in CAL.items():
        eI = rng.uniform(-1, 1, (n, N)) * np.maximum(0.03 * I, 0.1)[:, None]
        Im = np.abs(I[:, None] + eI)
        aIm = aI[:, None] + np.radians(rng.uniform(-5, 5, (n, N)))
        Vm = V[:, None] * (1 + rng.uniform(-ev, ev, (n, N))) * np.exp(1j * aV[:, None]) \
             + rng.uniform(0, 0.02, (n, N)) * E_N * np.exp(1j * rng.uniform(0, 2 * np.pi, (n, N)))
        phi = aIm - np.angle(-Vm)
        Iq = Im * np.sin(phi)
        vf = np.abs(Vm) / E_N
        res = {}
        for v in V_NEQ:
            on = vf > v
            for i in I_EQ:
                res[(v, i)] = ((on & (Iq > i)).mean(1), (on & (Iq < -i)).mean(1))
        out[cal] = res
    return out

def main(src, dst, chunk=4000):
    rows = [r for r in csv.DictReader(open(src)) if r['expected'] in ('A', 'B', 'none')]
    hdr = ['case_id', 'source', 'bay_id', 'station', 'expected', 'I0x3_A', 'V0_over_En', 'calibration']
    for v in V_NEQ:
        for i in I_EQ: hdr += [f'pB_v{int(v*100)}_i{i}', f'pA_v{int(v*100)}_i{i}']
    with gzip.open(dst, 'wt', newline='') as fh:
        w = csv.writer(fh); w.writerow(hdr)
        for s in range(0, len(rows), chunk):
            part = rows[s:s + chunk]; res = emulate(part, seed=20261022 + s)
            for cal in CAL:
                for k, r in enumerate(part):
                    line = [r['case_id'], r['source'], r['bay_id'], r['station'], r['expected'], r['I0x3_A'],
                            f"{float(r['V0_kV']) / E_N:.4f}", cal]
                    for v in V_NEQ:
                        for i in I_EQ:
                            pB, pA = res[cal][(v, i)]; line += [f'{pB[k]:.3f}', f'{pA[k]:.3f}']
                    w.writerow(line)
            print(f'{min(s + chunk, len(rows))}/{len(rows)}', flush=True)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
