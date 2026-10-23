"""Input and output locations of the Chapter 5 scripts, relative to the chapter folder.

data(name) finds an input by file name under output/ (results of an earlier script), data/ and model/; the names are
unique. out(name) is the path of a result; every script writes into output/ only, so the files of record in data/,
model/ and ../thesis_figures/ch5/ stay as published and can be compared with a rerun."""
import os, glob
CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(CH, 'output')
EXPORTS = os.path.join(CH, 'data', 'pf_exports')
# per-bay ComPass measurements: not part of the supplement (station-level aggregates only), available from the author
WITHHELD = ('holdout_measured.json', 'holdout_measured_vs_sweep.csv', 'alloc_wpbo.json', 'alloc_wnm.json')

def data(name):
    for d in (OUT, os.path.join(CH, 'data'), os.path.join(CH, 'model')):
        hits = glob.glob(os.path.join(d, '**', name), recursive=True)
        if hits: return hits[0]
    if name in WITHHELD:
        raise SystemExit(f'{name}: per-bay measurement input, not included in the supplement (available from the author)')
    raise SystemExit(f'{name}: not found under output/, data/ or model/')

def out(name):
    p = os.path.join(OUT, name); os.makedirs(os.path.dirname(p), exist_ok=True)
    return p
