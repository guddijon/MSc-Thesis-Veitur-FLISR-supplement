"""Figure 4.4: use of the ADMS power-analysis functions, 2013 to 2026.
Dates from thesis Chapter 4: OFR runs 22 Mar 2016 to Nov 2016 and Oct 2020 to Jun 2022, 11 manual runs May 2025;
DPA over-limit records 5 Mar 2022 to 26 Sep 2024 (6 254), live over-limit state last updated 5 Aug 2025;
first component event 27 Feb 2013; Power Analysis schema 5 Mar 2022; vendor pilot project 2026; study header empty."""
import os, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from datetime import date as D
BLUE,ORANGE,INK,MUTED,GRID='#2a78d6','#eb6834','#0b0b0b','#52514e','#e4e3df'
plt.rcParams.update({'font.family':'Liberation Sans','pdf.fonttype':42,'mathtext.fontset':'custom','mathtext.rm':'Liberation Sans','mathtext.it':'Liberation Sans:italic','mathtext.bf':'Liberation Sans:bold','font.size':8.5,'axes.edgecolor':MUTED,'text.color':INK})
fig,ax=plt.subplots(figsize=(6.5,2.6))
rows=['Open-point evaluation\n(OFR), 10-minute runs','Periodic DPF analysis,\nlimit violations stored','Saved power-flow\nstudies','Milestones']
y={r:i for i,r in enumerate(rows[::-1])}
H=0.42
def bar(row,a,b,c,label=None,lab_dx=0):
    ax.barh(y[row],mdates.date2num(b)-mdates.date2num(a),left=mdates.date2num(a),height=H,color=c,edgecolor='none')
    if label: ax.text(mdates.date2num(a)+(mdates.date2num(b)-mdates.date2num(a))/2+lab_dx,y[row]+H/2+0.08,label,ha='center',va='bottom',fontsize=7.2,color=MUTED)
# OFR
bar(rows[0],D(2016,3,22),D(2016,11,30),BLUE,'Mar to Nov 2016')
bar(rows[0],D(2020,10,1),D(2022,6,30),BLUE,'Oct 2020 to Jun 2022')
ax.plot(mdates.date2num(D(2025,5,15)),y[rows[0]],marker='|',ms=11,mew=2,color=BLUE,ls='none')
ax.text(mdates.date2num(D(2025,5,15)),y[rows[0]]+H/2+0.08,'11 manual runs,\nMay 2025',ha='center',va='bottom',fontsize=7.2,color=MUTED)
# DPF periodic
bar(rows[1],D(2022,3,5),D(2024,9,26),ORANGE,'5 Mar 2022 to 26 Sep 2024')
ax.plot(mdates.date2num(D(2025,8,5)),y[rows[1]],marker='|',ms=11,mew=2,color=ORANGE,ls='none')
ax.text(mdates.date2num(D(2025,8,5)),y[rows[1]]-H/2-0.08,'last live update\n5 Aug 2025',ha='center',va='top',fontsize=7.2,color=MUTED)
# saved studies: none
ax.text(mdates.date2num(D(2019,9,1)),y[rows[2]],'none recorded since commissioning',ha='center',va='center',fontsize=7.6,color=MUTED,style='italic')
# milestones
for d,t,ha in ((D(2013,2,27),'first component event\n27 Feb 2013','left'),(D(2022,3,5),'Power Analysis schema\n5 Mar 2022','center'),(D(2026,6,1),'vendor pilot\nproject, 2026','right')):
    ax.plot(mdates.date2num(d),y[rows[3]],'o',ms=5.5,color=INK)
    ax.text(mdates.date2num(d)+(4 if ha=='left' else -4 if ha=='right' else 0)*3,y[rows[3]]-H/2-0.02,t,ha=ha,va='top',fontsize=7.2,color=MUTED)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows[::-1],fontsize=8)
ax.set_ylim(-0.95,len(rows)-0.35)
ax.set_xlim(mdates.date2num(D(2012,7,1)),mdates.date2num(D(2027,3,1)))
ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_minor_locator(mdates.YearLocator(1))
ax.grid(axis='x',color=GRID,lw=0.6); ax.set_axisbelow(True)
for s in ('top','right','left'): ax.spines[s].set_visible(False)
ax.tick_params(axis='y',length=0); ax.tick_params(axis='x',colors=MUTED,labelsize=8)
ax.set_xlabel('Year',fontsize=8.5,color=INK)
fig.tight_layout()
CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
for e in ('pdf','png'): fig.savefig(os.path.join(OUT, f'dpa_timeline.{e}'),dpi=200 if e=='png' else None)
print('ok')
