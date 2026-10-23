# Chapter 5: PowerFactory benchmark of the Akranes 11 kV network

The benchmark is a PowerFactory 2025 model of the 54 stations and 192 cable sections (36.0 km) fed from A20, built
from the ADMS and the GIS (thesis Section "PowerFactory Benchmark Construction"), tuned to four SCADA snapshots,
validated on a hold-out set of ComPass measurements, and used for the restoration scenarios SCN-01 to SCN-15 and the
defect injections of Chapter 5.

## Model

| Path | Contents |
|---|---|
| `model/Akranes_11kV_benchmark.pfd` | PowerFactory 2025 project, release v1.0.4 (import with File, Import, Data). Holds the base data, the type library, the operation scenarios (the four snapshots, the boiler-on cases, SCN-01 to SCN-15), the earthing variations, the earth-fault study objects (scenario `EF_coupled_N-1`, variation `EF_variant3_Cadd` with the busbar 2 shunt) and the defect variations DEF-07, DEF-08 and DEF-13. |
| `model/dgs/akranes_11kv_benchmark.dgs` | DGS v7 file (UTF-8), importable on its own: the network as built from the ADMS and the GIS. Every object carries its source in the description field (`src=ADMS`, `src=GIS`, `src=model`, `src=author`). The switch ratings, zero-sequence data, scenarios and variations were entered in PowerFactory and are in the project file and in `model/parameters/`. |
| `model/parameters/` | `parameter_decisions.md` (parameter values and their sources for the earth-fault study and the remaining base-model assumptions), `ef_parameter_sheet.md` and `ef_cable_type_values.csv` (zero-sequence data of the line and transformer types), `switchgear_ratings_sheet.md` and `switch_ratings_model_map.csv` (ADMS switch ratings mapped to the model) |
| `model/build/tools/` | `lint_dgs.py` checks a DGS file for consistency; `a20_board.py` and `a20_station_diagram.py` draw the A20 station diagram into the DGS file |

## Data

| Path | Thesis | Contents |
|---|---|---|
| `data/snapshots/` | Tables 3.3, 4.12, 5.4 | The four snapshots (winter peak 10 Dec 2025 17:55, winter night minimum, summer peak, summer night minimum): A20 feeder currents and busbar voltages (15-min means), 66 kV voltage and tap positions, A20 breaker and station switch states, open points; station order and open points of the base state traced through the model (`open_rings_*.csv`) |
| `data/allocation/` | Table 5.4 | Load per station transformer and scenario (P0, Q0, factor), PowerFactory paste files, tuning tables (measured and simulated feeder-head currents) |
| `data/validation/` | Tables 5.5, 5.6, 5.8; Figure 5.4 | Hold-out metrics per snapshot, station-level hold-out summary, sensitivity metrics, voltage profile of circuit 13, GIS and model lengths of the 62 station links |
| `data/scenarios/` | Tables 5.9, 5.10; Figure 5.6 | Restoration scenarios from PowerFactory and from the offline sweep, defect injections |
| `data/pf_exports/` | Tables 5.3 to 5.10 | PowerFactory Flexible Data exports (model results): `snapshots/`, `model_parameters/` (switch, line, transformer and external-grid type data as entered), `boiler_scenarios/`, `restoration_scenarios/` (103 files), `defect_injections/` |
| `docs/` | Tables 5.5, 5.6, 5.8 | Hold-out validation and sensitivity reports, hold-out selection list, ComPass voltage calibration note |
| `procedures/` | | PowerFactory run sheets: restoration scenarios (`restoration_scenario_sheets.md`, `restoration_run_sheet.md`), defect injections, summer switching |

The allocation tables are the loads of the model and are reproduced by `snapshot_alloc.py`.

## Scripts

| Script | Purpose |
|---|---|
| `paths.py` | Locations of inputs and outputs; every script writes into `output/` |
| `radial_pf.py` | Balanced backward/forward sweep on the DGS file (ZIP loads, taps, source voltage); agrees with PowerFactory within 0.13 A on every compared branch |
| `snapshot_alloc.py <snapshot>` | Load allocation to the measured A20 feeder-head currents with the snapshot's switching state |
| `open_rings.py` | Station order of each A20 circuit and the open points between circuits in the December 2025 base state, traced through the DGS file (Table 4.12) |
| `restoration_sweep.py` | Restoration scenarios: isolation switches, de-energised islands, single-tie restoration options and their loading |
| `restoration_results_table.py` | Scenario results table from the PowerFactory exports |
| `defect_expect.py` | Offline expectation of the defect injections |
| `holdout_build.py`, `holdout_pf.py`, `holdout_validation.py`, `sensitivity.py` | Hold-out validation and sensitivity; need the per-bay ComPass measurements, which are not part of the supplement |
| `pf_adms_layout.py`, `pf_validation_scatter.py`, `pf_voltage_profile_fig.py`, `pf_constraints_fig.py` | Figures 5.1 and 5.5, 5.3, 5.4, 5.6 |

Rerun: `python3 ../reproduce.py ch5`. The figure files are in `../thesis_figures/ch5/`; Figure 5.2 (`pf_geographic_view.pdf`) is the geographic view exported
from PowerFactory.
