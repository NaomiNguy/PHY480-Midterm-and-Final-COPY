import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

import ex_part_b


def test_sinusoid_peak_period():
    """
    Synthetic sinusoid: DFT should recover the correct period.
    """

    period_true = 5.0
    t = np.linspace(0, 100, 1000)

    flux = np.sin(2 * np.pi * t / period_true)

    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux)

    peak_freqs, peak_periods, _ = ex_part_b.strongest_periods(freq, power, n_peaks=1)

    detected_period = peak_periods[0]

    assert np.isclose(detected_period, period_true, rtol=0.05)


def test_injected_box_transit():
    """
    Synthetic box-shaped transit should produce a peak
    near the injected orbital period.
    """

    period_true = 8.0
    depth = 0.01
    duration = 0.2

    t = np.linspace(0, 200, 2000)
    flux = np.ones_like(t)

    phase = np.mod(t, period_true)

    transit_mask = phase < duration
    flux[transit_mask] -= depth

    freq, power, _ = ex_part_b.power_spectrum_from_flux(t, flux)

    peak_freqs, peak_periods, _ = ex_part_b.strongest_periods(freq, power, n_peaks=3)

    detected_period = peak_periods[0]

    assert np.isclose(detected_period, period_true, rtol=0.1)