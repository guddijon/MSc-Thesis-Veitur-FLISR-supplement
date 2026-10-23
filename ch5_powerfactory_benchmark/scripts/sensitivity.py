"""Sensitivity of the hold-out metrics to the load model (ZIP variants) and to the within-feeder
distribution (rating share vs stations pinned to their measured transformer current).
Each variant is re-allocated to the A20 head currents exactly as the adopted case (sweep)."""
import os
from paths import data, out
import sys,json,math,csv,io,re,collections,statistics
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from radial_pf import parse,solve,feeder_heads,f
AUG={'A20_R11-105':0,'A20_R11-205':1,'A20_R11-110':0,'A20_R11-210':1,'A20_R11-204':1,'1030-1-2':0,'1058-1-2':1,'1056-1-1':0,'1059-1-2':0,'1005-1-1':0}
CH={'winter_peak_boiler_off':{},'winter_night_min':{},'summer_peak':AUG,'summer_night_min':AUG}
BASE_FIX={'1069-1-2':0}
VARIANTS={'adopted':(0.5,0.0),'Z100':(1.0,0.0),'I100':(0.0,1.0),'P100':(0.0,0.0)}
LABEL={'adopted':'Adopted (50 % Z, 50 % P)','Z100':'Constant impedance (ADMS default)','I100':'Constant current','P100':'Constant power','pinned':'Adopted mix, ComPass transformer currents pinned'}
src_all={r['snapshot']:r for r in csv.DictReader(open(data('snapshot_source_settings.csv')))}
snapI=json.load(open(data('snapshot_feeder_currents.json')))
hold=list(csv.DictReader(open(data('holdout_measured_vs_sweep.csv'))))
def setup(snap):
    rows=parse(data('akranes_11kv_benchmark.dgs')); chg=dict(BASE_FIX,**CH[snap])
    for r in rows['ElmCoup'].values():
        if r['loc_name'] in chg: r['on_off']=str(chg[r['loc_name']])
    Sx=src_all[snap]
    for r in rows['ElmXnet'].values(): r['usetp']=Sx['usetp_pu']
    for r in rows['ElmTr2'].values():
        if r['loc_name']=='S1': r['nntap']=Sx['S1_nntap']
    for r in rows['ElmTr3'].values():
        if r['loc_name']=='S2': r['n3tap_h']=Sx['S2_n3tap_h']
    return rows
def membership(rows):
    terms=rows['ElmTerm']; cub=rows['StaCubic']; sw=rows['StaSwitch']
    open_cub={s['fold_id'] for s in sw.values() if s['on_off']=='0'}
    el_t=collections.defaultdict(dict)
    for c in cub.values():
        if c['FID'] in open_cub: continue
        el_t[c['obj_id']][int(c['obj_bus'])]=c['fold_id']
    adj=collections.defaultdict(set)
    for el,ts in el_t.items():
        kind=next((t for t in ('ElmLne','ElmCoup','ElmTr2','ElmTr3') if el in rows[t]),None)
        if kind is None or (kind=='ElmCoup' and rows['ElmCoup'][el]['on_off']=='0'): continue
        for a in ts.values():
            for b in ts.values():
                if a!=b: adj[a].add(b)
    loads_at=collections.defaultdict(list)
    for el,ts in el_t.items():
        if el in rows['ElmLod'] and 0 in ts: loads_at[ts[0]].append(rows['ElmLod'][el]['loc_name'])
    circ={t['loc_name'][5:]:fid for fid,t in terms.items() if re.match(r'A20_C\d\d$',t['loc_name'])}
    bbn={fid for fid,t in terms.items() if t['loc_name'] in('A20_BB1','A20_BB2')}
    bus_of={}
    for fid,r in rows['ElmCoup'].items():
        if r['loc_name'].startswith('A20_R11') and r['on_off']=='1':
            ts=list(el_t.get(fid,{}).values()); c=[t for t in ts if t in circ.values()]; b=[t for t in ts if t in bbn]
            if c and b: bus_of[[k for k,v in circ.items() if v==c[0]][0]]=terms[b[0]]['loc_name'][-1]
    fl={}
    for p,fid in sorted(circ.items()):
        seen={fid}; st=[fid]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in seen and y not in bbn: seen.add(y); st.append(y)
        fl[p]={'loads':[l for t in seen for l in loads_at[t]],'bus':bus_of.get(p,'open')}
    return fl
def allocate(rows,snap,ZIP,pinned):
    """pinned: {load_name: scale_fixed}. Returns scale dict and solution."""
    fl=membership(rows); sn=snapI[snap]
    MEAS={p:sn[p.zfill(3)]['mean'] for p in fl if fl[p]['bus']!='open' and p not in('07','16','12','01','02','23')}
    zero=feeder_heads(rows,solve(rows,ZIP,{l:0.0 for p in fl for l in fl[p]['loads']}))
    scale=dict(pinned); cum={p:1.0 for p in MEAS}; FIX=set()
    for p,Im in MEAS.items():
        if fl[p]['loads'] and Im<=zero[p]*1.05: FIX.add(p)
    free={p:[l for l in fl[p]['loads'] if l not in pinned] for p in fl}
    for it in range(80):
        sol=solve(rows,ZIP,scale); fh=feeder_heads(rows,sol); maxdev=0
        for p,Im in MEAS.items():
            if p in FIX or not free[p] or Im<=0: continue
            # current of free loads = head current minus (approx) share of pinned; use proportional correction on free loads only
            s=Im/fh[p]
            if pinned:
                # correct only the free part: I_free_new = I_meas - I_pinned, approximated via I_free = fh - I_pinned_est
                Ipin=pinned_current(rows,sol,fl[p]['loads'],pinned)
                Ifree=max(fh[p]-Ipin,1e-6); s=max((Im-Ipin)/Ifree,0.0)
            maxdev=max(maxdev,abs(s-1)); cum[p]*=s
            for l in free[p]: scale[l]=scale.get(l,1.0)*s
        if maxdev<1e-4: break
    ok=[cum[p] for p in cum if p not in FIX and free[p] and MEAS[p]>0]
    mr=statistics.mean(ok)
    for p in FIX:
        cum[p]=mr
        for l in free[p]: scale[l]=mr
    sol=solve(rows,ZIP,scale); fh=feeder_heads(rows,sol)
    return scale,sol,fh,cum,FIX,MEAS
def pinned_current(rows,sol,loads,pinned):
    """sum of HV-side currents of the pinned loads' transformers in this feeder (approx. by load S/(sqrt3 U))."""
    tot=0.0
    for l in loads:
        if l in pinned:
            r=next(x for x in rows['ElmLod'].values() if x['loc_name']==l)
            P=f(r['plini'])*pinned[l]; Q=f(r['qlini'])*pinned[l]
            tot+=math.hypot(P,Q)*1e6/(math.sqrt(3)*11000)
    return tot
def extract(rows,sol):
    name2edge={p['name']:(i,k,p,a,b) for i,(a,b,k,p) in enumerate(sol['edges'])}
    tn={t['loc_name']:fid for fid,t in rows['ElmTerm'].items()}
    def cur(name):
        e=name2edge.get(name)
        if not e or e[0] not in sol['Iedge']: return 0.0
        i,k,p,a,b=e; I=abs(sol['Iedge'][i]); return I/p['a'] if k=='tr' else I
    def U(name):
        fid=tn.get(name); return abs(sol['V'][fid])*math.sqrt(3)/1000 if fid in sol['V'] else None
    return cur,U
def mets(e): return (statistics.mean(map(abs,e)), math.sqrt(statistics.mean(x*x for x in e)), max(map(abs,e)))
out=[]; detail=[]
for snap in ('winter_peak_boiler_off','winter_night_min','summer_peak','summer_night_min'):
    hs=[r for r in hold if r['snapshot']==snap]
    both=[r for r in hs if r['quantity']=='I' and float(r['measured'])>0.5 and r['pf'] not in ('',) and float(r['pf'])>0.5]
    V=[r for r in hs if r['quantity']=='U_LL' and r['pf']!='']
    # pinned loads: stations with a measured transformer bay (ElmTr2 rows), S from measured I and U, pf 0.95
    rows0=setup(snap)
    lod={r['loc_name']:r for r in rows0['ElmLod'].values()}
    pinned={}; pin_st=set()
    for r in hs:
        if r['quantity']=='I' and r['model_class']=='ElmTr2':
            Um=next((float(x['measured']) for x in V if x['station']==r['station']),11.0)
            S=math.sqrt(3)*Um*float(r['measured'])   # kVA
            ln='Load_'+r['model_object']
            if ln in lod and f(lod[ln]['plini'])>0:
                P0=f(lod[ln]['plini'])*1000; pinned[ln]=S*0.95/P0; pin_st.add(r['station'])
    for var in list(VARIANTS)+['pinned']:
        rows=setup(snap); ZIP=VARIANTS['adopted'] if var=='pinned' else VARIANTS[var]
        scale,sol,fh,cum,FIX,MEAS=allocate(rows,snap,ZIP,pinned if var=='pinned' else {})
        cur,U=extract(rows,sol)
        eI=[cur(r['model_object'])-float(r['measured']) for r in both]
        eI_np=[cur(r['model_object'])-float(r['measured']) for r in both if not (var=='pinned' and r['model_class']=='ElmTr2')]
        eV=[100*(U(r['model_object'])-float(r['measured']))/float(r['measured']) for r in V if U(r['model_object'])]
        off=statistics.mean(eV); eVc=[e-off for e in eV]
        rel=[100*(cur(r['model_object'])-float(r['measured']))/float(r['measured']) for r in both]
        headdev=max(abs(fh[p]-MEAS[p]) for p in MEAS if p not in FIX and fh.get(p) is not None)
        rec=dict(snapshot=snap,variant=var,n_bays=len(both),I_MAE=mets(eI)[0],I_RMSE=mets(eI)[1],I_MAD=mets(eI)[2],I_medrel=statistics.median(map(abs,rel)),
                 n_nonpinned=len(eI_np),I_MAE_nonpinned=mets(eI_np)[0],I_RMSE_nonpinned=mets(eI_np)[1],I_MAD_nonpinned=mets(eI_np)[2],
                 V_MAE=mets(eV)[0],V_RMSE=mets(eV)[1],V_MAD=mets(eV)[2],V_offset=off,V_MAE_offsetfree=mets(eVc)[0],V_MAD_offsetfree=mets(eVc)[2],
                 head_maxdev_A=headdev,scale_range='%.3f-%.3f'%(min(cum[p] for p in cum if p not in FIX),max(cum[p] for p in cum if p not in FIX)),
                 totalP_kW=sum(f(lod[l]['plini'])*1000*scale.get(l,1.0) for l in lod if l!='Load_Boiler_Brim_D1005' and any(l in d['loads'] for d in membership(rows).values() if d['bus']!='open')))
        out.append(rec)
        for r in both: detail.append(dict(snapshot=snap,variant=var,station=r['station'],bay=r['bay'],measured=float(r['measured']),model=round(cur(r['model_object']),2)))
        print(f"{snap:24s} {var:8s} bays {len(both)} I MAE {rec['I_MAE']:.2f} RMSE {rec['I_RMSE']:.2f} MAD {rec['I_MAD']:.2f} | non-pinned {rec['n_nonpinned']} MAE {rec['I_MAE_nonpinned']:.2f} | V MAE {rec['V_MAE']:.2f} RMSE {rec['V_RMSE']:.2f} MAD {rec['V_MAD']:.2f} off {off:+.2f} free MAD {rec['V_MAD_offsetfree']:.2f} | heads within {headdev:.2f} A | scales {rec['scale_range']} | P {rec['totalP_kW']:.0f} kW")
    print('   pinned stations:',sorted(pin_st),{k:round(v,2) for k,v in pinned.items()})
with open(out('sensitivity_metrics.csv'),'w',newline='') as fo:
    w=csv.DictWriter(fo,fieldnames=list(out[0].keys())); w.writeheader()
    for r in out: w.writerow({k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()})
with open(out('sensitivity_bays.csv'),'w',newline='') as fo:
    w=csv.DictWriter(fo,fieldnames=list(detail[0].keys())); w.writeheader(); w.writerows(detail)
