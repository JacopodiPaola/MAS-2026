"""A deterministic, constant-speed 2D social baseline for the shiner checks.

The three social zones follow Couzin's raw-vector combination. Perception is
360 degrees and turns are instantaneous; this is not a fitted fish model.
"""

import numpy as np
import mesa
from mesa.datacollection import DataCollector
from mesa.experimental.continuous_space import ContinuousSpace, ContinuousSpaceAgent


EPSILON = 1e-12
SOCIAL_RULES = frozenset({"repulsion", "orientation", "attraction"})


def unit_vector(vector, fallback):
    """Normalize a vector, or copy the fallback when the sum cancels."""
    length = np.linalg.norm(vector)
    return vector / length if length > EPSILON else np.array(fallback, dtype=float, copy=True)


def classify_collective_state(polarization, rotation, low=0.35, high=0.65):
    """Describe an observed state using exploratory, strict thresholds."""
    if not 0 <= low < high <= 1:
        raise ValueError("Thresholds must satisfy 0 <= low < high <= 1.")
    if polarization > high and rotation < low:
        return "polarized"
    if polarization < low and rotation > high:
        return "milling"
    if polarization < low and rotation < low:
        return "swarm"
    return "transition"


def compute_group_metrics(model):
    """Measure the current fish state without changing it or drawing randomness."""
    fish = list(model.agents)
    if not fish:
        raise ValueError("Group metrics require at least one fish.")
    positions = np.array([f.position for f in fish], dtype=float)
    directions = np.array([f.direction for f in fish], dtype=float)
    speeds = np.array([f.speed for f in fish], dtype=float)
    centroid = positions.mean(axis=0)
    polarization = float(np.linalg.norm(directions.mean(axis=0)))

    radial = positions - centroid
    radii = np.linalg.norm(radial, axis=1)
    unit_radial = np.divide(
        radial, radii[:, None], out=np.zeros_like(radial), where=radii[:, None] > 0
    )
    rotation = float(abs(np.mean(
        unit_radial[:, 0] * directions[:, 1] - unit_radial[:, 1] * directions[:, 0]
    )))

    mean_nnd = np.nan
    if len(fish) > 1:
        distances = np.linalg.norm(positions[:, None] - positions[None, :], axis=2)
        np.fill_diagonal(distances, np.inf)
        mean_nnd = float(distances.min(axis=1).mean())

    return {
        "Polarization": polarization,
        "Rotation": rotation,
        "MeanSpeed": float(speeds.mean()),
        "MeanNND": mean_nnd,
        "MeanDistanceToCentroid": float(radii.mean()),
        "CentroidX": float(centroid[0]),
        "CentroidY": float(centroid[1]),
        "CollectiveState": classify_collective_state(polarization, rotation),
    }


def reflect(position, direction, bounds):
    """Reflect a proposed state, including moves that cross multiple walls."""
    lower, upper = bounds[:, 0], bounds[:, 1]
    span = upper - lower
    folded = (position - lower) % (2 * span)
    mirrored = folded > span
    position = lower + np.where(mirrored, 2 * span - folded, folded)
    direction = direction * np.where(mirrored, -1.0, 1.0)
    outward = ((position == lower) & (direction < 0)) | ((position == upper) & (direction > 0))
    direction[outward] *= -1
    return position, direction


class GoldenShiners(ContinuousSpaceAgent):
    """A fish that plans from the old state, then commits its planned state."""

    def __init__(self, model, space, position=(0, 0), speed=1.0):
        super().__init__(space, model)
        self.position = np.array(position, dtype=float)
        self.speed = float(speed)
        angle = model.rng.uniform(0, 2 * np.pi)
        self.direction = np.array([np.cos(angle), np.sin(angle)])
        self.next_position = self.position.copy()
        self.next_direction = self.direction.copy()

    def get_neighbors(self):
        """Return relative positions inside the outer social radius."""
        neighbors = []
        for other in self.model.agents:
            if other is self:
                continue
            displacement = other.position - self.position
            distance = np.linalg.norm(displacement)
            if distance <= self.model.attraction_radius:
                neighbors.append((other, displacement, distance))
        return neighbors

    def overlap_direction(self, other):
        """Choose opposite escape vectors for an exactly coincident pair.

        Heading differences already reverse sign when the pair is reversed.
        Identical headings use opposite perpendiculars, ordered by agent ID.
        This is an explicit numerical convention, not a rule fitted to fish.
        """
        difference = self.direction - other.direction
        length = np.linalg.norm(difference)
        if length > 0:
            return difference / length
        perpendicular = np.array([-self.direction[1], self.direction[0]])
        if self.unique_id > other.unique_id:
            perpendicular *= -1
        return perpendicular

    def repulsion(self, neighbors):
        """Return an escape heading whenever the repulsion zone is occupied."""
        close = []
        for other, displacement, distance in neighbors:
            if distance < self.model.repulsion_radius:
                away = -displacement / distance if distance > 0 else self.overlap_direction(other)
                close.append((distance, other.unique_id, away))
        if not close:
            return None
        # A symmetric sum has no direction. Escape from the nearest fish;
        # agent ID breaks equal-distance ties without drawing random numbers.
        nearest = min(close, key=lambda item: (item[0], item[1]))[2]
        return unit_vector(np.sum([item[2] for item in close], axis=0), nearest)

    def orientation(self, neighbors):
        """Sum headings in the middle zone; normalization happens after combining."""
        vector = np.zeros(2)
        for other, _, distance in neighbors:
            if self.model.repulsion_radius <= distance < self.model.orientation_radius:
                vector += other.direction
        return vector

    def attraction(self, neighbors):
        """Sum unit displacements in the outer zone."""
        vector = np.zeros(2)
        for _, displacement, distance in neighbors:
            if self.model.orientation_radius <= distance <= self.model.attraction_radius:
                vector += displacement / distance
        return vector

    def social_direction(self, neighbors):
        """Apply repulsion priority, otherwise combine the two raw social sums."""
        rules = self.model.enabled_rules
        if "repulsion" in rules:
            repel = self.repulsion(neighbors)
            if repel is not None:
                return repel
        social = np.zeros(2)
        if "orientation" in rules:
            social += self.orientation(neighbors)
        if "attraction" in rules:
            social += self.attraction(neighbors)
        return unit_vector(social, self.direction)

    def decide(self):
        """Plan without mutating any current position, heading or speed."""
        direction = self.social_direction(self.get_neighbors())
        position = self.position + direction * self.speed * self.model.dt
        self.next_position, self.next_direction = reflect(position, direction, self.model.bounds)

    def advance(self):
        """Commit the state computed while all fish still had their old state."""
        self.position = self.next_position.copy()
        self.direction = self.next_direction.copy()


class GoldenShinersModel(mesa.Model):
    """Three-zone social dynamics with an observer-only DataCollector."""

    def __init__(
        self, width=20, height=20, speed=1.0, n_fish=20, seed=None, *,
        dt=0.125, repulsion_radius=0.5, orientation_radius=3.0,
        attraction_radius=5.5,
        enabled_rules=("repulsion", "orientation", "attraction"),
    ):
        if isinstance(n_fish, bool) or not isinstance(n_fish, (int, np.integer)) or n_fish < 1:
            raise ValueError("n_fish must be a positive integer.")
        if not all(np.isfinite([width, height, speed, dt, repulsion_radius, orientation_radius, attraction_radius])):
            raise ValueError("Model parameters must be finite.")
        if width <= 0 or height <= 0 or speed < 0 or dt <= 0:
            raise ValueError("Width, height and dt must be positive; speed must be nonnegative.")
        if not 0 < repulsion_radius < orientation_radius <= attraction_radius:
            raise ValueError("Radii must satisfy 0 < repulsion < orientation <= attraction.")
        self.enabled_rules = frozenset(enabled_rules)
        if not self.enabled_rules <= SOCIAL_RULES:
            raise ValueError("Unknown social rule in enabled_rules.")
        super().__init__(seed=seed)
        self.initial_seed = seed
        self.bounds = np.array([[0, width], [0, height]], dtype=float)
        self.dt = float(dt)
        self.repulsion_radius = float(repulsion_radius)
        self.orientation_radius = float(orientation_radius)
        self.attraction_radius = float(attraction_radius)
        self.space = ContinuousSpace(self.bounds, torus=False, random=self.random, n_agents=n_fish)
        for _ in range(n_fish):
            position = self.rng.random(2) * np.array([width, height])
            GoldenShiners(self, self.space, position=position, speed=speed)
        self.metrics = compute_group_metrics(self)
        self.datacollector = DataCollector(
            model_reporters={
                name: lambda model, key=name: model.metrics[key] for name in self.metrics
            },
            agent_reporters={
                "X": lambda fish: fish.position[0], "Y": lambda fish: fish.position[1],
                "DirX": lambda fish: fish.direction[0], "DirY": lambda fish: fish.direction[1],
                "Speed": "speed",
            },
        )
        self.datacollector.collect(self)

    def record_state(self):
        self.metrics = compute_group_metrics(self)
        self.datacollector.collect(self)

    def step(self):
        self.agents.do("decide")
        self.agents.do("advance")
        self.record_state()
