import numpy as np
import matplotlib.pyplot as plt

def dominant_period_from_periodogram(freq, power, strongest_periods_func):
    """
    Return the dominant nonzero period from the periodogram.
    """
    peak_freqs, peak_periods, peak_powers = strongest_periods_func(freq, power, n_peaks=1)
    return peak_periods[0]


def folded_transit_depth(phase, flux, center=0.0, width=0.1):
    """
    Measure the average transit depth in a folded light curve.

    Returns
    -------
    depth : float
        Mean out-of-transit flux minus mean in-transit flux.
        Positive values indicate a dip.
    """
    phase = np.asarray(phase)
    flux = np.asarray(flux)

    in_transit = np.abs(phase - center) < (width / 2.0)
    out_of_transit = ~in_transit

    if np.sum(in_transit) < 3 or np.sum(out_of_transit) < 3:
        return 0.0

    mean_in = np.mean(flux[in_transit])
    mean_out = np.mean(flux[out_of_transit])

    return mean_out - mean_in


def consistency_check_with_folded_curve(
    t,
    flux,
    freq,
    power,
    best_params,
    strongest_periods_func,
    fold_light_curve_func,
    rtol=0.05,
):
    """
    Check that the best-fit period matches the dominant periodogram peak
    and that the folded light curve shows a dip near phase 0.

    Returns
    -------
    result : dict
        Dictionary containing dominant period, best-fit period,
        folded transit depth, and consistency boolean.
    """
    dominant_period = dominant_period_from_periodogram(
        freq, power, strongest_periods_func
    )

    best_period = best_params["period"]
    best_epoch = best_params["epoch"]
    best_duration = best_params["duration"]

    phase, flux_fold = fold_light_curve_func(
        t - best_epoch,
        flux,
        best_period,
        centered=True,
    )

    width_phase = best_duration / best_period
    depth = folded_transit_depth(phase, flux_fold, center=0.0, width=width_phase)

    consistent_period = np.isclose(best_period, dominant_period, rtol=rtol)
    has_dip = depth > 0.0

    return {
        "dominant_period": dominant_period,
        "best_period": best_period,
        "folded_depth": depth,
        "consistent_period": consistent_period,
        "has_dip": has_dip,
        "consistent": consistent_period and has_dip,
    }


def report_best_fit(best_params, uncertainties):
    """
    Return formatted strings for final reported parameters.
    """
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
    plt.plot(freq[1:len(freq)//2], power[1:len(freq)//2])
    if best_period is not None:
        plt.axvline(1.0 / best_period, linestyle="--", label="Best-fit period")
        plt.legend()
    plt.xlabel("Frequency (1/day)")
    plt.ylabel("Power |c_k|^2")
    plt.title("DFT Periodogram")
    plt.tight_layout()
    plt.show()


def plot_folded_light_curve_with_model(
    t,
    flux,
    best_params,
    fold_light_curve_func,
    box_transit_model_func,
):
    phase, flux_fold = fold_light_curve_func(
        t - best_params["epoch"],
        flux,
        best_params["period"],
        centered=True,
    )

    model = box_transit_model_func(
        t,
        best_params["period"],
        best_params["depth"],
        best_params["duration"],
        best_params["epoch"],
    )

    phase_model, model_fold = fold_light_curve_func(
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


def plot_residuals(
    t,
    flux,
    best_params,
    fold_light_curve_func,
    box_transit_model_func,
):
    model = box_transit_model_func(
        t,
        best_params["period"],
        best_params["depth"],
        best_params["duration"],
        best_params["epoch"],
    )
    residuals = flux - model

    phase, residuals_fold = fold_light_curve_func(
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