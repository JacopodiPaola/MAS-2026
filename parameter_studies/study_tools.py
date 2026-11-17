"""Run one simulation, measure the group, and summarise many runs.

The success definition and its thresholds are fixed here BEFORE any study is run
(see the general README, "¿Cuándo decimos que el cardumen funciona?").
Do not change them after seeing results.
"""

from pathlib import Path
import time

import numpy as np
import pandas as pd

from study_model import StudyModel, compute_group_metrics


# ---------------------------------------------------------------------------
# Fixed definitions (decided before running anything)
# ---------------------------------------------------------------------------

SWIM_DISTANCE = 180.0        # BL: every run lasts until each fish has swum this far
TOGETHER_FRACTION = 0.95     # "together": the largest group has at least 95 % of the fish
TOGETHER_TIME = 0.90         # ... during at least 90 % of the final window
COLLISION_DISTANCE = 0.25    # BL: two fish closer than this count as a collision
COLLISION_TIME = 0.05        # at most 5 % of the moments may have a collision
ORDER_THRESHOLD = 0.65       # polarization or rotation of at least 0.65 = ordered
FIXED_LINK = 5.5             # BL: extra check of "together" that does not change when r_a changes

# Colours for the figures (the same blue, orange and teal as checks/06).
A0_COLOR = "#3366a8"
PUCKETT_COLOR = "#dc7c27"
EXTRA_COLOR = "#2c8c78"

# Set RERUN = True to simulate again even when a saved CSV file exists.
RERUN = False


# ---------------------------------------------------------------------------
# Configurations
# ---------------------------------------------------------------------------

# A0: our current model (360 degrees, instant turns, no noise, 20 x 20 BL arena).
A0_SETTINGS = {
    "label": "A0",
    "base": "A0",
    "n_fish": 20,
    "arena": 20.0,
    "speed": 1.0,
    "dt": 0.125,
    "repulsion_radius": 0.5,
    "orientation_radius": 3.0,
    "attraction_radius": 5.5,
    "fov_degrees": 360.0,
    "turn_per_decision": None,
    "noise_per_decision": 0.0,
    "rules": "repulsion+orientation+attraction",
}

# A4: the Puckett et al. (2018) model (270 degrees, 1.75 rad turn limit,
# 0.01 rad noise per decision, 28 x 28 BL arena).
PUCKETT_SETTINGS = dict(A0_SETTINGS)
PUCKETT_SETTINGS["label"] = "A4"
PUCKETT_SETTINGS["base"] = "A4"
PUCKETT_SETTINGS["fov_degrees"] = 270.0
PUCKETT_SETTINGS["turn_per_decision"] = 1.75
PUCKETT_SETTINGS["noise_per_decision"] = 0.01
PUCKETT_SETTINGS["arena"] = 28.0


def change_settings(settings, label, changes):
    """Return a copy of `settings` with a new label and some values changed."""
    new_settings = dict(settings)
    new_settings.update(changes)
    new_settings["label"] = label
    return new_settings


def rules_from_text(text):
    """Turn "repulsion+attraction" into ("repulsion", "attraction"); "none" means no rules."""
    if text == "none":
        return ()
    return tuple(text.split("+"))


def build_model(settings, seed):
    """Create a StudyModel from a settings dictionary."""
    return StudyModel(
        width=settings["arena"],
        height=settings["arena"],
        speed=settings["speed"],
        n_fish=settings["n_fish"],
        seed=seed,
        dt=settings["dt"],
        repulsion_radius=settings["repulsion_radius"],
        orientation_radius=settings["orientation_radius"],
        attraction_radius=settings["attraction_radius"],
        enabled_rules=rules_from_text(settings["rules"]),
        fov_degrees=settings["fov_degrees"],
        turn_per_decision=settings["turn_per_decision"],
        noise_per_decision=settings["noise_per_decision"],
    )


def number_of_decisions(speed, dt, swim_distance=SWIM_DISTANCE):
    """How many decisions a fish needs to swim `swim_distance` body lengths (default 180 BL)."""
    step_length = speed * dt
    return round(swim_distance / step_length)


def swim_distance_of(settings):
    """180 BL, unless the settings ask for a longer run (only used for one labelled extra check)."""
    if "swim_distance" in settings:
        return settings["swim_distance"]
    return SWIM_DISTANCE


# ---------------------------------------------------------------------------
# Measuring the group at one moment
# ---------------------------------------------------------------------------

def fish_positions(model):
    """Positions of all fish as an (n_fish, 2) array, ordered by fish ID."""
    fish_by_id = sorted(model.agents, key=lambda fish: fish.unique_id)
    positions = []
    for fish in fish_by_id:
        positions.append(fish.position.copy())
    return np.array(positions)


def fish_headings(model):
    """Headings (unit vectors) of all fish as an (n_fish, 2) array, ordered by fish ID."""
    fish_by_id = sorted(model.agents, key=lambda fish: fish.unique_id)
    headings = []
    for fish in fish_by_id:
        headings.append(fish.direction.copy())
    return np.array(headings)


def pair_distances(positions):
    """Distance between every pair of fish. A fish's distance to itself is set to infinity."""
    # differences[i, j] is the vector from fish j to fish i.
    differences = positions[:, None, :] - positions[None, :, :]
    distances = np.linalg.norm(differences, axis=2)
    np.fill_diagonal(distances, np.inf)
    return distances


def largest_group_size(distances, link_radius):
    """Number of fish in the biggest group.

    Two fish are linked if they are at most `link_radius` apart (they can sense
    each other). A group is every fish that can be reached through a chain of
    links. Same definition as handlings/trial_one/diagnostics.py.
    """
    n_fish = len(distances)
    linked = (distances <= link_radius).tolist()    # plain lists are fast to loop over
    visited = [False] * n_fish
    largest = 0

    for start in range(n_fish):
        if visited[start]:
            continue
        # Flood fill: visit every fish that can be reached from `start`.
        group_size = 0
        to_visit = [start]
        visited[start] = True
        while len(to_visit) > 0:
            current = to_visit.pop()
            group_size += 1
            for other in range(n_fish):
                if linked[current][other] and not visited[other]:
                    visited[other] = True
                    to_visit.append(other)
        largest = max(largest, group_size)

    return largest


def collective_state(polarization, rotation, largest_fraction):
    """Name the state of the group at one moment."""
    if largest_fraction < TOGETHER_FRACTION:
        return "fragmented"
    if polarization >= ORDER_THRESHOLD:
        return "polarized"
    if rotation >= ORDER_THRESHOLD:
        return "milling"
    return "swarm"


def measure_moment(model):
    """All measurements of the group at the current moment."""
    # Polarization, rotation, nearest-neighbour distance and distance to the
    # centroid come from the shared shiner_model.py, so they match the checks.
    shared = compute_group_metrics(model)

    distances = pair_distances(fish_positions(model))
    n_fish = len(distances)
    # Main definition: two fish are linked if they are within the attraction radius.
    largest_fraction = largest_group_size(distances, model.attraction_radius) / n_fish
    # Extra check with a fixed 5.5 BL link, for runs where the attraction radius changes.
    largest_fraction_fixed = largest_group_size(distances, FIXED_LINK) / n_fish

    return {
        "polarization": shared["Polarization"],
        "rotation": shared["Rotation"],
        "nnd": shared["MeanNND"],
        "centroid_distance": shared["MeanDistanceToCentroid"],
        "largest_fraction": largest_fraction,
        "largest_fraction_fixed": largest_fraction_fixed,
        "closest_pair": distances.min(),
        "state": collective_state(shared["Polarization"], shared["Rotation"], largest_fraction),
    }


# ---------------------------------------------------------------------------
# Summarising the final window of one run
# ---------------------------------------------------------------------------

def average(moments, key):
    """Mean of one measurement over all moments."""
    total = 0.0
    for moment in moments:
        total += moment[key]
    return total / len(moments)


def fraction_of_moments(moments, condition):
    """Fraction of moments for which condition(moment) is True."""
    count = 0
    for moment in moments:
        if condition(moment):
            count += 1
    return count / len(moments)


def fraction_in_state(moments, state):
    """Fraction of moments in which the group is in `state`."""
    count = 0
    for moment in moments:
        if moment["state"] == state:
            count += 1
    return count / len(moments)


def smallest(moments, key):
    """Smallest value of one measurement over all moments."""
    smallest_value = np.inf
    for moment in moments:
        smallest_value = min(smallest_value, moment[key])
    return smallest_value


def is_together(moment):
    return moment["largest_fraction"] >= TOGETHER_FRACTION


def is_together_fixed_link(moment):
    return moment["largest_fraction_fixed"] >= TOGETHER_FRACTION


def has_collision(moment):
    return moment["closest_pair"] < COLLISION_DISTANCE


def final_label(summary):
    """One label for the whole final window, from the window averages."""
    if summary["together_fraction"] < TOGETHER_TIME:
        return "fragmented"
    if summary["polarization"] >= ORDER_THRESHOLD:
        return "polarized"
    if summary["rotation"] >= ORDER_THRESHOLD:
        return "milling"
    return "swarm"


def summarize_window(moments):
    """Turn the list of moments of the final window into one row of results."""
    summary = {
        "polarization": average(moments, "polarization"),
        "rotation": average(moments, "rotation"),
        "nnd": average(moments, "nnd"),
        "centroid_distance": average(moments, "centroid_distance"),
        "largest_group_fraction": average(moments, "largest_fraction"),
        "together_fraction": fraction_of_moments(moments, is_together),
        "together_fraction_fixed_link": fraction_of_moments(moments, is_together_fixed_link),
        "collision_fraction": fraction_of_moments(moments, has_collision),
        "min_pair_distance": smallest(moments, "closest_pair"),
    }

    # Fraction of time in each collective state.
    for state in ["polarized", "milling", "swarm", "fragmented"]:
        summary["time_" + state] = fraction_in_state(moments, state)

    # The three parts of "works" (general README), and the final verdict.
    summary["is_together"] = summary["together_fraction"] >= TOGETHER_TIME
    summary["no_collisions"] = summary["collision_fraction"] <= COLLISION_TIME
    summary["is_ordered"] = (summary["polarization"] >= ORDER_THRESHOLD
                             or summary["rotation"] >= ORDER_THRESHOLD)
    summary["works"] = summary["is_together"] and summary["no_collisions"] and summary["is_ordered"]
    summary["label_final"] = final_label(summary)
    return summary


# ---------------------------------------------------------------------------
# Running simulations
# ---------------------------------------------------------------------------

def run_simulation(settings, seed):
    """Run one simulation and return one dictionary with settings and results.

    The run lasts until each fish has swum SWIM_DISTANCE body lengths.
    The group is measured at every decision of the final third of the run.
    """
    start_time = time.perf_counter()
    model = build_model(settings, seed)
    n_decisions = number_of_decisions(settings["speed"], settings["dt"], swim_distance_of(settings))
    window_start = n_decisions - n_decisions // 3   # decisions after this one are measured

    moments = []
    for decision in range(1, n_decisions + 1):
        model.step()
        if decision > window_start:
            moments.append(measure_moment(model))

    result = dict(settings)
    result["seed"] = seed
    result["step_length"] = settings["speed"] * settings["dt"]
    result["n_decisions"] = n_decisions
    result.update(summarize_window(moments))
    result["runtime_s"] = time.perf_counter() - start_time
    return result


def run_many(list_of_settings, seeds, csv_path):
    """Run every configuration with every seed and save the results to a CSV file.

    If the CSV file already exists, it is loaded instead (no new simulations),
    unless RERUN is True.
    """
    csv_path = Path(csv_path)
    if csv_path.exists() and not RERUN:
        print(f"Loaded saved results from {csv_path.name} (set study_tools.RERUN = True to simulate again).")
        return load_results(csv_path)

    rows = []
    start_time = time.perf_counter()
    for number, settings in enumerate(list_of_settings, start=1):
        works_count = 0
        for seed in seeds:
            result = run_simulation(settings, seed)
            rows.append(result)
            if result["works"]:
                works_count += 1
        minutes = (time.perf_counter() - start_time) / 60
        print(f"[{number}/{len(list_of_settings)}] {settings['label']}: "
              f"works in {works_count} of {len(seeds)} seeds ({minutes:.1f} min so far)", flush=True)

    results = pd.DataFrame(rows)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(csv_path, index=False)
    # Return the saved file, so a fresh run and a later reload give exactly the same numbers.
    return load_results(csv_path)


def load_results(csv_path):
    """Read a results CSV file; "round_trip" reads every number back exactly as it was saved."""
    return pd.read_csv(csv_path, float_precision="round_trip")


# ---------------------------------------------------------------------------
# Summarising many runs
# ---------------------------------------------------------------------------

METRICS = [
    "works", "polarization", "rotation", "nnd", "centroid_distance",
    "largest_group_fraction", "together_fraction", "together_fraction_fixed_link",
    "collision_fraction", "min_pair_distance",
    "time_polarized", "time_milling", "time_swarm", "time_fragmented", "runtime_s",
]


def summarize(results, group_by):
    """Mean and standard error (over seeds) of every metric, per configuration.

    "works" becomes the fraction of seeds in which the school works.
    Columns ending in "_se" are standard errors.
    """
    results = results.copy()
    results["works"] = results["works"].astype(float)
    groups = results.groupby(group_by, sort=False)

    table = groups[METRICS].mean()
    errors = groups[METRICS].sem()
    for metric in METRICS:
        table[metric + "_se"] = errors[metric]
    table["n_seeds"] = groups.size()
    return table.reset_index()


# ---------------------------------------------------------------------------
# Trajectories (for the exact comparisons in the tests and in study 3)
# ---------------------------------------------------------------------------

def record_trajectory(model, n_decisions):
    """Run `n_decisions` steps and return the positions after every step: (steps + 1, fish, 2)."""
    positions = [fish_positions(model)]
    for _ in range(n_decisions):
        model.step()
        positions.append(fish_positions(model))
    return np.array(positions)


# ---------------------------------------------------------------------------
# Short tables for the notebooks
# ---------------------------------------------------------------------------

def mean_and_error_text(summary, column):
    """Texts like "0.95 ± 0.01" (mean ± standard error) for one column of a summary."""
    texts = []
    for index in range(len(summary)):
        mean = summary[column].iloc[index]
        error = summary[column + "_se"].iloc[index]
        texts.append(f"{mean:.2f} ± {error:.2f}")
    return texts


def works_text(summary):
    """Texts like "9/10": in how many seeds the school works."""
    texts = []
    for index in range(len(summary)):
        n_seeds = summary["n_seeds"].iloc[index]
        n_works = round(summary["works"].iloc[index] * n_seeds)
        texts.append(f"{n_works}/{n_seeds}")
    return texts


def short_table(summary, label_column="label"):
    """The main results of each configuration in one small table."""
    table = pd.DataFrame()
    table["configuration"] = summary[label_column]
    table["works"] = works_text(summary)
    table["polarization"] = mean_and_error_text(summary, "polarization")
    table["rotation"] = mean_and_error_text(summary, "rotation")
    table["NND (BL)"] = mean_and_error_text(summary, "nnd")
    table["time together"] = mean_and_error_text(summary, "together_fraction")
    table["time with collision"] = mean_and_error_text(summary, "collision_fraction")
    table["closest pair (BL)"] = mean_and_error_text(summary, "min_pair_distance")
    return table


def final_label_counts(results, label_column="label"):
    """How many seeds of each configuration end in each final label."""
    counts = pd.crosstab(results[label_column], results["label_final"])
    # Keep the configurations in the order in which they were run.
    order = []
    for label in results[label_column]:
        if label not in order:
            order.append(label)
    counts = counts.reindex(order)
    for state in ["polarized", "milling", "swarm", "fragmented"]:
        if state not in counts.columns:
            counts[state] = 0
    return counts[["polarized", "milling", "swarm", "fragmented"]]

