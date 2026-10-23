"""Balanced positive-sequence backward/forward sweep on the Akranes DGS model.
Usage: radial_pf.py file.dgs [--zip aP bP] [--scale JSON] ; prints feeder-head currents.
Loads: S = S0*(aZ*(V/Vn)^2 + aI*(V/Vn) + aP) with aZ=zip[0], aI=zip[1], aP=1-aZ-aI."""
import io,re,sys,json,cmath,math,collections
def parse(fn):
    rows={};cur=None;cols=None
    for line in io.open(fn,encoding='utf-8'):
        line=line.rstrip('\r\n')
        if line.startswith('$$'):
            hdr=line[2:].split(';'); cur=hdr[0]; cols=[c.split('(')[0] for c in hdr[1:]]; rows.setdefault(cur,{}); continue
        if not line.strip() or line.startswith('*') or cur is None or line.count(';')<3: continue
        v=[x.strip() for x in line.split(';')]; r=dict(zip(cols,v)); rows[cur][r['FID']]=r
    return rows
f=lambda s: float(str(s).replace(',','.')) if s not in ('',None) else 0.0
def solve(rows, zipc=(0,0), scale=None, verbose=False):
    aZ,aI=zipc; aP=1-aZ-aI
    terms=rows['ElmTerm']; cub=rows['StaCubic']; sw=rows['StaSwitch']
    open_cub={s['fold_id'] for s in sw.values() if s['on_off']=='0'}
    el_t=collections.defaultdict(dict)   # element -> {bus index: terminal}
    for c in cub.values():
        if c['FID'] in open_cub: continue
        el_t[c['obj_id']][int(c['obj_bus'])]=c['fold_id']
    edges=[]  # (a,b,kind,params)
    for fid,r in rows['ElmLne'].items():
        t=el_t.get(fid,{})
        if len(t)<2: continue
        ty=rows['TypLne'][r['typ_id']]; L=f(r['dline']); n=max(1,int(r.get('nlnum','1') or 1))
        Z=complex(f(ty['rline']),f(ty['xline']))*L/n; B=f(ty['bline'])*1e-6*L*n
        edges.append((t[0],t[1],'lne',dict(Z=Z,B=B,name=r['loc_name'])))
    for fid,r in rows['ElmCoup'].items():
        t=el_t.get(fid,{})
        if len(t)<2 or r['on_off']=='0': continue
        edges.append((t[0],t[1],'cpl',dict(Z=0j,B=0.0,name=r['loc_name'])))
    for fid,r in rows['ElmTr2'].items():
        t=el_t.get(fid,{})
        if len(t)<2 or r.get('outserv','0')=='1': continue
        ty=rows['TypTr2'][r['typ_id']]; S=f(ty['strn']); Uh=f(ty['utrn_h']); Ul=f(ty['utrn_l'])
        tap=int(r.get('nntap','0') or 0); Uh_t=Uh*(1+tap*f(ty['dutap'])/100) if int(ty.get('tap_side','0') or 0)==0 else Uh
        Ul_t=Ul if int(ty.get('tap_side','0') or 0)==0 else Ul*(1+tap*f(ty['dutap'])/100)
        Zm=f(ty['uktr'])/100*Ul_t**2/S; R=f(ty['pcutr'])/1000/S**2*Ul_t**2; X=math.sqrt(max(Zm**2-R**2,0))
        Ym=complex(f(ty['pfe'])/1000/Uh_t**2, -f(ty['curmg'])/100*S/Uh_t**2)   # S (siemens, 3-ph MVA/kV^2 => actually MVA/kV^2 = S)
        edges.append((t[0],t[1],'tr',dict(a=Uh_t/Ul_t,Z=complex(R,X),Ym=Ym,name=r['loc_name'])))
    for fid,r in rows['ElmTr3'].items():
        t=el_t.get(fid,{})
        if 0 not in t or 1 not in t: continue
        ty=rows['TypTr3'][r['typ_id']]; S=f(ty['strn3_h']); Uh=f(ty['utrn3_h']); Um=f(ty['utrn3_m'])
        tap=int(r.get('n3tap_h','0') or 0); Uh_t=Uh*(1+tap*f(ty['du3tp_h'])/100)
        Zm=f(ty['uktr3_h'])/100*Um**2/S; R=f(ty['pcut3_h'])/1000/S**2*Um**2; X=math.sqrt(max(Zm**2-R**2,0))
        Ym=complex(f(ty['pfe'])/1000/Uh_t**2, -f(ty['curm3'])/100*S/Uh_t**2)
        edges.append((t[0],t[1],'tr',dict(a=Uh_t/Um,Z=complex(R,X),Ym=Ym,name=r['loc_name'])))
    loads=collections.defaultdict(list)
    for fid,r in rows['ElmLod'].items():
        t=el_t.get(fid,{})
        if 0 in t:
            sc=1.0
            if scale: sc=scale.get(r['loc_name'],1.0)
            loads[t[0]].append((complex(f(r['plini']),f(r['qlini']))*sc,r['loc_name']))
    # source
    xn=next(iter(rows['ElmXnet'].values())); src=el_t[xn['FID']][0]
    Vs=f(xn['usetp'])*f(terms[src]['uknom'])/math.sqrt(3)*1000  # V phase
    # build tree by BFS from source
    adj=collections.defaultdict(list)
    for i,(a,b,k,p) in enumerate(edges): adj[a].append((b,i)); adj[b].append((a,i))
    parent={src:None}; order=[src]; pedge={}
    q=[src]
    while q:
        x=q.pop(0)
        for y,i in adj[x]:
            if y in parent:
                if pedge.get(x)!=i and parent.get(x)!=y: pass
                continue
            parent[y]=x; pedge[y]=i; order.append(y); q.append(y)
    # mesh check
    ne=sum(1 for a,b,k,p in edges if a in parent and b in parent)
    if verbose: print('energised nodes',len(order),'edges',ne,'loops',ne-(len(order)-1))
    V={n:Vs+0j for n in order}
    # nominal per node for ZIP reference
    Vn={n:f(terms[n]['uknom'])*1000/math.sqrt(3) for n in order}
    Iedge={}
    for it in range(60):
        # backward: node injection currents
        Inode={}
        for n in reversed(order):
            I=0j
            for S0,name in loads.get(n,[]):
                v=abs(V[n])/Vn[n]; S=S0*(aZ*v*v+aI*v+aP)*1e6/3
                I+=(S/V[n]).conjugate()
            # shunts: line charging half at node, transformer magnetising at HV node
            for y,i in adj[n]:
                a,b,k,p=edges[i]
                if a not in parent or b not in parent: continue
                if k=='lne': I+=V[n]*complex(0,p['B']/2)
                if k=='tr' and n==a: I+=V[n]*p['Ym']/3*0+V[n]*complex(p['Ym'].real,p['Ym'].imag)  # Ym given in S (3-ph MVA/kV^2 == per-phase S)
            # children
            for y,i in adj[n]:
                if parent.get(y)==n:
                    a,b,k,p=edges[i]
                    Ic=Iedge[i]
                    if k=='tr':
                        Ic = Ic/p['a'] if a==n else Ic*p['a']
                    I+=Ic
            if n!=src: Iedge[pedge[n]]=I
            Inode[n]=I
        # forward
        maxd=0
        for n in order[1:]:
            i=pedge[n]; a,b,k,p=edges[i]; par=parent[n]; I=Iedge[i]
            if k=='tr':
                if a==par: Vn_new=V[par]/p['a']-p['Z']*I
                else: Vn_new=V[par]*p['a']-p['Z']*p['a']**2*I
            else: Vn_new=V[par]-p['Z']*I
            maxd=max(maxd,abs(Vn_new-V[n])); V[n]=Vn_new
        if maxd<1e-4: break
    return dict(V=V,Iedge=Iedge,edges=edges,parent=parent,order=order,terms=terms,loads=loads,el_t=el_t,iters=it+1)
def feeder_heads(rows,sol):
    terms=sol['terms']; res={}
    circ={t['loc_name'][5:]:fid for fid,t in terms.items() if re.match(r'A20_C\d\d$',t['loc_name'])}
    for p,n in sorted(circ.items()):
        for i,(a,b,k,pp) in enumerate(sol['edges']):
            if k=='lne' and n in (a,b) and i in sol['Iedge']:
                res[p]=abs(sol['Iedge'][i])
            if k=='tr' and n in (a,b) and i in sol['Iedge']:
                res[p]=abs(sol['Iedge'][i]) if b==n else abs(sol['Iedge'][i])
    return res
if __name__=='__main__':
    rows=parse(sys.argv[1]); zipc=(0,0)
    if '--zip' in sys.argv: k=sys.argv.index('--zip'); zipc=(float(sys.argv[k+1]),float(sys.argv[k+2]))
    sol=solve(rows,zipc,verbose=True)
    fh=feeder_heads(rows,sol)
    print('iters',sol['iters']); print({p:round(v,2) for p,v in fh.items()})
    for nm in ('A20_BB1','A20_BB2','A20_66kV'):
        fid=[f for f,t in rows['ElmTerm'].items() if t['loc_name']==nm][0]
        print(nm, round(abs(sol['V'][fid])*math.sqrt(3)/1000,3),'kV')
