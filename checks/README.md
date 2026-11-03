# Social-model checks before adding light

Use Python 3.11 and install the tested dependencies with `python -m pip install -r checks/requirements.txt` from the repository root. Select that environment as the notebook kernel, then use **Restart Kernel → Run All**. Each notebook works independently and contains executed outputs, assertions, the reason for its checks, and an interpretation of the observed results. They all import the same [model implementation](../shiner_model.py); no model classes are copied between notebooks.

The six-step validation sequence is listed below. Start with the integration notebook at the repository root, then run checks 02–06 in order. PyVista and light-dependent speed remain later steps.

| Plan point | Notebook | What it establishes |
|---|---|---|
| 1 | [DataCollector integration](../data_collector.ipynb) | Twenty-one controlled checks cover the three rules, rule priority, overlaps, synchronous planning, recording after movement, and reflecting walls. The final Markdown explains the checks. |
| 2 | [Recording integrity](02_recording_integrity.ipynb) | Genuine step 0, all 100 updates, 101 group records, 2020 fish records, matching snapshots, unchanged history, and observation-independent movement. |
| 3 | [Metric validation](03_metric_validation.ipynb) | Sixty-two known-answer comparisons cover alignment, clockwise/counterclockwise rotation, compactness, nearest neighbours, geometric invariances and degenerate cases. |
| 4 | [Schooling across seeds](04_schooling_across_seeds.ipynb) | Ten seeds and four paired rule conditions distinguish social effects from walls and the initial configuration. |
| 5 | [Collective-state summaries](05_collective_state_summary.ipynb) | Exact label definitions, threshold equality, occupancy, sensitivity and independence of behaviour from the label. |
| 6 | [Diagnostic plots](06_diagnostic_plots.ipynb) | Four metric time series, polarization–rotation trajectories and initial/final positions. The figures are also saved in [figures](figures/). |

## Changes to the model

The code is a deterministic, constant-speed baseline. `decide()` calculates a future state from current neighbours; `advance()` commits that state. Both methods are short. Maintaining the two phases avoids order-dependent movement without requiring a separate copy of the whole world.

Exactly coincident fish no longer get silently skipped. Pairwise escape headings reverse sign when the fish are exchanged. Identical headings use opposite perpendiculars, with agent IDs resolving the tie. This numerical convention uses no random draw or position teleportation. A cancelling repulsion sum also retains priority, with the nearest neighbour supplying a deterministic escape heading.

Orientation and attraction now combine their **raw** vector sums before normalization. The earlier implementation normalized each zone separately. A cancelling combined social vector retains the current heading. These two changes align the regular social-vector calculation with Couzin and the Puckett supplement, and can change earlier trajectories. The overlap/tie conventions are implementation decisions rather than fitted fish behaviour.

The model validates its inputs, handles multiple wall crossings, and shares one implementation across all checks. [check_support.py](check_support.py) contains only experiment fixtures and audit helpers. DataCollector remains an observer.

## Findings from the executed experiments

All execution, recording and known-answer checks passed. The multi-seed experiment ran 40 simulations: ten paired seeds, 500 updates each, with all rules, no orientation, no attraction, and no social rules. Comparisons use the last 100 records, steps 401–500.

| Late-window metric, mean across ten seeds | All rules | No social rules |
|---|---:|---:|
| Polarization | 0.8723 | 0.2165 |
| Rotation | 0.1461 | 0.1110 |
| Mean nearest-neighbour distance | 0.6484 | 2.5260 |
| Mean distance to centroid | 2.2619 | 7.3814 |

The full model has higher polarization in all ten paired comparisons and a smaller mean group radius in nine. This supports a social contribution to alignment and aggregation in this setup.

**Reliable whole-group schooling is not established for every seed.** Seed 0 has late-window mean polarization 0.4564 and mean group radius 9.8646, while several other seeds have a radius close to 1.1. At the final timestep, a distance graph with links inside the 5.5-BL social range confirms two disconnected components of 10 + 10 fish for seed 0 and 19 + 1 for seed 2; the other eight seeds have one component of 20. Small nearest-neighbour distance can coexist with large whole-group spread and disconnected subgroups. The results therefore require local spacing, global spread and connectivity, not a single average or an attractive trajectory.

The labels are descriptive. Their 0.35/0.65 boundaries come from experimental state separation, not universal constants. Reclassifying the same 5010 records with 0.25/0.75 changes 11.84% of labels; using 0.40/0.60 changes 5.33%. Consecutive records are correlated, and these checks use raw per-update order parameters rather than the experimental temporal smoothing. Prepared circular cases validate the rotation formula; they do not prove that the social dynamics generate stable milling.

## Decisions before light-dependent speed

1. Investigate the dispersed seed and repeat the multi-seed checks after each justified modelling change. Check social connectivity and arena/density effects before choosing a preferred trajectory or tuning parameters.
2. Decide how closely to follow the Puckett model: the current baseline has **360° perception, instantaneous turns and no social noise**. Its supplement instead specifies 270° perception, a maximum turn of 1.75 radians **per update** (about 100°), and angular error 0.01 radians. The units differ from the turn-rate convention in the original Couzin paper.
3. Check numerical resolution at the future maximum speed. At 5 BL/s and `dt=0.125`, a fish travels 0.625 BL per update, exceeding the 0.5-BL repulsion radius. Defined exact-overlap behaviour and correct wall reflection do not prevent fish from crossing between samples. Timestep/substep and crossing tests are needed, including consistent scaling of turn/noise parameters.
4. Keep explicit orientation matching as a model choice and retain the no-orientation comparison. Katz reports alignment emerging without clear evidence for explicit body-orientation matching in real shiners.
5. Add scalar local light-dependent speed only after deciding these issues. Keep the gradient direction unavailable to the fish in the shiner collective-sensing baseline, and compare future results against these constant-speed controls.

## References and their roles

- [Couzin et al. (2002), *Collective memory and spatial sorting in animal groups*](https://doi.org/10.1006/jtbi.2002.3065): local zones, repulsion priority, social-vector combination and synchronous decisions.
- [Berdahl et al. (2013), *Emergent sensing of complex environments by mobile animal groups*](https://doi.org/10.1126/science.1225883): collective sensing through scalar local environmental responses and social interactions.
- [Puckett et al. (2018), *Collective gradient sensing in fish schools*](https://doi.org/10.1038/s41598-018-26037-9): shiner-model parameters and the later light-speed mechanism. Its [official supplement](https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-018-26037-9/MediaObjects/41598_2018_26037_MOESM1_ESM.pdf), gives the social equations and Table S1 units. The checks use body-length units, with 5 cm per body length in that table.
- [Katz et al. (2011), *Inferring the structure and dynamics of interactions in schooling fish*](https://doi.org/10.1073/pnas.1107583108): empirical motivation for speed-regulation and no-explicit-alignment comparisons.
- [Tunstrøm et al. (2013), *Collective States, Multistability and Transitional Behavior in Schooling Fish*](https://doi.org/10.1371/journal.pcbi.1002915): polarization, rotation and exploratory state regions; supplementary Figure S3 considers threshold sensitivity.
- [Hein et al. (2015), *The evolution of distributed sensing and collective computation in animal populations*](https://doi.org/10.7554/eLife.10955): conceptual support and a different force/acceleration model for future comparison.

Execution environment: Python 3.11.16, Mesa 3.2.0 and NumPy 2.4.6 in `mesa-env`. The suite validates this implementation and its stated operating conditions; it does not calibrate biological parameters.
