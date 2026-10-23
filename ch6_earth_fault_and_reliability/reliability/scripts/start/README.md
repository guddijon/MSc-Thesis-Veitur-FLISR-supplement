# START reliability series of the Reykjavík utility, 1996-2024

Input: the START reports "Stuðlar um afhendingu raforku" (AFL 2006-2009, EFLA 2010-2024; ISSN 1670-7567); the
PDFs are public and not part of the supplement. Text extracted with `pdftotext -layout`.

1. `parse_start.py <txt-dir>`: every row of Orkuveita Reykjavíkur / Veitur in every index table (SRA, SSO, SMA, SMS,
   FSN, TSN, TSF, AS), with scope own system / other system / all / over 3 min. TSN in minutes, TSF in hours.
   Corrections: titles' year range wins over a misprinted header (2022 report, table 9); the 2018 report's CAIDI
   table labelled min/tilvik holds hours.
2. `build_series.py <raw.csv>`: one row per year from the newest report listing it, with the revision range;
   2024 from the thesis table (START 2015-2024 report).
3. `start_series_fig.py <series.csv> <out>`: three-panel figure TSN, FSN, TSF with ten-year rolling means.

Check: TSN = FSN x TSF x 60 within rounding for all 29 years.
