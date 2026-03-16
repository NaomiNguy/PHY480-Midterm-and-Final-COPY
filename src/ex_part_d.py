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


def transit_phase(t, period, epoch):
    """
    Return centered phase in [-0.5, 0.5).
    """
    t = np.asarray(t, dtype=float)
    return (((t - epoch) / period + 0.5) % 1.0) - 0.5


def box_transit_model(t, period, depth, duration, epoch):
    """
    Simple box transit model.

    Parameters
    ----------
    t : array
        Times.
    period : float
        Transit period.
    depth : float
        Transit depth.
    duration : float
        Transit duration in same time units as t.
    epoch : float
        Transit-center epoch.

    Returns
    -------
    flux_model : array
        Model flux values.
    """
    t = np.asarray(t, dtype=float)
    phase = transit_phase(t, period, epoch)

    half_width_phase = duration / (2.0 * period)
    in_transit = np.abs(phase) < half_width_phase

    model = np.ones_like(t, dtype=float)
    model[in_transit] -= depth
    return model


def weighted_chi2(y_obs, y_model, yerr=None):
    y_obs = np.asarray(y_obs, dtype=float)
    y_model = np.asarray(y_model, dtype=float)

    if yerr is None:
        return np.sum((y_obs - y_model) ** 2)

    yerr = np.asarray(yerr, dtype=float)
    return np.sum(((y_obs - y_model) / yerr) ** 2)


def grid_search_box_fit(t, flux, flux_err, period_grid, depth_grid, duration_grid, epoch_grid):
    """
    Simple brute-force fit for a box transit model.
    Returns best-fit parameters and chi^2.
    """
    best_params = None
    best_chi2 = np.inf

    for P in period_grid:
        for d in depth_grid:
            for tau in duration_grid:
                for t0 in epoch_grid:
                    model = box_transit_model(t, P, d, tau, t0)
                    chi2 = weighted_chi2(flux, model, flux_err)

                    if chi2 < best_chi2:
                        best_chi2 = chi2
                        best_params = {
                            "period": P,
                            "depth": d,
                            "duration": tau,
                            "epoch": t0,
                        }

    return best_params, best_chi2


def bootstrap_fit(
    t,
    flux,
    flux_err,
    period_grid,
    depth_grid,
    duration_grid,
    epoch_grid,
    n_boot=100,
    rng_seed=42,
):
    """
    Bootstrap uncertainties by resampling data points with replacement.
    """
    rng = np.random.default_rng(rng_seed)

    best_params, best_chi2 = grid_search_box_fit(
        t, flux, flux_err, period_grid, depth_grid, duration_grid, epoch_grid
    )

    results = []

    n = len(t)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)

        t_b = t[idx]
        flux_b = flux[idx]
        err_b = None if flux_err is None else flux_err[idx]

        fit_b, _ = grid_search_box_fit(
            t_b, flux_b, err_b, period_grid, depth_grid, duration_grid, epoch_grid
        )
        results.append(
            [fit_b["period"], fit_b["depth"], fit_b["duration"], fit_b["epoch"]]
        )

    results = np.asarray(results)

    uncertainties = {
        "period_std": np.std(results[:, 0], ddof=1),
        "depth_std": np.std(results[:, 1], ddof=1),
        "duration_std": np.std(results[:, 2], ddof=1),
        "epoch_std": np.std(results[:, 3], ddof=1),
    }

    return best_params, best_chi2, uncertainties, results


def plot_folded_model(t, flux, best_params):
    P = best_params["period"]
    d = best_params["depth"]
    tau = best_params["duration"]
    t0 = best_params["epoch"]

    phase = transit_phase(t, P, t0)
    order = np.argsort(phase)

    phase_sorted = phase[order]
    flux_sorted = flux[order]
    model_sorted = box_transit_model(t, P, d, tau, t0)[order]

    plt.figure(figsize=(8, 4))
    plt.scatter(phase_sorted, flux_sorted, s=6, label="Data")
    plt.plot(phase_sorted, model_sorted, linewidth=2, label="Box model", color="red")
    plt.xlabel("Phase")
    plt.ylabel("Flux")
    plt.title("Folded Light Curve with Best-Fit Transit Model")
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)

    t = df["t_rel"].to_numpy()
    flux = df["flux_norm"].to_numpy()
    flux_err = df["flux_err"].to_numpy()

    # Example: center grids around your Part C best period
    period_grid = np.linspace(2.9, 3.1, 21)
    depth_grid = np.linspace(0.001, 0.03, 20)
    duration_grid = np.linspace(0.05, 0.30, 20)
    epoch_grid = np.linspace(0.0, 3.0, 30)

    best_params, best_chi2, uncertainties, boot = bootstrap_fit(
        t,
        flux,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=100,
    )

    print("Best-fit parameters:")
    print(f"P     = {best_params['period']:.6f} ± {uncertainties['period_std']:.6f}")
    print(f"delta = {best_params['depth']:.6f} ± {uncertainties['depth_std']:.6f}")
    print(f"tau   = {best_params['duration']:.6f} ± {uncertainties['duration_std']:.6f}")
    print(f"t0    = {best_params['epoch']:.6f} ± {uncertainties['epoch_std']:.6f}")
    print(f"chi^2 = {best_chi2:.6f}")

    plot_folded_model(t, flux, best_params)


if __name__ == "__main__":
    main()