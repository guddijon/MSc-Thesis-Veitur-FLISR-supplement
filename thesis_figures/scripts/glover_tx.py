"""Redrawings after Glover, Overbye & Sarma, Power System Analysis and Design:
Figure 2.7 (transformer connections, single-line and per-unit equivalent) and
Figure 2.9 (per-unit sequence networks of Y-Y, Y-D, D-D transformers).
House style: Liberation Sans for text and mathematics, labels sized to print at about 7.5 pt at the text
width (the drawings are 12.5 in wide and print at 47 %), lines at about 0.85 pt; layout as in the book."""
import os, schemdraw, schemdraw.elements as elm, math
CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
from schemdraw.segments import Segment, SegmentCircle, SegmentText
import matplotlib
matplotlib.rcParams.update({'pdf.fonttype': 42, 'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans',
                            'mathtext.it': 'Liberation Sans:italic', 'mathtext.bf': 'Liberation Sans:bold'})
FS_S,FS_L=16,17
schemdraw.config(fontsize=FS_L, font='Liberation Sans', lw=1.8, color='#0b0b0b')

def coil_zigzag(d, p, q, n=3):
    """short winding drawn as inductor between points p and q"""
    d.add(elm.Inductor2(loops=n).at(p).to(q))

def single_line(d, x, y, kind):
    """single-line transformer symbol with winding connection symbols beneath, Glover style"""
    # two overlapping circles = transformer
    d.add(elm.Line().at((x-1.4,y)).to((x-0.6,y)))
    d.add(elm.Line().at((x+0.6,y)).to((x+1.4,y)))
    d.add(elm.Dot(open=True, radius=0.42).at((x-0.2,y)))
    d.add(elm.Dot(open=True, radius=0.42).at((x+0.2,y)))
    for side,xx in (('H',x-1.0),('X',x+1.0)):
        conn = kind[0] if side=='H' else kind[1]
        if conn=='Y':
            # wye symbol: three phase arms (two up, one down) meeting at the star point; the neutral lead leaves
            # the star point sideways and runs down through the earthing impedance, as in the book
            cx,cy=xx+0.15,y-0.95
            d.add(elm.Line().at((cx,cy)).to((cx-0.4,cy+0.48)))
            d.add(elm.Line().at((cx,cy)).to((cx+0.4,cy+0.48)))
            d.add(elm.Line().at((cx,cy)).to((cx,cy-0.5)))
            d.add(elm.Line().at((cx,cy)).to((cx-0.45,cy)))
            d.add(elm.Line().at((cx-0.45,cy)).to((cx-0.45,cy-0.25)))
            d.add(elm.Inductor2(loops=2).at((cx-0.45,cy-0.25)).to((cx-0.45,cy-0.95)).scale(0.45))
            d.add(elm.Ground().at((cx-0.45,cy-0.95)).scale(0.6))
        else:
            cx,cy=xx,y-1.15
            d.add(elm.Line().at((cx,cy+0.45)).to((cx-0.5,cy-0.4)))
            d.add(elm.Line().at((cx-0.5,cy-0.4)).to((cx+0.5,cy-0.4)))
            d.add(elm.Line().at((cx+0.5,cy-0.4)).to((cx,cy+0.45)))

def winding_schematic(d, x, y, kind):
    """phase-winding schematic after Glover: wye with H1 right, H3 upper left, H2 lower left and a neutral
    impedance to ground; delta with H3 top, H2 lower left, H1 lower right"""
    for side,lab in (('H','H'),('X','X')):
        conn = kind[0] if side=='H' else kind[1]
        xx = x+(-1 if side=='H' else 1)*(1.45 if conn=='Y' else 1.65)
        zl = 'Z_N' if side=='H' else 'Z_n'
        if conn=='Y':
            c=(xx,y)
            ends={'1':(xx+1.05,y),'3':(xx-0.55,y+0.95),'2':(xx-1.0,y-0.45)}
            for k,e in ends.items():
                d.add(elm.Inductor2(loops=3).at(c).to(e).scale(0.45))
                d.add(elm.Dot(radius=0.05).at(e))
                dx,dy=e[0]-xx,e[1]-y; n=(dx*dx+dy*dy)**0.5
                d.add(elm.Label().at((e[0]+0.38*dx/n,e[1]+0.38*dy/n)).label(f'{lab}{k}',fontsize=FS_S))
            d.add(elm.Line().at(c).to((xx,y-0.3)))
            d.add(elm.Inductor2(loops=2).at((xx,y-0.3)).to((xx,y-1.2)).scale(0.45))
            d.add(elm.Label().at((xx+0.22,y-0.75)).label(f'${zl}$',fontsize=FS_S,halign='left'))
            d.add(elm.Ground().at((xx,y-1.2)).scale(0.6))
        else:
            r=0.85
            pts={'3':(xx, y+r),'2':(xx-r*0.866, y-r*0.5),'1':(xx+r*0.866, y-r*0.5)}
            order=['3','2','1']
            for i in range(3):
                a=pts[order[i]]; b=pts[order[(i+1)%3]]
                d.add(elm.Inductor2(loops=3).at(a).to(b).scale(0.45))
            for k,p in pts.items(): d.add(elm.Dot(radius=0.05).at(p))
            d.add(elm.Label().at((pts['3'][0],pts['3'][1]+0.3)).label(f'{lab}3',fontsize=FS_S))
            d.add(elm.Label().at((pts['2'][0]-0.45,pts['2'][1]-0.05)).label(f'{lab}2',fontsize=FS_S))
            d.add(elm.Label().at((pts['1'][0]+0.45,pts['1'][1]-0.05)).label(f'{lab}1',fontsize=FS_S))

def seq_network(d, x, y, seq, kind, w=3.6, sub=True):
    """per-unit sequence network between H (left) and X (right) terminals. seq in ('0','1','2')."""
    xl, xr = x-w/2, x+w/2
    ytop, ybot = y+0.85, y-0.85
    xm = x-0.5 if ((seq in ('1','2')) and kind=='YD') else x
    lab = {'0':'0','1':'1','2':'2'}[seq] if sub else ''
    left_open = right_open = False
    left_series_label = right_series_label = None
    left_short = right_short = False   # delta side in zero sequence: terminal open, winding to reference
    if seq=='0':
        if kind[0]=='Y': left_series_label='3Z_N'
        else: left_open=True
        if kind[1]=='Y': right_series_label='3Z_n'
        else: right_open=True
    # series branches: (R, L) from terminal to centre
    def series(xa,xb,label,mirror=False):
        xmid=xa+(xb-xa)*0.5
        if not mirror:
            d.add(elm.Resistor().at((xa,ytop)).to((xmid,ytop)).scale(0.6))
            d.add(elm.Inductor2(loops=3).at((xmid,ytop)).to((xb,ytop)).scale(0.6))
        else:
            d.add(elm.Inductor2(loops=3).at((xa,ytop)).to((xmid,ytop)).scale(0.6))
            d.add(elm.Resistor().at((xmid,ytop)).to((xb,ytop)).scale(0.6))
        if label: d.add(elm.Label().at(((xa+xb)/2,ytop+0.45)).label(f'${label}$',fontsize=FS_S))
    # left side
    if not left_open:
        series(xl,xm,left_series_label)
    else:
        series(xl+0.45,xm,None)   # delta winding: series impedance closed to the reference, terminal open
        d.add(elm.Line().at((xl+0.45,ytop)).to((xl+0.45,ybot)))
    d.add(elm.Dot(open=True,radius=0.07).at((xl,ytop))); d.add(elm.Dot(open=True,radius=0.07).at((xl,ybot)))
    # right side
    phase_shift = (seq in ('1','2')) and kind=='YD'
    xr_eff = xr-1.1 if phase_shift else xr
    if not right_open:
        series(xm,xr_eff,right_series_label,mirror=True)
    else:
        series(xm,xr-0.45,None,mirror=True)
        d.add(elm.Line().at((xr-0.45,ytop)).to((xr-0.45,ybot)))
    d.add(elm.Dot(open=True,radius=0.07).at((xr,ytop))); d.add(elm.Dot(open=True,radius=0.07).at((xr,ybot)))
    # shunt magnetising branch at centre: Rc || Lm
    d.add(elm.Line().at((xm,ytop)).to((xm,ytop-0.15)))
    d.add(elm.Line().at((xm-0.22,ytop-0.15)).to((xm+0.22,ytop-0.15)))
    d.add(elm.Resistor().at((xm-0.22,ytop-0.15)).to((xm-0.22,ybot+0.15)).scale(0.6))
    d.add(elm.Inductor2(loops=3).at((xm+0.22,ytop-0.15)).to((xm+0.22,ybot+0.15)).scale(0.6))
    d.add(elm.Line().at((xm-0.22,ybot+0.15)).to((xm+0.22,ybot+0.15)))
    d.add(elm.Line().at((xm,ybot+0.15)).to((xm,ybot)))
    # bottom rail
    d.add(elm.Line().at((xl,ybot)).to((xr,ybot)))
    # ideal phase-shifting transformer on the X side for Y-D positive/negative sequence
    if phase_shift:
        xp,xs_=xr-0.72,xr-0.32
        d.add(elm.Line().at((xr_eff,ytop)).to((xp,ytop)))
        d.add(elm.Line().at((xp,ytop)).to((xp,ytop-0.25))); d.add(elm.Line().at((xp,ybot+0.25)).to((xp,ybot)))
        d.add(elm.Inductor2(loops=3).at((xp,ytop-0.25)).to((xp,ybot+0.25)).scale(0.45))
        d.add(elm.Line().at((xs_,ytop)).to((xs_,ytop-0.25))); d.add(elm.Line().at((xs_,ybot+0.25)).to((xs_,ybot)))
        d.add(elm.Inductor2(loops=3).at((xs_,ybot+0.25)).to((xs_,ytop-0.25)).scale(0.45))
        for xc in (xp+0.17,xp+0.23): d.add(elm.Line().at((xc,ytop-0.4)).to((xc,ybot+0.3)))
        d.add(elm.Line().at((xs_,ytop)).to((xr,ytop)))
        d.add(elm.Dot(radius=0.045).at((xp-0.12,ytop-0.12)))
        d.add(elm.Dot(radius=0.045).at((xs_+0.12,ytop-0.12)))
        sgn = '' if seq=='1' else '-'
        d.add(elm.Label().at(((xp+xs_)/2-0.12,ybot-0.5)).label(f'$e^{{{sgn}j30°}}:1$',fontsize=FS_S))
    # terminal labels (outside the terminals when the delta side is open in zero sequence)
    if left_open:
        d.add(elm.Label().at((xl-0.15,ytop-0.4)).label('+',fontsize=FS_S,halign='right'))
        d.add(elm.Label().at((xl-0.15,ybot+0.3)).label('−',fontsize=FS_S,halign='right'))
        d.add(elm.Label().at((xl-0.15,y)).label(f'$V_{{H{lab}}}$',fontsize=FS_S,halign='right'))
    else:
        d.add(elm.Label().at((xl+0.12,ytop-0.4)).label('+',fontsize=FS_S,halign='left'))
        d.add(elm.Label().at((xl+0.12,ybot+0.3)).label('−',fontsize=FS_S,halign='left'))
        d.add(elm.Label().at((xl+0.12,y)).label(f'$V_{{H{lab}}}$',fontsize=FS_S,halign='left'))
    if phase_shift or right_open:
        d.add(elm.Label().at((xr+0.15,ytop-0.4)).label('+',fontsize=FS_S,halign='left'))
        d.add(elm.Label().at((xr+0.15,ybot+0.3)).label('−',fontsize=FS_S,halign='left'))
        d.add(elm.Label().at((xr+0.2,y)).label(f'$V_{{X{lab}}}$',fontsize=FS_S,halign='left'))
    else:
        d.add(elm.Label().at((xr-0.12,ytop-0.4)).label('+',fontsize=FS_S,halign='right'))
        d.add(elm.Label().at((xr-0.12,ybot+0.3)).label('−',fontsize=FS_S,halign='right'))
        d.add(elm.Label().at((xr-0.12,y)).label(f'$V_{{X{lab}}}$',fontsize=FS_S,halign='right'))
def grid(d, cols, rows, x0, y0, cw, rh, left_w):
    """table lines: left label column plus cols columns, rows rows"""
    xs=[x0-left_w]+[x0+i*cw for i in range(cols+1)]
    ys=[y0-j*rh for j in range(rows+1)]
    for xx in xs: d.add(elm.Line().at((xx,ys[0])).to((xx,ys[-1])).color('#52514e').linewidth(0.8))
    for yy in ys: d.add(elm.Line().at((xs[0],yy)).to((xs[-1],yy)).color('#52514e').linewidth(0.8))

KINDS=[('YY','(a)  Y–Y'),('YD','(b)  Y–Δ'),('DD','(c)  Δ–Δ')]

def finish(d, row_labels, name, dpi):
    """Draw, then set the multi-line row labels centred in their rows on a fixed baseline grid (1.2 x font size),
    so the gaps between lines do not depend on the letters (Matplotlib's own line layout adds each line's descent)."""
    f = d.draw(show=False)
    pt = 1 / 72 / f.inches_per_unit                         # one point in drawing units
    pitch = 1.2 * FS_L * pt
    for x, y, s in row_labels:
        lines = s.split('\n')
        for i, line in enumerate(lines):
            base = y + ((len(lines) - 1) / 2 - i) * pitch - 0.36 * FS_L * pt   # 0.36 em: half the cap height
            f.ax.text(x, base, line, ha='center', va='baseline', fontsize=FS_L, color='#0b0b0b',
                      fontfamily='Liberation Sans')
    f.save(os.path.join(OUT, f'{name}.pdf')); f.save(os.path.join(OUT, f'{name}.png'), dpi=dpi)

# ---------------- Figure 2.7
d = schemdraw.Drawing(show=False)
cw,rh,left_w=6.8,4.2,4.8; x0,y0=0,0
grid(d,3,2,x0,y0,cw,rh,left_w)
rows=[(x0-left_w/2,y0-rh/2,'Single-line\ndiagram'),(x0-left_w/2,y0-1.5*rh,'Per-unit\nequivalent\ncircuit')]
for i,(k,cap) in enumerate(KINDS):
    xc=x0+i*cw+cw/2
    single_line(d,xc,y0-rh/2+0.9,k)
    seq_network(d,xc,y0-1.5*rh,'1',k,w=5.0,sub=False)
    d.add(elm.Label().at((xc,y0-2*rh-0.45)).label(cap,fontsize=FS_L))
finish(d, rows, 'transformer_connections', 160)
# ---------------- Figure 2.9
d = schemdraw.Drawing(show=False)
cw,rh,left_w=6.8,3.8,4.8; x0,y0=0,0
grid(d,3,5,x0,y0,cw,rh,left_w)
labels=['Single-line\ndiagram','Schematic','Per-unit\nzero-sequence\nnetwork','Per-unit\npositive-sequence\nnetwork','Per-unit\nnegative-sequence\nnetwork']
rows=[(x0-left_w/2,y0-(j+0.5)*rh,l) for j,l in enumerate(labels)]
for i,(k,cap) in enumerate(KINDS):
    xc=x0+i*cw+cw/2
    single_line(d,xc,y0-rh/2+0.8,k)
    winding_schematic(d,xc,y0-1.5*rh+0.25,k)
    for j,seq in enumerate(('0','1','2')):
        seq_network(d,xc,y0-(2.5+j)*rh,seq,k,w=4.6)
    d.add(elm.Label().at((xc,y0-5*rh-0.45)).label(cap,fontsize=FS_L))
finish(d, rows, 'sequence_transformers', 140)
print('ok')
