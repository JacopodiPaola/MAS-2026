# Fragmentation investigation before light

## Purpose and competing explanations

The first [validation stage](../checks/README.md) established that the local social rules, synchronous updates and DataCollector execute together, recording and metrics pass their known-answer checks, and social interaction changes alignment and aggregation. It did not establish reliable whole-group cohesion: final components were 10 + 10 for seed 0 and 19 + 1 for seed 2, versus one group for eight other seeds.

Mean nearest-neighbour distance measures local spacing. Two separated compact subgroups can have the same MeanNND as one group, so that measurement alone cannot establish cohesion. We need to understand this before interpreting accumulation or movement in a light environment.

**Hypothesis A — emergent non-assembly or fragmentation.** Finite-range local interactions may leave subgroups outside the attraction range, without a mechanism to reunite them. Initial geometry and subgroup trajectories can matter even when the implementation is correct.

**Hypothesis B — model or numerical artefact.** Wall reflections, arena geometry, decision frequency, unresolved interaction-zone crossings, instantaneous turns, perception and missing angular noise may change assembly or fragmentation. These explanations need not be mutually exclusive.

The experiments distinguish these possibilities without adding light, replacing the 2D model, moving fish toward a global centroid, or tuning for visually attractive trajectories. The original default configuration is retained as a control.

## Implementation and reproducibility

All notebooks use the existing shared [shiner_model.py](../shiner_model.py). Optional FOV, social-turn limits and angular error were added there; no model classes are copied into this folder. Default trajectories remain exactly equal to the previous implementation for seeds 0, 1 and 2 over 500 updates. Connectivity and wall diagnostics are computed from completed DataCollector records by [diagnostics.py](diagnostics.py), without changing fish states or random-generator state.

Use the `mesa-env` kernel, or the equivalent environment documented in the original checks, and **Restart Kernel → Run All**. Run notebooks 01–05 before 06: the selection notebook reads their saved CSV evidence. The figures are in [figures/](figures/) and the reusable evidence and recommendation are in [data/](data/).

| Notebook | Question and controlled experiment |
|---|---|
| [01 — Connectivity](01_connectivity_fragmentation.ipynb) | Ten baseline seeds; known 20, 10+10 and 19+1 graphs; connectivity compared with spacing and directional order. |
| [02 — Seed diagnosis](02_seed_diagnostics.ipynb) | Seeds 0 and 2 versus connected seed 1; episodes, initial/event/final positions, component sizes and centroids. |
| [03 — Walls](03_wall_effects.ipynb) | The same three seeds in 20×20 and translated 40×40 arenas, preserving initial local geometry and headings. |
| [04 — Timestep](04_timestep_sensitivity.ipynb) | Five matched seeds × two speeds × three timesteps, always over 31.25 simulated seconds; plus a controlled crossing probe. |
| [05 — Social assumptions](05_social_parameter_extensions.ipynb) | Ten matched seeds for baseline, FOV only, turning only, noise only, and then the combined setting: 50 runs over 62.5 s each. |
| [06 — Baseline selection](06_baseline_selection.ipynb) | Evidence-based comparison and explicit readiness criteria, without fitting a new condition. |

### Diagnostic conventions

- A geometric edge exists at distance ≤ 5.5 BL. We record number of groups, largest size/fraction, second-largest size and component sizes. This is an undirected distance graph; under restricted FOV it measures potential geometric connectivity, not directed information flow.
- A persistent disconnected episode lasts at least **2.5 s**. This is a diagnostic convention, not a biological constant. Each post-update label represents the preceding timestep interval; t=0 is not assigned a duration. The first observed split brackets onset within the preceding interval. Initial disconnection and right-censored episodes are reported explicitly.
- A **missed repulsion pass** occurs when a straight relative path enters the 0.5-BL zone although both sampled endpoints lie outside it. Reflected pair paths are excluded because a single line segment would misrepresent them. This detects unsampled zone encounters, not fish-body collisions. Exact sampled overlap is recorded separately.
- The selection screen requires late largest-group fraction ≥0.95 and late connected-time fraction ≥0.90 in at least 9/10 seeds. These are explicit study conventions, not paper-derived constants. Passing cohesion criteria would still require acceptable numerical resolution.

## Results from executed notebooks

### 1. The original issue is mainly failure to assemble

Seed 0 starts **18+2** and ends **10+10**. Seed 2 starts **19+1** and ends **19+1**. Neither forms a connected whole during the observed **62.5 s**. Seed 1 is connected throughout. The other seven seeds first assemble after **7.625–56 s**.

Across all ten baseline seeds, no fragmented record occurs after first whole-group cohesion. Thus the two problematic final frames are not evidence of a previously connected whole school breaking apart. Seed 0 still changes subgroup composition, so this global diagnosis does not exclude fission or merging among subgroups. Component lineage tracking would be needed for that finer question.

Known artificial configurations demonstrate the limitation of MeanNND directly: one group and two separated groups can both have MeanNND **0.2 BL**, while largest-group fractions are 1 and 0.5. Connectivity instrumentation preserves the original baseline records exactly.

### 2. Walls influence trajectories but do not explain the initial disconnection

Translating the same initial geometry into a 40×40 arena reduces reflected-fish steps per second:

| Seed | 20×20 | 40×40 | Final components, small → large arena |
|---|---:|---:|---|
| 0 | 9.680 | 3.648 | 10+10 → 10+10 |
| 2 | 2.112 | 0.784 | 19+1 → 15+5 |
| 1 | 1.408 | 0.784 | 20 → 20 |

Seeds 0 and 2 remain disconnected throughout both experiments. Their initial disconnection precedes any simulated reflection; there is no observed connected-to-fragmented onset to attribute to a wall impact. Outcomes can still depend on wall and arena context. The larger arena changes available travel space and nominal density, and the intervention tests only three seeds. It is not proof that walls never cause fragmentation.

### 3. The future speed exposes a resolution problem

All 30 timestep runs use the same **31.25 s**, with speeds 1 and 5 BL/s and dt = 0.125, 0.0625 and 0.03125 s. At 5 BL/s:

| dt (s) | Travel/update (BL) | Mean missed passes/s | Mean late polarization |
|---:|---:|---:|---:|
| 0.125 | 0.6250 | 11.4048 | 0.4760 |
| 0.0625 | 0.3125 | 1.0368 | 0.7854 |
| 0.03125 | 0.15625 | 0.0896 | 0.9447 |

No exact overlaps were recorded, yet a controlled head-on probe crosses the entire repulsion encounter at the coarsest timestep. Finer updates observe the close encounter. Zero endpoint overlap therefore does not establish adequate interaction resolution.

The finest step reduces missed passes substantially but does not eliminate them or demonstrate timestep independence. Connectivity and order also change with dt at speed 1. Because the baseline updates instantaneous social decisions more frequently as dt decreases, this is sensitivity of the implemented model, not a formal ODE-convergence test. Cohesion alone is especially misleading here: coarser high-speed runs can look more connected while missing far more interactions.

### 4. Literature-inspired settings do not uniformly improve cohesion

These 62.5-s runs use the same ten seeds and change one setting at a time before testing the combination:

| Condition | Mean late largest-group fraction | Final connected seeds | Seeds meeting the full late-cohesion screen |
|---|---:|---:|---:|
| Baseline | 0.93090 | 8/10 | 7/10 |
| FOV only | 0.88395 | 7/10 | 5/10 |
| Turning only | 0.88500 | 7/10 | 7/10 |
| Noise only | 0.94410 | 9/10 | 8/10 |
| Combined | 0.88000 | 7/10 | 7/10 |

Angular noise modestly improves these aggregate measures. The combined setting reconnects seeds 0 and 2 by the final frame but creates other failures. Choosing a configuration using only those two seeds would overfit the diagnosis. No tested condition meets the study's full 9/10 late-cohesion screen.

The tested FOV is 270° for orientation and attraction, with close repulsion kept omnidirectional following the chosen Couzin convention. The turn limit is **1.75 rad/update at dt=0.125**, represented as a derived rate of 14 rad/s for controlled timestep scaling. Angular error is 0.01 rad at that reference timestep, scaled as sqrt(dt/0.125) to preserve variance per physical time. These off-reference scaling rules and the separation of hard wall reflection from social turning are explicit implementation choices. Controlled visibility, turn, noise and repeatability checks passed.

## Interpretation and recommendation

The evidence is consistent with **finite-range interactions allowing persistent non-assembly**, while also showing strong sensitivity to numerical and modelling assumptions. It does not establish a single exclusive emergent-versus-artefact explanation, biological validity, a stationary fragmentation frequency or behaviour beyond the tested horizons. Global components also do not track subgroup identities.

**Retain the unchanged speed-1, dt=0.125, 360°, instantaneous-turn, zero-noise configuration as the reference control. Do not promote a light-ready baseline yet.** This preserves comparison with the validated first stage rather than silently selecting the nicest outcome. The finer dt=0.03125 is a refinement candidate, not a demonstrated converged solution.

Before light, test further timestep refinement and a chosen social configuration jointly over the future speed range, scaling turn/noise consistently. Include more initial states or held-out seeds and investigate why disconnected subgroups do or do not meet. A model may legitimately allow occasional disconnected groups; that should be a documented result rather than removed by a global cohesion force.

All six study notebooks were executed in fresh kernels with saved outputs. Numerical execution and boundedness checks passed; whole-group assembly and timestep robustness remain unresolved. **No light field, gradient information or light-dependent speed rule was implemented.** The recommendation is saved in [06_recommendation.json](data/06_recommendation.json); the study stops here for review.

## References

- [Couzin et al. (2002)](https://doi.org/10.1006/jtbi.2002.3065): social zones, local interactions, repulsion priority and the chosen perception convention.
- [Puckett et al. (2018)](https://doi.org/10.1038/s41598-018-26037-9) and its [supplement](https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-018-26037-9/MediaObjects/41598_2018_26037_MOESM1_ESM.pdf): radii, reference timestep, 270° FOV, 1.75-rad/update turn limit and 0.01-rad social error. These tests are not a full paper replication.
- [Tunstrøm et al. (2013)](https://doi.org/10.1371/journal.pcbi.1002915): polarization, rotation and collective-state interpretation; geometric cohesion needs additional measurements.
- [Katz et al. (2011)](https://doi.org/10.1073/pnas.1107583108): empirical interaction structure and the reason to keep explicit alignment as a modelling assumption.
- [Berdahl et al. (2013)](https://doi.org/10.1126/science.1225883): the later local scalar-light response, not a mechanism added in this study.
- [Hein et al. (2015)](https://doi.org/10.7554/eLife.10955): conceptual support and a possible future alternative, not a replacement of the current model.
