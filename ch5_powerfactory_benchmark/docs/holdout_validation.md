# Hold-out validation of the Akranes 11 kV benchmark

Model results from PowerFactory 2025, project Akranes_11kV_benchmark, one operation scenario per snapshot, load flow balanced with voltage dependency of loads. Measurements: ComPass bay currents (phase mean of L1, L2, L3) and line-to-line voltages at the remotely controlled substations, A20 busbar voltages from the station VTs. None of these values was used in tuning (tuning used the A20 feeder-head currents only).

Metrics as defined in the thesis (subsec:error_metrics): MAE mean absolute error, RMSE root mean squared error, MAD maximum absolute deviation. Reference = measurement, compared = model. Tolerances: ComPass current +/-1 % of reading or +/-0.5 A, whichever is larger; ComPass voltage +/-1 % (calibrated units); A20 VT analogue stored with 0.1 kV resolution (+/-0.45 %).


## Summary

| Snapshot | Bays both/neither/meas only/sim only | A20 V MAE/MAD % | Substation V MAE/RMSE/MAD % (offset) | Current bays | I MAE/RMSE/MAD A | within tol | Unbalance median (max) |
|---|---|---|---|---|---|---|---|
| Winter peak (boiler off) | 22/4/2/6 | 0.37/0.38 | 1.76/1.8/2.33 (+1.76) | 22 | 4.77/6.57/14.59 | 3/22 | 1.13 (1.33) |
| Winter night minimum | 22/4/2/6 | 0.3/0.45 | 2.07/2.1/2.71 (+2.07) | 22 | 1.4/1.96/4.98 | 8/22 | 1.12 (1.29) |
| Summer peak | 25/5/2/2 | 0.18/0.25 | 1.55/1.6/2.2 (+1.55) | 25 | 2.94/4.41/10.7 | 5/25 | 1.09 (1.27) |
| Summer night minimum | 25/5/2/2 | 0.26/0.28 | 1.77/1.81/2.33 (+1.77) | 25 | 2.45/3.75/12.81 | 6/25 | 1.09 (1.35) |

## Winter peak (boiler off) (2025-12-10 17:55)

Topology classes on 34 telemetered bays (threshold 0.5 A): both measured and simulated 22, neither 4, measured only 2, simulated only 6.
Measured only: D1056 102 (2.0 A), D1056 103 (1.5 A).
Simulated only: D1061 101 (3.0 A), D1061 102 (7.7 A), D1061 103 (5.0 A), D1062 101 (1.1 A), D1062 102 (2.9 A), D1062 103 (3.1 A).

A20 busbars: measured 11.17/11.23 kV, model 11.21/11.19 kV, errors +0.35 %/-0.38 %.
Substation V_LL (10 points): MAE 1.76 %, RMSE 1.80 %, MAD 2.33 %, mean offset +1.76 %; after removing the mean offset MAE 0.34 %, MAD 0.66 %.
Currents, both-class bays (22): MAE 4.77 A, RMSE 6.57 A, MAD 14.59 A, within ComPass tolerance 3/22. All matched bays (33): MAE 3.96 A, RMSE 5.67 A, MAD 14.59 A.
Measured phase unbalance (max/min phase, bays above 1 A, n=24): median 1.13, max 1.33; model balanced (1.00).

(per-bay table withheld in the public repository; station-level summary in data/validation/holdout_station_summary.csv)

## Winter night minimum (2025-12-25 06:25)

Topology classes on 34 telemetered bays (threshold 0.5 A): both measured and simulated 22, neither 4, measured only 2, simulated only 6.
Measured only: D1056 102 (1.5 A), D1056 103 (1.0 A).
Simulated only: D1061 101 (2.0 A), D1061 102 (4.7 A), D1061 103 (3.1 A), D1062 101 (1.1 A), D1062 102 (1.9 A), D1062 103 (1.9 A).

A20 busbars: measured 11.17/11.17 kV, model 11.22/11.19 kV, errors +0.45 %/+0.15 %.
Substation V_LL (10 points): MAE 2.07 %, RMSE 2.10 %, MAD 2.71 %, mean offset +2.07 %; after removing the mean offset MAE 0.30 %, MAD 0.64 %.
Currents, both-class bays (22): MAE 1.40 A, RMSE 1.96 A, MAD 4.98 A, within ComPass tolerance 8/22. All matched bays (33): MAE 1.43 A, RMSE 1.96 A, MAD 4.98 A.
Measured phase unbalance (max/min phase, bays above 1 A, n=24): median 1.12, max 1.29; model balanced (1.00).

(per-bay table withheld in the public repository; station-level summary in data/validation/holdout_station_summary.csv)

## Summer peak (2026-08-24 18:45)

Topology classes on 34 telemetered bays (threshold 0.5 A): both measured and simulated 25, neither 5, measured only 2, simulated only 2.
Measured only: D1056 102 (0.8 A), D1056 103 (0.8 A).
Simulated only: D1061 103 (6.1 A), D1062 103 (3.8 A).

A20 busbars: measured 11.23/11.27 kV, model 11.24/11.24 kV, errors +0.11 %/-0.25 %.
Substation V_LL (10 points): MAE 1.55 %, RMSE 1.60 %, MAD 2.20 %, mean offset +1.55 %; after removing the mean offset MAE 0.38 %, MAD 0.65 %.
Currents, both-class bays (25): MAE 2.94 A, RMSE 4.41 A, MAD 10.70 A, within ComPass tolerance 5/25. All matched bays (31): MAE 2.74 A, RMSE 4.16 A, MAD 10.70 A.
Measured phase unbalance (max/min phase, bays above 1 A, n=25): median 1.09, max 1.27; model balanced (1.00).

(per-bay table withheld in the public repository; station-level summary in data/validation/holdout_station_summary.csv)

## Summer night minimum (2026-08-03 06:15)

Topology classes on 34 telemetered bays (threshold 0.5 A): both measured and simulated 25, neither 5, measured only 2, simulated only 2.
Measured only: D1056 102 (0.8 A), D1056 103 (0.8 A).
Simulated only: D1061 103 (2.2 A), D1062 103 (1.4 A).

A20 busbars: measured 11.23/11.17 kV, model 11.20/11.14 kV, errors -0.28 %/-0.24 %.
Substation V_LL (10 points): MAE 1.77 %, RMSE 1.81 %, MAD 2.33 %, mean offset +1.77 %; after removing the mean offset MAE 0.29 %, MAD 0.56 %.
Currents, both-class bays (25): MAE 2.45 A, RMSE 3.75 A, MAD 12.81 A, within ComPass tolerance 6/25. All matched bays (31): MAE 2.13 A, RMSE 3.39 A, MAD 12.81 A.
Measured phase unbalance (max/min phase, bays above 1 A, n=25): median 1.09, max 1.35; model balanced (1.00).

(per-bay table withheld in the public repository; station-level summary in data/validation/holdout_station_summary.csv)

## LaTeX rows (tab:pf_val_voltage)
```
Winter peak (boiler off) & A20 busbar $V$ & 2 & 0.37 & 0.37 & 0.38 & 0.45 (\qty{0.1}{\kilo\volt} resolution) & yes \\
Winter peak (boiler off) & Substation $V_{12}$ & 10 & 1.76 & 1.80 & 2.33 & 1 & no (offset +1.8) \\
Winter night minimum & A20 busbar $V$ & 2 & 0.30 & 0.33 & 0.45 & 0.45 (\qty{0.1}{\kilo\volt} resolution) & yes \\
Winter night minimum & Substation $V_{12}$ & 10 & 2.07 & 2.10 & 2.71 & 1 & no (offset +2.1) \\
Summer peak & A20 busbar $V$ & 2 & 0.18 & 0.19 & 0.25 & 0.45 (\qty{0.1}{\kilo\volt} resolution) & yes \\
Summer peak & Substation $V_{12}$ & 10 & 1.55 & 1.60 & 2.20 & 1 & no (offset +1.5) \\
Summer night minimum & A20 busbar $V$ & 2 & 0.26 & 0.26 & 0.28 & 0.45 (\qty{0.1}{\kilo\volt} resolution) & yes \\
Summer night minimum & Substation $V_{12}$ & 10 & 1.77 & 1.81 & 2.33 & 1 & no (offset +1.8) \\
```
## LaTeX rows (tab:pf_val_current)
```
Winter peak (boiler off) & 22 & 4.77 & 6.57 & 14.59 & 1.13 (max 1.33) & 1.00 \\
Winter night minimum & 22 & 1.40 & 1.96 & 4.98 & 1.12 (max 1.29) & 1.00 \\
Summer peak & 25 & 2.94 & 4.41 & 10.70 & 1.09 (max 1.27) & 1.00 \\
Summer night minimum & 25 & 2.45 & 3.75 & 12.81 & 1.09 (max 1.35) & 1.00 \\
```
