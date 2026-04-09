# Final Project Extension — Midterm Project 2: Dynamical Ephemerides and Detection Robustness

## PHY 480, Michigan State University — Spring 2026

### Professor Sean Couch

## Relationship to the midterm

This final project extends the light-curve pipeline from `README.md` in this directory. The midterm work remains the front end of the final analysis: you should keep your data loading, preprocessing, DFT period search, folding, and transit fitting, then build new later-course methods on top of that baseline.

You may focus on one target deeply for the final, but your code should remain organized so that the same pipeline can still be run on any of the provided datasets.

## Carry forward from your midterm

Your final repository must reuse and clearly identify substantial pieces of your midterm code. At minimum, you must carry forward:

1. Your light-curve ingest and preprocessing workflow.
2. Your DFT or period-search implementation.
3. Your folding and transit-model fitting code.
4. At least two tests from the midterm repository, updated as needed for any refactors.

See `projects/final-project-workflow.md` for the required carry-forward record format and contents.

## Final goals

- Connect the fitted transit period to a dynamical orbit model.
- Use ODE integration to predict and interpret transit timing behavior.
- Quantify uncertainty or detection robustness with a random-sampling method.

## Suggested background

- Newman, Chapter 8 and ICA-10: RK4 integration for coupled ODEs.
- Newman, Chapter 10, §10.1: random number generators and seeds (§10.1.2) for reproducible resampling; Gaussian random numbers (§10.1.6) for noise-injection models.
- Your midterm work on DFT period finding, folding, and parameter fitting.
- Bootstrap or injection-recovery ideas for uncertainty estimation and detection performance.

### Connection to course material

| Required method | Where introduced | Key reference |
| --------------- | ---------------- | ------------- |
| RK4 time integration | PCA-11, PCA-12, ICA-10, ICA-11 | Newman Ch. 8 |
| Bootstrap / resampling | PCA-04 (Monte Carlo ideas) | Newman Ch. 10 (§10.1–10.1.6) |
| Nonlinear fitting / optimization | PCA-08, ICA-07 | Newman Ch. 6 |

## Required later-course methods

This final extension must include both of the following:

1. **RK4 integration** of a reduced orbital model that predicts transit times or conjunctions.
2. **One random-sampling robustness method:** either bootstrap/resampling or injection-recovery with synthetic transit signals.

The midterm Fourier and fitting pipeline remains required, but those earlier methods are now the starting point rather than the entire project.

## Minimum viable scope

To pass, your final must include at least:

- A locked midterm baseline with documented best-fit parameters (Part E).
- An RK4-integrated orbit for at least one case (circular is acceptable), with predicted transit times extracted from the integration (Part F, items 1–3).
- A bootstrap or injection-recovery study with at least 50 realizations or 20 injected trials (Part G).
- At least one new test for each of Parts F and G.

Full credit requires completion of all task items in Parts E–H, including the full-scope robustness study and the synthesis discussion.

## What you must implement

You can choose your own function names, but your code must be modular and testable. At a minimum, your final `src/` code should include functions that:

- rerun your midterm fit on a chosen target and expose the fitted parameters cleanly,
- integrate a planar orbit model with RK4,
- identify predicted transit times or transit phases from the integrated orbit,
- run either a bootstrap workflow or an injection-recovery workflow,
- summarize the spread in fitted quantities or the recovery fraction across the random trials.

## Final extension tasks

### Part E — Lock the midterm baseline

1. Choose one primary TESS target for the final extension.
2. Rerun your midterm pipeline and record the baseline best-fit values of `P`, `delta`, `tau`, and `t0`.
3. Document the exact code path that produces those baseline values.

### Part F — Dynamical orbit model

The governing equations for a planar gravitational two-body orbit are:

$$\frac{d^2 x}{dt^2} = -\frac{GM x}{r^3}, \qquad \frac{d^2 y}{dt^2} = -\frac{GM y}{r^3}, \qquad r = \sqrt{x^2 + y^2}$$

where $M$ is the stellar mass and the planet is treated as a massless test particle. Rewrite this as a first-order system of four equations for $(x, y, v_x, v_y)$ and integrate with RK4.

1. Build the orbital model using the equations above. A circular orbit is acceptable as the baseline; if you want to explore eccentricity, you must justify the additional parameter and verify that the eccentric orbit conserves energy.
2. Use RK4 to integrate the orbit over at least 5 orbital periods.
3. Identify transit times from the integrated orbit. A transit occurs when the planet crosses the line of sight to the observer (e.g., when $y$ changes sign while $x > 0$, or an equivalent geometric criterion you define and document).
4. Compare the dynamical transit times to the linear ephemeris $t_n = t_0 + nP$ from your midterm fit. For a circular orbit this comparison should show near-perfect agreement; if it does, state why explicitly and discuss what physical effects (eccentricity, perturbations) would break the linear ephemeris.
5. State clearly which physical assumptions you fixed, such as stellar mass, orbital plane orientation, or code units.

### Part G — Bootstrap or injection-recovery study

Choose **one** of the following as a required random-sampling component:

1. **Bootstrap / residual resampling:** resample the observed fluxes or fitted residuals, rerun the fit, and build empirical distributions for at least two fitted parameters. Use a fixed random seed (Newman §10.1.2) for reproducibility.
2. **Injection-recovery:** inject synthetic transit signals into a detrended light curve or comparable noise model and measure the fraction recovered by your own pipeline across a grid of periods and depths. Use Gaussian noise realizations (Newman §10.1.6) where appropriate. Use at least a $4 \times 4$ grid in $(P, \delta)$ with at least 2–3 noise realizations per grid point (minimum 40 total trials).

Minimum scope:

- at least 100 bootstrap realizations, or
- at least 40 injected-signal trials on a grid of at least $4 \times 4$ in period and depth.

### Part H — Synthesis

1. Explain whether the dynamical orbit model is consistent with the midterm ephemeris.
2. Identify the largest uncertainty source in your final analysis.
3. State what your robustness study says about confidence in the detected signal.

## Suggested parameter choices

- One primary target analyzed deeply is the recommended baseline.
- For the orbit model, circular motion with a fixed stellar mass is acceptable if you state your assumptions clearly.
- Integrate for at least 5 orbital periods so that transit timing predictions are not based on a single cycle.
- If using injection-recovery, keep the grid modest and interpretable rather than exhaustive.

## Deliverables

- Updated `docs/README.md` with a carry-forward record (see `projects/final-project-workflow.md` for the required format).
- Plots showing:
  - the retained midterm periodogram and folded transit,
  - the dynamical orbit or projected-separation model,
  - observed-versus-predicted transit timing information,
  - either bootstrap distributions or an injection-recovery summary plot.
- A table of final fitted parameters, with uncertainties or recovery metrics from the random-sampling analysis.
- Source code in `src/` and tests in `tests/` that reproduce the final analysis.

## Testing guidance

Write tests in `tests/` for the final-method additions.

### Part F — RK4 orbital model

- **Circular-orbit sanity check:** for a simple circular test case, the integrated orbit should preserve the expected radius within tolerance.
- **Transit-time finder check:** on a synthetic orbit with known conjunction spacing, your code should recover the expected transit cadence.
- **Energy conservation:** for a circular orbit, the total energy $E = \frac{1}{2}v^2 - GM/r$ should remain constant to within RK4 truncation error.

### Part G — Random-sampling method

- **Fixed-seed reproducibility:** bootstrap or injection-recovery results should be reproducible when a random seed is fixed.
- **Strong-signal recovery:** a high-depth or high-SNR injected signal should be recovered reliably by your own pipeline.
- **Edge case:** a bootstrap with zero added noise should return near-zero spread in fitted parameters.

### Pipeline integration

- **Baseline regression test:** at least one synthetic or simplified dataset should still pass through the retained midterm pipeline correctly after refactoring.

## Grading rubric (100 points)

- **Carry-forward integration of midterm code (10 pts):** your final repository clearly reuses and extends the midterm transit pipeline. (Your carry-forward documentation is also evaluated under the shared rubric in `projects/final-project-grading-rubric.md`.)
- **Dynamical ODE model (30 pts):** coherent orbit formulation, sensible RK4 integration, and useful comparison to the fitted ephemeris.
- **Bootstrap or injection-recovery analysis (25 pts):** meaningful random-sampling design and defensible uncertainty or robustness interpretation.
- **Scientific integration and interpretation (15 pts):** clear connection between the midterm fit, the orbit model, and the robustness study.
- **Validation, testing, and presentation (20 pts):** good tests, reproducible figures, and readable documentation.

## Common pitfalls

- **Trivial circular-orbit comparison:** for a perfectly circular orbit, the dynamical transit times will exactly match $t_0 + nP$, making the comparison trivial. This is expected — the point is to verify the RK4 machinery recovers the known result and to discuss what physical effects would break the linear ephemeris. Do not pretend the comparison reveals new physics if your model is purely circular.
- **Units mismatch:** if your midterm uses time in days and your orbit model uses SI or code units, the unit conversion for $P$ and $GM$ must be handled carefully. Document your unit system.
- **Injection-recovery grid too coarse:** injecting all signals at the same period and depth does not test detection robustness. Vary both $P$ and $\delta$ over a meaningful range.
- **Bootstrap on binned data:** bootstrapping phase-binned data instead of the original time-series can understate uncertainties. Resample the original data points, not the bins.
- **Orbital equations:** the equations provided above assume a test-particle limit (planet mass $\ll$ stellar mass). This is appropriate for exoplanets. Do not try to solve the full two-body problem.
