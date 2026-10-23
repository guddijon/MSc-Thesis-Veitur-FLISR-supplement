# Earth-fault parameter sheet for the PowerFactory model

Implements parameter_decisions.md. No topology, load or positive-sequence change: the validated load-flow baseline is
untouched. Everything below is zero-sequence type data, star-point earthing and short-circuit source data. Values per
type in ef_cable_type_values.csv. The columns "DGS file" give the values in `model/dgs/akranes_11kv_benchmark.dgs`
(ADMS catalog); the project file holds the values of the columns MAIN.

## A. What stays as it is (and why)
- Cable R1, X1, B1 (positive sequence) of all ten line types: these carry the validated load flow. The
  datasheet R1 values of parameter_decisions.md (0.125 / 0.206 / 0.641 ohm/km) are not used; the ADMS values stay. The thesis
  discusses the difference as "catalog vs datasheet" for the positive sequence.
- C1 stays at the ADMS value (XLPE 240: 0.65 uF/km) in B1. The datasheet capacitance (0.41 uF/km) goes into B0
  only, because the isolated-network earth-fault current depends on C0 alone and the balanced load flow on C1
  alone; the model then states "C0 per datasheet, C1 per ADMS catalog" and the baseline does not move. Setting
  C1 = C0 in the types for consistency would require re-tuning the four scenarios (charging currents change by
  0.5 to 1.5 A per feeder, feeder 19 from 1.9 to 1.2 A); not done.
- Distribution transformer types: Dyn5, uk 3.6 to 5.8 % and copper losses from the ADMS catalog per rating (not the
  generic 4 / 6 % of parameter_decisions.md); delta on 11 kV, so no zero-sequence path to the MV network. No change. P0 (pfe) is 0 in
  all eight types; immaterial.

## B. Cable types, zero-sequence columns (Equipment Type Library, Line Types, tab Load Flow or Basic Data depending on the type model; fields R0', X0', B0')
Main set = NKT AXAL-TT PRO for XLPE, generic PILC with C0/C1 = 0.83. Sensitivity set = Prysmian AXALJ-TT for XLPE,
C0/C1 = 0.60 for PILC.

| Type | km | DGS file R0' / X0' / B0' | MAIN R0' / X0' / B0' (uS/km) | SENS R0' / X0' / B0' |
|---|---|---|---|---|
| OR_3A_XLPE_240_12 | 24.16 | 0.972 / 0.102 / 204.2 | 1.93 / 0.08 / 128.8 | 0.65 / 0.56 / 144.5 |
| OR_3A_XLPE_150_12 | 2.69 | 1.59 / 0.108 / 172.8 | 2.61 / 0.08 / 103.7 | 0.76 / 0.68 / 119.4 |
| OR_3A_XLPE_50_12 | 0.88 | 4.932 / 0.126 / 113.1 | 4.24 / 0.09 / 69.1 | 1.31 / 0.87 / 78.5 |
| OR_1A_XLPE_240_12 | 0.01 | 0.08 / 0.04 / 161.2 | 1.93 / 0.08 / 128.8 | 0.65 / 0.56 / 144.5 |
| OR_3C_PILC_70_11 | 5.62 | 1.896 / 0.108 / 0 | 1.47 / 0.11 / 101.7 | 1.47 / 0.11 / 73.5 |
| OR_3C_PILC_120_11 | 0.42 | 1.086 / 0.0996 / 0 | 1.17 / 0.10 / 125.2 | 1.17 / 0.10 / 90.5 |
| OR_3C_PILC_150_11 | 0.10 | 0.882 / 0.0984 / 0 | 1.03 / 0.105 / 135.6 | 1.03 / 0.105 / 98.0 |
| OR_3A_PILC_150_11 | 0.66 | 1.464 / 0.0984 / 0 | 1.03 / 0.105 / 135.6 | 1.03 / 0.105 / 98.0 |
| OR_3A_PILC_240_11 | 1.44 | 0.894 / 0.0936 / 0 | 0.82 / 0.10 / 166.9 | 0.82 / 0.10 / 120.6 |
| Jumper_busbar_stub | 0.01 | 0.001 / 0.001 / 0 | unchanged | unchanged |

B0' = 2 pi 50 C0 in uS/km. PILC B0' = ratio x the model's own B1' (C1 0.39 / 0.48 / 0.52 / 0.52 / 0.64 uF/km).
Discrepancy: parameter_decisions.md quotes 0.48 uF/km as the ADMS C1 of the 3x70 PILC; the model type carries 0.39
(122.5 uS/km). If 0.48 is the ADMS value, B1' of OR_3C_PILC_70_11 is a build error (load-flow effect: 0.3 A of
charging current on 5.6 km, negligible) and B0' main becomes 125.2 / low 90.5 uS/km. The model value is used.

Resulting isolated-network capacitive earth-fault current of the whole 36 km at 11 kV (3 w C0 Uph summed):
DGS file values 105 A (PILC contributing nothing), MAIN 84 A (XLPE 66 + PILC 18), PILC low case 79 A, Prysmian XLPE 92 A.
The "about 85 A" of parameter_decisions.md is reproduced; its "140 A implied by the catalog" corresponds to C0 = C1 for all types.

## C. S1 (TypTr2 S1_ETRA_RT25000-66_25MVA_66-11_YNyn0, tab Load Flow, zero-sequence)
| Field | DGS file | MAIN | sensitivity range |
|---|---|---|---|
| uk0 (zero-seq. short-circuit voltage) | 10.01 % | 9.01 % (0.9 x uk, IEC 60076-8 three-limb YNyn) | 8.0 to 10.0 % |
| ur0 | 0.314 % | 0.314 % | |
| Zero-seq. magnetising impedance / uk0 (zx0hl_n) | 0 | 0 = no branch (the 0.9 factor already carries the three-limb effect) | n/a |
| Mag. R/X | default | default | |
Z0 seen from 11 kV with the 66 kV side earthed and the grid providing a zero-sequence path: 0.44 ohm (0.39 to 0.48).
The ORVV09 figures (R0 32.21, X0 85.37) are not entered.

## D. S2 (TypTr3 S2_DOR20000-60_16-16-5.33MVA_63-11-3.15; element S2 a three-winding YNyn0d1)
Pairwise short-circuit voltages from the IEC 60076-8 ratios scaled to uk(HV-MV) = 7.53 % (ZH 0.0188, ZX 0.0565,
ZY 0.0941 pu on 16 MVA). PowerFactory refers each pair to the smaller rated power of the two windings; the dialog
shows the reference.
| Pair | DGS file | MAIN |
|---|---|---|
| HV-MV (63-11) | 7.53 % on 16 MVA | 7.53 % (unchanged, the load flow does not move) |
| MV-LV (11-3.15) | 2.5 % | 15.06 % on 16 MVA = 5.02 % on 5.33 MVA |
| LV-HV (3.15-63) | 7.53 % | 11.29 % on 16 MVA = 3.76 % on 5.33 MVA |
| uk0 of each pair | = uk | 0.98 x uk of that pair |
| ur0 | 0.3 % | 0.3 % |
Check: Z0 seen from 11 kV = 0.98 x (ZX + ZH || ZY) = 0.0707 pu = 0.535 ohm (rule of thumb 0.8 to
1.0 x Zk = 0.46 to 0.57 ohm). The tertiary is unloaded. Type description: "IEC 60076-8 generic ratios".

## E. Star-point earthing (elements S1 and S2, tab Grounding / Neutral Conductor)
The base data is variant 1 (both star points connected, Re = Xe = 0). Two Network Variations, never active together:
- Variation `EF_variant1_earthed` (empty named variation, equal to the base data): S1 HV star point earthed
  (Re = Xe = 0), S1 LV star point earthed (Re = Xe = 0); S2 HV earthed, S2 MV (11 kV) earthed, both solid.
- Variation `EF_variant2_isolated`: S1 HV earthed solid; S1 LV star point "not connected"/isolated; S2 HV earthed
  solid; S2 MV star point isolated.
No resistor, reactor or coil anywhere. Variations are created in the Network Model Manager > Variations folder
(New > Variation, then an Expansion Stage inside it, activate the stage, make the edits, deactivate).

## F. External grid (ElmXnet Landsnet_66kV)
| Field | DGS file | MAIN |
|---|---|---|
| Sk'' max | 500 MVA | 500 MVA (run value) |
| R/X max | 0.1 | 0.1 |
| Sk'' min | 300 MVA | 197 MVA (Landsnet 2015 min) |
| R/X min | 0.1 | 0.1 |
| X0/X1, R0/X0 | 1, 0.1 | 1, 0.1 (Z0 = Z1, solidly earthed 66 kV) |
Description: "Sk'' 500 MVA run value; 373 MVA (Landsnet 2015 max) as sensitivity run, 197 MVA min; bracket
160-500 MVA". The 373 MVA sensitivity is one short-circuit run per earthing variant with Sk'' max set to 373 MVA
for that run (or a separate variation `EF_Sk373`).

## G. A20 switchboard (inventory data, no load-flow effect)
Busbars 12 kV / 31 kA; feeder and coupler breakers 1250 A (type `CB_1250A_A20`, 1.25 kA, 12 kV, on the 43 A20
breakers; see switchgear_ratings_sheet.md); incomers 2000 A (S1) / 1250 A (S2); phase CTs 400/1 A (800/1 A on
bays 04, 11, 17, 21), core-balance CTs 200/1 A, busbar VTs 11/sqrt3 : 110/sqrt3 : 110/3 V.

## H. Run matrix for the earth-fault study (short-circuit command, complete method, single-phase to ground, per
fault location of Table 3.5)
| Run | Variation | Cable set | Sk'' | Purpose |
|---|---|---|---|---|
| EF-1a | variant 1 earthed | MAIN (NKT + PILC 0.83) | 500 | reference, earthed |
| EF-1b | variant 1 earthed | SENS (Prysmian; PILC R0/X0 unchanged) | 500 | zero-seq impedance sensitivity |
| EF-1c | variant 1 earthed | MAIN | 373 | source sensitivity |
| EF-2a | variant 2 isolated | MAIN (C0/C1 0.83) | 500 | reference, isolated: Ic about 84 A |
| EF-2b | variant 2 isolated | PILC low (C0/C1 0.60) | 500 | PILC capacitance sensitivity: about 79 A |
| EF-2c | variant 2 isolated | MAIN | 373 | source sensitivity (small effect expected) |
Cable set changes are edits of the nine types (table B) between runs. The fault locations are those of Table 3.5.

## Values in the project file
Verified from the exports in `data/pf_exports/model_parameters/` (`line_types_*.txt`, `transformer*_types.txt`,
`transformer*_earthing.txt`, `external_grid_short_circuit.txt`, `loadflow_log_zero_sequence.txt`): line types
R0'/X0'/B0' as table B (MAIN), B' unchanged; S1 uk0 9.01 %, ur0 0.314, no zero-seq magnetising branch; S2 uk
7.53/5.02/3.76 (tertiary pairs on 5.33 MVA, as the dialog shows), uk0 7.38/4.92/3.68; grid Sk''min 197 MVA; base
data = variant 1 (both star points Connected, Re=Xe=0), EF_variant1_earthed is an empty named variation,
EF_variant2_isolated records S1 and S2 with the 11 kV star points Not connected. Base load flow unchanged.
