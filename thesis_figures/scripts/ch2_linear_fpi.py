"""Figure 2.16 (linear_fpi_layout): direction flags of the ComPass units along a radial feeder for a fault beyond the
second substation, drawn at the text width so the text prints at 6.6 pt or more: Direction A orange, Direction B blue,
fault in the status red.
Output: ../output/linear_fpi_layout.{pdf,png}.
Run: MATPLOTLIBRC=../../matplotlibrc python3 ch2_linear_fpi.py"""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon

CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
INK, SUB_FILL = '#0b0b0b', '#e2e1dc'
DIR = {'A': ('#eb6834', '#c2531f'), 'B': ('#2a78d6', '#2265b8')}     # (arrow, text) as in Figures 2.15 and 6.2
FAULT, BOLT = '#b3261e', '#eda100'
plt.rcParams.update({'font.family': 'Liberation Sans', 'pdf.fonttype': 42, 'text.color': INK})

W, H, Y = 6.27, 1.32, 0.62                                 # inches; data units are inches; feeder line at Y
fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

ax.plot([0.02, 6.02], [Y, Y], color=INK, lw=1.8, zorder=1, solid_capstyle='butt')
ax.text(0.02, Y + 0.07, 'Fault Current\nFrom Source', ha='left', va='bottom', fontsize=7.5, fontweight='bold',
        style='italic', color=FAULT, linespacing=1.15)

def fpi(cx, d, sub):
    ax.add_patch(Rectangle((cx - 0.18, Y - 0.15), 0.36, 0.3, fc='white', ec=INK, lw=0.9, zorder=3))
    ax.text(cx, Y, 'FPI', ha='center', va='center', fontsize=7.5, fontweight='bold', zorder=4)
    arrow, tone = DIR[d]
    ax.add_patch(FancyArrowPatch((cx - 0.3, Y + 0.42), (cx + 0.3, Y + 0.42), arrowstyle='-|>', mutation_scale=10,
                                 lw=1.6, color=arrow, shrinkA=0, shrinkB=0, zorder=3))
    ax.text(cx, Y + 0.255, sub, ha='center', va='baseline', fontsize=7, style='italic', zorder=4)
    ax.text(cx, Y + 0.52, f'Dir {d}', ha='center', va='baseline', fontsize=8, fontweight='bold', color=tone, zorder=4)

def substation(cx, label):
    ax.add_patch(Rectangle((cx - 0.4, Y - 0.21), 0.8, 0.42, fc=SUB_FILL, ec=INK, lw=0.9, zorder=3))
    ax.text(cx, Y, label, ha='center', va='center', fontsize=7.5, fontweight='bold', linespacing=1.15, zorder=4)

fpi(1.15, 'A', '(Into Station Bus)')
substation(1.9, 'Dist.\nSubstation 1')
fpi(2.65, 'B', '(Down Cable)')
ax.text(3.3, Y - 0.07, '11 kV Cable Section', ha='center', va='top', fontsize=7, style='italic')
fpi(3.95, 'A', '(Into Station Bus)')
substation(4.7, 'Dist.\nSubstation 2')
fpi(5.45, 'B', '(Down Cable)')
fx = 5.95                                                  # fault: lightning bolt across the line
bolt = [(fx + 0.02, Y + 0.3), (fx - 0.06, Y + 0.02), (fx + 0.03, Y + 0.02), (fx - 0.03, Y - 0.22),
        (fx + 0.07, Y - 0.22), (fx + 0.0, Y - 0.42), (fx + 0.13, Y - 0.12), (fx + 0.05, Y - 0.12),
        (fx + 0.11, Y + 0.08), (fx + 0.03, Y + 0.08), (fx + 0.1, Y + 0.3)]
ax.add_patch(Polygon(bolt, closed=True, fc=BOLT, ec=FAULT, lw=0.6, zorder=5))
ax.text(6.25, Y - 0.45, 'Fault Location', ha='right', va='top', fontsize=8, fontweight='bold', color=FAULT)

for e in ('pdf', 'png'): fig.savefig(os.path.join(OUT, f'linear_fpi_layout.{e}'), dpi=300 if e == 'png' else None)
print('written to', os.path.abspath(OUT))
