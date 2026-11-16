# MAS-2026

Golden-shiner collective light sensing, with planar swimming displayed in a 3D PyVista scene.

The agreed starting mechanism is local light-dependent swimming speed combined with social interactions. Individuals do not directly estimate the environmental gradient or exchange brightness readings in this baseline.

Doruk is working on visualization; Maria is working on the Couzin interaction logic. Their contributions will form the new implementation.

## Historical reference files

The previous project's files are preserved in [`past_repo/`](past_repo/README.md). They are reading and comparison material, not the new implementation. The archive guide explains which ideas may be reused, what needs adapting, and the limitations of the old experiments.

Keep new implementation files outside `past_repo/`. The historical dependencies and instructions apply to the old project only.

## Checks

Before adding light and implementing the visualization, we must ensure that the DataCollector and social local interaction rules work appropriately. Inside the `checks` folder, each notebook tests a different possible issue.

### Validation notebooks and setup

- [`data_collector.ipynb`](data_collector.ipynb): integration of repulsion, orientation, attraction, synchronous updates and data collection, including the point-1 checks and explanations.
- [`shiner_model.py`](shiner_model.py): the shared model used by every validation notebook.
- [`checks/README.md`](checks/README.md): the index for checks 02–07, with recording tests, metric validation, multiple seeds and controls, collective-state summaries, diagnostic plots, the decision-rate check, results and references.

### Handling issues

The early 62.5-s checks ended with disconnected groups in seeds 0 and 2. Longer tests showed that these groups needed more time: **30/30 reference runs assembled within 180 s**, with no observed breakup after assembly was confirmed. Low nearest-neighbour distance alone does not establish whole-group cohesion.

The complete history is organized in [handlings/README.md](handlings/README.md):

- **Trial One:** diagnosed connectivity, walls, timestep sensitivity and social parameters.
- **Trial Two:** validated longer-horizon assembly and checkpoint restoration; held-out noise did not improve assembly.
- **Trial Three:** neither timestep refinement nor bounded turning achieved temporal stability across speeds 1–5 BL/s.

**The timestep issue is resolved.** One timestep controls both movement and social decision frequency, and that is intended: `dt = 0.125 s` is the fish's decision interval (8 decisions per second, Puckett et al. 2018, SI Table S1), so it is fixed rather than refined. Moving in sub-steps between decisions gives the same trajectories, so the two-clock proposal in NEXT_SOLUTION.md is not needed. See [handlings/DECISION_RATE.md](handlings/DECISION_RATE.md) and [check 07](checks/07_decision_rate.ipynb). The 16 trial notebooks retain their saved outputs, data and figures. Trial Two checkpoints were made with this same protocol and can be used as starting states for the light experiments.

The shared model and check helpers include the already tested optional controls used in those completed trials; the original checks retain their default configuration. No new scientific runs were performed during this reorganization.
