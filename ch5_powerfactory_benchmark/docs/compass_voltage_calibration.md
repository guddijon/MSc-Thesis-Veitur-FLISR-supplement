# ComPass voltage channels: one-point field calibration

Source: Veitur operating practice.

Fact: the ComPass voltage channels at the remotely controlled substations are calibrated once, live, against a nominal
line-to-line voltage of 11.00 kV. The installer scales the channel so that it reads 11.00 kV at whatever the network
voltage is at that moment.

Consequence: a channel's reading is the true voltage multiplied by 11.00 / V_cal, where V_cal is the unknown network
voltage at calibration time. The +/-1 % ComPass class describes the channel around that scale; it is not the absolute
accuracy. The absolute error is systematic per station and equal to the calibration-time deviation from 11.00 kV.

Check against the hold-out validation (winter peak, 10 Dec 2025 17:55; simulated voltage taken as the estimate of the
true voltage): implied V_cal = 11.00 x simulated / recorded.

| Station | simulated kV | recorded kV | implied V_cal kV |
|---|---|---|---|
| D1029 | 11.110 | 10.982 | 11.13 |
| D1066 | 11.097 | 10.871 | 11.23 |
| D1025 | 11.063 | 10.937 | 11.13 |
| D1030 | 11.053 | 10.899 | 11.16 |
| D1001 | 11.198 | 10.943 | 11.26 |

All implied calibration voltages lie inside the 11.1 to 11.3 kV band observed on the A20 busbars, so the snapshot mean
"offset" of +1.6 to +2.1 % (holdout_validation.md) is consistent with the calibration practice. The
calibration dates and the busbar voltage at those dates are not recorded; if Veitur holds them, the
implied V_cal can be checked station by station.

Figure treatment: ComPass voltages are drawn as recorded without an uncertainty bar (Figures 5.3b and
5.4); the A20 VT keeps its 0.1 kV storage-step bar; ComPass currents keep the +/-1 % or +/-0.5 A class bar on the
assumption (not confirmed) that the current channels are not field-scaled in the same way.
In the thesis the deviation is presented as the calibration reference, not as a sensor offset to be removed.
