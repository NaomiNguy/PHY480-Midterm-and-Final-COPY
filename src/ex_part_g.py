import numpy as np
import matplotlib.pyplot as plt

from ex_part_d import box_transit_model, grid_search_box_fit


def bootstrap_transit_fit(
    t,
    flux,
    flux_err,
    period_grid,
    depth_grid,
    duration_grid,
    epoch_grid,
    n_boot=100,
    seed=42,
):
    rng = np.random.default_rng(seed)

    n = len(t)
    samples = []

    for _ in range(n_boot):
        idx = rng.integers(0, n, n)

        t_b = t[idx]
        flux_b = flux[idx]
        err_b = flux_err[idx] if flux_err is not None else None

        best_params, _ = grid_search_box_fit(
            t_b,
            flux_b,
            err_b,
            period_grid,
            depth_grid,
            duration_grid,
            epoch_grid,
        )

        samples.append(
            [
                best_params["period"],
                best_params["depth"],
                best_params["duration"],
                best_params["epoch"],
            ]
        )

    samples = np.asarray(samples)

    summary = {
        "period_mean": np.mean(samples[:, 0]),
        "period_std": np.std(samples[:, 0], ddof=1),
        "depth_mean": np.mean(samples[:, 1]),
        "depth_std": np.std(samples[:, 1], ddof=1),
        "duration_mean": np.mean(samples[:, 2]),
        "duration_std": np.std(samples[:, 2], ddof=1),
        "epoch_mean": np.mean(samples[:, 3]),
        "epoch_std": np.std(samples[:, 3], ddof=1),
    }

    return samples, summary


def inject_transit(t, period, depth, duration, epoch, noise_sigma=0.001, seed=42):
    rng = np.random.default_rng(seed)

    clean = box_transit_model(t, period, depth, duration, epoch)
    noisy = clean + rng.normal(0.0, noise_sigma, size=len(t))

    return noisy


def injection_recovery_grid(
    t,
    period_values,
    depth_values,
    duration,
    epoch,
    noise_sigma=0.001,
    n_realizations=3,
    tolerance=0.05,
    seed=42,
):
    rng = np.random.default_rng(seed)

    recovery = np.zeros((len(period_values), len(depth_values)))

    for i, period_true in enumerate(period_values):
        for j, depth_true in enumerate(depth_values):
            recovered = 0

            for _ in range(n_realizations):
                trial_seed = rng.integers(0, 1_000_000)

                flux = inject_transit(
                    t,
                    period_true,
                    depth_true,
                    duration,
                    epoch,
                    noise_sigma=noise_sigma,
                    seed=trial_seed,
                )

                flux_err = np.full_like(t, noise_sigma)

                period_grid = np.linspace(period_true * 0.9, period_true * 1.1, 21)
                depth_grid = np.linspace(depth_true * 0.5, depth_true * 1.5, 21)
                duration_grid = np.linspace(duration * 0.7, duration * 1.3, 15)
                epoch_grid = np.linspace(
                    epoch - 0.3 * period_true, epoch + 0.3 * period_true, 15
                )

                best_params, _ = grid_search_box_fit(
                    t,
                    flux,
                    flux_err,
                    period_grid,
                    depth_grid,
                    duration_grid,
                    epoch_grid,
                )

                if np.isclose(best_params["period"], period_true, rtol=tolerance):
                    recovered += 1

            recovery[i, j] = recovered / n_realizations

    return recovery


def plot_bootstrap_distributions(samples):
    labels = ["Period", "Depth", "Duration", "Epoch"]

    for i, label in enumerate(labels):
        plt.figure(figsize=(7, 4))
        plt.hist(samples[:, i], bins=20)
        plt.xlabel(label)
        plt.ylabel("Count")
        plt.title(f"Bootstrap Distribution: {label}")
        plt.tight_layout()

        filename = f"part_g_bootstrap_{label.lower()}.png"
        plt.savefig(filename)

        plt.show()


def plot_recovery_grid(period_values, depth_values, recovery):
    plt.figure(figsize=(7, 5))
    plt.imshow(
        recovery.T,
        origin="lower",
        aspect="auto",
        extent=[
            period_values[0],
            period_values[-1],
            depth_values[0],
            depth_values[-1],
        ],
    )
    plt.colorbar(label="Recovery Fraction")
    plt.xlabel("Injected Period")
    plt.ylabel("Injected Depth")
    plt.title("Injection-Recovery Summary")
    plt.tight_layout()
    plt.savefig("part_g_injection_summary.png")
    plt.show()


def main():
    t = np.linspace(0.0, 40.0, 600)

    # ACTUAL VALUES:
    # t = np.linspace(0.0, 40.0, 2000)

    period_true = 3.2
    depth_true = 0.018
    duration_true = 0.20
    epoch_true = 0.75
    noise_sigma = 0.001

    flux = inject_transit(
        t,
        period_true,
        depth_true,
        duration_true,
        epoch_true,
        noise_sigma=noise_sigma,
        seed=42,
    )

    flux_err = np.full_like(t, noise_sigma)

    period_grid = np.linspace(3.0, 3.4, 11)
    depth_grid = np.linspace(0.010, 0.025, 11)
    duration_grid = np.linspace(0.10, 0.30, 9)
    epoch_grid = np.linspace(0.4, 1.1, 11)

    # ACTUAL VALUES:
    # period_grid = np.linspace(3.0, 3.4, 31)
    # depth_grid = np.linspace(0.010, 0.025, 31)
    # duration_grid = np.linspace(0.10, 0.30, 21)
    # epoch_grid = np.linspace(0.4, 1.1, 31)

    samples, summary = bootstrap_transit_fit(
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

    print("Bootstrap summary:")
    for key, value in summary.items():
        print(f"{key}: {value:.6f}")

    plot_bootstrap_distributions(samples)
    period_values = np.linspace(2.8, 3.6, 3)
    depth_values = np.linspace(0.008, 0.024, 3)

    # ACTUAL VALUES:
    # period_values = np.linspace(2.8, 3.6, 4)
    # depth_values = np.linspace(0.008, 0.024, 4)

    recovery = injection_recovery_grid(
        t,
        period_values,
        depth_values,
        duration=0.20,
        epoch=0.75,
        noise_sigma=0.001,
        n_realizations=1,

        # ACTUAL VALUE:
        # n_realizations=3,

        seed=123,
    )

    print("\nInjection recovery grid:")
    print(recovery)

    plot_recovery_grid(period_values, depth_values, recovery)


if __name__ == "__main__":
    main()
