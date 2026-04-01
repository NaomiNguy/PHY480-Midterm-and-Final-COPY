import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from ex_part_a import (
    load_light_curve,
    make_relative_time,
    normalize_flux,
    detrend_linear,
    moving_average,
)
from ex_part_b import power_spectrum_from_flux, strongest_periods
from ex_part_c import candidate_periods_from_dft, choose_best_period, fold_light_curve
from ex_part_d import (
    box_transit_model,
    bootstrap_fit,
)

import numpy as np
import matplotlib.pyplot as plt


def dominant_period_from_periodogram(freq, power):
    _, peak_periods, _ = strongest_periods(freq, power, n_peaks=1)
    return peak_periods[0]


def report_best_fit(best_params, uncertainties):
    lines = [
        "Best-fit transit parameters:",
        f"P     = {best_params['period']:.6f} ± {uncertainties['period_std']:.6f} days",
        f"delta = {best_params['depth']:.6f} ± {uncertainties['depth_std']:.6f}",
        f"tau   = {best_params['duration']:.6f} ± {uncertainties['duration_std']:.6f} days",
        f"t0    = {best_params['epoch']:.6f} ± {uncertainties['epoch_std']:.6f} days",
    ]
    return lines


def plot_periodogram(freq, power, best_period=None):
    plt.figure(figsize=(8, 4))
    plt.plot(freq, power)
    if best_period is not None:
        plt.axvline(1.0 / best_period, linestyle="--", label="Best-fit period")
        plt.legend()
    plt.xlabel("Frequency (1/day)")
    plt.ylabel("Power |c(f)|^2")
    plt.title("Periodogram")
    plt.tight_layout()
    plt.show()


def plot_folded_light_curve_with_model(t, flux, best_params):
    phase, flux_fold = fold_light_curve(
        t - best_params["epoch"],
        flux,
        best_params["period"],
        centered=True,
    )

    model = box_transit_model(
        t,
        best_params["period"],
        best_params["depth"],
        best_params["duration"],
        best_params["epoch"],
    )

    phase_model, model_fold = fold_light_curve(
        t - best_params["epoch"],
        model,
        best_params["period"],
        centered=True,
    )

    plt.figure(figsize=(8, 4))
    plt.scatter(phase, flux_fold, s=6, label="Data")
    plt.plot(phase_model, model_fold, linewidth=2, label="Transit model")
    plt.xlabel("Phase")
    plt.ylabel("Flux")
    plt.title("Folded Light Curve with Best-Fit Model")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_residuals(t, flux, best_params):
    model = box_transit_model(
        t,
        best_params["period"],
        best_params["depth"],
        best_params["duration"],
        best_params["epoch"],
    )
    residuals = flux - model

    phase, residuals_fold = fold_light_curve(
        t - best_params["epoch"],
        residuals,
        best_params["period"],
        centered=True,
    )

    plt.figure(figsize=(8, 4))
    plt.scatter(phase, residuals_fold, s=6)
    plt.axhline(0.0, linestyle="--")
    plt.xlabel("Phase")
    plt.ylabel("Residual Flux")
    plt.title("Residuals After Model Subtraction")
    plt.tight_layout()
    plt.show()


def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    df = df.iloc[::10].copy()

    t = df["t_rel"].to_numpy()
    flux = moving_average(df["flux_clean"].to_numpy(), window=9)
    flux_err = df["flux_err"].to_numpy()

    candidate_periods, freq, power = candidate_periods_from_dft(t, flux, n_peaks=5)
    best_period, _, _ = choose_best_period(t, flux, candidate_periods, method="scatter")

    depth_guess = max(1e-4, 1.0 - np.min(flux))
    epoch_guess = t[np.argmin(flux)]
    duration_guess = 0.1 * best_period

    period_grid = np.linspace(best_period * 0.95, best_period * 1.05, 21)
    depth_grid = np.linspace(max(1e-4, depth_guess * 0.5), depth_guess * 1.5, 21)
    duration_grid = np.linspace(max(0.01, duration_guess * 0.5), duration_guess * 1.5, 21)
    epoch_grid = np.linspace(epoch_guess - 0.5 * best_period, epoch_guess + 0.5 * best_period, 21)

    best_params, _, uncertainties, _ = bootstrap_fit(
        t,
        flux,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=20,
    )

    for line in report_best_fit(best_params, uncertainties):
        print(line)

    dominant_period = dominant_period_from_periodogram(freq, power)
    print(f"\nDominant periodogram period = {dominant_period:.6f} days")
    print(
        "Consistency check:",
        np.isclose(best_params["period"], dominant_period, rtol=0.05)
    )

    plot_periodogram(freq, power, best_period=best_params["period"])
    plot_folded_light_curve_with_model(t, flux, best_params)
    plot_residuals(t, flux, best_params)


if __name__ == "__main__":
    main()