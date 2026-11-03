# MAS-2026

Golden-shiner collective light sensing, with planar swimming displayed in a 3D PyVista scene.

The agreed starting mechanism is local light-dependent swimming speed combined with social interactions. Individuals do not directly estimate the environmental gradient or exchange brightness readings in this baseline.

Doruk is working on visualization; Maria is working on the Couzin interaction logic. Their contributions will form the new implementation.

## Historical reference files

The previous project's files are preserved in [`past_repo/`](past_repo/README.md). They are reading and comparison material, not the new implementation. The archive guide explains which ideas may be reused, what needs adapting, and the limitations of the old experiments.

Keep new implementation files outside `past_repo/`. The historical dependencies and instructions apply to the old project only.

## Checks

Before adding light and implementing the visualization, we must ensure that the DataCollector and social local interaction rules work appropriately. Inside the `checks` folder, each notebook tests a different possible issue.

In `04_schooling_across_seeds.ipynb`, we found that the social model does not always produce one connected school. In seed 0, the group ended as two disconnected groups of 10 + 10 fish, while seed 2 ended as 19 + 1. This also showed that a low mean nearest-neighbour distance is not enough to guarantee whole-group cohesion, because fish can be close to neighbours inside separate subgroups.

Our main hypothesis is that this fragmentation could either be a meaningful emergent result of local social interactions, or an artefact caused by modelling and numerical choices such as wall interactions, timestep size, 360° perception, instantaneous turning, or the absence of social noise.

For this reason, before adding light, we created the `fragmentation_issue_handling` folder. There we test connectivity explicitly, diagnose the problematic seeds, check wall effects, test timestep sensitivity at the future maximum speed, evaluate perception/turning/noise assumptions, and finally choose a justified social baseline.
