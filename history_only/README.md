# Historical reference only

These files preserve the previous project's work for reading and comparison. They are **not the active implementation**, and adding them does not establish that the old simulations or results are validated.

The new project will use Doruk's visualization and Maria's Couzin logic. Its agreed baseline is planar swimming rendered in a 3D PyVista scene, with local light-dependent speed and social interactions. Full 3D swimming, direct gradient sensing, explicit brightness sharing, and recruitment signals are outside that initial baseline.

Original filenames are preserved so that the code remains readable and references are recognizable. The folder name marks every file as historical; individual `_history_only` suffixes would break existing module imports.

## Provenance

- Source: [jdipaola-stack/MAS-2026](https://github.com/jdipaola-stack/MAS-2026).
- Main archive snapshot: [`130c443945ac455d06a53abb6c7834128a6b0692`](https://github.com/jdipaola-stack/MAS-2026/tree/130c443945ac455d06a53abb6c7834128a6b0692).
- `LEGACY_README.md` is the source README, renamed to distinguish it from this guide.
- `recovered_pre_deletion/` contains `run.py` and five tests recovered from the parent of deletion commit [`fbae169`](https://github.com/jdipaola-stack/MAS-2026/commit/fbae1696e0a9345d62258e9303daf7c2dc57216e). These belong to an earlier revision, not the main archive snapshot, and require review before reuse.
- No simulation logic was rewritten for this archive.

## What to read and what to replace

| File | Value for the new project | Required action before reuse |
| --- | --- | --- |
| `model.py` | Synchronized planning/movement, bounded arena, seeded initialization, local light sampling, measurements and data collection. | Compare with Maria's implementation and selectively adapt. It combines four distinct sensing modes and optional ecology; do not import the whole model as the new baseline. |
| `paper_rules.py` | Separate repulsion/orientation/attraction zones and paper-inspired shiner movement. The Shiners preset uses zero direct gradient weight. | Compare with Maria's rules and verify scientific parameters. The moving light patch is a synthetic approximation. |
| `paper_experiments.py` | Group-size and environmental-weight sweeps, independent controls, trajectory export and normalized light-tracking performance. | Adapt to the new model interface. The current runner assumes a moving patch; its tracking metric is not automatically informative for a static field. |
| `app.py` | Old controls, measurement displays and visual explanations. | Replace with Doruk's visualization/PyVista work. It uses Solara and Matplotlib. Some sliders are overridden by the paper preset. |
| `Couzin_Parameters.ipynb` | Early notes on interaction zones and neighbour detection. | Reading only: detected neighbours are not used to steer fish. This is not a complete schooling implementation. |
| `N_Fish.ipynb` | Early multiple-fish movement and wall reflection. | Superseded prototype; no light sensing or social steering. |
| `SingleFish_ContinuousSpace.ipynb` | Early single-fish movement and wall reflection. | Superseded prototype; no light sensing. |
| `basic_continuous.ipynb` | Minimal movement and old display example. | Superseded prototype using a periodic space rather than the bounded baseline. |
| `research_experiments.py` | Matched controls, arrival times, censoring and sustained occupancy measurements. | Reading only for the initial baseline: its minority-leadership and recruitment mechanisms answer different questions. |
| `experiments.py` | Older alignment-strength sweep and averaging across seeds. | Depends on the deleted `run.py`; not runnable unchanged from this archive layout. Adapt only if that experiment is needed. |
| `EXPERIMENT_RESULTS.md` | Historical five-run minority/recruitment pilot summaries and their limitations. | Do not treat these as results for the new baseline. Linked raw results are absent; numerical claims were not reproduced during this review. |
| `LEGACY_README.md` | Detailed explanations of old modes and measurements. | Reading only: defaults and file listings are partly stale. Commands assume the original layout. |
| `requirements.txt` | Old simulation, interface and test dependency list. | Build a new dependency list around the new implementation; this one does not include PyVista. |
| `requirements-lock.txt` | Record of the old macOS/Python environment. | Historical environment record; do not use as the new Windows/PyVista environment specification. |
| `requirements-browser.txt` | Old browser-testing dependencies. | Relevant only if maintaining the old Solara interface. |
| `recovered_pre_deletion/run.py` | A headless runner with CSV output and settings export. | Adapt imports, resolved parameter reporting and supported modes to the new model. |
| `recovered_pre_deletion/tests/test_model.py` | Reproducibility, movement bounds, social responses, measurements and old light rules. | Retain relevant invariants; old shared-sensing assumptions do not define the new baseline. |
| `recovered_pre_deletion/tests/test_research.py` | Information access, controlled comparisons and arrival accounting. | Selectively adapt measurement/control checks; minority/recruitment behaviour is outside the baseline. |
| `recovered_pre_deletion/tests/test_population.py` | Historical birth/death and disturbance checks. | Reading only while ecology is excluded. |
| `recovered_pre_deletion/tests/test_app.py`, `tests/test_browser.py` | Old interface and browser regression examples. | Replace with checks appropriate to Doruk's visualization. |

The final table row's `tests/test_browser.py` is also inside `recovered_pre_deletion/`.

## Important limits of the old model

1. The app starts in **Paper model / Shiners**, whereas the Python constructor defaults to **Shared sensing** with light disabled. Always identify the mode before interpreting behaviour.
2. Shared sensing explicitly estimates a gradient from neighbours' brightness readings. Informed minority directly probes a gradient; Recruitment adds safe-light signals. None is equivalent to the agreed speed-mediated shiner baseline.
3. In paper mode, speed grows linearly with brightness; in the older modes, speed is slowest near a chosen preferred brightness. These are different environmental responses.
4. The old README lists scripts and tests that were deleted. Some have been recovered here as separate historical files; this folder is not a reconstructed runnable release.
5. `paper_rules.py` references a missing `PAPER_MODEL.md`. The paper-inspired implementation has not been audited equation by equation against the supplement.
6. The old model uses point agents and soft repulsion, not solid-body collisions. Its density and rotation measurements are planar. Rendering 3D meshes does not change these assumptions.
7. Births, deaths, predators and storms add mechanisms outside the initial sensing experiment. Keep them disabled/excluded when establishing that baseline.

## Suggested migration order

1. Review Maria's social rules and Doruk's visualization once contributed.
2. Document the selected social zones, light-to-speed rule, units, time step, noise and wall response.
3. Keep simulation positions in `(x, y)` and map them to `(x, y, constant z)` for display. Camera motion and rendering frame rate must not alter model time or random draws.
4. Render the same numerical light field used by the agents; the scene's decorative lighting must not determine sensed brightness.
5. Choose a static linear gradient or a moving dark patch explicitly. Both exist in the archive, but test different tasks.
6. Adapt headless exports and relevant checks, then compare solo and social fish across multiple seeds and group sizes.

## Scientific and display references

- [Puckett, Pokhrel & Giannini (2018), Collective gradient sensing in fish schools](https://www.nature.com/articles/s41598-018-26037-9): local light-dependent speed underlies the shiner mechanism; the archive's implementation is a research scaffold rather than a verified reproduction.
- [PyVista oriented glyphs](https://docs.pyvista.org/api/core/_autosummary/pyvista.DataSetFilters.glyph.html): potential display mechanism for fish aligned with the existing heading vectors.

## Archive verification

The copied snapshot files were checked against the source checkout, and recovered files against their historical Git contents. This archive operation does not run the simulations, install the old dependencies, or validate the historical experimental results.
