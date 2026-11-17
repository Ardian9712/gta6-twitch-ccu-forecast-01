# Midnight Curve

Current local iteration: **v3, ridge + nested residual spread calibration**.
This supersedes the earlier retain-v2 decision after the coverage objective
was added. The model accepts a small loss increase versus v2 for coverage
near 90%, while remaining clearly better than v1. No practice outcomes were
used to fit the calibration.

| Model / calibration | Live LOO loss / coverage | Live time loss / coverage | Live franchise loss / coverage | Time + franchise |
| --- | --- | --- | --- | --- |
| v1 | .276065 / 88.08% | .284266 / 82.02% | .284825 / 87.92% | .292904 / 81.03% |
| v2 | .250224 / 88.41% | .257816 / 84.58% | .250783 / 88.57% | .258957 / 84.19% |
| v3 pooled multiplier | **.253552 / 90.34%** | **.262881 / 89.53%** | **.254066 / 90.34%** | **.265244 / 89.33%** |
| Hour multiplier, n/(n+10) shrinkage | .250482 / 90.66% | .260541 / 88.34% | .251344 / 90.50% | .262147 / 88.54% |
| Absolute residual-radius floor | .251569 / 91.95% | .258102 / 87.94% | .252286 / 91.95% | .259600 / 87.55% |

V3 loss increases versus v2 by .003328 LOO and .005064 chronological;
it improves versus v1 by .022514 and .021386 (8.16% and 7.52%). Coverage
increases by 1.93 and 4.94 percentage points versus v2. This is calibration
progress under the revised two-axis rule, not a claim of better pinball loss
than v2. Pooled calibration is chosen because it is simple and reaches
89.3–90.3% coverage across all four checks. It improves loss in only 7/27
LOO and 7/22 time launches; it does not satisfy the older loss-only gate.

Calibration uses inner held-out donor errors |log(actual/predicted median)|
divided by the inner forecast's original hour-specific spread. Pool over
hours/launches; multiplier = max(1, Q90(standardized errors)/1.645). Every
outer fold recomputes this from its training donors. Inner chronological
folds use strictly earlier launches; franchise folds remove siblings. With
fewer than five inner donors, skip that inner target; with no residuals,
preserve v2. The same live donor pool supplies calibration for trickle targets;
these are stress diagnostics, not independently trained trickle models.

| Calibration | Trickle LOO/franchise loss / coverage | Trickle time loss / coverage |
| --- | --- | --- |
| v2 | 1.890186 / 27.83% | 2.152311 / 22.61% |
| Pooled | 1.869790 / 31.30% | 2.076138 / 32.17% |
| Hour | 1.884827 / 30.00% | 2.087907 / 29.57% |
| Absolute | 1.882550 / 31.30% | 2.140266 / 26.09% |

Pooled live loss improves only 2/23 LOO hours and 4/23 time hours. Its
quantile losses (.05/.25/.50/.75/.95) are
.107046/.292314/.378069/.338628/.151700 in LOO and
.106469/.299020/.391513/.351570/.165831 chronologically. The median
is unchanged. Coverage still varies by hour: chronological hours 16–18
cover only 77.27%, despite aggregate coverage 89.53%; this is not a claim
of perfect conditional calibration.

Final v3 practice execution: Python 3.12.3, two fresh runs each, all shapes,
bounds and byte determinism pass. Batch matches isolated; edge checks pass.
Slower timings: p00 .215 s, p01 .232 s, p02 .265 s, p03 .215 s; sizes
2546/2521/2548/2535 bytes. Python 3.13 is unavailable locally. Practice is a
known external check and no answer data is present for residual diagnostics.
The final nested evaluator below includes all calibration candidates; the
original loo_check.py does not enforce chronology inside calibration and
must not be used to label its chronological result as strict nested CV.

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

Each hour fits a weighted ridge regression of donor log(viewers / hour-1)
on log(donor hour-1 / target hour-1). The intercept predicts the target's
log ratio. The slope penalty is 0.5 times the sum of weights, shrinking toward
unit elasticity in log viewers. When target history exists, donor weights
combine Gaussian similarity in log hour-1 scale
(bandwidth 2) and the previous day's normalized hourly shape (bandwidth 1.5).
Clip shape log-ratios to ±4 and mix the kernel half-and-half with equal weights
to retain broad donor support. History never includes observations after the
checkpoint. Without history the regression uses equal donor weights.

Spread is weighted IQR / 1.349, floored at both 0.02 and the unweighted IQR
spread. This preserves the prototype's uncertainty calibration. Quantiles are
`p1 * exp(predicted_log_ratio + z * spread)`, with z = −1.645, −0.674, 0,
0.674, 1.645. Clamp to [1e-9, 1e9] and enforce non-decreasing order.
There is no network, randomness, clock dependence, or fitted external state.

## Local measurements

Comparable-only leave-one-out replay, scored with the rules' exact doubled
log-pinball loss. Each target's release-day future is removed from its input;
only its history through hour 1 is exposed. This iteration compared a fixed
ridge regression, median/regression ensembles, donor cross-fitted hour bias,
and a per-hour residual spread floor. Candidate selection used both evaluations;
these are development scores rather than an untouched test set.

| Evaluation | Cases | Model loss | House loss | Model 90% coverage | House coverage | Model typical miss | House typical miss | Wins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v1: Big-regime LOO | 27 | 0.276065 | 0.321418 | 88.08% | 79.23% | 54.22% | 62.97% | 22/27 |
| v2: Big-regime LOO | 27 | 0.250224 | 0.321418 | 88.41% | 79.23% | 45.95% | 62.97% | 23/27 |
| v1: Earlier-launch donors only | 22 | 0.284266 | 0.318952 | 82.02% | 79.84% | 55.38% | 62.59% | 17/22 |
| v2: Earlier-launch donors only | 22 | 0.257816 | 0.318952 | 84.58% | 79.84% | 47.92% | 62.59% | 17/22 |

Typical miss above uses the official pooled formula: 100 × (exp(mean absolute
log median error) − 1). For comparison with the original fit-test's arithmetic
mean of per-case miss percentages, v2 LOO is 52.88% vs 71.39%, and chronological
evaluation is 55.13% vs 71.91%. Loss improves over v1 by 9.36% and 9.30%,
respectively. Chronological
evaluation requires at least five strictly earlier big donors. It is a useful
robustness check, but these comparables remain development evidence.

Candidate ablations (exact same `loo_check.py` evaluator; bias and residual
floors learned from inner donor LOO, excluding the outer target):

| Candidate | Big-regime loss | Time-ordered loss | Decision |
| --- | ---: | ---: | --- |
| v1 median | 0.276065 | 0.284266 | Reference |
| 25% regression + 75% median | 0.266382 | 0.274720 | Improves v1; weaker than regression |
| Equal regression/median ensemble | 0.258708 | 0.267107 | Improves v1; weaker than regression |
| 75% regression + 25% median | 0.253188 | 0.261465 | Improves v1; weaker than regression |
| Regression alone | **0.250224** | **0.257816** | Retained |
| v1 + hour bias | 0.273928 | 0.285606 | Reject: worsens v1's time-ordered score |
| v1 + residual spread floor | 0.275989 | 0.281335 | Improves v1; weaker than regression |
| Regression + hour bias | 0.248828 | 0.260649 | Reject: worsens regression's time-ordered score |
| Regression + residual spread floor | 0.250260 | 0.257247 | Reject: worsens regression's big-regime score |
| Regression + bias + spread floor | 0.248888 | 0.259762 | Reject: worsens regression's time-ordered score |

The spread candidate floors each hour's original IQR spread at the 90th
percentile of absolute inner-LOO residuals divided by 1.645. Bias is the
per-hour median inner-LOO residual, shrunk by n/(n+10). Neither addition
improves regression on both evaluations. Retained coverage is closer to 90%
than v1, but the chronological 84.58% still indicates undercoverage.

Practice cases p00–p03 contain no answers, so local practice validation checks
execution and output validity rather than forecast accuracy. An official
practice grade requires server submission. The final is one unseen launch;
these measurements do not establish its score or performance against the
house AI model.

Verified in this iteration with Python 3.12.3, two fresh processes per practice
case (Python 3.13 is not installed in this session):

| Case | Output bytes | Slower execution | Shape | Repeated bytes |
| --- | ---: | ---: | --- | --- |
| p00 | 2,544 | 0.171 s | valid | identical |
| p01 | 2,523 | 0.300 s | valid | identical |
| p02 | 2,538 | 0.165 s | valid | identical |
| p03 | 2,534 | 0.175 s | valid | identical |

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

## Final nested evaluation: retain v2

The following table supersedes the preliminary tables below. All candidates
use identical outer LOO/time/franchise folds (27/22/27 live launches, 10
trickle launches). Every outer fold makes internal validation predictions
before scoring its target. A/B/F weights are chosen on a quarter-step simplex
grid shared across hours, using exact live-regime log-pinball; prior blends
use 70% declared prior + 30% inner fitted weights. Equal-weight controls stay
equal. Inner folds obey the outer protocol's chronology/franchise exclusions.
Data-derived spreads, regime quantiles and predictions are always fold-local.
No bias or quantile calibration is fitted in these evaluable candidates.
No held-out future is used to estimate unlock time; alignment is dropped.

Each cell is loss / 90% coverage %. AB means A ridge + B median; AF/AE adds
flat persistence to A. Named prior weights refer to the 70% prior portion,
not a claim of fixed final weights. Full per-case/hour/quantile results are
emitted by the nested executable evaluation at the end of this README.

| Candidate | Live LOO | Live time | Live franchise | Live cases improved, LOO/time/franchise |
| --- | --- | --- | --- | --- |
| A v2 | .250224 / 88.41 | .257816 / 84.58 | .250783 / 88.57 | Reference |
| B median | .276065 / 88.08 | .284266 / 82.02 | .284825 / 87.92 | 7/7/7 |
| E/F persistence | .321681 / 80.35 | .325826 / 73.72 | .320756 / 81.80 | 4/5/4 |
| AB80 log | .251645 / 88.73 | .259617 / 84.19 | .252928 / 88.73 | 12/11/10 |
| AB80 mixture | .251699 / 88.73 | .259208 / 85.57 | .253024 / 88.73 | 12/11/10 |
| AB65 log | .253111 / 88.57 | .261512 / 84.19 | .255016 / 88.57 | 12/10/10 |
| AB65 mixture | .253160 / 88.89 | .261088 / 85.57 | .255129 / 89.05 | 12/9/10 |
| AF95 log | .250272 / 88.41 | .257571 / 84.39 | .250785 / 88.73 | 14/12/14 |
| AF95 mixture | .250195 / 88.73 | .256890 / 85.38 | .250709 / 89.21 | 13/12/14 |
| AE85 log | .250878 / 88.73 | .258218 / 83.99 | .251318 / 89.05 | 13/10/13 |
| AE85 mixture | .250659 / 89.53 | .256910 / 86.17 | .251094 / 89.69 | 13/12/13 |
| Available Copilot prior, log | .257406 / 88.57 | .265439 / 83.79 | .259504 / 88.57 | 12/10/10 |
| Available Copilot prior, mixture | .256849 / 89.86 | .263867 / 86.17 | .259090 / 89.86 | 11/10/10 |
| Logistic level gate | .262027 / 90.82 | .264633 / 86.36 | .262873 / 90.82 | 7/6/7 |
| Hope quantile gate ablation | .296555 / 92.43 | .462462 / 83.99 | .296670 / 92.43 | 5/3/6 |
| Capped empirical analogues | .278947 / 86.31 | .280327 / 82.02 | .284498 / 86.31 | 6/5/6 |
| A + empirical 80/20 mixture | .252303 / 88.24 | .260108 / 84.19 | .253347 / 88.41 | 9/8/9 |
| Equal AB log | .258708 / 88.41 | .267107 / 84.39 | .262363 / 88.57 | 12/9/10 |
| Equal AB mixture | .258442 / 88.41 | .266752 / 84.98 | .262211 / 88.73 | 11/9/10 |
| Equal ABF log | .268567 / 87.60 | .273176 / 81.82 | .270699 / 87.76 | 10/10/10 |
| Equal ABF mixture | .267515 / 89.21 | .270446 / 85.97 | .269755 / 89.37 | 11/9/10 |
| Inner-selected best single | .250224 / 88.41 | .257816 / 84.58 | .250783 / 88.57 | Identical to A |
| Inner-fitted log ensemble | .250224 / 88.41 | .259125 / 83.79 | .250783 / 88.57 | 0/7/0 |

| Candidate | Trickle LOO/franchise | Trickle time |
| --- | --- | --- |
| A v2 / inner-selected single | 1.890186 / 27.83 | 2.152311 / 22.61 |
| B median | 2.448133 / 22.61 | 2.564370 / 20.43 |
| E/F persistence | 2.576722 / 19.13 | 2.614592 / 20.87 |
| AB80 log | 1.964219 / 26.09 | 2.234260 / 22.17 |
| AB80 mixture | 1.930607 / 26.96 | 2.187949 / 23.04 |
| AB65 log | 2.020737 / 25.22 | 2.276478 / 21.30 |
| AB65 mixture | 1.967074 / 26.52 | 2.216617 / 23.04 |
| AF95 log | 1.912613 / 27.39 | 2.194309 / 21.74 |
| AF95 mixture | 1.899785 / 27.39 | 2.165303 / 23.04 |
| AE85 log | 1.957943 / 26.09 | 2.224828 / 22.61 |
| AE85 mixture | 1.922215 / 28.26 | 2.177611 / 24.35 |
| Available Copilot prior, log | 2.142563 / 23.48 | 2.360169 / 21.74 |
| Available Copilot prior, mixture | 2.053296 / 26.09 | 2.278225 / 23.48 |
| Logistic level gate | .834518 / 77.39 | 1.095238 / 57.39 |
| Hope quantile gate ablation | .825299 / 77.83 | 1.103426 / 56.96 |
| Capped empirical analogues | 2.393368 / 25.22 | 2.477009 / 23.48 |
| A + empirical 80/20 | 1.940957 / 28.26 | 2.186176 / 23.04 |
| Equal AB log | 2.161459 / 23.04 | 2.353266 / 21.74 |
| Equal AB mixture | 2.080083 / 25.22 | 2.283072 / 23.48 |
| Equal ABF log | 2.296158 / 22.61 | 2.436011 / 21.30 |
| Equal ABF mixture | 2.193655 / 26.09 | 2.347644 / 24.78 |
| Inner-fitted log ensemble | 1.890186 / 27.83 | 2.242954 / 22.61 |

Decision: retain A. The AF95 mixture's LOO gain is only .000029 and it wins
13/27 launches, 12/23 hours and 2/5 quantiles. Time improves .000927, with
12/22 launch wins, 15/23 hours and 4/5 quantiles. Franchise improves .000074,
with 14/27 launch wins, 13/23 hours and 2/5 quantiles. Trickle loss worsens.
This is a thin, inconsistent advantage, so the predeclared simpler-model
rule rejects the ensemble. No tested model establishes loss below .20.
Combined chronological+franchise A remains .258957 / 84.19%; nested AF95
mixture is .258244 / 84.98%, with 12/22 wins, 13/23 hours and 3/5 quantiles.

V2 is clearly better than v1 on live donor evaluation, including franchise
holdout (.250783 vs .284825), but is not robust on trickle launches. Recommend
the existing v2 for the parent's live-regime submit gate; no new v3 submission.
Practice is a KNOWN external check, not a clean holdout. Its missing answers
prevent local residual diagnostics. Main.py remains unchanged at d862b8d;
this README records experiments without a no-op model commit.

### Superseded preliminary evaluation

No tested candidate clearly beats v2 on both required live-regime evaluations.
Each cell below is loss / 90% coverage percent, recomputed under the stricter
fold protocol including franchise holdout. Full per-case, per-hour and
per-quantile metrics for every candidate are emitted by the executable
evaluation below. Fixed 80/20 and 65/35 are explicit comparison priors;
65/35 uses 35% median.
These are fixed comparison priors, not weights estimated on the full dataset.

| Candidate | Live LOO (27) | Live time (22) | Live franchise (27) |
| --- | --- | --- | --- |
| A v2 | **0.250224 / 88.41** | **0.257816 / 84.58** | **0.250783 / 88.57** |
| B median | 0.276065 / 88.08 | 0.284266 / 82.02 | 0.284825 / 87.92 |
| E/F persistence | 0.321681 / 80.35 | 0.325826 / 73.72 | 0.320756 / 81.80 |
| AB80 log | 0.252445 / 88.57 | 0.260607 / 84.58 | 0.254071 / 88.57 |
| AB80 mixture | 0.252498 / 88.73 | 0.260512 / 84.98 | 0.254175 / 88.73 |
| AB65 log | 0.255030 / 88.57 | 0.263465 / 84.19 | 0.257607 / 88.89 |
| AB65 mixture | 0.254979 / 88.89 | 0.263227 / 84.98 | 0.257667 / 89.05 |
| AF95 log | 0.250334 / 88.57 | 0.257592 / 85.18 | 0.250837 / 88.73 |
| AF95 mixture | 0.250235 / 88.89 | 0.257084 / 85.77 | 0.250738 / 89.37 |
| AE85 log | 0.251669 / 88.57 | 0.258212 / 83.99 | 0.252047 / 89.21 |
| AE85 mixture | 0.251392 / 89.86 | 0.256900 / 86.76 | 0.251766 / 90.02 |
| Copilot log | 0.263585 / 88.24 | 0.269459 / 83.40 | 0.266614 / 88.57 |
| Copilot mixture | 0.262881 / 89.53 | 0.267711 / 85.77 | 0.265934 / 89.53 |
| Level gate | 0.262027 / 90.82 | 0.264633 / 86.36 | 0.262873 / 90.82 |
| Hope quantile gate (available evidence) | 0.296555 / 92.43 | 0.462462 / 83.99 | 0.296670 / 92.43 |
| Capped empirical analogues | 0.278947 / 86.31 | 0.280327 / 82.02 | 0.284498 / 86.31 |
| A + empirical 80/20 mixture | 0.252303 / 88.24 | 0.260108 / 84.19 | 0.253347 / 88.41 |

| Candidate | Trickle LOO/franchise (10) | Trickle time (10) |
| --- | --- | --- |
| A v2 | 1.890186 / 27.83 | 2.152311 / 22.61 |
| B median | 2.448133 / 22.61 | 2.564370 / 20.43 |
| E/F persistence | 2.576722 / 19.13 | 2.614592 / 20.87 |
| AB80 log | 1.996416 / 25.22 | 2.231191 / 22.17 |
| AB80 mixture | 1.950598 / 26.52 | 2.190283 / 22.61 |
| AB65 log | 2.078277 / 23.48 | 2.291971 / 21.30 |
| AB65 mixture | 2.009177 / 26.52 | 2.231737 / 23.48 |
| AF95 log | 1.922285 / 26.96 | 2.173679 / 22.17 |
| AF95 mixture | 1.904393 / 27.83 | 2.158654 / 23.04 |
| AE85 log | 1.987356 / 25.65 | 2.217472 / 21.74 |
| AE85 mixture | 1.937440 / 28.70 | 2.175064 / 24.35 |
| Copilot log | 2.254279 / 23.04 | 2.412247 / 21.30 |
| Copilot mixture | 2.158621 / 25.65 | 2.329736 / 24.78 |
| Level gate | 0.834518 / 77.39 | 1.095238 / 57.39 |
| Hope quantile gate (available evidence) | 0.825299 / 77.83 | 1.103426 / 56.96 |
| Capped empirical analogues | 2.393368 / 25.22 | 2.477009 / 23.48 |
| A + empirical 80/20 mixture | 1.940957 / 28.26 | 2.186176 / 23.04 |

Hope gate isolates its Q20/Q80 rule on the same branches as the logistic
gate; locked-at-checkpoint override and full log1p modeling are untested.
Empirical analogues use existing similarity features; the 0.15 cap is
infeasible below seven donors, so those sparse folds retain A.

Additional chronological + franchise holdout (22 live cases), loss / coverage:

| Candidate | Time + franchise |
| --- | --- |
| A v2 | 0.258957 / 84.19 |
| B median | 0.292904 / 81.03 |
| E/F persistence | 0.324466 / 74.31 |
| AB80 log / mixture | 0.262994 / 83.99; 0.262882 / 84.39 |
| AB65 log / mixture | 0.266826 / 84.19; 0.266599 / 84.78 |
| AF95 log / mixture | 0.258631 / 84.78; 0.258093 / 85.18 |
| AE85 log / mixture | 0.259097 / 83.60; 0.257771 / 86.17 |
| Copilot log / mixture | 0.272811 / 83.00; 0.270962 / 85.57 |
| Level gate | 0.265794 / 86.56 |
| Hope quantile gate | 0.463677 / 83.79 |
| Capped empirical analogues | 0.284183 / 82.02 |
| A + empirical 80/20 | 0.261764 / 84.19 |

Per-hour consistency: live hours (out of 23) with lower loss than A:

| Candidate | LOO / time / franchise |
| --- | --- |
| B median | 3 / 0 / 3 |
| E/F persistence | 0 / 2 / 0 |
| AB80 log / mixture | 4 / 3 / 4; 5 / 3 / 4 |
| AB65 log / mixture | 4 / 1 / 4; 4 / 2 / 4 |
| AF95 log / mixture | 10 / 13 / 13; 12 / 13 / 13 |
| AE85 log / mixture | 7 / 13 / 8; 9 / 12 / 11 |
| Copilot log / mixture | 3 / 5 / 3; 3 / 7 / 3 |
| Level gate | 7 / 12 / 7 |
| Hope quantile gate | 2 / 3 / 2 |
| Capped empirical analogues | 3 / 0 / 3 |
| A + empirical 80/20 | 6 / 5 / 6 |

V2 live per-quantile losses, .05/.25/.50/.75/.95 order:
LOO .102449/.292440/.378069/.332099/.146064;
time .093012/.290511/.391513/.347668/.166377;
franchise .102680/.293634/.380436/.331044/.146122.
Live hourly loss ranges: .105090–.303646 (LOO), .094613–.335307 (time),
.107664–.306499 (franchise). Early LOO coverage is weakest at hour 3
(70.37%); time coverage at hours 8 and 16–18 is 72.73%. The executable
evaluation emits every hour's loss/coverage and every case/quantile loss.

Final verification after all four designs: Python 3.12.3, all practice cases
valid and byte-identical over two fresh processes, batch matches isolated,
edge checks pass. Slower runs: p00 .115 s, p01 .115 s, p02 .116 s, p03 .118 s.
Main.py remains byte-for-byte committed v2; only evaluation documentation
is modified. No v3 commit, push or submission was made.

Hope's momentum needs a specified robust slope and eta/tau/c grid; minute
slopes cannot be reconstructed from hourly donors. Its bias formula needs
kappa, n_eff and valid release-relative phases. It also adds the median
residual in both b_h and Q50(e_h); whether residuals should first be centered
requires clarification. Complete Grokbot/Copilot/ChatGPT/Hope blends remain
untested because of stopped template, feature, alignment and momentum members.
Both self-donor alternatives remain untested pending pseudo-day/extrapolation
and context-to-gate definitions. No scores are invented for these components.
No coarse-grid parameter fitting was performed: parameter grids and several
constituent estimators were unspecified.

The closest AF95 mixture wins 13/27 live LOO cases, 12/22 time cases, and
13/27 franchise cases; only 12/23, 13/23, and 13/23 hours improve, with only
2/5, 3/5, and 2/5 quantile levels improving. Its LOO loss is slightly worse,
so it fails both the loss rule and the consistency requirement. Level gating
improves 8/10 trickle cases but only 7/27 live LOO cases. V2 is a live-launch
model: the poor trickle diagnostics are real, not a claim of general robustness.

Stopped components requiring clarification: C needs a class count, grouping,
normalization and matching algorithm; D needs exact feature definitions,
missingness, ridge penalty and smoothing; alignment needs an onset estimator,
uncertainty law and interpolation/extrapolation rules. Tau stability cannot
be measured without that estimator; alignment is dropped. Hierarchical bias
and quantile calibration need phase boundaries, support thresholds and pooling
weights. Self-donor construction needs a specified pseudo-day or extrapolation
rule for sparse non-launch history. Its use as weak context needs a specified
context-to-gate mapping. No arbitrary versions of these were tested.

Donors lack minute traces, streams and category snapshots, preventing honest
CV of the proposed minute/stream gate and stream-mix distance. Practice
answers are absent, so the requested practice log residuals cannot be reported.
No coefficients translating stream concentration into viewers were learned.
All four practice cases are live by the reporting threshold.

### Reproducible evaluation protocol

The following reproducible development evaluation uses 38 kit comparables:
37 complete launches and one sparse, non-launch GTA VI history excluded from
launch training. Every fold selects and fits donors anew. Fixed candidate
weights are declared design priors, never full-data fitted quantities; no
learned quantities cross folds. The chronological check preserves the existing
minimum of five earlier big donors. Franchise holdout removes siblings in
Call of Duty, Elden Ring, Forza Horizon, and Ghost of Tsushima/Yōtei. Other
represented franchises have only one eligible launch. Regime membership for
reporting uses the original 20,000-viewer definition.

All Gaussian components use A's conservative fold-local IQR spread to isolate
location and mixture changes. E/F tests the specified flat persistence option;
it does not claim to implement an unspecified decay law. B tests the existing
median's available inputs; the proposed stream-mix refinement lacks matching
donor observations. Copilot's available A/B/E weights are renormalized after
omitting the unspecified template component. No fitted ensemble weights are
used. Mixture quantiles invert the log-normal mixture CDF; log blends average
central log predictions, never component quantiles.

```python
# BEGIN MERGED EVALUATION
import json
import math
from pathlib import Path
import main
import loo_check

sample = json.loads(Path('/home/hatch/workspace/makefun/gta6-kit/gta6-twitch-ccu-forecast-01-kit/input/p00.in').read_text())
donors = main.launch_donors(sample['comparables'])
levels = (.05, .25, .5, .75, .95)
specs = [
    ('A v2', 'log', (1, 0, 0)),
    ('B median', 'log', (0, 1, 0)),
    ('E/F persistence', 'log', (0, 0, 1)),
    ('AB80 log', 'log', (.8, .2, 0)),
    ('AB80 mixture', 'mix', (.8, .2, 0)),
    ('AB65 log', 'log', (.65, .35, 0)),
    ('AB65 mixture', 'mix', (.65, .35, 0)),
    ('AF95 log', 'log', (.95, 0, .05)),
    ('AF95 mixture', 'mix', (.95, 0, .05)),
    ('AE85 log', 'log', (.85, 0, .15)),
    ('AE85 mixture', 'mix', (.85, 0, .15)),
    ('Copilot log', 'log', (.30/.80, .35/.80, .15/.80)),
    ('Copilot mixture', 'mix', (.30/.80, .35/.80, .15/.80)),
    ('Level gate', 'gate', (1, 0, 0)),
    ('Hope quantile gate', 'hope_gate', (1, 0, 0)),
    ('Hope empirical', 'empirical', (0, 1, 0)),
    ('A+empirical 80/20', 'empirical_mix', (.8, .2, 0)),
    ('Equal AB log', 'log', (.5, .5, 0)),
    ('Equal AB mixture', 'mix', (.5, .5, 0)),
    ('Equal ABF log', 'log', (1/3, 1/3, 1/3)),
    ('Equal ABF mixture', 'mix', (1/3, 1/3, 1/3)),
    ('Nested best single', 'selected', (1, 0, 0)),
    ('Nested fitted log', 'fitted', (1, 0, 0)),
    ('Calibration pooled', 'cal_pooled', (1, 0, 0)),
    ('Calibration hour', 'cal_hour', (1, 0, 0)),
    ('Calibration absolute', 'cal_absolute', (1, 0, 0)),
]

def franchise(name):
    text = name.lower()
    for prefix in ('call of duty:', 'elden ring', 'forza horizon', 'ghost of '):
        if text.startswith(prefix):
            return prefix
    return text

def mixture_quantile(components, probability):
    low = min(location - 12*scale for weight, location, scale in components)
    high = max(location + 12*scale for weight, location, scale in components)
    for _ in range(55):
        middle = (low + high)/2
        cdf = math.fsum(weight*.5*(1 + math.erf((middle-location)/(scale*math.sqrt(2))))
                        for weight, location, scale in components)
        if cdf < probability:
            low = middle
        else:
            high = middle
    return (low + high)/2

inner_cache = {}

def inner_weights(training, protocol):
    """Select shared weights from internal predictions only, on a coarse grid.

    Objective is exact pinball for log-center ensembles with A's IQR spread.
    Distribution mixtures use these locked weights as a separate outer test.
    Only live inner targets select the live-launch ensemble, never trickle.
    """
    key = (protocol, tuple(source['name'] for source, _ in training))
    if key in inner_cache:
        return inner_cache[key]
    grid = [(a/4, b/4, (4-a-b)/4) for a in range(5) for b in range(5-a)]
    losses = {weight: [] for weight in grid}
    for target, actual in training:
        if actual[0] < 20000:
            continue
        available = [(source, values) for source, values in training
                     if source is not target
                     and ('time' not in protocol or main.instant(source['day_start']) < main.instant(target['day_start']))
                     and ('franchise' not in protocol or franchise(source['name']) != franchise(target['name']))]
        if sum(values[0] >= 20000 for _, values in available) < 5:
            continue
        pool = main.regime_pool(available)
        history = {hour: value for hour, value in actual.items() if hour <= 0}
        prediction = main.curve(pool, history, actual[0])
        similarity = main.similarity_weights(pool, history, actual[0])
        for offset, (center, spread) in enumerate(prediction):
            median = main.weighted_percentile([math.log(values[offset+1]/values[0]) for _, values in pool], similarity, .5)
            truth = math.log(actual[offset+1]/actual[0])
            for weight in grid:
                location = weight[0]*center + weight[1]*median
                losses[weight].extend(2*max(p*(truth-location-z*spread), (p-1)*(truth-location-z*spread))
                                      for p, z in zip(levels, main.NORMAL_SCORES))
    def objective(weight):
        values = losses[weight]
        return math.fsum(values)/len(values) if values else float('inf')
    # Ties prefer A; no inner support falls back to A without outer tuning.
    best = min(grid, key=lambda weight: (objective(weight), -weight[0], -weight[1]))
    singles = [(1., 0., 0.), (0., 1., 0.), (0., 0., 1.)]
    single = min(singles, key=lambda weight: (objective(weight), -weight[0]))
    inner_cache[key] = best, single
    return best, single

for protocol in ('loo', 'time', 'franchise', 'time_franchise'):
    records = {name: {True: [], False: []} for name, _, _ in specs}
    for target, actual in sorted(donors, key=lambda item: item[0]['name']):
        available = [(source, values) for source, values in donors
                     if source is not target
                     and ('time' not in protocol or main.instant(source['day_start']) < main.instant(target['day_start']))
                     and ('franchise' not in protocol or franchise(source['name']) != franchise(target['name']))]
        if 'time' in protocol and sum(values[0] >= 20000 for _, values in available) < 5:
            continue
        pool = main.regime_pool(available)
        first = actual[0]
        logfirst = math.log(first)
        history = {hour: value for hour, value in actual.items() if hour <= 0}
        ridge = main.curve(pool, history, first)
        weights = main.similarity_weights(pool, history, first)
        medians = [main.weighted_percentile([math.log(values[hour]/values[0]) for _, values in pool], weights, .5)
                   for hour in range(1, 24)]
        small = [values for _, values in available if values[0] < 20000]
        live = first >= 20000
        fitted, selected_single = inner_weights(available, protocol)
        for name, mode, blend in specs:
            active_ridge = ridge
            if mode.startswith('cal_'):
                active_ridge = main.calibrate_curve(pool, ridge, mode[4:], 'time' in protocol,
                                                   franchise if 'franchise' in protocol else None)
                mode = 'log'
            if mode == 'selected':
                blend, mode = selected_single, 'log'
            elif mode == 'fitted':
                blend, mode = fitted, 'log'
            elif name.startswith(('AB80', 'AB65', 'AF95', 'AE85', 'Copilot')):
                blend = tuple(.7*prior+.3*fit for prior, fit in zip(blend, fitted))
            rows = []
            loss_matrix = []
            coverage = []
            for offset, (center, spread) in enumerate(active_ridge):
                locations = (logfirst+center, logfirst+medians[offset], logfirst)
                if mode == 'log':
                    location = math.fsum(weight*value for weight, value in zip(blend, locations))
                    logs = [location + z*spread for z in main.NORMAL_SCORES]
                else:
                    components = [(weight, location, spread) for weight, location in zip(blend, locations) if weight]
                    if mode in ('empirical', 'empirical_mix'):
                        components = [(1.0, locations[0], spread)]
                    if mode in ('gate', 'hope_gate') and small:
                        live_probability = 1/(1 + math.exp(-(logfirst-math.log(20000))/.4))
                        if mode == 'hope_gate':
                            anchors = [math.log1p(values[0]) for _, values in available]
                            equal_anchors = [1.0]*len(anchors)
                            low = main.weighted_percentile(anchors, equal_anchors, .2)
                            high = main.weighted_percentile(anchors, equal_anchors, .8)
                            live_probability = max(0.0, min(1.0, (math.log1p(first)-low)/(high-low)))
                        absolute = [math.log(values[offset+1]) for values in small]
                        equal = [1.0]*len(small)
                        prior = main.weighted_percentile(absolute, equal, .5)
                        scale = max(.02, (main.weighted_percentile(absolute, equal, .75)-main.weighted_percentile(absolute, equal, .25))/1.349)
                        components = [(live_probability, locations[0], spread), (1-live_probability, prior, scale)]
                    logs = [mixture_quantile(components, probability) for probability in levels]
                    if mode in ('empirical', 'empirical_mix'):
                        normalized = [weight/math.fsum(weights) for weight in weights]
                        # A 0.15 cap is feasible only with seven or more donors.
                        # Sparse folds fall back to the champion distribution.
                        if len(pool) >= 7:
                            # Redistribute excess proportionally among uncapped donors.
                            fixed = {}
                            while True:
                                free = [i for i in range(len(weights)) if i not in fixed]
                                remaining = 1-math.fsum(fixed.values())
                                total_free = math.fsum(weights[i] for i in free)
                                proposed = {i: remaining*weights[i]/total_free for i in free}
                                excess = [i for i in free if proposed[i] > .15]
                                if not excess:
                                    normalized = [fixed[i] if i in fixed else proposed[i] for i in range(len(weights))]
                                    break
                                fixed.update({i: .15 for i in excess})
                            points = [logfirst+math.log(values[offset+1]/values[0]) for _, values in pool]
                            empirical_share = 1.0 if mode == 'empirical' else .2
                            logs = []
                            for probability in levels:
                                low = min(min(points), locations[0]-12*spread)
                                high = max(max(points), locations[0]+12*spread)
                                for _ in range(55):
                                    middle = (low+high)/2
                                    empirical_cdf = math.fsum(weight for point, weight in zip(points, normalized) if point <= middle)
                                    normal_cdf = .5*(1+math.erf((middle-locations[0])/(spread*math.sqrt(2))))
                                    cdf = empirical_share*empirical_cdf+(1-empirical_share)*normal_cdf
                                    if cdf < probability:
                                        low = middle
                                    else:
                                        high = middle
                                logs.append((low+high)/2)
                estimates = [math.exp(max(math.log(1e-9), min(math.log(1e9), value))) for value in logs]
                rows.append({'hour': offset+2, 'q': estimates})
                residuals = [math.log(actual[offset+1]/estimate) for estimate in estimates]
                loss_matrix.append([2*max(probability*error, (probability-1)*error) for probability, error in zip(levels, residuals)])
                coverage.append(estimates[0] <= actual[offset+1] <= estimates[-1])
            measured = loo_check.measure({'hours': rows}, actual)
            records[name][live].append((target['name'], measured, loss_matrix, coverage))
    for live in (True, False):
        reference = records['A v2'][live]
        for name, _, _ in specs:
            data = records[name][live]
            count = len(data)
            hourly = [math.fsum(math.fsum(row[2][hour])/5 for row in data)/count for hour in range(23)]
            covered = [sum(row[3][hour] for row in data)/count for hour in range(23)]
            quantiles = [math.fsum(row[2][hour][quantile] for row in data for hour in range(23))/(count*23) for quantile in range(5)]
            ref_hourly = [math.fsum(math.fsum(row[2][hour])/5 for row in reference)/count for hour in range(23)]
            ref_quantiles = [math.fsum(row[2][hour][quantile] for row in reference for hour in range(23))/(count*23) for quantile in range(5)]
            summary = {
                'n': count,
                'loss': math.fsum(row[1]['loss'] for row in data)/count,
                'coverage': math.fsum(row[1]['coverage'] for row in data)/count,
                'wins_vs_A': sum(row[1]['loss'] < base[1]['loss']-1e-12 for row, base in zip(data, reference)),
                'hours_better': sum(a < b-1e-12 for a, b in zip(hourly, ref_hourly)),
                'quantiles_better': sum(a < b-1e-12 for a, b in zip(quantiles, ref_quantiles)),
                'hour_delta_range': [min(a-b for a, b in zip(hourly, ref_hourly)), max(a-b for a, b in zip(hourly, ref_hourly))],
            }
            print('SUMMARY', protocol, 'live' if live else 'trickle', name, json.dumps(summary), flush=True)
            print('DETAIL', protocol, 'live' if live else 'trickle', name, json.dumps({
                'hour_loss': [round(x, 6) for x in hourly],
                'hour_coverage': [round(x, 6) for x in covered],
                'quantile_loss': [round(x, 6) for x in quantiles],
                'case_loss': {row[0]: round(row[1]['loss'], 6) for row in data},
            }), flush=True)
# END MERGED EVALUATION
```
