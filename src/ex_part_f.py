import numpy as np
import matplotlib.pyplot as plt


def orbital_derivatives(state, gm=1.0):
    x, y, vx, vy = state
    r = np.sqrt(x**2 + y**2)

    ax = -gm * x / r**3
    ay = -gm * y / r**3

    return np.array([vx, vy, ax, ay], dtype=float)


def rk4_step(state, dt, gm=1.0):
    k1 = orbital_derivatives(state, gm)
    k2 = orbital_derivatives(state + 0.5 * dt * k1, gm)
    k3 = orbital_derivatives(state + 0.5 * dt * k2, gm)
    k4 = orbital_derivatives(state + dt * k3, gm)

    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def circular_initial_conditions(period, gm=1.0):
    radius = (gm * (period / (2.0 * np.pi))**2) ** (1.0 / 3.0)
    speed = np.sqrt(gm / radius)

    x0 = radius
    y0 = 0.0
    vx0 = 0.0
    vy0 = speed

    return np.array([x0, y0, vx0, vy0], dtype=float)


def integrate_orbit(period, n_periods=5, steps_per_period=500, gm=1.0):
    dt = period / steps_per_period
    n_steps = int(n_periods * steps_per_period) + 1

    times = np.linspace(0.0, n_periods * period, n_steps)
    states = np.zeros((n_steps, 4))

    states[0] = circular_initial_conditions(period, gm=gm)

    for i in range(1, n_steps):
        states[i] = rk4_step(states[i - 1], dt, gm=gm)

    return times, states


def orbital_energy(states, gm=1.0):
    x = states[:, 0]
    y = states[:, 1]
    vx = states[:, 2]
    vy = states[:, 3]

    r = np.sqrt(x**2 + y**2)
    v2 = vx**2 + vy**2

    return 0.5 * v2 - gm / r


def find_transit_times(times, states):
    """
    Transit criterion:
    y changes sign while x > 0.
    This corresponds to crossing the observer's line of sight.
    """
    x = states[:, 0]
    y = states[:, 1]

    transit_times = []

    for i in range(len(times) - 1):
        if y[i] == 0 and x[i] > 0:
            transit_times.append(times[i])

        if y[i] * y[i + 1] < 0:
            x_mid = 0.5 * (x[i] + x[i + 1])

            if x_mid > 0:
                frac = abs(y[i]) / (abs(y[i]) + abs(y[i + 1]))
                t_cross = times[i] + frac * (times[i + 1] - times[i])
                transit_times.append(t_cross)

    return np.array(transit_times)


def linear_ephemeris(period, epoch, n_transits):
    n = np.arange(n_transits)
    return epoch + n * period


def compare_to_ephemeris(transit_times, period, epoch=0.0):
    predicted = linear_ephemeris(period, epoch, len(transit_times))
    residuals = transit_times - predicted
    return predicted, residuals


def plot_orbit(states):
    x = states[:, 0]
    y = states[:, 1]

    plt.figure(figsize=(6, 6))
    plt.plot(x, y)
    plt.scatter([0], [0], s=80, label="Star")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("RK4 Integrated Circular Orbit")
    plt.axis("equal")
    plt.legend()
    plt.tight_layout()
    plt.savefig("part_f_integrated_circular_orbit.png")
    plt.show()


def plot_transit_timing(transit_times, predicted, residuals):
    plt.figure(figsize=(8, 4))
    plt.plot(predicted, transit_times, "o")
    plt.xlabel("Linear Ephemeris Time")
    plt.ylabel("RK4 Transit Time")
    plt.title("Observed vs Predicted Transit Times")
    plt.tight_layout()
    plt.savefig("part_f_observed_vs_predicted.png")
    plt.show()

    plt.figure(figsize=(8, 4))
    plt.axhline(0.0, linestyle="--")
    plt.plot(predicted, residuals, "o")
    plt.xlabel("Predicted Transit Time")
    plt.ylabel("Timing Residual")
    plt.title("Transit Timing Residuals")
    plt.tight_layout()
    plt.savefig("part_f_timing_residuals")
    plt.show()


def main():
    period = 3.2
    epoch = 0.0

    times, states = integrate_orbit(period, n_periods=5, steps_per_period=500, gm=1.0)
    transit_times = find_transit_times(times, states)
    predicted, residuals = compare_to_ephemeris(transit_times, period, epoch)

    energy = orbital_energy(states, gm=1.0)

    print("Detected transit times:")
    print(transit_times)

    print("\nTiming residuals:")
    print(residuals)

    print("\nEnergy drift:")
    print(np.max(np.abs(energy - energy[0])))

    plot_orbit(states)
    plot_transit_timing(transit_times, predicted, residuals)


if __name__ == "__main__":
    main()