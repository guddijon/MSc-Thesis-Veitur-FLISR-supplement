"""Figures 4.2 and 4.3 from the station data of the supplement:
  busbar_allocation  Figure 4.2  A20 circuit on busbar 1 (breaker R11-1cc closed), busbar 2 (R11-2cc closed) or open, at the
                                 two base snapshots and on 17 Oct 2026, from
                                 ../../ch5_powerfactory_benchmark/data/snapshots/a20_breaker_states_by_snapshot.csv
                                 (circuit 04 on 24 Aug 2026 is drawn on busbar 2 as in the snapshot reconstruction; the switching log does not
                                 confirm this position)
  cable_lengths      Figure 4.3  GIS route length against the ADMS section table for the four contradicted links, from
                                 ../../ch5_powerfactory_benchmark/data/validation/gis_vs_model_lengths.csv (model_m is the
                                 ADMS section-table length of the link; section A020-1056A03 is a section-split mismatch and
                                 is described in the text, not drawn)
Liberation Sans, TrueType fonts embedded (pdf.fonttype 42). Output: ../output/{name}.{pdf,png}.
Run: MATPLOTLIBRC=../../matplotlibrc python3 a20_station_figs.py"""
import os, csv
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__)); CH = os.path.dirname(HERE)
DATA = os.path.join(os.path.dirname(CH), 'ch5_powerfactory_benchmark', 'data')
OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE, ADMS_GREY = '#2a78d6', '#eb6834', '#c8c7c2'
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8.5, 'pdf.fonttype': 42, 'text.color': INK,
                     'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': INK, 'ytick.color': INK,
                     'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6})

def save(fig, name):
    for e in ('pdf', 'png'): fig.savefig(os.path.join(OUT, f'{name}.{e}'), dpi=300 if e == 'png' else None)
    plt.close(fig)

# ------------------------------------------------------------------ Figure 4.2 busbar allocation
SNAP = [('winter_peak_boiler_off', '10 Dec 2025'), ('summer_peak', '24 Aug 2026'), ('today', '17 Oct 2026')]
CIRCUITS = ['04', '05', '06', '08', '09', '10', '11', '13', '19', '21', '22']
pos = {(r['snapshot'], r['COMPONENT_ALIAS']): r['position']
       for r in csv.DictReader(open(os.path.join(DATA, 'snapshots', 'a20_breaker_states_by_snapshot.csv')))}
def busbar(snap, c):
    on = [b for b in ('1', '2') if pos.get((snap, f'A0020_R11-{b}{c}_ROFAR')) == 'closed']
    assert len(on) <= 1, (snap, c, on)
    return on[0] if on else 'open'

fig = plt.figure(figsize=(6.1, 1.9)); ax = fig.add_axes([0.14, 0.2, 0.85, 0.6])
CW, RH = 0.94, 0.88
for i, (snap, lab) in enumerate(SNAP):
    for j, c in enumerate(CIRCUITS):
        b = busbar(snap, c)
        fc, ec, tc = {'1': (BLUE, BLUE, 'white'), '2': (ORANGE, ORANGE, 'white'), 'open': ('white', '#9b9a96', INK)}[b]
        ax.add_patch(Rectangle((j - CW / 2, -i - RH / 2), CW, RH, fc=fc, ec=ec, lw=1.2 if b == 'open' else 0))
        ax.text(j, -i, b, ha='center', va='center', fontsize=7.5, color=tc)
ax.set_xlim(-0.5, len(CIRCUITS) - 0.5); ax.set_ylim(-len(SNAP) + 0.5, 0.5)
ax.set_xticks(range(len(CIRCUITS))); ax.set_xticklabels(CIRCUITS); ax.xaxis.tick_top()
ax.set_yticks([-i for i in range(len(SNAP))]); ax.set_yticklabels([l for _, l in SNAP])
ax.tick_params(length=0, labelsize=8.5); ax.set_xlabel('A20 circuit', fontsize=8, labelpad=4); ax.xaxis.set_label_position('top')
for s in ax.spines.values(): s.set_visible(False)
hand = [Rectangle((0, 0), 1, 1, fc=BLUE, ec='none'), Rectangle((0, 0), 1, 1, fc=ORANGE, ec='none'),
        Rectangle((0, 0), 1, 1, fc='white', ec='#9b9a96', lw=1.2)]
fig.legend(hand, ['busbar 1 (S1)', 'busbar 2 (S2)', 'open'], loc='lower center', bbox_to_anchor=(0.565, 0.0), ncol=3,
           frameon=False, fontsize=8, handlelength=2.2, columnspacing=2.0)
save(fig, 'busbar_allocation')

# ------------------------------------------------------------------ Figure 4.3 cable lengths
LINKS = [('D1019-D20', 'A20 to D1019\n(circuit 13 head)'), ('D1028-D20', 'A20 to D1028\n(circuit 22 head)'),
         ('D1054-D1031', 'D1031 to D1054'), ('D1069-D1067', 'D1067 to D1069')]
rows = {r['link']: r for r in csv.DictReader(open(os.path.join(DATA, 'validation', 'gis_vs_model_lengths.csv')))}
gis = [float(rows[k]['gis_m']) for k, _ in LINKS]; adms = [float(rows[k]['model_m']) for k, _ in LINKS]
fig, ax = plt.subplots(figsize=(6.1, 3.0))
x = range(len(LINKS)); w = 0.36
ax.bar([i - w / 2 for i in x], gis, w, color=BLUE, label='GIS (surveyed route)', zorder=2)
ax.bar([i + w / 2 for i in x], adms, w, color=ADMS_GREY, label='ADMS section table', zorder=2)
for i, (g, a) in enumerate(zip(gis, adms)):
    ax.text(i, max(g, a) + 40, f'−{g - a:.0f} m' if a < g else f'+{a - g:.0f} m', ha='center', va='bottom', fontsize=8)
ax.set_xticks(list(x)); ax.set_xticklabels([l for _, l in LINKS])
ax.set_ylabel('Length (m)'); ax.set_ylim(0, 2000)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.tick_params(axis='x', length=0)
ax.grid(axis='y', color=GRID, lw=0.5, zorder=0)
ax.legend(frameon=False, loc='upper right', fontsize=8)
fig.subplots_adjust(left=0.11, right=0.98, top=0.96, bottom=0.15)
save(fig, 'cable_lengths')
print('written to', os.path.abspath(OUT))
