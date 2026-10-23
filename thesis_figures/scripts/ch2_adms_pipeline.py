"""Figure 2.22 (adms_flowchart): the ADMS data pipeline as described in Section 2.6.3 of the thesis,
after the GE Vernova PowerOn documentation cited there.
  inputs     SCADA telemetry, fault indicators (ComPass), ADMS network data model
  chain      load allocation -> Distribution Power Flow (DPF)
  APRS       fault verification -> fault location -> fault switching
  output     Switching Advisor
Data links blue; the full-DPF link blue; the basic APRS level (feeder-head currents and ratings, no DPF) dashed grey.
House style: Liberation Sans, text printed at 6.6 to 7.5 pt at the text width, boxes grey with black text.
Output: ../output/adms_flowchart.{pdf,png}.
Run: MATPLOTLIBRC=../../matplotlibrc python3 ch2_adms_pipeline.py"""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
INK, MUTED, BLUE, F_BOX = '#0b0b0b', '#52514e', '#2a78d6', '#f3f2ef'
plt.rcParams.update({'font.family': 'Liberation Sans', 'pdf.fonttype': 42, 'text.color': INK})
FT, FS, LS = 8, 7, 1.2                                   # title and sub-line sizes (pt) and line spacing

W, H = 6.27, 3.75                                        # inches; data units are inches
fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

def box(cx, cy, w, h, title, sub, fc=F_BOX):
    """Box with a bold title and regular sub-lines on a fixed baseline grid, centred as a block."""
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.05',
                                fc=fc, ec=MUTED, lw=0.8, zorder=2))
    rows = [(l, FT, 'bold') for l in title.split('\n')] + [(l, FS, 'normal') for l in sub.split('\n')]
    pitch = [LS * size / 72 for _, size, _ in rows]; pitch[len(title.split('\n'))] += 0.03   # small gap under the title
    span = sum(pitch[1:]) + 0.72 * FT / 72                  # first cap height to the last baseline
    base = cy + span / 2 - 0.72 * FT / 72
    for i, (line, size, weight) in enumerate(rows):         # fixed baseline grid: even gaps whatever the letters
        if i: base -= pitch[i]
        ax.text(cx, base, line, ha='center', va='baseline', fontsize=size, fontweight=weight, zorder=3)
    return dict(l=cx - w / 2, r=cx + w / 2, t=cy + h / 2, b=cy - h / 2, x=cx, y=cy)

def route(pts, col=BLUE, dashed=False, lw=0.9):
    """Orthogonal connector through pts with an arrowhead on the last segment."""
    ls = (0, (4, 2.5)) if dashed else '-'
    for a, b in zip(pts[:-2], pts[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=lw, ls=ls, solid_capstyle='projecting', zorder=1)
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle='-|>', mutation_scale=9, lw=lw, color=col,
                                 ls=ls, shrinkA=0, shrinkB=0, zorder=1))

def note(x, y, s, ha='center', va='bottom', col=MUTED):
    ax.text(x, y, s, ha=ha, va=va, fontsize=FS, color=col, linespacing=LS, zorder=3)

# inputs (left column)
C1, W1 = 0.72, 1.34
scada = box(C1, 3.1, W1, 0.7, 'SCADA telemetry', 'feeder-head and in-line\ncurrents, voltages,\nswitch status')
fi = box(C1, 2.15, W1, 0.66, 'Fault indicators\n(ComPass)', 'Direction A/B mapped\nto Set/Clear')
adms = box(C1, 0.95, W1, 0.75, 'ADMS network\ndata model', 'topology, catalog codes,\nratings, load models')
# power-flow chain (middle)
C2, W2 = 2.38, 1.2
la = box(C2, 1.4, W2, 0.55, 'Load allocation', 'scales load models\nto SCADA currents')
dpf = box(C2, 0.5, W2, 0.72, 'Distribution Power\nFlow (DPF)', 'unbalanced load flow:\ncalculated loads\nand voltages')
# APRS with its three stages
AL, AR, AB, AT = 3.45, 5.1, 0.22, 3.62
ax.add_patch(FancyBboxPatch((AL, AB), AR - AL, AT - AB, boxstyle='round,pad=0,rounding_size=0.06', fc='white',
                            ec=MUTED, lw=0.8, zorder=0))
ax.text((AL + AR) / 2, AT - 0.08, 'APRS', ha='center', va='top', fontsize=FT, fontweight='bold')
C3, W3 = (AL + AR) / 2, 1.45
ver = box(C3, 3.0, W3, 0.5, 'Fault verification', 'trace from the tripped\ndevice, checks')
loc = box(C3, 2.15, W3, 0.5, 'Fault location', 'first connection after\nthe last Set indicator')
sw = box(C3, 0.72, W3, 0.6, 'Fault switching', 'isolation; upstream and\ndonor restoration')
for a, b in ((ver, loc), (loc, sw)): route([(C3, a['b']), (C3, b['t'])], col=MUTED)
# output (right)
sa = box(5.75, 2.15, 0.9, 0.72, 'Switching\nAdvisor', 'ranked donors,\nrestoration plan\nfor the operator')

# links
route([(scada['r'], 3.1), (AL, 3.1)])                                       # switch status, topology to APRS
note((scada['r'] + AL) / 2, 3.14, 'switch status, topology')
route([(scada['r'], 2.82), (1.56, 2.82), (1.56, 1.5), (la['l'], 1.5)])     # currents to load allocation
note(1.61, 1.85, 'currents', ha='left', va='center')
route([(scada['r'], 2.94), (3.2, 2.94), (3.2, 0.92), (sw['l'], 0.92)], col=MUTED, dashed=True)   # basic level
note(2.42, 2.88, 'basic level: feeder-head\ncurrents and ratings', va='top')
route([(fi['r'], 2.15), (loc['l'], 2.15)])                                  # Set/Clear to fault location
route([(adms['r'], 1.25), (la['l'], 1.25)])                                 # data model to load allocation
route([(adms['r'], 0.72), (dpf['l'], 0.72)])                                # data model to DPF
route([(C2, la['b']), (C2, dpf['t'])])                                      # allocated loads to DPF
route([(C1, adms['b']), (C1, 0.06), (3.62, 0.06), (3.62, AB)])              # topology to APRS
note(3.57, 0.08, 'topology', ha='right')
route([(dpf['r'], 0.6), (sw['l'], 0.6)])                                    # full DPF to fault switching
note((dpf['r'] + AL) / 2, 0.63, 'full DPF', col=BLUE)
route([(AR, 2.15), (sa['l'], 2.15)])                                        # APRS results to the Switching Advisor

for e in ('pdf', 'png'): fig.savefig(os.path.join(OUT, f'adms_flowchart.{e}'), dpi=300 if e == 'png' else None)
print('written to', os.path.abspath(OUT))
