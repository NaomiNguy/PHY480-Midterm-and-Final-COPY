[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5O0tF847)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=22883375&assignment_repo_type=AssignmentRepo)
# Midterm Project 2 — Exoplanet Transit Search with DFT + Folding

## PHY 480, Michigan State University — Spring 2026

### Professor Sean Couch

## Overview
You will analyze *TESS* light curves to detect and characterize transiting exoplanets using Fourier techniques, light-curve folding, and model fitting. This project goes beyond the lab by using DFT-based period search and by building a compact, reproducible “planet finder” pipeline. The data are provided in `projects/Lab8_Transits_SS25/` and must be reused here (but your analysis must go beyond the lab workflow).

## Suggested background
- NASA: TESS mission overview — https://science.nasa.gov/mission/tess/
- NASA: How we find and characterize exoplanets — https://science.nasa.gov/exoplanets/how-we-find-and-characterize/
- Wikipedia: Transit method — https://en.wikipedia.org/wiki/Transit_method
- Astropy docs: Box Least Squares (BLS) periodogram — https://docs.astropy.org/en/stable/timeseries/bls.html

## Project-specific requirements 
These are the common project expectations as they apply **specifically** to this topic. The global list is in `projects/README.md`.

1. **Original code + course standards**
   - Implement your pipeline in `src/` following `admin/codingStandards.md`.
   - No heavy computation or `input()` at import time; use a `main()` guard.
   - Run Ruff locally before pushing:
     - `ruff format .`
     - `ruff check . --show-source`

2. **GitHub workflow**
   - Use branches and commit as you finish each major part (A–E).
   - Your history should show incremental work, not one final commit.

3. **Academic integrity + AI use**
   - Do **not** use AI to write your solution wholesale.
   - If you use AI for help or debugging, add a short citation in your `docs/README.md`:
     - Example: “AI assistance: <tool>, used for <task> on <date>.”

4. **Reproducible documentation**
   - Your `docs/README.md` must explain the physical setup, numerical methods, and how to reproduce your results.
   - Include the exact commands to run your analysis and regenerate figures.

5. **Analysis and plotting**
   - You must produce and interpret a periodogram, a folded light curve with model, and residuals.
   - Label axes with units and annotate the best-fit period and transit parameters.

6. **Student-written unit tests**
   - You must write tests in `tests/` that verify the correctness of **your** numerical methods.
   - Use examples from `inclass/` as a model for structure and tolerances.
   - See “Testing guidance by part” below for concrete test targets.

## Goals
- Build a DFT-based period search that identifies candidate transit periods.
- Use light-curve folding to refine the period and extract transit parameters.
- Fit a simple transit model and estimate uncertainties.
- Interpret sampling, aliasing, and periodic-extension artifacts.

## Data
Use the provided datasets:
- `data/Lab8_Transits_SS25/TESSA_lc.dat`
- `data/Lab8_Transits_SS25/TESSB_lc.dat`
- `data/Lab8_Transits_SS25/TESSC_lc.dat`
- `data/Lab8_Transits_SS25/TESSD_lc.dat`

You may analyze one target deeply or multiple targets more lightly, but your pipeline must work for **any** of them. If you choose a single target, you must complete all parts A–E with full uncertainty estimation. If you analyze multiple targets, each must include a period search, folding, and a basic model fit (uncertainties can be deeper on one target).

## Required techniques 
- **DFT-based period search** and power spectrum interpretation (ICA-08 + PCA-09).
- **Fourier-series reasoning**: discuss periodic extension and implications for nonperiodic segments (PCA-09).
- **Nonlinear optimization or root finding** for model fitting (ICA-07).
- **Numerical differentiation or smoothing** to locate ingress/egress or estimate transit duration (ICA-04 + PCA-05).

## What you must implement
You can choose your own function names, but your code must be modular and testable. At a minimum, your `src/` code should include functions that:

- Load and preprocess a light curve (time normalization and detrending/normalization).
- Compute a DFT and power spectrum on uneven/finite sampling choices you define.
- Identify candidate periods from the power spectrum.
- Fold a light curve on a trial period and compute a phase curve.
- Define and fit a box or trapezoid transit model with parameters $(P, \delta, \tau, t_0)$.
- Estimate parameter uncertainties (bootstrap or residual-based).

Your repository must include:

- `src/` implementation code (no notebooks-only submissions).
- `tests/` with your own unit tests.
- `README.md` with method summary + reproduction commands.
- `docs/README.md` with method summary + reproduction commands.

## Tasks
### Part A — Ingest and clean
1. Load a light curve and convert times to a relative axis (e.g., $t\leftarrow t-t_0$).
2. Detrend or normalize if necessary (document your choice and show a before/after plot or summary statistic).

### Part B — DFT period search
1. Implement a DFT on the sampled fluxes and compute the power spectrum $|c_k|^2$.
2. Identify candidate periods from the strongest nonzero peaks. Explain how sampling cadence sets the frequency grid.
3. Discuss aliasing and periodic-extension artifacts explicitly.
4. Reference: Newman, Chapter 7a “Fourier transforms,” Section on the discrete Fourier transform (DFT).

### Part C — Folding and refinement
1. Fold the light curve on each candidate period.
2. Choose the best period by an objective criterion (e.g., minimize scatter in the folded transit window or maximize transit depth significance).
3. Report the chosen period and show the folded curve with phase in $[0,1)$ or $[-0.5,0.5)$.

### Part D — Transit model fit
1. Define a simple transit model (box or trapezoid) with parameters: period $P$, depth $\delta$, duration $\tau$, and epoch $t_0$.
2. Fit the model using least squares or a simple optimizer.
3. Estimate uncertainties (bootstrap or residual-based) and report them alongside best-fit parameters.

### Part E — Interpretation
1. Report best-fit parameters with uncertainties.
2. Provide at least one diagnostic plot: periodogram, folded light curve with model, residuals.

## Suggested parameter choices 
- Use time in days and normalize flux to median 1.0.
- DFT frequency grid: from $1/T$ to Nyquist-like cadence limit using at least 2000 trial frequencies (state your choice).
- Folding: 50–200 phase bins for visualization; use unbinned data for fitting.
- Initial guesses: depth from min flux, duration from ingress/egress estimates, $t_0$ from deepest transit center.

## Deliverables
- `docs/README.md` explaining methods, reasoning, and key results.
- Plots:
  - Power spectrum with labeled peaks.
  - Folded light curve with best-fit model.
  - Residuals vs phase.
- Table of fitted transit parameters for each analyzed target.
- Code in `src/` with a reproducible pipeline.

## Testing guidance by part 
Write tests in `tests/` for **your** functions. These are examples of strong, focused tests.

### Part A — Ingest and clean
- **Normalization check:** after normalization, median flux is near 1.0 for a synthetic or simple subset.
- **Detrending sanity:** detrending a constant signal returns (approximately) the same constant.

### Part B — DFT period search
- **Synthetic sinusoid:** a pure sine wave at known period yields a dominant peak at that period.
- **Injected transit:** a synthetic box-transit signal yields a peak near the injected period.

### Part C — Folding and refinement
- **Correct period improves coherence:** folding at the injected period yields lower scatter in the transit window than a nearby incorrect period.

### Part D — Transit model fit
- **Parameter recovery:** fit recovers injected $(P, \delta, \tau, t_0)$ within tolerance for synthetic data.
- **Uncertainty sanity:** uncertainty estimates are nonzero and scale sensibly with added noise.

### Part E — Interpretation
- **Consistency check:** the best-fit period matches the dominant periodogram peak within tolerance.

## Grading rubric (100 points)
- **DFT period search (25 pts):** correct spectrum, clear period identification, aliasing discussion.
- **Folding + refinement (20 pts):** justified selection of best period.
- **Model fit + uncertainty (25 pts):** correct model, fit quality, uncertainty method.
- **Numerical methods integration (15 pts):** differentiation/smoothing used appropriately.
- **Presentation & reproducibility (15 pts):** clean plots, clear README, runnable code.
