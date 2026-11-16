# Pre-light model handling and validation

**Current status: the timestep issue is resolved by fixing the decision rate at 8 decisions per second** (`dt = 0.125 s`, Puckett et al. 2018, SI Table S1). See [DECISION_RATE.md](DECISION_RATE.md).

This folder preserves the debugging and validation history before adding a light field to the Golden Shiner model. Each trial addresses a specific uncertainty; parameters were not selected merely to produce visually cohesive schools. Notebooks retain executed outputs, with their data, figures and decisions beside them.

## Executed results

| Trial | Question | Main result | Status after the trial |
| --- | --- | --- | --- |
| [Trial One](trial_one/README.md) | Do social rules, walls or parameters explain apparent fragmentation? | The diagnosis shifted toward insufficient assembly time and timestep sensitivity. | Further testing required |
| [Trial Two](trial_two/README.md) | Do random groups assemble, and can their states be restored? | 30/30 assembled within 180 s; no post-confirmation breakup was observed; checkpoints were validated. | Assembly resolved for that protocol; timestep unresolved |
| [Trial Three](trial_three/README.md) | Do refinement or bounded turning resolve timestep sensitivity? | Neither formulation with one shared timestep met practical stability criteria across speeds 1–5 BL/s. | Temporal problem unresolved |
| [Decision rate](DECISION_RATE.md) | Is the timestep sensitivity a numerical error, and do sub-steps between decisions fix it? | `dt` is the decision interval (8 decisions/s, Puckett et al. SI Table S1), so changing it changes reaction time. Sub-steps give the same trajectories at 1 BL/s; at 3–5 BL/s they drift apart no faster than a 1e-12 nudge does ([check 07](../checks/07_decision_rate.ipynb)). | Timestep resolved: `dt = 0.125 s` fixed |

The controlled [checks](../checks/README.md) established that the local social rules work together. Random initialization remains part of the protocol. In Trial Two, all 27 initially disconnected populations assembled; three were connected initially. Persistent assembly means one connected component continuously for at least 5 s, an operational project definition. These finite observations do not establish universal assembly or stability.

Checkpoint restoration and RNG continuation worked. Deterministic behaviour remains the reference because social noise did not improve held-out assembly. Recording frequency can be separated from internal updates. No light field has been implemented.

## Interpretation and remaining uncertainty

> **Update:** this section describes the situation after Trial Three. [DECISION_RATE.md](DECISION_RATE.md) resolves it: `dt = 0.125 s` is the decision interval, so there is no separate numerical timestep to converge, and the Trial Two checkpoints were made with exactly this protocol.

A timestep-independent social-motion protocol, a final light-ready timestep, and checkpoints under that final protocol have **not** been established. Trial Two checkpoints remain evidence for their original protocol, not final light starting states.

The current timestep controls both movement resolution and social decision frequency. Refining it changes both, so the comparisons cannot isolate numerical motion resolution.

## Evidence preservation and setup

Use the tested environment in [checks/requirements.txt](../checks/requirements.txt). The notebooks locate the shared model from either the repository root or their trial folder. This reorganization changed paths and imports only; all 16 saved notebook outputs and the original data, figures, manifests and checkpoints were preserved. No new scientific runs were performed.

The [relocation registry](trial_one/data/relocation_provenance.json) records the original and relocated source hashes. Cache checks accept an original source identity only while the relocated file exactly matches its audited hash; later edits invalidate that alias. Original documentation is archived in each trial's `data/documentation_before_reorganization.txt`.

## Next step: light

Keep `shiner_model.py` frozen so the trials stay reproducible, and put light in a new module, for example `light_model.py`. A `LightField` gives a value `L(x, y, t)` between 0 (dark) and 1 (bright): a moving dark spot plus noise. Fish only read the value at their own position and are never given the gradient. At each decision, a fish sets its speed from its local light, `s = s_min + L * (s_max - s_min)`, with `s_min = 0.2` and `s_max = 5` BL/s (1 and 25 cm/s, Puckett Table S1); the social heading rules do not change. Trial Two's 30 assembled checkpoints were made with exactly this protocol (`dt = 0.125`, speed 1, deterministic, instantaneous turns), and the timestep gate was the only one that failed in [06_light_readiness_decision.json](trial_two/data/06_light_readiness_decision.json), so they can be used as starting states. See [DECISION_RATE.md](DECISION_RATE.md), sections 7 and 8.
