# ComPass emulation with three phase sensors (3CT)

Veitur's ComPass B 2.0 units form the residual current as the sum of their three phase-current sensors (3CT). The
emulation of thesis Section 6.1 was therefore repeated with a load-dependent residual-current error (`ef_3ct.py`).
Only the device-error model changes: the network cases, the 1904-case sweep and the eight PowerFactory anchors are
those of the first run. The first run used a fixed residual-current error of ±3 % or ±0.1 A; in the tables its rows
carry the label `SumCT`.

## Results

**Akranes systems in the isolated variant (busbar 1 and 2 as built, coupled, restoration states), winter peak and
summer minimum.** The ComPass bays carry at most 89 A of load (D1029_102, winter peak; 32 A at summer minimum), so the
3CT error stays small.
- With I_EQ> = 5 A, every on-path bay keeps at least 99 % Direction B for R_F ≤ 30 Ω, at every phase-angle error up to
  ±2° and every unbalance option. No opposite or false indication occurs on any off-path bay.
- Reach (largest R_F with ≥ 95 %, V_NEQ> 20 %) at 5 A: 300 Ω in every Akranes system, as in the first run. The one
  exception is busbar 2 at winter peak with ±2°, which drops to 100 Ω.
- Busbar 1, coupled and the restoration states also keep 99 % and 300 Ω at 10 A.

**Busbar 2 as built (smallest forward current 10.3 A).**
- At 5 A: ≥ 99 % on the path for R_F ≤ 30 Ω at every θ and load level. Reach 300 Ω, or 100 Ω at ±2° and winter peak.
- At 10 A: the lowest on-path probability for R_F ≤ 30 Ω is 0.58 at winter peak and 0.69 at summer minimum (±1°,
  median unbalance), and 0.51 to 0.73 over all θ and unbalance options; 0.86 in the first run. A 10 A pickup therefore
  leaves busbar 2 as built uncovered.

**Capital-region sizes (120 and 200 A), uniform bay load.**
- On the fault path the 3CT error never matters: the forward currents are 109 A and more, so every pickup from 5 to
  30 A gives 100 % at R_F ≤ 30 Ω. At 10 A and 20 % the reach is 100 Ω, set by the displacement voltage.
- The limit is the off-path criterion: the load error makes healthy bays indicate Direction B. The table gives the
  smallest pickup with ≥ 99 % on the path and ≤ 1 % opposite or false indications on every off-path ComPass bay, for
  split-core sensors (±1 %) with median unbalance, and the off-path probability at 10 A in brackets.

| Bay load | θ ±0.5° | θ ±1° | θ ±2° | Does 10 A meet the criteria? |
|---|---|---|---|---|
| 50 A | 5 A (0 %) | 5 A (0 %) | 5 A (0 %) | yes |
| 150 A | 5 A (0 %) | 5–10 A (0 %) | 10 A (0.2–0.5 %) | yes |
| 300 A | 10 A (0 %) | 10 A on busbar-2 topology (0.4–0.7 %), 15 A on busbar-1 topology (1.3–1.4 %) | 20 A (9.5–12.6 %) | up to ±1°, marginal on the busbar-1 topology |
| 450 A | 10–15 A (0.3–1.3 %) | 15–20 A (4.8–8.4 %) | 30 A (20–24 %) | no: 15 to 30 A needed |

- Busbar-2 topology means bb2_120 and bb2_200; busbar-1 topology means bb1_120 and bb1_200. The busbar-1 topology has
  more ComPass bays off the path and so a larger maximum.
- At the factory pickup of 5 A, healthy bays give false indications in up to 16 % of samples at 300 A and 26 % at
  450 A per bay (±1°).
- On the 40 and 80 A systems the reach at 10 A falls from 300 Ω to 100 Ω at higher bay loads, and the 40 A system has
  no pickup that meets both criteria at 450 A with ±1° or at 300 A with ±2°.
- The phase-angle error θ dominates. The sensor class matters little: closed bushing sensors (±0.5 %) need the same
  pickup as split-core sensors from ±1° upward. The measured unbalance has no visible effect (see the error model).

**Earth short-circuit element IES> = 10 A in the earthed Akranes network, winter peak.** The table covers healthy
ComPass bays (not on the A20-to-fault path) over all earthed fault cases of the study matrix.

| θ | Largest measured \|3I0\| | Largest 3CT error | Load error alone, no fault: maximum (99th percentile) |
|---|---|---|---|
| 0 (gain only) | 6.4 A | 1.8 A | 1.6 A (1.3 A) |
| ±0.5° | 7.1 A | 3.1 A | 2.8 A (1.7 A) |
| ±1° | 7.5 A | 4.8 A | 4.0 A (2.6 A) |
| ±2° | 10.7 A | 8.0 A | 6.9 A (4.6 A) |

- Load error alone cannot pick up IES> = 10 A on a healthy Akranes bay at any θ up to ±2°. The largest error is at
  D1029_102 with 89 A of load.
- During an earthed fault, a healthy bay reaches 10 A only at ±2°, and then in at most 0.1 % of samples (D1029_102,
  faults at F13H and F09H). The rest of its measured value is its true residual current.
- Bay loads above about 130 A (±2°) or 220 A (±1°) would bring the load error alone to 10 A. This is a scaling of the
  Akranes maxima, not a simulated case.

## Manual values and their pages

Sources:
- Horstmann, *ComPass B 2.0 / ComPass BS 2.0 (1250 A)*, operating instructions 104101-0124, September 2019 (the manual).
- Horstmann, *Application Note: Modbus Protocol, ComPass A 2.0 / B 2.0 / BS 2.0*, 104101-0137, June 2020 (the
  application note).

| Item | Value | Page |
|---|---|---|
| Current sensor sets | 3 phase sensors; or 2 phase + 1 summation; or 3 phase + 1 summation | manual p. 5 |
| Phase sensor types | closed bushing 49-6025-xxx; split-core cable type 49-6024-xxx | manual p. 6 (Tab. 2.1) |
| Split-core phase sensor accuracy (49-6024) | ±1 % of measured value or ±0.5 A, 0–630 A; ±5 % 630–1500 A | manual p. 37 |
| Closed bushing phase sensor accuracy (49-6025) | ±0.5 % or ±0.5 A, 0–630 A; ±3 % 630–1500 A | manual p. 37 |
| Phase-angle error of the current sensors | not stated in the manual or the application note (run as ±0.5°, ±1° and ±2°) | none |
| Compensation of the 3CT residual current | none described. The amplitude and angle correction (±5 %, ±120 min) applies to the resistive voltage sensors only | manual p. 40 |
| LimitIE (0.1 A) | lower limit from which the residual current is shown in the display: a display threshold, not applied to detection | manual p. 40 |
| CT Select | 2 CT + SumCT, 3 CT + SumCT, 3 CT (default 3 CT) | manual p. 39 |
| Vnom | 0.050–145 kV, default 20.000 kV | manual p. 39 |
| sin φ method | VNEQ> 10–100 % (default 30 %), IEQ> 1–200 A (5 A), tIEQ> 40–60 000 ms (3000 ms) | manual p. 40 |
| IES> earth short circuit | 10–1000 A (default 100 A), tIES> 40–60 000 ms (160 ms) | manual pp. 37, 40 |

The application note is a Modbus register map. It contains no accuracy, phase-angle or 3CT information.

## Factory defaults that matter at commissioning

The defaults in ComPass 2.0 Explorer agree with the manual (pp. 39–40). Three of them matter for the study:

1. **Vnom, default 20.000 kV.** It must be set to 11 kV. The study assumes that VNEQ> is a percentage of the
   phase-to-earth voltage of Vnom; the manual does not state the reference. If so, a unit left at 20 kV on the 11 kV
   network applies VNEQ> = 30 % at 54.5 % of the 11 kV phase voltage, and by thesis Eq. (3.1) the reach falls to about
   460 Ω on busbar 2, 160 Ω on busbar 1 and 120 Ω coupled, against 970, 340 and 250 Ω at 30 %.
2. **tIEQ>, default 3000 ms.** The response delay must lie well below the 1 s high-set earth-fault stage at A20.
3. **Phase CT type, default bushing 49-6025.** The parameter must match the installed sensors.

## Error model (ef_3ct.py)

- **Measured residual current:** 3I0_meas = Σ_k m_k(I_k)·e^{jθ_k} over the three phases.
  - At |I_k| ≥ 50 A: m_k = I_k (1 + g_k), with g_k uniform in ±1 % (split-core) or ±0.5 % (bushing).
  - Below 50 A: m_k = I_k + e_k, with |e_k| uniform in 0–0.5 A at a random angle.
  - θ_k is uniform in ±θ, drawn independently per phase and sample.
  - LimitIE is not applied, because it is a display limit.
- **Phase currents:** I_k = load + fault contribution.
  - Load: the positive-sequence current of the bay.
  - Fault contribution: 3I0/3 + I1 + I2, with the positive- and negative-sequence bay currents taken from the
    faulted-network solution (Z2 = Z1, I1 = I2 = I0 at the fault).
- **Unbalance option:** a negative-sequence load component of random angle, sized so that the max/min phase ratio equals
  the measured median or maximum (`../../ch5_powerfactory_benchmark/data/validation/holdout_validation_metrics.csv`):

  | Load level | Median | Maximum |
  |---|---|---|
  | Winter peak | 1.13 | 1.33 |
  | Summer minimum | 1.09 | 1.35 |
  | Uniform loads | winter values | winter values |

  In an isolated network the load carries no zero-sequence current, so unbalance only rescales the phase errors. It
  has no visible effect.
- **Unchanged from the first run:** the ±5° angle error; the displacement-voltage error (±10 % with standard
  calibration, ±1 % with reference calibration); the standing V0 of 2 %; the 1000 samples and the seed. These errors
  are drawn in the original order from the original seed, so both runs use identical voltage errors (common random
  numbers). The 3CT draws come from a separate seeded stream and are paired across load levels.
- **Load levels:**
  - Akranes systems: an offline positive-sequence load flow of the allocated loads of the hold-out snapshots
    winter_peak_boiler_off and summer_night_min, with each load moved to its transformer's 11 kV node.
  - Systems with added capacitance (40 to 200 A): a uniform 50, 150, 300 and 450 A on every bay, at power factor 0.95
    inductive, flowing away from A20. This includes end bays that carry no load in reality, which is conservative.
- **Settings grid:** I_EQ> = 5, 10, 15, 20 and 30 A; V_NEQ> = 10, 20 and 30 %; R_F = 0, 10, 30, 100, 300, 1000 and
  3000 Ω; both calibrations.
- **Criteria (as in thesis Chapter 6):** an on-path bay is a ComPass bay on the A20-to-fault path facing the fault.
  "Off-path" means every other ComPass bay. A false indication is an indication opposite to the true direction, or any
  indication where none is expected.
- **Monte Carlo resolution:** with 1000 samples, a probability near 1 % has a standard error of about 0.3 %. Each
  reported value is the maximum over many bays, which biases it upward. Values between 1 % and 1.5 % (for example
  busbar-1 topology, 300 A, ±1°) are therefore marginal, not clear failures.

## Checks

- **First run reproduced:** the same code reproduces `results/offline_emulation.csv.gz` exactly (largest difference
  0.0000 over all rows and settings), and its direction and coverage tables agree with `results/ch6/direction_probability.csv`
  and `coverage_rf.csv` on all 336 overlapping rows.
- **Fault-contribution solve:** the 3I0 at every bay equals `results/offline_phasors.csv` within 5 µA.
- **Load flow:** the winter-peak feeder-head currents above 10 A agree with the allocation within 0.8 %. In the summer
  snapshot the August open points split circuits 08 and 13 differently from the study configuration (the December 2025
  switching state); the 08 + 13 sum agrees (39.8 A against 39.7 A).
- **Anchors:** the network cases are those of the first run, and `compare_sources.py` gives 8 of 8 anchors within the
  targets at every bay (33/33, and 31/31 for the SCN-15 restoration state).
- **Reproducibility:** repeated runs give byte-identical outputs.

## Running

`python3 ef_3ct.py` (about 7 min) writes the tables below; `python3 ef_3ct.py --summary` rebuilds `summary_3ct.csv`
from them; `ch6_figures_3ct.py` draws the figure. `../../reproduce.py ch6` runs both.

## Outputs (results/ch6/)

The four main tables have the column layout of the first-run tables, with error_model, phase_sensor, theta_deg,
unbalance and load_level after system; the first-run rows (`SumCT`) are included in each.

| File | Contents |
|---|---|
| direction_probability_3ct.csv | the direction table; adds max_P_opposite_or_false_offpath |
| path_probability_rf_3ct.csv | on-path probability per R_F |
| coverage_rf_3ct.csv | reach per setting |
| windows_3ct.csv | strict window, with the pickup range taken from the settings grid |
| summary_3ct.csv | per system and load level: smallest pickups, reach at 5 and 10 A, probabilities at 10 A |
| ies_check_3ct.csv | the IES> check |
| bay_loads_3ct.csv | the bay load phasors per configuration and snapshot |

Figure: `../../thesis_figures/ch6/direction_probability_3ct.pdf` (thesis Figure 6.4).
- (a) The lowest on-path probability against the pickup, three phase sensors (±1°) solid and the first run dashed.
- (b) The off-path false-indication probability against the pickup for the 120 and 200 A systems, per bay load, at ±1°
  and ±2°.
