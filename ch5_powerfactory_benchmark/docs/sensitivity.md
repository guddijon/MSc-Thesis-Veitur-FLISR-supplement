# Sensitivity of the hold-out metrics to the load-allocation assumptions

Method: every variant is re-allocated to the A20 feeder-head currents with the same per-feeder rule as the adopted case, then compared with the ComPass hold-out set on the same bays as the validation tables (22 bays in December, 25 in August; measured and simulated current above 0.5 A). Solver: offline sweep (`sensitivity.py`), which matched PowerFactory within 0.13 A for the adopted case; one PowerFactory confirmation of the load-type effect is listed at the end. Variants: ZIP 50/50 (adopted), constant impedance, constant current, constant power; and "pinned": the ten stations whose transformer-bay current the ComPass measures (D1001, D1004, D1026, D1029, D1030, D1061, D1062, D1066, D1069, D1070) are set to sqrt(3) x U_meas x I_meas at power factor 0.95 and not scaled, the remaining stations of each feeder are scaled to the head current.

| Snapshot | Variant | Bays | I MAE (A) | I RMSE (A) | I MAD (A) | median rel (%) | non-pinned bays MAE (A) | V MAE (%) | V MAD (%) | offset (%) | Load at Un (kW) | feeder factors |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Winter peak (boiler off) | Adopted (50 % Z, 50 % P) | 22 | 4.76 | 6.55 | 14.57 | 17 | 4.76 (22) | 1.76 | 2.33 | +1.76 | 7805 | 1.000-1.000 |
| Winter peak (boiler off) | Constant impedance (ADMS default) | 22 | 4.79 | 6.58 | 14.56 | 17 | 4.79 (22) | 1.76 | 2.33 | +1.76 | 7744 | 0.982-0.999 |
| Winter peak (boiler off) | Constant current | 22 | 4.76 | 6.55 | 14.57 | 17 | 4.76 (22) | 1.76 | 2.33 | +1.76 | 7806 | 1.000-1.000 |
| Winter peak (boiler off) | Constant power | 22 | 4.73 | 6.52 | 14.58 | 17 | 4.73 (22) | 1.76 | 2.33 | +1.76 | 7868 | 1.001-1.018 |
| Winter peak (boiler off) | Adopted mix, measured transformer currents pinned | 22 | 2.11 | 3.21 | 7.41 | 3 | 3.07 (15) | 1.75 | 2.33 | +1.75 | 7806 | 1.000-2.297 |
| Winter night minimum | Adopted (50 % Z, 50 % P) | 22 | 1.38 | 1.94 | 4.93 | 8 | 1.38 (22) | 2.08 | 2.65 | +2.08 | 2905 | 0.155-0.753 |
| Winter night minimum | Constant impedance (ADMS default) | 22 | 1.38 | 1.94 | 4.93 | 8 | 1.38 (22) | 2.08 | 2.65 | +2.08 | 2861 | 0.152-0.741 |
| Winter night minimum | Constant current | 22 | 1.38 | 1.94 | 4.93 | 8 | 1.38 (22) | 2.08 | 2.65 | +2.08 | 2905 | 0.155-0.753 |
| Winter night minimum | Constant power | 22 | 1.38 | 1.94 | 4.93 | 8 | 1.38 (22) | 2.08 | 2.65 | +2.08 | 2950 | 0.158-0.766 |
| Winter night minimum | Adopted mix, measured transformer currents pinned | 22 | 0.76 | 1.18 | 2.56 | 6 | 1.11 (15) | 2.08 | 2.65 | +2.08 | 2914 | 0.158-1.411 |
| Summer peak | Adopted (50 % Z, 50 % P) | 25 | 2.92 | 4.39 | 10.59 | 16 | 2.92 (25) | 1.54 | 2.16 | +1.54 | 5314 | 0.162-1.219 |
| Summer peak | Constant impedance (ADMS default) | 25 | 2.91 | 4.38 | 10.59 | 16 | 2.91 (25) | 1.54 | 2.16 | +1.54 | 5237 | 0.159-1.205 |
| Summer peak | Constant current | 25 | 2.92 | 4.39 | 10.59 | 16 | 2.92 (25) | 1.54 | 2.16 | +1.54 | 5315 | 0.162-1.219 |
| Summer peak | Constant power | 25 | 2.92 | 4.40 | 10.58 | 16 | 2.92 (25) | 1.54 | 2.16 | +1.54 | 5394 | 0.165-1.234 |
| Summer peak | Adopted mix, measured transformer currents pinned | 25 | 2.36 | 3.78 | 8.34 | 3 | 3.27 (18) | 1.54 | 2.16 | +1.54 | 5314 | 0.166-1.590 |
| Summer night minimum | Adopted (50 % Z, 50 % P) | 25 | 2.45 | 3.74 | 12.80 | 24 | 2.45 (25) | 1.77 | 2.28 | +1.77 | 2257 | 0.121-1.000 |
| Summer night minimum | Constant impedance (ADMS default) | 25 | 2.45 | 3.74 | 12.81 | 24 | 2.45 (25) | 1.77 | 2.28 | +1.77 | 2229 | 0.119-1.000 |
| Summer night minimum | Constant current | 25 | 2.45 | 3.74 | 12.80 | 24 | 2.45 (25) | 1.77 | 2.28 | +1.77 | 2257 | 0.121-1.000 |
| Summer night minimum | Constant power | 25 | 2.45 | 3.74 | 12.80 | 24 | 2.45 (25) | 1.77 | 2.28 | +1.77 | 2286 | 0.123-1.000 |
| Summer night minimum | Adopted mix, measured transformer currents pinned | 25 | 2.05 | 3.81 | 11.94 | 15 | 2.84 (18) | 1.77 | 2.28 | +1.77 | 2259 | 0.105-1.000 |

## Findings

1. The ZIP composition has no effect on the validation result once each variant is re-allocated: the current metrics move by at most 0.03 A and the voltage metrics not at all. The per-feeder allocation absorbs the load-model choice. What changes is the load at nominal voltage: 7745 kW (constant impedance) to 7867 kW (constant power) around 7805 kW adopted at the winter peak, +/-0.8 %, and the same spread at the other snapshots. The composition therefore matters when the model is used away from the tuning point (restoration cases with larger voltage drops, future-load cases), not for the validation itself.
2. Without re-allocation the type change is visible at the A20 heads: at the winter peak S1 moves from 312.9 A (adopted) to 316.0 A (constant impedance) and 309.8 A (constant power), feeder 22 from 117.4 to 118.1 / 116.7 A; constant current gives the adopted values within 0.02 A. These are the values compared in the PowerFactory confirmation below (type switched, loads unchanged).
3. Pinning the ten stations with a measured transformer current halves the winter errors (MAE 4.76 -> 2.11 A, MAD 14.6 -> 7.4 A at the peak; 1.38 -> 0.76 A at night) and improves the August totals (2.92 -> 2.36, 2.45 -> 2.05 A), but the bays that are not pinned get worse in August (3.27 against 2.92 A, 2.84 against 2.45 A): the residual of each feeder lands on fewer unmeasured stations, so the error concentrates there. The rating share of the unmeasured remainder stays the limiting assumption; the ComPass transformer-bay currents should enter the ADMS load allocation as measured loads, which the DPA load-allocation function can do with the Modbus points already mapped.
4. The voltage metrics do not move under any variant (offset +1.5 to +2.1 %, offset-free MAD 0.5-0.65 %), which confirms that the substation voltage error is the sensor offset and not a load-model effect.

Files: `data/validation/sensitivity_metrics.csv` (all variants and snapshots); `sensitivity.py` also writes sensitivity_bays.csv (per-bay model values per variant, not part of the supplement).

## PowerFactory confirmation

Scenario winter_peak_boiler_off, all 61 loads switched to P100_constant_power, loads unchanged (no re-allocation):

| Breaker | PowerFactory (A) | Sweep (A) |
|---|---|---|
| R11-116 (S1) | 309.76 | 309.78 |
| R11-122 | 116.71 | 116.69 |
| R11-105 | 68.44 | 68.53 |
| R11-106 | 38.51 | 38.50 |
| R11-213 | 95.74 | 95.75 |
| R11-207 (S2) | 109.03 | 109.05 |
| R11-110 | 35.07 | 35.06 |
| R11-121 | 36.18 | 36.18 |
| R11-109 | 12.91 | 12.91 |
| R11-208 | 13.43 | 13.43 |
| R11-111 | 4.16 | 4.16 |

Note for a DGS import: PowerFactory keeps its default exponents (0/1/2) for the four load types instead of the exponents in the file, so Z100 and P100 are swapped (with them, this run gives S1 315.7 A, the constant-impedance value); the adopted type is physically unchanged (0.5 at exponent 0 plus 0.5 at exponent 2). The exponents are set by hand to 2/1/0 in the four types, as in the project file.
