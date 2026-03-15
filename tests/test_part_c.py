import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_c


def test_correct_period_improves_transit_coherence():
    """
    Folding at the true injected period should produce lower
    scatter in the transit window than folding at a nearby
    incorrect period.
    """
    rng = np.random.default_rng(42)

    period_true = 6.0
    period_wrong = 6.3

    t = np.linspace(0.0, 200.0, 4000)
    flux = np.ones_like(t)

    # Inject a repeating box transit centered at phase 0
    depth = 0.02
    duration_phase = 0.08  # transit width in phase units

    phase_true = ((t / period_true + 0.5) % 1.0) - 0.5
    in_transit_true = np.abs(phase_true) < (duration_phase / 2.0)
    flux[in_transit_true] -= depth

    # Add a little noise
    flux += rng.normal(0.0, 0.002, size=len(flux))

    # Fold at true period
    phase_fold_true, flux_fold_true = ex_part_c.fold_light_curve(
        t, flux, period_true, centered=True
    )

    # Fold at incorrect nearby period
    phase_fold_wrong, flux_fold_wrong = ex_part_c.fold_light_curve(
        t, flux, period_wrong, centered=True
    )

    # Measure scatter inside the expected transit window
    scatter_true = ex_part_c.transit_window_scatter(
        phase_fold_true, flux_fold_true, center=0.0, width=duration_phase
    )
    scatter_wrong = ex_part_c.transit_window_scatter(
        phase_fold_wrong, flux_fold_wrong, center=0.0, width=duration_phase
    )

    assert scatter_true < scatter_wrong