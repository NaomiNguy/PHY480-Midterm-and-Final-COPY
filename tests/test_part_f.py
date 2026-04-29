import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import ex_part_f


def test_circular_orbit_preserves_radius():
    period = 2.0
    times, states = ex_part_f.integrate_orbit(
        period,
        n_periods=2,
        steps_per_period=400,
        gm=1.0,
    )

    x = states[:, 0]
    y = states[:, 1]
    r = np.sqrt(x**2 + y**2)

    assert np.max(np.abs(r - r[0])) < 1e-5


def test_energy_conservation_circular_orbit():
    period = 2.0
    times, states = ex_part_f.integrate_orbit(
        period,
        n_periods=2,
        steps_per_period=400,
        gm=1.0,
    )

    energy = ex_part_f.orbital_energy(states, gm=1.0)
    drift = np.max(np.abs(energy - energy[0]))

    assert drift < 1e-6


def test_transit_times_have_expected_spacing():
    period = 3.0
    times, states = ex_part_f.integrate_orbit(
        period,
        n_periods=5,
        steps_per_period=500,
        gm=1.0,
    )

    transit_times = ex_part_f.find_transit_times(times, states)

    spacings = np.diff(transit_times)

    assert len(transit_times) >= 5
    assert np.allclose(spacings, period, rtol=1e-3, atol=1e-3)


def test_ephemeris_residuals_near_zero_for_circular_orbit():
    period = 3.0
    epoch = 0.0

    times, states = ex_part_f.integrate_orbit(
        period,
        n_periods=5,
        steps_per_period=500,
        gm=1.0,
    )

    transit_times = ex_part_f.find_transit_times(times, states)
    predicted, residuals = ex_part_f.compare_to_ephemeris(
        transit_times,
        period,
        epoch,
    )

    assert np.max(np.abs(residuals)) < 1e-2