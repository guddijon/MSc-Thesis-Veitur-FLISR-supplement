"""Restoration scenario evaluation on the Akranes DGS model (winter peak base data).
Builds station-to-station sections, applies a fault (section or station busbar), finds the isolation switches,
the de-energised islands, the normally-open ties that can re-energise them, and evaluates each single tie closure
with the radial sweep (feeder-head currents vs alarm limits, minimum station voltage, loop check)."""
import sys,re,copy,math,collections,json
import radial_pf as rp
from paths import data, out
f=rp.f
LIMITS={'04':(260,280,320),'05':(260,280,320),'11':(260,280,320),'22':(260,280,320),'20':(240,260,280),'19':(210,230,250),
        '08':(200,220,240),'21':(200,220,240),'10':(190,210,230),'06':(160,180,200),'09':(160,180,200),'13':(160,180,200)}
def station_of(name):
    m=re.match(r'(D\d{4})',name)
    if m: return m.group(1)
    if name.startswith('A20'): return 'A20'
    return None
class Net:
    def __init__(self,dgs):
        self.rows0=rp.parse(dgs)
    def graph(self,rows,include_open=False):
        terms=rows['ElmTerm']; cub=rows['StaCubic']; sw=rows['StaSwitch']
        open_cub={s['fold_id']:s for s in sw.values() if s['on_off']=='0'}
        el_t=collections.defaultdict(dict); el_sw=collections.defaultdict(dict)
        for c in cub.values():
            if c['FID'] in open_cub and not include_open: continue
            el_t[c['obj_id']][int(c['obj_bus'])]=c['fold_id']
            if c['FID'] in open_cub: el_sw[c['obj_id']][int(c['obj_bus'])]=open_cub[c['FID']]['loc_name']
        edges=[]
        for fid,r in rows['ElmLne'].items():
            t=el_t.get(fid,{})
            if len(t)==2: edges.append(dict(a=t[0],b=t[1],kind='lne',name=r['loc_name'],fid=fid,open=bool(el_sw.get(fid)),opensw=(list(el_sw[fid].values())[0] if el_sw.get(fid) else None)))
        for fid,r in rows['ElmCoup'].items():
            t=el_t.get(fid,{})
            if len(t)==2: edges.append(dict(a=t[0],b=t[1],kind='cpl',name=r['loc_name'],fid=fid,open=(r['on_off']=='0') or bool(el_sw.get(fid)),opensw=(list(el_sw[fid].values())[0] if el_sw.get(fid) else None)))
        for cls,key in (('ElmTr2','ElmTr2'),('ElmTr3','ElmTr3')):
            for fid,r in rows[cls].items():
                t=el_t.get(fid,{})
                if 0 in t and 1 in t: edges.append(dict(a=t[0],b=t[1],kind='tr',name=r['loc_name'],fid=fid,open=bool(el_sw.get(fid)),opensw=(list(el_sw[fid].values())[0] if el_sw.get(fid) else None)))
        return edges
    def sections(self):
        """station-to-station chains of line segments in the closed/open network (all segments)."""
        rows=self.rows0; terms=rows['ElmTerm']; edges=self.graph(rows,include_open=True)
        st={fid:station_of(t['loc_name']) for fid,t in terms.items()}
        adj=collections.defaultdict(list)
        for i,e in enumerate(edges):
            if e['kind']=='lne': adj[e['a']].append((e['b'],i)); adj[e['b']].append((e['a'],i))
        seen=set(); secs=[]
        for i,e in enumerate(edges):
            if e['kind']!='lne' or i in seen: continue
            # walk both directions through non-station nodes
            chain=[i]; seen.add(i); ends=[]
            for start,prev in ((e['a'],e['b']),(e['b'],e['a'])):
                node=start; last=i
                while st.get(node) is None and len(adj[node])==2:
                    nxt=[(y,j) for y,j in adj[node] if j!=last][0]; node,last=nxt; 
                    if last in seen and last!=i: break
                    seen.add(last); chain.append(last)
                ends.append(node)
            secs.append(dict(edges=sorted(set(chain)),ends=ends,stations=[st.get(n) for n in ends],names=[edges[j]['name'] for j in sorted(set(chain))],
                             km=sum(f(rows['ElmLne'][edges[j]['fid']]['dline']) for j in set(chain))))
        self.edges_all=edges; self.st=st
        return secs
    def solve(self,rows,scale=None):
        sol=rp.solve(rows,(0.5,0.0),scale=scale)   # adopted mix: 50 % Z, 50 % P
        return sol
def apply(rows,sw_changes={},remove_lines=()):
    r=copy.deepcopy(rows)
    byname={x['loc_name']:k for k,x in r['ElmCoup'].items()}
    bysw={x['loc_name']:k for k,x in r['StaSwitch'].items()}
    for n,v in sw_changes.items():
        if n in byname: r['ElmCoup'][byname[n]]['on_off']=str(v)
        elif n in bysw: r['StaSwitch'][bysw[n]]['on_off']=str(v)
        else: raise KeyError(n)
    for fid in remove_lines: r['ElmLne'].pop(fid,None)
    return r
def evaluate(net,rows,label=''):
    sol=net.solve(rows); terms=rows['ElmTerm']
    fh=rp.feeder_heads(rows,sol)
    # loops
    ne=sum(1 for a,b,k,p in sol['edges'] if a in sol['parent'] and b in sol['parent']); loops=ne-(len(sol['order'])-1)
    # min station voltage (BB terminals, energised)
    vmin=(99,None)
    for fid,t in terms.items():
        if t['loc_name'].endswith('_BB') and fid in sol['V']:
            u=abs(sol['V'][fid])*math.sqrt(3)/1000
            if u<vmin[0]: vmin=(u,t['loc_name'])
    # de-energised load
    lost=[]; 
    el_t=sol['el_t']
    for fid,r in rows['ElmLod'].items():
        t=el_t.get(fid,{})
        if 0 in t and t[0] not in sol['parent'] and f(r['plini'])>0: lost.append((r['loc_name'],round(f(r['plini'])*1000)))
    # heaviest line loading (current vs sline)
    worst=(0,None)
    for i,(a,b,k,p) in enumerate(sol['edges']):
        if k=='lne' and i in sol['Iedge']:
            I=abs(sol['Iedge'][i]); 
            if I>worst[0]: worst=(I,p['name'])
    return dict(label=label,heads={k:round(v,1) for k,v in fh.items() if v>0.5},loops=loops,vmin=(round(vmin[0],3),vmin[1]),lost_kW=sum(p for n,p in lost),lost=lost,iters=sol['iters'],worst=(round(worst[0],1),worst[1]),sol=sol)
def head_check(heads):
    out=[]
    for c,I in heads.items():
        if c in LIMITS:
            lo,mid,hi=LIMITS[c]
            flag='ok' if I<=lo else ('>operating' if I<=mid else ('>long-time' if I<=hi else '>SHORT-TIME'))
            if flag!='ok': out.append(f"{c}:{I} A {flag} (limit {lo}/{mid}/{hi})")
    return out
if __name__=="__main__" and "--sections" in sys.argv:
    net=Net(data('akranes_11kv_benchmark.dgs'))
    secs=net.sections()
    print('sections',len(secs))
    for s in secs:
        if None in s['stations'] or s['km']<0.005: continue
        print(s['stations'],round(s['km'],3),s['names'][:3])
    base=evaluate(net,net.rows0,'base'); print('base heads',base['heads'],'loops',base['loops'],'vmin',base['vmin'],'lost',base['lost_kW'])

# ---------------- scenario machinery ----------------
def term_fid(rows,name):
    return [k for k,t in rows['ElmTerm'].items() if t['loc_name']==name][0]
def station_bb(rows,station):
    hits=[k for k,t in rows['ElmTerm'].items() if t['loc_name']==station+'_BB']
    if hits: return hits[0]
    # no named busbar: use the HV terminal of the station transformer
    for fid,r in rows['ElmTr2'].items():
        if r['loc_name'].startswith(station+'_S-11'):
            for c in rows['StaCubic'].values():
                if c['obj_id']==fid and c['obj_bus']=='0': return c['fold_id']
    raise KeyError(station)
def path_to_upstream(net,sol,rows,station):
    """edges (indices into sol['edges']) on the tree path from station BB up to the next station; returns (line edge list, switch names, upstream station, nodes)"""
    terms=rows['ElmTerm']; bb=station_bb(rows,station)
    node=bb; lines=[]; sws=[]; nodes=[bb]
    while True:
        par=sol['parent'].get(node)
        if par is None: return None
        # find the edge between node and par
        for j,(a,b,k,p) in enumerate(sol['edges']):
            if {a,b}=={node,par}: i=j;break
        a,b,k,p=sol['edges'][i]
        if k=='lne': lines.append(i)
        elif k=='cpl': sws.append(p['name'])
        node=par; nodes.append(node)
        stn=station_of(terms[node]['loc_name'])
        if stn=='A20': return lines,sws,stn,nodes
        if stn is not None and stn!=station:
            try: mv=station_bb(rows,stn)
            except KeyError: mv=None
            if node==mv: return lines,sws,stn,nodes
        # stations without a named busbar: their MV node is a numeric terminal; detect by transformer cubicle
        if stn is None and lines:
            for fid,r in rows['ElmTr2'].items():
                if any(c['obj_id']==fid and c['obj_bus']=='0' and c['fold_id']==node for c in rows['StaCubic'].values()):
                    return lines,sws,r['loc_name'][:5],nodes
def line_end_switches(rows,line_fid):
    """names of cubicle switches at both ends of a line (closed ones included)"""
    out=[]
    for c in rows['StaCubic'].values():
        if c['obj_id']==line_fid:
            for s in rows['StaSwitch'].values():
                if s['fold_id']==c['FID']: out.append((rows['ElmTerm'][c['fold_id']]['loc_name'],s['loc_name'],s['on_off']))
    return out
def islands_and_ties(net,rows,sol,base_energised=None):
    """de-energised nodes with load, grouped; open switches linking them to energised nodes"""
    edges=net.graph(rows,include_open=True); terms=rows['ElmTerm']
    energ=set(sol['parent'])
    adj=collections.defaultdict(list)
    for i,e in enumerate(edges):
        if not e['open']: adj[e['a']].append(e['b']); adj[e['b']].append(e['a'])
    # components among non-energised nodes
    comp={}; comps=[]
    for n in terms:
        if n in energ or n in comp: continue
        if base_energised is not None and n not in base_energised: continue
        q=[n]; comp[n]=len(comps); cur=[n]
        while q:
            x=q.pop()
            for y in adj[x]:
                if y not in energ and y not in comp: comp[y]=len(comps); q.append(y); cur.append(y)
        comps.append(cur)
    # loads per component
    el_t=sol['el_t']; loadnode={}
    for fid,r in rows['ElmLod'].items():
        t=el_t.get(fid,{})
        if 0 in t: loadnode.setdefault(t[0],[]).append((r['loc_name'],f(r['plini'])*1000))
    res=[]
    for ci,nodes in enumerate(comps):
        kw=sum(p for n in nodes for nm,p in loadnode.get(n,[])); stns=sorted({station_of(terms[n]['loc_name']) for n in nodes if station_of(terms[n]['loc_name'])})
        if kw<1 and not stns: continue
        if stns==['A20'] or not stns: continue
        ties=[]
        for e in edges:
            if e['open'] and ((e['a'] in nodes and e['b'] in energ) or (e['b'] in nodes and e['a'] in energ)):
                other=e['b'] if e['a'] in nodes else e['a']
                ties.append((e['opensw'] or e['name'], terms[other]['loc_name']))
        res.append(dict(stations=stns,kW=round(kw),ties=ties,nodes=nodes))
    return res
def run_scenario(net,sc):
    rows=net.rows0; base=evaluate(net,rows,'base'); sol=base['sol']
    sol['pedge']={}
    rep=dict(id=sc['id'],title=sc['title'])
    if sc['kind']=='section':
        res=path_to_upstream(net,sol,rows,sc['station'])
        lines,sws,up,nodes=res
        linefids=[sol['edges'][i][3]['name'] for i in lines]
        fids=[k for k,r in rows['ElmLne'].items() if r['loc_name'] in linefids]
        km=sum(f(rows['ElmLne'][k]['dline']) for k in fids)
        ends=set()
        for k in fids:
            for t,s,o in line_end_switches(rows,k):
                if station_of(t): ends.add(t)
        rep.update(fault=f"cable path {up} -> {sc['station']} ({km:.3f} km, {len(fids)} segments: {', '.join(linefids)})",
                   isolation_bay_switches=sws, line_end_cubicle_switches=sorted(ends), upstream=up)
        faulted=apply(rows,remove_lines=fids)
    else:  # busbar
        bb=station_bb(rows,sc['station'])
        r=copy.deepcopy(rows)
        # open every cubicle at the busbar: drop them
        for k in [k for k,c in r['StaCubic'].items() if c['fold_id']==bb]: r['StaCubic'].pop(k)
        bays=[x['loc_name'] for x in rows['ElmCoup'].values() if x['loc_name'].startswith(sc['station'][1:]+'-')]
        # elements connected at the busbar (cubicles) with their switches
        conn=[]
        allel={**rows['ElmLne'],**rows['ElmCoup'],**rows['ElmTr2'],**rows['ElmTr3'],**rows['ElmLod']}
        for c in rows['StaCubic'].values():
            if c['fold_id']==bb:
                sws=[x['loc_name'] for x in rows['StaSwitch'].values() if x['fold_id']==c['FID']]
                conn.append((allel.get(c['obj_id'],{}).get('loc_name','?'),sws[0] if sws else '-'))
        bays=bays or [f"{e} (cubicle switch {s})" for e,s in conn]
        rep.update(fault=f"busbar of {sc['station']}: all bays opened, station load lost",isolation_bay_switches=bays,line_end_cubicle_switches=[],upstream=None)
        faulted=r
    post=evaluate(net,faulted,'isolated')
    base_lost={n for n,p in base['lost']}
    post['lost']=[(n,p) for n,p in post['lost'] if n not in base_lost]; post['lost_kW']=sum(p for n,p in post['lost'])
    rep['after_isolation']=dict(lost_kW=post['lost_kW'],lost=post['lost'],heads=post['heads'],vmin=post['vmin'])
    rep['base_lost']=sorted(base_lost)
    isl=islands_and_ties(net,faulted,post['sol'],set(sol['parent']))
    isl=[i for i in isl if not (i['stations']==[sc['station']] and not i['ties'])]
    rep['islands']=[dict(stations=i['stations'],kW=i['kW'],ties=i['ties']) for i in isl]
    options=[]
    allties=[(t,isl_i) for isl_i,i in enumerate(isl) for t in i['ties'] if not t[0].startswith('A20_R11') or t[0]=='A20_R11-204']
    for (tie,other),isl_i in allties:
        try: rr=apply(faulted,{tie:1})
        except KeyError: continue
        ev=evaluate(net,rr,tie); ev['lost']=[(n,p) for n,p in ev['lost'] if n not in base_lost]; ev['lost_kW']=sum(p for n,p in ev['lost'])
        options.append(dict(tie=tie,feeds_from=other,island=isl[isl_i]['stations'],heads=ev['heads'],flags=head_check(ev['heads']),loops=ev['loops'],vmin=ev['vmin'],lost_kW=ev['lost_kW'],worst=ev['worst']))
    # combination: best single tie per island (fewest flags, then lowest lost) all closed together
    best={}
    for o in options:
        key=tuple(o['island'])
        score=(len(o['flags']),o['loops'],o['lost_kW'])
        if key not in best or score<best[key][0]: best[key]=(score,o)
    if len(best)>1:
        rr=faulted
        for key,(s,o) in best.items(): rr=apply(rr,{o['tie']:1})
        ev=evaluate(net,rr,'combo'); ev['lost']=[(n,p) for n,p in ev['lost'] if n not in base_lost]; ev['lost_kW']=sum(p for n,p in ev['lost']); options.append(dict(tie=' + '.join(o['tie'] for s,o in best.values()),feeds_from='combination',island=['all'],heads=ev['heads'],flags=head_check(ev['heads']),loops=ev['loops'],vmin=ev['vmin'],lost_kW=ev['lost_kW'],worst=ev['worst']))
    rep['options']=options
    return rep
SCN=[
 dict(id='SCN-01',title='A20-10 (D1053) feeder head, 3P',kind='section',station='D1053'),
 dict(id='SCN-02',title='A20-11 (D1055) first substation, SLG',kind='busbar',station='D1055'),
 dict(id='SCN-03',title='A20-08 terminal (D1062 via D1061), LL',kind='section',station='D1062'),
 dict(id='SCN-04',title='A20-13 midline (D1050), 3P',kind='section',station='D1050'),
 dict(id='SCN-06',title='A20-09 midline (D1032), SLG',kind='section',station='D1032'),
 dict(id='SCN-07',title='A20-21 substation D1042, 3P',kind='busbar',station='D1042'),
 dict(id='SCN-09',title='A20-05 (D1070) feeder head, SLG',kind='section',station='D1070'),
 dict(id='SCN-10',title='A20-10 midline (D1034), 3P',kind='section',station='D1034'),
 dict(id='SCN-11',title='A20-11 branch end (D1067 via D1054), SLG',kind='section',station='D1067'),
 dict(id='SCN-12',title='A20-06 midline (D1012), LL',kind='section',station='D1012'),
 dict(id='SCN-13',title='A20-08 substation D1049, 3P',kind='busbar',station='D1049'),
 dict(id='SCN-14',title='A20-22 (D1028) feeder head, LL',kind='section',station='D1028'),
 dict(id='SCN-15',title='A20-21 substation D1026, SLG',kind='busbar',station='D1026'),
]
def main2():
    net=Net(data('akranes_11kv_benchmark.dgs')); net.sections()
    reps=[]
    for sc in SCN:
        try: rep=run_scenario(net,sc)
        except Exception as e:
            import traceback; traceback.print_exc(); rep=dict(id=sc['id'],error=str(e))
        reps.append(rep)
        print(json.dumps({k:v for k,v in rep.items() if k!='options'},default=str)[:900])
        for o in rep.get('options',[]): print('   OPTION',o['tie'],'<-',o['feeds_from'],'island',o['island'],'heads',o['heads'],'flags',o['flags'],'loops',o['loops'],'vmin',o['vmin'],'lost',o['lost_kW'],'worst',o['worst'])
    json.dump(reps,open(out('restoration_eval.json'),'w'),default=str,indent=1)
if __name__=="__main__" and "--sections" not in sys.argv: main2()
