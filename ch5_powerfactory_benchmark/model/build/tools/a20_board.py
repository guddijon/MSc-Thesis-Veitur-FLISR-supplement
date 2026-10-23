"""SVG drawing of the A20 switchboard (bays, busbars, breaker states) from a DGS file.
Usage: python3 a20_board.py in.dgs out.svg"""
import io,re,sys
src=sys.argv[1]; out=sys.argv[2]
rows={};cur=None;cols=None
for line in io.open(src,encoding='utf-8'):
    line=line.rstrip('\r\n')
    if line.startswith('$$'):
        hdr=line[2:].split(';'); cur=hdr[0]; cols=[c.split('(')[0] for c in hdr[1:]]; rows.setdefault(cur,[]); continue
    if not line or line.startswith('*') or cur is None: continue
    rows[cur].append(dict(zip(cols,[x.strip() for x in line.split(';')])))
terms={r['FID']:r for r in rows['ElmTerm']}
named={r['FID']:(t,r) for t,l in rows.items() for r in l if 'loc_name' in r}
ends={}
for c in rows['StaCubic']: ends.setdefault(c['obj_id'],[]).append(terms[c['fold_id']]['loc_name'])
bays={}; feed={}; coupler=None
for r in rows['ElmCoup']:
    if not r['loc_name'].startswith('A20_R11'): continue
    e=ends[r['FID']]; st=int(r['on_off']); nm=r['loc_name'][4:]
    circ=[x for x in e if x.startswith('A20_C')]; bb=[x for x in e if x.startswith('A20_BB')]
    if not circ: coupler=(nm,st); continue
    bays.setdefault(circ[0][5:],{})[bb[0][-1]]=(nm,st)
for fid,e in ends.items():
    tab,o=named[fid]
    if tab!='ElmCoup':
        for x in e:
            if re.match(r'A20_C\d\d$',x): feed[x[5:]]=(tab,o['loc_name'])
fdr={m.group(1):f['loc_name'] for f in rows['ElmFeeder'] for m in [re.match(r'A20-(\d\d)',f['loc_name'])] if m}
W,H=2060,700; x0=130; pitch=(W-x0-60)/23
yBB1,yBB2=230,290; ynode=400; ybot=640
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="12">','<rect width="100%" height="100%" fill="white"/>',
 f'<text x="{x0}" y="30" font-size="18" font-weight="bold">A20 Aðveitustöð 20, 11 kV switchboard (Millispennustæði 20-1), snapshot winter_peak_boiler_off, Dec 2025</text>',
 f'<text x="{x0}" y="48" fill="#444">Switch states from the ADMS as in akranes_11kv_benchmark.dgs. Filled square = closed, hollow square = open or withdrawn. R11-1nn connects panel nn to busbar 1, R11-2nn to busbar 2, R11-112 is the bus coupler. Panels in the physical order of the board (ADMS single line, 18 Oct 2026).</text>']
def bus(y,n,c):
    s.append(f'<line x1="{x0-20}" y1="{y}" x2="{W-40}" y2="{y}" stroke="{c}" stroke-width="5"/>'); s.append(f'<text x="{x0-26}" y="{y+4}" text-anchor="end" font-weight="bold" fill="{c}">{n}</text>')
bus(yBB1,'A20_BB1','#1f4e9a'); bus(yBB2,'A20_BB2','#b03a2e')
def sw(x,y,closed,label):
    s.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" fill="{"black" if closed else "white"}" stroke="black" stroke-width="1.5"/>'); s.append(f'<text x="{x+9}" y="{y+4}" font-size="9" fill="#333">{label}</text>')
L='stroke="black" stroke-width="1.5"'
ORDER=['13','23','22','21','20','19','05','14','12','06','11','10','08','09','18','17','15','04','03','16','07','02','01']
for k,nn in enumerate(ORDER,1):
    x=x0+(k-0.5)*pitch
    s.append(f'<text x="{x}" y="90" text-anchor="middle" font-weight="bold" font-size="14">{nn}</text>')
    if nn in fdr: s.append(f'<text x="{x}" y="106" text-anchor="middle" font-size="10" fill="#1f4e9a">feeder {fdr[nn]}</text>')
    if nn not in bays:
        if coupler and nn=='12':
            s.append(f'<line x1="{x}" y1="{yBB1}" x2="{x}" y2="{yBB2}" {L}/>'); sw(x,(yBB1+yBB2)/2,coupler[1],'R11-112 bus coupler ('+('closed' if coupler[1] else 'open')+')')
        continue
    b=bays[nn]
    if '1' in b:
        s.append(f'<line x1="{x}" y1="{yBB1}" x2="{x}" y2="{ynode}" {L}/>'); s.append(f'<circle cx="{x}" cy="{yBB2}" r="5" fill="white" stroke="#b03a2e" stroke-width="1.5"/>'); sw(x,yBB1+22,b['1'][1],b['1'][0])
    if '2' in b:
        xx=x+24
        s.append(f'<polyline points="{xx},{yBB2} {xx},{ynode} {x},{ynode}" fill="none" {L}/>'); sw(xx,yBB2+40,b['2'][1],b['2'][0])
    s.append(f'<circle cx="{x}" cy="{ynode}" r="3" fill="black"/>'); s.append(f'<text x="{x-5}" y="{ynode+4}" text-anchor="end" font-size="9" fill="#555">A20_C{nn}</text>')
    f=feed.get(nn)
    if not f:
        lbl={'01':'station auxiliary transformer','02':'ripple control T1','23':'ripple control T2'}.get(nn,'no circuit in model')
        s.append(f'<text transform="translate({x+4},{ynode+14}) rotate(90)" font-size="10" fill="#888">{lbl}</text>'); continue
    tab,name=f
    if tab in('ElmTr2','ElmTr3'):
        s.append(f'<line x1="{x}" y1="{ynode}" x2="{x}" y2="{ynode+40}" {L}/><circle cx="{x}" cy="{ynode+55}" r="14" fill="none" {L}/><circle cx="{x}" cy="{ynode+73}" r="14" fill="none" {L}/>')
        if tab=='ElmTr3': s.append(f'<circle cx="{x+12}" cy="{ynode+64}" r="14" fill="none" {L}/>')
        s.append(f'<text x="{x}" y="{ynode+108}" text-anchor="middle" font-weight="bold">{name}</text><text x="{x}" y="{ynode+122}" text-anchor="middle" font-size="10">incomer from A20_66kV</text>')
    else:
        s.append(f'<line x1="{x}" y1="{ynode}" x2="{x}" y2="{ybot-30}" {L}/><polyline points="{x-7},{ybot-30} {x},{ybot-18} {x+7},{ybot-30}" fill="none" {L}/>')
        s.append(f'<text transform="translate({x+4},{ynode+14}) rotate(90)" font-size="10">{name.split(" (")[0].split(" - ")[0]}</text>')
s.append('</svg>')
io.open(out,'w',encoding='utf-8').write('\n'.join(s))
print('bays',len(bays),'coupler',coupler,'panel02',bays.get('02'))
