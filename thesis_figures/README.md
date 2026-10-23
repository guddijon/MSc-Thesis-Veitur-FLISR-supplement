# Thesis figures by chapter

Every figure of the thesis is listed here with its file and the script or source that makes it. The files are those
used in the thesis: PDF where the figure is drawn by a script, with a PNG preview where the script writes one. Chapters 7 and 8
have no figures.

All figures drawn by a script share one style: Liberation Sans for text and mathematics, text printed at 6.5 to 9.5 pt at the
width used in the thesis, and one palette (blue #2a78d6 and orange #eb6834 for the two main series or the two directions,
a blue ramp for ordered series, muted grey #52514e for axes and secondary text, and the status red #b3261e for faults).
The Chapter 2 illustrations of `scripts/ch2_figures.py` are drawn and then set in this style by the same script. The redrawings after Glover, Overbye and Sarma (Figures 2.7, 2.9, 2.10) keep the book's layout in the same fonts and
sizes, in black, except the fault impedance of Figure 2.10, which is drawn in the status red.

Scripts stay with their data: the results figures are drawn by the scripts of the chapter folders, the illustrations
of Chapters 2 and 3 by `scripts/` here. `python3 ../reproduce.py figs ch4 ch5 ch6` redraws them into the `output/`
folder of each part, so the files below stay as published.

## Chapter 1

| Figure | File | Source |
|---|---|---|
| 1.1 | not included | screenshot from Veitur's website (service-area map) |
| 1.2 to 1.4 | not included | screenshots from Veitur's ADMS (single-line diagrams of A20, the Akranes network and the 11 kV network); see `ch1/README.md` |

## Chapter 2

| Figure | File | Made by |
|---|---|---|
| 2.1 | `ch2/start_veitur_indices_1996-2024.pdf` | `../ch6_earth_fault_and_reliability/reliability/scripts/start/start_series_fig.py` |
| 2.2 | `ch2/power_triangle.pdf` | `scripts/ch2_figures.py` |
| 2.3 | `ch2/phasor_diagram_colored.pdf` | `scripts/ch2_figures.py` |
| 2.4 | `ch2/impedance_admittance.pdf` | `scripts/ch2_impedance_protocol_figs.py` |
| 2.5 | `ch2/radial-vs-meshed.pdf` | `scripts/ch2_figures.py` |
| 2.6 | not included | screenshot of Veitur's ADMS network schematic |
| 2.7 | `ch2/transformer_connections.pdf` | `scripts/glover_tx.py` |
| 2.8 | `ch2/fault_types.pdf` | `scripts/ch2_figures.py` |
| 2.9 | `ch2/sequence_transformers.pdf` | `scripts/glover_tx.py` |
| 2.10 | `ch2/slg_fault_sequence.pdf` | `scripts/glover_slg.py` |
| 2.11 | `ch2/fault_current_stages.pdf` | `scripts/ch2_figures.py` |
| 2.12 | `ch2/tcc_ansi_50_51.pdf` | `scripts/ch2_figures.py` |
| 2.13 | not included | screenshot from the ComPass B 2.0 manual (Horstmann, cited in the thesis) |
| 2.14 | `ch2/feeder_fault_paths.pdf` | `scripts/ch2_figures.py` |
| 2.15 | `ch2/compass_directions_4bay.pdf` | `scripts/ch2_figures.py` |
| 2.16 | `ch2/linear_fpi_layout.pdf` | `scripts/ch2_linear_fpi.py` |
| 2.17 | not included | screenshot from the ComPass B 2.0 manual (Horstmann, cited in the thesis) |
| 2.18 | `ch2/sequence_angles_comparison.pdf` | `scripts/ch2_figures.py` |
| 2.19 | `ch2/sin_projection_directional.pdf` | `scripts/ch2_figures.py` |
| 2.20 | `ch2/protocol_architecture.pdf` | `scripts/ch2_impedance_protocol_figs.py` |
| 2.21 | `ch2/adms_network_hierarchy.pdf` | `scripts/ch2_figures.py` |
| 2.22 | `ch2/adms_flowchart.pdf` | `scripts/ch2_adms_pipeline.py` (pipeline of Section 2.6.3) |
| 2.23 | `ch2/raforkuspa_grunnspa_vs_haspa.pdf` | `scripts/ch2_figures.py`; reads the national energy forecast results workbook of 18 Feb 2026 (sheet Almenn raforka; cited in the thesis, not included) |

## Chapter 3

| Figure | File | Made by |
|---|---|---|
| 3.1 | `ch3/model_sources.pdf` | `scripts/ch3_method_diagrams.py` |
| 3.2 | `ch3/boiler_d1005.pdf` | `scripts/ch3_method_diagrams.py` |
| 3.3 | `ch3/tuning_validation.pdf` | `scripts/ch3_method_diagrams.py` |
| 3.4 | `ch3/ef_study_pipeline.pdf` | `scripts/ef_pipeline_fig.py` |
| 3.5 | `ch3/restoration_processes.pdf` | `scripts/ch3_method_diagrams.py` |

## Chapter 4

| Figure | File | Made by |
|---|---|---|
| 4.1 | `ch4/dpa_coverage.pdf` | `../ch4_data_audit/scripts/dpa_coverage_fig.py` |
| 4.2 | `ch4/busbar_allocation.pdf` | `../ch4_data_audit/scripts/a20_station_figs.py`; data in `../ch5_powerfactory_benchmark/data/snapshots/a20_breaker_states_by_snapshot.csv` |
| 4.3 | `ch4/cable_lengths.pdf` | `../ch4_data_audit/scripts/a20_station_figs.py`; data in `../ch5_powerfactory_benchmark/data/validation/gis_vs_model_lengths.csv` |
| 4.4 | `ch4/dpa_timeline.pdf` | `../ch4_data_audit/scripts/dpa_timeline_fig.py` |

The SQL listings of Appendix B, numbered as Figures B.1 and B.2, are in `../ch4_data_audit/sql/`.

## Chapter 5

| Figure | File | Made by |
|---|---|---|
| 5.1 | `ch5/pf_model_schematic_adms.pdf` | `../ch5_powerfactory_benchmark/scripts/pf_adms_layout.py` |
| 5.2 | `ch5/pf_geographic_view.pdf` | geographic view exported from PowerFactory |
| 5.3 | `ch5/pf_validation_scatter.pdf` | `../ch5_powerfactory_benchmark/scripts/pf_validation_scatter.py` (needs the per-bay ComPass measurements, which are not included) |
| 5.4 | `ch5/pf_voltage_profile.pdf` | `../ch5_powerfactory_benchmark/scripts/pf_voltage_profile_fig.py` |
| 5.5 | `ch5/pf_scenario_map_adms.pdf` | `../ch5_powerfactory_benchmark/scripts/pf_adms_layout.py` |
| 5.6 | `ch5/pf_constraints.pdf` | `../ch5_powerfactory_benchmark/scripts/pf_constraints_fig.py` |

## Chapter 6

| Figure | File | Made by |
|---|---|---|
| 6.1 | `ch6/v0_coverage.pdf` | `../ch6_earth_fault_and_reliability/earth_fault/ch6_figures.py` |
| 6.2 | `ch6/fpi_signatures.pdf` | `../ch6_earth_fault_and_reliability/earth_fault/ch6_figures.py` |
| 6.3 | `ch6/direction_probability.pdf` | `../ch6_earth_fault_and_reliability/earth_fault/ch6_figures.py` |
| 6.4 | `ch6/direction_probability_3ct.pdf` | `../ch6_earth_fault_and_reliability/earth_fault/ch6_figures_3ct.py` |
| 6.5 | `ch6/reliability_saidi_intervals.pdf` | `../ch6_earth_fault_and_reliability/reliability/scripts/mc_reliability_bars.py` |

## Scripts in this folder

| Script | Figures | Contents |
|---|---|---|
| `scripts/glover_tx.py` | 2.7, 2.9 | Transformer connections and their per-unit sequence networks, after Glover, Overbye and Sarma |
| `scripts/glover_slg.py` | 2.10 | Single line-to-ground fault and the interconnected sequence networks, after Glover, Overbye and Sarma |
| `scripts/ch2_impedance_protocol_figs.py` | 2.4, 2.20 | Impedance and admittance triangles; communication architecture from the ComPass to the control centre |
| `scripts/ch3_method_diagrams.py` | 3.1, 3.2, 3.3, 3.5 | Sources of the benchmark model; supply of the boiler network and D1005; tuning and validation split; actors and measured durations of the three restoration phases |
| `scripts/ch2_linear_fpi.py` | 2.16 | ComPass direction flags along a radial feeder |
| `scripts/ch2_adms_pipeline.py` | 2.22 | ADMS data pipeline: inputs, load allocation and DPF, the three APRS stages, Switching Advisor |
| `scripts/ch2_figures.py` | 2.2, 2.3, 2.5, 2.8, 2.11, 2.12, 2.14, 2.15, 2.18, 2.19, 2.21, 2.23 | Chapter 2 illustrations in the house style (fonts, sizes, palette); Figure 2.5 needs networkx; Figure 2.23 needs the national energy forecast results workbook of 18 Feb 2026 (path in ORKUSPA_XLSX) |
| `scripts/ef_pipeline_fig.py` | 3.4 | Earth-fault study pipeline |
