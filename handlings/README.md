# Pre-light model handling and validation

**Current status: NOT READY FOR LIGHT YET.**

This folder preserves the debugging and validation history before adding a light field to the Golden Shiner model. Each trial addresses a specific uncertainty; parameters were not selected merely to produce visually cohesive schools. Notebooks retain executed outputs, with their data, figures and decisions beside them.

## Executed results

| Trial | Question | Main result | Status after the trial |
| --- | --- | --- | --- |
| [Trial One](trial_one/README.md) | Do social rules, walls or parameters explain apparent fragmentation? | The diagnosis shifted toward insufficient assembly time and timestep sensitivity. | Further testing required |
| [Trial Two](trial_two/README.md) | Do random groups assemble, and can their states be restored? | 30/30 assembled within 180 s; no post-confirmation breakup was observed; checkpoints were validated. | Assembly resolved for that protocol; timestep unresolved |
| [Trial Three](trial_three/README.md) | Do refinement or bounded turning resolve timestep sensitivity? | Neither formulation with one shared timestep met practical stability criteria across speeds 1–5 BL/s. | Temporal problem unresolved |

The controlled [checks](../checks/README.md) established that the local social rules work together. Random initialization remains part of the protocol. In Trial Two, all 27 initially disconnected populations assembled; three were connected initially. Persistent assembly means one connected component continuously for at least 5 s, an operational project definition. These finite observations do not establish universal assembly or stability.

Checkpoint restoration and RNG continuation worked. Deterministic behaviour remains the reference because social noise did not improve held-out assembly. Recording frequency can be separated from internal updates. No light field has been implemented.

## Interpretation and remaining uncertainty

A timestep-independent social-motion protocol, a final light-ready timestep, and checkpoints under that final protocol have **not** been established. Trial Two checkpoints remain evidence for their original protocol, not final light starting states.

The current timestep controls both movement resolution and social decision frequency. Refining it changes both, so the comparisons cannot isolate numerical motion resolution.

## Evidence preservation and setup

Use the tested environment in [checks/requirements.txt](../checks/requirements.txt). The notebooks locate the shared model from either the repository root or their trial folder. This reorganization changed paths and imports only; all 16 saved notebook outputs and the original data, figures, manifests and checkpoints were preserved. No new scientific runs were performed.

The [relocation registry](trial_one/data/relocation_provenance.json) records the original and relocated source hashes. Cache checks accept an original source identity only while the relocated file exactly matches its audited hash; later edits invalidate that alias. Original documentation is archived in each trial's `data/documentation_before_reorganization.txt`.

## Proposed next step — not implemented

[Separate behavioural and physics timesteps](NEXT_SOLUTION.md): hold social decisions at `decision_dt = 0.125 s`, refine `physics_dt` independently, and keep recording on a separate clock. This is a hypothesis to test, not a proven fix. Finer movement steps alone cannot guarantee repulsion encounters are detected by less frequent social decisions. Temporal qualification, a new 30-seed assembly cohort and validated new checkpoints must precede a fresh light-readiness decision.
