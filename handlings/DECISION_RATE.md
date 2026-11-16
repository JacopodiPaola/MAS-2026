# Decision rate: how we resolved the timestep problem

**Status: resolved.** Each fish makes one social decision every **0.125 s (8 decisions per second)**, as in the Berdahl–Couzin model used by Puckett et al. (2018). In `shiner_model.py`, `dt = 0.125` **is this decision interval**. It is a behavioural parameter taken from the literature, not a numerical step that has to be made smaller until results converge.

---

## 1. The problem we had

Trials One–Three found that our results changed when we changed `dt`. Trial Three concluded that no `dt` met the stability criteria across speeds 1–5 BL/s.

In our model, one `dt` controlled two different things at the same time:

1. **Movement resolution**: how far a fish moves in one step.
2. **Decision frequency**: how often a fish looks at its neighbours and picks a new heading.

`NEXT_SOLUTION.md` proposed separating these into two clocks: a decision clock and a physics clock.

## 2. What commits `7f795a8` and `a4eeddf` did

In `handlings/Golden_Shiner_MAS_Complete.ipynb`, the commits made two changes:

- `dt` went from `0.125` to `0.015625` s (1/64 s).
- The social direction is only recomputed every 8 steps: `if (self.model.steps - 1) % 8 == 0:`.

So fish decide every 0.125 s and move in 8 small sub-steps between decisions. **The idea is right.** It matches the paper: Puckett et al. (2018), Supplementary Table S1, gives a "Direction update rate" of **8/s**, and the main text uses a time step of 0.125.

## 3. Why it did not change anything

Between two decisions, a fish swims **in a straight line at constant speed**: turns are instantaneous, there is no noise and speed is fixed. Eight steps of 1/64 s end at exactly the same point as one step of 1/8 s. Wall reflection is exact for straight-line motion too, so bouncing gives the same result. **The new code is the old `dt = 0.125` model, only slower.**

We compared the notebook's agent code before (`c476b48`) and after (`a4eeddf`) the commits, using 20 fish, a 20 × 20 BL arena, seeds 0–2 and 60 simulated seconds:

| Speed | What we saw (first comparison, test harness) | `checks/07` (real shared model) |
|---|---|---|
| 1 BL/s | Same trajectories: the largest position difference after 60 s was between 3e-11 and 1.3e-9 BL. | Same trajectories: the largest position difference in 60 s was between 2.1e-12 and 1.6e-11 BL. |
| 3 BL/s | The runs drift apart after 7–15 s. The old model drifts apart **from itself** at almost the same time (8–15 s) when every fish is moved by 1e-12 BL. | The sub-step runs drift apart after 14.4–26.5 s. The standard model with the 1e-12 nudge drifts apart from itself after 11.9–25.9 s. |
| 5 BL/s | Same pattern: 5–6.5 s for the new code, 5.25–6.5 s for the old model with the 1e-12 nudge. | Same pattern: 6.1–8.0 s for the sub-step runs, 5.6–7.25 s with the 1e-12 nudge. |
| Runtime | The new code is 6.2–6.6× slower. | 2.5–2.6× slower. `checks/07` searches for neighbours only at decisions, so this is the cost of the 7 extra movement sub-steps alone (see problem 1 below). |

The drift at higher speeds is **chaos**, not a different model. A tiny rounding difference can move a neighbour in or out of a zone, and after that the paths separate. The first comparison used a small test harness without Mesa. `checks/07_decision_rate.ipynb` repeats it with the real shared model and finds the same pattern. There, "drift apart" means that the largest distance between the same fish in the two runs first goes above 1e-3 BL.

The commits also had some practical problems:

1. `get_neighbors()` still ran at every sub-step even though the result is only used every 8th step. That is why the code was so much slower.
2. The `8` was hard-coded. If someone changed `dt`, the decision rate would change without anyone noticing.
3. `for _ in range(100)` now simulated 1.56 s instead of 12.5 s, and the DataCollector stored 8× more rows.
4. Only the notebook changed. `shiner_model.py`, which `data_collector.ipynb`, the checks and the trials all use, still had `dt = 0.125`, so the project had two different models.
5. `.vscode/settings.json` was committed with a Windows-only interpreter path.

## 4. What the "timestep sensitivity" really was

When Trials Two and Three changed `dt`, they were changing **how often fish decide**, which is their reaction time. A fish that reacts 16 times per second behaves differently from one that reacts 8 times per second. That is a change in **behaviour**, not a numerical error, so there is no `dt` at which the results "converge".

The fix is to take the decision rate from the literature and keep it fixed: **8 decisions per second, so `dt = 0.125 s`**.

## 5. What we changed

| File | Change |
|---|---|
| `shiner_model.py` | **Not changed.** Its default was already `dt = 0.125` with one decision per step. We keep it byte-identical because the trial notebooks check its SHA-256 hash (`handlings/trial_one/relocation.py`). |
| `handlings/Golden_Shiner_MAS_Complete.ipynb` | The sub-step change is removed. The notebook's own copies of `compute_group_metrics`, `GoldenShiners` and `GoldenShinersModel` are replaced by one cell that imports them from `shiner_model.py`, so there is one model. Runs are set by simulated seconds (12.5 s = 100 steps), the data has a `Time` column, and both plots use time in seconds. |
| `checks/07_decision_rate.ipynb` | New check. It confirms 8 decisions per fish per simulated second (exactly 80 in 10 s) and repeats section 3 with the real model. |
| `handlings/README.md`, `handlings/NEXT_SOLUTION.md`, `README.md`, `checks/README.md` | Status updated. `NEXT_SOLUTION.md` is marked as superseded by this file. `checks/README.md` lists check 07. |

Note on the notebook: its own classes normalised the orientation and attraction vectors separately before adding them. `shiner_model.py` adds the raw sums, as in Puckett et al. SI eq. 7. After the switch, the notebook's numbers differ from its old saved outputs.

## 6. How it all fits together

```text
one model.step()  =  0.125 s  =  one decision for every fish

1. decide()   every fish reads the same old state
              neighbours -> repulsion has priority, otherwise orientation + attraction -> new heading
              (light phase: read local light L -> set speed)
              new position = position + heading * speed * 0.125, reflected at the walls
2. advance()  every fish commits its new state at the same time
3. record     the DataCollector saves a row every `record_every` steps
```

Time is `t = model.steps * model.dt`. So 1 s = 8 steps, 60 s = 480 steps and 180 s = 1440 steps.

```python
from shiner_model import GoldenShinersModel

model = GoldenShinersModel(n_fish=20, speed=1.0, seed=0, record_every=8)  # one row per second
seconds = 60
for _ in range(round(seconds / model.dt)):
    model.step()

data = model.datacollector.get_model_vars_dataframe()
data["Time"] = [step * model.dt for step in model.recorded_steps]
```

**Smoother animations:** fish move in straight lines between decisions, so the visualisation can interpolate between saved frames. Sub-steps are not needed for this.

## 7. Where light goes next

- Keep `shiner_model.py` frozen so the trials stay reproducible. Put light in a new module, for example `light_model.py`.
- `LightField` gives a value `L(x, y, t)` between 0 (dark) and 1 (bright): a moving dark spot plus noise. Fish only read the value at their own position and are never given the gradient.
- At each decision, a fish sets its speed from its local light, `s = s_min + L * (s_max - s_min)`, with `s_min = 0.2` and `s_max = 5` BL/s (1 and 25 cm/s with 1 BL = 5 cm, Puckett Table S1). The social heading rules do not change.
- **Starting states:** Trial Two's 30 assembled checkpoints were made with exactly this protocol (`dt = 0.125`, speed 1, deterministic, instantaneous turns). In `06_light_readiness_decision.json`, the only gate that failed was the timestep one, which this file resolves. The checkpoints can therefore be used as starting states for the light experiments.

## 8. Limitations to report

- Behaviour depends on the decision rate. We use 8/s from the paper. An optional extra is a sensitivity check at 4/s and 16/s, reported as **parameter sensitivity**, not as convergence.
- At 5 BL/s a fish moves 0.625 BL per decision, which is more than the 0.5 BL repulsion radius. In bright areas two fish can pass through each other between decisions. Puckett et al. report a similar effect (nearest-neighbour distances below 0.5 BL, which they attribute to low time resolution). We report overlaps as a diagnostic.

## References

- Puckett, J. G., Pokhrel, A. R., & Giannini, J. A. (2018). Collective gradient sensing in fish schools. *Scientific Reports*. Supplementary Table S1.
- Berdahl, A., Torney, C. J., Ioannou, C. C., Faria, J. J., & Couzin, I. D. (2013). Emergent sensing of complex environments by mobile animal groups. *Science*, 339, 574–576.
