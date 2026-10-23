# Hold-out validation set: PowerFactory selection `holdout_set` and variables

Create one general selection in the study case from these 45 objects (Network Model
Manager, class by class, select the rows, Selections, Set - General, first New then add to
the existing set). Export the Flexible Data of the set from each of the four scenarios
(Data Manager, select the set, Detail Mode, Flexible Data, one class at a time, Spread Sheet
Format) and save the four files. Measured values and the sweep prediction are in
`holdout_measured_vs_sweep.csv` (per-bay measurements, not part of the supplement); the PowerFactory column is filled from these exports
(`scripts/holdout_pf.py`).

## Breaker/Switch (ElmCoup), variable I:bus1 (A, B, C) as already defined
1004-1-2, 1004-1-3, 1025-1-1, 1025-1-2, 1029-1-1, 1029-1-2, 1030-1-1, 1030-1-2,
1056-1-1, 1056-1-2, 1061-1-1, 1061-1-2, 1062-1-1, 1062-1-2, 1066-1-1, 1066-1-2, 1069-1-2

## Line (ElmLne), stations modelled with GIS stubs; add variables I:bus1 and I:bus2 (kA, 5 decimals)
| line | station | ADMS bay | station end |
|---|---|---|---|
| 1001-1026A01 - 13 | D1001 | 101 | bus1 |
| 1001-1002A01 - 13 | D1001 | 102 | bus1 |
| 1026-1042A01 - 13 | D1026 | 101 | bus1 |
| 1001-1026A03 - 13 | D1026 | 102 | bus1 |
| 1046-1070A04 - 13 | D1070 | 101 | bus2 |
| A020-1070A03 - 13 | D1070 | 102 | bus1 |
(read the current at the station end; the other end differs only by the charging current)

## 2-Winding Transformer (ElmTr2), add variable I:bushv (HV current, kA, 5 decimals)
D1001_S-11-01, D1004_S-11-01, D1026_S-11-01, D1029_S-11-01, D1030_S-11-01, D1056_S-11-01,
D1061_S-11-01, D1062_S-11-01, D1066_S-11-01, D1069_S-11-01, D1070_S-11-01

## Terminal (ElmTerm), variables Ul and u as defined
D1001_BB, D1004_BB, D1025_BB, D1026_BB, D1029_BB, D1030_BB, D1056_BB, D1061_BB, D1062_BB,
D1066_BB, D1069_BB, D1070_BB

## Mapping rule
ADMS bay n of a station is model bay n (checked on the flow direction at D1025, D1029,
D1030, D1056, D1066, D1058). Transformer bays: D1001/D1026/D1029/D1030/D1056/D1061/D1062/
D1066/D1070 bay 103, D1004 bay 101 (bay 104 = second transformer, not in the model, reads 0),
D1069 bay 104. D1025 has no transformer measurement. Voltages: the ComPass line-to-line
values (one per station, or the mean of the three where all are measured) against the
station busbar.
