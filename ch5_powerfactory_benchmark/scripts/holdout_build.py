"""Hold-out validation set: measured ComPass values per snapshot vs the sweep prediction,
plus the object list for the PowerFactory selection."""
import os
from paths import data, out
import sys,json,math,csv,io,re,collections,statistics
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from radial_pf import parse,solve,feeder_heads,f
AUG={'A20_R11-105':0,'A20_R11-205':1,'A20_R11-110':0,'A20_R11-210':1,'A20_R11-204':1,'1030-1-2':0,'1058-1-2':1,'1056-1-1':0,'1059-1-2':0,'1005-1-1':0}
SNAPS={'winter_peak_boiler_off':({},data('alloc_wpbo.json'),'scale_per_load'),
       'winter_night_min':({},data('alloc_wnm.json'),'scale'),
       'summer_peak':(AUG,data('alloc_summer_peak.json'),'scale'),
       'summer_night_min':(AUG,data('alloc_summer_night_min.json'),'scale')}
# ADMS bay -> model element (kind, name). Bay n = model bay n where bays exist; GIS-style stations by route.
MAP={
 'D1001':{'101':('ElmLne','1001-1026A01 - 13'),'102':('ElmLne','1001-1002A01 - 13'),'103':('ElmTr2','D1001_S-11-01')},
 'D1004':{'101':('ElmTr2','D1004_S-11-01'),'102':('ElmCoup','1004-1-2'),'103':('ElmCoup','1004-1-3')},
 'D1025':{'101':('ElmCoup','1025-1-1'),'102':('ElmCoup','1025-1-2')},
 'D1026':{'101':('ElmLne','1026-1042A01 - 13'),'102':('ElmLne','1001-1026A03 - 13'),'103':('ElmTr2','D1026_S-11-01')},
 'D1029':{'101':('ElmCoup','1029-1-1'),'102':('ElmCoup','1029-1-2'),'103':('ElmTr2','D1029_S-11-01')},
 'D1030':{'101':('ElmCoup','1030-1-1'),'102':('ElmCoup','1030-1-2'),'103':('ElmTr2','D1030_S-11-01')},
 'D1056':{'101':('ElmCoup','1056-1-1'),'102':('ElmCoup','1056-1-2'),'103':('ElmTr2','D1056_S-11-01')},
 'D1061':{'101':('ElmCoup','1061-1-1'),'102':('ElmCoup','1061-1-2'),'103':('ElmTr2','D1061_S-11-01')},
 'D1062':{'101':('ElmCoup','1062-1-1'),'102':('ElmCoup','1062-1-2'),'103':('ElmTr2','D1062_S-11-01')},
 'D1066':{'101':('ElmCoup','1066-1-1'),'102':('ElmCoup','1066-1-2'),'103':('ElmTr2','D1066_S-11-01')},
 'D1069':{'102':('ElmCoup','1069-1-2'),'104':('ElmTr2','D1069_S-11-01')},
 'D1070':{'101':('ElmLne','1046-1070A04 - 13'),'102':('ElmLne','A020-1070A03 - 13'),'103':('ElmTr2','D1070_S-11-01')},
}
meas=json.load(open(data('holdout_measured.json')))
allrows=[]
for snap,(chg,af,key) in SNAPS.items():
    rows=parse(data('akranes_11kv_benchmark.dgs'))
    for r in rows['ElmCoup'].values():
        if r['loc_name'] in chg: r['on_off']=str(chg[r['loc_name']])
    src={r['snapshot']:r for r in csv.DictReader(open(data('snapshot_source_settings.csv')))}[snap]
    for r in rows['ElmXnet'].values(): r['usetp']=src['usetp_pu']
    for r in rows['ElmTr2'].values():
        if r['loc_name']=='S1': r['nntap']=src['S1_nntap']
    for r in rows['ElmTr3'].values():
        if r['loc_name']=='S2': r['n3tap_h']=src['S2_n3tap_h']
    scale=json.load(open(af))[key]
    # base-file loads already hold the Dec allocation; other scenarios' scales are vs those
    if snap=='winter_peak_boiler_off': scale={}
    sol=solve(rows,(0.5,0),scale)
    name2edge={}
    for i,(a,b,k,p) in enumerate(sol['edges']): name2edge[p['name']]=(i,k,p,a,b)
    tn={t['loc_name']:fid for fid,t in rows['ElmTerm'].items()}
    def cur(kind,name):
        e=name2edge.get(name)
        if not e or e[0] not in sol['Iedge']: return None
        i,k,p,a,b=e; I=abs(sol['Iedge'][i])
        if k=='tr': I=I/p['a']   # HV side
        return I
    def U(name):
        fid=tn.get(name); return abs(sol['V'][fid])*math.sqrt(3)/1000 if fid in sol['V'] else None
    # measured
    m=meas[snap]; I=collections.defaultdict(dict); Uv=collections.defaultdict(list); P={}
    for st,q,bay,ph,v,u in m:
        if q=='I': I[(st,bay)][ph]=v
        elif q=='U' and (('L1L2' in ph or 'L1L3' in ph or 'L2L3' in ph or re.search(r'V\d\d',ph) or ph=='E11_101')) and v>1: Uv[st].append(v)
        elif q=='P': P[(st,bay)]=v
    for st,bays in MAP.items():
        for bay,(kind,nm) in bays.items():
            if (st,bay) not in I: continue
            ph=I[(st,bay)]; mean=statistics.mean(ph.values())
            allrows.append(dict(snapshot=snap,station=st,quantity='I',bay=bay,model_object=nm,model_class=kind,L1=round(ph.get('L1',0),2),L2=round(ph.get('L2',0),2),L3=round(ph.get('L3',0),2),measured=round(mean,2),P_kW=round(P.get((st,bay),0),1),sweep=round(cur(kind,nm) or 0,2),pf=''))
        if Uv[st]:
            allrows.append(dict(snapshot=snap,station=st,quantity='U_LL',bay='',model_object=st+'_BB',model_class='ElmTerm',L1='',L2='',L3='',measured=round(statistics.mean(Uv[st]),3),P_kW='',sweep=round(U(st+'_BB') or 0,3),pf=''))
with open(out('holdout_measured_vs_sweep.csv'),'w',newline='') as fo:
    w=csv.DictWriter(fo,fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
# summary per snapshot
for snap in SNAPS:
    cu=[r for r in allrows if r['snapshot']==snap and r['quantity']=='I' and r['measured']>1]
    vu=[r for r in allrows if r['snapshot']==snap and r['quantity']=='U_LL' and r['measured']>1]
    err=[r['sweep']-r['measured'] for r in cu]; rel=[100*(r['sweep']-r['measured'])/r['measured'] for r in cu]
    verr=[100*(r['sweep']-r['measured'])/r['measured'] for r in vu]
    print(snap,'currents n=%d MAE %.1f A, mean rel %.0f %%, MAD rel %.0f %%'%(len(cu),statistics.mean(abs(e) for e in err),statistics.mean(rel),statistics.median(abs(x) for x in rel)),'| voltages n=%d mean err %.2f %% max %.2f %%'%(len(vu),statistics.mean(verr),max(abs(x) for x in verr)))
    for r in cu+vu: print('   %-6s %-5s %-22s meas %8.2f sweep %8.2f P %s'%(r['station'],r['bay'],r['model_object'][:22],r['measured'],r['sweep'],r['P_kW']))
