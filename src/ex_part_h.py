import numpy as np

from ex_part_f import (
    integrate_orbit,
    find_transit_times,
    compare_to_ephemeris,
    orbital_energy,
)

from ex_part_g import (
    inject_transit,
    bootstrap_transit_fit,
)


def synthesis_summary(
    period,
    epoch,
    bootstrap_summary,
    timing_residuals,
    energy_drift,
):
    lines = []

    lines.append("Final Project Synthesis")
    lines.append("-----------------------")

    lines.append(
        f"The RK4 orbit model was integrated using period P = {period:.6f} days."
    )

    lines.append(
        f"The maximum transit-timing residual relative to the linear ephemeris was "
        f"{np.max(np.abs(timing_residuals)):.6e} days."
    )

    lines.append(
        "For a circular orbit, the RK4 transit times should agree with "
        "t_n = t0 + nP because the angular motion is periodic and unperturbed."
    )

    lines.append(
        f"The maximum orbital energy drift was {energy_drift:.6e}, which checks "
        "the numerical stability of the RK4 integration."
    )

    largest_uncertainty = max(
        [
            ("period", bootstrap_summary["period_std"]),
            ("depth", bootstrap_summary["depth_std"]),
            ("duration", bootstrap_summary["duration_std"]),
            ("epoch", bootstrap_summary["epoch_std"]),
        ],
        key=lambda item: item[1],
    )

    lines.append(
        f"The largest bootstrap uncertainty was in {largest_uncertainty[0]}, "
        f"with spread {largest_uncertainty[1]:.6e}."
    )

    lines.append(
        "The bootstrap distributions quantify how sensitive the fitted transit "
        "parameters are to random resampling of the light curve."
    )

    return lines


def main():
    period = 3.2
    epoch = 0.0

    times, states = integrate_orbit(
        period,
        n_periods=5,
        steps_per_period=500,
        gm=1.0,
    )

    transit_times = find_transit_times(times, states)
    predicted, residuals = compare_to_ephemeris(transit_times, period, epoch)

    energy = orbital_energy(states, gm=1.0)
    energy_drift = np.max(np.abs(energy - energy[0]))

    t = np.linspace(0.0, 40.0, 2000)

    flux = inject_transit(
        t,
        period=period,
        depth=0.018,
        duration=0.20,
        epoch=0.75,
        noise_sigma=0.001,
        seed=42,
    )

    flux_err = np.full_like(t, 0.001)

    period_grid = np.linspace(3.0, 3.4, 11)
    depth_grid = np.linspace(0.010, 0.025, 11)
    duration_grid = np.linspace(0.10, 0.30, 9)
    epoch_grid = np.linspace(0.4, 1.1, 11)

    # ACTUAL VALUES:
    # period_grid = np.linspace(3.0, 3.4, 31)
    # depth_grid = np.linspace(0.010, 0.025, 31)
    # duration_grid = np.linspace(0.10, 0.30, 21)
    # epoch_grid = np.linspace(0.4, 1.1, 31)

    _, bootstrap_summary = bootstrap_transit_fit(
        t,
        flux,
        flux_err,
        period_grid,
        depth_grid,
        duration_grid,
        epoch_grid,
        n_boot=20,

        # ACTUAL VALUE:
        # n_boot=100,
        
        seed=42,
    )

    lines = synthesis_summary(
        period,
        epoch,
        bootstrap_summary,
        residuals,
        energy_drift,
    )

    for line in lines:
        print(line)


if __name__ == "__main__":
    main()