# Trial One — Initial fragmentation and model diagnosis

This trial asked why some random-start simulations did not produce one globally connected school. It was the first systematic diagnosis, before the longer assembly study in [Trial Two](../trial_two/README.md). The notebooks and evidence are preserved; this reorganization added no experiments or model changes.

## Initial problem

The original checks showed that local social rules increased order and local aggregation, but some seeds still ended in separate groups. During the **62.5-s** reference runs, seed 0 ended **10 + 10** and seed 2 ended **19 + 1**. This initially suggested a fragmentation or cohesion problem.

The [shared model](../../shiner_model.py) uses local repulsion, orientation and attraction, repulsion priority, synchronous decide/advance, and reflecting walls. The reference was 20 fish in a 20 × 20 BL arena, speed **1 BL/s**, **dt = 0.125 s**, radii **0.5 / 3.0 / 5.5 BL**, 360° perception, instantaneous social turning and zero angular noise. Connectivity uses distance-based edges at the attraction radius; it is an observer rather than an extra cohesion force.

## What we tested

| Notebook | Question |
|---|---|
| [01 — Connectivity and fragmentation](01_connectivity_fragmentation.ipynb) | Can component counts distinguish one school from compact disconnected subgroups? |
| [02 — Seed diagnostics](02_seed_diagnostics.ipynb) | When do seeds 0 and 2 become disconnected, and do they ever assemble? |
| [03 — Wall effects](03_wall_effects.ipynb) | Does translating the same initial geometry into a larger arena change the result? |
| [04 — Timestep sensitivity](04_timestep_sensitivity.ipynb) | Do coarse updates miss repulsion-zone encounters or change group metrics? |
| [05 — Social parameter extensions](05_social_parameter_extensions.ipynb) | Do FOV, turning limits, angular noise or their combination improve results consistently? |
| [06 — Baseline selection](06_baseline_selection.ipynb) | Which conclusions and reference settings are justified? |

Observer and experiment helpers are in [diagnostics.py](diagnostics.py), results in [data/](data/), and plots in [figures/](figures/).

## Executed results

### Local aggregation did not establish whole-group cohesion

Artificial configurations showed that one group and two separated groups could both have **MeanNND = 0.2 BL**, while largest-group fractions were 1 and 0.5. Nearest-neighbour distance therefore needed component counts, largest-group fraction, group spread and component sizes alongside it.

Seed 0 started **18 + 2** and ended **10 + 10**; seed 2 started and ended **19 + 1**. Neither formed one connected population within 62.5 s. Seed 1 was connected throughout, and the other seven seeds first connected after **7.625–56 s**. Across the ten reference seeds, no disconnected record occurred after first whole-group connection. This supported delayed or censored assembly rather than demonstrated breakup of an established whole school; it did not rule out subgroup exchanges before assembly.

### Walls influenced trajectories but did not explain disconnected starts

The same initial geometry was translated into a 40 × 40 BL arena for three seeds:

| Seed | Reflected-fish steps/s, 20 × 20 | Reflected-fish steps/s, 40 × 40 | Final components, small → large arena |
|---|---:|---:|---|
| 0 | 9.680 | 3.648 | 10 + 10 → 10 + 10 |
| 2 | 2.112 | 0.784 | 19 + 1 → 15 + 5 |
| 1 | 1.408 | 0.784 | 20 → 20 |

Seeds 0 and 2 were disconnected before any reflection and remained disconnected in both arenas. Walls affected later paths and membership, but did not explain initial disconnection. The intervention also changed available space and nominal density; three seeds cannot establish that walls never cause fragmentation.

### Timestep sensitivity became a numerical concern

The **30 matched runs** compared five seeds, speeds 1 and 5 BL/s, and dt = 0.125 / 0.0625 / 0.03125 s over the same **31.25 s**. At 5 BL/s:

| dt (s) | Travel/update (BL) | Mean missed repulsion passes/model/s | Mean late polarization |
|---:|---:|---:|---:|
| 0.125 | 0.6250 | 11.4048 | 0.4760 |
| 0.0625 | 0.3125 | 1.0368 | 0.7854 |
| 0.03125 | 0.15625 | 0.0896 | 0.9447 |

A controlled head-on probe crossed the repulsion encounter between coarse updates despite zero exact sampled overlaps. Zero endpoint overlap did not establish adequate encounter resolution. Finer updates reduced missed passes substantially, but did not demonstrate temporal stability. With instantaneous turning, decreasing dt also increased social decision frequency, so this was sensitivity of the implemented model rather than formal ODE convergence.

### Literature-inspired extensions did not improve all seeds

The **50 extension runs** used the same ten seeds for 62.5 s per condition:

| Condition | Mean late largest-group fraction | Final connected seeds | Seeds passing the full late-cohesion screen |
|---|---:|---:|---:|
| Deterministic reference | 0.93090 | 8/10 | 7/10 |
| FOV only | 0.88395 | 7/10 | 5/10 |
| Turning only | 0.88500 | 7/10 | 7/10 |
| Noise only | 0.94410 | 9/10 | 8/10 |
| Combined | 0.88000 | 7/10 | 7/10 |

The FOV test used 270° for orientation/attraction and omnidirectional close repulsion. The turning reference was 1.75 rad/update at dt = 0.125 s, represented by the project scaling convention **14 rad/s**. Reference angular noise was 0.01 rad, scaled with the square root of dt to preserve variance per physical time. These were explicit implementation choices. Controlled visibility, turning, noise and repeatability checks passed.

Noise looked promising in these ten seeds, but no condition passed the full 9/10 late-cohesion screen. The combined setting connected seeds 0 and 2 while introducing other failures. Selecting it using those two seeds would overfit the diagnosis.

## Interpretation and decision after Trial One

The question shifted from “why does an assembled school fragment?” to “how long do random groups need to assemble?” The 62.5-s horizon could censor eventual assembly. Connectivity and encounter diagnostics also showed that visual or local cohesion did not establish numerical adequacy.

The decision was to retain the deterministic reference and random initialization, avoid tuning parameters merely to force cohesion, and add no global cohesion mechanism. The next executed work was [Trial Two](../trial_two/README.md): extend the horizon, define persistent assembly, validate saved states, and refine timestep comparisons before light.

**Status after this trial: NOT READY FOR LIGHT.** See [06_recommendation.json](data/06_recommendation.json). Later temporal results are separate in [Trial Three](../trial_three/README.md); the current unimplemented proposal is in [NEXT_SOLUTION.md](../NEXT_SOLUTION.md).

## Preserved evidence and scope

All notebook outputs, CSV/JSON evidence and figures remain with this trial. The [documentation before reorganization](data/documentation_before_reorganization.txt) preserves the earlier combined narrative; historical paths refer to its previous layout. The earlier [Stage 1 README snapshot](data/stage1_README_snapshot.txt) is also retained.

Connectivity measures potential local interaction, not biological realism. These finite-seed, finite-horizon results establish neither permanent stability nor empirical calibration. Couzin-style zones and Puckett-inspired parameters motivate the model; thresholds, scaling conventions and acceptance decisions are project choices.

[Back to the handling overview](../README.md).
