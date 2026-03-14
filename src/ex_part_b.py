from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

def load_light_curve(filename="TESSA_lc.dat"):
    path = DATA_DIR / filename
    df = pd.read_csv(
        path,
        sep=r"\s+",
        comment="#",
        names=["time", "flux", "flux_err"],
        header=None,
    )
    return df

def make_relative_time(df):
    df = df.copy()
    t0 = df["time"].iloc[0]
    df["t_rel"] = df["time"] - t0
    return df

def normalize_flux(df):
    df = df.copy()
    med = np.median(df["flux"])
    df["flux_norm"] = df["flux"] / med
    return df

def detrend_linear(df):
    df = df.copy()
    coeffs = np.polyfit(df["t_rel"], df["flux_norm"], deg=1)
    trend = np.polyval(coeffs, df["t_rel"])
    df["flux_clean"] = df["flux_norm"] / trend
    return df

def dft_manual(y):
    y = np.asarray(y, dtype=float)
    N = len(y)
    c = np.zeros(N, dtype=complex)

    for k in range(N):
        s = 0.0j
        for n in range(N):
            s += y[n] * np.exp(-2j * np.pi * k * n / N)
        c[k] = s

    return c

def power_spectrum_from_flux(t, y):
    """
    Use median cadence to define the frequency grid.
    """
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)

    # subtract mean so the DC component is reduced
    y_centered = y - np.mean(y)

    c = dft_manual(y_centered)
    power = np.abs(c) ** 2

    dt = np.median(np.diff(t))
    N = len(t)

    freq = np.arange(N) / (N * dt)
    return freq, power, c

def strongest_periods(freq, power, n_peaks=5):
    """
    Return strongest nonzero positive-frequency peaks.
    Only uses frequencies up to the Nyquist limit.
    """
    N = len(freq)
    half = N // 2

    freq_pos = freq[1:half]
    power_pos = power[1:half]

    idx = np.argsort(power_pos)[::-1][:n_peaks]

    peak_freqs = freq_pos[idx]
    peak_powers = power_pos[idx]
    peak_periods = 1.0 / peak_freqs

    order = np.argsort(peak_freqs)
    return peak_freqs[order], peak_periods[order], peak_powers[order]

def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    freq, power, coeffs = power_spectrum_from_flux(df["t_rel"], df["flux_clean"])

    peak_freqs, peak_periods, peak_powers = strongest_periods(freq, power, n_peaks=5)

    print("Top candidate periods:")
    for f, p, pw in zip(peak_freqs, peak_periods, peak_powers):
        print(f"frequency = {f:.6f} 1/day, period = {p:.6f} days, power = {pw:.6e}")

    plt.figure(figsize=(8, 4))
    plt.plot(freq[1:len(freq)//2], power[1:len(freq)//2])
    plt.xlabel("Frequency (1/day)")
    plt.ylabel("Power |c_k|^2")
    plt.title("DFT Power Spectrum")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()