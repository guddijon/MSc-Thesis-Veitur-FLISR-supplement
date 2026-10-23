# Reliability Monte Carlo (Section 6.4, RQ5): assumptions and inputs

Script: `scripts/mc_reliability.py` (results `results/mc_reliability_results.json`), figure
`scripts/mc_reliability_bars.py` -> `../../thesis_figures/ch6/reliability_saidi_intervals.pdf`. Seed 20261022, 20 000 blocks of
10 years (base and sensitivity).

## Inputs
| input | value | source |
|---|---|---|
| customers | 3 516 in 47 stations; six model stations without register entry set to 0 (D1017, D1059, D1061, D1062, D1067, D1069) | OMS register enmac.RPT_CUSTOMERS, 20 Oct 2026 (customers_per_station.csv) |
| fault record | seven fault days in 6.83 a (Jan 2020 to Oct 2026): five single-feeder days, two busbar days | outage report forms and switching log (akranes_fault_stages_2020-2026.csv) |
| response (trip to first switching operation) | 36, 26, 29, 41, 31, 68, 52 min | the seven fault days |
| crew sectionalizing (to first restoration) | 63, 45, 38 min | the three single-feeder crew days |
| remote sectionalizing (to first restoration) | 22, 6 min | the two 2025 days with remote switching |
| trip to last customer restored | 154, 123, 116, 941, 125, 92, 478 min | the seven fault days |
| busbar re-closing | 41, 31 min | the two busbar days |
| topology | ten feeders, 51 stations with customers, section lengths of the supply tree (27.1 km of the model's 36.0 km: tie cables, the 2.2 km boiler cable and the de-energised D1069 tail carry no customers and are left out of the fault placement); ties 1003-1-6, 1004-1-2, 1012-1-1, 1018-1-2, 1020-1-4, 1031-1-2, 1058-1-2, D1022 B-11-01 | benchmark model, December 2025 base, sld_bays.txt and gis_vs_model_lengths.csv |
| remotely controlled stations | D1001, D1004, D1025, D1026, D1029, D1030, D1056, D1061, D1062, D1066, D1067, D1070 (12; D1069 de-energised) | model and ADMS; D1067 is assumed remotely switchable although its ComPass reads zero |

## Assumptions
1. **Fault population.** The seven fault days are the population: feeder or busbar faults that needed sectionalizing.
   The arrival rate 7 / 6.83 a = 1.02 /a is not used as a point value; each simulated decade draws its rate from the
   Jeffreys posterior Gamma(7.5, 6.83 a) (mean 1.10 /a, 5th to 95th percentile 0.54 to 1.83 /a), which reproduces the
   exact Poisson interval 0.41 to 2.11 /a at 95 %. A fault lands on a feeder with probability proportional to its cable
   length and on a section of that feeder with probability proportional to the section length; two of seven faults are
   busbar events (busbar 1 or 2 by the feeder drawn).
2. **Crew and remote stage durations** are resampled from the measured values above (empirical distributions, no
   fitted law). Response applies to both manual processes (it is the call-out of the on-call operator and crew; all
   seven trips fell between 00:01 and 04:46). The time to the last customer stands in for repair; it is bounded below
   by response + crew sectionalizing + 1 min.
3. **Automated FLISR** restores within 1 to 5 min (uniform) the customers it can reach by switching at the remotely
   controlled stations only: upstream of the nearest remotely controlled station above the fault (breaker re-close) and
   below the nearest remotely controlled station under the fault if that part contains a tie. The customers between
   those two switching points (the zone) wait for the crew's segment isolation at response + crew sectionalizing, the
   same time as in process (i). Customers below a fault whose subtree has no tie wait for the last-customer time in
   every process. Transfer capacity is assumed sufficient, which the restoration study of Chapter 5 supports for every
   case except the boiler-on SCN-05.
4. **Busbar events.** All customers of the busbar's feeders are interrupted for the measured busbar re-closing time
   in every process; the faulted feeder is then handled by the process rules, with no restoration earlier than the
   busbar re-close.

Process (ii) uses the same zone logic as FLISR with the measured remote sectionalizing time instead of the 1 to 5 min.
Process (i) isolates at segment level: all upstream customers and, if a tie exists below the fault, all downstream
customers are restored at response + crew sectionalizing.

## Counting conventions
SAIDI = customer-minutes / 3 516 per year, SAIFI = customer interruptions / 3 516 per year, each customer counted once
per event; these equal the Icelandic TSN and FSN. Every interruption is counted regardless of duration; a second SAIFI
counts only interruptions longer than 5 min (IEEE 1366 sustained threshold) and a third those longer than 3 min (the START breakdown); these are where FLISR differs. SMS and SRA
are not simulated: they weight by interrupted power, and the record shows that the faults occur at night when the
loads are far from the winter-peak values of the model. Reported statistics are the mean and the 5th, 50th and 95th
percentiles of the ten-year average over 20 000 simulated decades, so the interval carries both the rate uncertainty
and the decade-to-decade variability.

## Results
| process | SAIDI mean (p5, p50, p95) min/customer-a | SAIFI mean (p5, p95) | SAIFI > 5 min (p5, p95) | SAIFI > 3 min (p5, p95) | customer-minutes per fault, median (p5, p95) |
|---|---|---|---|---|---|
| (i) crew | 18.2 (5.1, 16.9, 35.5) | 0.278 (0.072, 0.550) | 0.278 | 0.278 | 55 400 (3 700, 122 600) |
| (ii) remote | 15.4 (4.4, 14.4, 30.1) | 0.278 | 0.278 | 0.278 | 47 200 (3 700, 103 900) |
| (iii) FLISR | 12.0 (3.1, 11.1, 23.8) | 0.278 | 0.220 (0.043, 0.457) | 0.249 (0.059, 0.503) | 31 200 (2 000, 96 400) |
| (iii) FLISR, every station remotely controlled | 6.7 (0.4, 6.0, 14.7) | 0.277 | 0.170 (0.000, 0.380) | 0.224 (0.045, 0.468) | 2 200 (200, 85 000) |

SAIDI components at the mean rate (min per customer-year): busbar re-closing 4.6 in every process; customers
restored by the process 13.3 (i), 4.4 (ii), 1.0 (iii); customers in the crew zone 0 (i), 6.2 (ii) and (iii); customers
waiting for repair 0.3 in every process. Sensitivity, every station remotely controlled: (ii) 13.0, (iii) 6.7, of
which 4.5 is the busbar component.

Checks: the simulated crew process gives 18.2 min per customer-year against 29.4 measured for the 11 kV faults of the
record (`scripts/record_indices.py`: 4 224 customers, 706 763 customer-minutes; 9.2 without the busbar-2 day of 26 Dec
2022, which alone holds 138 of the 201 customer-minutes per customer) and against the Veitur-wide TSN mean of 24.2 (all
causes, 2015 to 2024). SAIFI 0.28 against 0.18 measured.
