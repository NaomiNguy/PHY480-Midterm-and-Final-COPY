# Exoplanet Transit Detection Pipeline

## 1. Project Goal

This project analyzes **TESS light curve data** to identify and characterize a possible exoplanet transit signal. A transit appears as a small, repeated dip in the measured brightness of a star when an orbiting planet passes in front of it along our line of sight. The purpose of the pipeline is to:

1. clean the light curve data,
2. search for periodic structure,
3. refine the likely period by folding the data,
4. fit a simple transit model,
5. estimate parameter uncertainties, and
6. evaluate whether the fitted result is consistent with the period search.

The final outputs are a best-fit transit period, depth, duration, and epoch, along with diagnostic plots that show the quality of the detection and fit.

---

## 2. Physical Setup

The underlying physical picture is a star observed repeatedly over time by the TESS mission. The data consist of measurements of stellar brightness, or **flux**, as a function of time. If a planet transits the star, the light curve will contain periodic decreases in flux with several important properties:

* **Period (P):** the time between repeated transit events. Physically, this is the orbital period of the transiting object.
* **Depth (\delta):** the fractional drop in brightness during transit. In a simple approximation, deeper transits correspond to larger planets relative to the star.
* **Duration (\tau):** the length of time that the transit lasts. This depends on the orbital geometry and transit speed.
* **Epoch (t_0):** the central time of a reference transit.

The observational challenge is that real light curves are noisy and often contain slow instrumental or astrophysical trends unrelated to the transit itself. The transit signal is also usually weak compared with the baseline stellar flux, so preprocessing and careful numerical analysis are necessary.

---

## 3. Input Data

The project uses TESS light curve files stored in the `data/` directory. Each file contains three columns:

* `time`: observation time
* `flux`: measured brightness
* `flux_err`: uncertainty in the measured brightness

The times are large astronomical timestamps, so one of the first preprocessing steps is to convert them into a relative time axis. This makes the numbers easier to work with and improves numerical stability in later calculations.

---

## 4. Pipeline Overview

The workflow is divided into five parts:

* **Part A:** ingest, normalize, detrend, smooth, and differentiate the light curve
* **Part B:** compute a Fourier-based period search from scratch
* **Part C:** fold the light curve on candidate periods and choose the best one
* **Part D:** fit a simple box transit model and estimate uncertainties
* **Part E:** interpret the result and generate final diagnostic plots

Each part is implemented in its own source file in `src/`.

---

## 5. Part A — Data Ingestion and Cleaning

### Purpose

The raw TESS light curve is not used directly. Before searching for periodic structure, the data are cleaned so that the later analysis focuses on real repeating features instead of long-term drifts or point-to-point noise.

### Method

#### 5.1 Relative time axis

The time values are transformed using

$
t_{\mathrm{rel}} = t - t_0
$

where (t_0) is the first observation time. This does not change the physical spacing between observations; it only shifts the origin of the time axis.

This is useful because the original times can be very large, while the relevant physics depends only on time differences and periodic structure.

#### 5.2 Flux normalization

The flux is normalized by dividing by its median value:

$
F_{\mathrm{norm}} = \frac{F}{\mathrm{median}(F)}
$

After this step, the baseline flux is near 1. This makes it easier to interpret transit depth as a fractional decrease in brightness.

#### 5.3 Detrending

A linear trend is fitted and removed from the normalized flux. The goal is to suppress slow instrumental or astrophysical variations that are not part of the transit signal.

In this project, a simple linear polynomial is used. The cleaned flux is formed by dividing the normalized flux by the fitted trend.

This is a simple detrending method, but it is appropriate for an introductory pipeline because it is transparent and easy to interpret.

#### 5.4 Smoothing

A moving average is applied to reduce high-frequency noise. Smoothing is especially helpful before the period search and before estimating slopes in the folded transit.

The moving average replaces each point by the average of its neighbors within a chosen window. This suppresses short-timescale scatter while preserving the broader transit shape.

#### 5.5 Differentiation

A numerical derivative is computed using finite differences. Differentiation is not used directly for the initial period search, but it becomes useful later when estimating the approximate ingress and egress of the transit from the folded light curve.

The derivative highlights places where the flux changes most rapidly. In a transit-shaped signal, the steepest negative slope usually corresponds to ingress, and the steepest positive slope corresponds to egress.

### Why this matters

Without cleaning, the period search could be dominated by long-term drift or random fluctuations. Without smoothing, the derivative would be too noisy to interpret physically. Part A therefore prepares the data for all later steps.

---

## 6. Part B — Period Search with a Fourier Transform

### Purpose

The next step is to identify repeating timescales in the cleaned light curve. This is done by transforming the signal from the time domain into the frequency domain.

### Standard DFT issue

The standard discrete Fourier transform is usually written as

$
c_k = \sum_{n=0}^{N-1} y_n e^{-2\pi i kn/N}
$

which assumes that the data are sampled at perfectly uniform intervals. TESS data are not always exactly evenly spaced, so this project instead uses a Fourier sum based on the **actual observation times**:

$
c(f) = \sum_{n=0}^{N-1} y_n e^{-2\pi i f t_n}
$

This preserves the “from scratch” requirement while avoiding the incorrect assumption of perfect uniform sampling.

### Power spectrum

The power at each trial frequency is computed as

$
P(f) = |c(f)|^2
$

Large peaks in the power spectrum indicate frequencies where the signal contains strong repeating structure.

### Frequency grid

A grid of trial frequencies must still be chosen. In this project, that grid is based on:

* the total observing baseline (T), which controls the frequency resolution,
* the median cadence (\Delta t), which gives an approximate upper frequency limit.

This is a practical compromise: the transform itself uses the real timestamps, while the search grid is chosen using physically sensible scales from the data.

### Output of Part B

The strongest peaks in the power spectrum are converted into candidate periods:

$
P = \frac{1}{f}
$

These candidate periods are passed directly into Part C. This means the project pipeline is connected: the period refinement does not rely on manually chosen trial periods.

### Why this matters

The Fourier analysis gives an objective first guess at the dominant repeating timescales in the data. It does not by itself prove that a signal is a transit, but it identifies the best candidates for further examination.

---

## 7. Part C — Folding and Period Refinement

### Purpose

A true periodic signal should line up when the light curve is folded on the correct period. Folding compresses many cycles of the light curve onto one phase interval so that repeated features can be compared directly.

### Folding

Given a trial period (P), the phase is computed as

$
\phi = \left(\frac{t}{P} \bmod 1\right)
$

or in centered form,

$
\phi_{\mathrm{centered}} = \left[\left(\frac{t}{P} + 0.5\right)\bmod 1\right] - 0.5
$

The centered version is especially useful for transit analysis, because it places the candidate transit near phase 0.

### Objective criterion

Several candidate periods come from Part B, so an objective way is needed to choose the best one.

This project evaluates candidate periods using coherence-based metrics such as:

* **binned scatter:** lower scatter means repeated cycles align more cleanly,
* **transit-window scatter:** lower scatter in the expected transit region indicates a more coherent dip.

The correct period should bring all transit events into alignment, so the folded light curve should look tighter and less blurred.

### Duration estimate from slopes

After folding on the best period, the folded flux is smoothed and differentiated. The steepest negative slope is interpreted as approximate ingress, and the steepest positive slope as approximate egress.

The phase separation between these features gives an estimated transit duration in phase units, which can be converted back into time using the best period.

This provides a physically motivated initial guess for the transit duration used in the fitting stage.

### Why this matters

Part B can identify dominant periodicities, but transit-like signals often generate harmonics or nearby peaks. Folding gives a direct visual and numerical way to decide which candidate period produces the most coherent transit signal.

---

## 8. Part D — Transit Model Fitting

### Purpose

Once the likely period has been identified, the next goal is to fit a simple model to the transit signal and estimate quantitative parameters.

### Model choice

This project uses a **box-shaped transit model**. The model is intentionally simple and is not meant to represent all physical details such as limb darkening. Instead, it provides an interpretable first-order estimate of the transit geometry.

The model parameters are:

* (P): period
* ($\delta$): depth
* ($\tau$): duration
* ($t_0$): epoch

The model flux is defined as:

* out of transit: flux = 1
* in transit: flux = (1 - $\delta$)

A point is considered in transit if its phase lies within half the transit duration of the transit center.

### Fitting method

The parameters are found using a grid search combined with a least-squares or (\chi^2)-style objective. For each trial parameter combination, the model is evaluated at the observed times and compared with the data.

The best-fit parameters are the ones that minimize the mismatch between the data and the model.

### Initial guesses

The fitting grids are centered on estimates derived from earlier parts of the pipeline:

* the best period from Part C,
* the transit duration estimated from slopes,
* an approximate depth from the minimum observed flux,
* an approximate epoch from the time of minimum flux.

Using physically motivated starting ranges makes the grid search more efficient and more stable.

### Uncertainty estimation

Uncertainties are estimated with bootstrap resampling. The data are repeatedly resampled with replacement, the model is refit, and the spread in the fitted parameter values is used as an uncertainty estimate.

This provides a simple way to quantify how sensitive the fitted parameters are to noise in the data.

### Why this matters

The period search only says where repeating power exists. The model fitting step turns that repeating signal into physically interpretable quantities and adds uncertainty estimates, which are essential for scientific reporting.

---

## 9. Part E — Interpretation and Diagnostics

### Purpose

The final stage summarizes the result and checks whether the fitted transit parameters are consistent with the earlier stages of the analysis.

### Best-fit parameter report

Part E prints the final values of:

* period
* depth
* duration
* epoch

along with their estimated uncertainties.

### Consistency check

A basic consistency check compares the final fitted period with the dominant periodogram peak from Part B. These should agree within a reasonable tolerance if the pipeline is behaving sensibly.

### Diagnostic plots

Part E produces several plots:

#### 9.1 Periodogram

This shows the Fourier power as a function of frequency. A strong peak indicates a candidate repeating timescale.

#### 9.2 Folded light curve with model

This plot overlays the folded data with the fitted transit model. It is one of the most important diagnostics because it shows whether the model aligns with the observed dip.

#### 9.3 Residuals

The residuals show the difference between the data and the model. If the fit is reasonable, the residuals should be centered near zero and should not show a strong leftover transit structure.

### Why this matters

A scientific result is not complete without interpretation and diagnostics. Part E ties together the earlier steps and makes it possible to judge whether the fitted solution is believable.

---

## 10. Reproducing the Full Project

### 10.1 Run each part separately

From the project root directory:

```bash
python src/ex_part_a.py
python src/ex_part_b.py
python src/ex_part_c.py
python src/ex_part_d.py
python src/ex_part_e.py
```

### 10.2 Run the full validation suite

```bash
pytest -q
```

### 10.3 Generate final figures and final results

To reproduce the final reported output and diagnostic plots, run:

```bash
python src/ex_part_e.py
```

This should produce:

* best-fit parameter summary,
* consistency check against the periodogram,
* periodogram plot,
* folded light curve with model,
* residual plot.

### 10.4 Figures for reference
All figures for this project can be found under `graphs` in the repo.

---

## 11. Final values
* (P): 21.536464 ± 0.228762 days
* ($\delta$): 0.333820 ± 0.057887
* ($\tau$): 1.076823 ± 0.072235 days
* ($t_0$): 21.536464 ± 0.000000 days
* Dominant periodogram period = 5.408993 days

---

## 12. Assumptions and Limitations

This project makes several deliberate simplifications:

### 12.1 Simple transit model

The box-shaped model ignores limb darkening and does not attempt a full physical transit fit. This makes the model easier to implement and interpret, but less realistic than a full astrophysical model.

### 12.2 Approximate frequency grid

Even though the Fourier sum uses actual timestamps, the trial frequency grid is still based on the total baseline and median cadence. This is a practical choice for an introductory project.

### 12.3 Computational cost

The Fourier transform is implemented manually from scratch, so it is much slower than FFT-based methods. For this reason, the data are downsampled before the period search to keep runtime reasonable.

### 12.4 Noise model

Least-squares fitting and bootstrap resampling give useful uncertainty estimates, but they do not capture every possible source of systematic error.

---

## 13. Scientific Interpretation

A successful run of the pipeline supports the interpretation that the light curve contains a repeating dimming event consistent with a transit-like signal. The period identifies the repetition timescale, the depth measures the size of the brightness drop, the duration estimates the crossing time, and the epoch gives the timing of a reference transit.

Because the pipeline combines period search, folding, slope-based duration estimation, model fitting, and consistency checks, it provides multiple layers of evidence for whether the detected signal is coherent and transit-like.

---

## 13. Summary

This project implements an end-to-end computational physics workflow for exoplanet transit detection using TESS light curve data. The analysis proceeds from data cleaning and smoothing to a Fourier-based period search, folding-based refinement, box-model fitting, uncertainty estimation, and final diagnostic interpretation.

The numerical methods are deliberately explicit rather than black-box. The Fourier analysis is written from scratch, the model fitting is transparent, and the physical meaning of each step is preserved throughout the pipeline. The final result is a reproducible method for turning a noisy light curve into a quantitative transit candidate description.
