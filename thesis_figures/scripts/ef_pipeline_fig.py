"""Figure 3.4 (ef_study_pipeline): steps of the earth-fault study. Output: ../output/ef_study_pipeline.{pdf,png}.
Run: MATPLOTLIBRC=../../matplotlibrc python3 ef_pipeline_fig.py"""
import os, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'Liberation Sans', 'pdf.fonttype': 42})
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ink='#0b0b0b'; grey='#52514e'; surf='#ffffff'; inp='#e8f0fb'; outc='#e6f2e6'
fig,ax=plt.subplots(figsize=(6.27,1.62),dpi=200); fig.patch.set_facecolor(surf); ax.set_facecolor(surf)
W,H=1.85,0.8
def box(x,y,txt,fc=surf,num=None):
    ax.add_patch(FancyBboxPatch((x-W/2,y-H/2),W,H,boxstyle='round,pad=0.02,rounding_size=0.08',fc=fc,ec=ink,lw=0.9))
    ax.text(x,y,txt,ha='center',va='center',fontsize=7.8,color=ink,linespacing=1.15)
    if num: ax.text(x-W/2,y+H/2+0.05,str(num),ha='left',va='bottom',fontsize=7.5,color=grey)
def arrow(a,b): ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=9,lw=0.9,color=ink,shrinkA=0,shrinkB=0))
y1,y2=1.12,0.0; xs=[0,2.25,4.5,6.75]
box(xs[0],y1,'Study matrix',fc=inp,num=1); box(xs[1],y1,'PowerFactory\nshort-circuit\ncases',num=2); box(xs[2],y1,'Residual phasors\nat each\nComPass bay',num=3)
box(xs[1],y2,'Measurement-\nerror Monte\nCarlo',fc=inp,num=4); box(xs[2],y2,'ComPass logic\nemulation',num=5); box(xs[3],y2,'Direction\nprobability per\nFPI and setting',num=6)
box(xs[3]+2.25,y2,'Reported\nFPI settings',fc=outc,num=7)
arrow((xs[0]+W/2,y1),(xs[1]-W/2,y1)); arrow((xs[1]+W/2,y1),(xs[2]-W/2,y1))
arrow((xs[2],y1-H/2),(xs[2],y2+H/2))
arrow((xs[1]+W/2,y2),(xs[2]-W/2,y2)); arrow((xs[2]+W/2,y2),(xs[3]-W/2,y2)); arrow((xs[3]+W/2,y2),(xs[3]+2.25-W/2,y2))
ax.set_xlim(-1.0,10.0); ax.set_ylim(-0.5,1.75); ax.set_aspect('equal'); ax.axis('off')
plt.subplots_adjust(left=0.01,right=0.99,top=0.99,bottom=0.01)
CH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(CH, 'output'); os.makedirs(OUT, exist_ok=True)
for ext in ('pdf','png'): fig.savefig(os.path.join(OUT, f'ef_study_pipeline.{ext}'),facecolor=surf)
print('ok')
