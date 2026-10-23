"""Figure 4.1: population of DPF properties across the Veitur ADMS model. Data: dpa_coverage_data.csv (one row per property,
populated/total live components). A CSV with the same columns can be given as the first argument."""
import os, sys, csv, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
BLUE,LBLUE,ORANGE,INK,MUTED,TRACK='#2a78d6','#a9c8ef','#eb6834','#0b0b0b','#52514e','#efeeea'
COL={'telemetry':BLUE,'catalog':LBLUE,'electrical':ORANGE}
NAME={'telemetry':'telemetry and topology','catalog':'catalog linkage','electrical':'component electrical data'}
CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
src=sys.argv[1] if len(sys.argv)>1 else os.path.join(CH, 'data', 'dpa_coverage_data.csv')
rows=list(csv.DictReader(open(src)))
plt.rcParams.update({'font.family':'Liberation Sans','pdf.fonttype':42,'mathtext.fontset':'custom','mathtext.rm':'Liberation Sans','mathtext.it':'Liberation Sans:italic','mathtext.bf':'Liberation Sans:bold','font.size':8.5,'text.color':INK})
fig,ax=plt.subplots(figsize=(6.5,4.6))
n=len(rows); ys=range(n)[::-1]
for yy,r in zip(ys,rows):
    p,t=int(r['populated']),int(r['total']); share=100*p/t if t else 0
    ax.barh(yy,100,height=0.62,color=TRACK,edgecolor='none')
    ax.barh(yy,share,height=0.62,color=COL[r['group']],edgecolor='none')
    ax.text(102,yy,f"{p:,} / {t:,}".replace(',',' '),va='center',ha='left',fontsize=8,color=INK)
ax.set_yticks(list(ys)); ax.set_yticklabels([r['label'] for r in rows],fontsize=8.5)
ax.set_xlim(0,100); ax.set_ylim(-0.7,n-0.3)
ax.set_xticks([0,25,50,75,100]); ax.set_xticklabels(['0 %','25 %','50 %','75 %','100 %'],fontsize=8,color=MUTED)
ax.set_xlabel('Share of live components with the property populated (%)',fontsize=8.5)
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(MUTED); ax.tick_params(axis='y',length=0); ax.tick_params(axis='x',color=MUTED)
ax.legend(handles=[Patch(color=COL[g],label=NAME[g]) for g in ('telemetry','catalog','electrical')],loc='upper center',bbox_to_anchor=(0.42,-0.13),ncol=3,frameon=False,fontsize=8,handlelength=1.6,columnspacing=1.6)
fig.tight_layout()
for e in ('pdf','png'): fig.savefig(os.path.join(OUT, f'dpa_coverage.{e}'),dpi=200 if e=='png' else None)
print('ok')
