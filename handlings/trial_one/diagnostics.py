"""Connectivity and motion diagnostics; no diagnostic enters a fish decision."""

import numpy as np
import pandas as pd
from checks.check_support import controlled_model, audit_run
from shiner_model import GoldenShinersModel


def _components(adjacency):
    unseen = set(range(len(adjacency)))
    groups = []
    while unseen:
        stack = [min(unseen)]
        unseen.remove(stack[0])
        group = []
        while stack:
            current = stack.pop()
            group.append(current)
            linked = set(np.flatnonzero(adjacency[current])) & unseen
            unseen.difference_update(linked)
            stack.extend(sorted(linked))
        groups.append(np.array(sorted(group), dtype=int))
    return sorted(groups, key=lambda group: (-len(group), int(group[0])))


def graph_components(positions, radius):
    """Undirected geometric components, with a link at distance <= radius."""
    positions = np.asarray(positions, dtype=float)
    distances = np.linalg.norm(positions[:, None] - positions[None, :], axis=2)
    return _components(distances <= radius)


def diagnostics_for(model):
    """Read completed records, including t=0, without modifying the model.

    MissedRepulsionPasses counts straight pair paths entering the repulsion
    range although both sampled endpoints were outside it. Reflected paths
    are excluded because a single straight segment would misrepresent them.
    This detects missed zone encounters, not physical body collisions.
    """
    if getattr(model, "record_every", 1) != 1:
        raise ValueError("Path diagnostics require every internal step; use handlings.trial_two.study_support for streamed diagnostics.")
    frame = model.datacollector.get_model_vars_dataframe().copy()
    fish = model.datacollector.get_agent_vars_dataframe().sort_index()
    n = len(model.agents)
    values = fish[["X", "Y", "DirX", "DirY", "Speed"]].to_numpy().reshape(len(frame), n, 5)
    positions = values[:, :, :2]
    headings = values[:, :, 2:4]
    speeds = values[:, :, 4]
    distances = np.linalg.norm(positions[:, :, None] - positions[:, None, :], axis=3)
    triangle = np.triu(np.ones((n, n), dtype=bool), 1)
    rows = []
    lower, upper = model.bounds[:, 0], model.bounds[:, 1]
    for step in range(len(frame)):
        components = _components(distances[step] <= model.attraction_radius)
        sizes = [len(group) for group in components]
        to_walls = np.minimum(positions[step] - lower, upper - positions[step]).min(axis=1)
        centroid = positions[step].mean(axis=0)
        centroid_wall = np.minimum(centroid - lower, upper - centroid).min()
        reflected = 0
        passes = 0
        eligible = 0
        if step:
            displacement = positions[step] - positions[step - 1]
            expected = headings[step] * speeds[step, :, None] * model.dt
            straight = np.max(np.abs(displacement - expected), axis=1) < 1e-10
            reflected = int((~straight).sum())
            r0 = positions[step - 1, :, None] - positions[step - 1, None, :]
            change = displacement[:, None] - displacement[None, :]
            denominator = (change * change).sum(axis=2)
            tau = np.divide(
                -(r0 * change).sum(axis=2), denominator,
                out=np.zeros_like(denominator), where=denominator > 0,
            ).clip(0, 1)
            nearest = np.linalg.norm(r0 + tau[:, :, None] * change, axis=2)
            valid = triangle & straight[:, None] & straight[None, :]
            eligible = int(valid.sum())
            missed = (distances[step - 1] >= model.repulsion_radius) & (distances[step] >= model.repulsion_radius)
            passes = int((valid & missed & (nearest < model.repulsion_radius - 1e-12)).sum())
        rows.append({
            "NumberOfGroups": len(sizes), "LargestGroupSize": sizes[0],
            "LargestGroupFraction": sizes[0] / n,
            "SecondLargestGroupSize": sizes[1] if len(sizes) > 1 else 0,
            "ComponentSizes": "+".join(map(str, sizes)),
            "DistanceCentroidToNearestWall": float(centroid_wall),
            "MeanFishDistanceToNearestWall": float(to_walls.mean()),
            "MinimumFishDistanceToWall": float(to_walls.min()),
            "ReflectedFishCount": reflected,
            "ExactOverlapPairs": int(((distances[step] == 0) & triangle).sum()),
            "MinimumPairDistance": float(distances[step][triangle].min()) if n > 1 else np.nan,
            "MissedRepulsionPasses": passes,
            "EligibleStraightPairs": eligible,
        })
    frame["Time"] = frame.index.to_numpy() * model.dt
    return frame.join(pd.DataFrame(rows, index=frame.index))


def run_case(seed=0, n_fish=20, duration=62.5, speed=1.0, dt=0.125,
             width=20, height=20, initial_state=None, **model_parameters):
    """Run an explicit physical duration with an integer number of updates."""
    steps = round(duration / dt)
    if not np.isclose(steps * dt, duration, rtol=0, atol=1e-10):
        raise ValueError("duration must be an integer multiple of dt.")
    parameters = dict(seed=seed, speed=speed, dt=dt, width=width, height=height, **model_parameters)
    if initial_state is None:
        model = GoldenShinersModel(n_fish=n_fish, **parameters)
    else:
        positions, headings = initial_state
        if len(positions) != n_fish:
            raise ValueError("initial_state must contain n_fish fish.")
        model = controlled_model(positions, headings, **parameters)
    for _ in range(steps):
        model.step()
    audit_run(model)
    frame = diagnostics_for(model)
    agents = model.datacollector.get_agent_vars_dataframe().copy()
    return model, frame, agents


def fragmentation_episodes(frame, min_duration_s=2.5):
    """Describe consecutive fragmented post-update records.

    Each post-update label represents the preceding dt interval. StartTime is
    the first observed fragmented sample; onset lies in its preceding interval.
    The initial t=0 sample receives no interval weight. A run that starts
    disconnected is not counted as a split from a connected school.
    """
    columns = ["StartStep", "EndStep", "StartTime", "EndTime", "Duration_s",
               "FromConnected", "RightCensored", "Persistent", "SizesAtStart", "Reconnected"]
    if len(frame) < 2:
        return pd.DataFrame(columns=columns)
    dt = float(frame["Time"].iloc[1] - frame["Time"].iloc[0])
    mask = frame["NumberOfGroups"].to_numpy() > 1
    episodes = []
    step = 1
    while step < len(frame):
        if not mask[step]:
            step += 1
            continue
        start = step
        while step + 1 < len(frame) and mask[step + 1]:
            step += 1
        end = step
        duration = (end - start + 1) * dt
        episodes.append({
            "StartStep": int(frame.index[start]), "EndStep": int(frame.index[end]),
            "StartTime": float(frame["Time"].iloc[start]),
            "EndTime": float(frame["Time"].iloc[end]), "Duration_s": duration,
            "FromConnected": bool(not mask[start - 1]),
            "RightCensored": bool(end == len(frame) - 1),
            "Persistent": bool(duration >= min_duration_s - 1e-12),
            "SizesAtStart": frame["ComponentSizes"].iloc[start],
            "Reconnected": bool(end < len(frame) - 1),
        })
        step += 1
    return pd.DataFrame(episodes, columns=columns)


def summarize_case(frame, late_seconds=12.5, persistence_s=2.5):
    """Use equal physical windows, not a fixed count of timestep records."""
    post = frame.iloc[1:]
    end = float(frame["Time"].iloc[-1])
    late = post.loc[post["Time"] > max(0, end - late_seconds) + 1e-12]
    episodes = fragmentation_episodes(frame, persistence_s)
    persistent = episodes.loc[episodes["Persistent"].astype(bool)]
    first_connected = frame.loc[frame["NumberOfGroups"] == 1, "Time"]
    final = frame.iloc[-1]
    return {
        "Duration_s": end,
        "MeanLargestGroupFraction": float(post["LargestGroupFraction"].mean()),
        "ConnectedTimeFraction": float(post["NumberOfGroups"].eq(1).mean()),
        "LateMeanLargestGroupFraction": float(late["LargestGroupFraction"].mean()),
        "LateConnectedFraction": float(late["NumberOfGroups"].eq(1).mean()),
        "LatePolarization": float(late["Polarization"].mean()),
        "LateRotation": float(late["Rotation"].mean()),
        "LateMeanNND": float(late["MeanNND"].mean()),
        "LateMeanDistanceToCentroid": float(late["MeanDistanceToCentroid"].mean()),
        "PersistentSplitEvents": int(persistent["FromConnected"].sum()),
        "PersistentFragmentedTimeFraction": float(persistent["Duration_s"].sum() / end) if end else np.nan,
        "FirstConnectedTime_s": float(first_connected.iloc[0]) if len(first_connected) else np.nan,
        "FinalGroups": int(final["NumberOfGroups"]),
        "FinalLargestGroupFraction": float(final["LargestGroupFraction"]),
        "FinalComponentSizes": final["ComponentSizes"],
        "MissedRepulsionPasses": int(post["MissedRepulsionPasses"].sum()),
        "ExactOverlapPairs": int(frame["ExactOverlapPairs"].sum()),
        "TotalReflectedFishSteps": int(post["ReflectedFishCount"].sum()),
    }
