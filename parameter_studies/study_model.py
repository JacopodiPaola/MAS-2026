"""The shared fish model with a few extra options for the parameter studies.

shiner_model.py is only imported, never changed. With the default options,
StudyModel gives exactly the same trajectories as GoldenShinersModel
(see test_study_model.py).

Extra options (all defined PER DECISION, so they do not depend on dt):
    turn_per_decision   largest turn in one decision, in radians (Puckett: 1.75).
                        None means the fish turns instantly, as in shiner_model.py.
    noise_per_decision  standard deviation of the heading error in one decision,
                        in radians (Puckett: 0.01). 0 means no error.
"""

from pathlib import Path
import sys

import numpy as np
import mesa
from mesa.experimental.continuous_space import ContinuousSpace

# Find the repository root: start in this file's folder and walk up
# until we reach the folder that contains shiner_model.py.
REPOSITORY_ROOT = Path(__file__).resolve().parent
while not (REPOSITORY_ROOT / "shiner_model.py").is_file():
    if REPOSITORY_ROOT == REPOSITORY_ROOT.parent:
        raise FileNotFoundError("shiner_model.py was not found in this folder or any parent folder.")
    REPOSITORY_ROOT = REPOSITORY_ROOT.parent

# Let Python import files from the repository root.
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from shiner_model import GoldenShiners, compute_group_metrics, reflect, unit_vector


class StudyFish(GoldenShiners):
    """A golden shiner whose turn limit and heading error are set per decision."""

    def turn_toward(self, target):
        """Turn from the current heading toward the social target heading."""
        turn_limit = self.model.turn_per_decision
        noise = self.model.noise_per_decision

        # Default: turn instantly to the target, exactly like shiner_model.py.
        if turn_limit is None and noise == 0:
            return target

        # Work with angles: how much does the fish want to turn?
        old_angle = np.arctan2(self.direction[1], self.direction[0])
        target_angle = np.arctan2(target[1], target[0])
        change = target_angle - old_angle

        # Heading error: a small random angle, the same size in every decision.
        if noise > 0:
            change = change + self.model.rng.normal(0, noise)

        # Keep the change between -pi and pi, so the fish turns the short way round.
        change = np.arctan2(np.sin(change), np.cos(change))

        # Turn limit: the fish cannot turn more than turn_limit in one decision.
        if turn_limit is not None:
            change = np.clip(change, -turn_limit, turn_limit)

        new_angle = old_angle + change
        return np.array([np.cos(new_angle), np.sin(new_angle)])


class StudyModel(mesa.Model):
    """Same as GoldenShinersModel, but with StudyFish and the extra options.

    The random numbers are drawn in the same order as in GoldenShinersModel:
    for each fish, first its position and then its heading.
    There is no DataCollector: study_tools.py measures the group itself.
    """

    def __init__(
        self, width=20, height=20, speed=1.0, n_fish=20, seed=None, *,
        dt=0.125, repulsion_radius=0.5, orientation_radius=3.0,
        attraction_radius=5.5,
        enabled_rules=("repulsion", "orientation", "attraction"),
        fov_degrees=360.0, turn_per_decision=None, noise_per_decision=0.0,
    ):
        # Check the radii, because the zones only make sense in this order.
        if not 0 < repulsion_radius < orientation_radius <= attraction_radius:
            raise ValueError("Radii must satisfy 0 < repulsion < orientation <= attraction.")

        super().__init__(seed=seed)

        # Arena and social zones (the same names as in shiner_model.py,
        # because the inherited fish methods read them).
        self.bounds = np.array([[0, width], [0, height]], dtype=float)
        self.dt = float(dt)
        self.repulsion_radius = float(repulsion_radius)
        self.orientation_radius = float(orientation_radius)
        self.attraction_radius = float(attraction_radius)
        self.enabled_rules = frozenset(enabled_rules)
        self.fov_degrees = float(fov_degrees)

        # Extra options of this study model.
        self.turn_per_decision = turn_per_decision
        self.noise_per_decision = float(noise_per_decision)

        # Create the fish at random positions (each fish draws its own heading).
        self.space = ContinuousSpace(self.bounds, torus=False, random=self.random, n_agents=n_fish)
        for _ in range(n_fish):
            position = self.rng.random(2) * np.array([width, height])
            StudyFish(self, self.space, position=position, speed=speed)

    def step(self):
        """One decision for every fish: all fish plan first, then all fish move."""
        self.agents.do("decide")
        self.agents.do("advance")
