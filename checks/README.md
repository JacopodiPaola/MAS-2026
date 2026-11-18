# Checks and trials before adding light

## How to use this folder

- **Environment:** Python 3.11. From the repository root run `python -m pip install -r checks/requirements.txt`, choose that environment as the notebook kernel, and use *Restart Kernel → Run All*.
- **Folder map:**
  - [`../shiner_model.py`](../shiner_model.py): the fish model. Every notebook imports this one file.
  - [`model_checks/`](model_checks/): checks 01 to 07 of the model. Run them in order; each takes seconds to minutes.
  - [`trial_one/`](trial_one/), [`trial_two/`](trial_two/), [`trial_three/`](trial_three/): the first three trials, kept as an archive with their saved outputs, data and figures.
  - [`check_support.py`](check_support.py): small helpers shared by the checks and the trials.
  - [`../Golden_Shiner_MAS_Complete.ipynb`](../Golden_Shiner_MAS_Complete.ipynb): the complete notebook, which runs the same model.
  - [`../past_repo/`](../past_repo/): earlier prototypes of the project (not used here).
- **Caching:** the trials save every result in their `data/` folder. When a trial notebook runs again, it first compares fingerprints (hashes) of its code and saved results; if they match, it loads the saved results instead of simulating. Trials one to three are slow, so do not re-run them. Their support modules (`diagnostics.py`, `relocation.py`, `study_support.py`, `temporal_support.py`) must not be edited, because the caches check their hashes.

## The project in one paragraph

Golden shiners are small fish that swim in schools and prefer dark water. A school can find dark areas even though each fish only senses the light where it is: fish swim faster in bright light and slower in the dark, and because they stay together, the whole group drifts towards the dark (Berdahl et al. 2013; Puckett et al. 2018). We model each fish as an agent that follows three local rules (Couzin et al. 2002). The goal is to add this light-dependent speed. Before adding light, we had to be sure that the social model works on its own. This folder documents that work.

## Key ideas in plain words

- **Agent-based model:** a simulation in which every fish is a small program (an *agent*) with simple rules. Group behaviour is not programmed; it emerges from the rules.
- **The three zones:** each fish looks at the fish around it in three rings. In the *repulsion* zone (too close) it swims away. In the *orientation* zone it copies their direction. In the *attraction* zone (farther away) it swims towards them. Repulsion has priority: if any fish is too close, the fish only avoids it (Couzin et al. 2002).
- **Body length (BL):** our unit of distance, the length of one fish, about 5 cm (Puckett et al. 2018, Table S1). Our zones end at 0.5, 3 and 5.5 BL.
- **Decision and dt:** every dt seconds, each fish looks around and picks a new direction. dt is the fish's reaction time. We use dt = 0.125 s, that is 8 decisions per second.
- **Step length:** how far a fish swims between two decisions, speed × dt. At 1 BL/s it is 0.125 BL.
- **Polarization:** a number from 0 to 1 that says how much the fish point the same way (1 = all the same direction).
- **Rotation (milling):** a number from 0 to 1 that says how much the fish swim in a circle around the group centre (1 = a perfect circle, called *milling*).
- **Together:** the fish form one connected group. Two fish are linked if they are at most 5.5 BL apart (the attraction radius); the group is together if every fish can be reached through links.
- **Collision:** two fish that come much closer than the repulsion zone allows. The model treats fish as points, so nothing physically stops two fish from overlapping.
- **Crowding:** when too many fish must share a small group, some always sit inside another fish's repulsion zone, keep escaping, and the group cannot line up.

## Chapter 1: Building and checking the model

**What we asked.** Does the model do exactly what the rules say, and do the fish behave like a school?

**What we did.** We wrote one model file, [`shiner_model.py`](../shiner_model.py), that every notebook imports. It follows Couzin et al. (2002) and the supplement of Puckett et al. (2018): repulsion has priority, orientation and attraction are added as raw sums (Puckett et al. 2018, SI eq. 7), and all fish decide from the same old state before any fish moves. Then we checked it in seven notebooks:

| Check | What it tests |
|---|---|
| [01 Data collector](model_checks/01_data_collector.ipynb) | 21 small hand-made cases: the three rules, repulsion priority, fish on top of each other, walls and recording |
| [02 Recording](model_checks/02_recording_integrity.ipynb) | Every step is recorded once, and recording does not change the fish |
| [03 Metrics](model_checks/03_metric_validation.ipynb) | 62 cases with a known answer for polarization, rotation, spread and nearest neighbours |
| [04 Seeds](model_checks/04_schooling_across_seeds.ipynb) | 10 random starts with all rules, without orientation, without attraction and without any social rule (62.5 s each) |
| [05 Labels](model_checks/05_collective_state_summary.ipynb) | Names for the group state (polarized, milling, swarm) with the 0.35 / 0.65 thresholds of Tunstrøm et al. (2013) |
| [06 Plots](model_checks/06_diagnostic_plots.ipynb) | Time series, polarization against rotation, and positions |
| [07 Decision rate](model_checks/07_decision_rate.ipynb) | Exactly 8 decisions per fish per second, and what sub-steps change (Chapter 3) |

**What we found.** All checks passed. The social rules clearly matter: over the last 100 steps of check 04, the mean polarization was 0.87 with all rules and 0.22 without social rules, and the mean distance to the nearest neighbour was 0.65 BL against 2.53 BL. But not every start ended as one group: after 62.5 s, seed 0 was split into 10 + 10 fish and seed 2 into 19 + 1.

**What we decided, and why.** The rules work. The split seeds needed a closer look before adding light, so we started the trials.

## Chapter 2: Trials one to three, the problem that would not go away

**What we asked.** Why did some groups look broken? And why did the results change when we changed dt?

**What we did.** [Trial One](trial_one/) followed seeds 0 and 2 step by step and tested walls, smaller dt and three extra rules from Puckett et al. (2018): 270° vision, a turn limit and a small heading error. [Trial Two](trial_two/) ran 30 random starts for 180 s, defined when a group counts as assembled (one group for 5 s in a row), tested saving and reloading groups (*checkpoints*), and tested the heading error on 20 new seeds. [Trial Three](trial_three/) made dt smaller and smaller, first with instant turns (90 runs) and then with a turn limit of 14 rad/s (120 runs).

**What we found.**

| Trial | Main result |
|---|---|
| One | The groups were not breaking apart; they had not come together yet. No group split again after it was connected. Walls did not explain it: seeds 0 and 2 were split before touching a wall, also in a 40 × 40 BL arena. The extra rules did not help consistently. But at 5 BL/s the results depended strongly on dt: polarization 0.48, 0.79 and 0.94 for dt = 0.125, 0.0625 and 0.03125 s. |
| Two | All 30 groups came together within 180 s (median 28.5 s, slowest 86.75 s), and none broke apart afterwards. All 30 checkpoints reloaded exactly. The heading error did not help (20 of 20 new seeds assembled without it, 19 of 20 with it). Results still changed with dt: from dt = 0.03125 to 0.015625 s, the nearest-neighbour distance changed by almost 25 % at 1 BL/s. |
| Three | Smaller dt never made the results settle. Between the two smallest dt (0.015625 and 0.0078125 s), the group spread still changed by 27–52 % with instant turns. With the turn limit, only 1 of 9 comparisons passed. |

**What we decided, and why.** The broken groups were a waiting problem: give random starts enough time, or start from an assembled group. We did not add rules just to force the fish together. The dt problem was still open, and each trial ended with "not ready for light".

## Chapter 3: The key insight, dt is the reaction time

**What we asked.** Is the dt problem a numerical error that smaller steps should remove?

**What we did.** We looked at what dt does in our model and what it means in the papers. [Check 07](model_checks/07_decision_rate.ipynb) also tested *sub-steps*: fish decide every 0.125 s but move in 8 small steps of 1/64 s between decisions. Sub-steps were the idea of two commits in the complete notebook.

**What we found.**
- In our model, one dt sets two things at once: how far a fish moves in one step and how often it decides. A smaller dt makes a fish that reacts faster. That is a different fish, not a more accurate one, so the results can never "converge".
- The papers treat the time step as behaviour. Couzin et al. (2002) set it to the fish's reaction time, 0.1 s, and Puckett et al. (2018, Table S1) use 8 decisions per second, that is dt = 0.125 s.
- Sub-steps change nothing. Between two decisions a fish swims in a straight line, so 8 small steps end where one big step ends. At 1 BL/s the paths stayed the same: after 60 s the largest difference was less than a billionth of a body length. At 3 and 5 BL/s the runs drift apart, but no sooner than the normal model drifts from itself when every fish is moved by a trillionth of a body length: that is chaos, not a different model. Sub-steps were also 2.5 to 2.6 times slower.

**What we decided, and why.**
- dt = 0.125 s is fixed. It is a value from the literature, not a number to refine.
- No sub-steps, and the old idea of two separate clocks (one for decisions and one for movement) was dropped: with a fixed decision rate there is nothing left to converge, and sub-steps give the same paths.
- The complete notebook now uses the shared model too, so the project has one model.
- Trial Two's checkpoints were made with exactly these settings (dt = 0.125 s, 1 BL/s), so they can be used as starting groups.

## Status and next steps

The social model works, and dt is fixed at 0.125 s. Before adding light we still want to know which parameters matter and how the model behaves at the higher speeds that light will cause (up to 5 BL/s; Puckett et al. 2018). These parameter studies are on the `develop` branch and will be added here as trials four to eight. Light is not implemented on `main`.

## References

- Berdahl, A., Torney, C. J., Ioannou, C. C., Faria, J. J., & Couzin, I. D. (2013). Emergent sensing of complex environments by mobile animal groups. *Science, 339*(6119), 574–576. https://doi.org/10.1126/science.1225883
- Couzin, I. D., Krause, J., James, R., Ruxton, G. D., & Franks, N. R. (2002). Collective memory and spatial sorting in animal groups. *Journal of Theoretical Biology, 218*(1), 1–11. https://doi.org/10.1006/jtbi.2002.3065
- Puckett, J. G., Pokhrel, A. R., & Giannini, J. A. (2018). Collective gradient sensing in fish schools. *Scientific Reports, 8*, 7587. https://doi.org/10.1038/s41598-018-26037-9 ([supplement](https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-018-26037-9/MediaObjects/41598_2018_26037_MOESM1_ESM.pdf))
- Tunstrøm, K., Katz, Y., Ioannou, C. C., Huepe, C., Lutz, M. J., & Couzin, I. D. (2013). Collective states, multistability and transitional behavior in schooling fish. *PLoS Computational Biology, 9*(2), e1002915. https://doi.org/10.1371/journal.pcbi.1002915
