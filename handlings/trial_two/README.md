# Trial Two — Assembly, checkpoints and light-readiness testing

[Trial One](../trial_one/README.md) suggested that problematic seeds might need more time to assemble rather than being permanently fragmented. This trial tested that hypothesis while separating assembly, experimental pairing and numerical resolution. These are executed results from preserved notebooks; reorganization added no experiments.

## What we tested

| Notebook | Executed work |
|---|---|
| [01 — Long-horizon assembly](01_long_horizon_assembly.ipynb) | 30 random-start reference seeds, 180 s; assembly and stability monitored every internal update. |
| [02 — Timestep refinement](02_timestep_refinement.ipynb) | 45 matched cases: five seeds × speeds 1/3/5 BL/s × dt 0.0625/0.03125/0.015625 s, each lasting 31.25 s; separate recording checks. |
| [03 — Assembly definition](03_assembly_definition.ipynb) | Reanalyse three persistence definitions using the saved cohort. |
| [04 — Assembled checkpoints](04_assembled_checkpoints.ipynb) | Validate 30 exact restores, original continuations and paired control branches. |
| [05 — Candidate solutions](05_candidate_solutions.ipynb) | Compare complementary approaches and run 40 held-out reference/noise cases. |
| [06 — Light-readiness decision](06_light_readiness_decision.ipynb) | Combine evidence and report which readiness gates passed. |

The study uses the [shared model](../../shiner_model.py), with streamed observers and checkpoint helpers in [study_support.py](study_support.py). Results and reproducibility caches are in [data/](data/), and plots in [figures/](figures/). There were **115 full scientific runs**: 30 assembly + 45 timestep + 40 held-out runs. Four recording-validation model runs and 90 checkpoint continuation branches are counted separately.

## Executed results

### Longer observation resolved the reference assembly concern

All **30/30 reference runs** achieved persistent assembly within **180 s** at speed 1 BL/s and dt = 0.125 s. Three started connected; all **27/27 initially disconnected** populations assembled. There were **0 censored runs** and **0 observed post-confirmation breakups** in this cohort.

Assembly onset had median **28.5 s**, IQR **13.1875–55.125 s**, and range **0–86.75 s**. Seed 0 assembled at **86.75 s** and seed 2 at **73.875 s**, with confirmation at 91.75 s and 78.875 s. The old 62.5-s horizon had censored these eventual successes. Extending it added six confirmed successes in the 30-seed cohort.

Post-confirmation follow-up ranged from **88.25 to 175 s** without breakup. This supports stability over the tested follow-up, not permanent assembly or a universal 100% success rate.

### Persistent assembly has an explicit operational definition

The adopted definition is **one connected component continuously for at least 5 simulated seconds**, monitored at every internal update. It is a project convention, not a biological constant.

Definitions A (one component for 2.5 s) and B (one component for 5 s) gave the same success and onset results, with confirmation 2.5 s apart. Definition C (largest-group fraction ≥0.95 for 5 s) could accept **19 + 1**, advanced onset in five seeds, and gave median onset **17.625 s** rather than 28.5 s. It therefore did not represent whole-population assembly.

`AssemblyTime` is the onset of the first episode that later satisfies persistence. Confirmation follows the full qualifying interval; checkpoints are captured then. Insufficient qualifying follow-up is right-censoring, not evidence that assembly is impossible. See [03_assembly_definition.json](data/03_assembly_definition.json).

### Checkpoint saving and restoration were validated

All **30 assembled checkpoints** restored state, parameters and both RNG states exactly, reproduced the next **16 original continuation steps**, and produced identical paired **64-step controls**. Saved information includes positions, headings, speeds, IDs, seed, parameters, absolute step/time and RNG states. See [04_checkpoint_findings.json](data/04_checkpoint_findings.json).

This validated the future experimental design:

**random initialization → emergent assembly → save checkpoint → branch the identical state into control and light conditions.**

The files in [assembled_checkpoints/](data/assembled_checkpoints/) belong to the **old temporal protocol: dt = 0.125 s, speed 1 BL/s**. They are preserved evidence, **not final light checkpoints**. A changed timestep or turning formulation requires new assembly validation and regenerated official states. State restoration does not reconstruct earlier DataCollector history; future branches must retain assembly metadata and define their own time origin.

### Recording cadence was independent of internal dynamics

At internal dt = 0.03125 s, recording every four updates gave a **0.125-s output interval**. Full and sparse recording produced bitwise identical internal states and matching retained group/fish records, including noisy controls and RNG states. Event monitoring still used every update. Saving fewer rows reduced storage; it did not improve physical resolution. See [recording validation](data/02_recording_stride_validation.json).

### Temporal resolution remained unresolved

The candidate **dt = 0.03125 s** did not behave sufficiently similarly to **0.015625 s** across speeds 1–5 BL/s under the declared practical criteria. At speed 1, MeanNND changed **24.85%** and paired group spread **24.79%**. At speed 3 all four metric criteria failed. At speed 5, polarization changed only **0.25%**, but ensemble group spread changed **17.49%** and paired spread **30.35%**. Similar polarization alone was insufficient.

At speed 5, missed repulsion passes fell from **0.0896 to 0.0192/model/s** (14 to 3 events across five 31.25-s runs). The finest missed separation was about **0.4984 BL**, near the 0.5-BL cutoff. These were geometric missed-zone encounters, not demonstrated body collisions. No exact sampled overlaps were observed. The finest dt was a comparison reference, not an established limit.

The screen used project thresholds for ensemble and matched-seed changes: ≤10% for polarization, MeanNND and group spread; ≤0.05 absolute largest-group-fraction change; and missed passes ≤0.01/model/s. It was not a formal convergence theorem. With instantaneous turning, refining dt also changed behavioural decision frequency. See [02_timestep_readiness.json](data/02_timestep_readiness.json).

### The apparent noise benefit did not replicate

Held-out seeds **30–49** gave **20/20 assembly for the deterministic reference** and **19/20 with angular noise** by 180 s. Noisy seed 48 was censored with final components **14 + 6**; noisy seed 36 had one post-assembly breakup. Mean restricted confirmation time was **39.88 s** for reference and **45.76 s** for noise.

This sample did not justify adopting noise, although it did not establish a universal harmful effect. Longer observation addressed assembly censoring, checkpoint pairing addressed experimental comparability, and timestep refinement addressed temporal adequacy; these solved different problems. See [held-out noise findings](data/05_noise_holdout_findings.json).

## Interpretation and decision after Trial Two

| Question | Decision |
|---|---|
| Can random groups assemble? | **Resolved for the tested protocol:** 30/30 by 180 s, without observed post-confirmation breakup. |
| Can assembled states be saved and branched reproducibly? | **Validated:** exact state/RNG restoration and matching continuations. |
| Is the temporal protocol adequate over speeds 1–5 BL/s? | **Unresolved:** finer updates still changed key metrics. |

**Status after this trial: NOT READY FOR LIGHT.** Keep the deterministic reference; do not transfer its assembly results or checkpoints automatically to another temporal formulation. [Trial Three](../trial_three/README.md) investigated further refinement and bounded turning. The current unimplemented proposal is in [NEXT_SOLUTION.md](../NEXT_SOLUTION.md).

The verdict is saved in [06_light_readiness_decision.json](data/06_light_readiness_decision.json). The [documentation before reorganization](data/documentation_before_reorganization.txt) retains the earlier text with its original-location links. All notebook outputs, CSVs, JSONs, figures, checkpoint candidates, validated checkpoints and caches remain preserved.

[Back to the handling overview](../README.md).
