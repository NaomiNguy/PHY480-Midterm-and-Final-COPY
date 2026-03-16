import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_d


def test_parameter_recovery_synthetic_box_transit():
    """
    Fit should recover injected (P, delta, tau, t0)
    within reasonable tolerance for synthetic data.
    """
    rng = np.random.default_rng(42)

    t = np.linspace(0.0, 30.0, 3000)

    period_true = 3.0
    depth_true = 0.020
    duration_true = 0.24
    epoch_true = 0.60

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

    period_grid = np.linspace(2.8, 3.2, 41)
    depth_grid = np.linspace(0.015, 0.025, 41)
    duration_grid = np.linspace(0.18, 0.30, 41)
    epoch_grid = np.linspace(0.40, 0.80, 41)

    best_params, best_chi2 = ex_part_d.grid_search_box_fit(
        t,
        flux_obs,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
    )

    assert np.isclose(best_params["period"], period_true, rtol=0.03)
    assert np.isclose(best_params["depth"], depth_true, rtol=0.20)
    assert np.isclose(best_params["duration"], duration_true, rtol=0.20)
    assert np.isclose(best_params["epoch"], epoch_true, rtol=0.15)


def test_uncertainty_estimates_nonzero():
    """
    Bootstrap uncertainty estimates should be nonzero
    for noisy synthetic data.
    """
    rng = np.random.default_rng(123)

    t = np.linspace(0.0, 30.0, 2000)

    period_true = 4.0
    depth_true = 0.015
    duration_true = 0.20
    epoch_true = 0.75

    flux_true = ex_part_d.box_transit_model(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
    )

    sigma = 0.0015
    flux_obs = flux_true + rng.normal(0.0, sigma, size=len(t))
    flux_err = np.full_like(t, sigma)

    period_grid = np.linspace(3.8, 4.2, 21)
    depth_grid = np.linspace(0.010, 0.020, 21)
    duration_grid = np.linspace(0.15, 0.25, 21)
    epoch_grid = np.linspace(0.55, 0.95, 21)

    best_params, best_chi2, uncertainties, boot = ex_part_d.bootstrap_fit(
        t,
        flux_obs,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=30,
    )

    assert uncertainties["period_std"] > 0.0
    assert uncertainties["depth_std"] > 0.0
    assert uncertainties["duration_std"] > 0.0
    assert uncertainties["epoch_std"] > 0.0


def test_uncertainties_increase_with_noise():
    """
    Uncertainty estimates should scale sensibly:
    noisier data should generally produce larger uncertainties.
    """
    rng = np.random.default_rng(999)

    t = np.linspace(0.0, 30.0, 2000)

    period_true = 2.5
    depth_true = 0.018
    duration_true = 0.16
    epoch_true = 0.50

    flux_true = ex_part_d.box_transit_model(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
    )

    sigma_low = 0.0005
    sigma_high = 0.0030

    flux_low = flux_true + rng.normal(0.0, sigma_low, size=len(t))
    flux_high = flux_true + rng.normal(0.0, sigma_high, size=len(t))

    err_low = np.full_like(t, sigma_low)
    err_high = np.full_like(t, sigma_high)

    period_grid = np.linspace(2.3, 2.7, 21)
    depth_grid = np.linspace(0.012, 0.024, 21)
    duration_grid = np.linspace(0.12, 0.20, 21)
    epoch_grid = np.linspace(0.35, 0.65, 21)

    _, _, unc_low, _ = ex_part_d.bootstrap_fit(
        t,
        flux_low,
        err_low,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=25,
    )

    _, _, unc_high, _ = ex_part_d.bootstrap_fit(
        t,
        flux_high,
        err_high,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=25,
    )

    assert unc_high["period_std"] >= unc_low["period_std"]
    assert unc_high["depth_std"] >= unc_low["depth_std"]
    assert unc_high["duration_std"] >= unc_low["duration_std"]
    assert unc_high["epoch_std"] >= unc_low["epoch_std"]