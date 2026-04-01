import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_b


def test_sinusoid_peak_period():
    period_true = 5.0
    t = np.linspace(0.0, 100.0, 800)
    flux = np.sin(2.0 * np.pi * t / period_true)

    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux, nfreq=400)
    _, peak_periods, _ = ex_part_b.strongest_periods(freq, power, n_peaks=3)

    detected_period = peak_periods[np.argmin(np.abs(peak_periods - period_true))]
    assert np.isclose(detected_period, period_true, rtol=0.05)


def test_injected_box_transit_yields_peak_near_period():
    period_true = 8.0
    depth = 0.02
    duration = 0.3

    t = np.linspace(0.0, 200.0, 1200)
    flux = np.ones_like(t)

    phase = (((t - 0.0) / period_true + 0.5) % 1.0) - 0.5
    in_transit = np.abs(phase) < (duration / period_true) / 2.0
    flux[in_transit] -= depth

    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux, nfreq=500)
    _, peak_periods, _ = ex_part_b.strongest_periods(freq, power, n_peaks=5)

    detected_period = peak_periods[np.argmin(np.abs(peak_periods - period_true))]
    assert np.isclose(detected_period, period_true, rtol=0.15)


def test_power_spectrum_shapes_match():
    t = np.linspace(0.0, 10.0, 100)
    flux = np.sin(2.0 * np.pi * t / 2.0)

    freq, power, coeffs = ex_part_b.power_spectrum_from_flux(t, flux, nfreq=80)

    assert len(freq) == len(power) == len(coeffs)