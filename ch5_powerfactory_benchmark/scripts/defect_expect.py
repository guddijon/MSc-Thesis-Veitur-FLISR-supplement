"""Offline expectation for the three defect injections with the radial sweep model."""
import sys,copy,math,json
sys.argv.append('--sections')
import restoration_sweep as rs, radial_pf as rp
from paths import data
f=rp.f
net=rs.Net(data('akranes_11kv_benchmark.dgs')); net.sections()
rows0=net.rows0
def busbar_fault(rows,station):
    bb=rs.station_bb(rows,station); r=copy.deepcopy(rows)
    for k in [k for k,c in r['StaCubic'].items() if c['fold_id']==bb]: r['StaCubic'].pop(k)
    return r
def line_fid(rows,name): return [k for k,r in rows['ElmLne'].items() if r['loc_name'].split(' (')[0].split(' - ')[0]==name][0]
def typ_fid(rows,name): return [k for k,t in rows['TypLne'].items() if t['loc_name']==name][0]
def term_v(rows,sol,name):
    fid=rs.station_bb(rows,name.replace('_BB',''))
    return abs(sol['V'][fid])*math.sqrt(3)/1000 if fid in sol['V'] else None
def line_I(sol,names):
    out={}
    for i,(a,b,k,p) in enumerate(sol['edges']):
        if k=='lne' and p['name'].split(' (')[0].split(' - ')[0] in names and i in sol['Iedge']: out[p['name'].split(' (')[0].split(' - ')[0]]=abs(sol['Iedge'][i])
    return out
def report(tag,rows,lines,terms):
    ev=rs.evaluate(net,rows,tag); sol=ev['sol']
    print(f"\n[{tag}] iters {ev['iters']} heads {ev['heads']} vmin {ev['vmin']} lost {ev['lost_kW']} kW")
    for n,I in line_I(sol,lines).items():
        r=rows['ElmLne'][line_fid(rows,n)]; ty=rows['TypLne'][r['typ_id']]
        print(f"   {n:40} I={I:6.1f} A  type={ty['loc_name']:18} sline={f(ty['sline'])*1000:5.0f} A  loading={100*I/(f(ty['sline'])*1000):5.1f} %  L={f(r['dline'])*1000:6.1f} m")
    for t in terms: print(f"   {t:12} {term_v(rows,sol,t):.4f} kV  {term_v(rows,sol,t)/11:.4f} pu")
    return ev
# ---------- D-07: SCN-07 restored, Default_Cable on the 70 Cu PILC back-feed sections
L07=['1002-1003A01','1001-1002A02','1001-1002A04','1001-1002A05','1001-1002A01','1001-1002A03','1001-1026A01','1001-1026A02']
T07=['D1003_BB','D1002_BB','D1001_BB','D1026_BB']
r07=rs.apply(busbar_fault(rows0,'D1042'),{'1003-1-6':1})
base07=report('SCN-07 restored, corrected model',r07,L07,T07)
d07=copy.deepcopy(r07); tdef=typ_fid(d07,'OR_3A_XLPE_240_12')
for n in ['1002-1003A01','1001-1002A02','1001-1002A04','1001-1002A05']: d07['ElmLne'][line_fid(d07,n)]['typ_id']=tdef
def07=report('D-07: same with the four 70 Cu sections typed as Default_Cable (240 Al XLPE)',d07,L07,T07)
# ---------- D-13: SCN-13 restored, A020-1019A03/A04 at 200 m
L13=['A020-1026A01','A020-1026A02','A020-1019A03','A020-1019A04','A020-1019A05','1058-1062A01','1058-1062A02','1061-1062A01']
T13=['D1019_BB','D1058_BB','D1062_BB','D1061_BB','D1051_BB']
r13=rs.apply(busbar_fault(rows0,'D1049'),{'1058-1-2':1})
base13=report('SCN-13 restored, corrected model',r13,L13,T13)
d13=copy.deepcopy(r13)
for n in ['A020-1019A03','A020-1019A04']: d13['ElmLne'][line_fid(d13,n)]['dline']='0.2'
def13=report('D-13: same with A020-1019A03/A04 at 200 m each (ADMS default)',d13,L13,T13)
dbase=copy.deepcopy(rows0)
for n in ['A020-1019A03','A020-1019A04']: dbase['ElmLne'][line_fid(dbase,n)]['dline']='0.2'
report('base winter peak, corrected',rows0,L13[:5],['D1019_BB','D1058_BB','D1062_BB'])
report('base winter peak with the 200 m default',dbase,L13[:5],['D1019_BB','D1058_BB','D1062_BB'])
# ---------- D-08: switch ratings vs 630 A default, from the restored SCN-08 export
print("\n[D-08] SCN-08 restored: switch currents from the PF export against the bay rating and the 630 A default")
def rows_txt(fn): return [l.split('\t') for l in open(fn,encoding='utf-8',errors='ignore').read().replace('\x00','').splitlines()[2:]]
rat={}
import csv
for r in csv.DictReader(open(data('switch_ratings_model_map.csv'))):
    if r['model_object']: rat[r['model_object']]=(r['station'],r['role'],float(r['Ir_bay_A']))
for p in rows_txt(data('SCN-08_res_coup.txt')):
    try: I=float(p[3].replace(',','.'))*1000
    except: continue
    n=p[0].strip()
    if n in rat and (n.startswith(('1004-','1005-','1036-','1003-','1040-','1018-','1028-')) or n.startswith('Cub_D1004')):
        st,role,Ir=rat[n]; print(f"   {n:26} {st} {role:16} I={I:6.1f} A  real {Ir:4.0f} A -> {100*I/Ir:5.1f} %   default 630 A -> {100*I/630:5.1f} %")
    elif n.startswith('A20_R11-1') and I>1:
        print(f"   {n:26} A20 feeder breaker   I={I:6.1f} A  real 1250 A -> {100*I/1250:5.1f} %   default 630 A -> {100*I/630:5.1f} %")
# ---------- D-07b: the same Default_Cable variation with SCN-14 restored (circuit 21 carries all of circuit 22)
fids14=[k for k,r in rows0['ElmLne'].items() if r['loc_name'].split(' (')[0].split(' - ')[0] in ('A020-1028A06','A020-1028A05','A020-1028A03','A020-1028A02','A020-1028A01')]
r14=rs.apply(rows0,{'1028-1-4':0,'1003-1-6':1},remove_lines=fids14)
L14=['1002-1003A01','1001-1002A02','1001-1002A04','1001-1002A05','1001-1026A03','1026-1042A01']
T14=['D1042_BB','D1026_BB','D1001_BB','D1002_BB','D1003_BB','D1004_BB','D1005_BB']
report('SCN-14 restored, corrected model',r14,L14,T14)
d14=copy.deepcopy(r14)
for n in ['1002-1003A01','1001-1002A02','1001-1002A04','1001-1002A05']: d14['ElmLne'][line_fid(d14,n)]['typ_id']=tdef
report('D-07b: SCN-14 restored with the four 70 Cu sections as Default_Cable',d14,L14,T14)
