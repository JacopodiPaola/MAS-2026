"""Tests for study_model.py and study_tools.py.

Run from any folder with:
    python test_study_model.py
Every test uses plain asserts and prints one line when it passes.
"""

from pathlib import Path
import sys

import numpy as np

# Let Python find study_model.py and study_tools.py next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import study_tools
from study_model import StudyModel
from study_tools import (
    A0_SETTINGS, PUCKETT_SETTINGS, build_model, change_settings, fish_headings,
    fish_positions, number_of_decisions, record_trajectory, run_simulation,
)
from shiner_model import GoldenShinersModel


def test_default_matches_shared_model():
    """1. With default options, StudyModel gives exactly the same fish as GoldenShinersModel."""
    for seed in range(5):
        shared = GoldenShinersModel(seed=seed)
        study = StudyModel(seed=seed)
        for _ in range(480):
            shared.step()
            study.step()
        assert np.array_equal(fish_positions(shared), fish_positions(study)), f"positions differ, seed {seed}"
        assert np.array_equal(fish_headings(shared), fish_headings(study)), f"headings differ, seed {seed}"
    print("Test 1 passed: default StudyModel = GoldenShinersModel (seeds 0-4, 480 steps, exact).")


def test_turn_limit_per_decision():
    """2. With turn_per_decision = 1.75, no fish turns more than 1.75 rad in one decision.

    A wall bounce also changes the heading, so we skip every fish that ends a step
    closer to a wall than one step length: only those fish can have bounced.
    """
    settings = change_settings(PUCKETT_SETTINGS, "turn test", {})
    model = build_model(settings, seed=0)
    step_length = settings["speed"] * settings["dt"]
    largest_turn = 0.0

    for _ in range(480):
        old_headings = fish_headings(model)
        model.step()
        new_headings = fish_headings(model)
        positions = fish_positions(model)
        for fish in range(len(positions)):
            distance_to_wall = min(positions[fish].min(), settings["arena"] - positions[fish].max())
            if distance_to_wall <= step_length:
                continue
            cosine = np.clip(np.dot(old_headings[fish], new_headings[fish]), -1.0, 1.0)
            turn = np.arccos(cosine)
            assert turn <= 1.75 + 1e-9, f"a fish turned {turn:.4f} rad in one decision"
            largest_turn = max(largest_turn, turn)

    # The limit must really be used at least once, otherwise this test proves nothing.
    assert largest_turn > 1.7, f"the turn limit was never reached (largest turn {largest_turn:.3f} rad)"
    print(f"Test 2 passed: largest turn in one decision = {largest_turn:.4f} rad (limit 1.75).")


def test_number_of_decisions():
    """3. Each run lasts until every fish has swum 180 BL: decisions = 180 / (speed * dt)."""
    expected = {0.2: 7200, 1.0: 1440, 2.6: 554, 5.0: 288, 8.0: 180}
    for speed in expected:
        assert number_of_decisions(speed, 0.125) == expected[speed], f"wrong count for speed {speed}"

    # run_simulation must report the same number.
    for speed in [5.0, 8.0]:
        settings = change_settings(A0_SETTINGS, "count test", {"speed": speed})
        result = run_simulation(settings, seed=0)
        assert result["n_decisions"] == expected[speed]
        assert result["step_length"] == speed * 0.125
    print("Test 3 passed: 0.2 BL/s -> 7200, 1 -> 1440, 2.6 -> 554, 5 -> 288, 8 -> 180 decisions.")


def test_same_step_length_same_trajectories():
    """4. Only the step length (speed x dt) matters: three pairs (speed, dt) with 0.25 BL per decision."""
    pairs = [(1.0, 0.25), (2.0, 0.125), (0.5, 0.5)]
    for base in [A0_SETTINGS, PUCKETT_SETTINGS]:
        for seed in range(3):
            trajectories = []
            for speed, dt in pairs:
                settings = change_settings(base, "step length test", {"speed": speed, "dt": dt})
                trajectories.append(record_trajectory(build_model(settings, seed), 400))
            assert np.array_equal(trajectories[0], trajectories[1]), f"{base['label']}, seed {seed}"
            assert np.array_equal(trajectories[0], trajectories[2]), f"{base['label']}, seed {seed}"
    print("Test 4 passed: (1, 0.25), (2, 0.125) and (0.5, 0.5) give identical trajectories "
          "(A0 and A4, seeds 0-2, 400 decisions).")


if __name__ == "__main__":
    test_default_matches_shared_model()
    test_turn_limit_per_decision()
    test_number_of_decisions()
    test_same_step_length_same_trajectories()
    print("All tests passed.")
