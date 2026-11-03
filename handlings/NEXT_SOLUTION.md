# Proposed next solution: Separate behavioural and physics timesteps

## Executed evidence and interpretation

[Trial Three](trial_three/README.md) found that neither instantaneous turning nor bounded social turning with one shared timestep met the practical temporal-stability criteria across speeds 1, 3 and 5 BL/s. The bounded-turn implementation passed its controlled checks, but this did not establish temporal stability.

Currently, reducing `dt` both shortens movement steps and increases how often fish sense neighbours and choose social headings. The experiments therefore change behavioural frequency together with numerical resolution. The proposal below isolates these two effects; its success remains untested.

## Proposed clocks and state

| Clock | Example interval | Purpose |
| --- | --- | --- |
| `decision_dt` | 0.125 s | Synchronous neighbour sensing and social target selection: 8 decisions/s |
| `physics_dt` | 0.015625 s | Movement, bounded turning and wall handling: 8 substeps per decision interval |
| `recording_dt` | 0.125 s | DataCollector output only; no effect on decisions or motion |

The proposed test values divide `decision_dt` exactly. Use integer counters for clock boundaries rather than accumulating floating-point times.

At each decision boundary, every fish reads the **same committed population snapshot**. Apply the existing repulsion priority, orientation and attraction rules, then cache a normalized desired heading and target speed. Commit all target decisions together. Keep these targets fixed until the next decision; do not recompute social rules in physics substeps.

At each physics substep, compute all fish's next states from the same committed state, then commit all states together. If bounded turning is retained, turn the current heading toward the cached desired heading by at most `max_turn_rate * physics_dt`, then move using that heading and the cached speed. Preserve the existing instantaneous hard wall reflections as a separate boundary rule. For this proposed variant, reflection changes the current heading and position; the cached social target remains fixed until the next scheduled decision. Document and test this convention, since wall interactions may remain a source of sensitivity.

The candidate `max_turn_rate = 14 rad/s` comes from the project's conversion of the cited Puckett reference `1.75 rad/update` at `dt = 0.125 s`. It is a **derived project scaling convention**, not a fitted biological rate. Freeze the turning formulation across all physics-timestep comparisons; changing turning and timestep together would introduce another confound.

## Scheduling and implementation checks

Use an explicit boundary order:

1. At `t = 0`, initialize state, observe/record the initial population once, then calculate and commit its first social targets.
2. Advance one physics substep, committing all positions and headings together.
3. At the resulting time, update diagnostics from the committed state. Record it if a recording boundary is due.
4. If a decision boundary is due, calculate and commit the next targets from that same state. Then begin the next substep.

At an experiment's terminal time, observe/record the final state and stop before an unused next decision. Thus a half-open one-second evolution has eight decision events at `0, 0.125, …, 0.875 s`. Never duplicate a record where clocks coincide.

Before scientific runs, check synchronous decisions, simultaneous movement, cached-target persistence, event ordering, angular units, normalization, wrap-around, wall behaviour and exact clock counts. At fixed `decision_dt`, changing `physics_dt` must leave the decision count at 8/s. Changing only recording frequency must leave physical states and RNG continuation identical. Diagnostic observers must not draw random values or modify the model.

Keep social angular noise disabled for the proposed reference test. If a later variant uses it, draw noise at decision events and scale it with `decision_dt`, with the convention documented beforehand. Refining physics must not introduce additional social-noise draws.

Future checkpoints must save positions, headings, parameters, agent IDs/order and RNG states **plus cached targets, absolute time, clock counters, next decision/record times and scheduling phase**. Define the checkpoint boundary explicitly; a checkpoint immediately after a decision must restore those targets without drawing or deciding again. Test restored continuation against the original run and paired control branches. Trial Two checkpoints do not contain the complete state of this proposed architecture.

## Important limitation: movement resolution and social latency

Smaller physics steps do not guarantee that social decisions detect a repulsion encounter entirely between two decision times. At 5 BL/s, a fish travels `5 * 0.125 = 0.625 BL` per decision interval, exceeding the `0.5 BL` repulsion radius; relative closing distances can be larger still.

Distinguish a **numerical missed passage** between physics samples from an encounter that physics samples resolve but scheduled social decisions never observe. The latter is a consequence of the proposed decision latency. Monitor distances and connectivity at every physics substep, including between saved DataCollector rows, and report both mechanisms separately using definitions frozen before experiments.

Retain the documented scope of the existing missed-passage detector, including its restriction to straight, non-reflected pair motion. Zero detected passages or exact sampled overlaps cannot prove collision avoidance. A fast repulsion check or event-triggered response would change the behavioural protocol; it needs a separate explicit proposal and comparison, rather than silently adding social updates at the physics frequency.

## Future experiment and proposed acceptance rules

**Do not execute this plan during the reorganization.** Before future runs, save a new protocol/criteria file and source hashes. The existing [Trial Three criteria](trial_three/data/predeclared_criteria.json) are historical evidence; do not overwrite them or imply that they already tested this architecture.

Use matched seeds `0–9`, equal duration `31.25 s`, a common final `12.5 s` measurement window and recording every `0.125 s`. Hold `decision_dt = 0.125 s`, social parameters, deterministic initialization, turning and wall conventions fixed. Test all combinations of:

- `physics_dt = 0.03125, 0.015625, 0.0078125 s`;
- speeds `1, 3, 5 BL/s`.

Compare Polarization, Rotation, LargestGroupFraction, ConnectedTimeFraction, MeanNND, MeanDistanceToCentroid, MissedRepulsionPassesPerSecond and ExactOverlapPairs. Measure time fractions with physical-time weighting at every internal step. Report decision counts, RNG cadence, minimum separation and encounters between decision times alongside the original diagnostics.

Proposed practical criteria carry forward the earlier tolerances: ensemble-mean absolute changes at most `0.05` for order/connectivity metrics; relative changes at most `10%` for the two distance metrics, with a `0.01 BL` absolute fallback when the reference magnitude is at most `1e-8`; missed-passage rates at most `0.01/model/s` in both compared cohorts; and zero exact sampled overlaps. Freeze the precise definitions and treatment of decision-latency encounters before running. These are project diagnostics, not biological constants or a formal convergence proof.

Use matched-cohort ensemble means for acceptance; paired-seed absolute changes remain sensitivity diagnostics, not trajectory-identity requirements. A candidate must pass at all three speeds and at every available finer adjacent comparison. The central comparison is `0.015625` versus `0.0078125 s` at fixed decision frequency. Select the coarsest qualifying physics interval, not automatically the smallest tested.

If a candidate qualifies, run a **new** 30-seed, 180-s random-start assembly cohort under that complete protocol. Freeze its assembly/stability criteria before running, using the [previous final-cohort specification](trial_three/data/final_validation_criteria.json) as the documented starting point. Report censoring and every breakup. Then generate new official checkpoints, validate exact restoration and paired continuation, and review light readiness. Passing the temporal test alone does not authorize an automatic switch to light.

If no candidate qualifies, investigate hard social-zone boundaries, wall reflections, decision latency and event handling. Do not tune cohesion parameters simply to meet acceptance criteria.

## Future light architecture — conceptual only

At a future decision event, combine local social sensing with a local scalar light measurement `L(x, y)`. Social rules determine desired heading; light determines target speed through:

```text
s_i = s_min + L_i * (s_max - s_min)
```

Define the scalar field's normalization before applying this rule. Physics substeps then handle movement, turning and boundaries using cached targets. Fish receive only local scalar light, with no supplied gradient direction. This remains a later design step, conditional on the social protocol and checkpoint validation above.
