# Parameter decisions for the PowerFactory model

Scope: generalised parameters for the earth-fault study and the remaining assumptions of the base model. No topology
or load changes. The base model is the run case; the items below are type data and labelled sensitivity cases.

## 1. Decisions

| Item | Decision |
|---|---|
| A20 11 kV neutral treatment | Not established by the available evidence; carried as two bounding cases. Variant (1) solidly earthed star points (Re = Xe = 0), variant (2) star points open (isolated). Both are run and reported; no "base" earthing case is declared. The A20 protection design (110/3 V residual VT winding, 200/1 A core-balance CTs) points to (2). No resistor, reactor or coil value is assumed. |
| 66 kV neutrals of S1 and S2 | Earthed directly (Landsnet SLD AKR-E012 rev. 3). Modelled as solid. |
| 66 kV short-circuit level | Sk'' = 500 MVA, R/X = 0.1, Z0 = Z1 is the run value. Sensitivity at 373 MVA (Landsnet 2015 max, best present estimate) and 197 MVA (2015 min); bracket 160-500 MVA. One extra short-circuit run at 373 MVA per earthing variant. |
| Cable datasheets and transformer test reports | Out of scope. The published type data below are used, labelled "datasheet (type)" or "generic". |
| Switch ratings | From the ADMS free-text Rating attribute, mapped in switch_ratings_model_map.csv. The binding thermal constraint is the feeder alarm limits; no ring switch is below 400 A. |
| Restoration scenario list (tab:pf_scenarios, 15 cases) | SCN-05 is a fault on the SFAA cable on circuit 04 (the boiler network is customer-owned); SCN-08 is a midline fault on circuit 22 at D1036. Details in procedures/restoration_scenario_sheets.md. |

## 2. Cable type data (used instead of the ADMS catalog values in the earth-fault study only)

Source family: NKT AXAL-TT PRO 6/10(12) kV, the 12 kV PEX cable sold in Iceland (Johan Rönning). Nexans Axclight TT
and Prysmian AXALJ-TT give the same construction; Prysmian is the sensitivity set. R at 20 C; 90 C derived with
alpha = 0.00403/K (Al). X1 = 2*pi*50*L. C0 = C1 for screened XLPE. R0 = R_conductor + 3*R_screen (reproduces the NKT
table exactly); X0 as tabulated (screen return only). The ADMS positive-sequence R1/X1 are kept for the load flow so the
validated baseline is unchanged; only the capacitance and zero-sequence columns differ.

| ADMS code | Type | R1 20C (ohm/km) | X1 (ohm/km) | C1 = C0 (uF/km) | Ic at 11 kV (A/km) | R_screen (ohm/km) | R0 (ohm/km) | X0 (ohm/km) | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| OR_3A_XLPE_240_12 (and 0R_..., 22.9 km) | 3x240/50 Al | 0.125 | 0.085 | 0.41 | 2.45 | 0.6 | 1.93 | 0.08 | datasheet (type); ADMS catalog 0.65 uF/km |
| OR_3A_XLPE_150_12 (2.6 km) | 3x150/35 Al | 0.206 | 0.091 | 0.33 | 1.97 | 0.8 | 2.61 | 0.08 | datasheet (type); ADMS catalog 0.65 uF/km |
| OR_3A_XLPE_50_12 (0.9 km) | 3x50/25 Al (Rönning item TJX713008) | 0.641 | 0.110 | 0.22 | 1.32 | 1.2 | 4.24 | 0.09 | datasheet (exact product) |
| OR_1A_XLPE_95_12, OR_1A_XLPE_240_12 (20 m total) | single-core | IEC 60228 | ADMS | 0.32 / 0.41 | - | - | R_c + 3 R_screen | ADMS | immaterial; note only |
| OR_3C_XLPE_16/25_12 (few m) | 3-core Cu | 1.15 / 0.727 | ADMS | 0.18-0.22 | - | 1.2 | R_c + 3.6 | 0.10 | immaterial |

Prysmian AXALJ-TT sensitivity set (same sizes): C 0.46 / 0.38 / 0.25 uF/km; R0 0.65 / 0.76 / 1.31; X0 0.56 / 0.68 /
0.87 ohm/km (X0 includes earth return, hence the difference from NKT). The earth-fault matrix is run once with each
set for variant (1); variant (2) depends on C only.

PILC, belted, lead sheath (8.2 km: 3x70 Cu 6.1 km, 3x120 Cu 0.6, 3x150 Al 0.7, 3x240 Al 0.9). No datasheet for the
installed make; used as a RANGE, labelled "generic":

| ADMS code | R1 20C | X1 | C1 (uF/km) | C0/C1 | R0 (ohm/km) | X0 (ohm/km) | Source of R0/X0 |
|---|---|---|---|---|---|---|---|
| OR_3C_PILC_70_11 | 0.268 | 0.110 (ADMS) | 0.48 (ADMS) to 0.53 (BS 6480 max) | 0.6 to 0.83 | 1.47 | 0.11 | CBI/African Cables 6.35/11 kV tables |
| OR_3C_PILC_120_11 | 0.153 | 0.110 | 0.48 to 0.67 | 0.6 to 0.83 | 1.17 | 0.10 | same |
| OR_3A_PILC_150_11 | 0.206 | 0.090 | 0.48 to 0.73 | 0.6 to 0.83 | 1.03 | 0.105 | same |
| OR_3A_PILC_240_11 | 0.125 | 0.090 | 0.48 to 0.90 | 0.6 to 0.83 | 0.82 | 0.10 | same |

C0/C1 = 0.83 (Northern Powergrid IMP/001/013) is the main value and 0.6 (Happoldt, via Phase to Phase) as the
low case. PILC is 23 % of the cable, so the C0 range moves the Akranes isolated-network Ic by roughly +/-5 %.

Resulting Akranes isolated-network capacitive current (variant 2), datasheet values: about 2.45 A/km XLPE and about
2.3-2.9 A/km PILC, i.e. roughly 85 A for the whole 36 km instead of the 140 A the ADMS catalog implies. Both are reported.

## 3. Transformers

S1, ETRA RT 25000-66/11, 25 MVA, YNyn0, no tertiary, uk = 10.01 % (nameplate), Zbase(11 kV) = 4.84 ohm, Zk = 0.485 ohm.
- Core: not confirmed; assume three-limb (generic).
- Zero-sequence, 66 kV neutral earthed and 66 kV system providing a zero-sequence path (Z0 = Z1 at the grid): Z0 seen
  from 11 kV = a2*Zk with a2 = 0.8-1.0 (IEC 60076-8); 0.9*Zk = 0.44 ohm is used; sensitivity 0.39-0.48 ohm.
- Zero-sequence magnetising branch (open 66 kV neutral case, not run): 0.43-0.50 pu, i.e. about 2.1-2.4 ohm at 11 kV.
- Cross-check only: Veitur document ORVV09.docx records R0 = 32.21, X0 = 85.37 from a January 2008 test report, units
  and reference side unconfirmed. If ohms at 66 kV: |Z0| = 52 % on 25 MVA, consistent with the single-side-earthed
  measurement (IEC 60076-8 typical 50-60 %). Not entered as a model value.
- Losses, X/R: not available; the model assumptions are kept and labelled.

S2, EBG (Elektro Bau AG, Linz) DOR 20000/60, 16 MVA, 63/11 kV star in service, delta tertiary 3.15 kV 5.333 MVA,
uk = 7.53 % (nameplate; the service record says 8.0 %), Zbase(11 kV) = 7.56 ohm, Zk = 0.569 ohm.
- Three-winding model where practicable, YNyn0d1. Pairwise impedances HV-tertiary and LV-tertiary are not available:
  use the IEC 60076-8 worked ratios (ZH 0.05, ZX 0.15, ZY 0.25 pu with ZM 0.45) scaled so that ZH + ZX = uk, labelled
  generic. Z0 from the 11 kV side = a2*(ZX + ZH||ZY), a2 = 0.98.
- Rule of thumb check: with a delta tertiary, Z0 = 0.8-1.0 * Zk.
- S2 normally carries busbar 2 only; its zero-sequence model matters for the split-busbar variant (1) on busbar 2
  and for the coupled N-1 case.
- Identity conflict (not resolved): the ADMS and the 2022 service record call S2 "TTHF 16000/63, serial
  136601, uk 8.0 %"; the nameplate reads DOR 20000/60, 1985, uk 7.53 %. The nameplate values are used.

Distribution transformers, Dyn5, 11(6.3)/0.4 kV: uk 4 % (160, 500 kVA), 6 % (800, 1250, 1600 kVA); losses per EU
Regulation 548/2014 Tier 2 limits (e.g. 1600 kVA: P0 1080 W, Pk 12 000 W) as generic values; delta on 11 kV, so no
zero-sequence path on the MV side. Older units have higher losses; immaterial for the earth-fault study.

## 4. A20 switchboard data (Veitur drawing 126-NR-2001, 16.07.2021; relay-setting register for 1 A ratios)

- Busbars 12 kV, 31 kA. Feeder and coupler breakers 1250 A. Incomers: drawing queries 2000 A (S1) and 1250 A (S2).
- Phase CTs 400/1/1 A on the feeders (800/1/1 A on bays 004, 011, 017, 021), core-balance CTs 200/1 A on the cable
  panels, incomers 1600-800/1/1 A, auxiliary and VT bays 100/1/1 A. The 2021 drawing shows /5/5 secondaries; the
  2024 issue and the setting register show /1/1. Ratios only; no accuracy class, burden or ALF is known.
- Busbar VTs: 11/sqrt3 kV : 110/sqrt3 V : 110/3 V (open-delta residual winding), one set per busbar.
- A0020 breakers do not bind thermally (1250 A against feeder limits of 160-320 A).

## 5. Files

- Switch ratings: switch_ratings_model_map.csv and switchgear_ratings_sheet.md
- Zero-sequence type data as entered: ef_parameter_sheet.md and ef_cable_type_values.csv
- Sources (cited in the thesis): NKT AXAL-TT PRO 6/10(12) kV datasheet; Prysmian AXALJ-TT
  datasheet; Northern Powergrid IMP/001/013; Phase to Phase, Networks for Electricity Distribution; IEC 60076-8;
  Landsnet Kerfisáætlun 2012 and 2015-2024; Veitur drawing 126-NR-2001.
