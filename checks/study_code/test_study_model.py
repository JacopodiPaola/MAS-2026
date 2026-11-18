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

from study_model import StudyModel
from study_tools import (
    A0_SETTINGS, PUCKETT_SETTINGS, build_model, change_settings, fish_headings,
    fish_positions, number_of_decisions, record_trajectory, run_simulation,
)
from shiner_model import GoldenShiners, GoldenShinersModel


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


# ---------------------------------------------------------------------------
# Tests for the trial five options
# ---------------------------------------------------------------------------

def place_fish(model, positions, headings):
    """Put the fish of a small test model at chosen positions with chosen headings."""
    fish_by_id = sorted(model.agents, key=lambda fish: fish.unique_id)
    for index in range(len(fish_by_id)):
        fish_by_id[index].position = np.array(positions[index], dtype=float)
        fish_by_id[index].direction = np.array(headings[index], dtype=float)
    return fish_by_id


def test_initial_spread():
    """5. With initial_spread = 0.25, every fish starts in the central square (side 7 BL of 28)."""
    model = StudyModel(width=28, height=28, seed=0, initial_spread=0.25)
    positions = fish_positions(model)
    assert positions.min() >= 10.5 and positions.max() <= 17.5
    # The headings are the same random numbers as with the default start.
    default = StudyModel(width=28, height=28, seed=0)
    assert np.array_equal(fish_headings(model), fish_headings(default))
    print("Test 5 passed: initial_spread = 0.25 starts every fish inside [10.5, 17.5] x [10.5, 17.5].")


def test_asynchronous_update():
    """6. Asynchronous update is reproducible, differs from synchronous, and still moves one step length."""
    first = StudyModel(seed=0, update="asynchronous")
    second = StudyModel(seed=0, update="asynchronous")
    synchronous = StudyModel(seed=0)
    for _ in range(100):
        first.step()
        second.step()
        synchronous.step()
    assert np.array_equal(fish_positions(first), fish_positions(second))
    assert not np.array_equal(fish_positions(first), fish_positions(synchronous))

    # In one asynchronous step every fish still moves exactly speed x dt (away from walls).
    model = StudyModel(seed=1, update="asynchronous")
    before = fish_positions(model)
    model.step()
    after = fish_positions(model)
    for fish in range(len(after)):
        distance_to_wall = min(after[fish].min(), 20 - after[fish].max())
        if distance_to_wall > 0.125:
            assert abs(np.linalg.norm(after[fish] - before[fish]) - 0.125) < 1e-12
    print("Test 6 passed: asynchronous update is reproducible and differs from synchronous.")


def test_topological_neighbours():
    """7. Topological mode keeps exactly the k nearest of the fish inside the zones."""
    model = StudyModel(seed=0, n_fish=30, neighbour_mode="topological", k_neighbours=4)
    for fish in model.agents:
        all_neighbours = GoldenShiners.get_neighbors(fish)   # the metric list of the shared model
        kept = fish.get_neighbors()
        assert len(kept) == min(4, len(all_neighbours))
        all_distances = sorted(neighbour[2] for neighbour in all_neighbours)
        kept_distances = sorted(neighbour[2] for neighbour in kept)
        assert kept_distances == all_distances[:len(kept)]
    print("Test 7 passed: topological mode keeps the 4 nearest neighbours.")


def test_normalized_combination():
    """8. Normalized: one aligned neighbour counts as much as two attracting neighbours."""
    # Fish 0 swims east. Fish 1 (orientation zone, 1 BL away) swims north.
    # Fish 2 and 3 are 4 BL east (attraction zone).
    positions = [(10, 10), (10, 11), (14, 10), (14, 10)]
    headings = [(1, 0), (0, 1), (1, 0), (1, 0)]

    raw_model = StudyModel(seed=0, n_fish=4)
    fish = place_fish(raw_model, positions, headings)[0]
    raw = fish.social_direction(fish.get_neighbors())
    assert np.allclose(raw, np.array([2, 1]) / np.sqrt(5))      # (0, 1) + 2 x (1, 0)

    normalized_model = StudyModel(seed=0, n_fish=4, social_combination="normalized")
    fish = place_fish(normalized_model, positions, headings)[0]
    normalized = fish.social_direction(fish.get_neighbors())
    assert np.allclose(normalized, np.array([1, 1]) / np.sqrt(2))   # (0, 1) + (1, 0)
    print("Test 8 passed: raw sum -> (2, 1)/sqrt(5); normalized -> (1, 1)/sqrt(2).")


def test_speed_differences():
    """9. speed_sd gives each fish its own speed and does not change positions or headings."""
    model = StudyModel(seed=0, n_fish=400, speed_sd=0.3)
    same_fish = StudyModel(seed=0, n_fish=400)
    assert np.array_equal(fish_positions(model), fish_positions(same_fish))
    assert np.array_equal(fish_headings(model), fish_headings(same_fish))
    speeds = []
    for fish in model.agents:
        speeds.append(fish.speed)
    assert abs(np.mean(speeds) - 1.0) < 0.05
    assert abs(np.std(speeds) - 0.3) < 0.04
    print(f"Test 9 passed: 400 fish, mean speed {np.mean(speeds):.3f}, standard deviation {np.std(speeds):.3f}.")


def test_speed_regulation():
    """10. Speed regulation: close ahead -> slower, close behind -> faster, far ahead -> faster, far behind -> slower."""
    cases = [
        (0.3, 1 - 0.3 * 0.3),    # close ahead: signal -0.3
        (-0.3, 1 + 0.3 * 0.3),   # close behind: signal +0.3
        (1.0, 1 + 0.3 * 1.0),    # far ahead: signal +1
        (-1.0, 1 - 0.3 * 1.0),   # far behind: signal -1
        (2.0, 1.5),              # far ahead, clipped at 1.5 x the normal speed
        (-2.0, 0.5),             # far behind, clipped at 0.5 x the normal speed
    ]
    for ahead, expected_speed in cases:
        model = StudyModel(seed=0, n_fish=2, speed_gain=0.3)
        fish = place_fish(model, [(10, 10), (10 + ahead, 10)], [(1, 0), (1, 0)])[0]
        speed = fish.regulated_speed(fish.get_neighbors())
        assert abs(speed - expected_speed) < 1e-12, (ahead, speed, expected_speed)

    # In a real run the speeds really change and stay between 0.5 and 1.5.
    model = StudyModel(seed=0, speed_gain=0.3)
    for _ in range(50):
        model.step()
    speeds = []
    for fish in model.agents:
        speeds.append(fish.speed)
    assert min(speeds) >= 0.5 and max(speeds) <= 1.5 and min(speeds) < max(speeds)
    print("Test 10 passed: the speed rule follows checks/README.md (trial five), limited to 0.5-1.5 x the normal speed.")


if __name__ == "__main__":
    test_default_matches_shared_model()
    test_turn_limit_per_decision()
    test_number_of_decisions()
    test_same_step_length_same_trajectories()
    test_initial_spread()
    test_asynchronous_update()
    test_topological_neighbours()
    test_normalized_combination()
    test_speed_differences()
    test_speed_regulation()
    print("All tests passed.")
