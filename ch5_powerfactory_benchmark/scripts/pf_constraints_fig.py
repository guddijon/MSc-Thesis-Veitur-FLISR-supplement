"""Figure 5.6: post-restoration loading of the limiting device against the operating alarm limit of its circuit,
one bar per scenario, sorted by loading. Data: restoration sweep (tab:pf_scenarios, winter peak 10 Dec 2025,
boiler off; SCN-05 boiler on at 3.8 MW, with the 4.9 MW case as the outlined extension). The lowest energised 11 kV
busbar voltage is 0.999 pu or higher in every case (limit 0.955 pu) and the cable-rating margin is looser than the alarm
limit by 7 to 27 points in every case, so neither is drawn; both are stated in the text."""
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from paths import out
BLUE,LBLUE,INK,MUTED,GRID,TRACK='#2a78d6','#a9c8ef','#0b0b0b','#52514e','#e4e3df','#f1f0ec'
plt.rcParams.update({'font.family':'Liberation Sans','font.size':8.5,'text.color':INK})
rows=[('01',40.3,'circuit 05 head'),('02',9.9,'circuit 09 head'),('03',61.7,'circuit 13 head'),('04',34.8,'circuit 08 head'),
      ('05',120.7,'circuit 22 head'),('06',None,''),('07',55.7,'circuit 22 head'),('08',45.2,'circuit 22 head'),
      ('09',67.7,'circuit 06 head'),('10',35.1,'circuit 05 head'),('11',None,''),('12',40.2,'circuit 05 head'),
      ('13',64.6,'circuit 13 head'),('14',77.3,'circuit 21 head'),('15',50.1,'circuit 22 head')]
SCN05_49=142.4
order=sorted(rows,key=lambda r:(-1 if r[1] is None else r[1]),reverse=True)
fig,ax=plt.subplots(figsize=(6.27,3.9))
plt.rcParams['hatch.linewidth']=0.8
n=len(order); ys=list(range(n))[::-1]
for y,(sid,v,dev) in zip(ys,order):
    if v is None:
        ax.text(1.5,y,'no restoration path',va='center',ha='left',fontsize=8,color=MUTED,style='italic'); continue
    ax.barh(y,v,height=0.62,color=BLUE,edgecolor='none',zorder=3)
    xl=v
    if sid=='05':
        ax.barh(y,SCN05_49-v,left=v,height=0.62,color='white',edgecolor=BLUE,lw=1.0,hatch='////',zorder=3)
        xl=SCN05_49
    lab=f'{v:.0f} %  {dev}\n{SCN05_49:.0f} % with the boiler at 4.9 MW' if sid=='05' else f'{v:.0f} %  {dev}'
    ax.text(xl+2,y,lab,va='center',ha='left',fontsize=8,color=INK,zorder=6,bbox=dict(fc='white',ec='none',pad=1.2))
ax.axvline(100,color=INK,lw=1,ls=(0,(4,2)),zorder=4); ax.text(100,n-0.3,'alarm limit',ha='center',va='bottom',fontsize=8,color=INK)
ax.set_yticks(ys); ax.set_yticklabels([f'SCN-{r[0]}' for r in order],fontsize=8.5)
ax.set_xlim(0,172); ax.set_ylim(-0.7,n-0.1); ax.set_xticks([0,25,50,75,100,125,150])
ax.set_xlabel('Loading of the limiting device after restoration, share of the circuit alarm limit (%)')
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(MUTED); ax.tick_params(axis='y',length=0); ax.tick_params(axis='x',colors=MUTED,labelsize=8)
ax.grid(axis='x',color=GRID,lw=0.6); ax.set_axisbelow(True)
fig.tight_layout()
for e in ('pdf','png'): fig.savefig(out(f'pf_constraints.{e}'),dpi=200 if e=='png' else None)
print('ok')
