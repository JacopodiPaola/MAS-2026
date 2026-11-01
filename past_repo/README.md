<!-- Authored for JacopodiPaola/MAS-2026 during archive curation; this guide is not copied from the original repository. -->
# Past repository: reading and comparison only

This folder preserves a selected subset of [jdipaola-stack/MAS-2026](https://github.com/jdipaola-stack/MAS-2026). These files are references, not the new implementation. Each Python file starts with source comments; each notebook starts with a source Markdown cell. Original simulation logic and notebook cells have not been rewritten.

Doruk's visualization and Maria's Couzin logic will form the new implementation. The agreed baseline is planar swimming displayed in a 3D PyVista scene, with local light-dependent speed and social interactions.

## Selected files and provenance

| File | Source branch and original path | Why retain it / limitations |
| --- | --- | --- |
| [model.py](model.py) | `main`: `model.py` | Developed fish/model classes, synchronized movement, bounded arena, light response, measurements and seeded initialization. Contains several alternative sensing modes and optional ecology; selectively reuse rather than adopt everything. |
| [paper_rules.py](paper_rules.py) | `main`: `paper_rules.py` | Separate repulsion/orientation/attraction zones and paper-inspired light-dependent speed. The Shiners preset has zero direct gradient weight. The moving light field is synthetic; the implementation is not a verified reproduction of the paper. |
| [paper_experiments.py](paper_experiments.py) | `main`: `paper_experiments.py` | Group-size comparisons, independent controls, trajectory export and normalized light tracking. Requires adaptation to the new model and task; the runner assumes a moving patch. |
| [SingleFish_ContinuousSpace.ipynb](SingleFish_ContinuousSpace.ipynb) | `main`: `SingleFish_ContinuousSpace.ipynb` | Teaching prototype defining a fish class, movement and wall reflection. No light response or social steering. |
| [Couzin_Parameters.ipynb](Couzin_Parameters.ipynb) | `main`: `Couzin_Parameters.ipynb` | Early fish/model classes and neighbour detection. It detects neighbours but does not use them to steer. |
| [Couzin_Parameters_maria_attraction.ipynb](Couzin_Parameters_maria_attraction.ipynb) | `maria-attraction`: `Couzin_Parameters.ipynb` | Later development version containing repulsion and an attraction function. Attraction is not called by `decide()`. `step()` is nested inside the constructor, and attempted movement-limit exception handling needs correction before reuse. |
| [Couzin.py](Couzin.py) | `maria-attraction`: `Couzin.py` | Fish/model classes with repulsion and simultaneous decide/advance phases. Despite the branch name, this Python file does not implement attraction. It includes the old Solara display. |

Main-branch files are pinned to [`130c443945ac455d06a53abb6c7834128a6b0692`](https://github.com/jdipaola-stack/MAS-2026/tree/130c443945ac455d06a53abb6c7834128a6b0692). Maria-branch files are pinned to [`3421cfcbe5d830a35040120719dcc97eb6e7ee76`](https://github.com/jdipaola-stack/MAS-2026/tree/3421cfcbe5d830a35040120719dcc97eb6e7ee76). This README was written for the destination repository; it is not an original source file.

## Reading the files correctly

- These are alternative implementations and development stages, not modules that must all be used together. Maria's new implementation should determine the active fish class.
- In `model.py`, the Python constructor defaults to Shared sensing with light disabled. To interpret the agreed speed-mediated shiner mechanism, read the Paper model / Shiners path and `paper_rules.py`.
- Shared sensing explicitly estimates gradients from neighbours' brightness readings; minority leadership and recruitment add different mechanisms. They are outside the agreed initial baseline, as are births, deaths, predators and storms.
- The notebook classes use Mesa's experimental continuous-space API; the developed `model.py` uses a different space API. Preserve the distinction when adapting ideas.
- `paper_rules.py` references a missing `PAPER_MODEL.md`. These references are not a reconstructed runnable release, and their historical dependencies have deliberately not been carried over.
- All four published branch tips (`main`, `develop`, `couzin-repulsion`, `maria-attraction`) were compared during curation. `bla.py` was omitted because it largely duplicates `Couzin.py`; the alternate Couzin notebook largely duplicates Maria's version. `develop` adds no distinct simulation logic worth retaining. None of those branch tips contains PyVista code.

Archive verification checked original Python contents after removing the added source headers, and notebook content after removing the added provenance cell. Simulations and historical experimental results were not run or validated as part of this cleanup.
