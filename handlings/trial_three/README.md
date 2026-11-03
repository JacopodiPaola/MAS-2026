# Trial Three — Temporal resolution and turning formulation

[Trial Two](../trial_two/README.md) established assembly and reproducible checkpoints for its reference protocol. This trial focused on the remaining timestep problem. It did not transfer those results to new protocols, change defaults, or introduce light. The executed outputs are preserved; reorganization added no simulations.

## Problem and hypotheses

The original model used the same dt for movement integration, neighbour sensing, social decisions and heading changes. Reducing dt therefore both refined movement and increased how often fish could react socially. The comparison did not isolate motion resolution from behavioural response frequency.

**Hypothesis A:** retain instantaneous turning and refine dt to **0.03125 / 0.015625 / 0.0078125 s**.

**Hypothesis B:** bound social turning by a physical angular rate and compare dt = **0.0625 / 0.03125 / 0.015625 / 0.0078125 s**. The reference increment of 1.75 rad/update at dt = 0.125 s was converted to **14 rad/s**, giving a per-update cap of **14 × dt**. This was an explicit project scaling convention, not a fitted biological rate. Hard-wall reflection remained a separate instantaneous response outside the social cap.

Both arms used ten matched seeds, speeds **1 / 3 / 5 BL/s**, equal **31.25-s** durations, 20 fish in a 20 × 20 BL arena, radii 0.5 / 3.0 / 5.5 BL, 360° FOV and zero angular noise. The bounded-turn option already existed in the [shared model](../../shiner_model.py); this trial validated and reused it.

## What we tested

| Notebook | Executed work |
|---|---|
| [01 — Instantaneous refinement](01_instantaneous_turn_dt_refinement.ipynb) | **90 fresh runs:** ten seeds × three speeds × three dt values. |
| [02 — Turn-rate implementation](02_turn_rate_implementation.ipynb) | **12 controlled checks:** clipping, wraparound, normalization, units, backwards compatibility, synchrony and recording independence. |
| [03 — Bounded-turn refinement](03_turn_rate_dt_convergence.ipynb) | **120 fresh runs:** ten seeds × three speeds × four dt values. |
| [04 — Final protocol](04_final_social_protocol.ipynb) | Recompute eligibility and apply the conditional final-validation gate. |

There were **210 full scientific runs**. A timing pilot and ten implementation-validation model runs were separate. The [temporal helper](temporal_support.py), [data and reproducibility caches](data/), and [figures](figures/) remain with the notebooks. The common recording interval was **0.125 s**; late averages used the last **12.5 s**, while connectivity and encounter events were monitored every internal update.

## Predeclared practical criteria

The [criteria JSON](data/predeclared_criteria.json) was saved before the experiments. Primary decisions compared ensemble means for adjacent dt pairs:

- Absolute change ≤0.05 for polarization, rotation, largest-group fraction and connected-time fraction.
- Relative change ≤10% for MeanNND and mean distance to centroid, with the declared 0.01-BL absolute fallback near zero.
- Mean missed-repulsion-pass rate ≤0.01/model/s and zero sampled exact overlaps in both candidate and finer cohorts.
- Every speed and every finer available adjacent comparison had to pass before accepting a candidate.

Matched-seed absolute differences were diagnostic; identical long trajectories were not required. These finite-cohort practical thresholds were project decisions, not biological constants, significance tests or a formal convergence theorem.

## Executed results

### Controlled implementation checks passed

All **12/12 checks** passed. With `max_turn_rate=None`, trajectories, DataCollector records and RNG states matched the previous pipeline exactly. Clockwise/counterclockwise clipping and wraparound worked, headings remained normalized, updates stayed synchronous, and maximum social turning totalled **14 rad per physical second** across all five tested dt values.

At dt = 0.015625 s, recording every eighth update gave 0.125-s output. Across **640 internal updates**, full and sparse recording retained identical internal states, RNGs and shared rows. Group rows fell from **641 to 81**, and fish rows from **12,820 to 1,620**. Recording cadence did not cause the dynamics differences.

### Hypothesis A failed practical temporal stability

For the finest comparison, **0.015625 → 0.0078125 s**:

| Speed (BL/s) | Relative change in mean distance to centroid | Other failed criteria: absolute change |
|---:|---:|---|
| 1 | 37.08% | Connected-time fraction: 0.07410 |
| 3 | 52.31% | Polarization: 0.06393; rotation: 0.05095; connected-time fraction: 0.052675 |
| 5 | 27.37% | None additional |

No instantaneous-turn candidate passed across all speeds. Across dt = 0.03125 → 0.015625 → 0.0078125 s, missed passes/model/s were **0 → 0 → 0** at speed 1, **0.0192 → 0.0096 → 0** at speed 3, and **0.0928 → 0.0160 → 0** at speed 5. Removing detected missed encounters in these samples did not make aggregate behaviour stable.

Thirty conditions overlapping Trial Two were freshly simulated and exactly reproduced nine previous measurements, supporting cross-stage consistency. They were not substituted from the previous cohort. See [instantaneous findings](data/01_findings.json).

### Hypothesis B also failed practical temporal stability

For the finest comparison, **0.015625 → 0.0078125 s**:

| Speed (BL/s) | Finest-pair outcome |
|---:|---|
| 1 | Mean centroid distance 2.225382 → 2.546543 BL: **12.61%** change, above the 10% criterion. |
| 3 | **All criteria passed** for this pair. |
| 5 | Mean centroid distance 1.063108 → 1.383269 BL: **23.15%** change; connected-time fraction 0.822100 → 0.659875: **0.162225** absolute change. |

Only **1/9** complete bounded-turn speed/pair comparisons passed; no candidate met the all-speed chain rule. At speed 5, missed-pass rates declined **0.304 → 0.0416 → 0.0032 → 0/model/s** across four dt values. Bounded turning gave a more physically interpretable response and improved some comparisons, but was insufficient to resolve temporal sensitivity. See [bounded-turn findings](data/03_findings.json).

All 210 cases had zero sampled exact overlaps. However, minimum sampled pair separation in the bounded cohort was only **0.00380 BL**. Point-like agents and soft behavioural repulsion do not impose hard-body exclusion. The missed-pass detector measures restricted straight-path zone encounters and excludes reflected segments; neither diagnostic guarantees collision avoidance.

## Interpretation and decision after Trial Three

Neither instantaneous turning nor bounded turning with the single shared timestep achieved practical stability over speeds 1–5 BL/s. Correct implementation and fewer missed encounters did not establish stable group metrics. The experiments measured disagreement without isolating its cause. Hard social-zone boundaries, wall events and finite-cohort sensitivity remained possible contributors rather than established explanations.

**No new temporal protocol was accepted.** The smallest tested dt was not promoted automatically. Because the temporal prerequisite failed, the conditional final **30-seed × 180-s cohort was not run**, and **zero official checkpoints were regenerated**. These gates remain untested; they are not failed assembly results. The earlier checkpoints remain evidence only for their stored Trial Two protocol.

**Status after this trial: NOT READY FOR LIGHT.** See [04_final_social_protocol.json](data/04_final_social_protocol.json). No light field, light reading, light-dependent speed, environmental noise or gradient-performance metric was implemented.

## Proposed next step — not implemented

The documented proposal holds behavioural decision frequency fixed while refining physics substeps independently. This would distinguish motion resolution from social reaction frequency. The implementation and future test specification are in [NEXT_SOLUTION.md](../NEXT_SOLUTION.md); they are proposals, not executed findings. Criteria must not be silently relaxed or cohesion parameters tuned merely to obtain a passing school.

## Preserved evidence and scope

All notebooks retain saved outputs. CSV summaries, JSON decisions, traces, figures and reproducibility caches remain in this trial. The [documentation before reorganization](data/documentation_before_reorganization.txt) preserves the earlier narrative with its original-location links. Historical assembly and checkpoint evidence remains in [Trial Two](../trial_two/README.md).

Puckett-inspired turning increments and speed ranges motivated these tests; the 14-rad/s conversion and acceptance thresholds were project conventions. This study establishes neither empirical calibration nor formal mathematical convergence.

[Back to the handling overview](../README.md).
