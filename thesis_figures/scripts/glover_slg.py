"""Figure 2.10 redrawn after Glover, Overbye & Sarma Figure 10-7: single line-to-ground fault.
(a) three-phase bus with the fault on phase a through Z_F; (b) interconnected sequence networks.
House style: Liberation Sans for text and mathematics, labels sized to print at about 8.5 pt at the text
width, lines at about 1 pt; layout as in the book. The fault impedance (Z_F and its branch in (a), 3Z_F in (b)) is drawn
in the status red used for faults elsewhere in the thesis; the rest stays black."""
import os, schemdraw, schemdraw.elements as elm
import matplotlib
matplotlib.rcParams.update({'pdf.fonttype': 42, 'mathtext.fontset': 'custom', 'mathtext.rm': 'Liberation Sans',
                            'mathtext.it': 'Liberation Sans:italic', 'mathtext.bf': 'Liberation Sans:bold'})
CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
schemdraw.config(fontsize=12, font='Liberation Sans', lw=1.4, color='#0b0b0b')
ink='#0b0b0b'; grey='#52514e'
fault = '#b3261e'                                                # status red, as for faults in Figures 2.8, 2.14 and 5.5
NAME = 'slg_fault_sequence'
def L(d,a,b,**k): return d.add(elm.Line().at(a).to(b),**k) if False else d.add(elm.Line().at(a).to(b))
with schemdraw.Drawing(show=False) as d:
    # ---------- (a) general three-phase bus
    x0,y0=0,0; YCAP=-10.3
    d.add(elm.Line().at((x0,y0+0.2)).to((x0,y0-3.3)).linewidth(2.4))
    d.add(elm.Label().at((x0+0.15,y0+0.45)).label('three-phase bus',fontsize=12,halign='left'))
    phases=(('c',y0-0.5),('b',y0-1.5),('a',y0-2.5))
    for ph,yy in phases:
        d.add(elm.Line(arrow='->').at((x0,yy)).to((x0+1.0,yy)))
        d.add(elm.Line().at((x0+1.0,yy)).to((x0+1.4,yy)))
        d.add(elm.Dot(open=True,radius=0.07).at((x0+1.4,yy)))
        d.add(elm.Label().at((x0+0.5,yy+0.22)).label(f'$I_{ph}$'+(' = 0' if ph!='a' else ''),fontsize=12))
        d.add(elm.Label().at((x0-0.25,yy)).label(ph,fontsize=12,halign='right'))
    ya=y0-2.5
    d.add(elm.Line().at((x0+1.4,ya)).to((x0+2.3,ya)).color(fault))
    d.add(elm.Resistor().at((x0+2.3,ya)).to((x0+2.3,ya-1.3)).scale(0.7).color(fault).label('$Z_F$',loc='right',fontsize=12,ofst=0.12,color=fault))
    d.add(elm.Ground().at((x0+2.3,ya-1.3)).scale(0.7).color(fault))
    # reference g and the three phase-to-ground voltages
    d.add(elm.Line().at((x0+1.0,y0-4.1)).to((x0+5.9,y0-4.1)).color(grey))
    d.add(elm.Label().at((x0+6.1,y0-4.1)).label('g',fontsize=12,halign='left'))
    for ph,yy,xx in (('c',y0-0.5,x0+5.2),('b',y0-1.5,x0+4.2),('a',y0-2.5,x0+3.2)):
        d.add(elm.Line().at((x0+1.4,yy)).to((xx,yy)).color(grey).linestyle(':'))
        d.add(elm.Line().at((xx,yy)).to((xx,y0-4.1)).color(grey).linestyle(':'))
        d.add(elm.Label().at((xx+0.1,yy-0.22)).label('+',fontsize=11,halign='left'))
        d.add(elm.Label().at((xx+0.1,y0-3.9)).label('−',fontsize=11,halign='left'))
        d.add(elm.Label().at((xx+0.12,(yy+y0-4.1)/2)).label(f'$V_{{{ph}g}}$',fontsize=12,halign='left'))
    d.add(elm.Label().at((x0-0.4,y0-8.0)).label('Fault conditions in the phase domain:',fontsize=12,halign='left'))
    d.add(elm.Label().at((x0-0.4,y0-8.6)).label('$V_{ag} = Z_F\\, I_a$',fontsize=12,halign='left'))
    d.add(elm.Label().at((x0-0.4,y0-9.2)).label('$I_b = I_c = 0$',fontsize=12,halign='left'))
    d.add(elm.Label().at((x0+3.0,YCAP)).label('(a)  Single line-to-ground fault\non phase a of a three-phase bus',fontsize=12))
    # ---------- (b) interconnected sequence networks
    bx=9.4; yb=-0.3; xL=bx+0.4; xZ=bx+1.2; xT=bx+4.4; xR=bx+5.6; H=1.6; P=2.6
    for k,(seq,yy) in enumerate((('0',yb),('1',yb-P),('2',yb-2*P))):
        d.add(elm.Line().at((xL,yy)).to((xZ,yy)))
        d.add(elm.Inductor2(loops=3).at((xZ,yy)).to((xZ+1.5,yy)).scale(0.7).label(f'$Z_{seq}$',loc='top',fontsize=12,ofst=0.1))
        d.add(elm.Line(arrow='->').at((xZ+1.5,yy)).to((xZ+2.5,yy)))
        d.add(elm.Line().at((xZ+2.5,yy)).to((xT,yy)))
        d.add(elm.Label().at((xZ+2.1,yy+0.25)).label(f'$I_{seq}$',fontsize=12))
        d.add(elm.Dot(open=True,radius=0.07).at((xT,yy)))
        d.add(elm.Dot(open=True,radius=0.07).at((xT,yy-H)))
        d.add(elm.Label().at((xT+0.18,yy-0.3)).label('+',fontsize=11,halign='left'))
        d.add(elm.Label().at((xT+0.18,yy-H+0.3)).label('−',fontsize=11,halign='left'))
        d.add(elm.Label().at((xT+0.18,yy-H/2)).label(f'$V_{seq}$',fontsize=12,halign='left'))
        d.add(elm.Line().at((xL,yy-H)).to((xT,yy-H)))
        if seq=='1':
            d.add(elm.SourceSin().at((xL,yy-H)).to((xL,yy)).scale(0.8))
            d.add(elm.Label().at((xL-0.35,yy-0.3)).label('+',fontsize=11,halign='right'))
            d.add(elm.Label().at((xL-0.35,yy-H+0.3)).label('−',fontsize=11,halign='right'))
            d.add(elm.Label().at((xL-0.45,yy-H/2)).label('$V_F$',fontsize=12,halign='right'))
        else:
            d.add(elm.Line().at((xL,yy)).to((xL,yy-H)))
    # series interconnection: bottom of 0 to top of 1, bottom of 1 to top of 2, and 3Z_F from the top of 0 to the bottom of 2
    d.add(elm.Line().at((xT,yb-H)).to((xT,yb-P)))
    d.add(elm.Line().at((xT,yb-P-H)).to((xT,yb-2*P)))
    d.add(elm.Line().at((xT,yb)).to((xR,yb)))
    d.add(elm.Line().at((xR,yb)).to((xR,yb-1.4)))
    d.add(elm.Resistor().at((xR,yb-1.4)).to((xR,yb-2.8)).scale(0.7).color(fault))
    d.add(elm.Label().at((xR+0.3,yb-2.1)).label('$3Z_F$',fontsize=12,halign='left',color=fault))
    d.add(elm.Line().at((xR,yb-2.8)).to((xR,yb-2*P-H)))
    d.add(elm.Line().at((xR,yb-2*P-H)).to((xT,yb-2*P-H)))
    d.add(elm.Label().at((bx-0.4,yb-2*P-H-0.9)).label('Fault conditions in the sequence domain:',fontsize=12,halign='left'))
    d.add(elm.Label().at((bx-0.4,yb-2*P-H-1.5)).label('$I_0 = I_1 = I_2$',fontsize=12,halign='left'))
    d.add(elm.Label().at((bx-0.4,yb-2*P-H-2.1)).label('$V_0 + V_1 + V_2 = 3Z_F\\, I_1$',fontsize=12,halign='left'))
    d.add(elm.Label().at((bx+3.0,YCAP)).label('(b)  Interconnected\nsequence networks',fontsize=12))
    d.save(os.path.join(OUT, f'{NAME}.pdf')); d.save(os.path.join(OUT, f'{NAME}.png'), dpi=160)
print('ok')
