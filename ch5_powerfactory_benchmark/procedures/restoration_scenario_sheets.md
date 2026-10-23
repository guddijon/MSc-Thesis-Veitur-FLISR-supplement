# Restoration scenario sheets (SCN-01 to SCN-15)

Base: winter_peak_boiler_off (10 Dec 2025 17:55 state, D1069 open, D1018 on circuit 22). Solver: offline sweep (`restoration_sweep.py`, adopted 50 % Z / 50 % P mix; matched PowerFactory within 0.13 A on the base case). Fault placement rule: 'feeder head' and 'midline (X)' and 'terminal/branch end (X via Y)' = the whole cable path from the upstream station to X (all GIS segments); 'substation X' = X busbar, every X bay opened, X's own load lost. Thermal check: A20 feeder alarm limits (operating / long-time / short-time, tab:a20_limits); voltage check: lowest station busbar after restoration (limit -5 % = 10.45 kV). Islands and ties are found automatically from the model's normally-open switches; A20 spare bays are not ties. SCN-05 (fault on the SFAA cable, boiler on) and SCN-08 (D1036 midline fault on circuit 22) are at the end of this file.

Conventions: D1032/D1043 and D1067/D1069 are radial ends with no normally-open point (ADMS checked; a tie would create dead sections), so SCN-06 and SCN-11 are 'no restoration path' findings; 157 A on the 160 A operating limit counts as feasible, the alarm limits being conservative against the cable ratings; apart from SCN-05 the scenarios run with the boiler off. Sweep results of tab:pf_scenarios: `data/scenarios/tab_pf_scenarios_sweep.csv`.

Expected head currents of the untouched feeders: 05 69.3 A, 06 39.0 A, 07 109.3 A, 08 13.6 A, 09 13.1 A, 10 35.6 A, 11 4.2 A, 13 95.9 A, 16 312.9 A, 19 1.9 A, 21 36.6 A, 22 117.4 A.

| Scenario | Lost after isolation (kW) | Result |
|---|---|---|
| SCN-01 A20-10 (D1053) feeder head, 3P | 646 | Recommended: close D1022_B-11-01 (normally-open point to D1016, circuit 10 <-> 05) (0 kW remain out). |
| SCN-02 A20-11 (D1055) first substation, SLG | 69 | Recommended: close 1031-1-2 (19 kW remain out). |
| SCN-03 A20-08 terminal (D1062 via D1061), LL | 56 | Recommended: close 1058-1-2 (0 kW remain out). |
| SCN-04 A20-13 midline (D1050), 3P | 1031 | Recommended: close 1058-1-2 (0 kW remain out). |
| SCN-06 A20-09 midline (D1032), SLG | 198 | No restoration path in the model: the island has no normally-open tie. Load stays out until repair. |
| SCN-07 A20-21 substation D1042, 3P | 676 | Recommended: close 1003-1-6 (168 kW remain out). |
| SCN-09 A20-05 (D1070) feeder head, SLG | 1275 | Recommended: close D1022_B-11-01 (normally-open point to D1016, circuit 10 <-> 05) (0 kW remain out). |
| SCN-10 A20-10 midline (D1034), 3P | 399 | Recommended: close D1022_B-11-01 (normally-open point to D1016, circuit 10 <-> 05) (0 kW remain out). |
| SCN-11 A20-11 branch end (D1067 via D1054), SLG | 31 | No restoration path in the model: the island has no normally-open tie. Load stays out until repair. |
| SCN-12 A20-06 midline (D1012), LL | 648 | Recommended: close 1012-1-1 (0 kW remain out). |
| SCN-13 A20-08 substation D1049, 3P | 258 | Recommended: close 1058-1-2 (112 kW remain out). |
| SCN-14 A20-22 (D1028) feeder head, LL | 2150 | Recommended: close 1003-1-6 (0 kW remain out); alternatives R11-204 (SFAA route) or 1018-1-2 (marginal on circuit 06). |
| SCN-15 A20-21 substation D1026, SLG | 508 | Recommended: close 1003-1-6 (268 kW remain out). |

## SCN-01  A20-10 (D1053) feeder head, 3P

**Fault.** cable path A20 -> D1053 (0.015 km, 1 segments: A020-1053A01 - 13).

**Isolation (open).** `1053-1-1`; line-end switches at `A20_C10`, `D1053_F-11-01`.

**After isolation.** Load de-energised 646 kW: D1022_S-11-01 95, D1034_S-11-01 152, D1053_S-11-01 152, D1053_S-11-02 95, D1057_S-11-01 152 (kW). Heads: 16 277.4 A.

**De-energised islands and available ties.**

- D1022, D1034, D1053, D1057 (646 kW): `D1022_B-11-01` (ADMS: Dist Switch Manual, normally open, opposite D1016; model: open cubicle switch on cable 1016-1022A01)

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| `D1022_B-11-01` (ADMS: Dist Switch Manual, normally open, opposite D1016; model: open cubicle switch on cable 1016-1022A01) | D1022, D1034, D1053, D1057 | 05 104.8 (260/280/320) | 11.045 at D1058_BB | 0 | feasible, full restoration |

**Recommended: close D1022_B-11-01 (normally-open point to D1016, circuit 10 <-> 05) (0 kW remain out).**

**PowerFactory.** Scenario `SCN-01_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-01_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-02  A20-11 (D1055) first substation, SLG

**Fault.** busbar of D1055: all bays opened, station load lost.

**Isolation (open).** `1055-1-1` (ADMS D1055 B-11-01, 630 A); `1055-1-2` (ADMS D1055 B-11-02, 630 A).

**After isolation.** Load de-energised 69 kW: D1054_S-11-01 19, D1055_S-11-01 19, D1067_S-11-01 31 (kW). Heads: 16 309.9 A.

**De-energised islands and available ties.**

- D1031, D1054, D1055, D1067, D1069 (50 kW): `1031-1-2` (ADMS D1031 B-11-02, 630 A) from D1031_BB

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1031-1-2 (ADMS D1031 B-11-02, 630 A) from D1031_BB | D1031, D1054, D1055, D1067, D1069 | 09 15.8 (160/180/200), 16 311.8 (1260/1290/1312) | 11.045 at D1058_BB | 19 | feasible, partial |

**Recommended: close 1031-1-2 (19 kW remain out).**

**PowerFactory.** Scenario `SCN-02_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-02_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-03  A20-08 terminal (D1062 via D1061), LL

**Fault.** cable path D1061 -> D1062 (0.360 km, 1 segments: 1061-1062A01 (3 x 240 Al PEX 11 kV)).

**Isolation (open).** `1062-1-2` (ADMS D1062 B11-102, 630 A); `1061-1-1` (ADMS D1061 B11-101, 630 A); line-end switches at `D1061_F-11-01`, `D1062_F-11-02`.

**After isolation.** Load de-energised 56 kW: D1062_S-11-01 56 (kW). Heads: 07 106.6, 08 10.8 A.

**De-energised islands and available ties.**

- D1058, D1062 (56 kW): `1058-1-2` (ADMS D1058 B-11-02, 630 A) from D1058_BB

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1058-1-2 (ADMS D1058 B-11-02, 630 A) from D1058_BB | D1058, D1062 | 08 10.8 (200/220/240), 13 98.7 (160/180/200) | 11.037 at D1062_BB | 0 | feasible, full restoration |

**Recommended: close 1058-1-2 (0 kW remain out).**

**PowerFactory.** Scenario `SCN-03_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-03_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-04  A20-13 midline (D1050), 3P

**Fault.** cable path D1023 -> D1050 (0.439 km, 3 segments: 1023-1050A03 (3 x 240 Al PEX 11kV), 1023-1050A02 (3 x 150 Al + 70 6kV), 1023-1050A01 (3 x 240 Al PEX 11kV)).

**Isolation (open).** `1050-1-2` (ADMS D1050 B-11-02, 630 A); `1023-1-2` (ADMS D1023 B-11-02, 630 A); line-end switches at `D1023_F-11-02`, `D1050_F-11-02`.

**After isolation.** Load de-energised 1031 kW: D1025_S-11-01 126, D1027_S-11-01 159, D1030_S-11-01 202, D1041_S-11-01 126, D1045_S-11-01 40, D1050_S-11-01 126, D1051_S-11-01 126, D1058_S-11-01 126 (kW). Heads: 07 53.4, 13 39.9 A.

**De-energised islands and available ties.**

- D1025, D1027, D1030, D1041, D1045, D1050, D1051, D1058 (1032 kW): `1058-1-2` (ADMS D1058 B-11-02, 630 A) from D1058_F-11-02

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1058-1-2 (ADMS D1058 B-11-02, 630 A) from D1058_F-11-02 | D1025, D1027, D1030, D1041, D1045, D1050, D1051, D1058 | 08 69.6 (200/220/240), 13 39.9 (160/180/200) | 11.104 at D1050_BB | 0 | feasible, full restoration |

**Recommended: close 1058-1-2 (0 kW remain out).**

**PowerFactory.** Scenario `SCN-04_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-04_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-06  A20-09 midline (D1032), SLG

**Fault.** cable path D1031 -> D1032 (1.220 km, 5 segments: 1031-1032A05 (3 x 150 Al PEX 11kV), 1031-1032A04 (3 x 150 Al PEX 11kV), 1031-1032A03 (3 x 150 Al PEX 11kV), 1031-1032A02 (3 x 150 Al PEX 11kV), 1031-1032A01 (3 x 150 Al PEX 11kV)).

**Isolation (open).** `1032-1-1` (ADMS D1032 B-11-01, 630 A); `1031-1-1` (ADMS D1031 B-11-01, 630 A); line-end switches at `D1031_F-11-01`, `D1032_F-11-01`.

**After isolation.** Load de-energised 198 kW: D1032_S-11-01 132, D1043_S-11-01 66 (kW). Heads: 09 2.9, 16 302.5 A.

**De-energised islands and available ties.**

- D1032, D1043 (198 kW): none: no normally-open point reaches this island

**No restoration path in the model: the island has no normally-open tie. Load stays out until repair.**

**PowerFactory.** Scenario `SCN-06_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. No restored scenario (no tie); export the isolated scenario with the line loading table as well. Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-07  A20-21 substation D1042, 3P

**Fault.** busbar of D1042: all bays opened, station load lost.

**Isolation (open).** `1042-1-3`.

**After isolation.** Load de-energised 676 kW: D1001_S-11-01 106, D1002_S-11-01 134, D1026_S-11-01 268, D1042_S-11-01 168 (kW). Heads: 16 276.2, 21 0.7 A.

**De-energised islands and available ties.**

- D1001, D1002, D1026 (508 kW): `1003-1-6` (ADMS D1003 B-11-06, 630 A) from the D1003 side

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1003-1-6 (ADMS D1003 B-11-06, 630 A) from the D1003 side | D1001, D1002, D1026 | 16 303.6 (1260/1290/1312), 21 0.7 (200/220/240), 22 144.9 (260/280/320) | 11.045 at D1058_BB | 168 | feasible, partial |

**Recommended: close 1003-1-6 (168 kW remain out).**

**PowerFactory.** Scenario `SCN-07_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-07_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-09  A20-05 (D1070) feeder head, SLG

**Fault.** cable path A20 -> D1070 (0.482 km, 4 segments: 070 -  - 6116, A020-1070A03 - 13, A020-1070A02 - 13, A020-1070A01 - 13).

**Isolation (open).** line-end switches at `A20_C05`, `D1070_BB`.

**After isolation.** Load de-energised 1275 kW: D1013_S-11-01 210, D1015_S-11-01 131, D1016_S-11-01 131, D1020_S-11-01 83, D1021_S-11-01 131, D1046_S-11-01 131, D1046_S-11-02 131, D1070_S-11-01 327 (kW). Heads: 16 243.6 A.

**De-energised islands and available ties.**

- D1013, D1015, D1016, D1020, D1021, D1046, D1070 (1275 kW): `D1022_B-11-01` (ADMS: Dist Switch Manual, normally open, opposite D1016; model: open cubicle switch on cable 1016-1022A01), `1012-1-1` (ADMS D1012 B-11-01, 630 A) from 012

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| `D1022_B-11-01` (ADMS: Dist Switch Manual, normally open, opposite D1016; model: open cubicle switch on cable 1016-1022A01) | D1013, D1015, D1016, D1020, D1021, D1046, D1070 | 10 104.9 (190/210/230) | 11.045 at D1058_BB | 0 | feasible, full restoration |
| 1012-1-1 (ADMS D1012 B-11-01, 630 A) from 012 | D1013, D1015, D1016, D1020, D1021, D1046, D1070 | 06 108.4 (160/180/200) | 11.045 at D1058_BB | 0 | feasible, full restoration |

**Recommended: close D1022_B-11-01 (normally-open point to D1016, circuit 10 <-> 05) (0 kW remain out).**

**PowerFactory.** Scenario `SCN-09_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-09_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-10  A20-10 midline (D1034), 3P

**Fault.** cable path D1053 -> D1034 (0.282 km, 4 segments: 034 -  - 9191, 1034-1053A01 - 13, 1034-1053A02 - 13, 053 -  - 7442).

**Isolation (open).** `1034--1`; line-end switches at `D1053_BB`.

**After isolation.** Load de-energised 399 kW: D1022_S-11-01 95, D1034_S-11-01 152, D1057_S-11-01 152 (kW). Heads: 10 13.8, 16 291.1 A.

**De-energised islands and available ties.**

- D1022, D1034, D1057 (399 kW): `D1022_B-11-01` (ADMS: Dist Switch Manual, normally open, opposite D1016; model: open cubicle switch on cable 1016-1022A01)

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| `D1022_B-11-01` (ADMS: Dist Switch Manual, normally open, opposite D1016; model: open cubicle switch on cable 1016-1022A01) | D1022, D1034, D1057 | 05 91.1 (260/280/320), 10 13.8 (190/210/230) | 11.045 at D1058_BB | 0 | feasible, full restoration |

**Recommended: close D1022_B-11-01 (normally-open point to D1016, circuit 10 <-> 05) (0 kW remain out).**

**PowerFactory.** Scenario `SCN-10_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-10_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-11  A20-11 branch end (D1067 via D1054), SLG

**Fault.** cable path D1054 -> D1067 (0.334 km, 1 segments: 1054-1067A01 (3 x 240 Al PEX 11kV)).

**Isolation (open).** `1067-1-3` (ADMS D1067 B11-103, 630 A); `1054-1-1`; line-end switches at `D1054_F-11-01`, `D1067_F-11-03`.

**After isolation.** Load de-energised 31 kW: D1067_S-11-01 31 (kW). Heads: 11 2.5, 16 311.6 A.

**De-energised islands and available ties.**

- D1067, D1069 (31 kW): none: no normally-open point reaches this island

**No restoration path in the model: the island has no normally-open tie. Load stays out until repair.**

**PowerFactory.** Scenario `SCN-11_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. No restored scenario (no tie); export the isolated scenario with the line loading table as well. Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-12  A20-06 midline (D1012), LL

**Fault.** cable path D1014 -> D1012 (0.498 km, 5 segments: 012 -  - 7583, 1012-1014A01 - 2, 1012-1014A02 - 2, 1012-1014A03 - 2, 014 -  - 7672).

**Isolation (open).** `1012-1-2` (ADMS D1012 B-11-02, 630 A); `1014-1-2` (ADMS D1014 B-11-02, 400 A).

**After isolation.** Load de-energised 648 kW: D1008_S-11-01 91, D1009_S-11-01 91, D1011_S-11-01 57, D1012_S-11-01 91, D1017_S-11-01 91, D1052_S-11-01 227 (kW). Heads: 06 3.8, 16 277.6 A.

**De-energised islands and available ties.**

- D1008, D1009, D1011, D1012, D1017, D1052 (647 kW): `1012-1-1` (ADMS D1012 B-11-01, 630 A) from CNA3888D43-B485-409B-8144-C89195, `1018-1-2` (ADMS D1018 B-11-02, 630 A) from CNAA9DBD66-E119-4C7F-A03A-0D1154(1)

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1012-1-1 (ADMS D1012 B-11-01, 630 A) from CNA3888D43-B485-409B-8144-C89195 | D1008, D1009, D1011, D1012, D1017, D1052 | 05 104.8 (260/280/320), 06 3.8 (160/180/200) | 11.045 at D1058_BB | 0 | feasible, full restoration |
| 1018-1-2 (ADMS D1018 B-11-02, 630 A) from CNAA9DBD66-E119-4C7F-A03A-0D1154(1) | D1008, D1009, D1011, D1012, D1017, D1052 | 06 3.8 (160/180/200), 22 152.9 (260/280/320) | 11.045 at D1058_BB | 0 | feasible, full restoration |

**Recommended: close 1012-1-1 (0 kW remain out).**

**PowerFactory.** Scenario `SCN-12_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-12_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-13  A20-08 substation D1049, 3P

**Fault.** busbar of D1049: all bays opened, station load lost.

**Isolation (open).** `1049-1-1`; `1049-1-2` (ADMS D1049 B-11-02, 630 A).

**After isolation.** Load de-energised 258 kW: D1049_S-11-01 56, D1049_S-11-02 56, D1061_S-11-01 90, D1062_S-11-01 56 (kW). Heads: 07 95.6, 08 1.0 A.

**De-energised islands and available ties.**

- D1049, D1058, D1061, D1062 (146 kW): `1058-1-2` (ADMS D1058 B-11-02, 630 A) from D1058_BB

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1058-1-2 (ADMS D1058 B-11-02, 630 A) from D1058_BB | D1049, D1058, D1061, D1062 | 07 103.1 (600/615/630), 08 1.0 (200/220/240), 13 103.4 (160/180/200) | 11.028 at D1061_BB | 112 | feasible, partial |

**Recommended: close 1058-1-2 (112 kW remain out).**

**PowerFactory.** Scenario `SCN-13_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-13_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-14  A20-22 (D1028) feeder head, LL

**Fault.** cable path A20 -> D1028 (1.776 km, 5 segments: A020-1028A06 (3 x 240 Al 11 kV), A020-1028A05 (3 x 240 Al PEX 11 kV), A020-1028A03 (3 x 240 Al 11kV), A020-1028A02 (3 x 240 Al PEX 11kV), A020-1028A01 (3 x 240 Al PEX 11kV)).

**Isolation (open).** `1028-1-4` (ADMS D1028 B-11-04, 630 A); line-end switches at `A20_C22`, `D1028_F-11-04`.

**After isolation.** Load de-energised 2150 kW: D1003_S-11-01 121, D1004_S-11-01 303, D1005_S-11-01 303, D1005_S-11-02 388, D1005_S-11-03 303, D1018_S-11-01 78, D1028_S-11-01 194, D1036_S-11-01 97, D1040_S-11-01 121, D1040_S-11-02 121, D1040_S-11-03 121 (kW). Heads: 16 195.7 A.

**De-energised islands and available ties.**

- A20, D1003, D1004, D1005, D1018, D1028, D1036, D1040 (2148 kW): `1018-1-2` (ADMS D1018 B-11-02, 630 A) from CNAA9DBD66-E119-4C7F-A03A-0D1154, `1003-1-6` (ADMS D1003 B-11-06, 630 A) from the D1003 side, `A20_R11-104` from A20_BB1, `A20_R11-204` (circuit 04, SFAA cable; tie 1005-1-1 already closed in the December state)

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1018-1-2 (ADMS D1018 B-11-02, 630 A) from CNAA9DBD66-E119-4C7F-A03A-0D1154 | A20, D1003, D1004, D1005, D1018, D1028, D1036, D1040 | 06 157.0 (160/180/200), 16 313.5 (1260/1290/1312) | 10.943 at D1004_BB | 0 | feasible, full restoration |
| 1003-1-6 (ADMS D1003 B-11-06, 630 A) from the D1003 side | A20, D1003, D1004, D1005, D1018, D1028, D1036, D1040 | 16 313.5 (1260/1290/1312), 21 154.6 (200/220/240) | 11.045 at D1058_BB | 0 | feasible, full restoration |
| A20_R11-204 (circuit 04, SFAA cable; tie 1005-1-1 already closed in the December state) | A20, D1003, D1004, D1005, D1018, D1028, D1036, D1040 | 04 118.2 (260/280/320), 07 227.3 (600/615/630), 16 195.7 (1260/1290/1312) | 11.002 at D1058_BB | 0 | feasible, full restoration |

**Recommended: close 1003-1-6 (0 kW remain out); alternatives: A20_R11-204 via the SFAA cable (circuit 04 118 A, S2 227 A) or 1018-1-2 from circuit 06 (157 A against a 160 A operating limit, marginal).**

**PowerFactory.** Scenario `SCN-14_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-14_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-15  A20-21 substation D1026, SLG

**Fault.** busbar of D1026: all bays opened, station load lost.

**Isolation (open).** open line-end cubicle switch (GUID name in the model); open line-end cubicle switch (GUID name in the model); open line-end cubicle switch (GUID name in the model).

**After isolation.** Load de-energised 508 kW: D1001_S-11-01 106, D1002_S-11-01 134, D1026_S-11-01 268 (kW). Heads: 16 285.2, 21 8.9 A.

**De-energised islands and available ties.**

- D1001, D1002 (240 kW): `1003-1-6` (ADMS D1003 B-11-06, 630 A) from the D1003 side

**Restoration options (sweep).**

| Close | Island fed | Changed head currents (A, limit op/long/short) | Min busbar V (kV) | Load still out (kW) | Verdict |
|---|---|---|---|---|---|
| 1003-1-6 (ADMS D1003 B-11-06, 630 A) from the D1003 side | D1001, D1002 | 16 298.1 (1260/1290/1312), 21 8.9 (200/220/240), 22 130.2 (260/280/320) | 11.045 at D1058_BB | 268 | feasible, partial |

**Recommended: close 1003-1-6 (268 kW remain out).**

**PowerFactory.** Scenario `SCN-15_isolated`: from winter_peak_boiler_off, open the isolation switches above (for a cable-path fault set the listed line segments Out of Service as well, so the fault location is explicit); run; export Breaker/Switch and terminal tables. Scenario `SCN-15_restored`: additionally close the recommended tie; run; export the same plus the line loading table (Lines, Loading %, Current). Expected: head currents of the table row, isolated areas = base count + the faulted section.

## SCN-05  A20-04 (boiler feeder): fault on the SFAA cable, 3P

Base: this case only exists with the boiler on, so it runs on `winter_peak_boiler_on_3.8MW` (R11-204 closed, 1005-1-1 open, boiler 3.8 MW at D1005_F-11-01). Sweep base: circuit 04 199.5 A, S2 306 A, feeder 22 118.3 A, S1 313.7 A.

**Fault.** SFAA cable, A20 bay 04 to the plant connection point D1005_F-11-01 (2.192 km, 7 segments A020-SFAA02..08). No other load on the cable.

**Isolation (open).** `A20_R11-204` (already the fault-clearing breaker) and the cable-end switch at `D1005_F-11-01` (plant end; model cubicle switch Sw_1652_1).

**After isolation.** Boiler network de-energised: 3800 kW. All other feeders unchanged.

**Restoration option.** Close the tie `1005-1-1` (D1005 B-11-01, 400 A bay) and feed the plant from circuit 22 through D1005.

| Case | Circuit 22 head (limit 260/280/320) | S1 | Boiler terminal | Lowest busbar | Verdict |
|---|---|---|---|---|---|
| 3.8 MW | 314 A | 509 A | 10.997 kV | D1018 10.991 kV | exceeds operating and long-time limits, inside the short-time limit only: not a sustained restoration |
| 4.9 MW | 371 A | 566 A | about 10.95 kV | D1018 10.951 kV | exceeds the short-time limit: no restoration |

**Finding.** The tie can carry the plant only as a short-time measure at the measured maximum and not at all at the connection figure; a sustained supply through D1005 requires the boiler to be curtailed to about 2.7 MW (circuit 22 at 260 A: 117.4 A base plus 51.7 A per MW gives 260 A at 2.76 MW).

**PowerFactory.** `SCN-05_isolated`: from winter_peak_boiler_on_3.8MW open R11-204 and set the seven SFAA segments Out of Service; run; export. `SCN-05_restored`: additionally close 1005-1-1; run; export Breaker/Switch, terminals (A20_BB1, D1005_BB, D1005_F-11-01, D1018_BB), lines. Expected: R11-122 about 314 A, S1 about 509 A. Third scenario `SCN-05_restored_4.9MW` with the boiler at 4,9 MW (expected 371 A).

## SCN-08  A20-22 midline (D1036), LL

**Fault.** Cable path D1005 -> D1036 (0.089 km, section 1005-1036A01).

**Isolation (open).** `1005-1-2` (ADMS D1005 B-11-02) and `1036-1-2`; line-end switches at `D1005_F-11-02`, `D1036_F-11-02`.

**After isolation.** 400 kW out: D1036 (97 kW) and D1004 (303 kW). Circuit 22 head 95.3 A.

**Island and tie.** D1036 + D1004; the only normally-open point touching it is `1004-1-2` (D1004 toward D1003). D1003 is itself on circuit 22 (fed D1005 -> D1003 -> D1040 -> D1018), so closing 1004-1-2 re-feeds the island from the other side of the circuit 22 ring, not from circuit 21. The circuit 21 tie 1003-1-6 (D1003 to D1002) does not reach the island.

| Close | Changed head currents | Min busbar V | Load still out | Verdict |
|---|---|---|---|---|
| 1004-1-2 | circuit 22 back to 117.4 A (own ring) | 11.045 kV (unchanged) | 0 kW | feasible, full restoration, same feeder |

**Topology note.** The case is a ring re-closure inside circuit 22, the only one of its kind in the set; the circuit 21 back-feed of circuit 22 is exercised by SCN-14 (feeder head), not here.

**PowerFactory.** `SCN-08_isolated`: open 1005-1-2 and 1036-1-2, line 1005-1036A01 Out of Service; `SCN-08_restored`: close 1004-1-2. Expected: R11-122 117.4 A, D1004 fed through D1003.
