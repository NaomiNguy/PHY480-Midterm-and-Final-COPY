import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_b
import ex_part_c
import ex_part_d


def test_folded_light_curve():
    """
    The best-fit period should be consistent with the dominant
    periodogram peak, and when folding on that best-fit period,
    the folded light curve should show a clear transit dip near phase 0.
    """
    rng = np.random.default_rng(42)

    # Synthetic transit signal
    t = np.linspace(0.0, 40.0, 3000)

    period_true = 3.2
    depth_true = 0.018
    duration_true = 0.20
    epoch_true = 0.75

    flux_true = ex_part_d.box_transit_model(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
    )

    sigma = 0.001
    flux_obs = flux_true + rng.normal(0.0, sigma, size=len(t))
    flux_err = np.full_like(t, sigma)

    # Part B: dominant periodogram peak
    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux_obs)
    peak_freqs, peak_periods, _ = ex_part_b.strongest_periods(freq, power, n_peaks=3)

    dominant_period = peak_periods[np.argmin(np.abs(peak_periods - period_true))]

    # Part D: fit near the dominant period
    period_grid = np.linspace(dominant_period * 0.95, dominant_period * 1.05, 41)
    depth_grid = np.linspace(0.010, 0.025, 31)
    duration_grid = np.linspace(0.10, 0.30, 31)
    epoch_grid = np.linspace(0.4, 1.1, 41)

    best_params, best_chi2 = ex_part_d.grid_search_box_fit(
        t,
        flux_obs,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
    )

    best_fit_period = best_params["period"]
    best_fit_epoch = best_params["epoch"]

    # Part E: fold the light curve on the best-fit period
    phase, flux_fold = ex_part_c.fold_light_curve(
        t - best_fit_epoch,
        flux_obs,
        best_fit_period,
        centered=True,
    )

    # Transit window in folded phase
    width_phase = best_params["duration"] / best_fit_period
    in_transit = np.abs(phase) < (width_phase / 2.0)
    out_of_transit = ~in_transit

    mean_in = np.mean(flux_fold[in_transit])
    mean_out = np.mean(flux_fold[out_of_transit])

    # Check 1: folded curve has a real dip
    assert mean_in < mean_out

    # Check 2: best-fit period agrees with dominant periodogram peak
    assert np.isclose(best_fit_period, dominant_period, rtol=0.05)