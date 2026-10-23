"""ADMS-style schematic of the Akranes 11 kV benchmark (December 2025 base, boiler off), drawn at print size.
Shared layout for Figure 5.1 (model schematic) and Figure 5.5 (scenario map). Topology from the model.
Print geometry: memoir 12pt A4 with 25.4 mm margins -> text block 6.27 x 9.69 in;
the figure is included at width=\\textwidth, height=0.88\\textheight, so the page is 6.27 x 8.5 in and all font
sizes below are true print points. Circuit 13 is folded after D1030 so that no row needs more than nine boxes."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
plt.rcParams['font.family']='Liberation Sans'
ink='#0b0b0b'; grey='#52514e'; lgrey='#9a9994'; blue='#2a78d6'; tele='#dbe8f8'; surf='#ffffff'; red='#b3261e'
TELE={'D1001','D1004','D1025','D1026','D1029','D1030','D1056','D1061','D1062','D1066','D1069','D1070','D1067'}
BB1X,BB2X=-0.25,0.25
BW,BH=0.76,0.32
FS_ST,FS_R,FS_NO,FS_LEG,FS_T=7.5,9,7.5,8.5,9.5
# row y positions (bay order top to bottom as in the ADMS)
Y={'R13':0.0,'R23':-0.75,'R22':-1.7,'R20':-3.0,'R04':-3.6,'R19':-4.25,'R21':-4.9,'R12':-5.5,'R06':-6.15,'R08':-6.85,
   'R05':-7.6,'R14':-8.95,'R11':-9.55,'R18':-10.15,'R10':-10.75,'R09':-11.5,'R17':-12.1,'R15':-12.6,'R03':-13.1,
   'R16':-13.7,'R07':-14.3,'R02':-14.9,'R01':-15.5}
SIDE={'R13':'R','R23':'L','R22':'R','R20':'R','R04':'R','R19':'R','R21':'R','R12':'L','R06':'R','R08':'L','R05':'R',
      'R14':'R','R11':'L','R18':'L','R10':'R','R09':'L','R17':'R','R15':'L','R03':'R','R16':'L','R07':'L','R02':'R','R01':'L'}
BB={'R13':2,'R22':1,'R04':2,'R19':1,'R21':1,'R12':'C','R06':1,'R08':2,'R05':1,'R11':1,'R10':1,'R09':1,'R16':1,'R07':2,'R02':1,'R01':2}
CLOSED={'R13','R22','R19','R21','R06','R08','R05','R11','R10','R09','R16','R07','R02','R01'}
ORDER=['R13','R23','R22','R20','R04','R19','R21','R12','R06','R08','R05','R14','R11','R18','R10','R09','R17','R15','R03','R16','R07','R02','R01']
XC=[1.25+0.9*i for i in range(9)]   # box columns on the right
XL=[-1.95-0.9*i for i in range(4)]  # box columns on the left
XLIM=(-5.05,9.0); YLIM=(-16.35,1.5)

def draw(scenario=False, out=None):
    fig,ax=plt.subplots(figsize=(6.27,8.5),dpi=200); fig.patch.set_facecolor(surf); ax.set_facecolor(surf)
    def box(x,y,name,dead=False):
        fc='#eeeeee' if dead else (tele if name in TELE else surf)
        ax.add_patch(FancyBboxPatch((x-BW/2,y-BH/2),BW,BH,boxstyle='round,pad=0.02,rounding_size=0.06',fc=fc,ec=lgrey if dead else ink,lw=0.9,ls='--' if dead else '-',zorder=3))
        ax.text(x,y,name,ha='center',va='center',fontsize=FS_ST,color=grey if dead else ink,zorder=4)
    def seg(x0,y0,x1,y1,open_=False,lw=0.9):
        ax.plot([x0,x1],[y0,y1],color=ink,lw=lw,ls=(0,(3,2)) if open_ else '-',zorder=2,solid_capstyle='round')
    def note(x,y,t,ha='center',va='bottom',c=grey):
        if not t: return
        ax.text(x,y,t,ha=ha,va=va,fontsize=FS_NO,color=c,style='italic',zorder=6)
    def hlink(xa,xb,y,open_=False):
        d=1 if xb>xa else -1; seg(xa+d*BW/2,y,xb-d*BW/2,y,open_)
    def vlink(x,ya,yb,open_=False):
        d=-1 if yb<ya else 1; seg(x,ya+d*BH/2,x,yb-d*BH/2,open_)
    def row(xs,names,y):
        for a,b in zip(xs,xs[1:]): hlink(a,b,y)
        for x,s in zip(xs,names): box(x,y,s)
    # ---------------- A20 busbars and bays
    ytop,ybot=0.55,-16.0
    ax.add_patch(Rectangle((-1.75,ybot-0.2),3.5,ytop-ybot+0.7,fc='none',ec=lgrey,lw=0.6,ls=(0,(1,2)),zorder=1))
    ax.text(-1.65,ytop+0.14,'A20 Smiðjuvellir 66/11 kV',ha='left',va='bottom',fontsize=FS_T,color=ink)
    for xb in (BB1X,BB2X): ax.plot([xb,xb],[ybot,ytop],color=ink,lw=2.2,zorder=2)
    ax.text(BB1X-0.1,ytop,'busbar 1',ha='right',va='center',fontsize=FS_R,color=ink)
    ax.text(BB2X+0.1,ytop,'busbar 2',ha='left',va='center',fontsize=FS_R,color=ink)
    FEED={}
    for name in ORDER:
        y=Y[name]; d=1 if SIDE[name]=='R' else -1; bb=BB.get(name)
        if bb=='C':
            ax.plot([BB1X,BB2X],[y,y],color=ink,lw=0.9); ax.add_patch(Rectangle((-0.09,y-0.09),0.18,0.18,fc=surf,ec=ink,lw=0.9,zorder=4))
            ax.text(-0.95,y,name,ha='center',va='center',fontsize=FS_R,color=ink); continue
        xout=BB2X if d>0 else BB1X
        ax.plot([BB1X,BB2X],[y,y],color=ink,lw=0.9,zorder=2)
        if bb: ax.add_patch(Circle(((BB1X if bb==1 else BB2X),y),0.055,fc=ink,ec=ink,zorder=4))
        xbrk=xout+d*0.45
        ax.plot([xout,xbrk+d*0.12],[y,y],color=ink,lw=0.9,zorder=2)
        ax.add_patch(Rectangle((xbrk-0.09,y-0.09),0.18,0.18,fc=ink if name in CLOSED else surf,ec=ink,lw=0.9,zorder=4))
        FEED[name]=xbrk+d*0.12
        ax.text(-d*0.98,y,name,ha='center',va='center',fontsize=FS_R,color=ink,zorder=5)
    def feeder(name,x_first,open_line=False):
        x0=FEED[name]; d=1 if x_first>x0 else -1; seg(x0,Y[name],x_first-d*BW/2,Y[name],open_line)
    # ---------------- R13, circuit 13 (busbar 2), folded after D1030
    y=Y['R13']; feeder('R13',XC[0])
    row(XC[:8],['D1019','D1029','D1066','D1023','D1050','D1025','D1027','D1030'],y)
    y41,y51,y58=y-0.55,y-1.10,y-1.65
    box(XC[7],y41,'D1041'); vlink(XC[7],y,y41)
    box(XC[8],y41,'D1045'); hlink(XC[7],XC[8],y41)
    box(XC[7],y51,'D1051'); vlink(XC[7],y41,y51)
    box(XC[7],y58,'D1058'); vlink(XC[7],y51,y58)
    # ---------------- R22, circuit 22 (busbar 1)
    y=Y['R22']; feeder('R22',XC[0]); row(XC[:4],['D1028','D1005','D1036','D1004'],y)
    yb=y-0.7
    seg(XC[1]+0.2,y-BH/2,XC[1]+0.2,yb); seg(XC[1]+0.2,yb,XC[3]-BW/2,yb)
    row(XC[3:6],['D1003','D1040','D1018'],yb)
    vlink(XC[3],y,yb,open_=True)
    note(XC[3]+0.08,(y+yb)/2,'SCN-08' if scenario else '',ha='left',va='center')
    # SFAA cable and boiler network (R04, busbar 2, breaker open; tie 1005-1-1 closed)
    y4=Y['R04']; seg(FEED['R04'],y4,XC[1]-1.05,y4)
    ax.add_patch(FancyBboxPatch((XC[1]-1.05,y4-BH/2),2.3,BH,boxstyle='round,pad=0.02,rounding_size=0.06',fc='#eeeeee',ec=lgrey,lw=0.9,ls='--',zorder=3))
    ax.text(XC[1]+0.1,y4,'boiler network (off)',ha='center',va='center',fontsize=FS_ST,color=grey,zorder=4)
    seg(XC[1]-0.2,y-BH/2,XC[1]-0.2,y4+BH/2+0.03)
    if scenario: note(XC[1]-0.12,(y+y4)/2-0.2,'SCN-05',ha='left',va='center')
    # R20: open circuit
    feeder('R20',XC[0],open_line=True); box(XC[0],Y['R20'],'D1035',dead=True)
    # ---------------- R19, circuit 19
    y=Y['R19']; feeder('R19',XC[0]); row(XC[:2],['D1056','D1059'],y)
    # ---------------- R21, circuit 21
    y=Y['R21']; feeder('R21',XC[0]); row(XC[:4],['D1042','D1026','D1001','D1002'],y)
    vlink(XC[3],yb,y,open_=True)
    note(XC[3]+0.08,Y['R19']+0.05,'SCN-07,\n14, 15' if scenario else '',ha='left',va='center')
    # ---------------- R06, circuit 06
    y=Y['R06']; feeder('R06',XC[0]); row(XC[:7],['D1014','D1012','D1011','D1052','D1009','D1008','D1017'],y)
    vlink(XC[5],yb,y,open_=True)
    # ---------------- R05, circuit 05
    y=Y['R05']; feeder('R05',XC[0]); row(XC[:6],['D1070','D1046','D1015','D1020','D1021','D1013'],y)
    y16=y-0.7; x16=XC[3]-0.15
    box(x16,y16,'D1016'); vlink(x16,y,y16)
    yno=y-0.45
    seg(XC[3]+0.22,y-BH/2,XC[3]+0.22,yno,open_=True); seg(XC[3]+0.22,yno,XC[5]-0.1,yno,open_=True); seg(XC[5]-0.1,yno,XC[5]-0.1,y-BH/2,open_=True)
    
    # tie 1012-1-1: D1012 (R06) to D1013 (R05)
    ym=(Y['R06']+Y['R05'])/2
    seg(XC[1],Y['R06']-BH/2,XC[1],ym,open_=True); seg(XC[1],ym,XC[5],ym,open_=True); seg(XC[5],ym,XC[5],y+BH/2,open_=True)
    note((XC[1]+XC[5])/2,ym+0.04,'SCN-09, 12' if scenario else '')
    # ---------------- R10, circuit 10
    y=Y['R10']; feeder('R10',XC[0]); row(XC[:4],['D1053','D1034','D1057','D1022'],y)
    vlink(x16,y16,y,open_=True); note(x16+0.08,(y16+y)/2,'SCN-01, 10' if scenario else '',ha='left',va='center')
    for nm in ('R14','R17','R03','R02'): seg(FEED[nm],Y[nm],FEED[nm]+0.35,Y[nm])
    # ---------------- left side: R08, circuit 08 (busbar 2)
    y=Y['R08']; feeder('R08',XL[0]); row(XL[:3],['D1049','D1061','D1062'],y)
    # tie 1058-1-2 around the top: D1062 to D1058
    xt=XC[8]+0.1; yt=1.2
    seg(XL[2],y+BH/2,XL[2],yt,open_=True); seg(XL[2],yt,xt,yt,open_=True); seg(xt,yt,xt,y58,open_=True); seg(xt,y58,XC[7]+BW/2,y58,open_=True)
    note(2.6,yt+0.04,'SCN-03, 04, 13' if scenario else '')
    # R11, circuit 11
    y=Y['R11']; feeder('R11',XL[0]); row(XL[:3],['D1055','D1054','D1067'],y)
    box(XL[3],y,'D1069',dead=True); hlink(XL[2],XL[3],y,open_=True)
    # R09, circuit 09
    y=Y['R09']; feeder('R09',XL[1]); row(XL[1:4],['D1031','D1032','D1043'],y)
    vlink(XL[1],Y['R11'],y,open_=True); note(XL[1]+0.08,(Y['R11']+y)/2,'SCN-02' if scenario else '',ha='left',va='center')
    for nm in ('R23','R18','R15','R01'): seg(FEED[nm],Y[nm],FEED[nm]-0.35,Y[nm])
    for nm,txt in (('R16','S1 25 MVA'),('R07','S2 16 MVA')):
        x0=FEED[nm]; yy=Y[nm]; seg(x0,yy,x0-0.3,yy)
        ax.add_patch(Circle((x0-0.42,yy),0.12,fc=surf,ec=ink,lw=0.9,zorder=4)); ax.add_patch(Circle((x0-0.58,yy),0.12,fc=surf,ec=ink,lw=0.9,zorder=4))
        seg(x0-0.7,yy,x0-1.0,yy); ax.text(x0-1.08,yy,txt+', 66/11 kV',ha='right',va='center',fontsize=FS_LEG,color=grey)
    # ---------------- fault locations (Figure 5.5)
    if scenario:
        def fseg(x0,x1,y,lab,below=False):
            ax.plot([x0,x1],[y,y],color=red,lw=2.4,solid_capstyle='butt',zorder=2.5)
            ax.text((x0+x1)/2,y-BH/2-0.05 if below else y+BH/2+0.05,lab,ha='center',va='top' if below else 'bottom',fontsize=FS_NO,color=red,fontweight='bold',zorder=6)
        def fbox(x,y,lab):
            ax.add_patch(FancyBboxPatch((x-BW/2,y-BH/2),BW,BH,boxstyle='round,pad=0.02,rounding_size=0.06',fc='none',ec=red,lw=1.8,zorder=5))
            ax.text(x,y+BH/2+0.06,lab,ha='center',va='bottom',fontsize=FS_NO,color=red,fontweight='bold',zorder=6)
        fseg(FEED['R10'],XC[0]-BW/2,Y['R10'],'SCN-01',below=True)
        fbox(XL[0],Y['R11'],'SCN-02')
        fseg(XL[1]-BW/2,XL[2]+BW/2,Y['R08'],'SCN-03')
        fseg(XC[3]+BW/2,XC[4]-BW/2,Y['R13'],'SCN-04')
        fseg(FEED['R04'],XC[1]-1.05,Y['R04'],'SCN-05',below=True)
        fseg(XL[1]-BW/2,XL[2]+BW/2,Y['R09'],'SCN-06')
        fbox(XC[0],Y['R21'],'SCN-07')
        fseg(XC[1]+BW/2,XC[2]-BW/2,Y['R22'],'SCN-08')
        fseg(FEED['R05'],XC[0]-BW/2,Y['R05'],'SCN-09')
        fseg(XC[0]+BW/2,XC[1]-BW/2,Y['R10'],'SCN-10')
        fseg(XL[1]-BW/2,XL[2]+BW/2,Y['R11'],'SCN-11')
        fseg(XC[0]+BW/2,XC[1]-BW/2,Y['R06'],'SCN-12')
        fbox(XL[0],Y['R08'],'SCN-13')
        fseg(FEED['R22'],XC[0]-BW/2,Y['R22'],'SCN-14')
        fbox(XC[1],Y['R21'],'SCN-15')
    # ---------------- legend (lower right), clear of the A20 station frame
    lx=2.25; ly=-11.55 if scenario else -12.5; dy=0.5; dy2=0.18
    def sym_tele(y): ax.add_patch(FancyBboxPatch((lx,y-0.14),0.5,0.28,boxstyle='round,pad=0.02,rounding_size=0.06',fc=tele,ec=ink,lw=0.8))
    def sym_cl(y): ax.add_patch(Rectangle((lx+0.16,y-0.09),0.18,0.18,fc=ink,ec=ink))
    def sym_op(y): ax.add_patch(Rectangle((lx+0.16,y-0.09),0.18,0.18,fc=surf,ec=ink,lw=0.9))
    def sym_tr(y): ax.add_patch(Circle((lx+0.17,y),0.12,fc=surf,ec=ink,lw=0.9)); ax.add_patch(Circle((lx+0.33,y),0.12,fc=surf,ec=ink,lw=0.9))
    def sym_no(y): ax.plot([lx,lx+0.5],[y,y],color=ink,lw=0.9,ls=(0,(3,2)))
    def sym_dot(y): ax.add_patch(Circle((lx+0.25,y),0.055,fc=ink,ec=ink))
    def sym_f(y): ax.plot([lx,lx+0.5],[y,y],color=red,lw=2.4)
    def sym_fb(y): ax.add_patch(FancyBboxPatch((lx,y-0.14),0.5,0.28,boxstyle='round,pad=0.02,rounding_size=0.06',fc='none',ec=red,lw=1.8))
    items=[(sym_tele,'remotely controlled station\nwith ComPass telemetry'),(sym_cl,'breaker closed'),(sym_op,'breaker open'),
           (sym_tr,'66/11 kV transformer'),(sym_no,'normally open point (NO)'),(sym_dot,'busbar the bay is connected to\n(bays without a feeder are not in use)')]
    if scenario: items+=[(sym_f,'faulted cable section (scenario SCN-xx)'),(sym_fb,'faulted station busbar'),(None,'tie labels name the scenarios restored through them')]
    yy=ly
    for sym,txt in items:
        two='\n' in txt
        if two: yy-=dy2
        if sym: sym(yy)
        ax.text(lx+0.7 if sym else lx,yy,txt,fontsize=FS_LEG,va='center',color=grey)
        yy-=dy+(dy2 if two else 0)
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM); ax.set_aspect('equal'); ax.axis('off')
    plt.subplots_adjust(left=0,right=1,top=1,bottom=0)
    for ext in ('pdf','png'): fig.savefig(f'{out}.{ext}',facecolor=surf)
    plt.close(fig)

if __name__=='__main__':
    from paths import out as _out
    draw(False,_out('pf_model_schematic_adms'))
    draw(True,_out('pf_scenario_map_adms'))
    print('ok')
