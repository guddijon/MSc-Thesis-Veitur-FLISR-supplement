"""Annual START series for the Reykjavík utility (Orkuveita Reykjavíkur 1996-2013, Veitur from 2014), unplanned
interruptions in its own system. Each year is taken from the newest report that covers it; the revision range across
all reports that list the year is kept. 2024 is added from the thesis table (START report for 2024, Reinholdsdóttir 2025)."""
import csv, sys, collections
R = list(csv.DictReader(open(sys.argv[1])))
best = {}; spread = collections.defaultdict(list)
for r in R:
    k = (r['key'], r['scope'], int(r['year'])); v = float(r['value']); ct = int(r['cover_to'])
    # within one report the TSN minutes table is preferred over the hours table (finer resolution)
    prec = 1 if (r['key'] == 'TSN' and 'mín' in r['title']) else 0
    spread[k].append(v)
    if k not in best or (ct, prec) > (best[k][1], best[k][2]): best[k] = (v, ct, prec, r['report'], r['name'])
rows = []
years = sorted(set(y for _, _, y in best))
for y in years + [2024]:
    row = dict(year=y)
    for key in ['SRA', 'SSO', 'SMA', 'SMS', 'FSN', 'TSN', 'TSF', 'AS']:
        b = best.get((key, 'own', y))
        row[key] = b[0] if b else ''
        if key in ('SMS', 'FSN', 'TSN') and b:
            s = spread[(key, 'own', y)]; row[key + '_rev_min'] = min(s); row[key + '_rev_max'] = max(s)
        if b: row['source_report'] = b[3]; row['name'] = b[4]
    for key in ('FSN', 'TSN', 'SMS'):
        o = best.get((key, 'other', y)); row[key + '_other_system'] = o[0] if o else ''
        g = best.get((key, 'gt3', y)); row[key + '_over_3min'] = g[0] if g else ''
    rows.append(row)
# 2024 from the thesis table (tab:veitur_start, START report for 2024)
T24 = dict(SRA=0.24, SMS=25, FSN=0.37, TSN=25, TSF=1.14, source_report='thesis tab:veitur_start (START 2024 report, Reinholdsdóttir 2025)', name='Veitur')
rows[-1].update(T24)
cols = ['year','name','SRA','SSO','SMA','SMS','FSN','TSN','TSF','AS','SMS_rev_min','SMS_rev_max','FSN_rev_min','FSN_rev_max','TSN_rev_min','TSN_rev_max',
        'SMS_other_system','FSN_other_system','TSN_other_system','SMS_over_3min','FSN_over_3min','TSN_over_3min','source_report']
w = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
