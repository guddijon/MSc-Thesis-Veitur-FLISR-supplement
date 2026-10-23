# Run sheet: restoration scenarios in PowerFactory

Every case = two operation scenarios saved from `winter_peak_boiler_off` (SCN-05 from `winter_peak_boiler_on_3.8MW`): `<id>_isolated` and `<id>_restored`. Work in the Network Model Manager: Line table (Out of Service box), Breaker/Switch table (Closed box), Switch table for cubicle switches, Terminal table (Out of Service box) for busbar faults. Save the scenario (File, Save Operation Scenario) before each load flow.

**Scenario-relevance check, once, at the first pair:** after saving `SCN-05_isolated`, deactivate it (right-click, Deactivate) and look at the SFAA line segments and R11-204 in the base data: they must be back in service and R11-204 open. If the Out of Service flag stays set in the base data, open the line-end cubicle switches instead of using the Out of Service flag.

**Exports per scenario** (Flexible Data, Spread Sheet Format, no filter): isolated: `<id>_iso_coup.txt` (Breaker/Switch currents), `<id>_iso_lne.txt` (Line table with loading and current) and `<id>_iso_log.txt`; restored: `<id>_res_coup.txt`, `<id>_res_term.txt` (Terminal voltages), `<id>_res_lne.txt` (Line table with loading and current, as the hold-out `_lne` exports), `<id>_res_log.txt`. For SCN-06 and SCN-11 there is no restored scenario: export the isolated one with all four files.

**Order:** SCN-05 (boiler-on base), then SCN-01 to SCN-15 in number order. Expected head currents refer to the sweep; PowerFactory should agree within about 1 A.

## SCN-05  SFAA cable fault, base `winter_peak_boiler_on_3.8MW`

- `SCN-05_isolated`: Breaker/Switch `A20_R11-204` Closed unticked; Lines `A020-SFAA02`, `A020-SFAA03`, `A020-SFAA04`, `A020-SFAA05`, `A020-SFAA06`, `A020-SFAA07`, `A020-SFAA08` Out of Service ticked (filter the Line table on `A020-SFAA*`). Save, run. Expected: R11-204 open, R11-122 118.3 A, boiler de-energised, R11-116 313.7 A.
- `SCN-05_restored`: from `SCN-05_isolated` Save as; Breaker/Switch `1005-1-1` Closed ticked. Save, run. Expected: R11-122 about 314 A (exceeds the 260/280 A limits, inside 320 A), R11-116 about 509 A, D1005_F-11-01 about 0.9997 pu, D1018_BB about 0.999 pu.
- `SCN-05_restored_4.9MW` (third scenario): from `SCN-05_restored` Save as; `Load_Boiler_Brim_D1005` P 4,9 MW. Expected R11-122 about 371 A. Exports `SCN-05_res49_coup.txt`, `SCN-05_res49_term.txt`, `SCN-05_res49_lne.txt`, `SCN-05_res49_log.txt`.

## SCN-01  A20-10 (D1053) feeder head, 3P, base `winter_peak_boiler_off`

- `SCN-01_isolated`: Lines `A020-1053A01 - 13` Out of Service ticked; Breaker/Switch `1053-1-1` Closed unticked. Save, run. Expected: R11-116 277.4 A; load out 646 kW (D1022, D1034, D1053, D1053, D1057).
- `SCN-01_restored`: from `SCN-01_isolated` Save as; the normally-open point D1022_B-11-01: in the model it is the open cubicle switch on cable 1016-1022A01 (Switch table, name begins 090A5AEB); set it Closed. Save, run. Expected: R11-105 104.8 A; lowest busbar 11.045 kV at D1058_BB; load still out 0 kW.

## SCN-02  A20-11 (D1055) first substation, SLG, base `winter_peak_boiler_off`

- `SCN-02_isolated`: Terminal `D1055_BB` Out of Service ticked (this opens every bay of the station at once); for the record also untick Closed on `1055-1-1`, `1055-1-2`. Save, run. Expected: R11-116 309.9 A; load out 69 kW (D1054, D1055, D1067).
- `SCN-02_restored`: from `SCN-02_isolated` Save as; Breaker/Switch `1031-1-2` Closed ticked. Save, run. Expected: R11-109 15.8 A, R11-116 311.8 A; lowest busbar 11.045 kV at D1058_BB; load still out 19 kW.

## SCN-03  A20-08 terminal (D1062 via D1061), LL, base `winter_peak_boiler_off`

- `SCN-03_isolated`: Lines `1061-1062A01 (3 x 240 Al PEX 11 kV)` Out of Service ticked; Breaker/Switch `1062-1-2`, `1061-1-1` Closed unticked. Save, run. Expected: R11-207 106.6 A, R11-208 10.8 A; load out 56 kW (D1062).
- `SCN-03_restored`: from `SCN-03_isolated` Save as; Breaker/Switch `1058-1-2` Closed ticked. Save, run. Expected: R11-208 10.8 A, R11-213 98.7 A; lowest busbar 11.037 kV at D1062_BB; load still out 0 kW.

## SCN-04  A20-13 midline (D1050), 3P, base `winter_peak_boiler_off`

- `SCN-04_isolated`: Lines `1023-1050A03 (3 x 240 Al PEX 11kV)`, `1023-1050A02 (3 x 150 Al + 70 6kV)`, `1023-1050A01 (3 x 240 Al PEX 11kV)` Out of Service ticked; Breaker/Switch `1050-1-2`, `1023-1-2` Closed unticked. Save, run. Expected: R11-207 53.4 A, R11-213 39.9 A; load out 1031 kW (D1025, D1027, D1030, D1041, D1045, D1050, D1051, D1058).
- `SCN-04_restored`: from `SCN-04_isolated` Save as; Breaker/Switch `1058-1-2` Closed ticked. Save, run. Expected: R11-208 69.6 A, R11-213 39.9 A; lowest busbar 11.104 kV at D1050_BB; load still out 0 kW.

## SCN-06  A20-09 midline (D1032), SLG, base `winter_peak_boiler_off`

- `SCN-06_isolated`: Lines `1031-1032A05 (3 x 150 Al PEX 11kV)`, `1031-1032A04 (3 x 150 Al PEX 11kV)`, `1031-1032A03 (3 x 150 Al PEX 11kV)`, `1031-1032A02 (3 x 150 Al PEX 11kV)`, `1031-1032A01 (3 x 150 Al PEX 11kV)` Out of Service ticked; Breaker/Switch `1032-1-1`, `1031-1-1` Closed unticked. Save, run. Expected: R11-109 2.9 A, R11-116 302.5 A; load out 198 kW (D1032, D1043).
- No restored scenario: the island has no normally-open point. Export the isolated scenario with all four files.

## SCN-07  A20-21 substation D1042, 3P, base `winter_peak_boiler_off`

- `SCN-07_isolated`: Terminal `042 (the MV terminal of D1042, parent of Cub_D1042_S-11-01_HV)` Out of Service ticked (this opens every bay of the station at once); for the record also untick Closed on `1042-1-3`. Save, run. Expected: R11-116 276.2 A, R11-121 0.7 A; load out 676 kW (D1001, D1002, D1026, D1042).
- `SCN-07_restored`: from `SCN-07_isolated` Save as; Breaker/Switch `1003-1-6` Closed ticked. Save, run. Expected: R11-116 303.6 A, R11-121 0.7 A, R11-122 144.9 A; lowest busbar 11.045 kV at D1058_BB; load still out 168 kW.

## SCN-08  A20-22 midline (D1036), LL, base `winter_peak_boiler_off`

- `SCN-08_isolated`: Lines `1005-1036A01 (3 x 150 Al PEX + 25 11kV)` Out of Service ticked; Breaker/Switch `1036-1-2`, `1005-1-2` Closed unticked. Save, run. Expected: R11-116 290.9 A, R11-122 95.3 A; load out 400 kW (D1004, D1036).
- `SCN-08_restored`: from `SCN-08_isolated` Save as; Breaker/Switch `1004-1-2` Closed ticked. Save, run. Expected: R11-122 117.4 A; lowest busbar 11.045 kV at D1058_BB; load still out 0 kW.

## SCN-09  A20-05 (D1070) feeder head, SLG, base `winter_peak_boiler_off`

- `SCN-09_isolated`: Lines `070 -  - 6116`, `A020-1070A03 - 13`, `A020-1070A02 - 13`, `A020-1070A01 - 13` Out of Service ticked. Save, run. Expected: R11-116 243.6 A; load out 1275 kW (D1013, D1015, D1016, D1020, D1021, D1046, D1046, D1070).
- `SCN-09_restored`: from `SCN-09_isolated` Save as; Breaker/Switch `1012-1-1` Closed ticked. Save, run. Expected: R11-106 108.4 A; lowest busbar 11.045 kV at D1058_BB; load still out 0 kW.
  Alternatives (not run): `090A5AEB-A764-494F-AD8D-0649A15ABC36.1` -> R11-110 104.9 A

## SCN-10  A20-10 midline (D1034), 3P, base `winter_peak_boiler_off`

- `SCN-10_isolated`: Lines `034 -  - 9191`, `1034-1053A01 - 13`, `1034-1053A02 - 13`, `053 -  - 7442` Out of Service ticked; Breaker/Switch `1034--1` Closed unticked. Save, run. Expected: R11-110 13.8 A, R11-116 291.1 A; load out 399 kW (D1022, D1034, D1057).
- `SCN-10_restored`: from `SCN-10_isolated` Save as; the normally-open point D1022_B-11-01: in the model it is the open cubicle switch on cable 1016-1022A01 (Switch table, name begins 090A5AEB); set it Closed. Save, run. Expected: R11-105 91.1 A, R11-110 13.8 A; lowest busbar 11.045 kV at D1058_BB; load still out 0 kW.

## SCN-11  A20-11 branch end (D1067 via D1054), SLG, base `winter_peak_boiler_off`

- `SCN-11_isolated`: Lines `1054-1067A01 (3 x 240 Al PEX 11kV)` Out of Service ticked; Breaker/Switch `1067-1-3`, `1054-1-1` Closed unticked. Save, run. Expected: R11-111 2.5 A, R11-116 311.6 A; load out 31 kW (D1067).
- No restored scenario: the island has no normally-open point. Export the isolated scenario with all four files.

## SCN-12  A20-06 midline (D1012), LL, base `winter_peak_boiler_off`

- `SCN-12_isolated`: Lines `012 -  - 7583`, `1012-1014A01 - 2`, `1012-1014A02 - 2`, `1012-1014A03 - 2`, `014 -  - 7672` Out of Service ticked; Breaker/Switch `1012-1-2`, `1014-1-2` Closed unticked. Save, run. Expected: R11-106 3.8 A, R11-116 277.6 A; load out 648 kW (D1008, D1009, D1011, D1012, D1017, D1052).
- `SCN-12_restored`: from `SCN-12_isolated` Save as; Breaker/Switch `1012-1-1` Closed ticked. Save, run. Expected: R11-105 104.8 A, R11-106 3.8 A; lowest busbar 11.045 kV at D1058_BB; load still out 0 kW.
  Alternatives (not run): `1018-1-2` -> R11-106 3.8 A, R11-122 152.9 A

## SCN-13  A20-08 substation D1049, 3P, base `winter_peak_boiler_off`

- `SCN-13_isolated`: Terminal `D1049_BB` Out of Service ticked (this opens every bay of the station at once); for the record also untick Closed on `1049-1-1`, `1049-1-2`. Save, run. Expected: R11-207 95.6 A, R11-208 1.0 A; load out 258 kW (D1049, D1049, D1061, D1062).
- `SCN-13_restored`: from `SCN-13_isolated` Save as; Breaker/Switch `1058-1-2` Closed ticked. Save, run. Expected: R11-207 103.1 A, R11-208 1.0 A, R11-213 103.4 A; lowest busbar 11.028 kV at D1061_BB; load still out 112 kW.

## SCN-14  A20-22 (D1028) feeder head, LL, base `winter_peak_boiler_off`

- `SCN-14_isolated`: Lines `A020-1028A06 (3 x 240 Al 11 kV)`, `A020-1028A05 (3 x 240 Al PEX 11 kV)`, `A020-1028A03 (3 x 240 Al 11kV)`, `A020-1028A02 (3 x 240 Al PEX 11kV)`, `A020-1028A01 (3 x 240 Al PEX 11kV)` Out of Service ticked; Breaker/Switch `1028-1-4` Closed unticked. Save, run. Expected: R11-116 195.7 A; load out 2150 kW (D1003, D1004, D1005, D1005, D1005, D1018, D1028, D1036, D1040, D1040, D1040).
- `SCN-14_restored`: from `SCN-14_isolated` Save as; Breaker/Switch `1003-1-6` Closed ticked. Save, run. Expected: R11-116 313.5 A, R11-121 154.6 A; lowest busbar 11.045 kV at D1058_BB; load still out 0 kW.
  Alternatives (not run): `1018-1-2` -> R11-106 157.0 A, R11-116 313.5 A; `A20_R11-204` -> R11-204 118.2 A, R11-207 227.3 A, R11-116 195.7 A

## SCN-15  A20-21 substation D1026, SLG, base `winter_peak_boiler_off`

- `SCN-15_isolated`: Terminal `D1026_BB` Out of Service ticked (this opens every bay of the station at once). Save, run. Expected: R11-116 285.2 A, R11-121 8.9 A; load out 508 kW (D1001, D1002, D1026).
- `SCN-15_restored`: from `SCN-15_isolated` Save as; Breaker/Switch `1003-1-6` Closed ticked. Save, run. Expected: R11-116 298.1 A, R11-121 8.9 A, R11-122 130.2 A; lowest busbar 11.045 kV at D1058_BB; load still out 268 kW.

## Close
Activate `winter_peak_boiler_off` and run; R11-116 312.80 A confirms that the scenarios leave the base case unchanged.
