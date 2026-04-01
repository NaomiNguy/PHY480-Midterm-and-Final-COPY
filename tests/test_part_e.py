import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_b
import ex_part_c
import ex_part_d
import ex_part_e


def test_folded_transit_depth_positive_for_transit_signal():
    t = np.linspace(0.0, 20.0, 2000)

    period_true = 4.0
    depth_true = 0.02
    duration_true = 0.24
    epoch_true = 0.5

    flux = ex_part_d.box_transit_model(
        t, period_true, depth_true, duration_true, epoch_true
    )

    phase, flux_fold = ex_part_c.fold_light_curve(
        t - epoch_true, flux, period_true, centered=True
    )

    width_phase = duration_true / period_true

    in_transit = np.abs(phase) < (width_phase / 2.0)
    out_of_transit = ~in_transit

    depth = np.mean(flux_fold[out_of_transit]) - np.mean(flux_fold[in_transit])

    assert depth > 0.0


def test_best_fit_period_matches_dominant_periodogram_peak_using_folded_curve():
    rng = np.random.default_rng(42)

    t = np.linspace(0.0, 40.0, 2500)

    period_true = 3.2
    depth_true = 0.018
    duration_true = 0.20
    epoch_true = 0.75

    flux_true = ex_part_d.box_transit_model(
        t, period_true, depth_true, duration_true, epoch_true
    )

    sigma = 0.001
    flux_obs = flux_true + rng.normal(0.0, sigma, size=len(t))
    flux_err = np.full_like(t, sigma)

    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux_obs, nfreq=500)
    dominant_period = ex_part_e.dominant_period_from_periodogram(freq, power)

    period_grid = np.linspace(dominant_period * 0.95, dominant_period * 1.05, 31)
    depth_grid = np.linspace(0.010, 0.025, 21)
    duration_grid = np.linspace(0.10, 0.30, 21)
    epoch_grid = np.linspace(0.4, 1.1, 31)

    best_params, _ = ex_part_d.grid_search_box_fit(
        t, flux_obs, flux_err,
        period_grid, depth_grid, duration_grid, epoch_grid
    )

    phase, flux_fold = ex_part_c.fold_light_curve(
        t - best_params["epoch"], flux_obs, best_params["period"], centered=True
    )

    width_phase = best_params["duration"] / best_params["period"]
    in_transit = np.abs(phase) < (width_phase / 2.0)
    out_of_transit = ~in_transit

    mean_in = np.mean(flux_fold[in_transit])
    mean_out = np.mean(flux_fold[out_of_transit])

    assert mean_in < mean_out
    assert np.isclose(best_params["period"], dominant_period, rtol=0.05)


def test_report_best_fit_returns_expected_lines():
    best_params = {
        "period": 3.2,
        "depth": 0.018,
        "duration": 0.20,
        "epoch": 0.75,
    }

    uncertainties = {
        "period_std": 0.01,
        "depth_std": 0.002,
        "duration_std": 0.01,
        "epoch_std": 0.02,
    }

    lines = ex_part_e.report_best_fit(best_params, uncertainties)

    assert len(lines) == 5
    assert "Best-fit transit parameters:" in lines[0]
    assert "P" in lines[1]
    assert "delta" in lines[2]
    assert "tau" in lines[3]
    assert "t0" in lines[4]