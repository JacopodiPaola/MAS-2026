"""Predeclared, shared comparisons for the two temporal formulations.

Primary practical decisions use matched-cohort ensemble statistics. Paired-seed
absolute changes remain visible without requiring chaotic trajectories to match.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd


CRITERIA_PATH = Path(__file__).parent / "data" / "predeclared_criteria.json"
METRICS = ["Polarization", "Rotation", "LargestGroupFraction", "ConnectedTimeFraction",
           "MeanNND", "MeanDistanceToCentroid"]


def group_aggregate(summary):
    """Flat speed/dt table; raw individual cases are retained separately."""
    rows = []
    for (speed, dt), group in summary.groupby(["Speed", "dt"], sort=True):
        row = {"Speed": speed, "dt": dt, "Seeds": group.Seed.nunique()}
        row.update({name: float(group[name].mean()) for name in METRICS})
        row.update({
            "MissedRepulsionPassesPerSecond": float(group.MissedRepulsionPassesPerSecond.mean()),
            "TotalMissedRepulsionPasses": int(group.MissedRepulsionPasses.sum()),
            "ExactOverlapPairs": int(group.ExactOverlapPairs.sum()),
            "MinimumRecordedPairDistance": float(group.MinimumRecordedPairDistance.min()),
            "MinimumMissedSeparation": float(group.MinimumMissedSeparation.min()),
            "AssemblySuccessRate": float(group.AssemblySuccess.mean()),
            "MeanAssemblyTime": float(group.AssemblyTime.mean()),
            "PostAssemblyBreakupRuns": int(group.PostAssemblyBreakup.sum()),
        })
        rows.append(row)
    return pd.DataFrame(rows)


def compare_adjacent(summary, dts):
    """Return one decision row per speed/pair, and raw metric comparisons."""
    criteria = json.loads(CRITERIA_PATH.read_text())
    dts = sorted(set(dts), reverse=True)
    decisions, metric_rows = [], []
    assert not summary.duplicated(["Seed", "Speed", "dt"]).any()
    for speed in sorted(summary.Speed.unique()):
        for candidate, finer in zip(dts[:-1], dts[1:]):
            coarse = summary.loc[(summary.Speed == speed) & (summary.dt == candidate)].set_index("Seed").sort_index()
            fine = summary.loc[(summary.Speed == speed) & (summary.dt == finer)].set_index("Seed").sort_index()
            assert len(coarse) and coarse.index.equals(fine.index)
            failed = []
            for name in METRICS:
                reference = float(fine[name].mean())
                observed = float(coarse[name].mean())
                change = abs(observed - reference)
                paired = float((coarse[name] - fine[name]).abs().mean())
                near_zero = abs(reference) <= criteria["NearZeroReference"]
                relative = change / abs(reference) if not near_zero else np.nan
                paired_relative = paired / abs(reference) if not near_zero else np.nan
                rule = criteria["MetricRules"][name]
                kind = rule["kind"]
                tolerance = rule["tolerance"]
                if kind == "relative" and near_zero:
                    kind = "absolute near-zero fallback"
                    tolerance = criteria["NearZeroAbsoluteTolerance_BL"]
                tested = relative if kind == "relative" else change
                passed = bool(np.isfinite(tested) and tested <= tolerance + 1e-12)
                if not passed:
                    failed.append(name)
                metric_rows.append({
                    "Speed": speed, "CandidateDt": candidate, "FinerDt": finer,
                    "Metric": name, "Seeds": len(coarse),
                    "CandidateMean": observed, "FinerMean": reference,
                    "AbsoluteChange": change, "RelativeChange": relative,
                    "PairedMeanAbsoluteChange": paired,
                    "PairedRelativeChange": paired_relative,
                    "ToleranceKind": kind, "Tolerance": tolerance,
                    "MetricPass": passed,
                })
            coarse_rate = float(coarse.MissedRepulsionPassesPerSecond.mean())
            fine_rate = float(fine.MissedRepulsionPassesPerSecond.mean())
            crossing_pass = max(coarse_rate, fine_rate) <= criteria["MaximumMissedRepulsionPassesPerSecond"] + 1e-12
            no_overlap = int(coarse.ExactOverlapPairs.sum() + fine.ExactOverlapPairs.sum()) == 0
            decisions.append({
                "Speed": speed, "CandidateDt": candidate, "FinerDt": finer,
                "Seeds": len(coarse), "MetricsPass": not failed,
                "FailedMetrics": ", ".join(failed),
                "CandidateMissedPassRate": coarse_rate, "FinerMissedPassRate": fine_rate,
                "CrossingRateNonIncreasing": bool(fine_rate <= coarse_rate + 1e-12),
                "CrossingRatePass": bool(crossing_pass), "ExactOverlapPass": no_overlap,
                "Pass": bool(not failed and crossing_pass and no_overlap),
            })
    return pd.DataFrame(decisions), pd.DataFrame(metric_rows)


def protocol_candidates(comparison, dts):
    """Coarsest first; require every finer available adjacent comparison too."""
    dts = sorted(set(dts), reverse=True)
    accepted = []
    speed_count = comparison.Speed.nunique()
    for index, candidate in enumerate(dts[:-1]):
        required = comparison.loc[comparison.CandidateDt.isin(dts[index:-1])]
        assert len(required) == speed_count * (len(dts) - index - 1)
        if required.Pass.all():
            accepted.append(float(candidate))
    return accepted
