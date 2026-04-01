from ex_part_a import (
    load_light_curve,
    make_relative_time,
    normalize_flux,
    detrend_linear,
    moving_average,
)
from ex_part_c import (
    candidate_periods_from_dft,
    choose_best_period,
    fold_light_curve,
    estimate_duration_from_slopes,
)

import numpy as np
import matplotlib.pyplot as plt


def transit_phase(t, period, epoch):
    return (((t - epoch) / period + 0.5) % 1.0) - 0.5


def box_transit_model(t, period, depth, duration, epoch):
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
    n_boot=30,
    rng_seed=42,
):
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


def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    df = df.iloc[::10].copy()

    t = df["t_rel"].to_numpy()
    flux = df["flux_clean"].to_numpy()
    flux_err = df["flux_err"].to_numpy()
    flux_smooth = moving_average(flux, window=9)

    candidate_periods, freq, power = candidate_periods_from_dft(t, flux_smooth, n_peaks=5)
    best_period, _, _ = choose_best_period(t, flux_smooth, candidate_periods, method="scatter")

    phase, flux_fold = fold_light_curve(t, flux_smooth, best_period, centered=True)
    _, duration_guess, _, _, _, _ = estimate_duration_from_slopes(
        phase, flux_fold, smooth_window=11, period=best_period
    )

    depth_guess = max(1e-4, 1.0 - np.min(flux_smooth))
    epoch_guess = t[np.argmin(flux_smooth)]

    period_grid = np.linspace(best_period * 0.95, best_period * 1.05, 21)
    depth_grid = np.linspace(max(1e-4, depth_guess * 0.5), depth_guess * 1.5, 21)
    duration_grid = np.linspace(max(0.01, duration_guess * 0.5), duration_guess * 1.5, 21)
    epoch_grid = np.linspace(epoch_guess - 0.5 * best_period, epoch_guess + 0.5 * best_period, 21)

    best_params, best_chi2, uncertainties, _ = bootstrap_fit(
        t,
        flux_smooth,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=20,
    )

    print("Best-fit transit parameters:")
    print(f"P     = {best_params['period']:.6f} ± {uncertainties['period_std']:.6f} days")
    print(f"delta = {best_params['depth']:.6f} ± {uncertainties['depth_std']:.6f}")
    print(f"tau   = {best_params['duration']:.6f} ± {uncertainties['duration_std']:.6f} days")
    print(f"t0    = {best_params['epoch']:.6f} ± {uncertainties['epoch_std']:.6f} days")
    print(f"chi^2 = {best_chi2:.6f}")


if __name__ == "__main__":
    main()