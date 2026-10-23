"""Compare two phasor tables in the common format, case by case and bay by bay.
Typical use: PowerFactory anchor runs against the offline model, or the PowerFactory script against the GUI runs.

Usage: compare_sources.py <reference.csv> <test.csv> [out.csv]
Reports per bay the residual current magnitude ratio, the angle difference of 3 I0 relative to -V0 (the quantity the
ComPass decides on) and the V0 magnitude ratio; summary per case. Agreement targets for accepting the offline sweep:
|3I0| within 5 % (or 0.2 A for currents below 4 A), angle relative to -V0 within 2 deg, |V0| within 2 % (or 0.02 kV,
0.3 % of the phase voltage, far below the ComPass displacement thresholds of 10 to 30 %; it covers the earthed
anchors, where V0 away from the fault is a few tens of volts).
"""
import sys, csv, math, collections

def load(fn):
    d = {}
    for r in csv.DictReader(open(fn)): d[(r['case_id'], r['bay_id'])] = r
    return d

def rel_angle(r):
    return float(r['ang_I0x3_deg']) - (float(r['ang_V0_deg']) + 180.0)

def main(ref_fn, test_fn, out=None):
    ref, tst = load(ref_fn), load(test_fn)
    keys = sorted(set(ref) & set(tst))
    rows = []; bad = collections.Counter(); tot = collections.Counter()
    for k in keys:
        a, b = ref[k], tst[k]
        Ia, Ib = float(a['I0x3_A']), float(b['I0x3_A']); Va, Vb = float(a['V0_kV']), float(b['V0_kV'])
        dphi = (rel_angle(b) - rel_angle(a) + 180) % 360 - 180 if min(Ia, Ib) > 0.05 else 0.0
        okI = abs(Ib - Ia) <= max(0.05 * Ia, 0.2); okA = abs(dphi) <= 2.0 or min(Ia, Ib) < 0.2
        okV = abs(Vb - Va) <= max(0.02 * Va, 0.02)
        tot[k[0]] += 1; bad[k[0]] += not (okI and okA and okV)
        rows.append([k[0], k[1], f'{Ia:.3f}', f'{Ib:.3f}', f'{dphi:.2f}', f'{Va:.4f}', f'{Vb:.4f}', 'ok' if okI and okA and okV else 'CHECK'])
    for c in sorted(tot): print(f'{c}: {tot[c] - bad[c]}/{tot[c]} bays within the agreement targets')
    print(f'cases compared: {len(tot)}; bays missing in test: {len(set(ref) - set(tst))}; extra in test: {len(set(tst) - set(ref))}')
    if out:
        with open(out, 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['case_id', 'bay_id', 'I0x3_ref_A', 'I0x3_test_A', 'dphi_deg', 'V0_ref_kV', 'V0_test_kV', 'status']); w.writerows(rows)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
