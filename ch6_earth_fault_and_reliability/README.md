# Chapter 6: earth-fault feasibility and reliability benefit

## Earth-fault study (Sections 6.1 to 6.3)

`earth_fault/` is a self-contained package; its README lists the files, the study set-up and the modelling notes. In short:
an offline sequence-network model of the benchmark (`ef_network.py`, built from the Chapter 5 DGS and cable data)
sweeps 1904 cases (earthing variant, configuration, fault location, fault resistance, cable set, source level and
added capacitance) and writes the residual current and zero-sequence voltage at every ComPass line bay. The ComPass
sin φ rule is then emulated with the sensor errors of Table 3.6, and the pickup window of the indication is computed
per system size (`results/selectivity.csv`). Eight PowerFactory anchor runs (`gui_anchor_run_sheet.md`, exports in
`anchors/`) validate the offline model: every ComPass bay of every anchor agrees within the targets (isolated cases
within 0.71 % and 0.01 deg, earthed cases within 1.4 % and 0.32 deg).
The thesis tables and figures of Sections 6.1 to 6.3 come from `ch6_results.py` (`results/ch6/`) and
`ch6_figures.py` (Figures 6.1 to 6.3 in `../thesis_figures/ch6/`).
The rerun with three phase sensors (3CT), as installed, is `ef_3ct.py` with its report `ef_3ct_report.md`, tables
`results/ch6/*_3ct.csv` and Figure 6.4 (`../thesis_figures/ch6/direction_probability_3ct`).

The package writes its `tables/` and `results/` in place. `results/offline_phasors.csv` is stored compressed
(`.csv.gz`); `run_offline.py` recreates it.

## Reliability benefit (Section 6.4)

| Path | Thesis | Contents |
|---|---|---|
| `reliability/data/akranes_11kv_events_2020-2026.csv` | Section 6.4 | Unplanned interruption events on the Akranes 11 kV network 2020 to 2026: date, circuit, class, stations out, minutes from the trip to the first and last customer restored, customers interrupted and customer-minutes (per station from the outage reports with the customer register) |
| `reliability/data/akranes_fault_stages_2020-2026.csv` | Table 6.6 | The seven events that needed sectionalizing: trip time, response and sectionalizing phases, minutes to the first and last customer restored, customers interrupted and customer-minutes (both trips of 13 Nov 2022) |
| `reliability/data/customers_per_station.csv` | Section 6.4 | Customer count per station (OMS register, 20 Oct 2026; 3 516 customers in 47 stations) |
| `reliability/mc_reliability_assumptions.md` | Section 6.4 | Inputs with their sources, the four modelling assumptions and the results |
| `reliability/scripts/mc_reliability.py` | Section 6.4 | Monte Carlo of ten-year SAIDI under (i) crew-based sectionalizing, (ii) remote sectionalizing, (iii) automated FLISR |
| `reliability/scripts/mc_reliability_bars.py` | Section 6.4 figure | Ten-year SAIDI per restoration process as interval bars |
| `reliability/scripts/record_indices.py` | Section 6.4 | Measured SAIFI and SAIDI of the 11 kV network faults of the record (`results/record_indices.csv`) |
| `reliability/results/mc_reliability_results.json` | Section 6.4 | Monte Carlo results: base case and the all-stations-remote sensitivity |
| `reliability/data/start_reykjavik_rows_raw.csv` | Table 2.1 | Every row of Orkuveita Reykjavíkur, Rafveita Reykjavíkur and Veitur in the START reliability reports (years 1996 to 2024) |
| `reliability/data/start_veitur_series_1996-2024.csv` | Table 2.1 | One row per year 1996 to 2024 from the newest report covering it, with the revision range |
| `reliability/scripts/start/` | | Parser of the START reports, series builder and figure (see its README) |

Rerun: `python3 ../reproduce.py ch6` (about 1.5 min).
