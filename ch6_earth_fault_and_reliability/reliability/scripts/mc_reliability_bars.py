"""Figure for thesis Section 6.4: ten-year average SAIDI of the Akranes 11 kV network under the three
restoration processes, as interval bars (Monte Carlo of mc_reliability.py). Per process: thin line
5th to 95th percentile of the simulated decades, thick bar 25th to 75th percentile, dot median. References: band of
the Reykjavík utility's ten-year TSN means 1996-2024 (17.1 to 29.9 min, START), dashed line the measured Akranes
11 kV faults 2020-2026 (29.4 min, record_indices.py)."""
import os, sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc_reliability as mc
BLUE,ORANGE,AQUA,INK,MUTED,GRID='#2a78d6','#eb6834','#1baf7a','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'font.family':'Liberation Sans','font.size':8.5,'pdf.fonttype':42,'text.color':INK,'axes.edgecolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED})
mc.simulate(verbose=False, label='base')
rows=[('crew','(i) crew-based sectionalizing',BLUE),('remote','(ii) remote sectionalizing',ORANGE),('flisr','(iii) automated FLISR',AQUA)]
fig,ax=plt.subplots(figsize=(6.27,2.4))
ax.axvspan(17.1,29.9,color='#e8e7e3',zorder=0,lw=0)
ax.text(23.5,2.58,'Veitur, ten-year means\n1996 to 2024',fontsize=7.5,color=MUTED,ha='center',va='bottom')
ax.axvline(29.4,color=MUTED,lw=0.9,ls=(0,(4,2)),zorder=1)
ax.text(30.0,2.58,'measured 11 kV faults\n2020 to 2026',fontsize=7.5,color=MUTED,ha='left',va='bottom')
for i,(p,lab,c) in enumerate(rows):
    y=2-i; a=mc.ARRAYS[('base',p)]['saidi']
    p5,p25,p50,p75,p95=np.percentile(a,[5,25,50,75,95])
    ax.plot([p5,p95],[y,y],color=c,lw=1.6,solid_capstyle='butt',zorder=2)
    for x in (p5,p95): ax.plot([x,x],[y-0.09,y+0.09],color=c,lw=1.6,zorder=2)
    ax.barh(y,p75-p25,left=p25,height=0.34,color=c,edgecolor='none',zorder=3)
    ax.plot(p50,y,'o',ms=7,mfc='white',mec=INK,mew=1.2,zorder=4)
    ax.text(p50,y-0.3,f'{p50:.0f}',ha='center',va='top',fontsize=8,color=INK)
    ax.text(p5-0.6,y,f'{p5:.0f}',ha='right',va='center',fontsize=7.5,color=MUTED)
    ax.text(p95+0.6,y,f'{p95:.0f}',ha='left',va='center',fontsize=7.5,color=MUTED)
ax.set_yticks([2,1,0]); ax.set_yticklabels([r[1] for r in rows],fontsize=8.5,color=INK)
# key, drawn in the empty lower right
kx,ky=41.0,0.05
ax.plot([kx,kx+5],[ky,ky],color=MUTED,lw=1.6); [ax.plot([x,x],[ky-0.09,ky+0.09],color=MUTED,lw=1.6) for x in (kx,kx+5)]
ax.barh(ky,2.4,left=kx+1.3,height=0.30,color=MUTED,edgecolor='none'); ax.plot(kx+2.5,ky,'o',ms=6,mfc='white',mec=INK,mew=1.1)
ax.text(kx+2.5,ky+0.24,'median',fontsize=7,color=MUTED,ha='center',va='bottom')
ax.text(kx+2.5,ky-0.24,'25 to 75 %',fontsize=7,color=MUTED,ha='center',va='top')
ax.text(kx+5.4,ky,'5 to 95 %',fontsize=7,color=MUTED,ha='left',va='center')
ax.set_ylim(-0.55,2.55); ax.set_xlim(0,50)
ax.set_xlabel('Ten-year average SAIDI (min per customer-year)')
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.tick_params(axis='y',length=0); ax.grid(axis='x',color=GRID,lw=0.5); ax.set_axisbelow(True)
fig.tight_layout(rect=(0,0,1,0.93))
OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'output','reliability_saidi_intervals'); os.makedirs(os.path.dirname(OUT),exist_ok=True)
for e in ('pdf','png'): fig.savefig(f'{OUT}.{e}',dpi=200 if e=='png' else None)
print('ok', {p: [round(v,1) for v in np.percentile(mc.ARRAYS[('base',p)]['saidi'],[5,25,50,75,95])] for p,_,_ in rows})
print('share of decades below / above the band:', {p: (round(100*(mc.ARRAYS[('base',p)]['saidi']<17.1).mean()), round(100*(mc.ARRAYS[('base',p)]['saidi']>29.9).mean())) for p,_,_ in rows})
