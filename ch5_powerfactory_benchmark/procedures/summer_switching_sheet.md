# Switching sheet for the August 2026 scenarios (summer_peak, summer_night_min)

Both snapshots share one switching state. Start from the December base scenario state,
create the new scenario, activate it, then make these changes **with the scenario active**.
Switch states: Network Model Manager, Breaker/Switch, Basic Data tab, column "Closed"
(or open the element and tick/untick Closed). ADMS alias in brackets.

## A20 switchboard (extract a20_breaker_states_by_snapshot.csv)
| model object | action | why |
|---|---|---|
| A20_R11-105 | open | circuit 05 moves to busbar 2 (105 withdrawn) |
| A20_R11-205 | close | |
| A20_R11-110 | open | circuit 10 moves to busbar 2 (110 withdrawn) |
| A20_R11-210 | close | |
| A20_R11-204 | close | boiler bay on busbar 2, boiler itself off (Cub_Boiler stays open) |
| A20_R11-116 | keep closed | extract says "open (racked in)": known gap in the switching log, S1 carried 98 A |

## Distribution network (extracts akranes_open_points / switch_states_by_snapshot.csv)
| model object | action | ADMS | effect |
|---|---|---|---|
| 1030-1-2 (D1030 bay to D1027) | open | D1030_B11-102 open | D1030, D1041, D1045, D1051, D1058 leave feeder 13 |
| 1058-1-2 (D1058 bay to D1062) | close | D1058_B-11-02 closed | ... and join feeder 08 through D1062 (D1062_T11-101 closed, model 1062-1-1 already closed) |
| 1056-1-1 (D1056 bay to D1059) | open | D1056_T11-101 open | D1059 disconnected |
| 1059-1-2 (D1059 bay to D1056) | open | D1059 all open | |
| 1005-1-1 (D1005 bay to the boiler cable A020-SFAA) | open | ASSUMPTION | with 204 closed the boiler cable would otherwise couple busbar 2 to feeder 22 on busbar 1; measured 04 current 0.0 A and S2 = sum of 05+08+10+13 show no coupling, so the cable is energised from A20 and open at D1005 |

Not in the model, no action: D1071 (bays 101-103 closed in August, station not in the
inventory), D1072 (all open), D1053_R-11-01 (NULL -> closed, model already closed).

## Snapshot settings
| scenario | time | external grid usetp | S1 tap | S2 HV tap | measured busbars kV |
|---|---|---|---|---|---|
| summer_peak | 2026-08-24 18:45 | 0.9961 | -3 (pos 17) | +1 (pos 10) | 11.23 / 11.27 |
| summer_night_min | 2026-08-03 06:15 | 1.0005 | -2 (pos 16) | +2 (pos 9) | 11.23 / 11.17 |

Loads: paste files `scenario_summer_peak_paste.txt` and `scenario_summer_night_min_paste.txt`
(name, P MW, Q Mvar, decimal comma, sorted by name). Expected head currents after the
load flow: `tuning_summer_peak.csv` and `tuning_summer_night_min.csv` (column I_sim).
Feeder membership check in the sweep: 08 = D1049, D1061, D1062, D1030, D1041, D1045, D1051,
D1058 (8 stations); 13 = D1019, D1029, D1066, D1023, D1050, D1025, D1027 (7); 19 = D1056.
Cross-check of the sweep: summer_peak S1 98.4 A (measured 97.9), S2 187.2 A (measured 187.6);
summer_night_min S1 48.1 (50.2), S2 70.8 (67.2).
