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
- [`checks/README.md`](checks/README.md): the index for checks 02–06, with recording tests, metric validation, multiple seeds and controls, collective-state summaries, diagnostic plots, results and references.

### Current findings

The early 62.5-s checks ended with disconnected groups in seeds 0 and 2. Longer tests showed that these groups needed more time: **30/30 reference runs assembled within 180 s**, with no observed breakup after assembly was confirmed. Low nearest-neighbour distance alone does not establish whole-group cohesion.

The complete history is organized in [handlings/README.md](handlings/README.md):

- **Trial One:** diagnosed connectivity, walls, timestep sensitivity and social parameters.
- **Trial Two:** validated longer-horizon assembly and checkpoint restoration; held-out noise did not improve assembly.
- **Trial Three:** neither timestep refinement nor bounded turning achieved temporal stability across speeds 1–5 BL/s.

The remaining issue is that one timestep controls both movement and social decision frequency.NEXT_SOLUTION.md proposes separate behavioural and physics timesteps; this proposal has not been implemented. The 16 trial notebooks retain their saved outputs, data and figures. Trial Two checkpoints belong to the previous protocol and are not final light checkpoints.

The shared model and check helpers include the already tested optional controls used in those completed trials; the original checks retain their default configuration. No new scientific runs were performed during this reorganization.
