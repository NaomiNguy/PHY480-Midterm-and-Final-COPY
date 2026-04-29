import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import ex_part_g
import ex_part_d


def test_inject_transit_reproducible_with_fixed_seed():
    t = np.linspace(0.0, 20.0, 1000)

    flux1 = ex_part_g.inject_transit(
        t,
        period=3.0,
        depth=0.02,
        duration=0.2,
        epoch=0.5,
        noise_sigma=0.001,
        seed=42,
    )

    flux2 = ex_part_g.inject_transit(
        t,
        period=3.0,
        depth=0.02,
        duration=0.2,
        epoch=0.5,
        noise_sigma=0.001,
        seed=42,
    )

    assert np.allclose(flux1, flux2)


def test_strong_signal_injection_recovery():
    t = np.linspace(0.0, 30.0, 1000)

    period_values = np.array([3.0])
    depth_values = np.array([0.05])

    recovery = ex_part_g.injection_recovery_grid(
        t,
        period_values,
        depth_values,
        duration=0.3,
        epoch=0.5,
        noise_sigma=0.0005,
        n_realizations=2,
        tolerance=0.10,
        seed=123,
    )

    assert recovery.shape == (1, 1)
    assert recovery[0, 0] >= 0.5


def test_bootstrap_fixed_seed_reproducible():
    t = np.linspace(0.0, 20.0, 800)

    period_true = 3.0
    depth_true = 0.02
    duration_true = 0.2
    epoch_true = 0.5
    sigma = 0.001

    flux = ex_part_g.inject_transit(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
        noise_sigma=sigma,
        seed=7,
    )
    flux_err = np.full_like(t, sigma)

    period_grid = np.linspace(2.8, 3.2, 11)
    depth_grid = np.linspace(0.015, 0.025, 11)
    duration_grid = np.linspace(0.15, 0.25, 9)
    epoch_grid = np.linspace(0.4, 0.6, 9)

    samples1, summary1 = ex_part_g.bootstrap_transit_fit(
        t,
        flux,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=5,
        seed=99,
    )

    samples2, summary2 = ex_part_g.bootstrap_transit_fit(
        t,
        flux,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=5,
        seed=99,
    )

    assert np.allclose(samples1, samples2)

    for key in summary1:
        assert np.isclose(summary1[key], summary2[key])


def test_zero_noise_bootstrap_has_small_spread():
    t = np.linspace(0.0, 20.0, 800)

    period_true = 3.0
    depth_true = 0.02
    duration_true = 0.2
    epoch_true = 0.5

    flux = ex_part_d.box_transit_model(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
    )
    flux_err = np.full_like(t, 1e-6)

    period_grid = np.array([period_true])
    depth_grid = np.array([depth_true])
    duration_grid = np.array([duration_true])
    epoch_grid = np.array([epoch_true])

    samples, summary = ex_part_g.bootstrap_transit_fit(
        t,
        flux,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=5,
        seed=42,
    )

    assert summary["period_std"] == 0.0
    assert summary["depth_std"] == 0.0
    assert summary["duration_std"] == 0.0
    assert summary["epoch_std"] == 0.0