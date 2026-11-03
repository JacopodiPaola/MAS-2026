"""Small fixtures shared by the validation notebooks, with no model copies."""

import numpy as np
from mesa.datacollection import DataCollector
from shiner_model import GoldenShinersModel


def run_model(n_fish=20, seed=1, steps=100, **kwargs):
    model = GoldenShinersModel(n_fish=n_fish, seed=seed, **kwargs)
    for _ in range(steps):
        model.step()
    return model


def controlled_model(positions, directions, **kwargs):
    """Replace the random initial state and record the controlled state at t=0."""
    positions = np.asarray(positions, dtype=float)
    directions = np.asarray(directions, dtype=float)
    if positions.ndim != 2 or positions.shape[1] != 2 or directions.shape != positions.shape:
        raise ValueError("Positions and directions must be matching (n, 2) arrays.")
    if not np.isfinite(positions).all() or not np.isfinite(directions).all():
        raise ValueError("Controlled states must be finite.")
    if not np.allclose(np.linalg.norm(directions, axis=1), 1.0, rtol=0, atol=1e-12):
        raise ValueError("Controlled directions must have unit length.")
    kwargs.setdefault("seed", 123)
    model = GoldenShinersModel(n_fish=len(positions), **kwargs)
    if np.any(positions < model.bounds[:, 0]) or np.any(positions > model.bounds[:, 1]):
        raise ValueError("Controlled positions must be inside the arena.")
    for fish, position, direction in zip(model.agents, positions, directions):
        fish.position = position.copy()
        fish.direction = direction.copy()
        fish.next_position = position.copy()
        fish.next_direction = direction.copy()
    model.datacollector = DataCollector(
        model_reporters=model.datacollector.model_reporters,
        agent_reporters=model.datacollector.agent_reporters,
    )
    model.record_state()
    return model


def audit_run(model):
    """Check recording completeness, finite values, unit headings and bounds."""
    group = model.datacollector.get_model_vars_dataframe()
    fish = model.datacollector.get_agent_vars_dataframe()
    n = len(model.agents)
    assert group.shape == (model.steps + 1, 8)
    assert fish.shape == ((model.steps + 1) * n, 5)
    assert list(group.index) == list(range(model.steps + 1))
    assert fish.index.is_unique
    assert fish.groupby(level="Step").size().eq(n).all()
    assert np.isfinite(fish.to_numpy()).all()
    assert np.isfinite(group.select_dtypes(include="number").drop(columns="MeanNND")).all().all()
    assert (group["MeanNND"].isna().all() if n == 1 else np.isfinite(group["MeanNND"]).all())
    np.testing.assert_allclose(np.hypot(fish["DirX"], fish["DirY"]), 1.0, atol=1e-12)
    for column, (lower, upper) in zip(("X", "Y"), model.bounds):
        assert fish[column].between(lower, upper).all()
    assert group["Polarization"].between(-1e-12, 1 + 1e-12).all()
    assert group["Rotation"].between(-1e-12, 1 + 1e-12).all()
    return {"Fish": n, "Steps": model.steps, "Model rows": len(group), "Agent rows": len(fish), "Result": "passed"}
