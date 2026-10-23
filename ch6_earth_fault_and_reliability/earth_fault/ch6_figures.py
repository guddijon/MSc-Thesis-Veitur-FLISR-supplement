"""Chapter 6 figures from results/ch6 (ch6_results.py), at print size for the thesis text width:
  v0_coverage            displacement voltage against fault resistance per system size, model and Eq. (3.x)
  fpi_signatures         reactive residual current at every ComPass bay of busbar 2 for fault SCN-04
  direction_probability  lowest probability of Direction B at the path bays against I_EQ> and against R_F
Output: PDF (thesis) and PNG (preview) in ../../thesis_figures/ch6, or in the folder EF_FIG_DIR names."""
import os, sys, csv, math, collections
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'results', 'ch6')
FIG = os.environ.get('EF_FIG_DIR') or os.path.join(os.path.dirname(os.path.dirname(HERE)), 'thesis_figures', 'ch6')   # reproduce.py: output/
os.makedirs(FIG, exist_ok=True)
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE = '#2a78d6', '#eb6834'
RAMP = ['#86b6ef', '#5598e7', '#3987e5', '#256abf', '#184f95', '#0d366b']      # sequential blue, steps 250 to 700
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8.5, 'pdf.fonttype': 42, 'text.color': INK,
                     'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans', 'mathtext.it': 'Liberation Sans:italic', 'mathtext.bf': 'Liberation Sans:bold',
                     'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
                     'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6})
W = 6.27
SYS = [('bb2', '21 A'), ('bb2_40', '40 A'), ('bb1', '61 A'), ('coupled', '83 A'), ('bb2_120', '120 A'), ('bb2_200', '200 A')]
LABEL = {'bb2': 'busbar 2', 'bb2_40': 'busbar 2 + shunt', 'bb1': 'busbar 1', 'coupled': 'coupled', 'bb2_120': 'busbar 2 + shunt',
         'bb2_200': 'busbar 2 + shunt'}

def rd(name): return list(csv.DictReader(open(os.path.join(R, name))))
def save(fig, name):
    for e in ('pdf', 'png'): fig.savefig(os.path.join(FIG, f'{name}.{e}'), dpi=200 if e == 'png' else None)
    plt.close(fig)
def style(ax):
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    ax.grid(color=GRID, lw=0.5); ax.set_axisbelow(True)

# ------------------------------------------------------------------ displacement voltage against fault resistance
cov = rd('v0_coverage.csv'); ic = {r['system']: float(r['IC_A']) for r in cov}
fig, ax = plt.subplots(figsize=(W, 3.0)); style(ax)
E_RATIO = (11.15 / 11.0)
rf_line = [10 ** (k / 40) for k in range(0, 161)]                                   # 1 to 10 000 ohm
for (key, lab), col in zip(SYS, RAMP):
    I = ic[key]; E = 11.15 / math.sqrt(3) * 1000
    ax.plot(rf_line, [E_RATIO / math.sqrt(1 + (I * rf / E) ** 2) for rf in rf_line], color=col, lw=1.6,
            label=f'{lab} ({LABEL[key]})')
    pts = [r for r in cov if r['system'] == key and int(r['RF_ohm']) >= 10]
    ax.plot([int(r['RF_ohm']) for r in pts], [float(r['V0_over_En_model']) for r in pts], 'o', ms=3.2, mfc=col, mec='white',
            mew=0.6, ls='none')
for t in (0.10, 0.20, 0.30):
    ax.axhline(t, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    ax.text(1.15, t + 0.012, f'$V_{{\\mathrm{{NEQ}}>}}$ = {int(t * 100)} %', fontsize=7, color=MUTED, va='bottom')
ax.set_xscale('log'); ax.set_xlim(1, 10000); ax.set_ylim(0, 1.08)
ax.set_xlabel('Fault resistance $R_{\\mathrm{F}}$ ($\\Omega$)'); ax.set_ylabel('$|\\mathbf{V}_0|$ / $E_{\\mathrm{n}}$')
h, l = ax.get_legend_handles_labels()
h.append(plt.Line2D([], [], color=MUTED, marker='o', ls='none', ms=3.2, mfc=MUTED, mec='white')); l.append('offline model')
h.insert(len(h) - 1, plt.Line2D([], [], color=MUTED, lw=1.6)); l.insert(len(l) - 1, 'closed-form expression')
ax.legend(h, l, title='$I_{\\mathrm{C}}$ of the system', fontsize=7, title_fontsize=7.5, frameon=False, loc='upper right',
          ncol=1, handlelength=1.8)
fig.tight_layout(); save(fig, 'v0_coverage')

# ------------------------------------------------------------------ FPI signatures, SCN-04
def load_sig(name): return {r['bay']: r for r in rd(name)}
ORDER = [('A20_F13', 'A20, circuit 13 head'), ('D1029_102', 'D1029, toward A20'), ('D1029_101', 'D1029, away from A20'),
         ('D1066_101', 'D1066, toward A20'), ('D1066_102', 'D1066, away from A20'), None,
         ('D1025_101', 'D1025, toward A20'), ('D1025_102', 'D1025, away from A20'), ('D1030_102', 'D1030, toward A20'),
         ('D1030_101', 'D1030, away from A20'), 'gap',
         ('A20_F08', 'A20, circuit 08 head'), ('D1061_102', 'D1061, toward A20'), ('D1061_101', 'D1061, away from A20'),
         ('D1062_102', 'D1062, toward A20'), ('D1062_101', 'D1062, away from A20')]
fig, axes = plt.subplots(1, 2, figsize=(W, 3.9), sharey=True, gridspec_kw=dict(width_ratios=[1, 1.25], wspace=0.08))
for ax, (fn, title, xmax) in zip(axes, (('fpi_phasors_scn04.csv', '(a) busbar 2 as built, $I_{\\mathrm{C}}$ = 21 A', 14),
                                       ('fpi_phasors_scn04_120A.csv', '(b) with added capacitance, $I_{\\mathrm{C}}$ = 120 A', 120))):
    sig = load_sig(fn); y = 0; ticks, labels = [], []; fault_y = None; sep_y = None
    style(ax); ax.grid(axis='y', visible=False)
    for item in ORDER:
        if item is None: fault_y = y + 0.5; y += 1.0; continue
        if item == 'gap': sep_y = y + 0.4; y += 0.8; continue
        b, lab = item; v = float(sig[b]['Iq_A'])
        ax.barh(y, v, height=0.62, color=BLUE if v > 0 else ORANGE, edgecolor='white', lw=0.5)
        if sig[b]['role'] == 'pathB' or b.startswith('A20'):
            ax.text(v + (0.012 if v > 0 else -0.012) * xmax * 2, y, f'{v:+.1f}', va='center', ha='left' if v > 0 else 'right',
                    fontsize=7, color=INK)
        ticks.append(y); labels.append(lab); y += 1
    ax.axvline(0, color=MUTED, lw=0.6)
    for s in (-5, 5): ax.axvline(s, color=MUTED, lw=0.7, ls=(0, (3, 2)))
    ax.axhline(fault_y, color=INK, lw=0.9)
    ax.text(13.6 if xmax < 50 else 131, fault_y - 0.12, 'fault SCN-04', ha='right', va='bottom', fontsize=7, color=INK)
    ax.axhline(sep_y, color=GRID, lw=0.8)
    ax.set_xlim((-14, 14) if xmax < 50 else (-135, 135))
    ax.set_title(title, fontsize=8.5, loc='left')
    ax.set_xlabel('$|3\\mathbf{I}_0|\\sin\\varphi$ (A)')
axes[0].set_yticks(ticks); axes[0].set_yticklabels(labels, fontsize=7.3); axes[0].invert_yaxis()
axes[0].tick_params(axis='y', length=0)
axes[0].text(5.4, ticks[-1] + 0.1, '$\\pm I_{\\mathrm{EQ}>}$ = 5 A', fontsize=7, color=MUTED, va='center', ha='left')
from matplotlib.patches import Patch
fig.legend([Patch(color=BLUE), Patch(color=ORANGE)], ['Direction B (fault beyond the bay\'s cable)', 'Direction A'],
           loc='lower center', ncol=2, frameon=False, fontsize=7.5, bbox_to_anchor=(0.55, 0.0))
fig.subplots_adjust(left=0.2, right=0.98, top=0.93, bottom=0.2)
save(fig, 'fpi_signatures')

# ------------------------------------------------------------------ direction probability
dp = rd('direction_probability.csv'); pr = rd('path_probability_rf.csv')
IE = [1, 2, 3, 5, 8, 10, 15, 20]; RFS = [0, 10, 30, 100, 300, 1000, 3000]
fig, axes = plt.subplots(1, 2, figsize=(W, 2.9), sharey=True, gridspec_kw=dict(wspace=0.08))
for ax in axes: style(ax)
for (key, lab), col in zip(SYS, RAMP):
    ys = [float(next(r['min_P_B_path_RF_le_30'] for r in dp if r['system'] == key and r['calibration'] == 'standard'
                     and r['V_NEQ_pct'] == '20' and r['I_EQ_A'] == str(ie))) for ie in IE]
    axes[0].plot(range(len(IE)), ys, '-o', color=col, lw=1.6, ms=3.6, mec='white', mew=0.6, label=f'{lab} ({LABEL[key]})')
    yr = [float(next(r['min_P_B_path'] for r in pr if r['system'] == key and r['calibration'] == 'standard'
                     and r['V_NEQ_pct'] == '20' and r['I_EQ_A'] == '5' and r['RF_ohm'] == str(rf))) for rf in RFS]
    axes[1].plot(range(len(RFS)), yr, '-o', color=col, lw=1.6, ms=3.6, mec='white', mew=0.6)
for ax in axes:
    for lvl, txt in ((0.99, '99 %'), (0.95, '95 %')):
        ax.axhline(lvl, color=MUTED, lw=0.7, ls=(0, (3, 2)))
    ax.set_ylim(-0.03, 1.06)
axes[1].text(len(RFS) - 1.02, 0.99, '99 %', fontsize=7, color=MUTED, ha='right', va='bottom')
axes[1].text(len(RFS) - 1.02, 0.95, '95 %', fontsize=7, color=MUTED, ha='right', va='top')
axes[0].set_xticks(range(len(IE))); axes[0].set_xticklabels(IE)
axes[0].set_xlabel('Reactive current pickup $I_{\\mathrm{EQ}>}$ (A)')
axes[0].set_ylabel('Lowest probability of Direction B\nat the bays facing the fault')
axes[0].set_title('(a) $R_{\\mathrm{F}} \\leq$ 30 $\\Omega$', fontsize=8.5, loc='left')
axes[1].set_xticks(range(len(RFS))); axes[1].set_xticklabels(RFS)
axes[1].set_xlabel('Fault resistance $R_{\\mathrm{F}}$ ($\\Omega$)')
axes[1].set_title('(b) $I_{\\mathrm{EQ}>}$ = 5 A', fontsize=8.5, loc='left')
axes[0].legend(title='$I_{\\mathrm{C}}$ of the system', fontsize=7, title_fontsize=7.5, frameon=False, loc='lower left')
fig.subplots_adjust(left=0.12, right=0.98, top=0.9, bottom=0.17)
save(fig, 'direction_probability')
print('figures written to', FIG)
