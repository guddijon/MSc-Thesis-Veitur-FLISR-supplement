"""Fill the PowerFactory column of holdout_measured_vs_sweep.csv from the class exports and print metrics."""
import os
from paths import data, out, EXPORTS
import csv,io,sys,glob,statistics,os
def read_pf(fn):
    raw=open(fn,'rb').read()
    if b'\x00' in raw[:200]: t=raw.decode('utf-16')
    else:
        try: t=raw.decode('utf-8-sig')
        except UnicodeDecodeError: t=raw.decode('cp1252')
    lines=[l.rstrip('\r') for l in t.split('\n') if l.strip()]
    hdr=lines[0].split('\t'); sub=lines[1].split('\t')
    cols=[(h+' '+s).strip() for h,s in zip(hdr,sub+['']*len(hdr))]
    rows={}
    for l in lines[2:]:
        v=l.split('\t'); rows[v[0].strip()]=dict(zip(cols,v))
    return cols,rows
def num(s):
    try: return float(str(s).replace(',','.'))
    except: return None
base=os.path.join(EXPORTS,'snapshots')+os.sep
data=list(csv.DictReader(open(data('holdout_measured_vs_sweep.csv'))))
fields=list(data[0].keys())
for snap in sorted({r['snapshot'] for r in data}):
    files={k:base+f'{snap}_{k}.txt' for k in ('coup','tr2','lne','term')}
    if not all(os.path.exists(f) for f in files.values()): continue
    coupc,coup=read_pf(files['coup']); tr2c,tr2=read_pf(files['tr2']); lnec,lne=read_pf(files['lne']); termc,term=read_pf(files['term'])
    def col(cols,key): return next(c for c in cols if key in c)
    cI=col(coupc,'Positive-Sequence Current'); tI=col(tr2c,'Positive-Sequence Current'); lI=col(lnec,'Magnitude A'); tU=col(termc,'u, Magnitude A')
    n=0
    for r in data:
        if r['snapshot']!=snap: continue
        nm=r['model_object']; val=None
        if r['model_class']=='ElmCoup' and nm in coup: val=num(coup[nm][cI])
        elif r['model_class']=='ElmTr2' and nm in tr2: val=num(tr2[nm][tI])
        elif r['model_class']=='ElmLne' and nm in lne: val=num(lne[nm][lI])
        elif r['model_class']=='ElmTerm' and nm in term: val=num(term[nm][tU])
        if val is not None:
            r['pf']=round(val*1000,2) if r['quantity']=='I' else round(val*11.0,3); n+=1
    cu=[r for r in data if r['snapshot']==snap and r['quantity']=='I' and float(r['measured'])>1 and r['pf']!='']
    vu=[r for r in data if r['snapshot']==snap and r['quantity']=='U_LL' and r['pf']!='']
    err=[float(r['pf'])-float(r['measured']) for r in cu]; rel=[100*e/float(r['measured']) for e,r in zip(err,cu)]
    verr=[100*(float(r['pf'])-float(r['measured']))/float(r['measured']) for r in vu]
    dsw=[abs(float(r['pf'])-float(r['sweep'])) for r in cu]
    print(f'{snap}: filled {n}; currents n={len(cu)} MAE {statistics.mean(map(abs,err)):.2f} A, RMSE {statistics.sqrt(statistics.mean(e*e for e in err)) if hasattr(statistics,"sqrt") else (sum(e*e for e in err)/len(err))**0.5:.2f} A, median |rel| {statistics.median(map(abs,rel)):.0f} %; voltages n={len(vu)} mean {statistics.mean(verr):+.2f} % (max {max(map(abs,verr)):.2f} %); PF vs sweep max {max(dsw):.2f} A')
with open(out('holdout_measured_vs_sweep.csv'),'w',newline='') as fo:
    w=csv.DictWriter(fo,fieldnames=fields); w.writeheader(); w.writerows(data)
