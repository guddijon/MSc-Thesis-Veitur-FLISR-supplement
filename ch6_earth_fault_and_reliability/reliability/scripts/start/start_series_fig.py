"""Figure: reliability indices of the Reykjavík utility (Orkuveita Reykjavíkur, from 2014 Veitur), unplanned
interruptions in its own system, 1996-2024, from the START reports (each year from the newest report that lists it;
2024 from the 2015-2024 report). Three panels, one per index, each with its ten-year rolling mean."""
import csv, sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Liberation Sans','font.size':8.5,'pdf.fonttype':42,'axes.edgecolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e'})
BLUE,INK,MUTED,GRID='#2a78d6','#0b0b0b','#52514e','#e4e3df'
R=list(csv.DictReader(open(sys.argv[1]))); out=sys.argv[2]
y=np.array([int(r['year']) for r in R])
P=[('TSN','(a) TSN, SAIDI','Duration (min)'),('FSN','(b) FSN, SAIFI','Frequency (1/a)'),('TSF','(c) TSF, CAIDI','Duration (h)')]
fig,axs=plt.subplots(3,1,figsize=(6.27,5.4),sharex=True)
for ax,(k,ttl,lab) in zip(axs,P):
    v=np.array([float(r[k]) for r in R])
    ax.bar(y,v,width=0.72,color='#a9c8ef',edgecolor='none',zorder=2)
    roll=np.array([v[i-9:i+1].mean() for i in range(9,len(v))])
    ax.plot(y[9:],roll,color=BLUE,lw=2.0,zorder=3)
    ax.set_ylabel(lab,fontsize=8); ax.set_title(ttl,fontsize=8.5,loc='left',pad=3); ax.grid(axis='y',color=GRID,lw=0.6,zorder=0)
    for s in ('top','right'): ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8)
from matplotlib.patches import Patch; from matplotlib.lines import Line2D
fig.legend(handles=[Patch(color='#a9c8ef',label='annual value'),Line2D([],[],color=BLUE,lw=2,label='ten-year rolling mean, plotted at the end year')],loc='upper center',ncol=2,frameon=False,fontsize=8,bbox_to_anchor=(0.55,1.0))
axs[2].set_xlabel('Year'); axs[2].set_xlim(1995.2,2024.8); axs[2].set_xticks(range(1996,2025,4))
fig.tight_layout(h_pad=0.8,rect=(0,0,1,0.95))
for e in ('pdf','png'): fig.savefig(f'{out}.{e}',dpi=200 if e=='png' else None)
print('ok')
