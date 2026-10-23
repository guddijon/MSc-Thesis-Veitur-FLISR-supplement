"""Figure 5.3: hold-out validation as measured-versus-simulated scatter with measurement-uncertainty bars.
Bars (horizontal, on the measured value only): ComPass current +/-1 % of reading or +/-0.5 A, whichever is larger;
ComPass voltage none (field-scaled once against an assumed 11.00 kV, absolute accuracy unknown); A20 VT analogue +/-0.05 kV (half the 0.1 kV storage step). Simulated values carry no bar.
(a) 34 telemetered bay currents per snapshot (phase mean of L1-L3), model vs ComPass; 1:1 line.
(b) ten substation line-to-line voltages (ComPass) and two A20 busbar voltages (SCADA VT) per snapshot;
    1:1 line and the line of a constant +1.8 % sensor offset.
Data: holdout_measured_vs_sweep.csv (per-bay ComPass values, not part of the supplement) and A20 busbar values from
docs/holdout_validation.md. Model: Akranes_11kV_benchmark, PowerFactory 2025."""
import csv, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
BLUE,ORANGE,INK,MUTED,GRID='#2a78d6','#eb6834','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'font.family':'Liberation Sans','font.size':8.5,'text.color':INK,'axes.edgecolor':MUTED,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED})
from paths import data, out
src=sys.argv[1] if len(sys.argv)>1 else data('holdout_measured_vs_sweep.csv')
rows=list(csv.DictReader(open(src)))
SN={'winter_peak_boiler_off':('Winter peak',BLUE,'o',True),'winter_night_min':('Winter night',BLUE,'o',False),
    'summer_peak':('Summer peak',ORANGE,'s',True),'summer_night_min':('Summer night',ORANGE,'s',False)}
A20={'winter_peak_boiler_off':[(11.17,11.21),(11.23,11.19)],'winter_night_min':[(11.17,11.22),(11.17,11.19)],
     'summer_peak':[(11.23,11.24),(11.27,11.24)],'summer_night_min':[(11.23,11.20),(11.17,11.14)]}
fig,(a,b)=plt.subplots(1,2,figsize=(6.27,3.1))
def pts(ax,x,y,c,m,filled,ms=4.2):
    ax.plot(x,y,ls='none',marker=m,ms=ms,mec=c,mfc=c if filled else 'white',mew=1.0,alpha=0.9,zorder=3)
BAR=dict(ls='none',ecolor='#b5b4ae',elinewidth=0.7,capsize=1.5,capthick=0.7,zorder=2)
for sn,(lab,c,m,filled) in SN.items():
    cur=[r for r in rows if r['snapshot']==sn and r['quantity']=='I' and r['measured']!='' and r['pf']!='']
    xm=[float(r['measured']) for r in cur]; ym=[float(r['pf']) for r in cur]
    a.errorbar(xm,ym,xerr=[max(0.01*x,0.5) for x in xm],**BAR)   # ComPass current class: +/-1 % of reading or +/-0.5 A
    pts(a,xm,ym,c,m,filled)
    vol=[r for r in rows if r['snapshot']==sn and r['quantity']=='U_LL']
    xv=[float(r['measured']) for r in vol]; yv=[float(r['pf']) for r in vol]
    # ComPass voltages carry no bar: one-point field calibration against an assumed 11.00 kV (Veitur operating practice)
    pts(b,xv,yv,c,m,filled)
    xa=[u for u,_ in A20[sn]]; ya=[v for _,v in A20[sn]]
    b.errorbar(xa,ya,xerr=0.05,**BAR)                           # A20 VT analogue resolution 0.1 kV
    pts(b,xa,ya,c,'^',filled,ms=5)
# panel a
L=95; a.plot([0,L],[0,L],color=MUTED,lw=0.8,zorder=1)
a.set_xlim(0,L); a.set_ylim(0,L); a.set_aspect('equal')
a.set_xlabel('Measured bay current (A)'); a.set_ylabel('Simulated bay current (A)')
a.set_title('(a) Bay currents, 34 telemetered bays',fontsize=8.5,loc='left')
# panel b
lo,hi=10.80,11.35
b.plot([lo,hi],[lo,hi],color=MUTED,lw=0.8,zorder=1)
b.plot([lo,hi],[lo*1.018,hi*1.018],color=MUTED,lw=0.8,ls=(0,(3,2)),zorder=1)
b.text(10.83,10.83*1.018-0.012,'mean +1.8 %',fontsize=7.5,color=MUTED,rotation=45,rotation_mode='anchor',ha='left',va='top')
b.text(10.84,10.84-0.012,'1:1',fontsize=7.5,color=MUTED,rotation=45,rotation_mode='anchor',ha='left',va='top')
b.set_xlim(lo,hi); b.set_ylim(lo,hi); b.set_aspect('equal')
b.set_xlabel('Measured line-to-line voltage (kV)'); b.set_ylabel('Simulated line-to-line voltage (kV)')
b.set_title('(b) Substation and A20 busbar voltages',fontsize=8.5,loc='left')
for ax in (a,b):
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.grid(color=GRID,lw=0.5); ax.set_axisbelow(True); ax.tick_params(labelsize=8)
h=[Line2D([],[],ls='none',marker='o',mec=BLUE,mfc=BLUE,ms=4.5,label='winter peak'),
   Line2D([],[],ls='none',marker='o',mec=BLUE,mfc='white',ms=4.5,label='winter night'),
   Line2D([],[],ls='none',marker='s',mec=ORANGE,mfc=ORANGE,ms=4.5,label='summer peak'),
   Line2D([],[],ls='none',marker='s',mec=ORANGE,mfc='white',ms=4.5,label='summer night'),
   Line2D([],[],ls='none',marker='^',mec=INK,mfc='none',ms=5,label='A20 busbar (SCADA VT), by snapshot colour')]
fig.legend(handles=h,loc='lower center',ncol=5,frameon=False,fontsize=7.8,handletextpad=0.3,columnspacing=1.0,bbox_to_anchor=(0.5,-0.01))
fig.tight_layout(rect=(0,0.07,1,1))
OUT=sys.argv[2] if len(sys.argv)>2 else out('pf_validation_scatter')
for e in ('pdf','png'): fig.savefig(f'{OUT}.{e}',dpi=200 if e=='png' else None)
print('ok')
