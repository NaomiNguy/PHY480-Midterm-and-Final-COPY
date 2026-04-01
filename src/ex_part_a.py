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


def moving_average(y, window=9):
    y = np.asarray(y, dtype=float)

    if window < 3 or window % 2 == 0:
        raise ValueError("window must be an odd integer >= 3")

    kernel = np.ones(window) / window
    return np.convolve(y, kernel, mode="same")


def numerical_derivative(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    dydx = np.zeros_like(y)
    dydx[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
    dydx[0] = (y[1] - y[0]) / (x[1] - x[0])
    dydx[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])

    return dydx


def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    t = df["t_rel"].to_numpy()
    flux_raw = df["flux"].to_numpy()
    flux_clean = df["flux_clean"].to_numpy()
    flux_smooth = moving_average(flux_clean, window=9)

    print("Median normalized flux:", np.median(df["flux_norm"]))

    plt.figure(figsize=(8, 4))
    plt.scatter(t, flux_raw, s=5, label="Raw")
    plt.xlabel("Relative Time (days)")
    plt.ylabel("Flux")
    plt.title("Raw Light Curve")
    plt.tight_layout()
    plt.savefig("part_a_raw_light_curve.png")
    plt.show()

    plt.figure(figsize=(8, 4))
    plt.scatter(t, flux_clean, s=5, label="Cleaned")
    plt.plot(t, flux_smooth, linewidth=2, label="Smoothed")
    plt.xlabel("Relative Time (days)")
    plt.ylabel("Flux")
    plt.title("Cleaned and Smoothed Light Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig("part_a_clean_smooth_light_curve.png")
    plt.show()


if __name__ == "__main__":
    main()