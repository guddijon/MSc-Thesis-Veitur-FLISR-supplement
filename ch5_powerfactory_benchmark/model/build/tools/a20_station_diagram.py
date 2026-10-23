"""Append a hand-laid double-busbar station diagram for Millispennustæði 20-1 to the DGS.
Usage: python3 a20_station_diagram.py in.dgs out.dgs
Geometry in PowerFactory drawing units (y up). Panels in the physical order of the ADMS board."""
import io,re,sys
src,out=sys.argv[1],sys.argv[2]
text=io.open(src,encoding='utf-8',newline='').read().replace('\r\n','\n')
lines=text.split('\n')
rows={};cur=None;cols=None
for l in lines:
    if l.startswith('$$'):
        hdr=l[2:].split(';'); cur=hdr[0]; cols=[c.split('(')[0] for c in hdr[1:]]; rows.setdefault(cur,[]); continue
    if not l.strip() or l.startswith('*') or cur is None or l.count(';')<3: continue
    rows[cur].append(dict(zip(cols,[x.strip() for x in l.split(';')])))
terms={r['FID']:r for r in rows['ElmTerm']}
named={r['FID']:(t,r) for t,l in rows.items() for r in l if 'loc_name' in r}
SUB='286'
# connections: element -> list of (obj_bus index, terminal fid)
cons={}
for c in rows['StaCubic']: cons.setdefault(c['obj_id'],[]).append((int(c['obj_bus']),c['fold_id']))
tname=lambda f: terms[f]['loc_name']
BB1=[f for f,t in terms.items() if t['loc_name']=='A20_BB1'][0]
BB2=[f for f,t in terms.items() if t['loc_name']=='A20_BB2'][0]
KV66=[f for f,t in terms.items() if t['loc_name']=='A20_66kV'][0]
TERT=[f for f,t in terms.items() if t['loc_name']=='S2_tertiary_3.15kV'][0]
circ={t['loc_name'][5:]:f for f,t in terms.items() if re.match(r'A20_C\d\d$',t['loc_name'])}
ORDER=['13','23','22','21','20','19','05','14','12','06','11','10','08','09','18','17','15','04','03','16','07','02','01']
G=8.75; PITCH=4*G
X0=10*G; Y_BB1=32*G; Y_BB2=28*G; Y_SW=26*G; Y_NODE=23*G; Y_ELM=17*G; Y_66=9*G; Y_NET=5*G
HALF_SW=2.1875   # d_couple connection anchors at +-2.1875 along the axis (from the PF export)
HALF_TR=4.375
maxfid=max(int(r['FID']) for l in rows.values() for r in l if r.get('FID','').isdigit())
def nf():
    global maxfid; maxfid+=1; return str(maxfid)
def num(v): return ('%.4f'%v).rstrip('0').rstrip('.').replace('.',',')
DIA=nf()
grf=[]; gcon=[]
def sym(name,x,y,symnam,obj,rot=0,sx=1,sy=1):
    f=nf(); grf.append(f'  {f};C;{name};{DIA};1;1;1;{num(x)};{num(y)};{symnam};{obj};{rot};{num(sx)};{num(sy)}'); return f
def con(gf,idx,pts):
    f=nf(); n=len(pts); assert 2<=n<=4
    xs=[num(p[0]) for p in pts]+['']*(4-n); ys=[num(p[1]) for p in pts]+['']*(4-n)
    gcon.append(f'  {f};C;GCO_{idx+1};{gf};{n};'+';'.join(xs)+f';{n};'+';'.join(ys)+f';{idx}')
xs={p:X0+i*PITCH for i,p in enumerate(ORDER)}
XL=X0-2*G; XR=X0+22*PITCH+2*G; LEN=XR-XL
BASE=26.25  # base length of TermStrip, read from a PowerFactory import (66 kV strip rSizeX 6 spanned 157 units)
sym('A20_BB1_Graph',(XL+XR)/2,Y_BB1,'TermStrip',BB1,0,LEN/BASE)
sym('A20_BB2_Graph',(XL+XR)/2,Y_BB2,'TermStrip',BB2,0,LEN/BASE)
def side(el,fid):   # cubicle index of element el on terminal fid
    return [i for i,t in cons[el] if t==fid][0]
drawn=set()
for p in ORDER:
    x=xs[p]; node=circ.get(p)
    if p=='12' or node is None:
        continue
    sym(f'A20_C{p}_Graph',x,Y_NODE,'PointTerm',node)
    for el,(idx_t) in [(c['FID'],None) for c in rows['ElmCoup'] if any(t==node for _,t in cons.get(c['FID'],[]))]:
        bus=[t for _,t in cons[el] if t in(BB1,BB2)][0]
        xx=x if bus==BB1 else x+G
        g=sym(named[el][1]['loc_name']+'_Graph',xx,Y_SW,'d_couple',el,0)
        yb=Y_BB1 if bus==BB1 else Y_BB2
        con(g,side(el,bus),[(xx,Y_SW+HALF_SW),(xx,yb)])
        if bus==BB1: con(g,side(el,node),[(xx,Y_SW-HALF_SW),(xx,Y_NODE)])
        else: con(g,side(el,node),[(xx,Y_SW-HALF_SW),(xx,Y_NODE),(x,Y_NODE)])
        drawn.add(el)
    # element on the node
    for el,i in [(e,i) for e,l in cons.items() for i,t in l if t==node and named[e][0]!='ElmCoup']:
        tab,r=named[el]
        if tab=='ElmLne':
            g=sym(r['loc_name'][:38]+'_G',x,Y_ELM,'d_lin',el,0)
            con(g,i,[(x,Y_ELM),(x,Y_NODE)])
        elif tab=='ElmTr2':
            g=sym(r['loc_name']+'_Graph',x,Y_ELM,'d_tr2',el,180)
            con(g,side(el,node),[(x,Y_ELM+HALF_TR),(x,Y_NODE)])
            con(g,side(el,KV66),[(x,Y_ELM-HALF_TR),(x,Y_66)])
        elif tab=='ElmTr3':
            # d_tr3 (rot 180): HV anchor bottom centre, MV anchor upper right (+2.1875), tertiary on the right side.
            xc=x-HALF_SW
            g=sym(r['loc_name']+'_Graph',xc,Y_ELM,'d_tr3',el,180)
            con(g,side(el,node),[(x,Y_ELM+HALF_TR),(x,Y_NODE)])
            con(g,side(el,KV66),[(xc,Y_ELM-HALF_TR),(xc,Y_66)])
            con(g,side(el,TERT),[(xc+1.5*G,Y_ELM),(xc+2*G,Y_ELM)])
            sym('S2_tertiary_Graph',xc+2*G,Y_ELM,'PointTerm',TERT)
# coupler
cp=[c for c in rows['ElmCoup'] if c['loc_name'].startswith('A20_R11-112')][0]
x=xs['12']; g=sym('A20_R11-112_Graph',x,(Y_BB1+Y_BB2)/2,'d_couple',cp['FID'],0)
con(g,side(cp['FID'],BB1),[(x,(Y_BB1+Y_BB2)/2+HALF_SW),(x,Y_BB1)]); con(g,side(cp['FID'],BB2),[(x,(Y_BB1+Y_BB2)/2-HALF_SW),(x,Y_BB2)])
# 66 kV terminal and external grid
x16,x07=xs['16'],xs['07']; xc=(x16+x07)/2
sym('A20_66kV_Graph',xc,Y_66,'TermStrip',KV66,0,(abs(x16-x07)+4*G)/BASE)
xn=[e for e,l in cons.items() if named[e][0]=='ElmXnet'][0]
g=sym('Landsnet_66kV_Graph',xc,Y_NET,'d_net',xn,0); con(g,0,[(xc,Y_NET+HALF_TR),(xc,Y_66)])
# ---- write back: rebuild IntGrfcon table with 4 point columns, append rows, add IntGrfnet row
outl=[];cur=None
for l in lines:
    if l.startswith('$$IntGrfcon'):
        if cur=='IntGrf': outl.extend(grf); outl.append('')
        cur='IntGrfcon'; outl.append('$$IntGrfcon;FID(a:40);OP(a:1);loc_name(a:80);fold_id(p);rX:SIZEROW(i);rX:0(r);rX:1(r);rX:2(r);rX:3(r);rY:SIZEROW(i);rY:0(r);rY:1(r);rY:2(r);rY:3(r);iDatConNr(i)'); continue
    if l.startswith('$$'):
        if cur=='IntGrfcon': outl.extend(gcon); outl.append('')
        if cur=='IntGrf': outl.extend(grf); outl.append('')
        if cur=='IntGrfnet': outl.append(f'  {DIA};C;Millispennustæði 20-1;;1;1;{SUB}'); outl.append('')
        cur=l[2:].split(';')[0]; outl.append(l); continue
    if cur=='IntGrfcon' and l.strip() and not l.startswith('*') and l.count(';')>=3:
        v=l.split(';'); # FID OP name fold n x0 x1 n y0 y1 idx
        v=v[:7]+['','']+v[7:10]+['','']+v[10:]; outl.append(';'.join(v)); continue
    # drop trailing blank lines before next table handled above
    if l=='' and cur in('IntGrfcon','IntGrf','IntGrfnet'): continue
    outl.append(l)
t='\n'.join(outl).replace('\n','\r\n')
io.open(out,'w',encoding='utf-8',newline='').write(t)
io.open(out.replace('.dgs','_ansi.dgs'),'w',encoding='cp1252',newline='').write(t)
print('diagram',DIA,'symbols',len(grf),'connections',len(gcon),'switches drawn',len(drawn))
