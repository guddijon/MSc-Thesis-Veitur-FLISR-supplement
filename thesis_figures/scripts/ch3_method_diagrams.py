"""Chapter 3 diagrams in the house style:
  model_sources          Figure 3.1  sources of the PowerFactory benchmark model; counts from the GIS export of 17 Oct 2026,
                                     the ADMS section table and the GIS trace (55 of 62 links within 10 %, data in
                                     ../../ch5_powerfactory_benchmark/data/validation/gis_vs_model_lengths.csv)
  boiler_d1005           Figure 3.2  supply of the boiler network and of substation D1005 (circuit 04 and tie bay 1005-1-1)
  tuning_validation      Figure 3.3  split of the measurements into a tuning set and a validation set
  restoration_processes  Figure 3.5  actor performing each restoration phase in the three modelled processes, with the
                                     measured phase durations of Table 3.8
Liberation Sans, TrueType fonts embedded (pdf.fonttype 42). Output: ../output/{name}.{pdf,png}.
Run: MATPLOTLIBRC=../../matplotlibrc python3 ch3_method_diagrams.py"""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle

CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE = '#2a78d6'
F_ADMS, F_GIS, F_MID, F_TAN, E_TAN, DARK = '#eaf2fc', '#e6f2e6', '#f3f2ef', '#f6e8d5', '#9a6a2a', '#3a3937'
F_REMOTE, F_FIELD = '#a4c6f0', '#e2e1dc'
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8, 'pdf.fonttype': 42, 'text.color': INK})

def canvas(w, h, k=1.0):
    """Figure whose data units are inches (times k for a figure printed narrower), so box and font sizes relate directly."""
    fig = plt.figure(figsize=(w * k, h * k)); ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis('off')
    return fig, ax

def save(fig, name):
    for e in ('pdf', 'png'): fig.savefig(os.path.join(OUT, f'{name}.{e}'), dpi=300 if e == 'png' else None)
    plt.close(fig)

def text_block(ax, x, y, text, fs=8, color=INK, ls=1.25):
    """Multi-line text centred on (x, y) with the lines on a fixed baseline grid (ls x font size), so the gaps do not
    depend on the letters; Matplotlib's own line layout adds each line's descent."""
    unit = ax.figure.get_size_inches()[0] / (ax.get_xlim()[1] - ax.get_xlim()[0])     # inches per data unit
    pitch, cap = ls * fs / 72 / unit, 0.72 * fs / 72 / unit
    lines = text.split('\n')
    base = y + ((len(lines) - 1) * pitch + cap) / 2 - cap
    for i, line in enumerate(lines):
        ax.text(x, base - i * pitch, line, ha='center', va='baseline', fontsize=fs, color=color, zorder=3)

class Box:
    def __init__(self, ax, x, y, w, h, text, fc='white', ec=MUTED, tc=INK, fs=8, r=0.07):
        self.x, self.y, self.w, self.h = x, y, w, h
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                    fc=fc, ec=ec, lw=0.8, zorder=2))
        text_block(ax, x, y, text, fs, tc)

    def edge(self, tx, ty):
        """Point on the box outline in the direction of (tx, ty)."""
        dx, dy = tx - self.x, ty - self.y
        t = min(self.w / 2 / abs(dx) if dx else 1e9, self.h / 2 / abs(dy) if dy else 1e9)
        return self.x + t * dx, self.y + t * dy

def link(ax, a, b, arrow=True, dashed=False, pa=None, pb=None, lw=0.9):
    """Line from box a to box b; pa/pb override the aim points (x, y) on each box."""
    ta = pb or (b.x, b.y); tb = pa or (a.x, a.y)
    p = a.edge(*ta) if pa is None else pa
    q = b.edge(*tb) if pb is None else pb
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>' if arrow else '-', mutation_scale=9, lw=lw, color=MUTED,
                                 ls=(0, (3, 2)) if dashed else '-', shrinkA=0, shrinkB=0, zorder=1))
    return p, q

# ------------------------------------------------------------------ Figure 3.1 model sources
def route(ax, pts, arrow=True, lw=0.9):
    """Orthogonal connector through the points pts; arrowhead on the last segment."""
    for a, b in zip(pts[:-2], pts[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=MUTED, lw=lw, solid_capstyle='projecting', zorder=1)
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle='-|>' if arrow else '-', mutation_scale=9, lw=lw,
                                 color=MUTED, shrinkA=0, shrinkB=0, zorder=1))

fig, ax = canvas(6.27, 4.25)
ax.add_patch(FancyBboxPatch((0.08, 0.08), 2.17, 4.07, boxstyle='round,pad=0,rounding_size=0.08', fc='none', ec='#b9b8b3', lw=0.8))
ax.text(1.165, 4.0, 'Sources', ha='center', va='center', fontsize=9)
SX, SW, H2, H3 = 1.165, 1.95, 0.40, 0.54
src = {}
for key, y, h, txt, fc in (
        ('adms', 3.55, H2, 'ADMS section table\n119 sections, 31 substations', F_ADMS),
        ('trace', 3.0, H3, 'GIS cable-layer trace\n62 station links\n(55 within 10 %)', F_GIS),
        ('gis', 2.37, H3, 'GIS export (17 Oct 2026)\n73 sections, 23 substations\nroutes and lengths', F_GIS),
        ('log', 1.8, H2, 'ADMS switching log\nand operators', F_ADMS),
        ('scada', 1.3, H2, 'SCADA historian\n(15-min means)', 'white'),
        ('plate', 0.8, H2, 'Nameplates and\nmanufacturer records', 'white'),
        ('cat', 0.3, H2, 'ADMS catalogs and\nasset ratings', F_ADMS)):
    src[key] = Box(ax, SX, y, SW, h, txt, fc=fc)
MX, MW = 3.95, 1.65
topo = Box(ax, MX, 3.0, MW, H3, 'Topology\n54 substations, 192 sections\n36.0 km', fc=F_MID)
state = Box(ax, MX, 1.82, MW, H3, 'Operating state\nswitch positions, taps,\n66 kV voltage', fc=F_MID)
loads = Box(ax, MX, 1.22, MW, H2, 'Loads\nallocated per feeder', fc=F_MID)
par = Box(ax, MX, 0.55, MW, H3, 'Electrical parameters\ncables, transformers,\nswitchgear', fc=F_MID)
model = Box(ax, 5.65, 1.82, 1.06, 0.5, 'PowerFactory\nbenchmark model', fc=DARK, ec=DARK, tc='white', fs=8.5)
XS, XM, XE, XB = SX + SW / 2, MX - MW / 2, 2.85, 4.97        # source edge, middle left edge, elbow, collector
# sources -> middle column: straight where a source is level with its target, one elbow otherwise
route(ax, [(XS, 3.55), (XE, 3.55), (XE, 3.15), (XM, 3.15)])
route(ax, [(XS, 3.0), (XM, 3.0)])
ax.text(2.55, 3.05, 'lengths:\nGIS wins', ha='center', va='bottom', fontsize=7.5, color=MUTED, linespacing=1.15)
route(ax, [(XS, 2.37), (XE, 2.37), (XE, 2.85), (XM, 2.85)])
route(ax, [(XS, 1.86), (XM, 1.86)])
route(ax, [(XS, 1.38), (XE, 1.38), (XE, 1.66), (XM, 1.66)])
route(ax, [(XS, 1.22), (XM, 1.22)])
route(ax, [(XS, 0.72), (XM, 0.72)])
route(ax, [(XS, 0.4), (XM, 0.4)])
# middle column -> one collector -> model
XR = MX + MW / 2
for b in (topo, loads, par): ax.plot([XR, XB], [b.y, b.y], color=MUTED, lw=0.9, zorder=1)
ax.plot([XB, XB], [topo.y, par.y], color=MUTED, lw=0.9, solid_capstyle='projecting', zorder=1)
route(ax, [(XR, state.y), (model.x - model.w / 2, state.y)])
for y in (state.y, loads.y): ax.plot(XB, y, 'o', ms=2.6, color=MUTED, zorder=2)
save(fig, 'model_sources')

# ------------------------------------------------------------------ Figure 3.2 boiler network and D1005
fig, ax = canvas(3.85, 3.95, k=0.88)                            # printed at 0.55 of the text width
LX, RX = 0.95, 3.0
bb1 = Box(ax, LX, 3.72, 1.0, 0.3, 'A20 busbar 1', fc=DARK, ec=DARK, tc='white', fs=8.5, r=0.0)
bb2 = Box(ax, RX, 3.72, 1.0, 0.3, 'A20 busbar 2', fc=DARK, ec=DARK, tc='white', fs=8.5, r=0.0)
d1028 = Box(ax, LX, 3.12, 0.62, 0.28, 'D1028')
d1005 = Box(ax, LX, 2.5, 1.3, 0.56, 'D1005 SFA (Veitur\ndistribution station,\n3 transformers)')
bnet = Box(ax, RX + 0.05, 2.5, 1.42, 0.4, 'Boiler 11 kV network\n(plant site)', fc=F_TAN, ec=E_TAN)
boil = Box(ax, RX + 0.05, 1.86, 1.18, 0.4, 'Electrode boiler\n4.9 MW', fc=F_TAN, ec=E_TAN)
d1036 = Box(ax, 0.6, 1.86, 0.62, 0.28, 'D1036')
d1004 = Box(ax, 0.6, 1.3, 0.62, 0.28, 'D1004')
d1003 = Box(ax, 0.95, 0.8, 0.62, 0.28, 'D1003')
d1040 = Box(ax, 0.48, 0.25, 0.62, 0.28, 'D1040')
d1002 = Box(ax, 1.45, 0.25, 0.8, 0.38, 'D1002\n(circuit 21)')
link(ax, bb1, d1028, arrow=False, lw=1.3)
ax.text(LX + 0.05, 3.42, 'circuit 22', ha='left', va='center', fontsize=7.5)
link(ax, d1028, d1005, arrow=False, lw=1.3)
link(ax, d1005, d1036, arrow=False, lw=1.3, pa=(0.72, d1005.y - d1005.h / 2))
link(ax, d1036, d1004, arrow=False, lw=1.3)
p, q = link(ax, d1004, d1003, arrow=False, dashed=True, lw=1.3, pa=(0.6, d1004.y - d1004.h / 2), pb=(0.85, d1003.y + d1003.h / 2))
ax.text((p[0] + q[0]) / 2 + 0.06, (p[1] + q[1]) / 2, 'NO', ha='left', va='center', fontsize=7.5)
link(ax, d1005, d1003, arrow=False, lw=1.3, pa=(1.05, d1005.y - d1005.h / 2), pb=(1.05, d1003.y + d1003.h / 2))
link(ax, d1003, d1040, arrow=False, lw=1.3, pa=(0.85, d1003.y - d1003.h / 2))
p, q = link(ax, d1003, d1002, arrow=False, dashed=True, lw=1.3, pa=(1.1, d1003.y - d1003.h / 2))
ax.text((p[0] + q[0]) / 2 + 0.07, (p[1] + q[1]) / 2, 'NO', ha='left', va='center', fontsize=7.5)
link(ax, bb2, bnet, arrow=False, dashed=True, lw=1.3)
ax.text(RX - 0.06, 3.15, 'circuit 04 (R11-204)\nSFAA cable, 2.2 km', ha='right', va='center', fontsize=7.5, linespacing=1.2)
p, q = link(ax, d1005, bnet, arrow=False, dashed=True, lw=1.3)
ax.text((p[0] + q[0]) / 2, p[1] - 0.06, 'tie\nbay 1005-1-1', ha='center', va='top', fontsize=7.5, linespacing=1.2)
link(ax, bnet, boil, arrow=False, lw=1.3)
save(fig, 'boiler_d1005')

# ------------------------------------------------------------------ Figure 3.3 tuning and validation
fig, ax = canvas(6.27, 1.62)
YT, YV = 1.22, 0.47
scada = Box(ax, 0.58, YT, 1.06, 0.4, 'SCADA snapshot\n(15-min mean)')
tune = Box(ax, 1.78, YT, 1.06, 0.54, 'Tuning set\nA20 feeder-head\ncurrents', fc=F_ADMS)
alloc = Box(ax, 3.07, YT, 1.3, 0.54, 'Load allocation\none factor per feeder,\nimpedances fixed')
tuned = Box(ax, 4.32, YT, 0.92, 0.4, 'Tuned model\nload flow')
valid = Box(ax, 2.0, YV, 1.4, 0.66, 'Validation set\nA20 busbar voltages\nComPass bay currents\nsubstation voltages', fc=F_GIS)
err = Box(ax, 3.95, YV, 1.15, 0.4, 'Error metrics\nMAE, RMSE, MAD')
DX, DW, DH = 5.4, 1.5, 0.62
# straight connectors along each row; the two links between the rows are vertical or have one right-angle elbow
route(ax, [(scada.x + scada.w / 2, YT), (tune.x - tune.w / 2, YT)])
route(ax, [(tune.x + tune.w / 2, YT), (alloc.x - alloc.w / 2, YT)])
route(ax, [(alloc.x + alloc.w / 2, YT), (tuned.x - tuned.w / 2, YT)])
route(ax, [(scada.x, YT - scada.h / 2), (scada.x, YV), (valid.x - valid.w / 2, YV)])
XV = (max(tuned.x - tuned.w / 2, err.x - err.w / 2) + min(tuned.x + tuned.w / 2, err.x + err.w / 2)) / 2
route(ax, [(XV, YT - tuned.h / 2), (XV, YV + err.h / 2)])              # straight down: the boxes overlap in x
route(ax, [(valid.x + valid.w / 2, YV), (err.x - err.w / 2, YV)])
route(ax, [(err.x + err.w / 2, YV), (DX - DW / 2, YV)])
ax.add_patch(Polygon([(DX - DW / 2, YV), (DX, YV + DH / 2), (DX + DW / 2, YV), (DX, YV - DH / 2)], closed=True,
                     fc=F_TAN, ec=E_TAN, lw=0.8, zorder=2))
text_block(ax, DX, YV, 'Within sensor\ntolerance?', 8)
save(fig, 'tuning_validation')

# ------------------------------------------------------------------ Figure 3.5 restoration processes
# the three measured phases of the reliability model (Table 3.8): response, sectionalizing, time to the last customer;
# in (ii) and (iii) the customers between two remotely controlled stations (crew zone) wait for the crew as in (i)
PHASES = [('Response', 'trip to first switching'), ('Sectionalizing', 'to first customers restored'),
          ('Repair', 'to last customer restored')]
ACTORS = {'a': ('automatic', BLUE, 'white'), 'c': ('control room', F_REMOTE, INK), 'f': ('field crew', F_FIELD, INK),
          'o': ('call-out', F_TAN, INK)}
CALL, CREW, REPAIR = ('o', 'night call-out\n26 to 68 min'), ('f', 'crew switching, megger\n38 to 63 min'), \
                     ('f', 'repair\n92 to 941 min after trip')
# cells: (first column, last column, upper or full or lower half, actor, text)
ROWS = [('(i) Crew-based\nsectionalizing', [(0, 0, 'full') + CALL, (1, 1, 'full') + CREW, (2, 2, 'full') + REPAIR]),
        ('(ii) FPI-assisted\nremote sectionalizing',
         [(0, 0, 'full') + CALL, (1, 1, 'upper', 'c', 'remote switching, 6 to 22 min'),
          (1, 1, 'lower', 'f', 'crew zone, 38 to 63 min'), (2, 2, 'full') + REPAIR]),
        ('(iii) Automated\nFLISR',
         [(0, 1, 'upper', 'a', 'FLISR isolation and restoration, 1 to 5 min'),
          (0, 0, 'lower', 'o', 'night call-out'), (1, 1, 'lower', 'f', 'crew zone, 38 to 63 min'),
          (2, 2, 'full') + REPAIR])]
fig, ax = canvas(6.27, 2.62)
X0, CW, CG, RH, RG, HG, Y0 = 1.5, 1.52, 0.07, 0.5, 0.14, 0.04, 2.08
for j, (ph, sub) in enumerate(PHASES):
    xc = X0 + j * (CW + CG) + CW / 2
    ax.text(xc, Y0 + 0.25, ph, ha='center', va='baseline', fontsize=8.5)
    ax.text(xc, Y0 + 0.1, sub, ha='center', va='baseline', fontsize=7, color=MUTED)
for i, (lab, cells) in enumerate(ROWS):
    top = Y0 - i * (RH + RG)
    text_block(ax, X0 - 0.12 - 0.62, top - RH / 2, lab, 8.5)
    for c0, c1, part, k, txt in cells:
        x0 = X0 + c0 * (CW + CG); x1 = X0 + c1 * (CW + CG) + CW
        hh = RH if part == 'full' else (RH - HG) / 2
        yc = top - hh / 2 if part in ('full', 'upper') else top - RH + hh / 2
        _, fc, tc = ACTORS[k]
        Box(ax, (x0 + x1) / 2, yc, x1 - x0, hh, txt, fc=fc, ec=fc, tc=tc, fs=7.5 if part == 'full' else 7, r=0.04)
LEG = [('a', 'automatic (protection, ADMS)'), ('c', 'control room, remote'), ('f', 'field crew, on site'),
       ('o', 'call-out of operator and crew')]
ax.legend([Rectangle((0, 0), 1, 1, fc=ACTORS[k][1], ec='none') for k, _ in LEG], [t for _, t in LEG], loc='lower center',
          bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=7.5, handlelength=1.6, handleheight=0.9,
          columnspacing=1.0, handletextpad=0.5, borderaxespad=0)
save(fig, 'restoration_processes')
print('written to', os.path.abspath(OUT))
