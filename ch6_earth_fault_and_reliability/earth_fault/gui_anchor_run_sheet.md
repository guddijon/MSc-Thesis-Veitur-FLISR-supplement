# Earth-fault study: PowerFactory GUI anchor runs, procedure and results

Eight short-circuit runs in the PowerFactory 2025 GUI that validate the offline sequence-network model
(`ef_network.py`). The case definitions are in `tables/anchor_runs.csv` and `tables/cases.csv`. The released benchmark
project (`../../ch5_powerfactory_benchmark/model/Akranes_11kV_benchmark.pfd`) already holds the study objects of steps
1.2 and 1.3.

Steps 1.2 and 1.3 add study objects only, one operation scenario and one variation
holding one shunt. No base data, type or element parameter is changed by the procedure.

## 1. Preparation (once)

1.1 Save a project version before adding the study objects.

1.2 **Operation scenario `EF_coupled_N-1`** (coupled busbars, S2 out), used by A4:
- Activate `winter_peak_boiler_off`, then use Save Operation Scenario As, `EF_coupled_N-1`.
- Breaker/Switch `A20_R11-112_coupler`: tick Closed. Breaker/Switch `A20_R11-207` (S2 bay): untick Closed.
- Load flow: converges in 2 iterations, 4 isolated areas; coupler 109.33 A (the S2 bay current R11-207 in `winter_peak_boiler_off`), R11-116
  422.13 A. Save the scenario and re-activate `winter_peak_boiler_off`.

1.3 **Variation `EF_variant3_Cadd`** with one shunt, used by A6:
- Variations folder: New, Variation `EF_variant3_Cadd`, expansion stage with activation 01.01.2025; activate it.
- In the grid folder `VeiturRegion`: New Object, Shunt/Filter (ElmShnt) `EF_Cadd_BB2`. Terminal: in the selection
  browser open `A20_BB2` and create a new cubicle `Cub_EF_Cadd_BB2` there (a terminal itself is not accepted).
- Basic Data: Technology 3PH-'YN', Rated Voltage 11 kV, Shunt Type C, Input Mode Design Parameter, Max. No. of Steps 1,
  Act. No. of Step 1, Rated Reactive Power C 0.6103 Mvar, tan delta 0 (susceptance 5043.8 uS = 16.05 uF per phase;
  120 A target on busbar 2, `tables/shunt_sizing.csv`). Zero Sequence: star point Connected, Re = Xe = 0, B0/B1 = 1.
  Load Flow: no controller, not switchable.
- Check that the shunt and its cubicle are listed in the expansion stage. Load flow with the variation active: R11-207
  105.86 A (109.33 A without). Deactivate the variation.

1.4 **Flexible Data** (Network Model Manager, class, Define Flexible Data, Calculation "Short-Circuit Complete",
Balanced unticked):
- Lines (ElmLne): `I` (exported as Ik", kA) and `phii` (Ik", Angle), phases A, B, C, at bus1 (Terminal i) and bus2
  (Terminal j): 12 columns.
- Terminals (ElmTerm): `U` (line-ground voltage, kV) and `phiu` (angle), phases A, B, C, plus `U0` and `phiu0`. Check
  that the three angle rows carry phases A, B and C.
- Decimals (Project Settings, Formats and Units, Output Variables, Short-Circuit, and the Format/Header page where
  needed): kA 7, kV 6, angles 4 or more. A round trip through the export format shows why: with 5 / 1 / 1 decimals
  the rebuilt residual current is off by up to 19 deg; with 7 / 4 / 6 by 0.03 deg.

1.5 **Short-circuit command** (Calculation, Short-Circuit): Method complete; Fault Type Single Phase to Ground; Phase a;
Calculate Max. Short-Circuit Currents; Load Flow Initialisation ticked (Complete page); Fault Impedance Rf per run,
Xf 0; Fault Location User Selection; Advanced Options: **untick** "Calculate max. Branch Currents = Busbar Currents"
(the branch currents must be the calculated ones, they are the ComPass bay currents); output Short.

## 2. The runs

Per run: set the variation and operation scenario, place the fault, set Rf, execute, check, export.
- Isolated means `EF_variant2_isolated` active; earthed means no variation active (the base data are earthed).
- Fault at a terminal: Network Model Manager, Terminals, right-click, Calculate, Short-Circuit.
- Fault on a line: right-click the line, Calculate, Short-Circuit, fault distance 50 % from Terminal i.
- Exports (Flexible Data, select all, Spread Sheet Format, no filter): `<run>_lne.txt`, `<run>_term.txt`, and the
  output window as `<run>_log.txt`.

| Run | Variation | Operation scenario | Fault location | Rf | Fault current PowerFactory | Offline model | ComPass bays within targets |
|---|---|---|---|---|---|---|---|
| A1 | isolated | winter_peak_boiler_off | terminal `D1026_BB` | 0 | 61.2 A | 61.0 A | 33/33 |
| A2 | isolated | winter_peak_boiler_off | terminal `D1026_BB` | 300 ohm | 20.3 A | 20.2 A | 33/33 |
| A3 | isolated | winter_peak_boiler_off | line `1023-1050A02`, 50 % | 0 | 21.3 A | 21.4 A | 33/33 |
| A4 | isolated | EF_coupled_N-1 | terminal `D1026_BB` | 0 | 82.8 A | 82.7 A | 33/33 |
| A5 | isolated | SCN-15_restored | terminal `A20_C21` | 0 | 61.3 A | 60.9 A | 31/31 |
| A6 | isolated + EF_variant3_Cadd | winter_peak_boiler_off | line `1023-1050A02`, 50 % | 0 | 120.0 A | 120.5 A | 33/33 |
| A7 | earthed | winter_peak_boiler_off | terminal `D1026_BB` | 0 | 5.22 kA | 5.29 kA | 33/33 |
| A8 | earthed | winter_peak_boiler_off | terminal `D1026_BB` | 30 ohm | 208.9 A | 208.2 A | 33/33 |

Fault currents of the line faults (A3, A6) are the phase-A currents into the faulted line from both ends. Agreement
targets (`compare_sources.py`): |3I0| within 5 % or 0.2 A, angle of 3I0 to -V0 within 2 deg, |V0| within 2 % or
0.02 kV. Worst cases: isolated anchors 0.71 % and 0.01 deg; earthed anchors 1.4 % and 0.32 deg. The remaining
isolated-case difference is the pre-fault voltage (PowerFactory: load flow; offline: 11.15 kV flat), -0.7 % on
busbar 2 and +0.4 to +0.6 % on busbar 1.

## 3. Afterwards

- Deactivate all variations, activate `winter_peak_boiler_off`; load flow R11-116 312.80 A.
- Save a project version; export the project.

## 4. Processing the exports

```
python3 parse_pf_exports.py <export_dir> results/pf_gui_phasors.csv pf_gui
python3 compare_sources.py results/offline_phasors.csv results/pf_gui_phasors.csv results/compare_gui_offline.csv
```
