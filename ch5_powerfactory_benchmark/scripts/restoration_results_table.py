import csv, re, json, os
import os
from paths import data, out as out_path, EXPORTS
D=os.path.join(EXPORTS,'restoration_scenarios')+os.sep
def rows(f): return [l.split('\t') for l in open(f,encoding='utf-8',errors='ignore').read().replace('\x00','').splitlines()[2:]]
def f(x): return float(x.replace(',','.'))
HEADS={'05':'A20_R11-105','06':'A20_R11-106','07':'A20_R11-207','08':'A20_R11-208','09':'A20_R11-109','10':'A20_R11-110','11':'A20_R11-111','13':'A20_R11-213','16':'A20_R11-116','19':'A20_R11-119','21':'A20_R11-121','22':'A20_R11-122','04':'A20_R11-204'}
LIM={'05':260,'06':160,'07':260,'08':200,'09':160,'10':190,'11':260,'13':160,'19':210,'21':200,'22':260,'04':260}
def heads(cf):
    out={}
    for p in rows(cf):
        for k,v in HEADS.items():
            if p[0]==v and len(p)>3 and p[3].strip():
                out[k]=f(p[3])*1000
    return out
def areas(lf):
    t=open(lf,encoding='utf-8',errors='ignore').read().replace('\x00','')
    a=re.findall(r'split into (\d+) isolated',t); u=re.findall(r'(\d+) area\(s\) are unsupplied',t)
    return (int(a[-1]),int(u[-1])) if a and u else (None,None)
def vmin(tf):
    best=None
    for p in rows(tf):
        try:
            if f(p[3])==11.0:
                pu=f(p[7])
                if pu>0 and p[0].endswith('_BB') and (best is None or pu<best[0]): best=(pu,p[0])
        except: pass
    return best
def lmax(lf):
    best=None
    for p in rows(lf):
        try:
            v=f(p[3])
            if best is None or v>best[0]: best=(v,p[0],f(p[5])*1000,f(p[6])*1000)
        except: pass
    return best
base=heads(D+'SCN-08_res_coup.txt')  # restored SCN-08 == base state
base['22']=117.4
sw={r['id']:r for r in csv.DictReader(open(data('tab_pf_scenarios_sweep.csv')))}
donor={'SCN-01':('05','circuit 05 via D1022_B-11-01',2),'SCN-02':('09','circuit 09 via 1031-1-2',3),'SCN-03':('13','circuit 13 via 1058-1-2',3),'SCN-04':('08','circuit 08 via 1058-1-2',3),'SCN-05':('22','circuit 22 via 1005-1-1',2),'SCN-06':(None,'none',2),'SCN-07':('22','circuit 22 via 1003-1-6',2),'SCN-08':('22','circuit 22 (own ring) via 1004-1-2',3),'SCN-09':('06','circuit 06 via 1012-1-1',1),'SCN-10':('05','circuit 05 via D1022_B-11-01',2),'SCN-11':(None,'none',2),'SCN-12':('05','circuit 05 via 1012-1-1',3),'SCN-13':('13','circuit 13 via 1058-1-2',3),'SCN-14':('21','circuit 21 via 1003-1-6',2),'SCN-15':('22','circuit 22 via 1003-1-6',1)}
out=[]
for i in range(1,16):
    s=f'SCN-{i:02d}'; d,dn,steps=donor[s]
    iso=heads(D+s+'_iso_coup.txt'); ia=areas(D+s+'_iso_log.txt'); il=lmax(D+s+'_iso_lne.txt') if os.path.exists(D+s+'_iso_lne.txt') else None
    rec={'id':s,'donor':dn,'steps':steps,'iso_areas':ia,'iso_changed':{k:round(v,1) for k,v in iso.items() if abs(v-base.get(k,0))>0.5},'iso_lmax':il}
    if os.path.exists(D+s+'_res_coup.txt'):
        res=heads(D+s+'_res_coup.txt'); ra=areas(D+s+'_res_log.txt'); rl=lmax(D+s+'_res_lne.txt'); rv=vmin(D+s+'_res_term.txt')
        rec.update({'res_areas':ra,'res_changed':{k:round(v,1) for k,v in res.items() if abs(v-base.get(k,0))>0.5},'res_lmax':rl,'res_vmin':rv,
                    'lim_dev':f'{HEADS[d]} {res[d]:.1f} A of {LIM[d]} A','loading_pct':round(100*res[d]/LIM[d],1)})
    else:
        rv=vmin(D+s+'_iso_term.txt'); rec.update({'res_vmin':rv})
    rec['sweep']={k:sw[s][k] for k in ('substations_off_after_isolation','load_restored_kW','load_still_out_kW','vmin_pu','loading_pct_alarm','compliant')}
    out.append(rec)
json.dump(out,open(out_path('restoration_pf_results.json'),'w'),indent=1,default=str)
for r in out:
    print(r['id'],r['iso_areas'],r.get('res_areas'),'| lim',r.get('lim_dev'),r.get('loading_pct'),'| sweep',r['sweep']['loading_pct_alarm'],'| vmin',r['res_vmin'],'| lmax',(r.get('res_lmax') or r['iso_lmax'] or ('',''))[:2],'| still out',r['sweep']['load_still_out_kW'])
