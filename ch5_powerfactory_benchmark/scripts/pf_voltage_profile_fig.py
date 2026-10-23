"""Figure 5.4: simulated and measured voltage profile along circuit A20-13 at the winter peak (10 Dec 2025, 17:55).
Simulated: PowerFactory winter-peak solution, line-to-line kV at each station busbar (pf_voltage_profile_data.csv).
Measured: A20 busbar 2 SCADA VT (0.1 kV storage step, bar +/-0.05 kV) and ComPass line-to-line voltages as recorded
(no bar: the voltage channels are scaled once in the field against an assumed 11.00 kV, so their
absolute accuracy is the unknown network voltage at calibration time, not the +/-1 % class; Veitur operating practice). No offset correction is applied in the figure; the mean offset is discussed in the text."""
import csv, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
BLUE,ORANGE,INK,MUTED,GRID='#2a78d6','#eb6834','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'font.family':'Liberation Sans','font.size':8.5,'text.color':INK,'axes.edgecolor':MUTED,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED})
from paths import data, out
src=sys.argv[1] if len(sys.argv)>1 else data('pf_voltage_profile_data.csv')
rows=list(csv.DictReader(open(src)))
km=[float(r['km']) for r in rows]; sim=[float(r['sim_kV']) for r in rows]
fig,ax=plt.subplots(figsize=(6.27,3.0))
ax.plot(km,sim,color=BLUE,lw=1.8,marker='o',ms=3.5,zorder=3)
bar=dict(ls='none',ecolor='#9a9994',elinewidth=0.8,capsize=2,capthick=0.8,zorder=2)
for r in rows:
    if r['meas_kV']=='': continue
    x=float(r['km']); y=float(r['meas_kV'])
    if r['station'].startswith('A20'):
        ax.errorbar(x,y,yerr=0.05,**bar); ax.plot(x,y,marker='^',ms=6,mec=INK,mfc='white',mew=1.0,ls='none',zorder=4)
    else:
        ax.plot(x,y,marker='s',ms=5,color=ORANGE,ls='none',zorder=4)   # no bar: one-point field calibration against 11.00 kV, absolute accuracy unknown
for r in rows:   # station names along the top
    ax.annotate(r['station'],(float(r['km']),11.31),ha='center',va='bottom',fontsize=6.8,color=MUTED,rotation=90,annotation_clip=False)
ax.set_xlim(-0.15,6.0); ax.set_ylim(10.75,11.30)
ax.set_xlabel('Route length from A20 busbar 2 (km)'); ax.set_ylabel('Line-to-line voltage (kV)')
for s in ('top','right'): ax.spines[s].set_visible(False)
ax.grid(color=GRID,lw=0.5); ax.set_axisbelow(True); ax.tick_params(labelsize=8)
h=[Line2D([],[],color=BLUE,lw=1.8,marker='o',ms=3.5,label='simulated, winter-peak load flow'),
   Line2D([],[],ls='none',marker='^',ms=6,mec=INK,mfc='white',label='A20 busbar 2, SCADA VT (bar: 0.1 kV storage step)'),
   Line2D([],[],ls='none',marker='s',ms=5,color=ORANGE,label='ComPass line-to-line voltage as recorded')]
ax.legend(handles=h,loc='upper right',frameon=False,fontsize=7.8,handlelength=1.8,bbox_to_anchor=(1.0,0.97))
fig.subplots_adjust(top=0.80,bottom=0.16,left=0.09,right=0.985)
OUT=sys.argv[2] if len(sys.argv)>2 else out('pf_voltage_profile')
for e in ('pdf','png'): fig.savefig(f'{OUT}.{e}',dpi=200 if e=='png' else None)
print('ok')
