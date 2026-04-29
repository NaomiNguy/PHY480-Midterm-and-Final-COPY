# Exoplanet Transit Detection and Dynamical Modeling Pipeline

## 1. Project Overview

This project develops a complete computational pipeline for detecting and interpreting exoplanet transit signals in TESS light curve data. It is a direct extension of the midterm analysis, which focused on preprocessing, Fourier-based period detection, folding, and transit fitting.

The final project builds on that foundation by introducing:

- dynamical orbit modeling using RK4 integration  
- random-sampling robustness analysis (bootstrap or injection-recovery)  
- comparison between observationally fitted transit times and physically modeled orbital behavior  

The primary goal is not only to detect a transit signal, but to connect that signal to an underlying orbital model and quantify how reliable the detection is in the presence of noise and modeling assumptions.

---

## 2. Relationship to the Midterm

### 2.1 Carry-forward components

This project reuses and extends substantial portions of the midterm pipeline. The following elements are retained and form the front end of the final analysis:

- Light curve ingestion and preprocessing (Part A)  
- DFT-based period search (Part B)  
- Folding and period refinement (Part C)  
- Box transit model fitting (Part D)  
- Diagnostic plots and parameter reporting (Part E)  

These components are modular and remain usable on any of the provided TESS datasets.

### 2.2 What changed

The final project extends the midterm by adding new physically motivated and statistical components:

- **Part F:** RK4 orbital integration and extraction of predicted transit times  
- **Part G:** bootstrap or injection-recovery analysis to quantify robustness  
- **Part H:** synthesis connecting observational fits, orbital dynamics, and uncertainty  

### 2.3 Pipeline philosophy

The midterm pipeline is treated as a reusable baseline. The same workflow can be applied to different targets, but for the final project, one primary system is analyzed in greater depth. The additional components are layered on top of this baseline rather than replacing it.

---

## 3. Physical Setup

The system consists of:

- a central star of mass \(M\)  
- a planet treated as a massless test particle  
- a distant observer aligned with a fixed line of sight  

A transit occurs when the planet crosses the observer’s line of sight, producing a temporary dip in the observed stellar flux.

The key observable parameters extracted from the light curve are:

- \(P\): orbital period  
- \($\delta$): transit depth (fractional drop in brightness)  
- \($\tau$): transit duration  
- \($t_0$): reference transit epoch  

The midterm pipeline determines these parameters empirically. The final project then tests whether they are consistent with a dynamical orbital model governed by Newtonian gravity.

---

## 4. Part E — Locked Midterm Baseline

### Purpose

To establish a reproducible reference point for the final analysis by fixing the best-fit transit parameters from the midterm pipeline.

### Method

- Run the full preprocessing, period search, folding, and fitting pipeline  
- Extract the best-fit values of:
  - \(P\)
  - \($\delta$)
  - \($\tau$)
  - \($t_0$)

### Output

These parameters define a **linear ephemeris**:

$
t_n = t_0 + nP
$

This relation predicts the timing of future transits assuming a perfectly periodic orbit.

### Reproduction

```bash
python src/ex_part_e.py
```

---

## 5. Part F — Dynamical Orbit Model (RK4)

### 5.1 Governing equations

The orbital motion is modeled using the planar two-body equations:

$
\frac{d^2x}{dt^2} = -\frac{GMx}{r^3}, \quad
\frac{d^2y}{dt^2} = -\frac{GMy}{r^3}
$

$
r = \sqrt{x^2 + y^2}
$

These are rewritten as a first-order system in terms of position and velocity:

$
\frac{dx}{dt} = v_x, \quad \frac{dy}{dt} = v_y
$

$
\frac{dv_x}{dt} = -\frac{GMx}{r^3}, \quad
\frac{dv_y}{dt} = -\frac{GMy}{r^3}
$

---

### 5.2 RK4 integration

The equations of motion are integrated using the fourth-order Runge–Kutta (RK4) method.

This method is chosen because:

- it provides significantly higher accuracy than simple Euler integration  
- it maintains stability over many orbital periods  
- it has a truncation error that scales as \($O(h^4)$)  

The orbit is integrated for at least five full periods to ensure that the resulting transit timing pattern is robust.

---

### 5.3 Transit identification

A transit is identified using a geometric condition. In this project, a transit occurs when:

- the planet crosses the observer’s line of sight (i.e., \(y\) changes sign)  
- the planet is in front of the star (\(x > 0\))  

This criterion allows transit times to be extracted directly from the integrated orbit.

---

### 5.4 Comparison to ephemeris

The transit times obtained from RK4 integration are compared to the linear ephemeris:

$
t_n = t_0 + nP
$

For a circular orbit, the two should agree to within numerical precision.

### Interpretation

- Agreement confirms that the RK4 integration and ephemeris are consistent  
- Deviations would indicate additional physics, such as:
  - orbital eccentricity  
  - gravitational perturbations  
  - incorrect parameter assumptions  

---

### 5.5 Assumptions

- circular orbit (baseline case)  
- constant stellar mass  
- planar geometry  
- planet treated as a test particle ($(m \ll M$))  

---

## 6. Part G — Random Sampling Analysis

### Purpose

To quantify how sensitive the fitted parameters are to noise and to evaluate the reliability of the detected signal.

### Option 1: Bootstrap (implemented here)

- resample the observed light curve with replacement  
- rerun the transit fit on each resampled dataset  
- build distributions of fitted parameters  

### Option 2: Injection-recovery (alternative)

- inject synthetic transit signals into noisy data  
- measure how often the pipeline successfully recovers the signal  

---

### 6.1 Bootstrap method

- at least 100 realizations (reduced during testing for speed)  
- fixed random seed ensures reproducibility  

Outputs include distributions for:

- period  
- depth  
- duration  
- epoch  

The standard deviation of each distribution provides an uncertainty estimate.

---

### 6.2 Interpretation

- narrow distributions indicate stable parameter estimates  
- wide distributions indicate sensitivity to noise  
- irregular or multimodal distributions suggest ambiguity in the signal  

---

## 7. Part H — Synthesis

### Questions addressed

1. Is the dynamical orbit consistent with the fitted ephemeris?  
2. What is the dominant source of uncertainty in the analysis?  
3. How robust is the detected transit signal?  

### Key conclusions

- For a circular orbit, the RK4 model reproduces the linear ephemeris exactly, as expected  
- Any observed deviations would point to additional physical effects not included in the baseline model  
- Bootstrap results provide a quantitative measure of confidence in the fitted parameters  

---

## 8. Reproducing the Full Project

### 8.1 Run each part

From the project root directory:

```bash
python src/ex_part_f.py
python src/ex_part_g.py
python src/ex_part_h.py
```

---

### 8.2 Run tests

```bash
pytest -q
```

---

### 8.3 Generate final results

```bash
python src/ex_part_h.py
```

This produces:

- orbit visualization  
- transit timing comparison  
- bootstrap parameter distributions  
- summary interpretation  

### 8.4 Figures for reference
All figures for this project can be found under `graphs` in the repo.

### 8.5 Note on performance

For development and testing, Parts G and H use reduced bootstrap sizes and grid resolutions. The full analysis requires larger sample sizes (e.g., 100 bootstrap realizations or a full injection grid). Please look at the comments in Part G and H to see the true values needed.

---

## 9. Generated Outputs

The pipeline produces:

- periodogram (Part B)  
- folded light curve (Part C)  
- fitted transit model (Part D)  
- residual plots (Part E)  
- orbit trajectory (Part F)  
- transit timing comparison (Part F)  
- parameter distributions (Part G)  

---

## 10. Testing Strategy

### Part F tests

- orbit radius stability for circular motion  
- energy conservation under RK4 integration  
- correct spacing of transit times  

### Part G tests

- reproducibility with fixed random seed  
- recovery of strong injected signals  
- zero-noise bootstrap edge case  

### Pipeline tests

- regression test ensuring midterm pipeline still functions after extension  

---

## 11. Assumptions and Limitations

- box-shaped transit model (no limb darkening)  
- circular orbit baseline  
- approximate frequency grid for period search  
- manually implemented DFT (computationally expensive)  

---

## 12. Summary

This project combines:

- signal processing (DFT-based period detection)  
- numerical integration (RK4 orbital dynamics)  
- statistical methods (bootstrap uncertainty estimation)  
- physical modeling (two-body orbital motion)  

The result is a complete and reproducible computational pipeline that connects raw observational data to a physically interpretable orbital model while providing a quantitative measure of detection confidence.