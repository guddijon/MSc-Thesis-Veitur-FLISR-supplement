# Switchgear ratings in the PowerFactory model

Source: ADMS asset attribute "Rating" (264 devices at 56 stations), mapped to the model in switch_ratings_model_map.csv
(195 ADMS bays; 143 map to a named model switch, 52 are line bays of the remote-controlled stations and transformer
bays of stations outside the model, see below). A20 breakers: Veitur drawing 126-NR-2001 (parameter_decisions.md,
Section 4).

## Switch objects and types in the DGS file
- 162 Breaker/Switch elements (ElmCoup): 43 A20 breakers (usage circuit-breaker), 101 station bay switches named
  `SSSS-1-n` (usage disconnector, 93; load switch, 13), 3 bus-side switches, 2 at D1034, 1 bus coupler.
- 380 cubicle switches (StaSwitch): 61 transformer HV switches `Cub_Dxxxx_S-11-0k_HV`, 80 cable-end switches `Sw_*`
  at the F-11-0n terminals, 239 line-end switches with GUID names (GIS import).
- One placeholder type `1002-1-1` with rated current 0.04 kA on 120 ElmCoup and 147 StaSwitch (267 objects); 29
  per-bay types on the transformer-bay switches, rated current = fuse (0.063 / 0.08 / 0.1 kA) or 0.

## Ratings by class (ADMS)
| Class | Rated current | Devices | Model objects |
|---|---|---|---|
| Ring/line bays, ordinary stations | 630 A | 75 bays | ElmCoup `SSSS-1-n`, placeholder type |
| Ring/line bays, Eaton units D1030, D1056 | 600 A | 4 bays | 1030-1-1, 1030-1-2, 1056-1-1, 1056-1-2 |
| Ring/line bays, D1070 (Eaton) | 600 A | 2 bays | line-end cubicle switches at D1070 (no named object) |
| Ring/line bays, remote-controlled stations (B11/T11 pairs) | 630 A | 36 bays | line-end cubicle switches (GUID names) |
| 400 A bays | 400 A | 1005-1-1 (tie to boiler network), 1014-1-2, 1014-1-3, D1014 transformer bay | ElmCoup / Cub_D1014_S-11-01_HV |
| Transformer bays, switch-fuse or breaker | 200 A (46), 630 A (14) | 60 bays | `Cub_Dxxxx_S-11-0k_HV` and the per-bay ElmCoup types |
| A20 feeder breakers | no ADMS value; 1250 A from the switchboard drawing | 43 | A20 breakers, type `CB_1250A_A20` |
| No rating | D1025_R11-103 ("---A"), D1034_T11-101..103 | 4 | no ADMS value |

Conclusion: every ring/line bay is rated 600 A or more and the two 400 A ring bays sit on circuits whose operating
limits are 160 A (06) and 260 A (04/22); the switchgear is never the binding thermal constraint in a back-feed, the
feeder alarm limit of tab:a20_limits is. The ratings are entered so that the PowerFactory loading colouring and the
thesis inventory carry real ratings, not 40 A placeholders.

## GUI steps (base data, no scenario active)
1. Equipment Type Library, Switch Types: open type `1002-1-1` (the one used by 267 objects). Rename it `SW_630A_ring`,
   Rated Current 0.63 kA, Rated Voltage 12 kV. One edit covers all ring/line bays and line-end switches.
2. New switch types in the same folder: `CB_1250A_A20` (1.25 kA, 12 kV), `SW_600A_Eaton` (0.6 kA, 12 kV),
   `SW_400A` (0.4 kA, 12 kV), `SW_200A_trafo` (0.2 kA, 12 kV). Assign `CB_1250A_A20` to the 43 A20 breakers.
3. Assign `SW_600A_Eaton` to ElmCoup 1030-1-1, 1030-1-2, 1056-1-1, 1056-1-2 (Data Manager, ElmCoup table sorted by
   name; Type cell, select the type). D1070's 600 A bays have no named switch.
4. Assign `SW_400A` to ElmCoup 1005-1-1, 1014-1-2, 1014-1-3 and to StaSwitch Cub_D1014_S-11-01_HV.
5. Transformer bays: the 61 `Cub_Dxxxx_S-11-0k_HV` switches use the placeholder and read 630 A after step 1.
   Assign `SW_200A_trafo` to the 46 bays rated 200 A (list in switch_ratings_model_map.csv, role transformer bay,
   Ir_bay_A 200); the 14 rated 630 A keep `SW_630A_ring`.
6. The per-bay types with rated current 0 (1002-1-2, 1002-1-3, 1003-1-6, 1008-1-1, 1008-1-4, 1009-1-4, 1012-1-1/2/3,
   1014-1-2/3, 1016-1-1/2, 1017-1-1, 1018-1-2, 1020-1-3, 1034--1, 1034--2): these are ring/line bays with their own
   type in the DGS file. Set their rated current to 0.63 kA (0.4 kA for 1014-1-2 and 1014-1-3). The fuse types
   (0.063/0.08/0.1 kA) stay: they are the transformer-bay fuses and are correct as protection data.
7. Load flow on the base data: result unchanged (ratings do not enter the solution). Export the Breaker/Switch table
   with the columns Name, Type, Rated Current (typ_id:Inom); the exports are in `data/pf_exports/model_parameters/`
   (`breaker_types.txt`, `station_switch_types.txt`, `switch_types.txt`, `breaker_currents_base_case.txt`,
   `loadflow_log_switch_ratings.txt`).
