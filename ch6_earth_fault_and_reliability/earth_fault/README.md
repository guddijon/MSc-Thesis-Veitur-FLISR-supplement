# Earth-fault study package (thesis Sections 3.6 and 6.1 to 6.3)

One set of study definitions serves three routes to the same results: the GUI anchor runs, the PowerFactory script
(not used for the results), and the offline sequence-network sweep. All three write residual currents and
zero-sequence voltages in one common format. The ComPass emulation and the comparisons therefore treat them alike.

| File | Role |
|---|---|
| `ef_network.py` | Offline sequence-network model built from the model DGS, plus the study definitions: configurations, earthing variants, cable sets, fault locations, ComPass bays |
| `build_cases.py` | Writes `tables/`: locations, configurations, bays (the cable segment and end each bay measures into, and its V0 reference terminal), the 1904 cases, the 8 anchor runs, and copies of the cable and shunt tables |
| `shunt_sizing.csv` | Added shunt capacitance per target I_C and busbar section (iterated on the offline model) |
| `run_offline.py` | Offline sweep of all cases (about 10 s): `results/offline_phasors.csv` (stored as `.csv.gz`), `results/offline_cases.csv` |
| `compass_emulation.py` | sin φ rule with the measurement errors of thesis Table tab:ef_errors, 1000 samples per case and bay, settings V_NEQ 10/20/30 % × I_EQ 1 to 20 A, standard and reference calibration |
| `gui_anchor_run_sheet.md` | GUI procedure of the 8 anchor runs, settings as used, and their results |
| `parse_pf_exports.py` | GUI Flexible Data exports to the common format (3I0 and V0 rebuilt from phase values) |
| `compare_sources.py` | Bay-by-bay agreement between two sources, with the acceptance targets |
| `analysis_selectivity.py` | Pickup window of the sin φ indication per system size and fault location: `results/selectivity.csv` |
| `ch6_results.py` | Thesis Chapter 6 tables from the offline sweep and the emulation: `results/ch6/` (I_C per system and feeder, V0 against R_F, SCN-04 signatures, direction probability and coverage, pickup windows, localization zones) |
| `ch6_figures.py` | Thesis figures v0_coverage, fpi_signatures and direction_probability (PDF and PNG) in `../../thesis_figures/ch6/`; run with `MATPLOTLIBRC=../../matplotlibrc` |
| `ef_3ct.py` | Emulation with the residual current from three phase sensors (3CT) beside the summation-sensor reference, per load level and phase-angle error: `results/ch6/*_3ct.csv`; report `ef_3ct_report.md` |
| `ch6_figures_3ct.py` | Figure direction_probability_3ct (PDF and PNG) in `../../thesis_figures/ch6/` |
| `pf_ef_script.py` | PowerFactory script for the full matrix (not used for the results): preflight, anchors and full modes; resumable; restores all parameters |
| `tests/make_synthetic_exports.py` | Round-trip test of the parser with exports in the PowerFactory file format |

## Validation
Eight PowerFactory GUI anchor runs (`gui_anchor_run_sheet.md`) validate the offline model: every ComPass bay of every
anchor agrees within the targets (isolated cases within 0.71 % on 3I0 and 0.01 deg on the angle to -V0, earthed cases
within 1.4 % and 0.32 deg). The full matrix is therefore reported from the offline sweep, with the anchors as its
validation. Anchor exports: `anchors/`; parsed: `results/pf_gui_phasors.csv`; comparison:
`results/compare_gui_offline.csv`.

## Study set-up
- **I_C sweep (variant 3 of Table 3.5):** reported for busbar 2 (circuits 08 and 13, 21 A on its own; 40 to 200 A
  reached with an added shunt). Busbar 1 carries 61 A on its own, so the 20 A and 40 A targets cannot be reached there.
  Both variants are in `tables/cases.csv` (groups `ic_sweep` with `c_add_bus` A20_BB2 or A20_BB1).
- **Fault locations:** the Table 3.5 locations (four scenario locations, head and end of each faulted feeder) are on
  busbar 1. The busbar 2 sweep uses SCN-04 midline on circuit 13, the circuit 13 head and end, and the circuit 08 end
  (`tables/locations.csv`).
- **Signature figure:** fault SCN-04 on circuit 13, with two remotely controlled stations upstream and two downstream.

## Modelling notes
- **Omitted elements:** loads and the Dyn distribution transformers carry no zero-sequence current and are left out
  of the zero-sequence network. Loads are also left out of the positive sequence, where their effect on the
  fault-point impedance is negligible next to Z0 in the isolated cases.
- **Sources (earthed variant):** S1, S2 and the solidly earthed 66 kV grid form one zero-sequence network, built from
  the PowerFactory type data and reduced onto the two A20 busbars (`source_y0`). The S2 delta tertiary loads the
  66 kV zero sequence, so in the earthed variant a fault on one busbar induces a small V0 on the other. Both
  sequences use the transformer tap positions of the 10 Dec 2025 snapshot (S1 63.62 kV, S2 64.05 kV).
- **One-end energised cables:** a cable behind a normally open switch at one end stays energised from the other end
  and is kept with its full capacitance.
- **Pre-fault voltage:** taken as 11.15 kV line-to-line at the fault. PowerFactory takes it from the load flow, so
  the anchor runs show the difference.
- **Cable data:** the zero-sequence values are the "main" set of the parameter sheet. The sensitivity sets are
  `xlpe_sens` (Prysmian) and `pilc_low` (PILC C0/C1 0.60).
- **D1067:** its bays are included although its ComPass reads zero in SCADA. D1069 is de-energised in every
  configuration.
- **Bays in the other busbar section:** in the split configuration the two sections are separate systems, so these
  bays see no V0 and their expected indication is "none".
