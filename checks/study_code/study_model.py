"""The shared fish model with a few extra options for the parameter studies.

shiner_model.py is only imported, never changed. With the default options,
StudyModel gives exactly the same trajectories as GoldenShinersModel
(see test_study_model.py).

Extra options (turn and noise are defined PER DECISION, so they do not depend on dt):
    turn_per_decision   largest turn in one decision, in radians (Puckett: 1.75).
                        None means the fish turns instantly, as in shiner_model.py.
    noise_per_decision  standard deviation of the heading error in one decision,
                        in radians (Puckett: 0.01). 0 means no error.

Options added for trial five (parameters the papers did not test):
    initial_spread      1.0 = fish start anywhere in the arena; 0.25 = fish start in a
                        central square whose side is 25 % of the arena side.
    update              "synchronous" = all fish decide from the same old state, then all move;
                        "asynchronous" = in a random order, each fish decides and moves at once.
    neighbour_mode      "metric" = every fish inside the zones counts;
                        "topological" = only the k_neighbours nearest fish count (zones still apply).
    k_neighbours        k for the topological mode.
    social_combination  "raw_sum" = add the orientation and attraction sums (Puckett SI eq. 7);
                        "normalized" = make each of them length 1 before adding.
    speed_sd            relative standard deviation of each fish's own fixed speed (0 = all equal).
    speed_gain          strength of the speed regulation inspired by Katz et al. (2011) (0 = off).
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

from shiner_model import GoldenShiners, reflect, unit_vector

# Limits of the regulated speed, as a multiple of the fish's own normal speed.
SLOWEST_FACTOR = 0.5
FASTEST_FACTOR = 1.5


def neighbour_distance(neighbour):
    """The distance stored in a (fish, displacement, distance) neighbour tuple."""
    return neighbour[2]


class StudyFish(GoldenShiners):
    """A golden shiner with the extra options of the study model."""

    def __init__(self, model, space, position=(0, 0), speed=1.0):
        super().__init__(model, space, position=position, speed=speed)
        # Each fish remembers its own normal speed (used by speed_sd and speed_gain).
        self.base_speed = self.speed
        self.next_speed = self.speed

    def get_neighbors(self):
        """Neighbours inside the zones; in topological mode only the k nearest of them."""
        neighbors = super().get_neighbors()
        if self.model.neighbour_mode == "metric":
            return neighbors
        # Topological mode: sort by distance and keep the k nearest.
        neighbors.sort(key=neighbour_distance)
        return neighbors[:self.model.k_neighbours]

    def social_direction(self, neighbors):
        """Desired heading from the neighbours (repulsion has priority)."""
        # Default: add the raw sums, exactly like shiner_model.py.
        if self.model.social_combination == "raw_sum":
            return super().social_direction(neighbors)

        # Normalized: same rules, but orientation and attraction count equally,
        # whatever the number of fish in each zone.
        rules = self.model.enabled_rules
        if "repulsion" in rules:
            repel = self.repulsion(neighbors)
            if repel is not None:
                return repel
        social = np.zeros(2)
        if "orientation" in rules:
            social += unit_vector(self.orientation(neighbors), np.zeros(2))
        if "attraction" in rules:
            social += unit_vector(self.attraction(neighbors), np.zeros(2))
        return unit_vector(social, self.direction)

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

    def regulated_speed(self, neighbors):
        """Speed regulation inspired by Katz et al. (2011), as described in checks/README.md (trial five).

        For each neighbour, take how far it is ahead (+) or behind (-) in BL.
        A neighbour inside the repulsion zone counts with the opposite sign:
        close ahead -> slow down, close behind -> speed up,
        far ahead -> speed up, far behind -> slow down.
        """
        if len(neighbors) == 0:
            return self.base_speed

        total = 0.0
        for other, displacement, distance in neighbors:
            ahead = np.dot(displacement, self.direction)
            if distance < self.model.repulsion_radius:
                ahead = -ahead
            total += ahead
        signal = total / len(neighbors)

        factor = 1 + self.model.speed_gain * signal
        factor = min(max(factor, SLOWEST_FACTOR), FASTEST_FACTOR)
        return self.base_speed * factor

    def decide(self):
        """Plan the next heading, speed and position from the old state."""
        # Default: constant speed, exactly like shiner_model.py.
        if self.model.speed_gain == 0:
            super().decide()
            return

        neighbors = self.get_neighbors()
        direction = self.turn_toward(self.social_direction(neighbors))
        self.next_speed = self.regulated_speed(neighbors)
        position = self.position + direction * self.next_speed * self.model.dt
        self.next_position, self.next_direction = reflect(position, direction, self.model.bounds)

    def advance(self):
        """Commit the planned state."""
        super().advance()
        if self.model.speed_gain != 0:
            self.speed = self.next_speed


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
        initial_spread=1.0, update="synchronous", neighbour_mode="metric",
        k_neighbours=7, social_combination="raw_sum", speed_sd=0.0, speed_gain=0.0,
    ):
        # Check the options, because a typo would otherwise silently use the default.
        if not 0 < repulsion_radius < orientation_radius <= attraction_radius:
            raise ValueError("Radii must satisfy 0 < repulsion < orientation <= attraction.")
        if not 0 < initial_spread <= 1:
            raise ValueError("initial_spread must be in (0, 1].")
        if update not in ["synchronous", "asynchronous"]:
            raise ValueError("update must be 'synchronous' or 'asynchronous'.")
        if neighbour_mode not in ["metric", "topological"]:
            raise ValueError("neighbour_mode must be 'metric' or 'topological'.")
        if social_combination not in ["raw_sum", "normalized"]:
            raise ValueError("social_combination must be 'raw_sum' or 'normalized'.")

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
        self.update = update
        self.neighbour_mode = neighbour_mode
        self.k_neighbours = int(k_neighbours)
        self.social_combination = social_combination
        self.speed_gain = float(speed_gain)
        self.lightField = None   # shiner_model.py on develop (Jacopo's light draft) reads this; the study model has no light

        # Create the fish at random positions (each fish draws its own heading).
        self.space = ContinuousSpace(self.bounds, torus=False, random=self.random, n_agents=n_fish)
        arena_size = np.array([width, height])
        for _ in range(n_fish):
            if initial_spread == 1.0:
                # Default: anywhere in the arena, exactly like shiner_model.py.
                position = self.rng.random(2) * arena_size
            else:
                # Inside a central square whose side is initial_spread times the arena side.
                corner = arena_size * (1 - initial_spread) / 2
                position = corner + self.rng.random(2) * arena_size * initial_spread
            StudyFish(self, self.space, position=position, speed=speed)

        # Each fish gets its own fixed speed. We draw these numbers only after all
        # fish exist, so positions and headings are the same as without this option.
        if speed_sd > 0:
            for fish in self.agents:
                factor = 1 + speed_sd * self.rng.normal()
                factor = max(factor, 0.1)   # a fish never stops or swims backwards
                fish.speed = speed * factor
                fish.base_speed = fish.speed
                fish.next_speed = fish.speed

    def step(self):
        """One decision for every fish."""
        if self.update == "synchronous":
            # Default: all fish plan from the same old state, then all fish move.
            self.agents.do("decide")
            self.agents.do("advance")
        else:
            # Asynchronous: in a new random order every step, each fish decides
            # and moves at once, so later fish already see the new positions.
            fish_list = list(self.agents)
            order = self.rng.permutation(len(fish_list))
            for index in order:
                fish = fish_list[index]
                fish.decide()
                fish.advance()
