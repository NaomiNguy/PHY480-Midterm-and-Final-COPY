import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

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

def detrend_constant_test(n=100):
    t = np.linspace(0.0, 10.0, n)
    flux = np.ones_like(t)
    coeffs = np.polyfit(t, flux, deg=2)
    trend = np.polyval(coeffs, t)
    detrended = flux / trend
    return detrended

def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)

    print(df.head())
    print("Median normalized flux:", np.median(df["flux_norm"]))

    plt.figure(figsize=(8, 4))
    plt.scatter(df["t_rel"], df["flux"], s=5)
    plt.xlabel("Relative Time (days)")
    plt.ylabel("Flux")
    plt.title("Raw TESS Light Curve")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 4))
    plt.scatter(df["t_rel"], df["flux_norm"], s=5)
    plt.axhline(1.0, linestyle="--")
    plt.xlabel("Relative Time (days)")
    plt.ylabel("Normalized Flux")
    plt.title("Normalized TESS Light Curve")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()