"""Allocate loads for a snapshot with its own switching state. Usage: snapshot_alloc.py <snapshot>"""
import os
from paths import data, out
import sys,json,math,csv,io,re,collections,statistics
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from radial_pf import parse,solve,feeder_heads,f
snapname=sys.argv[1]
rows=parse(data('akranes_11kv_benchmark.dgs'))
# ---- switching changes vs the December base, model object names (ElmCoup on_off)
AUG={'A20_R11-105':0,'A20_R11-205':1,'A20_R11-110':0,'A20_R11-210':1,'A20_R11-204':1,
     '1030-1-2':0,'1058-1-2':1,'1056-1-1':0,'1059-1-2':0,'1005-1-1':0}
CHANGES={'summer_peak':AUG,'summer_night_min':AUG,'winter_night_min':{},'winter_peak_boiler_off':{}}
# base-data switch states: D1069 de-energised (ADMS open points D1069_T11-101/103)
BASE_FIX={'1069-1-2':0,'1018-1-1':1,'1018-1-2':0}  # D1018 fed from D1040 (ADMS)
chg=dict(BASE_FIX,**CHANGES[snapname])
for r in rows['ElmCoup'].values():
    if r['loc_name'] in chg: r['on_off']=str(chg[r['loc_name']])
src={r['snapshot']:r for r in csv.DictReader(open(data('snapshot_source_settings.csv')))}
Sx=src[snapname]
for r in rows['ElmXnet'].values(): r['usetp']=Sx['usetp_pu']
for r in rows['ElmTr2'].values():
    if r['loc_name']=='S1': r['nntap']=Sx['S1_nntap']
for r in rows['ElmTr3'].values():
    if r['loc_name']=='S2': r['n3tap_h']=Sx['S2_n3tap_h']
# ---- feeder membership by BFS with the snapshot switch states
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
    lds=[l for t in seen for l in loads_at[t]]
    fl[p]={'loads':lds,'stations':sorted({re.sub(r'^Load_(D\d{4}).*',r'\1',l) for l in lds}),'bus':bus_of.get(p,'open')}
dup=collections.Counter(l for p,d in fl.items() if d['bus']!='open' for l in d['loads'])
assert not [k for k,v in dup.items() if v>1], 'load on two energised feeders: '+str([k for k,v in dup.items() if v>1])
print('feeders:',{p:(d['bus'],len(d['stations'])) for p,d in fl.items() if d['loads'] or d['bus']!='open'})
# ---- allocation
snap=json.load(open(data('snapshot_feeder_currents.json')))[snapname]
MEAS={p:snap[p.zfill(3)]['mean'] for p in fl if fl[p]['bus']!='open' and p not in('07','16','12','01','02','23')}
zero=feeder_heads(rows,solve(rows,(0.5,0),{l:0.0 for p in fl for l in fl[p]['loads']}))
ZIP=(0.5,0.0); scale={}; cum={p:1.0 for p in MEAS}; FIX=set()
for p,Im in MEAS.items():
    if fl[p]['loads'] and Im<=zero[p]*1.05: FIX.add(p)
for it in range(60):
    sol=solve(rows,ZIP,scale); fh=feeder_heads(rows,sol); maxdev=0
    for p,Im in MEAS.items():
        if p in FIX or not fl[p]['loads'] or Im<=0: continue
        s=Im/fh[p]; maxdev=max(maxdev,abs(s-1)); cum[p]*=s
        for l in fl[p]['loads']: scale[l]=scale.get(l,1.0)*s
    if maxdev<1e-4: break
ok=[cum[p] for p in cum if p not in FIX and fl[p]['loads'] and MEAS[p]>0]
mean_ratio=statistics.mean(ok)
for p in FIX:
    cum[p]=round(mean_ratio,4)
    for l in fl[p]['loads']: scale[l]=cum[p]
sol=solve(rows,ZIP,scale); fh=feeder_heads(rows,sol)
tn={t['loc_name']:fid for fid,t in terms.items()}
U=lambda n: abs(sol['V'][tn[n]])*math.sqrt(3)/1000
print(snapname,'iters',it+1,'fixed',sorted(FIX),'mean ratio %.4f'%mean_ratio,'BB1 %.3f BB2 %.3f  S1 %.1f (meas %s)  S2 %.1f (meas %s)'%(U('A20_BB1'),U('A20_BB2'),fh['16'],snap['016']['mean'],fh['07'],snap['007']['mean']))
inv={l:p for p,d in fl.items() for l in d['loads'] if d['bus']!='open'}
tot=0; paste=[]
with open(out(f'scenario_{snapname}_loads.csv'),'w',newline='') as fo:
    w=csv.writer(fo); w.writerow(['load','feeder','P0_kW','Q0_kvar','scale_vs_base'])
    for fid,r in sorted(rows['ElmLod'].items(),key=lambda x:x[1]['loc_name']):
        s=scale.get(r['loc_name'],1.0); P=f(r['plini'])*s*1000; Q=f(r['qlini'])*s*1000
        if r['loc_name']!='Load_Boiler_Brim_D1005' and r['loc_name'] in inv: tot+=P
        w.writerow([r['loc_name'],inv.get(r['loc_name'],'-'),round(P,2),round(Q,2),round(s,4)])
        paste.append((r['loc_name'],('%.6f'%(P/1000)).replace('.',','),('%.6f'%(Q/1000)).replace('.',',')))
io.open(out(f'scenario_{snapname}_paste.txt'),'w',encoding='utf-8').write('\n'.join(f'{n}\t{p}\t{q}' for n,p,q in paste)+'\n')
with open(out(f'tuning_{snapname}.csv'),'w',newline='') as fo:
    w=csv.writer(fo); w.writerow(['feeder','busbar','I_meas','I_sim','scale_vs_base','n_substations','note'])
    for p in sorted(fl):
        if p in('01','02','12','23','07','16') : continue
        note='offline sweep'
        if p in FIX: note='not matchable: measured %.2f A at or below the modelled charging current %.2f A; loads set to the mean ratio of the other feeders'%(MEAS[p],zero[p])
        if not fl[p]['loads']: note='no load'
        w.writerow(['A20-'+p,fl[p]['bus'],MEAS.get(p,snap.get(p.zfill(3),{}).get('mean','')),round(fh.get(p,0),2),round(cum.get(p,1),4) if p in cum and fl[p]['loads'] else '',len(fl[p]['stations']),note])
    w.writerow(['S1 (circuit 16)','1',snap['016']['mean'],round(fh['16'],2),'','','busbar 1 %.3f kV, measured %s'%(U('A20_BB1'),Sx['U11_BB1_meas_kV'])])
    w.writerow(['S2 (circuit 07)','2',snap['007']['mean'],round(fh['07'],2),'','','busbar 2 %.3f kV, measured %s'%(U('A20_BB2'),Sx['U11_BB2_meas_kV'])])
print('total energised P0 kW',round(tot,1)); print('station moves:',{p:fl[p]['stations'] for p in ('08','13','19','04')})
json.dump({'scale':scale,'cum':cum,'fl':fl},open(out(f'alloc_{snapname}.json'),'w'))
