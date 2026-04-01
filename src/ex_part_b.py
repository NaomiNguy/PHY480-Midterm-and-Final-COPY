from ex_part_a import (
    load_light_curve,
    make_relative_time,
    normalize_flux,
    detrend_linear,
    moving_average,
)

import numpy as np
import matplotlib.pyplot as plt


def dft_nonuniform(t, y, freqs):
    """
    Fourier sum from scratch using actual sample times.
    No np.fft is used.
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    freqs = np.asarray(freqs, dtype=float)

    coeffs = np.zeros(len(freqs), dtype=complex)

    for k, f in enumerate(freqs):
        total = 0.0j
        for n in range(len(t)):
            total += y[n] * np.exp(-2j * np.pi * f * t[n])
        coeffs[k] = total

    return coeffs


def power_spectrum_from_flux(t, y, nfreq=None):
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    y_centered = y - np.mean(y)

    dt = np.median(np.diff(t))
    T = t.max() - t.min()

    if nfreq is None:
        nfreq = len(t)

    f_min = 1.0 / T
    f_max = 0.5 / dt
    freqs = np.linspace(f_min, f_max, nfreq)

    coeffs = dft_nonuniform(t, y_centered, freqs)
    power = np.abs(coeffs) ** 2

    return freqs, power, coeffs


def strongest_periods(freq, power, n_peaks=5):
    freq = np.asarray(freq)
    power = np.asarray(power)

    valid = freq > 0
    freq_pos = freq[valid]
    power_pos = power[valid]

    idx = np.argsort(power_pos)[::-1][:n_peaks]

    peak_freqs = freq_pos[idx]
    peak_powers = power_pos[idx]
    peak_periods = 1.0 / peak_freqs

    return peak_freqs, peak_periods, peak_powers


def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    # Downsample to keep manual Fourier sum runtime reasonable
    df = df.iloc[::10].copy()

    t = df["t_rel"].to_numpy()
    flux = df["flux_clean"].to_numpy()
    flux_smooth = moving_average(flux, window=9)

    freq, power, _ = power_spectrum_from_flux(t, flux_smooth, nfreq=min(len(t), 800))
    peak_freqs, peak_periods, peak_powers = strongest_periods(freq, power, n_peaks=5)

    print("Top candidate periods:")
    for f, p, pw in zip(peak_freqs, peak_periods, peak_powers):
        print(f"frequency = {f:.6f} 1/day, period = {p:.6f} days, power = {pw:.6e}")

    plt.figure(figsize=(8, 4))
    plt.plot(freq, power)
    plt.xlabel("Frequency (1/day)")
    plt.ylabel("Power |c(f)|^2")
    plt.title("Periodogram")
    plt.tight_layout()
    plt.savefig("part_b_periodogram")
    plt.show()


if __name__ == "__main__":
    main()