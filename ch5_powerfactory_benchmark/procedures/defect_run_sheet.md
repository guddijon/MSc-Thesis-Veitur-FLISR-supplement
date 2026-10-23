# Run sheet: defect injections for tab:pf_defects

Purpose (thesis Section 5.4 "Outcome of the Audited Data Defects"): reproduce the three ADMS silent corruptors in
the benchmark with the substitute values the DPF applies, on the restored state of SCN-07, SCN-08 and SCN-13, and
report convergence, branch loading, minimum voltage and the restoration verdict against the defect-free model (the
restoration scenarios, `procedures/restoration_run_sheet.md`).

Mechanism: PowerFactory Variations. Each defect is one Variation with one expansion stage; the base network is not
touched. The variations are in the project file, deactivated, so that each row of the table can be reproduced by
activating one variation and one operation scenario.

Assignment of the three defect classes (from the ADMS extracts of 18 Oct 2026):

| Row | Defect class | Where the ADMS actually has it | Injection in the benchmark |
|---|---|---|---|
| SCN-13 | null DPA Length, 200 m substituted | A020-1019A03 and A04 (circuit 13 head, the donor of SCN-13); also the two D1049 bay stubs CABLE_7236/7237 (no code, no length; not separate elements in the model, and D1049 is the faulted station) | A020-1019A03 and A04 length 349.6 m -> 200 m each (head 1142 m -> 843 m) |
| SCN-07 | unresolved cable code, Default_Cable substituted (240 Al XLPE, 0.162 ohm/km, 390 A) | 36 Akranes aliases without a code are bay stubs at D1011-D1016, D1027, D1032, D1041, D1043, D1049, D1051 plus A020-SFAA04; none on the SCN-07 path. The 0R misspellings are on circuit 11 and resolve in Veitur's catalog. The injection is therefore representative: the 70 mm2 PILC back-feed sections of SCN-07, the cable class the thesis example names | 1002-1003A01, 1001-1002A02, A04, A05 (983 m of 3 x 70 Cu PILC, 0.316 ohm/km, 195 A) typed as OR_3A_XLPE_240_12 (identical to Default_Cable) |
| SCN-08 | unrated switch, Default_Switch 630 A substituted | 94 % of Veitur switching devices, all 266 Akranes devices | A20_R11-122 (1250 A) and the D1004 transformer-bay switch (200 A) typed 630 A; 1004-1-2 is already 630 A |

## Expected results (offline sweep, 50/50 ZIP, winter peak boiler off)

| Run | Scenario | Quantity | Corrected | With defect |
|---|---|---|---|---|
| D-07 | SCN-07_restored | circuit 22 head | 144.8 A | 144.7 A |
| D-07 | | 1002-1003A01 loading | 27.5 A, 14.1 % of 195 A | 27.4 A, 7.0 % of 390 A |
| D-07 | | 1001-1002A05 loading | 20.1 A, 10.3 % | 20.1 A, 5.2 % |
| D-07 | | D1026_BB | 1.0089 pu | 1.0095 pu |
| D-07b | SCN-14_restored (same variation) | circuit 21 head | 154.6 A | 154.5 A |
| D-07b | | 1001-1002A05 loading | 125.4 A, 64.3 % | 125.3 A, 32.1 % |
| D-07b | | 1002-1003A01 loading | 118.0 A, 60.5 % | 118.0 A, 30.3 % |
| D-07b | | D1003_BB / D1004_BB | 1.0053 / 1.0047 pu | 1.0082 / 1.0076 pu |
| D-13 | SCN-13_restored | circuit 13 head | 103.3 A | 103.5 A |
| D-13 | | A020-1019A05 loading | 53.2 % | 53.2 % |
| D-13 | | D1061_BB (lowest) | 1.0025 pu | 1.0034 pu |
| D-13 | | D1019_BB | 1.0127 pu | 1.0135 pu |
| D-13b | winter_peak_boiler_off (same variation) | D1058_BB | 1.0041 pu | 1.0048 pu |
| D-08 | SCN-08_restored | all currents | unchanged | unchanged |
| D-08 | | A20_R11-122 loading | 117.4 A, 9.4 % of 1250 A | 18.6 % of 630 A |
| D-08 | | D1004 transformer bay | 16 A, 8 % of 200 A | 2.5 % of 630 A |

Convergence: every run is expected to converge in 2 Newton-Raphson iterations, like the restoration scenarios. No restoration
verdict changes in any of the three scenarios; the errors are in the reported loading (factor 2 on the 70 Cu
sections) and in the voltage profile (up to 0.003 pu in D-07b), i.e. the defects converge to wrong answers.
Head currents checked against the restoration-sweep expectations (SCN-07, SCN-13, SCN-14 and SCN-08 restored).

## Variation mechanics (PowerFactory 2025, GUI)

Create: Data Manager, expand the project, Network Model, right-click the folder Variations, New, Variation.
Name it as below, OK. PowerFactory then asks for the Expansion Stage: keep the proposed name, set Activation Time
to a date before the study case time (01.01.2025 00:00 is safe), OK. The variation is now active and the stage is
the recording stage (red dot on the stage icon; the status bar names the variation). Every change to network data
made from now on, including edits in the Network Model Manager, is recorded in the stage, not in the base network.
If the Variations folder does not exist, right-click the project folder itself, New, Variation; PowerFactory
creates the folder.

Deactivate: Data Manager, right-click the variation, Deactivate. Check that the edited values have returned to
the base values in the Network Model Manager. Do not delete the variation.

Operation scenarios and variations are independent: activate the operation scenario named for the run as for
the restoration scenarios; the switch states and Out of Service flags come from the scenario, the defect from the variation.

## D-07  Variation `DEF-07_default_cable`

1. Operation scenario SCN-07_restored active.
2. Create the variation DEF-07_default_cable (above).
3. Data, Network Model Manager, Line table. For each of `1002-1003A01 - 2`, `1001-1002A02 - 2`,
   `1001-1002A04 - 2`, `1001-1002A05 - 2`: in the Type column select the project type
   Equipment Type Library, Line Types, `OR_3A_XLPE_240_12`. The four show OR_3C_PILC_70_11 before the change.
4. Load flow (settings of the restoration scenarios). Expect 2 iterations, circuit 22 head 144.7 A.
5. Export Breaker/Switch, Terminal, Line tables and the output window: `DEF-07_coup.txt`, `DEF-07_term.txt`,
   `DEF-07_lne.txt`, `DEF-07_log.txt`.
6. D-07b: activate operation scenario SCN-14_restored (variation stays active). Load flow. Expect circuit 21
   head 154.5 A. Export `DEF-07b_coup.txt`, `DEF-07b_term.txt`, `DEF-07b_lne.txt`, `DEF-07b_log.txt`.
7. Deactivate DEF-07_default_cable. Check the four lines show OR_3C_PILC_70_11 again.

## D-13  Variation `DEF-13_null_length`

1. Operation scenario SCN-13_restored active.
2. Create the variation DEF-13_null_length.
3. Line table, filter `A020-1019A0`: set Length of `A020-1019A03 (3 X 240 Al PEX 11kV)` and
   `A020-1019A04 (3 x 240 Al PEX 11kV)` from 0.349584 km to 0.2 km. Leave A05 (0.268761 km).
4. Load flow. Expect 2 iterations, circuit 13 head 103.5 A.
5. Export `DEF-13_coup.txt`, `DEF-13_term.txt`, `DEF-13_lne.txt`, `DEF-13_log.txt`.
6. D-13b: activate winter_peak_boiler_off (variation stays active). Load flow. Export `DEF-13b_term.txt`,
   `DEF-13b_coup.txt`, `DEF-13b_lne.txt`, `DEF-13b_log.txt`.
7. Deactivate DEF-13_null_length. Check both lengths read 0.349584 km again.

## D-08  Variation `DEF-08_default_switch`

1. Operation scenario SCN-08_restored active.
2. Create the variation DEF-08_default_switch.
3. Network Model Manager, Breaker/Switch table: `A20_R11-122`, Type from CB_1250A_A20 to the project type
   Equipment Type Library, Switch Types, `SW_630A_ring`. `1004-1-2` already carries SW_630A_ring (no change). Switch table (StaSwitch): `Cub_D1004_S-11-01_HV` (and `Cub_D1036_S-11-01_HV` if it has a type),
   Type to SW_630A_ring.
4. Load flow. Expect 2 iterations, every current identical to SCN-08_restored (circuit 22 head 117.4 A).
5. Export the Breaker/Switch table with the flexible-data columns Name, Type, Rated Current, Current and
   Loading (c:loading) as `DEF-08_coup.txt`; the Switch table the same way as `DEF-08_stasw.txt`; the output
   window as `DEF-08_log.txt`.
6. Deactivate DEF-08_default_switch. Check A20_R11-122 shows CB_1250A_A20 again.

## Close

All three variations deactivated; operation scenario winter_peak_boiler_off active; load flow; expect R11-116
312.80 A, R11-122 117.38 A, 4 isolated areas, 2 unsupplied.
