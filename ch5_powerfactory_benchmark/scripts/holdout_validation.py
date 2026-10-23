"""Validation metrics (MAE, RMSE, MAD) on the hold-out set for the four snapshots.
Reads holdout_measured_vs_sweep.csv (pf column filled by holdout_pf.py), snapshot_source_settings.csv
(measured A20 busbar voltages) and data/pf_exports/snapshots/<snap>_term.txt (model A20 busbar voltages).
Writes output/holdout_validation_metrics.csv, output/holdout_validation.md and LaTeX rows."""
import os
import csv,statistics,math,os,json
from paths import data, out
SNAPS=['winter_peak_boiler_off','winter_night_min','summer_peak','summer_night_min']
LABEL={'winter_peak_boiler_off':'Winter peak (boiler off)','winter_night_min':'Winter night minimum','summer_peak':'Summer peak','summer_night_min':'Summer night minimum'}
THR=0.5   # A: ComPass tolerance, a bay below this is treated as carrying no current
def read_pf(fn):
    raw=open(fn,'rb').read()
    t=raw.decode('utf-16') if b'\x00' in raw[:200] else raw.decode('utf-8-sig')
    lines=[l.rstrip('\r') for l in t.split('\n') if l.strip()]
    hdr=lines[0].split('\t'); sub=lines[1].split('\t')
    cols=[(h+' '+s).strip() for h,s in zip(hdr,sub+['']*len(hdr))]
    return {l.split('\t')[0].strip():dict(zip(cols,l.split('\t'))) for l in lines[2:]}
def f(s):
    try: return float(str(s).replace(',','.'))
    except: return None
def mae(e): return statistics.mean(abs(x) for x in e)
def rmse(e): return math.sqrt(statistics.mean(x*x for x in e))
def mad(e): return max(abs(x) for x in e)
data=list(csv.DictReader(open(data('holdout_measured_vs_sweep.csv'))))
src={r['snapshot']:r for r in csv.DictReader(open(data('snapshot_source_settings.csv')))}
out=[]; md=[]; tex_v=[]; tex_i=[]; topo=[]
md.append('# Hold-out validation of the Akranes 11 kV benchmark\n')
md.append('Model results from PowerFactory 2025, project Akranes_11kV_benchmark, one operation scenario per snapshot, load flow balanced with voltage dependency of loads. Measurements: ComPass bay currents (phase mean of L1, L2, L3) and line-to-line voltages at the remotely controlled substations, A20 busbar voltages from the station VTs. None of these values was used in tuning (tuning used the A20 feeder-head currents only).\n')
md.append('Metrics as defined in the thesis (subsec:error_metrics): MAE mean absolute error, RMSE root mean squared error, MAD maximum absolute deviation. Reference = measurement, compared = model. Tolerances: ComPass current +/-1 % of reading or +/-0.5 A, whichever is larger; ComPass voltage +/-1 % (calibrated units); A20 VT analogue stored with 0.1 kV resolution (+/-0.45 %).\n')
for s in SNAPS:
    rows=[r for r in data if r['snapshot']==s]
    term=read_pf(data(f'{s}_term.txt'))
    ucol=next(c for c in term['A20_BB1'] if c.startswith('u, Magnitude A'))
    # --- topology agreement classes on telemetered bays
    I=[r for r in rows if r['quantity']=='I']
    cls={'both':0,'neither':0,'meas_only':0,'sim_only':0}; sim_only=[]; meas_only=[]
    for r in I:
        m=float(r['measured']); p=f(r['pf']) if r['pf']!='' else 0.0
        a=m>THR; b=p>THR
        k='both' if a and b else 'neither' if not a and not b else 'meas_only' if a else 'sim_only'
        cls[k]+=1
        if k=='sim_only': sim_only.append(f"{r['station']} {r['bay']} ({p:.1f} A)")
        if k=='meas_only': meas_only.append(f"{r['station']} {r['bay']} ({m:.1f} A)")
    topo.append((s,len(I),cls,sim_only,meas_only))
    # --- A20 busbar voltages
    mb=[float(src[s]['U11_BB1_meas_kV']),float(src[s]['U11_BB2_meas_kV'])]
    pb=[f(term['A20_BB1'][ucol])*11.0,f(term['A20_BB2'][ucol])*11.0]
    eb=[100*(p-m)/m for p,m in zip(pb,mb)]
    # --- substation voltages
    V=[r for r in rows if r['quantity']=='U_LL' and r['pf']!='']
    ev=[100*(float(r['pf'])-float(r['measured']))/float(r['measured']) for r in V]
    off=statistics.mean(ev); ev_c=[e-off for e in ev]
    # --- currents on the "both" class (corrected topology) and on all matched bays
    both=[r for r in I if float(r['measured'])>THR and r['pf']!='' and float(r['pf'])>THR]
    allm=[r for r in I if r['pf']!='']
    def cur(rs):
        e=[float(r['pf'])-float(r['measured']) for r in rs]
        tol=sum(1 for r,x in zip(rs,e) if abs(x)<=max(0.5,0.01*float(r['measured'])))
        return e,tol
    e_b,tol_b=cur(both); e_a,tol_a=cur(allm)
    # --- unbalance (measured) on bays with mean > 1 A
    unb=[]
    for r in I:
        ph=[float(r[k]) for k in ('L1','L2','L3') if r[k] not in ('','None')]
        if len(ph)==3 and min(ph)>0 and float(r['measured'])>1: unb.append(max(ph)/min(ph))
    rec=dict(snapshot=s,bays_telemetered=len(I),both=cls['both'],neither=cls['neither'],meas_only=cls['meas_only'],sim_only=cls['sim_only'],
        a20_points=2,a20_mae_pct=round(mae(eb),2),a20_rmse_pct=round(rmse(eb),2),a20_mad_pct=round(mad(eb),2),
        sub_points=len(V),sub_mae_pct=round(mae(ev),2),sub_rmse_pct=round(rmse(ev),2),sub_mad_pct=round(mad(ev),2),sub_mean_offset_pct=round(off,2),
        sub_mae_offsetfree_pct=round(mae(ev_c),2),sub_mad_offsetfree_pct=round(mad(ev_c),2),
        cur_bays=len(both),cur_mae_A=round(mae(e_b),2),cur_rmse_A=round(rmse(e_b),2),cur_mad_A=round(mad(e_b),2),cur_within_tol=tol_b,
        cur_all_bays=len(allm),cur_all_mae_A=round(mae(e_a),2),cur_all_rmse_A=round(rmse(e_a),2),cur_all_mad_A=round(mad(e_a),2),cur_all_within_tol=tol_a,
        unb_median=round(statistics.median(unb),2),unb_max=round(max(unb),2),unb_n=len(unb))
    out.append(rec)
    # per-station markdown
    md.append(f"\n## {LABEL[s]} ({src[s]['time']})\n")
    md.append(f"Topology classes on {len(I)} telemetered bays (threshold {THR} A): both measured and simulated {cls['both']}, neither {cls['neither']}, measured only {cls['meas_only']}, simulated only {cls['sim_only']}.")
    if meas_only: md.append(f"Measured only: {', '.join(meas_only)}.")
    if sim_only: md.append(f"Simulated only: {', '.join(sim_only)}.")
    md.append(f"\nA20 busbars: measured {mb[0]:.2f}/{mb[1]:.2f} kV, model {pb[0]:.2f}/{pb[1]:.2f} kV, errors {eb[0]:+.2f} %/{eb[1]:+.2f} %.")
    md.append(f"Substation V_LL ({len(V)} points): MAE {mae(ev):.2f} %, RMSE {rmse(ev):.2f} %, MAD {mad(ev):.2f} %, mean offset {off:+.2f} %; after removing the mean offset MAE {mae(ev_c):.2f} %, MAD {mad(ev_c):.2f} %.")
    md.append(f"Currents, both-class bays ({len(both)}): MAE {mae(e_b):.2f} A, RMSE {rmse(e_b):.2f} A, MAD {mad(e_b):.2f} A, within ComPass tolerance {tol_b}/{len(both)}. All matched bays ({len(allm)}): MAE {mae(e_a):.2f} A, RMSE {rmse(e_a):.2f} A, MAD {mad(e_a):.2f} A.")
    md.append(f"Measured phase unbalance (max/min phase, bays above 1 A, n={len(unb)}): median {statistics.median(unb):.2f}, max {max(unb):.2f}; model balanced (1.00).\n")
    md.append('| Station | Bay | Object | Measured | Model | Error | L1/L2/L3 |\n|---|---|---|---|---|---|---|')
    for r in rows:
        if r['quantity']=='I':
            p=r['pf'] if r['pf']!='' else 'open/absent'
            e=f"{float(r['pf'])-float(r['measured']):+.2f} A" if r['pf']!='' else ''
            md.append(f"| {r['station']} | {r['bay']} | {r['model_object']} | {float(r['measured']):.2f} A | {p if p=='open/absent' else format(float(p),'.2f')+' A'} | {e} | {r['L1']}/{r['L2']}/{r['L3']} |")
        else:
            md.append(f"| {r['station']} | V_LL | {r['model_object']} | {float(r['measured']):.3f} kV | {float(r['pf']):.3f} kV | {100*(float(r['pf'])-float(r['measured']))/float(r['measured']):+.2f} % | |")
    # LaTeX rows
    L=LABEL[s]
    tex_v.append(f"{L} & A20 busbar $V$ & 2 & {mae(eb):.2f} & {rmse(eb):.2f} & {mad(eb):.2f} & 0.45 (\\qty{{0.1}}{{\\kilo\\volt}} resolution) & {'yes' if mad(eb)<=0.45 else 'no'} \\\\")
    tex_v.append(f"{L} & Substation $V_{{12}}$ & {len(V)} & {mae(ev):.2f} & {rmse(ev):.2f} & {mad(ev):.2f} & 1 & no (offset {off:+.1f}) \\\\")
    tex_i.append(f"{L} & {len(both)} & {mae(e_b):.2f} & {rmse(e_b):.2f} & {mad(e_b):.2f} & {statistics.median(unb):.2f} (max {max(unb):.2f}) & 1.00 \\\\")
# summary tables at top of md
summ=['\n## Summary\n','| Snapshot | Bays both/neither/meas only/sim only | A20 V MAE/MAD % | Substation V MAE/RMSE/MAD % (offset) | Current bays | I MAE/RMSE/MAD A | within tol | Unbalance median (max) |','|---|---|---|---|---|---|---|---|']
for r in out:
    summ.append(f"| {LABEL[r['snapshot']]} | {r['both']}/{r['neither']}/{r['meas_only']}/{r['sim_only']} | {r['a20_mae_pct']}/{r['a20_mad_pct']} | {r['sub_mae_pct']}/{r['sub_rmse_pct']}/{r['sub_mad_pct']} ({r['sub_mean_offset_pct']:+}) | {r['cur_bays']} | {r['cur_mae_A']}/{r['cur_rmse_A']}/{r['cur_mad_A']} | {r['cur_within_tol']}/{r['cur_bays']} | {r['unb_median']} ({r['unb_max']}) |")
md[3:3]=summ
md.append('\n## LaTeX rows (tab:pf_val_voltage)\n```\n'+'\n'.join(tex_v)+'\n```\n## LaTeX rows (tab:pf_val_current)\n```\n'+'\n'.join(tex_i)+'\n```')
open(out('holdout_validation.md'),'w').write('\n'.join(md)+'\n')
with open(out('holdout_validation_metrics.csv'),'w',newline='') as fo:
    w=csv.DictWriter(fo,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print('\n'.join(summ)); print(); print('\n'.join(tex_v)); print(); print('\n'.join(tex_i))
for t in topo: print(t[0],t[2],'SIM ONLY:',t[3],'MEAS ONLY:',t[4])
