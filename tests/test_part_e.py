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


def test_consistency_check_uses_folded_light_curve():
    """
    The best-fit period should match the dominant periodogram peak
    within tolerance, and the folded light curve should show a dip.
    """
    rng = np.random.default_rng(42)

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

    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux_obs)

    period_grid = np.linspace(3.0, 3.4, 41)
    depth_grid = np.linspace(0.010, 0.025, 31)
    duration_grid = np.linspace(0.10, 0.30, 31)
    epoch_grid = np.linspace(0.4, 1.1, 41)

    best_params, _ = ex_part_d.grid_search_box_fit(
        t,
        flux_obs,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
    )

    result = ex_part_e.consistency_check_with_folded_curve(
        t=t,
        flux=flux_obs,
        freq=freq,
        power=power,
        best_params=best_params,
        strongest_periods_func=ex_part_b.strongest_periods,
        fold_light_curve_func=ex_part_c.fold_light_curve,
        rtol=0.05,
    )

    assert result["consistent_period"]
    assert result["has_dip"]
    assert result["consistent"]


def test_folded_transit_depth_positive_for_transit_signal():
    """
    Folded transit depth should be positive for a real transit-like dip.
    """
    t = np.linspace(0.0, 20.0, 2000)

    period_true = 4.0
    depth_true = 0.02
    duration_true = 0.24
    epoch_true = 0.5

    flux = ex_part_d.box_transit_model(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
    )

    phase, flux_fold = ex_part_c.fold_light_curve(
        t - epoch_true,
        flux,
        period_true,
        centered=True,
    )

    width_phase = duration_true / period_true
    depth = ex_part_e.folded_transit_depth(
        phase,
        flux_fold,
        center=0.0,
        width=width_phase,
    )

    assert depth > 0.0


def test_report_best_fit_returns_expected_number_of_lines():
    """
    Reporting helper should return the formatted parameter summary.
    """
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