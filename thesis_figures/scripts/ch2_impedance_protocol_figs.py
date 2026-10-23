"""Chapter 2 figures in the house style:
  impedance_admittance   Z = R + jX (inductive, X > 0) and Y = 1/Z = G + jB with B < 0 (thesis Eqs. eq:impedance to
                         eq:admittance_def)
  protocol_architecture  ComPass B 2.0 -> RS-485 Modbus RTU -> Brodersen RTU -> DNP3 Class 1 events -> SCADA / ADMS
Liberation Sans, TrueType fonts embedded (pdf.fonttype 42). Output: ../output/{name}.{pdf,png}.
Run: MATPLOTLIBRC=../../matplotlibrc python3 ch2_impedance_protocol_figs.py"""
import os, math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(CH, 'output')
os.makedirs(OUT, exist_ok=True)                                 # thesis_figures/output
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE = '#2a78d6', '#eb6834'
TINT = ['#eaf2fc', '#d6e6f9', '#c2daf6']                       # light steps of the blue ramp for box fills
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 9, 'pdf.fonttype': 42, 'text.color': INK,
                     'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans',
                     'mathtext.it': 'Liberation Sans:italic', 'mathtext.bf': 'Liberation Sans:bold'})

def save(fig, name):
    for e in ('pdf', 'png'): fig.savefig(os.path.join(OUT, f'{name}.{e}'), dpi=300 if e == 'png' else None)
    plt.close(fig)

def arrow(ax, p, q, col, lw=2.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=12, lw=lw, color=col, shrinkA=0, shrinkB=0))

# ------------------------------------------------------------------ impedance and admittance triangles
R, X = 1.0, 1.1                                  # drawn proportions; the admittance triangle mirrors the angle
fig, axes = plt.subplots(1, 2, figsize=(5.64, 2.75), gridspec_kw=dict(wspace=0.32))
for ax in axes:
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for s in ('top', 'right', 'left', 'bottom'): ax.spines[s].set_visible(False)
# (a) impedance
ax = axes[0]
ax.axhline(0, color=MUTED, lw=0.7); ax.axvline(0, color=MUTED, lw=0.7)
arrow(ax, (0, 0), (R, 0), BLUE); arrow(ax, (R, 0), (R, X), ORANGE); arrow(ax, (0, 0), (R, X), INK)
ang = math.degrees(math.atan2(X, R))
ax.text(R / 2, -0.09, '$R$', color=BLUE, ha='center', va='top', fontsize=10)
ax.text(R + 0.06, X / 2, '$jX$', color=ORANGE, ha='left', va='center', fontsize=10)
ax.text(R / 2 - 0.08, X / 2 + 0.06, r'$\mathbf{Z} = R + jX$', color=INK, ha='center', va='bottom', rotation=ang,
        rotation_mode='anchor', fontsize=9.5)
ax.text(1.42, 0.03, 'Re', color=MUTED, ha='right', va='bottom', fontsize=8)
ax.text(0.03, 1.32, 'Im', color=MUTED, ha='left', va='top', fontsize=8)
ax.set_xlim(-0.12, 1.45); ax.set_ylim(-0.3, 1.35)
ax.set_title('(a) Impedance, inductive: $X > 0$', fontsize=9, loc='left')
# (b) admittance
ax = axes[1]
ax.axhline(0, color=MUTED, lw=0.7); ax.axvline(0, color=MUTED, lw=0.7)
arrow(ax, (0, 0), (R, 0), BLUE); arrow(ax, (R, 0), (R, -X), ORANGE); arrow(ax, (0, 0), (R, -X), INK)
ax.text(R / 2, 0.08, '$G$', color=BLUE, ha='center', va='bottom', fontsize=10)
ax.text(R + 0.06, -X / 2, '$jB$\n$(B < 0)$', color=ORANGE, ha='left', va='center', fontsize=10, linespacing=1.3)
ax.text(R / 2 + 0.16, -X / 2 + 0.1, r'$\mathbf{Y} = G + jB$', color=INK, ha='center', va='bottom', rotation=-ang,
        rotation_mode='anchor', fontsize=9.5)
ax.text(1.42, 0.03, 'Re', color=MUTED, ha='right', va='bottom', fontsize=8)
ax.text(0.03, 0.22, 'Im', color=MUTED, ha='left', va='top', fontsize=8)
ax.set_xlim(-0.12, 1.45); ax.set_ylim(-1.35, 0.3)
ax.set_title(r'(b) Admittance $\mathbf{Y} = 1/\mathbf{Z}$: $B < 0$', fontsize=9, loc='left')
fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.03)
save(fig, 'impedance_admittance')

# ------------------------------------------------------------------ protocol architecture
fig, ax = plt.subplots(figsize=(6.27, 1.45))
ax.set_xlim(0, 10); ax.set_ylim(0, 2.2); ax.axis('off')
boxes = [('ComPass B 2.0', 'field device'), ('Brodersen RTU', 'protocol gateway'), ('Veitur SCADA / ADMS', 'control centre')]
W_, H_, Y0 = 2.6, 1.15, 0.15; xs = [0.05, 3.7, 7.35]
for (title, sub), x, fill in zip(boxes, xs, TINT):
    ax.add_patch(FancyBboxPatch((x, Y0), W_, H_, boxstyle='round,pad=0,rounding_size=0.08', fc=fill, ec=MUTED, lw=0.8))
    ax.text(x + W_ / 2, Y0 + H_ * 0.62, title, ha='center', va='center', fontsize=10, fontweight='bold', color=INK)
    ax.text(x + W_ / 2, Y0 + H_ * 0.3, sub, ha='center', va='center', fontsize=8.5, color=MUTED)
for (x1, x2), lab in zip(((xs[0] + W_, xs[1]), (xs[1] + W_, xs[2])), ('RS-485\nModbus RTU', 'DNP3\nClass 1 events')):
    ym = Y0 + H_ / 2
    arrow(ax, (x1 + 0.08, ym), (x2 - 0.08, ym), INK, lw=1.4)
    ax.text((x1 + x2) / 2, Y0 + H_ + 0.12, lab, ha='center', va='bottom', fontsize=8.5, color=BLUE, linespacing=1.25)
fig.subplots_adjust(left=0.005, right=0.995, top=0.99, bottom=0.01)
save(fig, 'protocol_architecture')
print('written to', os.path.abspath(OUT))
