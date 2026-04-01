from ex_part_a import (
    load_light_curve,
    make_relative_time,
    normalize_flux,
    detrend_linear,
    moving_average,
    numerical_derivative,
)
from ex_part_b import power_spectrum_from_flux, strongest_periods

import numpy as np
import matplotlib.pyplot as plt


def fold_light_curve(t, flux, period, centered=False):
    t = np.asarray(t, dtype=float)
    flux = np.asarray(flux, dtype=float)

    if centered:
        phase = ((t / period + 0.5) % 1.0) - 0.5
    else:
        phase = (t / period) % 1.0

    order = np.argsort(phase)
    return phase[order], flux[order]


def candidate_periods_from_dft(t, flux, n_peaks=5):
    freq, power, _ = power_spectrum_from_flux(t, flux, nfreq=min(len(t), 800))
    _, peak_periods, _ = strongest_periods(freq, power, n_peaks=n_peaks)
    return peak_periods, freq, power


def binned_scatter_metric(phase, flux, nbins=40):
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

    return np.average(np.asarray(scatters), weights=np.asarray(counts))


def transit_window_scatter(phase, flux, center=0.0, width=0.1):
    phase = np.asarray(phase)
    flux = np.asarray(flux)

    in_window = np.abs(phase - center) < (width / 2.0)

    if np.sum(in_window) < 3:
        return np.inf

    return np.std(flux[in_window])


def choose_best_period(t, flux, candidate_periods, method="scatter"):
    best_period = None
    best_score = None
    results = []

    for period in candidate_periods:
        if method == "scatter":
            phase, f_fold = fold_light_curve(t, flux, period, centered=False)
            score = binned_scatter_metric(phase, f_fold)
            better = (best_score is None) or (score < best_score)

        elif method == "window":
            phase, f_fold = fold_light_curve(t, flux, period, centered=True)
            score = transit_window_scatter(phase, f_fold, center=0.0, width=0.1)
            better = (best_score is None) or (score < best_score)

        else:
            raise ValueError("method must be 'scatter' or 'window'")

        results.append((period, score))

        if better:
            best_period = period
            best_score = score

    return best_period, best_score, results


def estimate_duration_from_slopes(phase, flux, smooth_window=11, period=1.0):
    flux_smooth = moving_average(flux, window=smooth_window)
    dflux = numerical_derivative(phase, flux_smooth)

    ingress_idx = np.argmin(dflux)
    egress_idx = np.argmax(dflux)

    duration_phase = abs(phase[egress_idx] - phase[ingress_idx])
    duration_time = duration_phase * period

    return duration_phase, duration_time, ingress_idx, egress_idx, flux_smooth, dflux


def plot_folded_curve(t, flux, period, centered=True):
    phase, f_fold = fold_light_curve(t, flux, period, centered=centered)

    plt.figure(figsize=(8, 4))
    plt.scatter(phase, f_fold, s=6)
    plt.xlabel("Phase")
    plt.ylabel("Flux")
    plt.title(f"Folded Light Curve (P = {period:.6f} days)")
    plt.tight_layout()
    plt.savefig("part_c_folded_light_curve.png")
    plt.show()


def main():
    df = load_light_curve("TESSA_lc.dat")
    df = make_relative_time(df)
    df = normalize_flux(df)
    df = detrend_linear(df)

    df = df.iloc[::10].copy()

    t = df["t_rel"].to_numpy()
    flux = df["flux_clean"].to_numpy()
    flux_smooth = moving_average(flux, window=9)

    candidate_periods, freq, power = candidate_periods_from_dft(t, flux_smooth, n_peaks=5)

    best_period, best_score, results = choose_best_period(
        t, flux_smooth, candidate_periods, method="scatter"
    )

    print("Candidate periods from Part B:")
    for p in candidate_periods:
        print(f"  {p:.6f} days")

    print("\nRefinement scores:")
    for p, s in results:
        print(f"  P = {p:.6f} days, score = {s:.6e}")

    print(f"\nChosen period: {best_period:.6f} days")
    print(f"Best score: {best_score:.6e}")

    phase, flux_fold = fold_light_curve(t, flux_smooth, best_period, centered=True)
    duration_phase, duration_time, i_in, i_eg, flux_fold_smooth, dflux = estimate_duration_from_slopes(
        phase, flux_fold, smooth_window=11, period=best_period
    )

    print(f"Estimated duration from slopes: {duration_time:.6f} days")

    plt.figure(figsize=(8, 4))
    plt.plot(phase, flux_fold_smooth, label="Smoothed folded flux")
    plt.plot(phase, dflux, label="dF/dphase")
    plt.xlabel("Phase")
    plt.ylabel("Value")
    plt.title("Folded Light Curve and Derivative")
    plt.legend()
    plt.tight_layout()
    plt.savefig("part_c_derivative.png")
    plt.show()

    plot_folded_curve(t, flux_smooth, best_period, centered=True)


if __name__ == "__main__":
    main()