# Midnight Curve

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Ardian9712/gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Ardian9712/gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)

A deterministic forecast of GTA VI's launch-day Twitch viewers for hours 2–24,
anchored to the observed first hour. Python 3.13, standard library only.

## Method

Use complete 24-hour release-day curves from the case's comparables, excluding
the GTA VI pre-release category history. Prefer donors with at least 20,000
hour-1 viewers: these represent games already live at UTC midnight. With fewer
than five donors, relax to 10,000, then all complete curves. With no donors,
fall back to the house's widening log-normal forecast.

Each hour uses a weighted median of donor log(viewers / hour-1). When target
history exists, donor weights combine Gaussian similarity in log hour-1 scale
(bandwidth 2) and the previous day's normalized hourly shape (bandwidth 1.5).
Clip shape log-ratios to ±4 and mix the kernel half-and-half with equal weights
to retain broad donor support. History never includes observations after the
checkpoint. Without history the big-donor curve is unweighted.

Spread is weighted IQR / 1.349, floored at both 0.02 and the unweighted IQR
spread. This preserves the prototype's uncertainty calibration. Quantiles are
`p1 * exp(median_log_ratio + z * spread)`, with z = −1.645, −0.674, 0,
0.674, 1.645. Clamp to [1e-9, 1e9] and enforce non-decreasing order.
There is no network, randomness, clock dependence, or fitted external state.

## Local measurements

Comparable-only leave-one-out replay, scored with the rules' exact doubled
log-pinball loss. Each target's release-day future is removed from its input;
only its history through hour 1 is exposed. Parameters were chosen broadly
for stability, without a parameter sweep or holdout-based calibration.

| Evaluation | Cases | Model loss | House loss | Model 90% coverage | House coverage | Model typical miss | House typical miss | Wins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Big-regime LOO | 27 | 0.276065 | 0.321418 | 88.08% | 79.23% | 54.22% | 62.97% | 22/27 |
| Earlier-launch donors only | 22 | 0.284266 | 0.318952 | 82.02% | 79.84% | 55.38% | 62.59% | 17/22 |

Typical miss above uses the official pooled formula: 100 × (exp(mean absolute
log median error) − 1). For comparison with the original fit-test's arithmetic
mean of per-case miss percentages, LOO is 61.68% vs 71.39%, and chronological
evaluation is 63.73% vs 71.91%. The verified unweighted prototype's LOO loss
was 0.283553; similarity weighting improves it here by 0.007488. Chronological
evaluation requires at least five strictly earlier big donors. It is a useful
robustness check, but these comparables remain development evidence.

Practice cases p00–p03 contain no answers, so local practice validation checks
execution and output validity rather than forecast accuracy. An official
practice grade requires server submission. The final is one unseen launch;
these measurements do not establish its score or performance against the
house AI model.

Verified locally with Python 3.13.18, two fresh processes per practice case:

| Case | Output bytes | Slower execution | Shape | Repeated bytes |
| --- | ---: | ---: | --- | --- |
| p00 | 2,541 | 0.115 s | valid | identical |
| p01 | 2,533 | 0.179 s | valid | identical |
| p02 | 2,540 | 0.115 s | valid | identical |
| p03 | 2,536 | 0.115 s | valid | identical |

Every case has hours 2–24 exactly once, five finite quantiles per hour,
0 < q ≤ 1e9, ordered within each row, and output below 65,536 bytes. The
combined four-case run matches isolated outputs. Empty history, sparse/empty
donors, zero hour-1 viewers, minute-history fallback, upper clamping and
exclusion of post-checkpoint history also pass. Timing includes process start
and local subprocess polling; it is a VM measurement, not server timing.

## Run and reproduce

```sh
MAKEFUN_INPUT_DIR=/path/to/kit/input MAKEFUN_OUTPUT_DIR=/path/to/output python3 main.py
python3 loo_check.py --input-dir /path/to/kit/input --output /path/to/loo-results.json
python3 verify.py --input-dir /path/to/kit/input
```

The entry reads every `*.in` in name order and writes the matching `*.out`.
Only the input/output directory variables affect file locations. Each output
contains exactly 23 hourly rows with five finite, positive, ordered quantiles.
`loo_check.py` imports the actual entry model; `verify.py` checks isolated
practice runs, repeatability, timing, and unusual donor/history fallbacks.

MIT licensed. LICENSE and the freshness root were created by the kit's init.
Badge paths assume the GitHub owner/repository shown above; if published under
a different name, update both repository-specific badge URLs before entry.
