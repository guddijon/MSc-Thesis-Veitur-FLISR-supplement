# Enabling FLISR in Veitur's ADMS: thesis supplement

Supplementary data, models and scripts for the M.Sc. thesis *Enabling FLISR in Veitur's ADMS: DPA Validation and
Earth-Fault Feasibility* by Guðjón Hafsteinn Kristinsson (Reykjavik University, Iceland School of Energy, 2027).

The study network is Veitur's 11 kV distribution network in Akranes, fed from primary substation A20. The supplement
holds what is needed to check and rerun the results chapters: the aggregated audit data of Chapter 4, the PowerFactory
benchmark of Chapter 5, the earth-fault study and the reliability analysis of Chapter 6, and the sources of the
figures drawn for the thesis. Use is subject to the licence below.

## Contents by thesis chapter

| Folder | Thesis | Contents |
|---|---|---|
| `ch4_data_audit/` | Chapter 4, Results I: ADMS Data Audit; Figures 4.1 to 4.4, B.1 and B.2 | ADMS extraction queries, DPA coverage data, figure scripts |
| `ch5_powerfactory_benchmark/` | Chapter 5, Results II: PowerFactory Baseline and Reference Switching Sequences; Figures 5.1 to 5.6, Tables 5.1 to 5.11 | PowerFactory model (DGS and project), parameter sheets, snapshot inputs, load allocation, validation results, restoration and defect scenarios with the PowerFactory exports, run sheets, scripts |
| `ch6_earth_fault_and_reliability/` | Chapter 6, Results III: Earth-Fault Feasibility and Reliability Benefit | Earth-fault study package (offline sequence-network model, ComPass emulation, PowerFactory run sheet and script); reliability Monte Carlo and the START series 1996 to 2024 |
| `thesis_figures/` | All chapters: every figure of the thesis, by chapter (`ch1/` to `ch6/`; Chapters 7 and 8 have none) | Figure files, an index of the script or source of each figure, and the scripts of the Chapter 2 and 3 illustrations |

Each chapter folder has its own README with the file list and the thesis tables and figures each file supports.

## Reproducing the results

Python 3.11 or later with the packages in `requirements.txt`; the figures use the Liberation Sans font.

```
pip install -r requirements.txt
python3 reproduce.py            # all parts, about 10 min; or e.g. python3 reproduce.py ch5
```

`reproduce.py` runs every script whose inputs are in the supplement, writes the results into an `output/` folder of
each part, and compares them with the files of record. Steps that need material outside the supplement are listed
when it finishes:

- the per-bay ComPass measurements of the hold-out validation (station-level results are included);
- the PowerFactory runs themselves (PowerFactory 2025; the model, the run sheets and the exports are included);
- the START report PDFs (public reports, cited in the thesis);
- the national energy forecast results workbook for Figure 2.23 (cited in the thesis; give its path in `ORKUSPA_XLSX`).

## Data notice

All data derive from Veitur's systems (ADMS, SCADA historian, GIS, OMS and outage reports) and are published with
Veitur's permission. Measurements are aggregated to the station or feeder level; no per-customer data, operator names
or other personal data are included. Station names and positions are those of Veitur's public
network maps.

## Licence

© 2027 Guðjón Hafsteinn Kristinsson. All rights reserved. See `LICENSE.md`. For permission to use any part of the
supplement, contact the author.
