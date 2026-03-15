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

def fold_light_curve(t, flux, period, centered=False):
    t = np.asarray(t, dtype=float)
    flux = np.asarray(flux, dtype=float)

    phase = (t / period) % 1.0
    if centered:
        phase = ((t / period + 0.5) % 1.0) - 0.5

    order = np.argsort(phase)
    return phase[order], flux[order]

def binned_scatter_metric(phase, flux, nbins=40):
    """
    Objective metric: lower is better.
    Bin the folded curve in phase and measure the within-bin scatter.
    """
    phase = np.asarray(phase)
    flux = np.asarray(flux)

    edges = np.linspace(np.min(phase), np.max(phase), nbins + 1)
    bin_ids = np.digitize(phase, edges) - 1

    scatters = []
    counts = []

    for i in range(nbins):
        mask = bin_ids == i
        if np.sum(mask) >= 3:
            scatters.append(np.std(flux[mask]))
            counts.append(np.sum(mask))

    if len(scatters) == 0:
        return np.inf

    scatters = np.asarray(scatters)
    counts = np.asarray(counts)

    return np.average(scatters, weights=counts)

def transit_depth_significance_metric(phase, flux, center=0.0, width=0.1):
    """
    Objective metric: larger is better.
    Compare mean in-transit flux to out-of-transit flux.
    Assumes centered phase in [-0.5, 0.5).
    """
    phase = np.asarray(phase)
    flux = np.asarray(flux)

    in_transit = np.abs(phase - center) < (width / 2.0)
    out_of_transit = ~in_transit

    if np.sum(in_transit) < 3 or np.sum(out_of_transit) < 3:
        return -np.inf

    f_in = np.mean(flux[in_transit])
    f_out = np.mean(flux[out_of_transit])

    sigma_out = np.std(flux[out_of_transit])
    if sigma_out == 0:
        return np.inf if f_out > f_in else -np.inf

    depth = f_out - f_in
    return depth / sigma_out

def choose_best_period(t, flux, candidate_periods, method="scatter"):
    best_period = None
    best_score = None
    results = []

    for period in candidate_periods:
        if method == "scatter":
            phase, f_fold = fold_light_curve(t, flux, period, centered=False)
            score = binned_scatter_metric(phase, f_fold)
            better = (best_score is None) or (score < best_score)

        elif method == "transit":
            phase, f_fold = fold_light_curve(t, flux, period, centered=True)
            score = transit_depth_significance_metric(phase, f_fold)
            better = (best_score is None) or (score > best_score)

        else:
            raise ValueError("method must be 'scatter' or 'transit'")

        results.append((period, score))

        if better:
            best_period = period
            best_score = score

    return best_period, best_score, results

def plot_folded_curve(t, flux, period, centered=True):
    phase, f_fold = fold_light_curve(t, flux, period, centered=centered)

    plt.figure(figsize=(8, 4))
    plt.scatter(phase, f_fold, s=6)
    plt.xlabel("Phase")
    plt.ylabel("Flux")
    plt.title(f"Folded Light Curve (P = {period:.6f} days)")
    plt.tight_layout()
    plt.show()

def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    t = df["t_rel"].to_numpy()
    flux = df["flux_clean"].to_numpy()

    candidate_periods = [2.5, 5.0, 7.8]

    best_period, best_score, results = choose_best_period(
        t, flux, candidate_periods, method="scatter"
    )

    print("Candidate period scores:")
    for p, s in results:
        print(f"P = {p:.6f} days, score = {s:.6e}")

    print(f"\nChosen period: {best_period:.6f} days")
    print(f"Best score: {best_score:.6e}")

    plot_folded_curve(t, flux, best_period, centered=False)

if __name__ == "__main__":
    main()