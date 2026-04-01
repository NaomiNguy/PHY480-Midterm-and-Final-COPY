import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_c


def test_fold_phase_range_zero_to_one():
    t = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    flux = np.ones_like(t)
    period = 2.0

    phase, _ = ex_part_c.fold_light_curve(t, flux, period, centered=False)

    assert np.all(phase >= 0.0)
    assert np.all(phase < 1.0)


def test_fold_phase_range_centered():
    t = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    flux = np.ones_like(t)
    period = 2.0

    phase, _ = ex_part_c.fold_light_curve(t, flux, period, centered=True)

    assert np.all(phase >= -0.5)
    assert np.all(phase < 0.5)


def test_correct_period_improves_transit_coherence():
    rng = np.random.default_rng(42)

    period_true = 6.0
    period_wrong = 6.3

    t = np.linspace(0.0, 200.0, 4000)
    flux = np.ones_like(t)

    depth = 0.02
    duration_phase = 0.08

    phase_true = ((t / period_true + 0.5) % 1.0) - 0.5
    in_transit_true = np.abs(phase_true) < (duration_phase / 2.0)
    flux[in_transit_true] -= depth
    flux += rng.normal(0.0, 0.002, size=len(flux))

    phase_fold_true, flux_fold_true = ex_part_c.fold_light_curve(
        t, flux, period_true, centered=True
    )
    phase_fold_wrong, flux_fold_wrong = ex_part_c.fold_light_curve(
        t, flux, period_wrong, centered=True
    )

    scatter_true = ex_part_c.transit_window_scatter(
        phase_fold_true, flux_fold_true, center=0.0, width=duration_phase
    )
    scatter_wrong = ex_part_c.transit_window_scatter(
        phase_fold_wrong, flux_fold_wrong, center=0.0, width=duration_phase
    )

    assert scatter_true < scatter_wrong


def test_duration_estimate_is_positive():
    period_true = 5.0
    t = np.linspace(0.0, 100.0, 3000)
    flux = np.ones_like(t)

    depth = 0.02
    duration_phase = 0.10

    phase_true = ((t / period_true + 0.5) % 1.0) - 0.5
    in_transit = np.abs(phase_true) < (duration_phase / 2.0)
    flux[in_transit] -= depth

    phase, flux_fold = ex_part_c.fold_light_curve(t, flux, period_true, centered=True)
    duration_phase_est, duration_time_est, *_ = ex_part_c.estimate_duration_from_slopes(
        phase, flux_fold, smooth_window=11, period=period_true
    )

    assert duration_phase_est > 0.0
    assert duration_time_est > 0.0