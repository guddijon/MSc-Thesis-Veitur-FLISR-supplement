# Chapter 4: data audit and topological remediation

| Path | Thesis | Contents |
|---|---|---|
| `sql/transformer_query.sql` | Figure B.1 | Transformer codes and winding types of substation A0020 |
| `sql/cable_query.sql` | Figure B.2 | Cable codes and lengths of the A020 cable groups |
| `data/dpa_coverage_data.csv` | Figure 4.1 | Population of the DPF properties across the ADMS model: populated and total live components per property |
| `scripts/dpa_coverage_fig.py` | Figure 4.1 | Draws the coverage figure from the CSV |
| `scripts/dpa_timeline_fig.py` | Figure 4.4 | Use of the ADMS power-analysis functions, 2013 to 2026 (dates in the script) |
| `scripts/a20_station_figs.py` | Figures 4.2, 4.3 | Allocation of the A20 circuits to the busbars on three dates (breaker states in `../ch5_powerfactory_benchmark/data/snapshots/`); GIS and ADMS lengths of the four contradicted links (`../ch5_powerfactory_benchmark/data/validation/gis_vs_model_lengths.csv`) |
| `../thesis_figures/ch4/` | Figures 4.1 to 4.4 | The figure files, drawn by the scripts above |

The queries run against the GE PowerOn ADMS (ENMAC schema, as documented by the vendor; thesis Appendix B, ADMS Extraction Queries). The
audit results are reported in the thesis tables of Chapter 4 at the level of counts and aggregates; component-level
ADMS records are not part of the supplement. The GIS trace of the 62 station-to-station links behind the length check (paragraph "Lengths against the GIS" and
Figure 4.3) is in `../ch5_powerfactory_benchmark/data/validation/gis_vs_model_lengths.csv` (model and GIS length per
link).

Rerun: `python3 ../reproduce.py ch4` (outputs in `output/`).
