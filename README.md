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

Use Python 3.11 and install the tested validation dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r checks/requirements.txt
```

Open `data_collector.ipynb` in VS Code or Jupyter, select that environment as the kernel, and use **Restart Kernel → Run All**. Then run checks 02–06 in order. Each notebook can also run independently from the repository root or `checks/`. These are constant-speed social-model checks before adding light-dependent speed.

### Current findings

In `04_schooling_across_seeds.ipynb`, we found that the social model does not always produce one connected school. In seed 0, the group ended as two disconnected groups of 10 + 10 fish, while seed 2 ended as 19 + 1. This also showed that a low mean nearest-neighbour distance is not enough to guarantee whole-group cohesion, because fish can be close to neighbours inside separate subgroups.

Our main hypothesis is that this fragmentation could either be a meaningful emergent result of local social interactions, or an artefact caused by modelling and numerical choices such as wall interactions, timestep size, 360° perception, instantaneous turning, or the absence of social noise.

For this reason, before adding light, we created the `fragmentation_issue_handling` folder. There we test connectivity explicitly, diagnose the problematic seeds, check wall effects, test timestep sensitivity at the future maximum speed, evaluate perception/turning/noise assumptions, and finally choose a justified social baseline.
