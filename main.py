#!/usr/bin/env python3
"""Forecast release-day Twitch viewers using comparable launch shapes.

Hour 1 anchors the level; later hours use donor log(viewers / hour-1).
The big-launch regime starts at 20,000 hour-1 viewers. If fewer than five
donors qualify, relax to 10,000, then all complete launch curves. With no
history use equal weights. Otherwise use broad Gaussian similarity in log
hour-1 scale (bandwidth 2) and the preceding 24 hourly log ratios (bandwidth
1.5). A half-uniform mixture prevents a single neighbour dominating.
Weighted medians supply the curve. Spread is IQR / 1.349, at least 0.02
and at least the unweighted IQR calibration: similarity never narrows it.
Normal z scores (-1.645, -0.674, 0, 0.674, 1.645) produce five quantiles.
Only input data affect forecasts; environment variables select I/O paths.
"""

import json
import math
import os
from datetime import datetime
from pathlib import Path

NORMAL_SCORES = (-1.645, -0.674, 0.0, 0.674, 1.645)


def instant(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()


def hourly_values(rows, origin, stamp="from", cutoff=24):
    """Aggregate by relative hour, including minute-history fallbacks."""
    buckets = {}
    for row in rows or []:
        value = row.get("viewers")
        if value is None or not math.isfinite(float(value)):
            continue
        offset = math.floor((instant(row[stamp]) - origin) / 3600)
        if offset >= cutoff:
            continue
        buckets.setdefault(offset, []).append(max(1.0, float(value)))
    return {offset: math.fsum(values) / len(values)
            for offset, values in buckets.items()}


def launch_donors(comparables):
    donors = []
    for source in comparables:
        if "grand theft auto vi category before release" in source["name"].lower():
            continue
        values = hourly_values(source.get("hourly"), instant(source["day_start"]))
        if all(hour in values for hour in range(24)):
            donors.append((source, values))
    return donors


def regime_pool(donors):
    for threshold in (20000, 10000, 0):
        pool = [item for item in donors if item[1][0] >= threshold]
        if len(pool) >= 5 or threshold == 0:
            return pool


def weighted_percentile(values, weights, probability):
    """Interpolate weighted mid-ranks; equal weights give linear percentiles."""
    ordered = sorted(zip(values, weights))
    if len(ordered) == 1:
        return ordered[0][0]
    centers = []
    cumulative = 0.0
    for _, weight in ordered:
        centers.append(cumulative + weight / 2)
        cumulative += weight
    position = centers[0] + probability * (centers[-1] - centers[0])
    for index in range(1, len(ordered)):
        if position <= centers[index]:
            fraction = ((position - centers[index - 1]) /
                        (centers[index] - centers[index - 1]))
            return ordered[index - 1][0] + fraction * (
                ordered[index][0] - ordered[index - 1][0])
    return ordered[-1][0]


def similarity_weights(pool, history, first):
    if not history:
        return [1.0] * len(pool)
    weights = []
    for _, values in pool:
        scale_distance = math.log(values[0] / first) / 2.0
        overlaps = [hour for hour in range(-24, 0)
                    if hour in history and hour in values]
        shape_distance = 0.0
        if len(overlaps) >= 6:
            differences = []
            for offset in overlaps:
                target_shape = max(-4.0, min(4.0, math.log(history[offset] / first)))
                donor_shape = max(-4.0, min(4.0, math.log(values[offset] / values[0])))
                differences.append((target_shape - donor_shape) ** 2)
            shape_distance = math.fsum(differences) / len(differences) / 1.5 ** 2
        kernel = math.exp(-0.5 * (scale_distance ** 2 + shape_distance))
        weights.append(0.5 + 0.5 * kernel)
    return weights


def forecast(case):
    known = next(row for row in case["known"] if row["hour"] == 1)
    first = max(1.0, float(known["viewers"]))
    origin = instant(case["day_start"])
    history = hourly_values(case.get("history_hourly"), origin, cutoff=1)
    if not history:
        history = hourly_values(case.get("history"), origin, "at", cutoff=1)
    pool = regime_pool(launch_donors(case.get("comparables", [])))
    weights = similarity_weights(pool, history, first)
    rows = []
    for hour in range(2, 25):
        if pool:
            ratios = [math.log(values[hour - 1] / values[0]) for _, values in pool]
            center = weighted_percentile(ratios, weights, 0.5)
            equal = [1.0] * len(pool)
            spreads = [(weighted_percentile(ratios, w, 0.75) -
                        weighted_percentile(ratios, w, 0.25)) / 1.349
                       for w in (weights, equal)]
            spread = max(0.02, *spreads)
        else:
            center, spread = 0.0, 0.15 * math.sqrt(hour - 1)
        quantiles = []
        for z_score in NORMAL_SCORES:
            log_value = math.log(first) + center + z_score * spread
            value = math.exp(max(math.log(1e-9), min(math.log(1e9), log_value)))
            quantiles.append(max(quantiles[-1] if quantiles else 0.0,
                                 min(1e9, value)))
        rows.append({"hour": hour, "q": quantiles})
    return {"hours": rows}


def main():
    input_root = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_root = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_root.mkdir(parents=True, exist_ok=True)
    for source in sorted(input_root.glob("*.in")):
        result = forecast(json.loads(source.read_text(encoding="utf-8")))
        encoded = json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
        (output_root / (source.stem + ".out")).write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    main()
