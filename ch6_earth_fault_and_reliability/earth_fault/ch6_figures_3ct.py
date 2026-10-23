"""Figure direction_probability_3ct (thesis Figure 6.4): the direction probability of Figure 6.3 with the
residual current from three phase sensors (3CT, solid) beside the first run with a fixed residual error (+/-3 % or
0.1 A, dashed), from results/ch6/*_3ct.csv (ef_3ct.py). (a) lowest P(Direction B) at the on-path bays, R_F <= 30 ohm; 3CT with split-core
sensors (1 %), phase-angle error +/-1 deg, median measured unbalance, Akranes systems at winter peak and systems with
added capacitance at a uniform bay load of 300 A. (b) highest probability of a false or opposite indication at an
off-path ComPass bay over the 120 and 200 A systems, per bay load, at +/-1 and +/-2 deg. Standard calibration, 20 %.
Output: PDF and PNG in ../../thesis_figures/ch6, or in the folder EF_FIG_DIR names."""
import os, csv
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'results', 'ch6')
FIG = os.environ.get('EF_FIG_DIR') or os.path.join(os.path.dirname(os.path.dirname(HERE)), 'thesis_figures', 'ch6'); os.makedirs(FIG, exist_ok=True)
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
RAMP = ['#86b6ef', '#5598e7', '#3987e5', '#256abf', '#184f95', '#0d366b']
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8.5, 'pdf.fonttype': 42, 'text.color': INK,
                     'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans', 'mathtext.it': 'Liberation Sans:italic', 'mathtext.bf': 'Liberation Sans:bold',
                     'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6})
W = 6.27
SYS = [('bb2', '21 A', 'busbar 2', 'winter_peak'), ('bb1', '61 A', 'busbar 1', 'winter_peak'),
       ('coupled', '83 A', 'coupled', 'winter_peak'), ('bb2_120', '120 A', 'busbar 2 + shunt', '300'),
       ('bb2_200', '200 A', 'busbar 2 + shunt', '300')]
COLS = [RAMP[0], RAMP[1], RAMP[3], RAMP[4], RAMP[5]]
CT3 = ('3CT', 'split-core 1 %', '1', 'median')
IE = [5, 10, 15, 20, 30]; RFS = [0, 10, 30, 100, 300, 1000, 3000]

def rd(name): return list(csv.DictReader(open(os.path.join(R, name))))
dp = rd('direction_probability_3ct.csv'); pr = rd('path_probability_rf_3ct.csv')
def sel(rows, key, model, level, **kw):
    out = []
    for r in rows:
        if r['system'] != key or r['calibration'] != 'standard' or r['V_NEQ_pct'] != '20': continue
        if model == 'SumCT' and r['error_model'] != 'SumCT': continue
        if model == '3CT' and (r['error_model'], r['phase_sensor'], r['theta_deg'], r['unbalance'], r['load_level']) != CT3 + (level,): continue
        if all(r[k] == str(v) for k, v in kw.items()): out.append(r)
    return out

def style(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.grid(color=GRID, lw=0.5); ax.set_axisbelow(True)

fig, axes = plt.subplots(1, 2, figsize=(W, 3.1), gridspec_kw=dict(wspace=0.3))
for ax in axes: style(ax)
# (a) on-path detection against the pickup
for (key, ic, lab, level), col in zip(SYS, COLS):
    for model, ls, mfc in (('SumCT', (0, (3, 2)), 'white'), ('3CT', '-', col)):
        y = [float(sel(dp, key, model, level, I_EQ_A=i)[0]['min_P_B_path_RF_le_30']) for i in IE]
        axes[0].plot(range(len(IE)), y, ls=ls, marker='o', color=col, lw=1.5 if model == '3CT' else 1.1, ms=3.6,
                     mfc=mfc, mec=col, mew=0.9)
axes[0].axhline(0.99, color=MUTED, lw=0.7, ls=(0, (1, 2)))
axes[0].text(len(IE) - 1.02, 0.975, '99 %', fontsize=7, color=MUTED, ha='right', va='top')
axes[0].set_ylim(-0.03, 1.06)
axes[0].set_ylabel('Lowest probability of Direction B\nat the bays facing the fault')
axes[0].set_title('(a) on the fault path, $R_{\\mathrm{F}} \\leq$ 30 $\\Omega$', fontsize=8.5, loc='left')
# (b) false or opposite indications off the path, systems of 120 and 200 A, per bay load
CAP = ('bb2_120', 'bb2_200', 'bb1_120', 'bb1_200'); LOADS = [('150', RAMP[1]), ('300', RAMP[3]), ('450', RAMP[5])]
for load, col in LOADS:
    for theta, ls in (('1', '-'), ('2', (0, (3, 2)))):
        y = []
        for i in IE:
            y.append(max(float(r['max_P_opposite_or_false_offpath']) for r in dp if r['system'] in CAP and r['calibration'] == 'standard'
                         and r['V_NEQ_pct'] == '20' and r['I_EQ_A'] == str(i) and r['error_model'] == '3CT'
                         and r['phase_sensor'] == 'split-core 1 %' and r['theta_deg'] == theta and r['unbalance'] == 'median'
                         and r['load_level'] == load))
        ymax_b = max(globals().get('ymax_b', 0), 100 * max(y))
        axes[1].plot(range(len(IE)), [100 * v for v in y], ls=ls, marker='o', color=col, lw=1.5 if theta == '1' else 1.1, ms=3.6,
                     mfc=col if theta == '1' else 'white', mec=col, mew=0.9)
axes[1].axhline(1, color=MUTED, lw=0.7, ls=(0, (1, 2)))
axes[1].text(len(IE) - 0.9, 1, '1 %', fontsize=7, color=MUTED, ha='left', va='center', clip_on=False)
axes[1].set_ylim(-1, ymax_b * 1.05)
axes[1].set_ylabel('Highest probability of a false or\nopposite indication off the path (%)')
axes[1].set_title('(b) off the path, $I_{\\mathrm{C}}$ = 120 and 200 A', fontsize=8.5, loc='left')
for ax in axes:
    ax.set_xticks(range(len(IE))); ax.set_xticklabels(IE)
    ax.set_xlabel('Reactive current pickup $I_{\\mathrm{EQ}>}$ (A)')
ha = [Line2D([], [], color=c, lw=1.5, marker='o', ms=3.6, mec=c) for c in COLS]
la = [f'{ic} ({lab})' for key, ic, lab, level in SYS]
ha += [Line2D([], [], color=MUTED, lw=1.5, marker='o', ms=3.6), Line2D([], [], color=MUTED, lw=1.1, ls=(0, (3, 2)), marker='o', ms=3.6, mfc='white')]
la += ['three phase sensors, $\\pm$1$\\degree$', 'first run, fixed error']
axes[0].legend(ha, la, fontsize=6.9, frameon=False, loc='center right', handlelength=2.2)
hb = [Line2D([], [], color=c, lw=1.5, marker='o', ms=3.6, mec=c) for _, c in LOADS]
lb = [f'bay load {l} A' for l, _ in LOADS]
hb += [Line2D([], [], color=MUTED, lw=1.5, marker='o', ms=3.6), Line2D([], [], color=MUTED, lw=1.1, ls=(0, (3, 2)), marker='o', ms=3.6, mfc='white')]
lb += ['phase-angle error $\\pm$1$\\degree$', 'phase-angle error $\\pm$2$\\degree$']
axes[1].legend(hb, lb, fontsize=6.9, frameon=False, loc='upper right', handlelength=2.2)
fig.subplots_adjust(left=0.1, right=0.955, top=0.9, bottom=0.16)
for e in ('pdf', 'png'): fig.savefig(os.path.join(FIG, f'direction_probability_3ct.{e}'), dpi=200 if e == 'png' else None)
print('figure written to', FIG)
