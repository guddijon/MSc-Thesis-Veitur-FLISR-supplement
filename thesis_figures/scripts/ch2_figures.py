"""Chapter 2 illustrations (Figures 2.2, 2.3, 2.5, 2.8, 2.11, 2.12, 2.14, 2.15, 2.18, 2.19, 2.21, 2.23) in the house
style of the thesis.

Each fig_* function draws one figure; restyle() then sets the house style before the figure is saved (Figures 2.16 and
2.22 are drawn by ch2_linear_fpi.py and ch2_adms_pipeline.py, 2.4 and 2.20 by ch2_impedance_protocol_figs.py):
  fonts    Liberation Sans for text and mathematics, TrueType embedded (pdf.fonttype 42)
  sizes    every text scaled by a factor per figure and kept between 6.5 and 9.5 pt as printed at the width used in the
           thesis (width column of FIGS, inches); axis labels in regular weight
  colours  the named Matplotlib colours of the drawings mapped to the house palette (BASE); the meaning follows the other
           chapters: Direction A orange and Direction B blue (as in Chapter 6), voltage blue and current orange, fault in
           the status red of the scenario map (Figure 5.5), communication links blue as in Figure 2.20
Figure 2.23 reads the national energy forecast results workbook of 18 Feb 2026 (cited in the thesis, not included); give
its path in ORKUSPA_XLSX, otherwise 2.23 is skipped. Needs networkx (Figure 2.5), pandas and openpyxl (2.23).
Output: ../output/{thesis file name}.pdf and .png.
Run: python3 ch2_figures.py [figure numbers]"""
import os, sys, traceback
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.colors import to_rgba, to_hex

HERE = os.path.dirname(os.path.abspath(__file__)); CH = os.path.dirname(HERE)
OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE, AQUA, YELLOW, FAULT = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#b3261e'
TEXT_TONE = {BLUE: '#2265b8', ORANGE: '#c2531f', AQUA: '#14875e', YELLOW: '#9a6a00'}   # darker steps for small text
TW = 15.0 / 2.54                                                                          # text width of the thesis
RC = {'font.family': 'Liberation Sans', 'pdf.fonttype': 42, 'mathtext.fontset': 'custom',
      'mathtext.rm': 'Liberation Sans', 'mathtext.it': 'Liberation Sans:italic', 'mathtext.bf': 'Liberation Sans:bold',
      'mathtext.sf': 'Liberation Sans', 'axes.unicode_minus': True}

# default colour map (drawing colour -> house colour); fills keep their alpha
BASE = {'#000000': INK, '#1f77b4': BLUE, '#0000ff': BLUE, '#00008b': BLUE, '#d62728': ORANGE, '#ff0000': ORANGE,
        '#8b0000': ORANGE, '#008000': AQUA, '#006400': AQUA, '#800080': ORANGE, '#808080': MUTED, '#b0b0b0': GRID,
        '#cccccc': '#c8c7c2', '#d3d3d3': '#e2e1dc', '#ffd700': YELLOW, '#ffff00': YELLOW, '#ffa500': YELLOW,
        '#e6f2ff': '#eaf2fc', '#e6ffe6': '#e6f2e6', '#ffe6e6': '#fbe7df', '#f4f7f9': '#f3f2ef', '#1f497d': MUTED,
        '#002060': INK, '#333333': INK}
DIR = {'#008000': ORANGE, '#006400': ORANGE, '#ff0000': BLUE, '#8b0000': BLUE}            # Direction A green -> orange, B red -> blue
# figure: (drawing function, file name the drawing saves, thesis file name, printed width in, font factor, colour overrides,
#          text rule: function(text, colour) -> colour or None); a font factor given as (factor, minimum pt) lowers the
#          6.5 pt floor for a diagram whose boxes are sized to its text
FIGS = [
    ('2.2', 'fig_2_2', 'power_triangle_recreation', 'power_triangle', 0.6, 0.96, {}, None),
    ('2.3', 'fig_2_3', 'phasor_diagram_colored', 'phasor_diagram_colored', 0.5, 1.15, {}, None),
    ('2.5', 'fig_2_5', None, 'radial-vs-meshed', 1.0, 1.3, {}, None),
    ('2.8', 'fig_2_8', 'fault_types', 'fault_types', 0.9, 1.2, {'#ff0000': FAULT, '#008000': MUTED}, None),
    ('2.11', 'fig_2_11', 'fault_current_stages', 'fault_current_stages', 1.0, 1.15, {}, lambda t, c: INK),
    ('2.12', 'fig_2_12', 'tcc_ansi_50_51', 'tcc_ansi_50_51', 0.85, 1.1, {'#ff0000': BLUE}, lambda t, c: INK),
    ('2.14', 'fig_2_14', 'feeder_fault_paths', 'feeder_fault_paths', 1.0, 1.3,
     {'#ff0000': FAULT, '#8b0000': FAULT, '#008000': ORANGE, '#006400': ORANGE}, None),
    ('2.15', 'fig_2_15', 'compass_directions_4bay', 'compass_directions_4bay', 1.0, 1.35, DIR, None),
    ('2.18', 'fig_2_18', 'sequence_angles_comparison', 'sequence_angles_comparison', 1.0, 1.05,
     {'#008000': ORANGE, '#800080': ORANGE, '#ff0000': INK}, None),
    ('2.19', 'fig_2_19', 'sin_projection_directional', 'sin_projection_directional', 1.0, 0.92,
     dict(DIR, **{'#0000ff': INK}), None),
    ('2.21', 'fig_2_21', 'adms_network_hierarchy', 'adms_network_hierarchy', 1.0, 1.3,
     {'#006400': BLUE, '#00008b': BLUE, '#e6ffe6': '#eaf2fc', '#e6f2ff': '#d6e6f9', '#ffe6e6': '#c2daf6'},
     lambda t, c: BLUE if c in (BLUE,) else None),
    ('2.23', 'fig_2_23', 'raforkuspa_grunnspa_vs_haspa', 'raforkuspa_grunnspa_vs_haspa', 0.9, 1.05, {}, None),
]

def hx(c):
    try: return to_hex(c, keep_alpha=False).lower()
    except (ValueError, TypeError): return None

def recolour(c, cmap):
    """Mapped colour with the original alpha, or None if unchanged."""
    if c is None or (isinstance(c, str) and c == 'none'): return None
    try: rgba = to_rgba(c)
    except (ValueError, TypeError): return None
    new = cmap.get(to_hex(rgba, keep_alpha=False).lower())
    return None if new is None else to_rgba(new, rgba[3])

def restyle(fig, width_in, factor, min_pt=6.5, over=None, text_rule=None):
    cmap = dict(BASE, **(over or {}))
    fig.canvas.draw()                                                   # final size after the cell's own layout
    scale = width_in * TW / fig.get_size_inches()[0]
    lo, hi = min_pt / scale, 9.5 / scale
    for a in fig.findobj(lambda o: not isinstance(o, Text)):
        for get, setter in (('get_color', 'set_color'), ('get_facecolor', 'set_facecolor'), ('get_edgecolor', 'set_edgecolor'),
                            ('get_markerfacecolor', 'set_markerfacecolor'), ('get_markeredgecolor', 'set_markeredgecolor')):
            if not (hasattr(a, get) and hasattr(a, setter)): continue
            try: c = getattr(a, get)()
            except Exception: continue
            if hasattr(c, 'shape') and getattr(c, 'ndim', 1) == 2:     # collections: one colour per item
                new = [recolour(tuple(x), cmap) or tuple(x) for x in c]
                if any(recolour(tuple(x), cmap) for x in c): getattr(a, setter)(new)
            else:
                n = recolour(c, cmap)
                if n is not None: getattr(a, setter)(n)
    for t in fig.findobj(Text):
        ap = getattr(t, 'arrow_patch', None)                            # annotation arrows belong to their text
        for patch in ([ap] if ap is not None else []):
            for get, setter in (('get_facecolor', 'set_facecolor'), ('get_edgecolor', 'set_edgecolor')):
                n = recolour(getattr(patch, get)(), cmap)
                if n is not None: getattr(patch, setter)(n)
        if not t.get_text().strip(): continue
        t.set_fontfamily('Liberation Sans')
        t.set_fontsize(min(max(t.get_fontsize() * factor, lo), hi))
        n = recolour(t.get_color(), cmap); c = hx(n) if n is not None else hx(t.get_color())
        if text_rule:
            r = text_rule(t.get_text(), c)
            if r: c = r
        t.set_color(TEXT_TONE.get(c, c))
        bb = t.get_bbox_patch()
        if bb is not None:
            for get, setter in (('get_facecolor', 'set_facecolor'), ('get_edgecolor', 'set_edgecolor')):
                n = recolour(getattr(bb, get)(), cmap)
                if n is not None: getattr(bb, setter)(n)
    for ax in fig.axes:
        for lab in (ax.xaxis.label, ax.yaxis.label): lab.set_fontweight('normal')
        for s in ax.spines.values():
            if hx(s.get_edgecolor()) == INK: s.set_edgecolor(MUTED)

def run(fig_no, fn, own_name, name, width, factor, over, text_rule):
    if fig_no == '2.23' and not os.path.exists(os.environ.get('ORKUSPA_XLSX', '')):
        return 'skipped (set ORKUSPA_XLSX to the forecast workbook)'
    saved = []
    def savefig(self, fname, *args, **kw):                              # the drawing's own savefig: restyle, then write once
        if saved or (own_name and not str(fname).startswith(own_name)): return
        saved.append(fname); finish(self)
    def finish(f):
        restyle(f, width, *(factor if isinstance(factor, tuple) else (factor,)), over=over, text_rule=text_rule)
        for e in ('pdf', 'png'):
            orig(f, os.path.join(OUT, f'{name}.{e}'), bbox_inches='tight', dpi=300 if e == 'png' else None)
    orig = Figure.savefig; Figure.savefig = savefig; show = plt.show; plt.show = lambda *x, **k: None
    try:
        plt.close('all'); plt.rcParams.update(RC)
        globals()[fn]()
        if not saved and plt.get_fignums(): saved.append('shown'); finish(plt.gcf())   # drawing shows without saving
        return 'ok'
    except ImportError as e:
        return f'skipped ({e})'
    finally:
        Figure.savefig = orig; plt.show = show; plt.close('all')

# ------------------------------------------------------------------ drawings (geometry, text and data of each figure)
def fig_2_2():
    """Figure 2.2."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')  # Hide the axes
    ax.set_aspect('equal') # Ensure the triangle is accurately proportioned

    # Define the vertices of the right-angled triangle
    # Base = 4, Height = 3, Hypotenuse = 5
    x = [0, 4, 4, 0]
    y = [0, 0, 3, 0]

    # 1. Draw the triangle lines
    ax.plot([0, 4], [0, 0], color='black', lw=2)  # Base (Real Power)
    ax.plot([4, 4], [0, 3], color='black', lw=2)  # Height (Reactive Power)
    ax.plot([0, 4], [0, 3], color='black', lw=2)  # Hypotenuse (Apparent Power)

    # 2. Draw the angle arc with an upward-pointing arrowhead
    theta = np.arctan2(3, 4) # Calculate the angle in radians
    radius = 1.5

    # We use a FancyArrowPatch to draw the curved line with the arrow
    angle_arc = patches.FancyArrowPatch(
        (radius, 0),
        (radius * np.cos(theta), radius * np.sin(theta)),
        connectionstyle="arc3,rad=0.15", # Gives it a natural circular curve
        color="black",
        arrowstyle="-|>",
        mutation_scale=15, # Size of the arrowhead
        lw=1
    )
    ax.add_patch(angle_arc)

    # 3. Add the text annotations using Matplotlib's MathText (LaTeX formatting)

    # Inside angle text
    ax.text(2.5, 0.4, r'$(\theta)$', fontsize=18, ha='right', va='center')

    # Base: Real Power (P)
    ax.text(1.8, -0.2, r'P = VI $\cos(\theta)$ W', fontsize=18, ha='center', va='top')

    # Height: Reactive Power (Q)
    ax.text(4.3, 1.5, r'Q = VI $\sin(\theta)$ var', fontsize=18, ha='left', va='center')

    # Hypotenuse: Apparent Power (S)
    ax.text(1.2, 2.3, r'S = VI', fontsize=18, ha='center', va='bottom')
    ax.text(1.5, 1.6, r'VA', fontsize=18, ha='center', va='bottom')

    # 4. Adjust the plot limits to ensure all text fits comfortably
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-1.0, 3.5)

    # 5. Save and display the image
    plt.tight_layout()
    plt.savefig("power_triangle_recreation.png", dpi=300, bbox_inches='tight')
    plt.savefig("power_triangle_recreation.pdf", format='pdf', bbox_inches='tight') # Vector format for LaTeX
    plt.show()


def fig_2_3():
    """Figure 2.3."""
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc

    # -----------------------------
    # User settings
    # -----------------------------
    V_mag = 1.0
    I_mag = 0.75
    delta_deg = 40.0
    beta_deg = 15.0

    # Colors
    V_color = "tab:blue"
    I_color = "tab:red"
    theta_color = "black"
    axis_color = "black"

    output_png = "phasor_diagram_colored.png"
    output_pdf = "phasor_diagram_colored.pdf"

    # -----------------------------
    # Derived values
    # -----------------------------
    delta = np.deg2rad(delta_deg)
    beta = np.deg2rad(beta_deg)

    Vx, Vy = V_mag * np.cos(delta), V_mag * np.sin(delta)
    Ix, Iy = I_mag * np.cos(beta), I_mag * np.sin(beta)

    theta_deg = delta_deg - beta_deg

    # Keep the plot focused on the first quadrant, with a small margin
    r_max = 1.25 * max(V_mag, I_mag)
    x_min = -0.12 * r_max
    x_max = 1.18 * r_max
    y_min = -0.12 * r_max
    y_max = 1.18 * r_max

    # -----------------------------
    # Figure setup
    # -----------------------------
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Remove outer frame and ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # Axes through origin
    ax.axhline(0, color=axis_color, linewidth=1.2)
    ax.axvline(0, color=axis_color, linewidth=1.2)

    # Arrowheads for positive axes
    ax.annotate(
        "", xy=(x_max, 0), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", lw=1.2, color=axis_color)
    )
    ax.annotate(
        "", xy=(0, y_max), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", lw=1.2, color=axis_color)
    )

    # Axis labels
    ax.text(
        x_max * 0.98, -0.055 * r_max,
        "Re",
        ha="right", va="top", fontsize=16, color=axis_color
    )
    ax.text(
        0.05 * r_max, y_max * 0.98,
        "Im",
        ha="left", va="top", rotation=0, fontsize=16, color=axis_color
    )

    # Origin marker and label
    ax.plot(0, 0, marker="o", color=axis_color, markersize=4)
    ax.text(
        0.045 * r_max, -0.065 * r_max,
        r"$(0,0)$",
        fontsize=14, color=axis_color
    )

    # -----------------------------
    # Phasors
    # -----------------------------
    ax.annotate(
        "", xy=(Vx, Vy), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", lw=2.4, color=V_color)
    )
    ax.annotate(
        "", xy=(Ix, Iy), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", lw=2.4, linestyle="--", color=I_color)
    )

    # Phasor labels
    ax.text(
        1.05 * Vx, 1.05 * Vy,
        r"$\mathbf{V}=|V|\angle\delta$",
        fontsize=16, ha="left", va="bottom", color=V_color
    )
    ax.text(
        1.05 * Ix, 1.05 * Iy,
        r"$\mathbf{I}=|I|\angle\beta$",
        fontsize=16, ha="left", va="bottom", color=I_color
    )

    # -----------------------------
    # Angle arcs
    # -----------------------------
    # Beta arc in current color
    arc_beta = Arc(
        (0, 0),
        width=0.52 * r_max, height=0.52 * r_max,
        angle=0,
        theta1=0, theta2=beta_deg,
        lw=1.6, color=I_color
    )

    # Delta arc in voltage color
    arc_delta = Arc(
        (0, 0),
        width=0.78 * r_max, height=0.78 * r_max,
        angle=0,
        theta1=0, theta2=delta_deg,
        lw=1.6, color=V_color
    )

    # Theta arc in neutral color
    arc_theta = Arc(
        (0, 0),
        width=1.02 * r_max, height=1.02 * r_max,
        angle=0,
        theta1=beta_deg, theta2=delta_deg,
        lw=1.8, color=theta_color
    )

    ax.add_patch(arc_beta)
    ax.add_patch(arc_delta)
    ax.add_patch(arc_theta)

    # -----------------------------
    # Angle labels
    # -----------------------------
    beta_mid = np.deg2rad(beta_deg / 2.0)
    delta_mid = np.deg2rad(delta_deg / 2.0)
    theta_mid = np.deg2rad((beta_deg + delta_deg) / 2.0)

    ax.text(
        0.30 * r_max * np.cos(beta_mid),
        0.30 * r_max * np.sin(beta_mid),
        r"$\beta$",
        fontsize=18, ha="center", va="center", color=I_color
    )

    ax.text(
        0.43 * r_max * np.cos(delta_mid),
        0.43 * r_max * np.sin(delta_mid),
        r"$\delta$",
        fontsize=18, ha="center", va="center", color=V_color
    )

    ax.text(
        0.67 * r_max * np.cos(theta_mid),
        0.60 * r_max * np.sin(theta_mid),
        r"$\theta=\delta-\beta$",
        fontsize=16, ha="center", va="center", color=theta_color
    )

    

    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.savefig(output_pdf, bbox_inches="tight")
    plt.show()


def fig_2_5():
    """Figure 2.5."""
    import networkx as nx
    import matplotlib.pyplot as plt

    # Data Setup
    nodes = list(range(20))

    # Manual Node Positions (Central trunk with radiating branches)
    pos = {
        0: (0, 0),     # Root node at the very bottom
        1: (0, 0.15),  # Trunk lower point
        2: (0, 0.35),  # Trunk mid point
        3: (0, 0.55),  # Trunk upper point
        4: (0, 0.75),  # Trunk top point

        # Lower trunk branches
        5: (-0.3, 0.25),
        6: (-0.1, 0.45),
        7: (0.3, 0.25),
        8: (0.1, 0.45),

        # Mid trunk branches
        9: (-0.4, 0.5),
        10:(0.4, 0.5),

        # Upper trunk branches
        11:(-0.5, 0.7),
        12:(0.5, 0.7),
        13:(-0.2, 0.7),
        14:(0.2, 0.7),

        # Top trunk branches
        15:(-0.3, 0.85),
        16:(0.3, 0.85),
        17:(-0.1, 0.85),
        18:(0.1, 0.85),
        19:(0, 0.95),
    }

    # Tree Edges (Radial structure)
    tree_edges = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (1, 5), (1, 6), (1, 7), (1, 8),
        (2, 9), (2, 10),
        (3, 11), (3, 12), (3, 13), (3, 14),
        (4, 15), (4, 16), (4, 17), (4, 18), (4, 19)
    ]

    # Create standard NetworkX graph object for the radial tree
    G_radial = nx.Graph()
    G_radial.add_nodes_from(nodes)
    G_radial.add_edges_from(tree_edges)

    # Create standard NetworkX graph object for the meshed tree
    G_meshed = nx.Graph()
    G_meshed.add_nodes_from(nodes)

    # Additional Meshed Edges (adding cycles and cross-connections)
    meshed_edges = tree_edges + [
        (5, 7), (6, 8),
        (9, 10),
        (11, 15), (12, 16), (13, 17), (14, 18),
        (9, 6), (10, 8),
        (11, 4), (12, 4),
        (15, 17), (16, 18),
        (19, 13), (19, 14), (19, 1),
        (5, 19), (7, 19)
    ]
    G_meshed.add_edges_from(meshed_edges)

    # Drawing Function
    def draw_network_diagram(ax, G, title):
        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, width=1, edge_color='black')

        # Draw all nodes uniformly
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=50, node_color='black')

        # Add title and format axis
        ax.set_title(title, fontsize=14, y=-0.1)
        ax.set_axis_off()
        ax.set_xlim(-0.6, 0.6)
        ax.set_ylim(-0.1, 1.05)

    # Plotting
    fig, axs = plt.subplots(1, 2, figsize=(14, 7))

    # Draw subplots
    draw_network_diagram(axs[0], G_radial, "Radial")
    draw_network_diagram(axs[1], G_meshed, "Meshed")

    plt.tight_layout()
    plt.show()


def fig_2_8():
    """Figure 2.8."""
    import matplotlib.pyplot as plt

    # Set up a 2x2 grid for the four fault types
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    axes = axes.flatten()

    # Titles for the subplots
    titles = [
        "(a) Single Line-to-Ground (SLG)",
        "(b) Line-to-Line (LL)",
        "(c) Double Line-to-Ground (LLG)",
        "(d) Three-Phase (3P)"
    ]

    def draw_base_grid(ax, title):
        """Draws the three conductors and the earth line."""
        ax.set_title(title, fontsize=12, pad=10)

        # Draw conductors (L1, L2, L3)
        ax.hlines(y=[3, 2, 1], xmin=0, xmax=1, colors='black', linewidth=1.5)

        # Draw Earth line (dashed)
        ax.hlines(y=0, xmin=0, xmax=1, colors='green', linewidth=1.5, linestyles='dashed')

        # Add Labels
        ax.text(-0.05, 3, 'L1', va='center', ha='right', fontsize=12, fontweight='bold')
        ax.text(-0.05, 2, 'L2', va='center', ha='right', fontsize=12, fontweight='bold')
        ax.text(-0.05, 1, 'L3', va='center', ha='right', fontsize=12, fontweight='bold')
        ax.text(-0.05, 0, 'Earth', va='center', ha='right', fontsize=12, color='green', style='italic')

        # Clean up axes
        ax.set_xlim(-0.15, 1.1)
        ax.set_ylim(-0.5, 3.5)
        ax.axis('off')

    # --- Plot (a): SLG (L1 to Ground) ---
    draw_base_grid(axes[0], titles[0])
    # Fault line from L1 (y=3) to Earth (y=0)
    axes[0].plot([0.5, 0.5], [3, 0], color='red', linewidth=3, zorder=5)
    # Connection dots
    axes[0].scatter([0.5, 0.5], [3, 0], color='red', s=80, zorder=6)

    # --- Plot (b): LL (L1 to L2) ---
    draw_base_grid(axes[1], titles[1])
    # Fault line from L1 (y=3) to L2 (y=2)
    axes[1].plot([0.5, 0.5], [3, 2], color='red', linewidth=3, zorder=5)
    # Connection dots
    axes[1].scatter([0.5, 0.5], [3, 2], color='red', s=80, zorder=6)

    # --- Plot (c): LLG (L1 and L2 to Ground) ---
    draw_base_grid(axes[2], titles[2])
    # Fault line connecting L1, L2, and Earth
    axes[2].plot([0.5, 0.5], [3, 0], color='red', linewidth=3, zorder=5)
    # Connection dots at L1, L2, and Earth
    axes[2].scatter([0.5, 0.5, 0.5], [3, 2, 0], color='red', s=80, zorder=6)

    # --- Plot (d): 3P (L1, L2, L3 shorted) ---
    draw_base_grid(axes[3], titles[3])
    # Fault line connecting L1, L2, and L3
    axes[3].plot([0.5, 0.5], [3, 1], color='red', linewidth=3, zorder=5)
    # Connection dots at L1, L2, and L3
    axes[3].scatter([0.5, 0.5, 0.5], [3, 2, 1], color='red', s=80, zorder=6)

    plt.tight_layout()
    plt.savefig('fault_types.png', dpi=300, bbox_inches='tight')


def fig_2_11():
    """Figure 2.11."""
    import numpy as np
    import matplotlib.pyplot as plt

    def draw_fault_current_stages():
        # A standard textbook textbook aesthetic with larger, more legible text.
        # Figure size
        fig, ax = plt.subplots(figsize=(14, 6))

        # Time vector (0 to 0.5 seconds)
        t = np.linspace(0, 0.5, 1000)
        f = 50  # 50 Hz system (standard for Iceland/Veitur)
        w = 2 * np.pi * f

        # Fault Current Parameters (Magnitudes and Time Constants)
        # Data
        I_ss = 1.0       # Steady-state current magnitude
        I_trans = 2.5    # Transient current magnitude
        I_sub = 5.0      # Subtransient current magnitude
        T_sub = 0.03     # Subtransient time constant (seconds)
        T_trans = 0.15   # Transient time constant (seconds)

        # Calculate the decaying envelope
        envelope = (I_sub - I_trans) * np.exp(-t / T_sub) + \
                   (I_trans - I_ss) * np.exp(-t / T_trans) + I_ss

        # Calculate the oscillating fault current
        i_t = envelope * np.sin(w * t)

        # ----------------------------------------------------
        # Plot Waveforms
        # ----------------------------------------------------
        ax.plot(t, i_t, color='darkblue', linewidth=1.5, zorder=3)
        # Red
        ax.plot(t, envelope, color='red', linestyle='--', linewidth=2, zorder=4)
        ax.plot(t, -envelope, color='red', linestyle='--', linewidth=2, zorder=4)

        # ----------------------------------------------------
        # Define and Shade the Three Distinct Stages
        # ----------------------------------------------------
        t_sub_end = 0.06   # ~3 cycles
        t_trans_end = 0.25 # ~12.5 cycles

        # Text vertical offset from the top border for all region labels
        # Position adjusted slightly for larger text.
        y_text_pos = 5.7  # Increased from 5.5 to 5.7 for space

        # Subtransient region (red)
        ax.axvspan(0, t_sub_end, color='red', alpha=0.08, zorder=1)
        ax.text(t_sub_end / 2, y_text_pos, 'Subtransient\nPeriod', ha='center', va='bottom',
                fontweight='bold', fontsize=16, color='darkred') # Increased fontsize to 16

        # Transient region (orange)
        ax.axvspan(t_sub_end, t_trans_end, color='orange', alpha=0.08, zorder=1)
        ax.text((t_sub_end + t_trans_end) / 2, y_text_pos, 'Transient\nPeriod', ha='center', va='bottom',
                fontweight='bold', fontsize=16, color='darkblue') # Increased fontsize to 16

        # Steady-state region (green)
        ax.axvspan(t_trans_end, 0.5, color='green', alpha=0.08, zorder=1)
        ax.text((t_trans_end + 0.5) / 2, y_text_pos, 'Steady-State\nPeriod', ha='center', va='bottom',
                fontweight='bold', fontsize=16, color='darkgreen') # Increased fontsize to 16

        # Vertical Dividers
        # Using zorder to place behind the text for better textbook aesthetic.
        ax.axvline(t_sub_end, color='black', linestyle=':', linewidth=1.5, zorder=2)
        ax.axvline(t_trans_end, color='black', linestyle=':', linewidth=1.5, zorder=2)

        # ----------------------------------------------------
        # Annotate the Envelope Components
        # ----------------------------------------------------
        # Positions are adjusted slightly to avoid clashing with larger text.
        ax.annotate(r'$I^{\prime\prime}$ (Subtransient Peak)', xy=(0.01, envelope[10]), xytext=(0.06, 4.6),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=6),
                    fontsize=18, fontweight='bold') # Increased fontsize to 16

        ax.annotate(r'$I^{\prime}$ (Transient)', xy=(0.1, 2.3), xytext=(0.15, 3.1),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=6),
                    fontsize=18, fontweight='bold') # Increased fontsize to 16

        ax.annotate(r'$I_{ss}$ (Steady-State)', xy=(0.4, 1.0), xytext=(0.4, 2.1),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=6),
                    fontsize=18, fontweight='bold', ha='center') # Increased fontsize to 16

        # ----------------------------------------------------
        # Formatting
        # ----------------------------------------------------
        ax.set_xlim(0, 0.5)
        # y limit slightly increased to accommodate larger region text.
        ax.set_ylim(-5.5, 6.7) # Increased y_max to 6.7 for space

        # Clean up axes for a professional textbook look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Place bottom and left axes through origin.
        ax.spines['bottom'].set_position('zero')
        ax.spines['left'].set_position('zero')

        # x ticks
        ax.set_xticks([0.1, 0.2, 0.3, 0.4, 0.5])
        # Define and scale xticklabels.
        ax.set_xticklabels(['0.1s', '0.2s', '0.3s', '0.4s', '0.5s'], fontsize=15) # Increased fontsize to 14

        # Hide y-ticks to keep it conceptual/general
        ax.set_yticks([])

        # The generic functional description handles the rest.
        plt.tight_layout()

        # The functional description requires returning a static visual, so we display the plot.
        # Output file
        plt.savefig('fault_current_stages.png', dpi=300, bbox_inches='tight')
        # In a widget context, we'd typically use plt.show(), but this script
        # is intended for execution to save an image.

    draw_fault_current_stages()


def fig_2_12():
    """Figure 2.12."""
    import numpy as np
    import matplotlib.pyplot as plt

    def draw_time_current_curve():
        fig, ax = plt.subplots(figsize=(10, 8))

        # ----------------------------------------------------
        # Define Relay Parameters
        # ----------------------------------------------------
        I_pickup_51 = 200.0     # 51 Element Pickup Current (Amps)
        TDS = 1.0               # Time Dial Setting
        I_inst_50 = 2000.0      # 50 Element Instantaneous Pickup (Amps)
        t_inst = 0.02           # Instantaneous mechanical clearing time (Seconds)

        # Create current array for the x-axis (logarithmic spacing)
        I = np.logspace(np.log10(I_pickup_51 * 1.01), np.log10(10000), 1000)

        # IEC Standard Inverse Curve Formula
        # t = TDS * (0.14 / ((I / I_pickup)^0.02 - 1))
        t_51 = TDS * (0.14 / ((I / I_pickup_51)**0.02 - 1))

        # Apply the 50 Instantaneous cutoff
        # If the current is greater than I_inst_50, the time drops to t_inst
        t_combined = np.where(I >= I_inst_50, t_inst, t_51)

        # ----------------------------------------------------
        # Plotting
        # ----------------------------------------------------
        # Plot the combined relay curve
        ax.loglog(I, t_combined, color='red', linewidth=2.5, label='Relay Trip Characteristic')

        # Plot the hidden continuation of the 51 curve (for educational illustration)
        ax.loglog(I[I >= I_inst_50], t_51[I >= I_inst_50], color='red', linestyle='--', alpha=0.4,
                  label='51 Inverse Curve (Bypassed by 50)')

        # ----------------------------------------------------
        # Annotations
        # ----------------------------------------------------
        # 51 Region
        ax.text(400, 2, 'ANSI 51 Element\n(Inverse Time)', ha='center', va='center',
                fontsize=12, fontweight='bold', color='darkred')

        # 50 Region
        ax.text(4000, 0.05, 'ANSI 50 Element\n(Instantaneous)', ha='center', va='bottom',
                fontsize=12, fontweight='bold', color='darkred')

        # Highlight the Instantaneous Pickup Point
        ax.axvline(I_inst_50, color='gray', linestyle=':', linewidth=1.5)
        # FIX: Raised the y-coordinate from 0.01 to 0.015 to prevent x-axis overlap
        ax.annotate(r'$I_{inst}$ Pickup', xy=(I_inst_50, t_inst), xytext=(I_inst_50 * 0.6, 0.015),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                    ha='right', va='center', fontsize=16, fontweight='bold')

        # Highlight the 51 Pickup Point
        ax.axvline(I_pickup_51, color='gray', linestyle=':', linewidth=1.5)
        ax.text(I_pickup_51 * 0.9, 50, r'$I_{pickup}$', ha='right', va='center',
                fontsize=16, fontweight='bold', rotation=90)

        # ----------------------------------------------------
        # Formatting (Standard Log-Log TCC Style)
        # ----------------------------------------------------
        ax.set_xlim(100, 10000)
        ax.set_ylim(0.01, 100)

        ax.set_xlabel('Current (Amperes)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Time (Seconds)', fontsize=14, fontweight='bold')
        ax.set_title('Time-Current Characteristic Curve (ANSI 50/51)', fontsize=16, pad=15, fontweight='bold')

        ax.grid(True, which="both", ls="--", alpha=0.7)
        ax.legend(loc='upper right', fontsize=14, framealpha=1)

        plt.tight_layout()
        plt.savefig('tcc_ansi_50_51.png', dpi=300, bbox_inches='tight')

    draw_time_current_curve()


def fig_2_14():
    """Figure 2.14."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    def draw_base_feeder(ax, title):
        """Draws the primary substation, feeder line segments, distribution substations, and FPIs."""
        ax.set_title(title, fontsize=18, pad=15, fontweight='bold')

        # Primary Substation (Source)
        ax.add_patch(patches.Rectangle((0, 4), 1.5, 2, facecolor='lightgray', edgecolor='black', lw=2))
        ax.text(0.75, 5, 'Primary\nSub.\n(Source)', ha='center', va='center', fontweight='bold', fontsize=14)

        # Main 11 kV Feeder Line (Drawn in segments so it does not pass through the substations)
        # Segment 1: Source to Sub 1
        ax.plot([1.5, 3.5], [5, 5], color='black', linewidth=3)
        # Segment 2: Sub 1 to Sub 2
        ax.plot([4.5, 7.5], [5, 5], color='black', linewidth=3)
        # Segment 3: Sub 2 to downstream
        ax.plot([8.5, 11], [5, 5], color='black', linewidth=3)

        # Distribution Substation 1
        ax.add_patch(patches.Rectangle((3.5, 4.5), 1, 1, facecolor='white', edgecolor='black', lw=2))
        ax.text(4, 5, 'Dist.\nSub 1', ha='center', va='center', fontsize=12, fontweight='bold')

        # Distribution Substation 2
        ax.add_patch(patches.Rectangle((7.5, 4.5), 1, 1, facecolor='white', edgecolor='black', lw=2))
        ax.text(8, 5, 'Dist.\nSub 2', ha='center', va='center', fontsize=12, fontweight='bold')

        # Downstream Network (Rest of Mesh)
        ax.plot([11, 11.5], [5, 5], color='black', linewidth=3, linestyle='--')
        ax.text(11.5, 5, 'To Rest of\nNetwork', ha='left', va='center', style='italic', fontsize=14)

    def draw_fpis(ax, fault_type):
        """Draws the ComPass FPIs and colors them based on the fault type."""
        # FPI locations: Left of Sub 1, Right of Sub 1, Left of Sub 2, Right of Sub 2
        fpi_x = [3.0, 4.7, 7.0, 8.7]

        for i, x in enumerate(fpi_x):
            # Base FPI box
            rect = patches.Rectangle((x, 4.75), 0.3, 0.5, facecolor='white', edgecolor='black', lw=1.5, zorder=3)
            ax.add_patch(rect)
            ax.text(x + 0.15, 4.4, 'FPI', ha='center', va='top', fontsize=12, fontweight='bold')

            # Color logic based on fault type and position (Fault is at x=6)
            if fault_type == 'Short':
                if x < 6: # Upstream sees massive forward current
                    ax.annotate('', xy=(x+0.4, 5.5), xytext=(x-0.1, 5.5), arrowprops=dict(facecolor='red', shrink=0, width=2, headwidth=6))
                else: # Downstream sees nothing
                    pass

            elif fault_type == 'Earth':
                if x < 6: # Upstream sees forward capacitive current
                    ax.annotate('', xy=(x+0.4, 5.5), xytext=(x-0.1, 5.5), arrowprops=dict(facecolor='blue', shrink=0, width=2, headwidth=6))
                else: # Downstream sees REVERSE capacitive current
                    ax.annotate('', xy=(x-0.1, 5.5), xytext=(x+0.4, 5.5), arrowprops=dict(facecolor='green', shrink=0, width=2, headwidth=6))

    def draw_fault(ax, x, y):
        """Draws a lightning bolt symbol for the fault."""
        bolt_x = [x, x-0.2, x+0.1, x-0.1, x+0.2, x]
        bolt_y = [y+1, y+0.4, y+0.4, y-0.2, y-0.2, y-1]
        ax.plot(bolt_x, bolt_y, color='gold', linewidth=2, zorder=4)
        ax.fill(bolt_x, bolt_y, color='yellow', zorder=4)

    # Create Figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # ---------------------------------------------------------
    # Panel A: Phase-to-Phase Short Circuit
    # ---------------------------------------------------------
    draw_base_feeder(ax1, "(a) Phase-to-Phase Short Circuit Current Path")
    draw_fpis(ax1, 'Short')
    draw_fault(ax1, 6, 5)

    # Current Arrows (Short Circuit)
    ax1.annotate('', xy=(5.5, 5.8), xytext=(1.5, 5.8),
                 arrowprops=dict(facecolor='red', edgecolor='darkred', shrink=0.05, width=4, headwidth=10))
    ax1.text(3.5, 6.1, 'Active Fault Current (Forward)', ha='center', va='bottom', color='darkred', fontweight='bold', fontsize=14)

    ax1.annotate('', xy=(1.5, 4.2), xytext=(5.5, 4.2),
                 arrowprops=dict(facecolor='red', edgecolor='darkred', shrink=0.05, width=4, headwidth=10))
    ax1.text(3.5, 3.9, 'Active Return Current (via 2nd Phase)', ha='center', va='top', color='darkred', fontweight='bold', fontsize=14)

    ax1.set_xlim(-0.5, 13.5)
    ax1.set_ylim(3, 7)
    ax1.axis('off')

    # ---------------------------------------------------------
    # Panel B: Single-Phase Earth Fault (Isolated Delta)
    # ---------------------------------------------------------
    draw_base_feeder(ax2, "(b) Isolated Delta Earth-Fault Capacitive Current Paths")
    draw_fpis(ax2, 'Earth')
    draw_fault(ax2, 6, 5)

    # Current Arrows (Earth Fault - Source Side)
    ax2.annotate('', xy=(5.5, 5.8), xytext=(1.5, 5.8),
                 arrowprops=dict(facecolor='blue', edgecolor='darkblue', shrink=0.05, width=3, headwidth=8))
    ax2.text(3.5, 6.1, 'Capacitive Current (Downstream)', ha='center', va='bottom', color='darkblue', fontweight='bold', fontsize=14)

    # Current Arrows (Earth Fault - Downstream Side)
    ax2.annotate('', xy=(6.5, 5.8), xytext=(11.5, 5.8),
                 arrowprops=dict(facecolor='green', edgecolor='darkgreen', shrink=0.05, width=3, headwidth=8))
    ax2.text(9, 6.1, 'Capacitive Current (Upstream)', ha='center', va='bottom', color='darkgreen', fontweight='bold', fontsize=14)

    ax2.set_xlim(-0.5, 13.5)
    ax2.set_ylim(3, 7)
    ax2.axis('off')

    plt.tight_layout()
    plt.savefig('feeder_fault_paths.png', dpi=300, bbox_inches='tight')


def fig_2_15():
    """Figure 2.15."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    def draw_4bay_direction_diagram():
        # Widened the figure to accommodate 4 bays side-by-side
        fig, ax = plt.subplots(figsize=(15, 8)) # Increased figsize from (14, 7) to (15, 8)

        # Draw Common Busbar (Top)
        ax.hlines(8, 1, 17, color='black', linewidth=6)
        ax.text(9, 8.5, '11 kV Distribution Substation Busbar', ha='center', va='center', fontsize=20, fontweight='bold') # Increased from 16 to 20

        # X-coordinates for the center of each of the 4 bays
        bay_centers = [3, 7, 11, 15]

        for i, x in enumerate(bay_centers):
            # -----------------------------------------------------
            # Draw Bay / Feeder Line in SEGMENTS (avoids passing through boxes)
            # -----------------------------------------------------
            # Top segment (Busbar down to Switch)
            ax.vlines(x, 7.3, 8, color='gray', linewidth=4)
            # Middle segment (Switch down to CTs & VTs)
            ax.vlines(x, 5.5, 6.5, color='gray', linewidth=4)
            # Bottom segment (CTs & VTs down to Outgoing Cable)
            ax.vlines(x, 1, 4.5, color='gray', linewidth=4)

            # -----------------------------------------------------
            # Draw Circuit Breaker / Switch Box (Symbolic)
            # -----------------------------------------------------
            ax.add_patch(patches.Rectangle((x - 0.5, 6.5), 1, 0.8, facecolor='white', edgecolor='black', lw=2, zorder=3))
            ax.plot([x - 0.5, x + 0.5], [6.5, 7.3], color='black', lw=2, zorder=4) # Switch symbol diagonal line

            # -----------------------------------------------------
            # Draw ComPass Sensors Box (CTs & VTs)
            # -----------------------------------------------------
            ax.add_patch(patches.Rectangle((x - 0.9, 4.5), 1.8, 1, facecolor='#e6f2ff', edgecolor='black', lw=2, zorder=3)) # Increased width slightly for text
            ax.text(x, 5, 'CTs & VTs', ha='center', va='center', fontweight='bold', fontsize=14, zorder=4) # Increased from default 10 to 14

            # -----------------------------------------------------
            # Draw Directional Arrows
            # -----------------------------------------------------
            # Shifted slightly further left to accommodate larger text
            # Direction A Arrow (Up to Busbar)
            ax.annotate('', xy=(x - 1.2, 7.5), xytext=(x - 1.2, 5.8),
                        arrowprops=dict(facecolor='green', shrink=0.05, width=4, headwidth=12))

            # Direction B Arrow (Down to Cable)
            ax.annotate('', xy=(x - 1.2, 2.5), xytext=(x - 1.2, 4.2),
                        arrowprops=dict(facecolor='red', shrink=0.05, width=4, headwidth=12))

            # -----------------------------------------------------
            # Add Labels (Full text on first bay, abbreviated on others to prevent clutter)
            # -----------------------------------------------------
            if i == 0:
                ax.text(x - 1.4, 6.65, 'Dir A\n(Towards Busbar)', ha='right', va='center', color='green', fontsize=14, fontweight='bold') # 11 -> 14
                ax.text(x - 1.4, 3.35, 'Dir B\n(Away along Cable)', ha='right', va='center', color='red', fontsize=14, fontweight='bold') # 11 -> 14
            else:
                ax.text(x - 1.4, 6.65, 'Dir A', ha='right', va='center', color='green', fontsize=14, fontweight='bold') # 10 -> 14
                ax.text(x - 1.4, 3.35, 'Dir B', ha='right', va='center', color='red', fontsize=14, fontweight='bold') # 10 -> 14

            # Outgoing Cable Label at the bottom
            ax.text(x, 0.5, f'Outgoing 11 kV\nFeeder {i+1}', ha='center', va='center', fontsize=14, fontweight='bold') # 11 -> 14

        # Formatting the plot
        ax.set_xlim(-0.5, 18) # Shifted left limit to accommodate the larger text on the first bay
        ax.set_ylim(0, 9.5) # Increased top limit to accommodate larger title/busbar text
        ax.axis('off')
        plt.tight_layout()

        # Save the figure
        plt.savefig('compass_directions_4bay.png', dpi=300, bbox_inches='tight')
        plt.show()

    # Execute the function
    draw_4bay_direction_diagram()


def fig_2_18():
    """Figure 2.18."""
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Arc

    # Set up the figure for side-by-side plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7)) # Increased figsize from (14, 6) to (15, 7)

    def setup_theoretical_axes(ax, title, x_limits, y_limits):
        """Formats axes to look like a textbook theoretical plane."""
        ax.axhline(0, color='black', linewidth=1.2, zorder=1)
        ax.axvline(0, color='black', linewidth=1.2, zorder=1)

        # Axis End Markers (Re and Im)
        ax.text(x_limits[1] - 0.1, 0.05, 'Re', fontsize=16, style='italic') # 12 -> 16
        ax.text(0.05, y_limits[1] - 0.1, 'Im', fontsize=16, style='italic') # 12 -> 16

        ax.set_xlim(x_limits)
        ax.set_ylim(y_limits)
        ax.set_aspect('equal')

        # Remove grid, tick marks, and outer box
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_title(title, fontsize=18, pad=20, fontweight='bold') # 14 -> 18

    # ----------------------------------------------------
    # Panel A: Positive-Sequence Domain (Load Power Factor)
    # ----------------------------------------------------
    setup_theoretical_axes(ax1, '(a) Positive-Sequence Domain', [-0.2, 1.2], [-0.8, 0.6])

    # V1 Vector (Reference) - Shortened to prevent overlap with "Re"
    ax1.quiver(0, 0, 0.85, 0, angles='xy', scale_units='xy', scale=1, color='blue', width=0.008)
    ax1.text(0.85, 0.08, r'$\mathbf{V}_1$', fontsize=18, color='blue') # 14 -> 18

    # I1 Vector (Lagging Load)
    theta = np.deg2rad(-35)
    i1_mag = 0.8
    ix1 = i1_mag * np.cos(theta)
    iy1 = i1_mag * np.sin(theta)
    ax1.quiver(0, 0, ix1, iy1, angles='xy', scale_units='xy', scale=1, color='green', width=0.008)
    ax1.text(ix1 + 0.05, iy1 - 0.1, r'$\mathbf{I}_1$', fontsize=18, color='green') # 14 -> 18

    # Theta Angle Arc
    arc1 = Arc((0, 0), 0.5, 0.5, angle=0, theta1=-35, theta2=0, color='black', linewidth=1.5)
    ax1.add_patch(arc1)
    ax1.text(0.3, -0.12, r'$\theta$', fontsize=18) # 14 -> 18

    # ----------------------------------------------------
    # Panel B: Zero-Sequence Domain (Fault Direction Projection)
    # ----------------------------------------------------
    setup_theoretical_axes(ax2, '(b) Zero-Sequence Domain', [-0.55, 1.2], [-0.2, 1.2]) # Extended left limit for projection text

    # 3V0 Vector (Reference)
    ax2.quiver(0, 0, 1.0, 0, angles='xy', scale_units='xy', scale=1, color='blue', width=0.008)
    ax2.text(1.05, -0.08, r'$3\mathbf{V}_0$', fontsize=18, color='blue') # 14 -> 18

    # 3I0 Vector (Capacitive Fault Current)
    phi = np.deg2rad(70)
    i0_mag = 0.95
    ix0 = i0_mag * np.cos(phi)
    iy0 = i0_mag * np.sin(phi)
    ax2.quiver(0, 0, ix0, iy0, angles='xy', scale_units='xy', scale=1, color='purple', width=0.008)
    ax2.text(ix0 + 0.05, iy0 + 0.05, r'$3\mathbf{I}_0$', fontsize=18, color='purple') # 14 -> 18

    # Phi Angle Arc
    arc2 = Arc((0, 0), 0.4, 0.4, angle=0, theta1=0, theta2=70, color='black', linewidth=1.5)
    ax2.add_patch(arc2)
    ax2.text(0.25, 0.15, r'$\varphi$', fontsize=18) # 14 -> 18

    # Geometric Projection onto Imaginary Axis
    ax2.plot([ix0, 0], [iy0, iy0], color='purple', linestyle='--', linewidth=1.5)
    # Highlight the projection length on the y-axis
    ax2.plot([0, 0], [0, iy0], color='purple', linewidth=4, alpha=0.5)
    # Adjusted position slightly left for the larger text
    ax2.text(-0.55, iy0/2, r'$|3\mathbf{I}_0| \sin(\varphi)$', fontsize=16, color='purple', fontweight='bold') # 12 -> 16

    # Relay Threshold Setting (I_set,Q)
    iset = 0.45
    ax2.plot([-0.1, 1.1], [iset, iset], color='red', linestyle='-.', linewidth=2)
    ax2.text(0.5, iset + 0.05, r'$I_{set, Q}$ Threshold', fontsize=14, color='red', fontweight='bold') # 12 -> 14, moved left to fit

    plt.tight_layout()
    plt.savefig('sequence_angles_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()


def fig_2_19():
    """Figure 2.19."""
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Arc

    def draw_directional_projection():
        fig, ax = plt.subplots(figsize=(9, 9))

        # Clean textbook axes
        ax.axhline(0, color='black', linewidth=1.2, zorder=2)
        ax.axvline(0, color='black', linewidth=1.2, zorder=2)
        ax.text(1.15, 0.05, 'Re', fontsize=12, style='italic')
        ax.text(0.05, 1.15, 'Im', fontsize=12, style='italic')

        ax.set_xlim(-1.2, 1.3)
        ax.set_ylim(-1.2, 1.3)
        ax.set_aspect('equal')
        ax.axis('off')

        # ----------------------------------------------------
        # Shade Directional Regions
        # ----------------------------------------------------
        # Forward Region (Direction A) - Upper Half Plane
        ax.fill_between([-1.2, 1.3], 0, 1.3, color='green', alpha=0.08, zorder=1)
        ax.text(-1.1, 1.1, 'Forward Fault Region\n(Direction A)', color='darkgreen', fontweight='bold', fontsize=13)

        # Reverse Region (Direction B) - Lower Half Plane
        ax.fill_between([-1.2, 1.3], -1.3, 0, color='red', alpha=0.08, zorder=1)
        ax.text(-1.1, -1.1, 'Reverse Fault Region\n(Direction B)', color='darkred', fontweight='bold', fontsize=13)

        # ----------------------------------------------------
        # Plot Vectors
        # ----------------------------------------------------
        # Reference Vector (3V0)
        ax.quiver(0, 0, 1.0, 0, angles='xy', scale_units='xy', scale=1, color='blue', width=0.008, zorder=3)
        ax.text(1.05, -0.08, r'$3\mathbf{V}_0$', fontsize=16, color='blue', fontweight='bold')

        # Vector 1: Forward Fault (3I0_fwd)
        phi_f = np.deg2rad(65)
        mag_f = 0.95
        ix_f, iy_f = mag_f * np.cos(phi_f), mag_f * np.sin(phi_f)
        ax.quiver(0, 0, ix_f, iy_f, angles='xy', scale_units='xy', scale=1, color='darkgreen', width=0.008, zorder=3)
        ax.text(ix_f + 0.05, iy_f, r'$3\mathbf{I}_{0, fwd}$', fontsize=15, color='darkgreen')

        # Vector 2: Reverse Fault (3I0_rev)
        phi_r = np.deg2rad(-115)
        mag_r = 0.85
        ix_r, iy_r = mag_r * np.cos(phi_r), mag_r * np.sin(phi_r)
        ax.quiver(0, 0, ix_r, iy_r, angles='xy', scale_units='xy', scale=1, color='darkred', width=0.008, zorder=3)
        ax.text(ix_r - 0.05, iy_r - 0.05, r'$3\mathbf{I}_{0, rev}$', fontsize=15, color='darkred', ha='right')

        # ----------------------------------------------------
        # Draw Geometric Projections (sin(phi) components)
        # ----------------------------------------------------
        # Forward Projection (Shifted to the left side of the y-axis)
        ax.plot([ix_f, 0], [iy_f, iy_f], color='darkgreen', linestyle='--', linewidth=1.5, zorder=3)
        ax.plot([0, 0], [0, iy_f], color='darkgreen', linewidth=5, alpha=0.6, zorder=4)
        ax.text(-0.05, iy_f / 2, r'$+|3\mathbf{I}_0|\sin(\varphi_{fwd})$', color='darkgreen', fontsize=14, fontweight='bold', ha='right', va='center')

        # Reverse Projection (Shifted to the right side of the y-axis, and moved down slightly)
        ax.plot([ix_r, 0], [iy_r, iy_r], color='darkred', linestyle='--', linewidth=1.5, zorder=3)
        ax.plot([0, 0], [0, iy_r], color='darkred', linewidth=5, alpha=0.6, zorder=4)
        ax.text(0.05, -0.65, r'$-|3\mathbf{I}_0|\sin(\varphi_{rev})$', color='darkred', fontsize=14, fontweight='bold', ha='left', va='center')

        # ----------------------------------------------------
        # Draw Relay Thresholds (I_set,Q)
        # ----------------------------------------------------
        iset = 0.35
        ax.axhline(iset, color='black', linestyle='-.', linewidth=1.5, zorder=2)
        ax.text(0.8, iset + 0.03, r'$+I_{set,Q}$ Threshold', fontsize=11, fontweight='bold')

        ax.axhline(-iset, color='black', linestyle='-.', linewidth=1.5, zorder=2)
        ax.text(0.8, -iset - 0.08, r'$-I_{set,Q}$ Threshold', fontsize=11, fontweight='bold')

        # ----------------------------------------------------
        # Draw Angles
        # ----------------------------------------------------
        arc_f = Arc((0, 0), 0.4, 0.4, angle=0, theta1=0, theta2=65, color='darkgreen', linewidth=1.5, zorder=3)
        ax.add_patch(arc_f)
        ax.text(0.25, 0.12, r'$\varphi_{fwd}$', color='darkgreen', fontsize=14)

        arc_r = Arc((0, 0), 0.3, 0.3, angle=0, theta1=-115, theta2=0, color='darkred', linewidth=1.5, zorder=3)
        ax.add_patch(arc_r)
        # Shifted to the right to avoid the red phasor vector
        ax.text(0.12, -0.22, r'$\varphi_{rev}$', color='darkred', fontsize=14)

        # Title
        plt.tight_layout()

        plt.savefig('sin_projection_directional.png', dpi=300, bbox_inches='tight')

    draw_directional_projection()


def fig_2_21():
    """Figure 2.21."""
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    def draw_adms_network_hierarchy():
        fig, ax = plt.subplots(figsize=(16, 9))

        box_args = dict(edgecolor='black', lw=2, zorder=3)

        # ----------------------------------------------------
        # Level 1: ADMS (The Central Brain)
        # ----------------------------------------------------
        adms_x, adms_y = 8, 7.5
        ax.add_patch(patches.Rectangle((adms_x - 2.5, adms_y - 0.75), 5, 1.5, facecolor='#ffe6e6', **box_args))
        ax.text(adms_x, adms_y, 'Veitur ADMS / SCADA\n(Central Control)',
                ha='center', va='center', fontweight='bold', fontsize=16)

        # ----------------------------------------------------
        # Level 2: RTUs (Substation Gateways)
        # ----------------------------------------------------
        rtu_centers = [2, 6, 10, 14]
        rtu_y = 4.5

        for i, cx in enumerate(rtu_centers):
            # Draw RTU Box
            ax.add_patch(patches.Rectangle((cx - 1.3, rtu_y - 0.6), 2.6, 1.2, facecolor='#e6f2ff', **box_args))
            ax.text(cx, rtu_y, f'Dist. Substation {i+1} \nRTU',
                    ha='center', va='center', fontweight='bold', fontsize=14)

            # Draw DNP3 Connection (ADMS to RTU)
            ax.plot([adms_x, cx], [adms_y - 0.75, rtu_y + 0.6], color='darkblue', lw=2, zorder=1)

            # ----------------------------------------------------
            # Level 3: ComPass FPIs (Field Devices)
            # ----------------------------------------------------
            compass_x_offsets = [-0.9, 0, 0.9]
            compass_y = 1.5

            # Draw RS-485 Bus Line (Horizontal drop from RTU)
            bus_y = 2.8
            ax.plot([cx, cx], [rtu_y - 0.6, bus_y], color='darkgreen', lw=2, zorder=1)
            ax.plot([cx - 0.9, cx + 0.9], [bus_y, bus_y], color='darkgreen', lw=2, zorder=1)

            # Label the Modbus Bus (Applied to all branches)
            # The bbox (bounding box) with a white facecolor prevents the green line from bleeding through the text
            ax.text(cx, bus_y + 0.55, 'RS-485 Modbus', ha='center', va='center',
                    color='darkgreen', fontsize=16, fontweight='bold', style='italic',
                    bbox=dict(facecolor='white', edgecolor='none', pad=2))

            for offset in compass_x_offsets:
                comp_x = cx + offset

                # Draw ComPass Box (Wider, but same height)
                ax.add_patch(patches.Rectangle((comp_x - 0.4, compass_y - 0.9), 0.8, 1.8, facecolor='#e6ffe6', **box_args))

                # Draw vertical text. Removed the newline \n so it prints as one continuous line
                ax.text(comp_x, compass_y, 'ComPass', ha='center', va='center',
                        fontweight='bold', fontsize=16, rotation='vertical')

                # Draw Drop line from Bus to ComPass
                ax.plot([comp_x, comp_x], [bus_y, compass_y + 0.9], color='darkgreen', lw=2, zorder=1)

        # Label the Wide Area Network
        ax.text(8, 5.8, 'Wide Area Network (SDNP3 Protocol via TCP/IP)',
                ha='center', va='center', color='darkblue', fontsize=18, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', pad=2))

        # Formatting
        ax.set_xlim(-0.5, 16.5)
        ax.set_ylim(0, 9)
        ax.axis('off')
        plt.tight_layout()

        plt.savefig('adms_network_hierarchy.png', dpi=300, bbox_inches='tight')

    draw_adms_network_hierarchy()


def fig_2_23():
    """Figure 2.23."""
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    # Your exact path to the Excel file
    file_name = os.environ['ORKUSPA_XLSX']                   # national energy forecast results workbook, 18 Feb 2026

    # Use read_excel instead of read_csv, and specify the sheet name 'Almenn raforka'
    df_almenn = pd.read_excel(file_name, sheet_name='Almenn raforka', skiprows=3)

    # Extract the relevant columns for the 20-year projection
    df_plot = df_almenn[['Ár', 'Orkukaup', 'Orkukaup.1']].copy()

    # Clean the data: drop rows containing string artifacts and convert to numeric
    df_plot = df_plot[df_plot['Ár'].astype(str).str.isnumeric()]
    df_plot['Ár'] = df_plot['Ár'].astype(int)
    df_plot['Orkukaup'] = pd.to_numeric(df_plot['Orkukaup'], errors='coerce') / 1000  # Convert GWh to TWh
    df_plot['Orkukaup.1'] = pd.to_numeric(df_plot['Orkukaup.1'], errors='coerce') / 1000

    # Filter to the 20-year horizon (2025 to 2046)
    df_plot = df_plot[(df_plot['Ár'] >= 2025) & (df_plot['Ár'] <= 2046)]

    # Plotting the data
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df_plot['Ár'], df_plot['Orkukaup'], label='Grunnspá (Base Forecast)', color='blue', linewidth=2.5, linestyle='-')
    ax.plot(df_plot['Ár'], df_plot['Orkukaup.1'], label='Háspá (High Forecast)', color='red', linewidth=2.5, linestyle='--')

    # Fill the uncertainty gap between the two forecasts
    ax.fill_between(df_plot['Ár'], df_plot['Orkukaup'], df_plot['Orkukaup.1'], color='gray', alpha=0.15, label='Demand Uncertainty Gap')

    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Gross Consumption (TWh)', fontsize=14, fontweight='bold')
    ax.set_xlim(2025, 2046)
    ax.set_ylim(4, 8.5)

    # --- THE FIX FOR THE X-AXIS ---
    # Force the x-axis to only show integer ticks (every 3 years looks clean)
    ax.set_xticks(np.arange(2025, 2047, 2))

    # Formatting
    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', fontsize=14)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('raforkuspa_grunnspa_vs_haspa.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    only = set(sys.argv[1:])
    for f in FIGS:
        if only and f[0] not in only: continue
        try: print(f'Figure {f[0]:5s} {f[3]:30s}', run(*f))
        except Exception: print(f'Figure {f[0]:5s} {f[3]:30s} FAILED'); traceback.print_exc(limit=3)
    print('written to', OUT)
