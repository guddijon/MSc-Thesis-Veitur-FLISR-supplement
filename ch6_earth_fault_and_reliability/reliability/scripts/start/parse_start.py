"""Extract the Reykjavík utility's rows (Orkuveita Reykjavíkur, later Veitur) from the index tables of the START
reports (Stuðlar um afhendingu raforku). Output: one row per report, table, index, scope, year, value."""
import re, sys, os, glob, csv
TXT = sys.argv[1]
KEYS = [('SEV', r'alvarleika'), ('SRA', r'rofi[ðd] álag'), ('SSO', r'skerta orkuafhendingu'), ('SMA', r'meðalskerðingu álags'),
        ('SMS', r'meðallengd skerðingar'), ('FSN', r'fjölda straumleysistilvika'),
        ('TSF', r'tilvik skerðingar|CAIDI'), ('TSN', r'tímalengd straumleysis á hvern notanda|SAIDI'),
        ('AS', r'Áreiðanleikastuðul')]
ROW = re.compile(r'^\s*(Orkuveita Reykjavíkur|Veitur|Rafveita Reykjavíkur|Rafmagnsveita Reykjavíkur)\s+([-0-9,.\s]+)$')
YEARS = re.compile(r'\b(19[89]\d|20[0-3]\d)\b')
TITLE = re.compile(r'^\s*(TAFLA|Tafla)\s+(\d+)\s+(.*)$')
out = []
for f in sorted(glob.glob(os.path.join(TXT, '*.txt'))):
    rep = os.path.basename(f)[:-4]
    L = open(f, encoding='utf-8', errors='ignore').read().split('\n')
    for i, line in enumerate(L):
        m = TITLE.match(line)
        if not m or '___' in line: continue
        # header: first line after the title with >= 3 years; abort if another title comes first (table of contents)
        hdr = None; title = m.group(3).strip()
        for j in range(i + 1, min(len(L), i + 15)):
            if TITLE.match(L[j]) or '___' in L[j]: break
            ys = YEARS.findall(L[j])
            if len(ys) >= 3 and re.match(r'^\s*(VEITA|Veita|Veitur|Fl\.|\s)', L[j]) and not re.search(r'[a-zþæöð]{4,}.*\d{4}-\d{4}', L[j]):
                hdr = j; break
            if L[j].strip() and not re.search(r'ALLAR TRUFLANIR|TRUFLANIR >', L[j]): title += ' ' + L[j].strip()
        if hdr is None: continue
        key = next((k for k, rx in KEYS if re.search(rx, title, re.I)), None)
        if key in (None, 'SEV'): continue
        years = [int(y) for y in YEARS.findall(L[hdr])]
        split = len(years) != len(set(years))          # "all" and "> 3 min" side by side
        # misprinted headers (e.g. 2022 report, table 9: '2012 ... 2020 2022'): trust the title's range 'árin YYYY-YYYY'
        tr = re.search(r'árin\s+(\d{4})\s*-\s*(\d{4})', title)
        if tr and not split:
            a, b = int(tr.group(1)), int(tr.group(2)); rng = list(range(a, b + 1))
            if len(rng) == len(years) and years != rng: years = rng
        if 'öðru kerfi' in title: scope = 'other'
        elif split: scope = 'split'
        elif re.search(r'leng(ur|ri) en 3', title): scope = 'gt3'
        else: scope = 'own'
        unit = ''
        # units from the unit bracket: 'klst' = hours; 'mínútur/notanda' or 'mín/tilvik' = minutes
        if key == 'TSN': unit = 'h' if re.search(r'klst', title) else ('min' if re.search(r'mínútur/notanda|mín\.?/notanda', title) else 'h')
        if key == 'TSF': unit = 'h' if re.search(r'klst', title) else ('min' if re.search(r'mín/tilvik', title) else 'h')
        for k in range(hdr + 1, min(len(L), hdr + 25)):
            if TITLE.match(L[k]) or re.match(r'^\s*MYND', L[k]): break
            rm = ROW.match(L[k])
            if not rm: continue
            vals = [v for v in rm.group(2).split() if re.match(r'^-?\d+([.,]\d+)?$', v)]
            if split:
                h = len(years) // 2
                pairs = [(y, v, 'all') for y, v in zip(years[:h], vals[:h])] + [(y, v, 'gt3') for y, v in zip(years[h:], vals[h:])]
            else:
                yy = years[-len(vals):] if len(vals) <= len(years) else years
                pairs = [(y, v, scope) for y, v in zip(yy, vals[-len(yy):])]
            for y, v, sc in pairs:
                val = float(v.replace(',', '.'))
                if key == 'TSN' and unit == 'h': val = round(val * 60, 2)
                # 2018 report table 8 is labelled min/tilvik but its values are hours (they equal TSN/FSN in hours)
                if key == 'TSF' and unit == 'min' and val > 10: val = round(val / 60, 3)
                out.append(dict(report=rep, cover_to=max(years), table=m.group(2), key=key, scope=sc, name=rm.group(1), year=y, value=val, title=title[:160]))
w = csv.DictWriter(sys.stdout, fieldnames=['report','cover_to','table','key','scope','name','year','value','title']); w.writeheader(); w.writerows(out)
